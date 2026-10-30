"""Authorized fixed local model: minimal gate, then frozen twelve-case paired pilot."""
import collections,json,sys,time,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from project import ROOT,PREVIOUS,BASELINES,canonical,fingerprint,sha256,module,records
from agent_environment.token_budget_environment import create_episode,count
from agent_transport.transport import Transport,validate_real_episode
from llm.local_client import generate,request,MODEL,DIGEST
ENGINE=module(PREVIOUS/'frozen_baselines/research3_technique_strong_baselines_generalization02/baselines/engine.py','frozen_character_index')
DOCS=json.loads((BASELINES/'knowledge/K2_DESCRIPTION_16_1.json').read_text());IDS=sorted(DOCS);INDEX=ENGINE.Index(DOCS,'char')
EVALUATOR=module(PREVIOUS/'frozen_baselines/research3_attack_technique_benchmark01/evaluate_techniques.py','frozen_pilot_eval')
def rank(text:str)->list[str]:
 scores=INDEX.score(text);return [INDEX.ids[i] for i in sorted(range(len(INDEX.ids)),key=lambda i:(-scores[i],INDEX.ids[i]))]
def initial_text(env)->str:return '\n'.join(e['text'] for e in env.initial_observation()['events'])
def setup(index:int):
 env=create_episode(index);t=Transport(env,f'p2_{index:04d}',classification='REAL_FIXED_MODEL_EXECUTION')
 candidates=rank(initial_text(env));each=70
 knowledge=[{'technique_id':k,'partial_definition':DOCS[k].encode()[:each].decode('utf8',errors='ignore')} for k in candidates[:20]]
 t.messages.append({'role':'user','content':canonical({'kind':'public_knowledge','version':'ATTACK16.1_K2','definition_status':'same frozen partial top20 descriptions across A0-A3; full216 ranking allowed','data':knowledge})})
 return env,t
def seen_ids(t)->list[str]:
 out=[e['event_id'] for e in t.env.initial_observation()['events']]
 for c in t.calls.values():out.extend(e['event_id'] for e in c['envelope']['data'].get('events',[]))
 return list(dict.fromkeys(out))
def action_schema(t,allow_stop:bool)->dict:
 def obj(props,required=None):return {'type':'object','properties':props,'required':list(props) if required is None else required,'additionalProperties':False}
 variants=[]
 argsets={'search_events':obj({'source_type':{'type':'string','enum':['all']+t.env.initial_observation()['source_types']},'keywords':{'type':'array','items':{'type':'string','minLength':1,'maxLength':80},'minItems':1,'maxItems':8},'time_range':{'type':'null'},'max_results':{'type':'integer','minimum':1,'maximum':5}}),
 'get_event_context':obj({'event_id':{'type':'string','enum':seen_ids(t)},'before':{'type':'integer','minimum':0,'maximum':2},'after':{'type':'integer','minimum':0,'maximum':2}}),
 'search_related_entities':obj({'entity_type':{'type':'string','enum':['ip','domain','process','path','user','literal']},'value':{'type':'string','minLength':1,'maxLength':80},'max_results':{'type':'integer','minimum':1,'maximum':5}}),
 'retrieve_attack_technique':obj({'technique_id':{'type':'string','enum':IDS}})}
 if allow_stop:argsets['stop']=obj({})
 for name,args in argsets.items():variants.append(obj({'call_id':{'type':'string','enum':[t.next_call_id()]},'tool':{'type':'string','enum':[name]},'arguments':args}))
 return {'oneOf':variants}
def final_schema(t)->dict:
 return {'type':'object','properties':{'techniques':{'type':'array','items':{'type':'string','enum':IDS},'minItems':10,'maxItems':10,'uniqueItems':True},'evidence_ids':{'type':'array','items':{'type':'string','enum':seen_ids(t)},'maxItems':5},'evidence_limitations':{'type':'string','maxLength':200}},'required':['techniques','evidence_ids','evidence_limitations'],'additionalProperties':False}
def message(t,kind:str,text:str)->list[dict]:
 p=t.payload_for_model()['messages'];return p+[{'role':'user','content':canonical({'kind':kind,'instruction':text})}]
def final_validate(body:dict,t)->None:
 p=body['techniques'];ev=body['evidence_ids']
 if not isinstance(p,list) or len(p)!=10 or len(set(p))!=10 or not set(p)<=set(IDS):raise ValueError('OUTPUT_CONTRACT_DUPLICATE_OR_INVALID_TECHNIQUE')
 if not isinstance(ev,list) or not set(ev)<=set(seen_ids(t)):raise ValueError('OUTPUT_CONTRACT_UNSEEN_CITATION')
