#!/usr/bin/env python3
"""Reproduce the EXSU 500 MSK 2024 Data Lead preprocessing (no ML operations)."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import tarfile
import tempfile
import pandas as pd


def read_cbio(path: Path) -> pd.DataFrame:
    with path.open(encoding='utf-8') as f:
        skip = 0
        for line in f:
            if not line.startswith('#'):
                break
            skip += 1
    return pd.read_csv(path, sep='\t', skiprows=skip, dtype='string', low_memory=False)


def metadata(path: Path) -> dict[str, str]:
    fields = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if ':' in line and not line.lstrip().startswith('#'):
            key, value = line.split(':', 1)
            fields[key.strip().lower()] = value.strip()
    return fields


def check(condition: bool, msg: str) -> None:
    if not condition:
        raise ValueError(msg)


def process(study: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    pat = read_cbio(study / 'data_clinical_patient.txt')
    sam = read_cbio(study / 'data_clinical_sample.txt')
    check({'PATIENT_ID','STAGE_HIGHEST_RECORDED'} <= set(pat), 'Missing patient/stage fields')
    check({'PATIENT_ID','SAMPLE_ID','GENE_PANEL'} <= set(sam), 'Missing sample identifiers/panel')
    check(pat.PATIENT_ID.notna().all() and pat.PATIENT_ID.is_unique, 'Invalid patient identifiers')
    check(sam.SAMPLE_ID.notna().all() and sam.SAMPLE_ID.is_unique, 'Invalid sample identifiers')
    check(sam.PATIENT_ID.isin(pat.PATIENT_ID).all(), 'Unmatched sample patients')
    stage = pat[['PATIENT_ID','STAGE_HIGHEST_RECORDED']].rename(columns={'STAGE_HIGHEST_RECORDED':'STAGE_RAW'})
    clinical = sam.merge(stage, on='PATIENT_ID', how='left', validate='many_to_one', sort=False)
    clinical['stage_binary'] = clinical.STAGE_RAW.map({'Stage 1-3':0,'Stage 4':1}).astype('Int64')
    counts = clinical.groupby('PATIENT_ID', sort=False).SAMPLE_ID.nunique().rename('N_SAMPLES_PER_PATIENT')
    clinical = clinical.join(counts, on='PATIENT_ID')
    eligible = clinical.loc[clinical.stage_binary.notna()].copy()
    # Highest sample coverage, then alphabetically earliest sample ID.
    eligible['_coverage_numeric'] = pd.to_numeric(eligible['SAMPLE_COVERAGE'], errors='coerce')
    eligible = eligible.sort_values(['PATIENT_ID','_coverage_numeric','SAMPLE_ID'],
                                    ascending=[True,False,True], na_position='last', kind='stable')
    manifest = eligible.drop_duplicates('PATIENT_ID').drop(columns='_coverage_numeric').copy()
    manifest = manifest.sort_values('PATIENT_ID', kind='stable')
    check(manifest.PATIENT_ID.is_unique and manifest.SAMPLE_ID.is_unique, 'Duplicate manifest IDs')
    clinical.to_csv(out/'clinical_all_samples.csv', index=False)
    manifest.to_csv(out/'clinical_manifest.csv', index=False)
    selected = set(manifest.SAMPLE_ID)
    patient_lookup = manifest.set_index('SAMPLE_ID').PATIENT_ID

    mm = metadata(study/'meta_mutations.txt')
    check(mm.get('genetic_alteration_type','').upper()=='MUTATION_EXTENDED' and mm.get('datatype','').upper()=='MAF', 'Unexpected mutation metadata')
    mut = read_cbio(study/mm['data_filename'])
    check({'Tumor_Sample_Barcode','Hugo_Symbol'} <= set(mut), 'Mutation ID/gene missing')
    mut = mut.loc[mut.Tumor_Sample_Barcode.isin(selected)].copy()
    mut = mut.rename(columns={'Tumor_Sample_Barcode':'SAMPLE_ID','Hugo_Symbol':'HUGO_SYMBOL'})
    mut['PATIENT_ID'] = mut.SAMPLE_ID.map(patient_lookup)
    keep = ['PATIENT_ID','SAMPLE_ID','HUGO_SYMBOL','Variant_Classification','Variant_Type',
            'HGVSp_Short','HGVSp','Protein_Change','Mutation_Status','Chromosome',
            'Start_Position','End_Position','Reference_Allele','Tumor_Seq_Allele2',
            't_alt_count','t_ref_count']
    mut = mut[[x for x in keep if x in mut.columns]]
    check(mut.PATIENT_ID.notna().all(), 'Unmatched mutation IDs')
    mut.to_csv(out/'mutations_long.csv', index=False)

    cm = metadata(study/'meta_CNA.txt')
    check(cm.get('genetic_alteration_type','').upper()=='COPY_NUMBER_ALTERATION' and cm.get('datatype','').upper()=='DISCRETE', 'Unexpected CNA metadata')
    cna = read_cbio(study/cm['data_filename'])
    check('Hugo_Symbol' in cna, 'CNA gene column missing')
    check(cna.Hugo_Symbol.notna().all() and cna.Hugo_Symbol.is_unique, 'Duplicate/missing CNA genes')
    cn_samples = [s for s in manifest.SAMPLE_ID if s in cna.columns]
    check(bool(cn_samples), 'No selected samples found in CNA matrix')
    # Preserve every source CNA value, including -1.5. Do not impute.
    long = cna[['Hugo_Symbol',*cn_samples]].melt(id_vars='Hugo_Symbol',var_name='SAMPLE_ID',value_name='CNA_VALUE')
    long = long.rename(columns={'Hugo_Symbol':'HUGO_SYMBOL'})
    original = long.CNA_VALUE.copy()
    long['CNA_VALUE'] = pd.to_numeric(long.CNA_VALUE, errors='coerce')
    check(not (original.notna() & long.CNA_VALUE.isna()).any(), 'Nonnumeric CNA entries')
    long['PATIENT_ID'] = long.SAMPLE_ID.map(patient_lookup)
    long = long[['PATIENT_ID','SAMPLE_ID','HUGO_SYMBOL','CNA_VALUE']]
    check(not long.duplicated(['SAMPLE_ID','HUGO_SYMBOL']).any(), 'Duplicate CNA sample/gene pairs')
    long.to_csv(out/'cna_long.csv', index=False)

    gp = read_cbio(study/'data_gene_panel_matrix.txt')
    check({'SAMPLE_ID','mutations','cna'} <= set(gp), 'Missing gene-panel columns')
    check(gp.SAMPLE_ID.is_unique, 'Duplicate panel sample IDs')
    gp = gp.loc[gp.SAMPLE_ID.isin(selected)].copy()
    gp['PATIENT_ID'] = gp.SAMPLE_ID.map(patient_lookup)
    gp = gp[['PATIENT_ID',*[x for x in gp if x!='PATIENT_ID']]]
    gp.to_csv(out/'gene_panel_matrix.csv', index=False)

    raw_stage = pat.STAGE_HIGHEST_RECORDED.fillna('Missing').value_counts().sort_index()
    selected_stage = manifest.stage_binary.value_counts().sort_index()
    cna_counts = long.CNA_VALUE.value_counts(dropna=False).sort_index()
    unusual = sorted(set(long.CNA_VALUE.dropna())-{-2,-1,0,1,2})
    lines = ['# MSK 2024 preprocessing summary','',
             f'- Raw patients: {pat.PATIENT_ID.nunique()}', f'- Raw samples: {sam.SAMPLE_ID.nunique()}',
             f'- Patients with multiple samples: {(counts>1).sum()}',f'- Selected patients: {len(manifest)}',
             f'- Stage I–III: {selected_stage.get(0,0)}',f'- Stage IV: {selected_stage.get(1,0)}',
             f'- Mutation records: {len(mut)}',f'- Samples with mutation rows: {mut.SAMPLE_ID.nunique()}',
             f'- Samples without mutation rows: {len(manifest)-mut.SAMPLE_ID.nunique()}',
             f'- Distinct mutated genes: {mut.HUGO_SYMBOL.nunique()}',
             f'- CNA rows: {len(long)}',f'- CNA samples: {long.SAMPLE_ID.nunique()}',
             f'- CNA genes: {long.HUGO_SYMBOL.nunique()}',f'- Missing CNA values: {long.CNA_VALUE.isna().sum()}',
             f'- Gene-panel mapping samples: {gp.SAMPLE_ID.nunique()}',
             f'- Selected samples absent from CNA matrix: {len(selected-set(cn_samples))}',
             f'- Unexpected CNA values: {unusual}', '', '## CNA value counts']
    lines += [f'- {key}: {val}' for key,val in cna_counts.items()]
    lines += ['', '## Important limitations',
              '- STAGE_HIGHEST_RECORDED is not necessarily stage at tumor collection.',
              '- No mutation row is not proof of wild type without gene-level coverage.',
              '- Gene-panel IDs are not themselves gene-by-gene coverage definitions.',
              '- Unexpected CNA values are preserved, not recoded.',
              '- No ML splitting, imputation, scaling, or feature selection performed.']
    (out/'data_summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines[:18]))


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    source=p.add_mutually_exclusive_group(required=True)
    source.add_argument('--archive',type=Path,help='Downloaded prostate_msk_2024.tar.gz')
    source.add_argument('--study-dir',type=Path,help='Extracted prostate_msk_2024 folder')
    p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args()
    if a.archive:
        with tempfile.TemporaryDirectory(prefix='exsu500_msk_') as tmp:
            with tarfile.open(a.archive.expanduser(),'r:gz') as tar:
                # Avoid extracting unsafe paths or links.
                for m in tar.getmembers():
                    target=Path(m.name)
                    if m.issym() or m.islnk() or target.is_absolute() or '..' in target.parts:
                        raise ValueError(f'Unsafe TAR member: {m.name}')
                tar.extractall(tmp, filter='data')
            process(Path(tmp)/'prostate_msk_2024',a.output_dir.expanduser())
    else:
        process(a.study_dir.expanduser(),a.output_dir.expanduser())

if __name__=='__main__':
    main()
