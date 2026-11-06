"""Meaningful checks for data integrity, metric conventions and saved evidence."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score,accuracy_score
from run_experiments import classify,metrics
ROOT=Path(__file__).resolve().parents[1]

def main():
    # Worked nine-item confusion matrix from the submitted proposal, independently
    # expanded into labels, catches class-order/averaging convention mistakes.
    g=[0,0,0,0,1,1,2,2,2];p=[0,0,0,1,1,1,0,2,2]
    assert abs(f1_score(g,p,average='macro')-(.75+.8+.8)/3)<1e-12
    assert abs(accuracy_score(g,p)-7/9)<1e-12
    assert classify([-.050001,-.05,-.049999,0,.049999,.05,.050001]).tolist()==[0,0,1,1,1,2,2]
    data=pd.read_csv(ROOT/'data/constructed.csv')
    assert len(data)==288 and data.text.nunique()==288 and data.item_id.nunique()==288
    assert data.family_id.nunique()==48 and (data.groupby('family_id').size()==6).all()
    assert data.groupby('family_id').split.nunique().max()==1
    assert data[data.split=='test'].family_id.nunique()==36
    for name in ['A','B']:
        a=pd.read_csv(ROOT/f'annotations/annotator_{name}.csv',keep_default_na=False)
        assert len(a)==288 and a.item_id.nunique()==288
    original=pd.read_csv(ROOT/'results/original-data-results.csv')
    assert original.n.sum()==23703
    assert np.allclose(original.archived_r,[.881166,.416477,.570896,.491511],atol=1e-6)
    for rn,n in [(1,3600),(2,720)]:
        d=pd.read_csv(ROOT/f'results/dynasent_round{rn}-scores.csv')
        assert len(d)==n and d.item_id.nunique()==n
        assert d.gold_label.value_counts().tolist()==[n//3]*3
        assert d[['archived_compound','maintained_compound']].apply(lambda c:c.between(-1,1).all()).all()
    for name in ['dynasent','constructed']:
        inputs=json.loads((ROOT/f'annotations/llm_{name}_input.json').read_text())
        responses=json.loads((ROOT/f'annotations/llm_{name}_responses.json').read_text())
        assert len(inputs)==len(responses)==60
        assert {x['item_id'] for x in inputs}=={x['item_id'] for x in responses}
    print('PASS: metric example/boundaries, original replication evidence, corpus/split integrity and judge alignment.')

if __name__=='__main__':main()
