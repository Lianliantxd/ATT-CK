"""Actual tool controls; no LLM, pretrained model, or policy access to hidden pool.
Developer viewed reference episode 0 schema before implementation (disclosed).
All prediction-time policy code is reference-free; evaluation starts after close.
"""
import argparse,collections,copy,csv,importlib.util,json,re,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from agent_environment.environment import create_episode, proxy_tokens

def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj
ENGINE=module(ROOT/'frozen_baselines/research3_technique_strong_baselines_generalization02/baselines/engine.py','frozen_engine')
QUAL='DETERMINISTIC_POLICY_CONTROL_NOT_LLM_AGENT'
CONDITIONS=[('NO_EXTRA','S')]+[(p,b) for p in ('STATIC_BM25','FIXED_SOURCE','ADAPTIVE_HEURISTIC') for b in ('S','M')]
FIXED=[('audit',['execve','exe','proctitle']),('all',['failed','download','connection','permission']),('all',['process','command','network','user']),('all',['login','file','service','port'])]
STOP=set('the and for from with this that are was were not may can when into other their have has also its these such more than which use used using through system data process'.split())

def merge(seen,events):
 for e in events:
  if e['event_id'] not in seen or len(e['text'])>len(seen[e['event_id']]['text']):seen[e['event_id']]=e

def text_of(seen): return '\n'.join(e['text'] for e in seen.values())
def terms(text):
 return collections.Counter(t for t in ENGINE.words(text) if t not in STOP and 2<=len(t)<=60 and not any(x in t for x in ('reference','gold','ground_truth')))
def top_terms(text,n=32,excluded=()):
 return [t for t,c in sorted(terms(text).items(),key=lambda x:(-x[1],x[0])) if t not in excluded][:n]

def run_policy(episode,policy,budget,idx,docs,env):
 start=time.perf_counter()
 observation=env.initial_observation();seen={};merge(seen,observation['events']);initial_ids=set(seen)
 calls=0;used=set();initial_text=text_of(seen)
 steps=0 if policy=='NO_EXTRA' else 1 if policy=='STATIC_BM25' else (2 if budget=='S' else 4)
 for turn in range(steps):
  source='all'
  if policy=='STATIC_BM25':keys=top_terms(initial_text)
  elif policy=='FIXED_SOURCE':
   source,keys=FIXED[turn];source=source if source in observation['source_types'] else 'all'
  else:
   # Select from currently observed native words, then public top-2 distinction.
   keys=top_terms(text_of(seen),16,used)
   if turn and len(keys)<8:
    ranking=ENGINE.rank(idx.ids,idx.score(text_of(seen)));a,b=ranking[:2]
    distinct=terms(docs[a]).keys()-terms(docs[b]).keys()
    keys+=sorted(t for t in distinct if len(t)>=5 and t not in used and t not in keys)[:16-len(keys)]
   if turn:
    counts=collections.Counter(e['source_type'] for e in seen.values())
    source=min(observation['source_types'],key=lambda s:(counts[s],s)) if observation['source_types'] else 'all'
  if not keys:keys=['event'] # input has no valid lexical words; explicit fixed fallback
  used.update(keys)
  result=env.call('search_events',{'source_type':source,'keywords':keys,'time_range':None,'max_results':(20 if budget=='S' else 40) if policy=='STATIC_BM25' else 10})
  calls+=1;merge(seen,result.get('events',[]))
 ranking=ENGINE.rank(idx.ids,idx.score(text_of(seen)))
 submitted=env.call('submit_technique_ranking',{'ranking':ranking,'evidence_ids':list(seen)})
 if submitted.get('accepted') is not True:raise RuntimeError(submitted)
 elapsed=time.perf_counter()-start
 sample=f'v2_sampled_{episode:04d}';condition=policy if policy=='NO_EXTRA' else policy+'_'+budget
 costs=env.cost()
 pred={'sample_id':sample,'condition':condition,'policy':policy,'budget':budget,'qualification':QUAL,'predictions':ranking,'evidence_ids':list(seen),'observed_unique_rows':len(seen),'initial_empty':not bool(initial_text.strip()),'source_types_initial':observation['source_types'],'new_evidence_ids':[i for i in seen if i not in initial_ids],'cost':costs,'seconds':elapsed}
 trajectory={'sample_id':sample,'condition':condition,'qualification':QUAL,'initial_observation':observation,'calls':env.trace,'submission':env.submission,'seconds':elapsed}
 return pred,trajectory

