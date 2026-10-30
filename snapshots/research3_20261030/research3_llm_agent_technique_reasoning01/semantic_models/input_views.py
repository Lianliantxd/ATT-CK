"""GT-free common input views. Proxy budgets are NOT model tokenizer budgets."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

TOKEN = re.compile(r'\w+|[^\w\s]', re.UNICODE)
FIELD = re.compile(r'(?P<key>[A-Za-z_][\w.-]*)=(?P<value>"[^"\n]*"|\'[^\'\n]*\'|[^\s]+)')
ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parent / 'research3_technique_strong_baselines_generalization02'

def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

def count(text: str) -> int:
    return len(TOKEN.findall(text))

def native_lines(record: dict) -> list[dict]:
    if set(record) != {'sample_id', 'text', 'sources'}:
        raise ValueError('Only frozen prediction schema accepted; references/GT prohibited')
    rows = []
    for source in record['sources']:
        for row in source['lines']:
            text = row['text']
            if row.get('text_hash') != digest(text):
                raise ValueError('Frozen line hash mismatch')
            rows.append({'source_id': source['source_id'], 'source_type': source['source_type'],
                         'line_id': row['line_id'], 'text': text, 'text_hash': digest(text)})
    return rows

def select(rows: list[dict], budget: int, rule: str) -> list[dict]:
    spans = [(ri,m.start(),m.end()) for ri,row in enumerate(rows) for m in TOKEN.finditer(row['text'])]
    n = len(spans)
    if rule == 'prefix' or n <= budget:
        chosen = list(range(min(n,budget)))
    elif rule == 'window':
        # Eight fixed equispaced windows; total observations <= same budget.
        k = min(8,budget)
        widths = [budget//k+(i<budget%k) for i in range(k)]
        starts = [round(i*(n-budget)/(k-1))+sum(widths[:i]) for i in range(k)] if k>1 else [0]
        chosen = [j for s,w in zip(starts,widths) for j in range(s,s+w)]
    else:
        raise ValueError(rule)
    groups = []
    for j in chosen:
        ri,a,b = spans[j]
        if groups and groups[-1]['row_index']==ri and groups[-1]['token_end']==j:
            groups[-1]['char_end']=b;groups[-1]['token_end']=j+1
        else:
            groups.append({'row_index':ri,'char_start':a,'char_end':b,'token_start':j,'token_end':j+1})
    result = []
    for g in groups:
        row = rows[g['row_index']]
        text = row['text'][g['char_start']:g['char_end']]
        result.append({**g, **{k:row[k] for k in ['source_id','source_type','line_id','text_hash']},
                       'text':text,'fragment_hash':digest(text)})
    return result

def fields(fragment: dict) -> list[dict]:
    """Extract literal native key=value fields only; duplicate keys remain distinct."""
    return [{'key':m['key'],'value':m['value'],'char_start':fragment['char_start']+m.start(),
             'char_end':fragment['char_start']+m.end()} for m in FIELD.finditer(fragment['text'])]

def render(fragments: list[dict]) -> dict[str,str]:
    v0='\n'.join(f['text'] for f in fragments)
    structured=[]
    for f in fragments:
        fs=fields(f)
        # Field names and values are verbatim: action/actor/outcome never inferred.
        structured.append(' '.join(x['key']+'='+x['value'] for x in fs) if fs else f['text'])
    # V2: deterministic source-local token windows, identical selected observations.
    chunks=[]
    for f in fragments:
        spans=list(TOKEN.finditer(f['text']))
        chunks.extend(f['text'][spans[i].start():spans[min(i+256,len(spans))-1].end()] for i in range(0,len(spans),256))
    grouped={}
    for f in fragments:grouped.setdefault(f['source_type'],[]).append(f['text'])
    return {'V0':'\n'.join(f['text'] for f in fragments),'V1':'\n'.join(structured),
            'V2':'\n\n'.join(chunks),'V3':'\n'.join(k+':\n'+'\n'.join(v) for k,v in grouped.items())}

def make_views(record: dict, budget: int = 2048) -> dict:
    rows=native_lines(record)
    total=sum(count(r['text']) for r in rows)
    variants={}
    for rule in ['prefix','window']:
        # All representations share exactly the same selected raw fragments.
        n=min(total,budget)
        while True:
            fs=select(rows,n,rule);texts=render(fs)
            over=max(count(x) for x in texts.values())-budget
            if over<=0:break
            n=max(0,n-max(over,1))
        mappings=[]
        for f in fs:
            mappings.append({**{k:v for k,v in f.items() if k!='text'},'literal_fields':fields(f)})
        chunks=[]
        for fi,f in enumerate(fs):
            ts=list(TOKEN.finditer(f['text']))
            for i in range(0,len(ts),256):
                a,b=ts[i].start(),ts[min(i+256,len(ts))-1].end()
                chunks.append({'fragment_index':fi,'source_id':f['source_id'],'line_id':f['line_id'],
                               'char_start':f['char_start']+a,'char_end':f['char_start']+b,'chunk_hash':digest(f['text'][a:b])})
        variants[rule]={'views':texts,'view_proxy_counts':{k:count(v) for k,v in texts.items()},
                        'selected_native_proxy_tokens':n,'omitted_native_proxy_tokens':total-n,
                        'truncated':n<total,'line_mappings':mappings,'V2_chunk_mappings':chunks,
                        'source_groups':{s:[i for i,f in enumerate(fs) if f['source_type']==s] for s in sorted({f['source_type'] for f in fs})}}
    return {'sample_id':record['sample_id'],'status':'INPUT_PREPARATION_NOT_MODEL_INFERENCE',
            'proxy_unit':'regex_word_or_punctuation_NOT_MODEL_TOKENS','budget':budget,
            'raw_pool_hash':digest(json.dumps(rows,ensure_ascii=False,sort_keys=True)),
            'raw_line_count':len(rows),'raw_proxy_tokens':total,'variants':variants}

def rebuild_with_tokenizer(record: dict, tokenizer, budget: int=2048) -> dict:
    """After admission, enforce actual tokenizer caps across ALL paired views.
    Caller must count prompt/special/pair/knowledge overhead separately.
    """
    proxy=budget
    while True:
        out=make_views(record,proxy)
        actual={r:{v:len(tokenizer.encode(t,add_special_tokens=False)) for v,t in q['views'].items()} for r,q in out['variants'].items()}
        maximum=max((n for q in actual.values() for n in q.values()),default=0)
        if maximum<=budget:
            out['actual_tokenizer_counts']=actual;out['actual_log_token_budget']=budget
            out['budget_status']='ACTUAL_TOKENIZER_LOG_ONLY';return out
        proxy=max(0,proxy-max(1,round(proxy*(maximum-budget)/maximum)))

def rebuild_with_tokenizers(record: dict, tokenizers: dict, budget: int=2048) -> dict:
    """Common observation intersection under every admitted tokenizer's log budget.
    tokenizers maps audited model/revision IDs to tokenizer instances. Prompt and
    knowledge overhead must be reserved independently by each inference runner.
    """
    if not tokenizers:raise ValueError('At least one admitted tokenizer required')
    proxy=budget
    while True:
        out=make_views(record,proxy)
        counts={name:{r:{v:len(tok.encode(t,add_special_tokens=False)) for v,t in q['views'].items()}
                      for r,q in out['variants'].items()} for name,tok in tokenizers.items()}
        maximum=max((n for c in counts.values() for q in c.values() for n in q.values()),default=0)
        if maximum<=budget:
            out['actual_tokenizer_counts_by_model']=counts
            out['actual_log_token_budget']=budget
            out['budget_status']='SHARED_OBSERVATIONS_ALL_ADMITTED_TOKENIZERS_LOG_ONLY'
            return out
        if proxy==0:raise ValueError('Tokenizer generates tokens for empty input; budget infeasible')
        proxy=max(0,proxy-max(1,round(proxy*(maximum-budget)/maximum)))

def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,default=ROOT/'semantic_models/input_views')
    args=parser.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    paths={'P0':OLD/'datasets/p0_prediction.jsonl','P1':OLD/'datasets/p1_resampled/prediction.jsonl',
           'P2_SAMPLED':OLD/'datasets/p2_v2/prediction_sampled.jsonl'}
    manifest={'status':'INPUT_PREPARATION_NOT_MODEL_INFERENCE','actual_model_tokenization':'PENDING_MODEL_ADMISSION',
              'budget':2048,'proxy_regex':TOKEN.pattern,'views':['V0','V1','V2','V3'],'rules':['prefix','window'],
              'knowledge':'K2_DESCRIPTION_16_1','candidate_count':216,'datasets':{}}
    for name,path in paths.items():
        n=0;trunc={'prefix':0,'window':0};maxima={r:0 for r in trunc}
        target=args.output_dir/(name+'.jsonl')
        with path.open() as src,target.open('w') as dst:
            for line in src:
                out=make_views(json.loads(line));dst.write(json.dumps(out,ensure_ascii=False)+'\n');n+=1
                for r in trunc:
                    trunc[r]+=out['variants'][r]['truncated'];maxima[r]=max(maxima[r],max(out['variants'][r]['view_proxy_counts'].values()))
        manifest['datasets'][name]={'input':str(path),'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                                   'output':str(target),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                                   'sample_count':n,'truncated_sample_counts':trunc,'max_view_proxy_tokens':maxima}
    (ROOT/'data_manifests/NEURAL_INPUT_PROTOCOL.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
