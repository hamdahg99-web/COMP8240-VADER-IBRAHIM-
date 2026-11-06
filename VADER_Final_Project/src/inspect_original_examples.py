"""Reproduce post-hoc qualitative examples from the original released tweets."""
from pathlib import Path
import argparse,csv,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor'))
import audit_helpers as audit

def run(cache):
    cache.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'vendor/vader2014_py3.py',cache/'vader2014_py3.py')
    archived,maintained=audit.prepare(cache)
    wanted={'4','35','266','431'};records=[]
    for line in (cache/'original/tweets_GroundTruth.txt').read_text().splitlines():
        ident,mean,text=line.split('\t',2)
        if ident in wanted:
            h=float(mean)
            records.append({'id':ident,'text':text,'human_mean':h,
                'reference_policy':'human_mean/4; inclusive +/-0.05 thresholds',
                'derived_reference_class':audit.label(h/4).lower(),
                'archived_compound':archived.sentiment(text)['compound'],
                'maintained_compound':maintained.polarity_scores(text)['compound'],
                'selection':'Post-hoc qualitative illustration, not a prevalence estimate'})
    assert {r['id'] for r in records}==wanted
    with (ROOT/'results/original-qualitative-examples.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    text='not a good day'
    with (ROOT/'results/original-case-probe.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['text','archived_compound','maintained_compound','provenance'])
        w.writerow([text,archived.sentiment(text)['compound'],maintained.polarity_scores(text)['compound'],
            'Post-hoc lowercase probe of original item 431; excluded from aggregate metrics'])
    lines=[r'\begin{tabular}{rlrrrl}',r'\toprule',
        r'ID & Text & Human mean & Archived $c$ & Maintained $c$ & Ref. class\\',r'\midrule']
    for r in records:
        lines.append(f"{r['id']} & {r['text']} & {r['human_mean']:.4f} & {r['archived_compound']:+.4f} & {r['maintained_compound']:+.4f} & {r['derived_reference_class']} "+r'\\')
    lines += [r'\bottomrule',r'\end{tabular}']
    (ROOT/'report/table_original_examples.tex').write_text('\n'.join(lines)+'\n')
    print('Preserved four observed original-data examples and one lowercase diagnostic probe.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=ROOT/'.cache');args=p.parse_args();run(args.cache.resolve())