def predict(n,offset=0):
 docs=json.loads((ROOT.parent/'research3_technique_strong_baselines_generalization02/knowledge/K2_DESCRIPTION_16_1.json').read_text())
 idx=ENGINE.Index(docs,'char')
 (ROOT/'experiments').mkdir(exist_ok=True);(ROOT/'agent_trajectories').mkdir(exist_ok=True)
 with (ROOT/'experiments/deterministic_controls_predictions.jsonl').open('w') as out,(ROOT/'agent_trajectories/DETERMINISTIC_CONTROLS.jsonl').open('w') as trace:
  for i in range(offset,offset+n):
   # Trusted host clones an unused initialized state, never exposes its pool.
   host_start=time.perf_counter()
   bases={b:create_episode(i,b,initialization_max_proxy_tokens=256) for b in ('S','M')}
   setup_seconds=time.perf_counter()-host_start
   for policy,budget in CONDITIONS:
    clone_start=time.perf_counter();env=copy.deepcopy(bases[budget]);clone_seconds=time.perf_counter()-clone_start
    p,t=run_policy(i,policy,budget,idx,docs,env);p['host_setup_seconds']=setup_seconds;p['host_clone_seconds']=clone_seconds;out.write(json.dumps(p,ensure_ascii=False)+'\n');trace.write(json.dumps(t,ensure_ascii=False)+'\n')
   out.flush();trace.flush()
   if (i-offset+1)%10==0 or i==offset:print(json.dumps({'episodes_complete':i-offset+1,'last_index':i,'cache':str(idx.score.cache_info())}),flush=True)
  idx.score.cache_clear()


def audit_artifacts(preds):
 keyed={(p['sample_id'],p['condition']):p for p in preds}
 assert len(keyed)==len(preds)
 initials={};count=0
 with (ROOT/'agent_trajectories/DETERMINISTIC_CONTROLS.jsonl').open() as f:
  for line in f:
   tr=json.loads(line);p=keyed[(tr['sample_id'],tr['condition'])]
   events=tr['initial_observation']['events'];seen={e['event_id'] for e in events}
   signature=json.dumps(events,sort_keys=True)
   assert initials.setdefault(tr['sample_id'],signature)==signature
   assert sum(proxy_tokens(e['text']) for e in events)<=256
   calls=tokens=new=0
   for call in tr['calls']:
    assert call['status']=='ok'
    calls+=call['tool']!='submit_technique_ranking'
    for e in call['result'].get('events',[]):
     new+=e['event_id'] not in seen;seen.add(e['event_id']);tokens+=proxy_tokens(e['text'])
   assert calls==p['cost']['query_calls']
   assert tokens==p['cost']['returned_log_proxy_tokens']
   assert new==p['cost']['new_unique_rows']
   assert set(p['evidence_ids'])<=seen
   assert p['predictions']==tr['submission']['ranking']
   assert len(set(p['predictions']))==10
   assert new<=(20 if p['budget']=='S' else 40)
   assert tokens<=(2048 if p['budget']=='S' else 4096)
   count+=1
 assert count==len(preds)
 return {'checked_trajectories':count,'identical_initial_observations_per_episode':len(initials),
   'all_evidence_seen_and_submissions_match':True,'budgets_and_proxy_recount_exact':True}

