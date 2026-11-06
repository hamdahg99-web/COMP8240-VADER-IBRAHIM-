"""Combine each real reader's saved development/test CSVs without changing text."""
from pathlib import Path
import csv
ROOT=Path(__file__).resolve().parents[1]

def main():
    source=list(csv.DictReader((ROOT/'data/constructed.csv').open()))
    reference={r['item_id']:r['text'] for r in source}
    for who in ['A','B']:
        rows=[]
        for split in ['development','test']:
            rows+=list(csv.DictReader((ROOT/f'annotations/annotator_{who}_{split}.csv').open()))
        if len(rows)!=288 or len({r['item_id'] for r in rows})!=288 or {r['item_id'] for r in rows}!=set(reference):
            raise ValueError(f'Reader {who}: IDs or counts do not match the fixed corpus')
        if any(r['text']!=reference[r['item_id']] for r in rows):raise ValueError('Texts were changed')
        fields=['item_id','text','sentiment','intensity','confidence','notes']
        with (ROOT/f'annotations/annotator_{who}.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
        print(f'Reader {who}: {sum(bool(r["sentiment"]) for r in rows)}/288 ratings supplied.')

if __name__=='__main__':main()
