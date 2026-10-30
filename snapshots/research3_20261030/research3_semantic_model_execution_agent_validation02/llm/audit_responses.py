"""Requalify 54 historical native responses without model calls or Gold repair."""
import collections,csv,json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from project import ROOT,PREVIOUS,BASELINES,sha256,module,records,fingerprint
MODEL='deepseek-r1:1.5b';DIGEST='a42b25d8c10a841bd24724309898ae851466696a7d7f3a0a408b895538ccbc96'
def write_csv(path:Path,rows:list[dict])->None:
 keys=list(dict.fromkeys(k for row in rows for k in row))
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def main()->None:
 universe=json.loads((BASELINES/'knowledge/K2_DESCRIPTION_16_1.json').read_text())
 archived=records(PREVIOUS/'experiments/PILOT_V1_INVALID_AGENT/LLM_TECHNIQUE_PREDICTIONS.jsonl')
 historical={(x['episode_index'],x['method']):x for x in archived}
 reviewed=[]
 for path in sorted((PREVIOUS/'experiments').glob('PILOT_*.json')):
  native=json.loads(path.read_text())
  if not isinstance(native.get('response'),dict):continue
  match=re.fullmatch(r'PILOT_(\d{4})_(.+)_(final|action\d+)',path.stem)
  if not match:raise RuntimeError('Unrecognized native record')
  episode,method,stage=int(match[1]),match[2],match[3];response=native['response'];prompt=native['prompt'];adaptive=method.startswith('ADAPTIVE')
  device_path=path.with_name(path.stem+'_devices.json');device=json.loads(device_path.read_text())
  target=[x for x in device['models'] if x.get('digest')==DIGEST]
  verified=native['model']==MODEL and native['model_digest']==DIGEST and response.get('model')==MODEL and native['prompt_sha256']==__import__('hashlib').sha256(prompt.encode()).hexdigest() and bool(target) and all('size_vram' in x and x['size_vram']==0 for x in target)
  complete=response.get('done') is True and response.get('done_reason')=='stop'
  try:body=json.loads(response.get('response',''));json_valid=isinstance(body,dict)
  except (json.JSONDecodeError,TypeError):body={};json_valid=False
  allowed_match=re.search(r'^Allowed candidate IDs: ([^\n]+)',prompt,re.M)
  allowed=allowed_match[1].split(',') if allowed_match else []
  visible=re.findall(r'^\[([^\]]+)\]\[[^\]]+\] ',prompt,re.M)
  predictions=body.get('techniques',[]) if stage=='final' else []
  proposed=predictions if isinstance(predictions,list) else []
  invalid_ids=[x for x in proposed if not isinstance(x,str) or x not in universe]
  outside=[x for x in proposed if x not in allowed]
  citations=body.get('evidence_ids',[])
  valid_ranking=stage=='final' and json_valid and set(body)=={'techniques','evidence_ids','evidence_limitations'} and isinstance(predictions,list) and len(predictions)==10 and all(isinstance(x,str) for x in predictions) and len(set(predictions))==10 and not invalid_ids and not outside and isinstance(citations,list) and len(citations)<=5 and all(isinstance(x,str) and x in visible for x in citations) and isinstance(body.get('evidence_limitations'),str) and len(body['evidence_limitations'])<=200
  if not verified:qual='UNVERIFIED_RESPONSE'
  elif not complete:qual='INCOMPLETE_RESPONSE'
  elif adaptive:qual='INVALID_TRANSPORT_RESPONSE'
  elif not valid_ranking:qual='INVALID_OUTPUT_CONTRACT_RESPONSE'
  elif method in ['DIRECT216','KNOWLEDGE20']:qual='VALID_DIRECT_LLM_RESPONSE'
  else:qual='VALID_STATIC_RAG_RESPONSE'
  row=historical.get((episode,method),{})
  if stage=='final':assert bool(valid_ranking)==bool(row.get('predictions')),f'Native validator disagrees with saved condition {path.name}'
  reviewed.append({'receipt_id':path.stem,'source_path':str(path),'source_sha256':sha256(path),'device_path':str(device_path),'device_sha256':sha256(device_path),'sample_id':f'v2_sampled_{episode:04d}','method':method,'stage':stage,'qualification':qual,'model_id':MODEL,'model_digest':DIGEST,'prompt_sha256':native['prompt_sha256'],'inherited_not_new_inference':True,'new_inference_this_round':False,'model_provenance_verified':verified,'native_HTTP_response_complete':complete,'json_valid':json_valid,'ranking_contract_valid':bool(valid_ranking),'eligible_for_technique_evaluation':qual in ['VALID_DIRECT_LLM_RESPONSE','VALID_STATIC_RAG_RESPONSE'],'allowed_candidate_count':len(allowed) if stage=='final' else 216,'allowed_candidate_ids':allowed if stage=='final' else None,'visible_event_ids':visible,'predictions':proposed if stage=='final' else None,'invalid_attack_ids':invalid_ids,'invalid_attack_id_count':len(invalid_ids),'proposed_id_count':len(proposed),'duplicate_id_count':len(proposed)-len(set(map(str,proposed))),'outside_allowed_candidates_count':len(outside),'native_API_prompt_tokens':response.get('prompt_eval_count'),'native_API_output_tokens':response.get('eval_count'),'native_wall_seconds':native['wall_seconds'],'application_transport_status':'INVALID_TOOL_RESULT_FORWARDING' if adaptive else 'NO_DYNAMIC_TOOL_TRANSPORT','raw_schema_provenance':'NOT_SAVED_IN_V1; reconstructed validator, no claim of native schema receipt'})
 assert len(reviewed)==54
 (ROOT/'LLM_INFERENCE_RECEIPTS.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in reviewed))
 # Reference is opened only after audit qualification and payload indexing complete.
 reference={x['sample_id']:x for x in records(BASELINES/'datasets/p2_v2/reference_sampled.jsonl')}
 evaluator=module(PREVIOUS/'frozen_baselines/research3_attack_technique_benchmark01/evaluate_techniques.py','immutable_frozen_evaluator')
 results=[];per_sample=[]
 for method in sorted({x['method'] for x in reviewed if x['stage']=='final'}):
  finals=[x for x in reviewed if x['stage']=='final' and x['method']==method]
  eligible=[x for x in finals if x['eligible_for_technique_evaluation']]
  legitimate_attempts=[] if method.startswith('ADAPTIVE') else [x for x in finals if x['model_provenance_verified'] and x['native_HTTP_response_complete']]
  for label,selected in [('VALID_OUTPUTS_ONLY',eligible),('ALL_NONADAPTIVE_ATTEMPTS_FAILURES_EMPTY',legitimate_attempts)]:
   rs=[{'ground_truth':reference[x['sample_id']]['ground_truth'],'predictions':x['predictions'] if x['eligible_for_technique_evaluation'] else []} for x in selected]
   metrics=evaluator.summarize(rs,universe) if rs else {k:'N/A' for k in ['top1_accuracy','top5_accuracy','top10_accuracy','mrr','precision_at_1','precision_at_5','precision_at_10','recall_at_1','recall_at_5','recall_at_10','micro_f1_at_5']}
   results.append({'method':method,'scope':label,'data_status':'INHERITED_RELATED_DEVELOPMENT_PILOT_NOT_NEW_RUN','N_final_receipts':len(finals),'N_valid_output':len(eligible),'N_scored':len(selected),'output_contract_valid_rate':sum(x['ranking_contract_valid'] for x in finals)/len(finals),'qualified_output_rate':len(eligible)/len(finals),'invalid_attack_id_ratio':sum(x['invalid_attack_id_count'] for x in finals)/max(1,sum(x['proposed_id_count'] for x in finals)),**metrics})
  for x in finals:
   g=set(reference[x['sample_id']]['ground_truth']);p=x['predictions'] if x['eligible_for_technique_evaluation'] else []
   candidate_hit=bool(g&set(x['allowed_candidate_ids']))
   per_sample.append({'receipt_id':x['receipt_id'],'sample_id':x['sample_id'],'method':method,'qualification':x['qualification'],'gold':';'.join(sorted(g)),'predictions':';'.join(p),'top10_hit':bool(g&set(p[:10])) if x['eligible_for_technique_evaluation'] else 'N/A','candidate_hit':candidate_hit,'error_source':'INVALID_TOOL_RESULT_FORWARDING' if method.startswith('ADAPTIVE') else 'OUTPUT_CONTRACT_FAILURE' if not x['ranking_contract_valid'] else 'CORRECT_TOP10' if g&set(p) else 'CANDIDATE_RECALL_FAILURE' if not candidate_hit else 'UNRESOLVED','duplicate_ids':x['duplicate_id_count'],'candidate_size':x['allowed_candidate_count']})
 write_csv(ROOT/'LLM_VALID_RESPONSE_RESULTS.csv',results);write_csv(ROOT/'results/LLM_RECEIPT_ERROR_DETAILS.csv',per_sample)
 summary={'native_receipts':54,'final_rankings':sum(x['stage']=='final' for x in reviewed),'action_decisions':sum(x['stage']!='final' for x in reviewed),'qualification_counts':dict(collections.Counter(x['qualification'] for x in reviewed)),'valid_final_ranking_contract_count_including_invalid_agent_protocol':sum(x['ranking_contract_valid'] for x in reviewed),'eligible_final_rankings':sum(x['eligible_for_technique_evaluation'] for x in reviewed),'eligible_unique_execution_steps':len({x['sample_id'] for x in reviewed if x['eligible_for_technique_evaluation']}),'eligible_unique_logical_steps':len({reference[x['sample_id']]['logical_step_id'] for x in reviewed if x['eligible_for_technique_evaluation']}),'total_proposed_IDs_in_final_receipts':sum(x['proposed_id_count'] for x in reviewed),'invalid_attack_IDs':sum(x['invalid_attack_id_count'] for x in reviewed),'duplicate_ID_occurrences':sum(x['duplicate_id_count'] for x in reviewed),'native_prompt_tokens':sum(x['native_API_prompt_tokens'] for x in reviewed),'native_output_tokens':sum(x['native_API_output_tokens'] for x in reviewed),'known_wall_seconds':sum(x['native_wall_seconds'] for x in reviewed),'additional_interrupted_attempt_upper_bound':1,'interrupted_cost':'UNKNOWN','new_model_calls':0}
 (ROOT/'results/LLM_AUDIT_SUMMARY.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
