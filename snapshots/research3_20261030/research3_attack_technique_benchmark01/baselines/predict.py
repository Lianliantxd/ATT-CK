"""Separate predictor process: consumes only prediction view and public knowledge."""
import argparse
import ast
import json
import random
from pathlib import Path
from retrieval import Retriever
p=argparse.ArgumentParser();p.add_argument('--method',required=True);p.add_argument('--inputs',required=True);p.add_argument('--documents',required=True);p.add_argument('--dictionary');p.add_argument('--seed',type=int,default=13);p.add_argument('--output',required=True);a=p.parse_args()
docs=json.loads(Path(a.documents).read_text());ids=sorted(docs)
if a.method=='Random':
    rng=random.Random(a.seed)
    def rank(text):return rng.sample(ids,10)
elif a.method=='KnowHow':
    raw=ast.literal_eval(Path(a.dictionary).read_text());phrases={k:[] for k in ids}
    for k,values in raw.items():
        parent=k.split('.')[0]
        if parent in phrases:phrases[parent].extend(x.lower() for x in values if isinstance(x,str) and x)
    def rank(text):
        text=text.lower()
        return sorted(ids,key=lambda k:(-sum(x in text for x in phrases[k]),k))[:10]
else:
    retriever=Retriever(docs)
    def rank(text):return retriever.rank(text,a.method)
with Path(a.inputs).open() as inp,Path(a.output).open('w') as out:
    for line in inp:
        row=json.loads(line)
        if set(row)!={'sample_id','text'}:raise ValueError('Prediction schema rejects reference fields')
        out.write(json.dumps({'sample_id':row['sample_id'],'predictions':rank(row['text'])})+'\n')
