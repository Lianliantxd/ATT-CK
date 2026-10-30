"""Read-only, in-process controlled investigation tools. No model or gold access.
Host must expose call()/initial_observation() JSON only, never the Python object.
"""
import collections
import copy
import json
import math
from functools import lru_cache
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parent / 'research3_technique_strong_baselines_generalization02'
TOKEN_RE = re.compile(r'\w+|[^\w\s]', re.UNICODE)
WORD_RE = re.compile(r'\w+', re.UNICODE)
BUDGETS = {'S': (2, 20, 2048), 'M': (4, 40, 4096)}
TOOLS = {
 'search_events': {'source_type','keywords','time_range','max_results'},
 'get_event_context': {'event_id','before','after'},
 'search_related_entities': {'entity_type','value','max_results'},
 'retrieve_attack_technique': {'technique_id'},
 'submit_technique_ranking': {'ranking','evidence_ids'},
}

def proxy_tokens(text):
    return len(TOKEN_RE.findall(text))

def clip(text, limit):
    matches=list(TOKEN_RE.finditer(text))
    return (text,False) if len(matches)<=limit else (text[:matches[limit-1].end()] if limit else '',True)

@lru_cache(maxsize=1)
def _metadata():
    # Manifest has metadata only: screen excluded scope before opening predictions.
    allow={}
    with (OLD/'datasets/manifests/ALLOWLISTED_MEMBERS.jsonl').open() as f:
        for line in f:
            r=json.loads(line)
            if r['simulation_id'].split('_')[0]=='1' and int(r['step_id']) in (35,36,37):
                raise ValueError('Forbidden scope in allowlist')
            allow[r['source_id']]=(r['simulation_id'],str(r['step_id']),r['source_type'])
    return allow

@lru_cache(maxsize=2)
def _offsets(kind):
    if kind not in ('sampled','full'): raise ValueError('Invalid input view')
    path=OLD/f'datasets/p2_v2/prediction_{kind}.jsonl'
    offsets=[]
    with path.open('rb') as f:
        while True:
            offset=f.tell()
            if not f.readline(): break
            offsets.append(offset)
    if len(offsets)!=385: raise ValueError('Unexpected episode count')
    stat=path.stat()
    return tuple(offsets),stat.st_size,stat.st_mtime_ns

def _row(kind,index):
    if type(index) is not int or not 0<=index<385: raise ValueError('Invalid episode index')
    expected=f'v2_{kind}_{index:04d}'
    path=OLD/f'datasets/p2_v2/prediction_{kind}.jsonl'
    offsets,size,modified=_offsets(kind)
    stat=path.stat()
    if (stat.st_size,stat.st_mtime_ns)!=(size,modified): raise ValueError('Input changed after offset indexing')
    # Offsets contain no event text. Only requested record is deserialized.
    with path.open('rb') as f:
        f.seek(offsets[index]);row=json.loads(f.readline())
    if row['sample_id']!=expected: raise ValueError('Unexpected input ordering')
    return row

def create_episode(index, budget='S', initialization_max_proxy_tokens=2048):
    allow=_metadata()
    sampled,full=_row('sampled',index),_row('full',index)
    scopes=set()
    for row in (sampled,full):
        for src in row['sources']:
            meta=allow.get(src['source_id'])
            if not meta or meta[2]!=src['source_type']: raise ValueError('Unallowlisted source')
            scopes.add(meta[:2])
    if len(scopes)!=1: raise ValueError('Cross-episode sources')
    return AttackTechniqueInvestigationEnvironment(sampled,full,
        json.loads((OLD/'knowledge/K2_DESCRIPTION_16_1.json').read_text()),budget,
        initialization_max_proxy_tokens,scope=next(iter(scopes)))