def execute(index:int,method:str,scope:str,max_queries:int=2)->dict:
 env,t=setup(index);tagbase=f'VALIDATION02_{scope}_{index:04d}_{method}';native=[];started=time.monotonic();pred=[];body={};errors=[];status='COMPLETED';final_messages=None
 try:
  if method=='A1_STATIC_BM25_LLM':
   terms=[w for w,n in collections.Counter(ENGINE.words(initial_text(env))).most_common(32)] or ['event']
   t.execute({'call_id':t.next_call_id(),'tool':'search_events','arguments':{'source_type':'all','keywords':terms,'time_range':None,'max_results':20}})
  elif method=='A2_FIXED_QUERY_LLM':
   for source,terms in [('audit',['execve','exe','proctitle']),('all',['failed','download','connection','permission'])]:
    if env.cost()['query_calls']>=2:break
    t.execute({'call_id':t.next_call_id(),'tool':'search_events','arguments':{'source_type':source if source in env.initial_observation()['source_types'] else 'all','keywords':terms,'time_range':None,'max_results':10}})
  elif method=='A3_ADAPTIVE_LLM_AGENT':
   for step in range(max_queries):
    p=message(t,'tool_decision',f'Select one read-only tool to obtain evidence that distinguishes plausible ATT&CK mechanisms. Return only the registered tool JSON; call_id={t.next_call_id()}. '+('You may stop if further evidence is unnecessary.' if step else 'Choose one tool; this first turn must investigate.'))
    receipt=generate(p,action_schema(t,allow_stop=step>0),tagbase+f'_action{step}');native.append(receipt);action=json.loads(receipt['response']['response'])
    if action['tool']=='stop':break
    t.execute(action)
    if env.cost()['returned_actual_model_tokens']>=2048:break
  final_messages=message(t,'final_ranking','Return JSON with exactly TEN DISTINCT allowed parent technique IDs, no duplicates. Rank by supplied evidence only. Cite only visible event IDs; mention partial observation and execution-attempt limits. All 216 parent IDs in initial knowledge_ids remain allowed. Do not treat technique definitions as observed facts.')
  receipt=generate(final_messages,final_schema(t),tagbase+'_final');native.append(receipt);body=json.loads(receipt['response']['response']);final_validate(body,t);pred=body['techniques'];submission=t.submit(pred,body['evidence_ids'])
 except Exception as exc:
  errors.append(type(exc).__name__+': '+str(exc));status='FAILED';submission=None
  if isinstance(exc,RuntimeError):status='STOPPED_BUDGET_OR_RUNTIME'
 row={'sample_id':f'v2_sampled_{index:04d}','episode_index':index,'method':method,'scope':scope,'status':status,'predictions':pred,'errors':errors,'model_calls_with_native_receipt':len(native),'tool_cost':env.cost(),'query_calls':len(t.calls),'native_tags':[x['tag'] for x in native],'model_prompt_tokens':sum(x['response'].get('prompt_eval_count',0) for x in native),'model_output_tokens':sum(x['response'].get('eval_count',0) for x in native),'model_wall_seconds':sum(x['wall_seconds'] for x in native),'condition_wall_seconds':time.monotonic()-started,'model_id':MODEL,'model_digest':DIGEST,'tool_results_lossless':True,'qualification':'PENDING_INDEPENDENT_EVALUATION','initial_observation_hash':fingerprint(env.initial_observation()['events']),'final_model_messages':final_messages,'tool_calls':t.calls,'tool_audit':t.audit,'submission':submission,'final_response_body':body}
 # Gold enters only the independent host evaluator after output/prediction is fixed.
 reference=next(x for x in records(BASELINES/'datasets/p2_v2/reference_sampled.jsonl') if x['sample_id']==row['sample_id'])
 metrics=EVALUATOR.summarize([{'ground_truth':reference['ground_truth'],'predictions':pred}],IDS)
 ep=ROOT/'results'/(tagbase+'_evaluation.json');ep.write_text(json.dumps({'sample_id':row['sample_id'],'predictions_sha256':fingerprint(pred),'metrics':metrics,'qualification':'HOST_POST_PREDICTION_EVALUATION_NOT_MODEL_INPUT'},indent=2))
 row.update(metrics=metrics,evaluation_path=str(ep))
 if method=='A3_ADAPTIVE_LLM_AGENT' and status=='COMPLETED' and len(native)>=2 and any(c['envelope']['status']=='ok' for c in t.calls.values()):
  folder=ROOT/'agent_episodes/native_receipts';receipts=[]
  for x in native:
   path=folder/(x['tag']+'.json');dp=folder/(x['tag']+'_devices.json');receipts.append({'path':str(path),'sha256':sha256(path),'device_path':str(dp),'device_sha256':sha256(dp)})
  episode={'qualification':'VALID_MODEL_AGENT_EPISODE','record_origin':'NEW_FIXED_MODEL_INFERENCE','sample_id':row['sample_id'],'model_digest':DIGEST,'native_model_receipts':receipts,'authorization_sha256':sha256(ROOT/'manifests/INFERENCE_AUTHORIZATION.json'),'independent_evaluation_receipt':{'path':str(ep),'sha256':sha256(ep)},'complete_tool_result_feedback':True,'feedback_payload_sha256':fingerprint(final_messages),'final_model_messages':final_messages,'allowed_candidates':IDS,'submission':submission,'tool_calls':t.calls,'scope':scope}
  try:episode['integrity_validation']=validate_real_episode(episode);row['qualification']='VALID_MODEL_AGENT_EPISODE'
  except Exception as exc:row['qualification']='INVALID_EPISODE_INTEGRITY';row['errors'].append(str(exc))
  else:
   with (ROOT/'AGENT_VALID_EPISODES.jsonl').open('a') as f:f.write(json.dumps(episode)+'\n')
 elif method=='A3_ADAPTIVE_LLM_AGENT':row['qualification']='NO_VALID_MODEL_AGENT_EPISODE'
 else:row['qualification']='VALID_NONADAPTIVE_MODEL_CONDITION' if status=='COMPLETED' else 'MODEL_CONDITION_FAILURE'
 with (ROOT/'agent_episodes/ALL_CONDITIONS.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
 print(row['sample_id'],method,status,row['qualification'],'calls',len(native),'tokens',row['model_prompt_tokens'],row['model_output_tokens'],flush=True)
 return row
def main()->None:
 assert any(x.get('digest')==DIGEST for x in request('tags').get('models',[]))
 register=ROOT/'manifests/LOCAL_AGENT_ACTUAL_PROTOCOL.json'
 if register.exists():raise RuntimeError('Already started; explicit resume procedure required')
 register.write_text(json.dumps({'model':MODEL,'model_digest':DIGEST,'candidate_count':216,'knowledge':'K2_DESCRIPTION_16_1','knowledge_initial_partial_top20_bytes_per_doc':70,'shared_initial_regex_proxy_limit':256,'extra_evidence_actual_GGUF_tokens':2048,'extra_evidence_regex_proxy_cap':2048,'read_attempts':2,'new_rows':20,'source_sha256':sha256(Path(__file__)),'transport_sha256':sha256(ROOT/'agent_transport/transport.py'),'budget_environment_sha256':sha256(ROOT/'agent_environment/token_budget_environment.py'),'client_sha256':sha256(ROOT/'llm/local_client.py'),'authorization_sha256':sha256(ROOT/'manifests/INFERENCE_AUTHORIZATION.json'),'roster_sha256':sha256(ROOT/'manifests/PAIRED_PILOT_REGISTRATION.json'),'all_final_prompts_same_instruction':True,'temperature':0,'seed':42,'num_gpu':0,'cpu_threads':2,'context':8192,'output':512},indent=2))
 (ROOT/'AGENT_VALID_EPISODES.jsonl').touch(exist_ok=False)
 gate=execute(0,'A3_ADAPTIVE_LLM_AGENT','MINIMAL_GATE',max_queries=1)
 if gate['qualification']!='VALID_MODEL_AGENT_EPISODE':
  (ROOT/'results/AGENT_RUN_STATUS.json').write_text(json.dumps({'minimal_gate_success':False,'pilot_started':False,'reason':gate['errors'],'new_model_inference_occurred':True},indent=2));return
 roster=json.loads((ROOT/'manifests/PAIRED_PILOT_REGISTRATION.json').read_text())['selected_episodes'];done=[]
 for item in roster:
  for method in ['A0_DIRECT','A1_STATIC_BM25_LLM','A2_FIXED_QUERY_LLM','A3_ADAPTIVE_LLM_AGENT']:
   row=execute(item['episode_index'],method,'PAIRED_PILOT');done.append(row)
   if row['status']=='STOPPED_BUDGET_OR_RUNTIME':
    (ROOT/'results/AGENT_RUN_STATUS.json').write_text(json.dumps({'minimal_gate_success':True,'pilot_started':True,'recorded_pilot_conditions':len(done),'planned_pilot_conditions':48,'status':'STOPPED_BUDGET_OR_RUNTIME'},indent=2));return
 (ROOT/'results/AGENT_RUN_STATUS.json').write_text(json.dumps({'minimal_gate_success':True,'pilot_started':True,'recorded_pilot_conditions':len(done),'planned_pilot_conditions':48,'status':'FINISHED_RECORDED_MATRIX'},indent=2))
if __name__=='__main__':main()
