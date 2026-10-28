#!/usr/bin/env python3
"""Build descriptive (wide) and compact (44-column) MSK masters from processed CSVs."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

MARKERS=['AR','TP53','PTEN','RB1','SPOP','FOXA1','BRCA1','BRCA2','ATM','CDK12']
CLINICAL=['PATIENT_ID','SAMPLE_ID','STAGE_RAW','stage_binary','CANCER_TYPE_DETAILED',
          'SAMPLE_TYPE','GENE_PANEL','SAMPLE_COVERAGE','TUMOR_PURITY','MSI_SCORE',
          'MSI_TYPE','SOMATIC_STATUS','TMB_NONSYNONYMOUS','N_SAMPLES_PER_PATIENT']

def load(folder:Path,name:str)->pd.DataFrame:
    return pd.read_csv(folder/name, low_memory=False)

def check(ok:bool,msg:str)->None:
    if not ok: raise ValueError(msg)

def merge_left(left:pd.DataFrame,right:pd.DataFrame)->pd.DataFrame:
    return left.merge(right,on='SAMPLE_ID',how='left',sort=False,validate='one_to_one')

def build(folder:Path)->None:
    clinical=load(folder,'clinical_manifest.csv')
    mut=load(folder,'mutations_long.csv')
    cna=load(folder,'cna_long.csv')
    panel=load(folder,'gene_panel_matrix.csv')
    check(clinical.PATIENT_ID.is_unique and clinical.SAMPLE_ID.is_unique,'Duplicate clinical IDs')
    check(panel.SAMPLE_ID.is_unique,'Duplicate gene-panel IDs')
    check(not cna.duplicated(['SAMPLE_ID','HUGO_SYMBOL']).any(),'Duplicate CNA sample/gene')
    check(mut.SAMPLE_ID.isin(clinical.SAMPLE_ID).all(),'Mutation sample not in manifest')
    check(cna.SAMPLE_ID.isin(clinical.SAMPLE_ID).all(),'CNA sample not in manifest')
    check(panel.SAMPLE_ID.isin(clinical.SAMPLE_ID).all(),'Panel sample not in manifest')
    check(set(CLINICAL) <= set(clinical),'Required clinical columns missing')
    check({'mutations','cna','structural_variants'} <= set(panel),'Required panel columns missing')
    # Mutations: no-call is NA, not confirmed wild type.
    counts=mut.dropna(subset=['SAMPLE_ID','HUGO_SYMBOL']).groupby(['SAMPLE_ID','HUGO_SYMBOL'],sort=False).size()
    mut_wide=counts.unstack('HUGO_SYMBOL').add_prefix('MUT_COUNT__').reset_index()
    cna_wide=cna.pivot(index='SAMPLE_ID',columns='HUGO_SYMBOL',values='CNA_VALUE')
    cna_wide=cna_wide.add_prefix('CNA__').reset_index()
    panel_wide=panel.drop(columns='PATIENT_ID').rename(columns={x:'PANEL__'+x for x in panel if x not in ['PATIENT_ID','SAMPLE_ID']})
    descriptive=clinical.copy()
    descriptive['HAS_MUTATION_RECORDS']=descriptive.SAMPLE_ID.isin(mut.SAMPLE_ID).astype('int64')
    for table in (panel_wide,mut_wide,cna_wide): descriptive=merge_left(descriptive,table)
    descriptive=descriptive[['PATIENT_ID','SAMPLE_ID',*[x for x in descriptive if x not in ['PATIENT_ID','SAMPLE_ID']]]].sort_values('PATIENT_ID')
    check(len(descriptive)==len(clinical) and descriptive.PATIENT_ID.is_unique,'Invalid descriptive master')
    descriptive.to_csv(folder/'EXSU500_MSK_master_descriptive.csv',index=False)

    compact=clinical[CLINICAL].copy()
    mut_summary=mut.groupby('SAMPLE_ID').agg(N_MUTATION_RECORDS=('HUGO_SYMBOL','size'),N_GENES_WITH_MUTATIONS=('HUGO_SYMBOL','nunique')).reset_index()
    compact=merge_left(compact,mut_summary)
    compact['HAS_MUTATION_RECORDS']=compact.N_MUTATION_RECORDS.notna().astype('int64')
    for x in ('N_MUTATION_RECORDS','N_GENES_WITH_MUTATIONS'):
        compact[x]=compact[x].fillna(0).astype('int64')
    for gene in MARKERS:
        positive=set(mut.loc[mut.HUGO_SYMBOL.eq(gene),'SAMPLE_ID'])
        compact['MUT_REPORTED_'+gene]=pd.Series(pd.NA,index=compact.index,dtype='Int64')
        compact.loc[compact.SAMPLE_ID.isin(positive),'MUT_REPORTED_'+gene]=1
    cna_markers=cna.loc[cna.HUGO_SYMBOL.isin(MARKERS)]
    cna_focus=cna_markers.pivot(index='SAMPLE_ID',columns='HUGO_SYMBOL',values='CNA_VALUE').add_prefix('CNA_').reset_index()
    compact=merge_left(compact,cna_focus)
    cna_values=pd.to_numeric(cna.CNA_VALUE,errors='raise')
    cna_summary=pd.DataFrame({'SAMPLE_ID':cna.SAMPLE_ID,
                              'N_CNA_NONZERO':cna_values.notna() & cna_values.ne(0),
                              'N_CNA_DEEP_DEL':cna_values.eq(-2),
                              'N_CNA_AMPLIFICATION':cna_values.eq(2),
                              'N_CNA_MINUS_1_5':cna_values.eq(-1.5)})
    cna_summary=cna_summary.groupby('SAMPLE_ID',sort=False).sum().reset_index()
    compact=merge_left(compact,cna_summary)
    panel_compact=panel[['SAMPLE_ID','mutations','cna','structural_variants']].rename(columns={x:'PANEL_'+x for x in ['mutations','cna','structural_variants']})
    compact=merge_left(compact,panel_compact)
    compact=compact[['PATIENT_ID','SAMPLE_ID',*[x for x in compact if x not in ['PATIENT_ID','SAMPLE_ID']]]].sort_values('PATIENT_ID')
    check(len(compact)==len(clinical) and compact.PATIENT_ID.is_unique and compact.SAMPLE_ID.is_unique,'Invalid compact master')
    compact.to_csv(folder/'EXSU500_MSK_master_compact.csv',index=False)
    print(f'Descriptive master: {descriptive.shape[0]} rows x {descriptive.shape[1]} columns')
    print(f'Compact master: {compact.shape[0]} rows x {compact.shape[1]} columns')
    print(f'Stage counts: {compact.stage_binary.value_counts().sort_index().to_dict()}')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir',type=Path,required=True)
    args=parser.parse_args()
    build(args.input_dir.expanduser())
