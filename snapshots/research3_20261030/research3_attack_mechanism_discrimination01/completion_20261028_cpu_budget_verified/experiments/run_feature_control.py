"""Actual count-controlled CPU retrieval. Predictor never opens reference labels."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from common import *
from frozen_engine import Index,chars,words
from frozen_extractor import parse,relations,render

VIEWS=['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL']
def fits(text,ngram=2048,word=256):return sum(chars(text).values())<=ngram and len(words(text))<=word
def docclip(text):
    lo,hi=0,len(text)
    while lo<hi:
        mid=(lo+hi+1)//2
        if fits(text[:mid],1024,128):lo=mid
        else:hi=mid-1
    return text[:lo]

def main():
    started=time.monotonic();assert not (ROOT/'results/FEATURE_PREDICTIONS.jsonl').exists()
    samples=[];budgets=[]
    for row in records(ROOT/'frozen_inputs/LITERAL_EVENTS.jsonl'):
        original=row['events'];total=sum(len(e['evidence_source']['native_fragment']) for e in original)
        def make(n):
            ev=[];left=n
            for old in original:
                if left<=0:break
                source=old['evidence_source'];raw=source['native_fragment'];take=min(left,len(raw));left-=take
                fragment={'text':raw[:take],'source_id':old['source_id'],'source_type':old['source_type'],
                    'line_id':source['line_id'],'char_start':source['char_range'][0],'text_hash':source['native_line_sha256'],
                    'fragment_truncated':take<len(raw) or 'NATIVE_FRAGMENT_TRUNCATED' in old['uncertainty']}
                ev.append(parse(fragment,source['input_file_sha256']))
            rel=relations(ev);views={v:render(ev,rel,v) for v in VIEWS}
            return ev,rel,views
        lo,hi=1,total
        assert total and all(fits(v) for v in make(1)[2].values())
        while lo<hi:
            mid=(lo+hi+1)//2
            if all(fits(v) for v in make(mid)[2].values()):lo=mid
            else:hi=mid-1
        ev,rel,views=make(lo);assert all(fits(v) for v in views.values())
        samples.append({'sample_id':row['sample_id'],'views':views})
        for name,text in views.items():budgets.append({'sample_id':row['sample_id'],'view':name,'common_native_characters':lo,
            'inherited_common_characters':total,'events':len(ev),'relations':len(rel),'char_ngram_occurrences':sum(chars(text).values()),
            'BM25_word_tokens':len(words(text)),'UTF8_bytes':len(text.encode()),'GTE_tokens':'NOT_MEASURED',
            'text_sha256':hashlib.sha256(text.encode()).hexdigest()})
    docs={k:{t:docclip(v) for t,v in d.items()} for k,d in read(ROOT/'frozen_inputs/KNOWLEDGE.json').items()}
    assert all(len(d)==216 for d in docs.values())
    dump('frozen_inputs/FEATURE_VIEWS.json',samples);dump('frozen_inputs/FEATURE_KNOWLEDGE.json',docs)
    csvout('results/FEATURE_INPUT_BUDGETS.csv',budgets)
    dump('manifests/FEATURE_INPUT_FREEZE.json',{'code_sha256':sha(Path(__file__)),'extractor_sha256':sha(ROOT/'src/frozen_extractor.py'),
        'index_sha256':sha(ROOT/'src/frozen_engine.py'),'input_sha256':sha(ROOT/'frozen_inputs/FEATURE_VIEWS.json'),
        'knowledge_sha256':sha(ROOT/'frozen_inputs/FEATURE_KNOWLEDGE.json'),'new_log_records':0,'Gold_read':False})
    runtimes=[]
    with (ROOT/'results/FEATURE_PREDICTIONS.jsonl').open('x') as output:
        for mode in ['char','bm25']:
            for kname,knowledge in docs.items():
                idx=Index(knowledge,mode)
                for view in VIEWS:
                    begin=time.monotonic();method=mode.upper()+'__'+view+'__'+kname
                    for row in samples:
                        score=idx.score(row['views'][view]);order=sorted(range(216),key=lambda i:(-score[i],idx.ids[i]))
                        output.write(json.dumps({'sample_id':row['sample_id'],'method':method,'algorithm':mode,'input_view':view,
                            'knowledge':kname,'predictions':[idx.ids[i] for i in order],
                            'score_top10':[score[i] for i in order[:10]],'candidate_count':216,'model_calls':0})+'\n')
                    output.flush();runtimes.append({'method':method,'queries':len(samples),'seconds':time.monotonic()-begin})
                    print(method,'complete',flush=True)
    dump('manifests/FEATURE_PREDICTION_FREEZE.json',{'prediction_sha256':sha(ROOT/'results/FEATURE_PREDICTIONS.jsonl'),
        'conditions':len(runtimes),'queries_each':len(samples),'new_model_forwards':0,'wall_seconds':time.monotonic()-started})
    csvout('results/FEATURE_RUNTIME.csv',runtimes)

if __name__=='__main__':main()
