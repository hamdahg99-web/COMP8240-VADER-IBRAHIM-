"""Validate independent human ratings; never silently fabricate missing labels."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.metrics import cohen_kappa_score
from run_experiments import LABELS, metrics, bootstrap

ROOT=Path(__file__).resolve().parents[1]

def finite_or_none(value):
    value=float(value)
    return value if np.isfinite(value) else None

def intensity_correlation(x,y):
    # Constant vectors have undefined Pearson correlation, not a zero correlation.
    return None if np.ptp(x)==0 or np.ptp(y)==0 else finite_or_none(pearsonr(x,y).statistic)

def main():
    texts=pd.read_csv(ROOT/'data/constructed.csv')
    ratings=[]
    for name in ['A','B']:
        path=ROOT/f'annotations/annotator_{name}.csv'
        data=pd.read_csv(path,keep_default_na=False)
        if len(data)!=len(texts) or data.item_id.duplicated().any() or set(data.item_id)!=set(texts.item_id):
            raise ValueError(f'Annotator {name}: missing, duplicate or unexpected item IDs')
        joined=texts[['item_id','text']].merge(data,on='item_id',validate='one_to_one',suffixes=('_source','_rating'))
        if not joined.text_source.equals(joined.text_rating):raise ValueError('Rating-sheet texts were changed')
        count=int((data.sentiment!='').sum())
        if count<len(texts):
            print(f'PENDING: annotator {name} has {count}/{len(texts)} labels. No human metrics produced.')
            return 2
        if not data.sentiment.isin(LABELS).all():raise ValueError('Invalid sentiment class')
        intensity=pd.to_numeric(data.intensity,errors='raise')
        if not ((intensity>=-4)&(intensity<=4)&(intensity%1==0)).all():raise ValueError('Intensity must be integer -4..4')
        sign=data.sentiment.map({'negative':-1,'neutral':0,'positive':1})
        if not np.array_equal(np.sign(intensity),sign):raise ValueError('Class and intensity signs disagree')
        if not data.confidence.isin(['low','medium','high']).all():raise ValueError('Missing or invalid confidence')
        ratings.append(data.rename(columns={k:f'{k}_{name}' for k in ['sentiment','intensity','confidence','notes']}).drop(columns='text'))
    data=texts.merge(ratings[0],on='item_id',validate='one_to_one').merge(ratings[1],on='item_id',validate='one_to_one')
    agree=data.sentiment_A==data.sentiment_B
    agreement={}
    for split in ['development','test','all']:
        d=data if split=='all' else data[data.split==split]
        agreement[split]={'n':len(d),'raw_agreement':float((d.sentiment_A==d.sentiment_B).mean()),
            'cohen_kappa':finite_or_none(cohen_kappa_score(d.sentiment_A,d.sentiment_B,labels=LABELS)),
            'disagreements':int((d.sentiment_A!=d.sentiment_B).sum())}
    sheet=ROOT/'annotations/adjudication.csv'
    if not sheet.exists():
        data['final_label']=np.where(agree,data.sentiment_A,'')
        data[['item_id','text','sentiment_A','sentiment_B','intensity_A','intensity_B','final_label']].to_csv(sheet,index=False)
        print('Created adjudication.csv; fill disagreements or mark ambiguous and rerun.')
        (ROOT/'results/human-agreement.json').write_text(json.dumps(agreement,indent=2)+'\n')
        return 2
    adjudicated=pd.read_csv(sheet,keep_default_na=False)
    if adjudicated.item_id.duplicated().any() or set(adjudicated.item_id)!=set(data.item_id):raise ValueError('Invalid adjudication IDs')
    data=data.merge(adjudicated[['item_id','final_label']],on='item_id',validate='one_to_one')
    if not data.final_label.isin(LABELS+['ambiguous']).all():raise ValueError('Unfinished adjudication')
    scores=pd.read_csv(ROOT/'results/constructed-scores.csv')
    data=data.merge(scores[['item_id','archived_compound','maintained_compound','archived_label','maintained_label']],on='item_id',validate='one_to_one')
    valid=data[(data.split=='test')&(data.final_label!='ambiguous')].copy()
    if len(valid)==0:raise ValueError('No resolved held-out human reference labels')
    gold=valid.final_label.map({v:i for i,v in enumerate(LABELS)}).to_numpy()
    a=valid.archived_label.map({v:i for i,v in enumerate(LABELS)}).to_numpy()
    b=valid.maintained_label.map({v:i for i,v in enumerate(LABELS)}).to_numpy()
    intensity=(pd.to_numeric(valid.intensity_A)+pd.to_numeric(valid.intensity_B))/2
    out={'status':'complete_from_supplied_human_files','agreement_before_adjudication':agreement,
        'test_n_resolved':len(valid),'test_n_ambiguous':int(((data.split=='test')&(data.final_label=='ambiguous')).sum()),
        'archived':metrics(gold,a),'maintained':metrics(gold,b),
        'uncertainty':bootstrap(gold,a,b,valid.family_id),
        'archived_intensity_pearson_r':intensity_correlation(intensity.to_numpy(),valid.archived_compound.to_numpy()),
        'maintained_intensity_pearson_r':intensity_correlation(intensity.to_numpy(),valid.maintained_compound.to_numpy())}
    (ROOT/'results/human-results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    data.to_csv(ROOT/'results/constructed-human-reference.csv',index=False)
    metadata_path=ROOT/'results/final-run-metadata.json'
    if metadata_path.exists():
        metadata=json.loads(metadata_path.read_text());metadata['human_annotation_completed']=True
        metadata_path.write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(out,indent=2));return 0

if __name__=='__main__':sys.exit(main())