def evaluate():
 # Separate post-prediction evaluation. Policy functions never receive this map.
 evaluator=module(ROOT/'frozen_baselines/research3_attack_technique_benchmark01/evaluate_techniques.py','frozen_v1')
 preds=[json.loads(s) for s in (ROOT/'experiments/deterministic_controls_predictions.jsonl').read_text().splitlines()]
 audit=audit_artifacts(preds)
 initial_source_rows={}
 with (ROOT/'agent_trajectories/DETERMINISTIC_CONTROLS.jsonl').open() as tracefile:
  for line in tracefile:
   tr=json.loads(line);initial_source_rows[(tr['sample_id'],tr['condition'])]=collections.Counter(e['source_type'] for e in tr['initial_observation']['events'])
 gold={r['sample_id']:r for r in map(json.loads,(ROOT.parent/'research3_technique_strong_baselines_generalization02/datasets/p2_v2/reference_sampled.jsonl').open())}
 universe=json.loads((ROOT.parent/'research3_technique_strong_baselines_generalization02/knowledge/K2_DESCRIPTION_16_1.json').read_text())
 result={};rows=[]
 for condition in dict.fromkeys(p['condition'] for p in preds):
  selected=[p for p in preds if p['condition']==condition]
  records=[{'ground_truth':gold[p['sample_id']]['ground_truth'],'predictions':p['predictions']} for p in selected]
  query=evaluator.summarize(records,universe)
  steps=collections.defaultdict(list)
  for p,r in zip(selected,records):steps[gold[p['sample_id']]['logical_step_id']].append(r)
  per_step=[evaluator.summarize(v,universe) for v in steps.values()]
  stepmacro={key:sum(s[key] for s in per_step)/len(per_step) for key in query if key!='n_records'}
  n=len(selected);calls=sum(p['cost']['query_calls'] for p in selected)
  summary={'condition':condition,'episodes':n,'logical_steps':len(steps),**query,
   'step_macro_top1':stepmacro.get('top1_accuracy',0),'step_macro_top5':stepmacro.get('top5_accuracy',0),'step_macro_top10':stepmacro.get('top10_accuracy',0),'step_macro_mrr':stepmacro['mrr'],
   'initial_empty_count':sum(p['initial_empty'] for p in selected),
   'mean_tool_calls':calls/n,'mean_new_unique_rows':sum(p['cost']['new_unique_rows'] for p in selected)/n,
   'mean_initial_regex_tokens':sum(p['cost']['initial_proxy_tokens'] for p in selected)/n,
   'mean_returned_log_regex_tokens':sum(p['cost']['returned_log_proxy_tokens'] for p in selected)/n,
   'duplicate_query_fraction':sum(p['cost']['duplicate_queries'] for p in selected)/max(calls,1),
   'invalid_query_fraction':sum(p['cost']['errors'] for p in selected)/max(calls,1),
   'mean_returned_rows':sum(p['cost']['returned_rows'] for p in selected)/n,
   'duplicate_row_fraction':sum(p['cost']['duplicate_rows'] for p in selected)/max(1,sum(p['cost']['returned_rows'] for p in selected)),
   'seconds_total':sum(p['seconds'] for p in selected)}
  result[condition]={'query_metrics':query,'step_macro_metrics':stepmacro,'resource_summary':summary,
   'source_available_counts':dict(collections.Counter(s for p in selected for s in p['source_types_initial'])),
   'source_initial_nonempty_episode_counts':dict(collections.Counter(s for p in selected for s in initial_source_rows[(p['sample_id'],condition)])),
   'source_initial_empty_episode_counts':{s:sum(initial_source_rows[(p['sample_id'],condition)].get(s,0)==0 for p in selected) for s in sorted({s for p in selected for s in p['source_types_initial']})}}
  rows.append(summary)
 payload={'artifact_audit':audit,'qualification':QUAL,'evaluator':'frozen V1 summarize, top-parent normalization','initial_budget_regex_proxy_tokens':256,'candidate_count':len(universe),'conditions':result,'developer_reference_schema_exposure':'First reference row was read during schema inspection before coding. A three-episode frozen-policy smoke run was evaluated before the full run (the evaluator loaded the complete reference map but joined only those three saved predictions); no keyword/policy changes followed, only host cloning optimization and reporting fields. No reference access occurs in prediction code; full evaluation begins after all full-run predictions close.'}
 (ROOT/'results/DETERMINISTIC_CONTROL_METRICS.json').write_text(json.dumps(payload,indent=2))
 with (ROOT/'STATIC_RETRIEVAL_AGENT_CONTROLS.csv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 (ROOT/'reports').mkdir(exist_ok=True)
 report=['# Deterministic investigation tool controls','',f'Qualification: **{QUAL}**. No pretrained model, LLM calls, or learned Agent is used. These are resource-ceiling controls, not evidence of LLM reasoning. All predictions were closed on disk before the reference file was opened for evaluation. The developer inspected reference episode 0 schema (including its label) before implementation. A frozen-policy three-episode smoke run was evaluated before the full run; its separate evaluator loaded the complete reference map and joined only those three saved predictions. No policy or vocabulary changes followed that smoke evaluation; only host cloning optimization and reporting fields changed. These exposures are disclosed; fixed generic vocabulary was supplied by the parent task.','', 'All conditions start with the same native sampled view capped at 256 Unicode regex word/punctuation proxy tokens. Final ranking is the frozen K2 CharacterNgramTFIDF implementation. Only initial/tool-returned evidence is concatenated, deduplicated by native event ID (longest observed text retained). Final top-10 and evidence IDs pass the actual submit tool.','', 'NO_EXTRA performs no query. STATIC_BM25 uses initial native word frequency top 32 once, with 20/40 result limits. FIXED_SOURCE uses predeclared audit execve/exe/proctitle, then all failed/download/connection/permission, then all process/command/network/user, then all login/file/service/port. Missing audit source falls back to all. ADAPTIVE_HEURISTIC uses unqueried currently observed native tokens; if fewer than eight are available, public words distinguishing current top-2 K2 descriptions supplement them. After the first query it targets the least represented available native source. These deterministic decisions access no private event pool.','', '| Condition | Query Top-1 | Query Top-10 | MRR | Step-macro Top-10 | Mean new rows | Mean calls |','|---|---:|---:|---:|---:|---:|---:|']
 for r in rows:report.append(f"| {r['condition']} | {r['top1_accuracy']:.4f} | {r['top10_accuracy']:.4f} | {r['mrr']:.4f} | {r['step_macro_top10']:.4f} | {r['mean_new_unique_rows']:.2f} | {r['mean_tool_calls']:.2f} |")
 report+=['','The 385 execution–step records are repeated variants of fewer logical steps; report both query and logical-step macro metrics. This is a CAM-LDS-v2 within-source control, not independent external generalization. Resource budgets are maxima: STATIC_BM25 deliberately spends just one query; row/token exhaustion and genuinely small full pools can yield fewer additional rows. Proxy counts exclude JSON envelopes and are not actual model tokenizer counts. Runtime excludes shared index initialization, includes tool/final scoring but excludes shared host episode initialization and cloning (separately recorded), and is not comparable to API latency. No claim of superiority or significance is justified by these point metrics alone.','', 'Artifact audit verified every trajectory: common identical initial evidence per episode, seen-only citations, exact final-submission equality, and exact independent regex token/new-row/call recount under hard budgets.','', 'Artifacts: predictions in experiments/deterministic_controls_predictions.jsonl; exact controlled observations and tool trace in agent_trajectories/DETERMINISTIC_CONTROLS.jsonl; frozen V1 query and logical-step macro results in results/DETERMINISTIC_CONTROL_METRICS.json.']
 (ROOT/'reports/DETERMINISTIC_CONTROL_ANALYSIS.md').write_text('\n'.join(report)+'\n')
 print(json.dumps(rows),flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--n',type=int,default=385);ap.add_argument('--offset',type=int,default=0);ap.add_argument('--evaluate-only',action='store_true');args=ap.parse_args()
 if not args.evaluate_only:predict(args.n,args.offset)
 evaluate()
