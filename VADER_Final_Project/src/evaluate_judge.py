"""Score preserved assistant judgements; explicitly separate them from human gold."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from run_experiments import LABELS,metrics,bootstrap
ROOT=Path(__file__).resolve().parents[1]

def compare_constructed_human(frame):
    """Score only real resolved reference labels supplied by the human workflow."""
    valid=frame[frame.final_label.isin(LABELS)].copy()
    if valid.empty:
        return {'n_resolved':0,'n_ambiguous':len(frame),'metrics':None,'cohen_kappa':None}
    gold=valid.final_label.map({v:i for i,v in enumerate(LABELS)}).to_numpy()
    predicted=valid.judge_label.map({v:i for i,v in enumerate(LABELS)}).to_numpy()
    k=float(cohen_kappa_score(gold,predicted,labels=[0,1,2]))
    return {'n_resolved':len(valid),'n_ambiguous':len(frame)-len(valid),
        'metrics':metrics(gold,predicted),'cohen_kappa':k if np.isfinite(k) else None}

def main():
    response=json.loads((ROOT/'annotations/llm_dynasent_responses.json').read_text())
    judge=pd.DataFrame(response).rename(columns={'label':'judge_label'})
    ref=pd.read_csv(ROOT/'results/llm_dynasent_reference.csv')
    scores=pd.read_csv(ROOT/'results/dynasent_round2-scores.csv')
    data=ref.merge(judge,on='item_id',validate='one_to_one').merge(scores[['item_id','archived_label','maintained_label']],on='item_id',validate='one_to_one')
    if len(data)!=60 or not data.judge_label.isin(LABELS).all():raise ValueError('Missing or invalid judge labels')
    encode=lambda x:x.map({v:i for i,v in enumerate(LABELS)}).to_numpy()
    gold,pred,a,b=map(encode,[data.gold_label,data.judge_label,data.archived_label,data.maintained_label])
    results={'status':'completed_within_session_pilot','reference':'Released DynaSent human labels',
        'n':len(data),'sampling':'20 items per gold class, seed 8240; no threshold tuning',
        'judge':metrics(gold,pred),'archived_on_same_items':metrics(gold,a),'maintained_on_same_items':metrics(gold,b),
        'cohen_kappa_judge_vs_released_gold':float(cohen_kappa_score(gold,pred,labels=[0,1,2])),
        'paired_uncertainty_judge_minus_archived':bootstrap(gold,a,pred),
        'caution':'Paired bootstrap returns maintained_* keys for the second prediction array; here the second array is the judge. This small sample is exploratory and may have model pretraining contamination.'}
    # Avoid misleading generic maintained names in the judge-specific artifact.
    u=results.pop('paired_uncertainty_judge_minus_archived')
    results['uncertainty']={'bootstrap_replicates':u['replicates'],'seed':u['seed'],
        'judge_macro_f1_ci95':u['maintained_macro_f1_ci95'],
        'judge_minus_archived_macro_f1_ci95':u['maintained_minus_archived_macro_f1_ci95']}
    results.pop('caution')
    results['limitations']='Single within-session assistant; exact model snapshot and decoding settings not exposed; benchmark familiarity cannot be excluded; not a preregistered independent comparison.'
    (ROOT/'results/llm-dynasent-results.json').write_text(json.dumps(results,indent=2)+'\n')
    data.to_csv(ROOT/'results/llm-dynasent-comparison.csv',index=False)
    constructed=pd.read_csv(ROOT/'results/constructed-scores.csv')
    r=pd.DataFrame(json.loads((ROOT/'annotations/llm_constructed_responses.json').read_text())).rename(columns={'label':'judge_label'})
    d=constructed.merge(r,on='item_id',validate='one_to_one')
    if len(d)!=60:raise ValueError('Constructed judge sample mismatch')
    out={'n':len(d),'human_gold_available':False,'human_agreement_or_accuracy':None,
        'archived_judge_label_agreement':float((d.archived_label==d.judge_label).mean()),
        'maintained_judge_label_agreement':float((d.maintained_label==d.judge_label).mean()),
        'interpretation':'Model-to-model agreement only; the same assistant authored and judged the constructed texts.'}
    reference_path=ROOT/'results/constructed-human-reference.csv'
    completed_path=ROOT/'results/human-results.json'
    if reference_path.exists() and completed_path.exists():
        status=json.loads(completed_path.read_text()).get('status')
        if status=='complete_from_supplied_human_files':
            reference=pd.read_csv(reference_path,keep_default_na=False)
            human=d.merge(reference[['item_id','final_label']],on='item_id',validate='one_to_one')
            if len(human)!=60:raise ValueError('Human reference does not cover the judge sample')
            out['human_gold_available']=True
            out['human_agreement_or_accuracy']=compare_constructed_human(human)
    d.to_csv(ROOT/'results/llm-constructed-comparison.csv',index=False)
    (ROOT/'results/llm-constructed-results.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'judge_vs_dynasent':results['judge']['macro_f1'],'constructed_model_agreement_only':out},indent=2))

if __name__=='__main__':main()
