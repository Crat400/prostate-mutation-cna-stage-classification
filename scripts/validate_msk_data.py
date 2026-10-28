#!/usr/bin/env python3
"""Recheck processed MSK files and print a reproducible QC summary; exit on errors."""
import argparse
from pathlib import Path
import pandas as pd


def run(folder:Path)->None:
    files=['clinical_all_samples.csv','clinical_manifest.csv','mutations_long.csv','cna_long.csv','gene_panel_matrix.csv','EXSU500_MSK_master_compact.csv']
    raw,clinical,mut,cna,panel,master=[pd.read_csv(folder/f,low_memory=False) for f in files]
    def assert_ok(ok,msg):
        if not ok: raise AssertionError(msg)
        print('PASS:',msg)
    assert_ok(raw.SAMPLE_ID.is_unique,'All clinical samples unique')
    assert_ok(clinical.PATIENT_ID.is_unique and clinical.SAMPLE_ID.is_unique,'One selected sample per patient')
    assert_ok(master.PATIENT_ID.is_unique and master.SAMPLE_ID.is_unique,'Master IDs unique')
    assert_ok(set(master.SAMPLE_ID)==set(clinical.SAMPLE_ID),'Master sample IDs match manifest')
    assert_ok(set(mut.SAMPLE_ID)<=set(clinical.SAMPLE_ID),'Mutation samples contained in manifest')
    assert_ok(set(cna.SAMPLE_ID)==set(clinical.SAMPLE_ID),'CNA samples match manifest')
    assert_ok(set(panel.SAMPLE_ID)==set(clinical.SAMPLE_ID),'Panel samples match manifest')
    assert_ok(not cna.duplicated(['SAMPLE_ID','HUGO_SYMBOL']).any(),'No duplicate CNA sample-gene pairs')
    assert_ok(not panel.SAMPLE_ID.duplicated().any(),'Panel sample IDs unique')
    assert_ok((clinical.stage_binary.astype(int)==clinical.STAGE_RAW.map({'Stage 1-3':0,'Stage 4':1})).all(),'Stage mapping valid')
    ref=clinical[['SAMPLE_ID','GENE_PANEL']].merge(panel[['SAMPLE_ID','mutations','cna']],on='SAMPLE_ID',validate='one_to_one')
    assert_ok((ref.GENE_PANEL==ref.mutations).all() and (ref.GENE_PANEL==ref.cna).all(),'Panel assignments match clinical')
    assert_ok(master[['PATIENT_ID','SAMPLE_ID']].merge(clinical[['PATIENT_ID','SAMPLE_ID']],on=['PATIENT_ID','SAMPLE_ID'],validate='one_to_one').shape[0]==len(master),'Master patient/sample pairs valid')
    print('\nDATA SUMMARY')
    print('Raw patients:',raw.PATIENT_ID.nunique(),'Raw samples:',len(raw))
    print('Eligible:',len(clinical),'Stage distribution:',clinical.stage_binary.value_counts().sort_index().to_dict())
    print('Mutation rows:',len(mut),'Mutation-positive-row samples:',mut.SAMPLE_ID.nunique(),'No mutation rows:',len(clinical)-mut.SAMPLE_ID.nunique())
    print('CNA rows:',len(cna),'CNA genes:',cna.HUGO_SYMBOL.nunique(),'CNA missing:',cna.CNA_VALUE.isna().sum())
    print('Unexpected CNA values:',cna.loc[~cna.CNA_VALUE.isin([-2,-1,0,1,2]) & cna.CNA_VALUE.notna(),'CNA_VALUE'].value_counts().to_dict())
    print('Panel distribution:',clinical.GENE_PANEL.value_counts().to_dict())
    print('Sample type vs stage:\n',pd.crosstab(clinical.SAMPLE_TYPE,clinical.stage_binary).to_string())
    print('Clinical missingness:\n',clinical.isna().sum().loc[lambda x:x>0].to_string())
    print('Compact master dimensions:',master.shape)
    print('IMPORTANT: QC does not validate stage timing or gene-level panel coverage.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-dir',type=Path,required=True)
    run(p.parse_args().input_dir.expanduser())
