"""Offline audit of new native receipts and condition denominators; no model calls."""
import collections,csv,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from project import ROOT,records,fingerprint
from llm.gguf_tokenizer import templated_ids
def csvout(name,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with (ROOT/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def main():
 rows=records(ROOT/'agent_episodes/ALL_CONDITIONS.jsonl');folder=ROOT/'agent_episodes/native_receipts'
 attempts=[json.loads(p.read_text()) for p in folder.glob('*_attempt.json')]
 native=[json.loads(p.read_text()) for p in folder.glob('*.json') if not p.stem.endswith(('_devices','_attempt'))]
 for r in rows:
  prefix=f"VALIDATION02_{r['scope']}_{r['episode_index']:04d}_{r['method']}_"
  r['_attempts']=[a for a in attempts if a['tag'].startswith(prefix)]
  r['_attempt_count']=len(r['_attempts'])
 proof=[]
 for r in native:
  body=templated_ids(r['prompt'])[1:-2]
  proof.append({'receipt':r['tag']+'.json','body_token_count':len(body),'complete_prompt_body_in_backend_context':r['response']['context'][:len(body)]==body})
 assert all(p['complete_prompt_body_in_backend_context'] for p in proof)
 (ROOT/'results/BACKEND_CONTEXT_FEEDBACK_PROOF.json').write_text(json.dumps(proof,indent=2))
 summary=[];cost=[]
 for (scope,method),group in __import__('itertools').groupby(sorted(rows,key=lambda r:(r['scope'],r['method'])),key=lambda r:(r['scope'],r['method'])):
  g=list(group);valid=[r for r in g if r['status']=='COMPLETED'];called=[r for r in g if r['_attempt_count']]
  for denom,subset in [('VALID_ONLY',valid),('MODEL_CALLED_FAILURES_EMPTY',called),('PLANNED_CONDITIONS_FAILURES_EMPTY',g)]:
   summary.append({'scope':scope,'method':method,'denominator':denom,'N':len(subset),'valid':len(valid),'preflight_no_call':sum(not r['_attempt_count'] for r in g),**{m:sum(r['metrics'].get(m,0) for r in subset)/len(subset) if subset else 'NA' for m in ['top1_accuracy','top5_accuracy','top10_accuracy','mrr']}})
  ats=[a for r in g for a in r['_attempts']]
  cost.append({'scope':scope,'method':method,'planned_conditions':len(g),'completed':len(valid),'failed':len(g)-len(valid),'attempted_model_requests':len(ats),'native_calls':sum(r['model_calls_with_native_receipt'] for r in g),'unknown_timeout_requests':sum(a['status']=='FAILED_OR_INTERRUPTED' for a in ats),'input_tokens':sum(r['model_prompt_tokens'] for r in g),'output_tokens':sum(r['model_output_tokens'] for r in g),'charged_input_with_reservations':sum(a['prompt_tokens'] if a.get('prompt_tokens') is not None else a['reserved_input_tokens'] for a in ats),'charged_output_with_reservations':sum(a['output_tokens'] if a.get('output_tokens') is not None else a['reserved_output_tokens'] for a in ats),'model_wall_seconds_known_responses':sum(r['model_wall_seconds'] for r in g),'attempt_wall_seconds_including_timeouts':sum(a.get('wall_seconds') or 0 for a in ats),'tool_calls':sum(r['query_calls'] for r in g),'returned_actual_tokens':sum(r['tool_cost'].get('returned_actual_model_tokens',0) for r in g)})
 pairs=[];agent={r['sample_id']:r for r in rows if r['scope']=='PAIRED_PILOT' and r['method']=='A3_ADAPTIVE_LLM_AGENT'}
 for scope in ['PAIRED_PILOT','CONTEXT_FIT_STATIC_V4']:
  for method in ['A0_DIRECT','A1_STATIC_BM25_LLM','A2_FIXED_QUERY_LLM']:
   static={r['sample_id']:r for r in rows if r['scope']==scope and r['method']==method}
   same=[(s,agent[k]) for k,s in static.items() if k in agent and s['status']=='COMPLETED' and agent[k]['qualification']=='VALID_MODEL_AGENT_EPISODE']
   assert all(s['initial_observation_hash']==a['initial_observation_hash'] for s,a in same)
   pairs.append({'static_scope':scope,'static_method':method,'agent_scope':'PAIRED_PILOT','valid_same_case_pairs':len(same),'sample_ids':'|'.join(s['sample_id'] for s,a in same),'static_Top10':sum(s['metrics'].get('top10_accuracy',0) for s,a in same)/len(same) if same else 'NA','agent_Top10':sum(a['metrics'].get('top10_accuracy',0) for s,a in same)/len(same) if same else 'NA','static_MRR':sum(s['metrics'].get('mrr',0) for s,a in same)/len(same) if same else 'NA','agent_MRR':sum(a['metrics'].get('mrr',0) for s,a in same)/len(same) if same else 'NA','qualification':'POSTHOC_CONTEXT_CONTROL' if scope.endswith('V4') else 'PREREGISTERED_DEV_PILOT_VALID_SUBSET'})
 csvout('results/NEW_LLM_CONDITION_RESULTS.csv',summary);csvout('AGENT_COST_REPORT.csv',cost);csvout('AGENT_PAIRED_COMPARISON.csv',pairs)
 conditions=[]
 for r in rows:
  conditions.append({k:r[k] for k in ['sample_id','scope','method','status','qualification','model_calls_with_native_receipt']}|{'attempted_model_requests':r['_attempt_count'],'errors':' | '.join(r['errors']),'Top10':r['metrics'].get('top10_accuracy',0),'MRR':r['metrics'].get('mrr',0)})
 csvout('results/NEW_LLM_CONDITION_ERRORS.csv',conditions)
 sameobs=all(len({r['initial_observation_hash'] for r in rows if r['sample_id']==k})==1 for k in {r['sample_id'] for r in rows})
 cap=max(r['tool_cost'].get('returned_actual_model_tokens',0) for r in rows)
 valid_episodes=records(ROOT/'AGENT_VALID_EPISODES.jsonl')
 data={'recorded_conditions':len(rows),'condition_status':dict(collections.Counter(r['status'] for r in rows)),'native_responses':len(native),'attempts':len(attempts),'actual_input_tokens':sum(r['response'].get('prompt_eval_count',0) for r in native),'actual_output_tokens':sum(r['response'].get('eval_count',0) for r in native),'actual_model_seconds':sum(r['wall_seconds'] for r in native),'first_request_unix':min(r['start_unix'] for r in attempts),'last_request_end_unix':max(r['start_unix']+(r.get('wall_seconds') or 0) for r in attempts),'request_span_seconds':max(r['start_unix']+(r.get('wall_seconds') or 0) for r in attempts)-min(r['start_unix'] for r in attempts),'attempt_status':dict(collections.Counter(r['status'] for r in attempts)),'valid_agent_episodes':len(valid_episodes),'valid_agent_scopes':dict(collections.Counter(r['scope'] for r in valid_episodes)),'same_initial_observation_all_methods':sameobs,'max_returned_actual_tokens':cap,'backend_complete_prompt_proofs':len(proof),'all_backend_prompt_proofs_pass':True,'error_counts':dict(collections.Counter(e for r in rows for e in r['errors']))}
 data['input_tokens_with_unknown_attempt_reservations']=sum(r['prompt_tokens'] if r.get('prompt_tokens') is not None else r['reserved_input_tokens'] for r in attempts)
 data['output_tokens_with_unknown_attempt_reservations']=sum(r['output_tokens'] if r.get('output_tokens') is not None else r['reserved_output_tokens'] for r in attempts)
 data['unknown_timeout_actual_cost']='UNKNOWN; do not replace by zero; request caps reserved'
 data['model_stop_receipt']='LOCAL_MODEL_STOP_RECEIPT.json; late control unload is not inference; timeout backend completion times UNKNOWN'
 csvout('results/NEW_REQUEST_ATTEMPT_COSTS.csv',[{k:r.get(k) for k in ['tag','status','start_unix','wall_seconds','prompt_tokens','output_tokens','reserved_input_tokens','reserved_output_tokens','error']} for r in attempts])
 assert data['input_tokens_with_unknown_attempt_reservations']<=500000 and data['output_tokens_with_unknown_attempt_reservations']<=45000
 assert sameobs and cap<=2048 and len(attempts)<=80 and data['actual_input_tokens']<=500000 and data['actual_output_tokens']<=45000 and data['request_span_seconds']<=5400
 (ROOT/'results/NEW_LLM_SUMMARY.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))
if __name__=='__main__':main()
