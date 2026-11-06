"""Create LaTeX evidence tables directly from saved experiment outputs."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def write(name,lines):
    (ROOT/'report'/name).write_text('\n'.join(lines)+'\n')

def main():
    original=pd.read_csv(ROOT/'results/original-data-results.csv')
    names={'tweets':'Tweet-like','movie_reviews':'Movie','product_reviews':'Product','nyt_editorials':'Editorial'}
    f1=[.96,.61,.63,.55]
    lines=[r'\begin{tabular}{lrrrrrr}',r'\toprule',r'Corpus & Texts & Paper $r$ & Archived $r$ & Maintained $r$ & Paper F1 & Provisional macro-F1\\',r'\midrule']
    for (_,row),pf in zip(original.iterrows(),f1):
        lines.append(f"{names[row['domain']]} & {row['n']:,} & {row['paper_r']:.3f} & {row['archived_r']:.6f} & {row['maintained_r']:.6f} & {pf:.2f} & {row['archived_macro_f1_provisional']:.4f} "+r'\\')
    write('table_original.tex',lines+[r'\bottomrule',r'\end{tabular}'])
    audit=json.loads((ROOT/'results/classification-policy-audit.json').read_text())
    lines=[r'\begin{tabular}{lrrrr}',r'\toprule',r'Corpus & $h/4$ macro & $h$ macro & $h$ weighted & Paper F1\\',r'\midrule']
    for key,pf in zip(names,f1):
        rows={r['gold_policy']:r for r in audit if r['corpus']==key and r['implementation']=='archived'}
        a,b=rows['human_mean_div4'],rows['human_mean_raw']
        lines.append(f"{names[key]} & {a['macro_f1']:.3f} & {b['macro_f1']:.3f} & {b['weighted_f1']:.3f} & {pf:.2f} "+r'\\')
    write('table_policy.tex',lines+[r'\bottomrule',r'\end{tabular}'])
    results=json.loads((ROOT/'results/benchmark-results.json').read_text())
    lines=[r'\begin{tabular}{llrrrr}',r'\toprule',r'Test split & Version & $n$ & Accuracy & Macro-F1 & 95\% interval\\',r'\midrule']
    for key,r in results.items():
        for v in ['archived','maintained']:
            ci=r['uncertainty'][f'{v}_macro_f1_ci95']
            lines.append(f"Round {key[-1]} & {v.title()} & {r['n']:,} & {r[v]['accuracy']:.4f} & {r[v]['macro_f1']:.4f} & [{ci[0]:.3f}, {ci[1]:.3f}] "+r'\\')
    write('table_benchmark.tex',lines+[r'\bottomrule',r'\end{tabular}'])
    lines=[r'\begin{tabular}{lrrr}',r'\toprule',r'Class & Precision & Recall & F1\\',r'\midrule']
    for label in ['negative','neutral','positive']:
        r=results['dynasent_round2']['archived']['classification_report'][label]
        lines.append(f"{label.title()} & {r['precision']:.3f} & {r['recall']:.3f} & {r['f1-score']:.3f} "+r'\\')
    write('table_class.tex',lines+[r'\bottomrule',r'\end{tabular}'])
    d=json.loads((ROOT/'results/constructed-diagnostics.json').read_text())
    lines=[r'\begin{tabular}{lrrrr}',r'\toprule',r'Variant & Pos. $\Delta$ & Check & Neg. $\Delta$ & Check\\',r'\midrule']
    for condition in ['negation','modifier','capitals','punctuation','contrast']:
        p=next(r for r in d if r['split']=='test' and r['implementation']=='archived' and r['base_design_tone']=='positive' and r['condition']==condition)
        n=next(r for r in d if r['split']=='test' and r['implementation']=='archived' and r['base_design_tone']=='negative' and r['condition']==condition)
        lines.append(f"{condition.title()} & {p['mean_score_delta']:+.3f} & {p['design_direction_check_passed']}/12 & {n['mean_score_delta']:+.3f} & {n['design_direction_check_passed']}/12 "+r'\\')
    write('table_diagnostic.tex',lines+[r'\bottomrule',r'\end{tabular}'])
    judge=json.loads((ROOT/'results/llm-dynasent-results.json').read_text())
    lines=[r'\begin{tabular}{lrr}',r'\toprule',r'System on the same 60 items & Accuracy & Macro-F1\\',r'\midrule']
    for key,label in [('archived_on_same_items','Archived VADER'),('maintained_on_same_items','Maintained VADER'),('judge','Assistant judge')]:
        r=judge[key];lines.append(f"{label} & {r['accuracy']:.3f} & {r['macro_f1']:.3f} "+r'\\')
    write('table_judge.tex',lines+[r'\bottomrule',r'\end{tabular}'])
    print('Exported six report tables from observed results.')

if __name__=='__main__':main()