class AttackTechniqueInvestigationEnvironment:
    def __init__(self,sampled,full,knowledge,budget='S',initialization_max_proxy_tokens=2048,scope=None):
        if budget not in BUDGETS: raise ValueError('Unknown budget')
        if type(initialization_max_proxy_tokens) is not int or not 0<=initialization_max_proxy_tokens<=8192: raise ValueError('Invalid initial budget')
        self._limits=BUDGETS[budget]; self._knowledge=dict(knowledge); self._scope=scope
        self._events={}; self._source_order={}; self._seen=set(); self._returned=set()
        self._seen_text=set(); self._query_signatures=set(); self.trace=[]; self.submission=None
        self._cost={'query_calls':0,'knowledge_calls':0,'returned_log_proxy_tokens':0,
                    'returned_knowledge_proxy_tokens':0,'new_unique_rows':0,'returned_rows':0,
                    'duplicate_rows':0,'duplicate_text_rows':0,'duplicate_queries':0,
                    'initial_proxy_tokens':0,'initial_rows':0,'errors':0,'submission_attempts':0}
        for src in full['sources']:
            ids=[]
            for line in src['lines']:
                event={'event_id':line['line_id'],'source_type':src['source_type'],'source_id':src['source_id'],'text':line['text']}
                if event['event_id'] in self._events: raise ValueError('Duplicate native event ID')
                self._events[event['event_id']]=event; ids.append(event['event_id'])
            self._source_order[src['source_id']]=ids
        self._sources={e['source_type'] for e in self._events.values()}
        self._initial=[]; remain=initialization_max_proxy_tokens
        for src in sampled['sources']:
            for line in src['lines']:
                e=self._events.get(line['line_id'])
                if e is None or e['text']!=line['text']: raise ValueError('Sampled/full mismatch')
                if not remain: break
                txt,trunc=clip(e['text'],remain); out={**e,'text':txt,'truncated':trunc}
                self._initial.append(out); self._seen.add(e['event_id']); self._returned.add(e['event_id']); self._seen_text.add(txt)
                used=proxy_tokens(txt);remain-=used;self._cost['initial_proxy_tokens']+=used;self._cost['initial_rows']+=1
        self._terms={eid:collections.Counter(WORD_RE.findall(e['text'].lower())) for eid,e in self._events.items()}
        self._df=collections.Counter(t for counts in self._terms.values() for t in counts)
        self._avgdl=sum(map(lambda c:sum(c.values()),self._terms.values()))/max(1,len(self._terms))

    def initial_observation(self):
        return {'events':copy.deepcopy(self._initial),'source_types':sorted(self._sources),
                'token_accounting':'regex_proxy_NOT_MODEL_TOKENS',
                'knowledge_ids':sorted(self._knowledge),'budget':self.cost()}

    def cost(self): return {**self._cost,'query_call_limit':self._limits[0],
        'new_row_limit':self._limits[1],'returned_log_proxy_token_limit':self._limits[2],
        'knowledge_proxy_token_limit':4096}

    def _return_events(self,events):
        out=[]
        for e in events:
            eid=e['event_id']; new=eid not in self._seen
            if new and self._cost['new_unique_rows']>=self._limits[1]: break
            remain=self._limits[2]-self._cost['returned_log_proxy_tokens']
            if remain<=0: break
            txt,trunc=clip(e['text'],remain)
            self._cost['duplicate_rows']+=int(eid in self._returned)
            self._cost['duplicate_text_rows']+=int(txt in self._seen_text)
            self._cost['new_unique_rows']+=int(new);self._cost['returned_rows']+=1
            self._cost['returned_log_proxy_tokens']+=proxy_tokens(txt)
            self._seen.add(eid);self._returned.add(eid);self._seen_text.add(txt)
            out.append({**e,'text':txt,'truncated':trunc})
        return {'events':out,'budget':self.cost()}

    @staticmethod
    def _count(value,lo=0,hi=40):
        if type(value) is not int or not lo<=value<=hi: raise ValueError('Integer out of range')
        return value

    @staticmethod
    def _literal(value):
        if not isinstance(value,str) or not value or len(value)>200: raise ValueError('Invalid literal')
        # Never interpreted as a path, query language, or executable expression.
        if any(x in value.lower() for x in ('../','..\\',';','select ','union ','drop ','reference','gold','ground_truth')):
            raise ValueError('Unsupported query syntax')
        return value

    def call(self,name,arguments):
        record={'sequence':len(self.trace)+1,'tool':name,'arguments':copy.deepcopy(arguments)}
        try:
            if name=='submit_technique_ranking': self._cost['submission_attempts']+=1
            else:
                self._cost['query_calls']+=1
                if self._cost['query_calls']>self._limits[0]: raise ValueError('Query call budget exceeded')
            if self.submission is not None: raise ValueError('Episode already submitted')
            if name not in TOOLS or not isinstance(arguments,dict) or set(arguments)-TOOLS[name]: raise ValueError('Unknown tool or fields')
            sig=json.dumps([name,arguments],sort_keys=True)
            self._cost['duplicate_queries']+=int(sig in self._query_signatures);self._query_signatures.add(sig)
            result=getattr(self,'_'+name)(**arguments)
            record['status']='ok';record['result']=copy.deepcopy(result)
        except (ValueError,TypeError,KeyError) as exc:
            self._cost['errors']+=1;result={'error':str(exc),'budget':self.cost()};record['status']='rejected';record['result']=copy.deepcopy(result)
        record['cost']=self.cost();self.trace.append(record)
        return result

    def _search_events(self,source_type,keywords,time_range=None,max_results=10):
        if source_type not in self._sources and source_type!='all': raise ValueError('Unknown source type')
        if time_range is not None: raise ValueError('time_range unsupported: heterogeneous timestamps not normalized')
        n=self._count(max_results,1)
        if not isinstance(keywords,list) or not 1<=len(keywords)<=32: raise ValueError('Keywords must be literal string array')
        terms=set(t for k in keywords for t in WORD_RE.findall(self._literal(k).lower()))
        if not terms: raise ValueError('No literal tokens')
        count=len(self._events)
        def score(eid):
            c=self._terms[eid];dl=sum(c.values())
            return sum(math.log(1+(count-self._df[t]+.5)/(self._df[t]+.5))*
                (c[t]*2.5)/(c[t]+1.5*(.25+.75*dl/max(self._avgdl,1))) for t in terms if c[t])
        ranked=[(score(eid),eid) for eid,e in self._events.items() if source_type=='all' or e['source_type']==source_type]
        ranked.sort(key=lambda x:(-x[0],x[1]));selected=ranked[:n]
        result=self._return_events([self._events[eid] for _,eid in selected])
        result['search']='BM25 k1=1.5 b=0.75 binary_query_tf; stable event_id tie break'
        result['lexical_match']=bool(selected and selected[0][0]>0)
        return result

    def _get_event_context(self,event_id,before=1,after=1):
        self._count(before,0,20);self._count(after,0,20)
        if event_id not in self._seen: raise ValueError('Unknown or unseen event ID')
        e=self._events[event_id];ids=self._source_order[e['source_id']];i=ids.index(event_id)
        return self._return_events([self._events[eid] for eid in ids[max(0,i-before):i+after+1]])

    def _search_related_entities(self,entity_type,value,max_results=10):
        if entity_type not in ('ip','domain','process','path','user','literal'): raise ValueError('Unsupported entity type')
        value=self._literal(value);n=self._count(max_results,1)
        # Native literal string equality containment only; no inferred shared identity.
        return self._return_events([e for eid,e in sorted(self._events.items()) if value in e['text']][:n])

    def _retrieve_attack_technique(self,technique_id):
        self._cost['knowledge_calls']+=1
        if technique_id not in self._knowledge: raise ValueError('Unknown public technique ID')
        remain=4096-self._cost['returned_knowledge_proxy_tokens']
        if remain<=0: raise ValueError('Knowledge token budget exceeded')
        txt,trunc=clip(self._knowledge[technique_id],remain)
        self._cost['returned_knowledge_proxy_tokens']+=proxy_tokens(txt)
        return {'technique_id':technique_id,'text':txt,'truncated':trunc,'budget':self.cost()}

    def _submit_technique_ranking(self,ranking,evidence_ids):
        if not isinstance(ranking,list) or len(ranking)!=10 or any(not isinstance(x,str) for x in ranking) or len(set(ranking))!=10 or any(x not in self._knowledge for x in ranking): raise ValueError('Ranking must contain 10 unique candidate IDs')
        if not isinstance(evidence_ids,list) or any(not isinstance(x,str) or x not in self._seen for x in evidence_ids): raise ValueError('Evidence must cite seen native IDs')
        self.submission={'ranking':ranking[:],'evidence_ids':list(dict.fromkeys(evidence_ids))}
        return {'accepted':True,'ranking_count':10}
