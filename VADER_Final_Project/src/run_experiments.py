"""Reproduce VADER and evaluate pinned DynaSent splits and authored diagnostics.

Usage: python src/run_experiments.py [--cache PATH] [--dynasent-zip PATH]
No training, threshold optimisation, or use of human rating placeholders occurs.
"""
from pathlib import Path
import argparse
from collections import Counter
import csv
import hashlib
import json
import math
import platform
import random
import shutil
import sys
import time
import zipfile
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor'))
import audit_helpers as audit

DYNA_COMMIT='707b6208978bfe7ff251a0c3263c9f0552c27b48'
DYNA_SHA='33001cf394618aa38f9530c43ca87072b92f5ee609a02afa2d168d25560cedfd'
DYNA_URL=f'https://raw.githubusercontent.com/cgpotts/dynasent/{DYNA_COMMIT}/dynasent-v1.1.zip'
LABELS=['negative','neutral','positive']
SEED=8240
REPLICATES=2000


def normalise_text(s): return ' '.join(s.split()).casefold()


def classify(scores):
    x=np.asarray(scores,dtype=float)
    return np.where(x>=.05,2,np.where(x<=-.05,0,1)).astype(int)


def dump(name,obj):
    (ROOT/'results'/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')


def f1_from_counts(cm):
    tp=np.diag(cm).astype(float)
    den=cm.sum(axis=0)+cm.sum(axis=1)
    return np.divide(2*tp,den,out=np.zeros(3),where=den!=0).mean()


def bootstrap(gold,old,new,groups=None):
    """Paired percentile CIs. Related variants are resampled as whole families."""
    rng=np.random.default_rng(SEED)
    g,a,b=map(np.asarray,(gold,old,new))
    if groups is None:
        units=None
    else:
        groups=np.asarray(groups)
        units=[np.flatnonzero(groups==k) for k in np.unique(groups)]
    values=[]
    for _ in range(REPLICATES):
        idx=rng.integers(0,len(g),len(g)) if units is None else np.concatenate([units[k] for k in rng.integers(0,len(units),len(units))])
        scores=[]
        for p in [a,b]:
            cm=np.bincount(g[idx]*3+p[idx],minlength=9).reshape(3,3)
            scores.append(f1_from_counts(cm))
        values.append([*scores,scores[1]-scores[0]])
    ci=np.quantile(values,[.025,.975],axis=0)
    return {'replicates':REPLICATES,'seed':SEED,'unit':'sentence' if groups is None else 'family',
            'archived_macro_f1_ci95':ci[:,0].tolist(),'maintained_macro_f1_ci95':ci[:,1].tolist(),
            'maintained_minus_archived_macro_f1_ci95':ci[:,2].tolist()}


def metrics(gold,pred):
    return {'accuracy':float(accuracy_score(gold,pred)),
            'macro_f1':float(f1_score(gold,pred,labels=[0,1,2],average='macro',zero_division=0)),
            'weighted_f1':float(f1_score(gold,pred,labels=[0,1,2],average='weighted',zero_division=0)),
            'confusion_matrix':confusion_matrix(gold,pred,labels=[0,1,2]).tolist(),
            'classification_report':classification_report(gold,pred,labels=[0,1,2],target_names=LABELS,output_dict=True,zero_division=0)}


def run(cache,dyna_path):
    start=time.perf_counter()
    for directory in ['results','figures','annotations']:(ROOT/directory).mkdir(exist_ok=True)
    # A prior package used an ambiguous generic filename for the original-only
    # stage. Remove that owned duplicate; keep explicitly scoped metadata files.
    (ROOT/'results/run-metadata.json').unlink(missing_ok=True)
    cache.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'vendor/vader2014_py3.py',cache/'vader2014_py3.py')
    old,new=audit.prepare(cache)
    original_summary,result_dir=audit.full_audit(cache,old,new)
    for p in result_dir.glob('*'):
        if p.is_file():shutil.copy2(p,ROOT/'results'/('original-run-metadata.json' if p.name=='run-metadata.json' else p.name))
    original_texts=set();original_frames=[];sensitivity=[]
    for key,(_,filename,n,paper_r) in audit.CORPORA.items():
        records=[]
        for line in (cache/'original'/filename).read_text().splitlines():
            if line:
                item,mean,text=line.split('\t',2);records.append((item,float(mean),text))
        frame=pd.read_csv(ROOT/f'results/{key}-scores.csv',dtype={'id':str})
        assert len(frame)==len(records)==n
        frame['text']=[r[2] for r in records]
        original_frames.append(frame)
        original_texts.update(normalise_text(r[2]) for r in records)
        human=frame.human_mean.to_numpy()
        normalisations={'human_mean_div4':human/4,'human_mean_raw':human,
                        'human_mean_vader_normalise':human/np.sqrt(human**2+15)}
        for policy,values in normalisations.items():
            gold=classify(values)
            for version in ['archived','maintained']:
                pred=classify(frame[f'{version}_compound'].to_numpy())
                row={'corpus':key,'gold_policy':policy,'implementation':version,**metrics(gold,pred)}
                sensitivity.append(row)
        # An independently implemented sklearn check of the supplied notebook metric.
        for version in ['archived','maintained']:
            got=metrics(classify(human/4),classify(frame[f'{version}_compound']))['macro_f1']
            expected=next(r for r in original_summary if r['domain']==key)[f'{version}_macro_f1_provisional']
            assert abs(got-expected)<1e-6
    dump('classification-policy-audit.json',sensitivity)
    # Source versions differ in both lexical resources and rules: do not attribute
    # all score changes solely to the lexicon or solely to rule changes.
    def lexicon(path,encoding):
        result={}
        for l in path.read_text(encoding=encoding).splitlines():
            if l.strip():
                p=l.split('\t');result[p[0]]=float(p[1])
        return result
    lo=lexicon(cache/'original/vader_sentiment_lexicon.txt','latin-1')
    ln=lexicon(cache/'maintained/vader_lexicon.txt','utf-8')
    dump('lexicon-audit.json',{'archived_entries':len(lo),'maintained_entries':len(ln),
        'shared_entries':len(lo.keys()&ln.keys()),'added_entries':len(ln.keys()-lo.keys()),
        'removed_entries':len(lo.keys()-ln.keys()),
        'shared_entries_with_changed_valence':sum(lo[k]!=ln[k] for k in lo.keys()&ln.keys()),
        'attribution_limit':'Implementation comparison combines rule and resource changes; no causal decomposition.'})
    if dyna_path is None:
        dyna_path=cache/'dynasent-v1.1.zip';audit.download(DYNA_URL,dyna_path,DYNA_SHA)
    if audit.digest(dyna_path)!=DYNA_SHA:raise ValueError('DynaSent checksum mismatch')
    benchmark={};bench_frames=[];quality={}
    with zipfile.ZipFile(dyna_path) as z:
        for number,name in [(1,'yelp'),(2,'dynabench')]:
            member=f'dynasent-v1.1/dynasent-v1.1-round0{number}-{name}-test.jsonl'
            raw=[json.loads(line) for line in z.read(member).splitlines() if line.strip()]
            assert len(raw)==(3600 if number==1 else 720)
            assert all(r['gold_label'] in LABELS and r['sentence'].strip() for r in raw)
            ids=[r['text_id'] for r in raw];texts=[' '.join(r['sentence'].split()) for r in raw]
            assert len(set(ids))==len(ids)
            key=f'dynasent_round{number}'
            gold=np.array([LABELS.index(r['gold_label']) for r in raw])
            before=time.perf_counter()
            a=np.array([old.sentiment(t)['compound'] for t in texts])
            b=np.array([new.polarity_scores(t)['compound'] for t in texts])
            prediction_seconds=time.perf_counter()-before
            frame=pd.DataFrame({'item_id':ids,'gold_label':[LABELS[g] for g in gold],
                'archived_compound':a,'maintained_compound':b,
                'archived_label':[LABELS[g] for g in classify(a)],'maintained_label':[LABELS[g] for g in classify(b)]})
            frame.to_csv(ROOT/f'results/{key}-scores.csv',index=False)
            benchmark[key]={'n':len(raw),'class_counts':dict(Counter(frame.gold_label)),
                'archived':metrics(gold,classify(a)),'maintained':metrics(gold,classify(b)),
                'uncertainty':bootstrap(gold,classify(a),classify(b)),
                'prediction_seconds':prediction_seconds,
                'majority_baseline_accuracy':float(np.bincount(gold).max()/len(gold)),
                'all_neutral_baseline_macro_f1':metrics(gold,np.ones(len(gold),dtype=int))['macro_f1']}
            quality[key]={'empty_texts':0,'duplicate_ids':len(ids)-len(set(ids)),
                'duplicate_normalised_texts':len(texts)-len(set(map(normalise_text,texts))),
                'original_text_overlap':sum(normalise_text(t) in original_texts for t in texts),
                'whitespace_changed':sum(a['sentence']!=b for a,b in zip(raw,texts)),
                'missing_or_invalid_labels':0,'official_split_preserved':True}
            frame['text']=texts;frame['split']=key;bench_frames.append(frame)
            if number==2:
                # Balanced sample selected before model judgement. Gold labels are
                # used for sampling only and omitted from the judge input.
                rng=random.Random(SEED)
                ix=[]
                for cls in range(3):ix+=rng.sample(list(np.flatnonzero(gold==cls)),20)
                rng.shuffle(ix)
                inputs=[{'item_id':ids[i],'text':texts[i]} for i in ix]
                (ROOT/'annotations/llm_dynasent_input.json').write_text(json.dumps(inputs,indent=2)+'\n')
                pd.DataFrame([{'item_id':ids[i],'gold_label':LABELS[gold[i]]} for i in ix]).to_csv(ROOT/'results/llm_dynasent_reference.csv',index=False)
    dump('benchmark-results.json',benchmark);dump('data-quality.json',quality)
    constructed=pd.read_csv(ROOT/'data/constructed.csv')
    constructed['archived_compound']=[old.sentiment(t)['compound'] for t in constructed.text]
    constructed['maintained_compound']=[new.polarity_scores(t)['compound'] for t in constructed.text]
    for v in ['archived','maintained']:constructed[f'{v}_label']=[LABELS[k] for k in classify(constructed[f'{v}_compound'])]
    constructed.to_csv(ROOT/'results/constructed-scores.csv',index=False)
    diagnostics=[]
    for split in ['development','test']:
        data=constructed[constructed.split==split]
        for version in ['archived','maintained']:
            for tone in ['negative','neutral','positive']:
                families=data[data.design_base_tone==tone]
                base=families[families.condition=='base'].set_index('family_id')[f'{version}_compound']
                for condition in ['negation','modifier','capitals','punctuation','contrast']:
                    variant=families[families.condition==condition].set_index('family_id')[f'{version}_compound']
                    delta=variant-base;sign={'negative':-1,'neutral':0,'positive':1}[tone]
                    # Predeclared design checks; they are NOT accuracy or validation.
                    expected=0 if sign==0 else (-sign if condition in ['negation','contrast'] else sign)
                    passed=(np.abs(delta)<=1e-8) if expected==0 else delta*expected>1e-8
                    if tone=='neutral' and condition=='contrast':passed=None
                    diagnostics.append({'split':split,'implementation':version,'base_design_tone':tone,
                        'condition':condition,'families':len(delta),'mean_score_delta':float(delta.mean()),
                        'design_direction_check_passed':None if passed is None else int(passed.sum()),
                        'interpretation':'AI-authored drafting hypothesis; independent human validation pending'})
    dump('constructed-diagnostics.json',diagnostics)
    # Keep short error examples in the private working files, not the public
    # source package. Store IDs and predictions in public tables for retrieval.
    errors=pd.concat(bench_frames,ignore_index=True)
    errors=errors[errors.gold_label!=errors.archived_label]
    errors.to_csv(cache/'benchmark_errors_with_text.csv',index=False)
    errors.drop(columns='text').head(30).to_csv(ROOT/'results/error-example-ids.csv',index=False)
    versions={m:__import__(m).__version__ for m in ['numpy','pandas','scipy','sklearn','matplotlib']}
    dump('final-run-metadata.json',{'run_date_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        'python':platform.python_version(),'platform':platform.platform(),'packages':versions,
        'vader_source_commit':audit.COMMIT,'dynasent_commit':DYNA_COMMIT,'dynasent_sha256':DYNA_SHA,
        'seed':SEED,'bootstrap_replicates':REPLICATES,'classification_thresholds':[-.05,.05],
        'model_training':False,'threshold_tuning':False,'original_text_count':23703,'benchmark_text_count':4320,
        'constructed_text_count':288,'new_benchmark_scored':True,'constructed_scored':True,
        'human_annotation_completed':False,
        'public_github_repository_verified':False,
        'elapsed_seconds':time.perf_counter()-start})
    print(json.dumps({k:{'n':v['n'],'archived_f1':v['archived']['macro_f1'],
        'maintained_f1':v['maintained']['macro_f1']} for k,v in benchmark.items()},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=ROOT/'.cache')
    p.add_argument('--dynasent-zip',type=Path);args=p.parse_args()
    run(args.cache.resolve(),args.dynasent_zip)
