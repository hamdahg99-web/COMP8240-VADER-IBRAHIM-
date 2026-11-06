"""Generate publication figures from recorded numeric results only."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight','pdf.fonttype':42})
colors=['#175a77','#c26937']

def save(fig,name):
    fig.tight_layout();fig.savefig(ROOT/f'figures/{name}.pdf');fig.savefig(ROOT/f'figures/{name}.png',dpi=200);plt.close(fig)

def main():
    original=pd.read_csv(ROOT/'results/original-data-results.csv')
    fig,ax=plt.subplots(figsize=(6.2,2.6))
    x=np.arange(4);w=.24
    for i,(column,label,color) in enumerate([('paper_r','Paper','#939da3'),('archived_r','Archived',colors[0]),('maintained_r','Maintained',colors[1])]):
        ax.bar(x+(i-1)*w,original[column],w,label=label,color=color)
    ax.set(xticks=x,xticklabels=['Tweet-like','Movie','Product','Editorial'],ylabel='Pearson r',ylim=(0,1));ax.legend(frameon=False,ncol=3,loc='upper right')
    save(fig,'replication_correlations')
    results=json.loads((ROOT/'results/benchmark-results.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(6.3,2.6))
    for ax,(key,r) in zip(axes,results.items()):
        m=r['archived'];cm=np.array(m['confusion_matrix']);ax.imshow(cm,cmap='Blues')
        for i in range(3):
            for j in range(3):ax.text(j,i,str(cm[i,j]),ha='center',va='center',color='white' if cm[i,j]>.55*cm.max() else '#1b2630')
        ax.set(xticks=range(3),yticks=range(3),xticklabels=['Neg','Neu','Pos'],yticklabels=['Neg','Neu','Pos'],xlabel='Predicted class',ylabel='Reference class',title=f"Round {key[-1]} (n={r['n']:,})")
    save(fig,'benchmark_confusion')
    fig,ax=plt.subplots(figsize=(6.2,2.6));x=np.arange(2);w=.29
    for i,v in enumerate(['archived','maintained']):
        y=np.array([r[v]['macro_f1'] for r in results.values()]);ci=np.array([r['uncertainty'][f'{v}_macro_f1_ci95'] for r in results.values()])
        ax.bar(x+(i-.5)*w,y,w,yerr=np.vstack([y-ci[:,0],ci[:,1]-y]),label=v.title(),color=colors[i],capsize=4)
    ax.axhline(1/6,color='#808080',ls='--',lw=.8,label='All-neutral baseline')
    ax.set(xticks=x,xticklabels=['DynaSent Round 1','DynaSent Round 2'],ylabel='Macro-F1',ylim=(0,.7));ax.legend(frameon=False,ncol=3,fontsize=8,loc='upper center',bbox_to_anchor=(.5,1.16))
    save(fig,'benchmark_f1')
    data=pd.read_csv(ROOT/'results/constructed-scores.csv');data=data[(data.split=='test')&(data.design_base_tone!='neutral')]
    conditions=['base','negation','modifier','capitals','punctuation','contrast']
    fig,ax=plt.subplots(figsize=(6.2,2.8))
    for i,(tone,style) in enumerate([('positive','-'),('negative','--')]):
        means=[data[(data.design_base_tone==tone)&(data.condition==c)]['archived_compound'].mean() for c in conditions]
        ax.plot(range(6),means,marker='o',ms=3,lw=1.2,ls=style,color=colors[i],label=f'{tone.title()} base design')
    ax.axhline(0,color='#999999',lw=.7);ax.set(xticks=range(6),xticklabels=['Base','Negation','Modifier','Capitals','!!!','Contrast'],ylabel='Mean compound score',ylim=(-.85,.85))
    ax.legend(frameon=False,ncol=2,fontsize=8,loc='lower left');save(fig,'constructed_scores')
    judge=json.loads((ROOT/'results/llm-dynasent-results.json').read_text())
    fig,ax=plt.subplots(figsize=(3.1,2.5));cm=np.array(judge['judge']['confusion_matrix']);ax.imshow(cm,cmap='Blues')
    for i in range(3):
        for j in range(3):ax.text(j,i,str(cm[i,j]),ha='center',va='center',color='white' if cm[i,j]>.55*cm.max() else '#1b2630')
    ax.set(xticks=range(3),yticks=range(3),xticklabels=['Neg','Neu','Pos'],yticklabels=['Neg','Neu','Pos'],xlabel='Assistant judge',ylabel='DynaSent human reference',title='Within-session pilot (n=60)');save(fig,'judge_confusion')
    print('Saved five numeric figure sets.')

if __name__=='__main__':main()
