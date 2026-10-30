"""Explicit V2 repair: all tool feedback, attempt ledger, original global budget."""
import csv,datetime,hashlib,json,sys,time,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R),str(R/'llm')]
import run_local_pilot as V1
import local_ollama as client
from agent_environment.environment import create_episode,proxy_tokens
MODES=['DIRECT216','KNOWLEDGE20','RETRIEVAL20','STATIC_EVIDENCE_S','ADAPTIVE_AGENT_S']
CAP=240; WALL=3600; halted=False
class BudgetStop(Exception):pass

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def old_receipts():
 out=[]
 for p in (R/'experiments').rglob('PILOT_*.json'):
  if p.name.endswith(('_devices.json','_attempt.json')):continue
  try:
   x=json.loads(p.read_text())
   if 'response' in x and 'created_at' in x['response']:out.append((p,x))
  except (ValueError,KeyError):continue
 return sorted(out,key=lambda z:(z[1]['response']['created_at'],str(z[0])))
OLD=old_receipts()
if not OLD:raise RuntimeError('No V1 native receipt; cannot reconstruct original wall budget')
ORIGINAL_START=min(datetime.datetime.fromisoformat(x['response']['created_at'].replace('Z','+00:00')).timestamp()-x['wall_seconds'] for p,x in OLD)
INTERRUPTION=json.loads((R/'results/V1_INTERRUPTION.json').read_text())
V1_ATTEMPTS=len(OLD)+INTERRUPTION['interrupted_request_count_upper_bound']
def remaining():return max(0.,ORIGINAL_START+WALL-time.time())
def attempts():return V1_ATTEMPTS+len(list((R/'experiments').glob('V2_*_attempt.json')))

def shared_knowledge(env,candidates):
 remain=V1.CONFIG['knowledge_render_max_utf8_bytes'];parts=[];seen=set()
 for t in env.trace:
  z=t.get('result',{})
  if t['tool']=='retrieve_attack_technique' and 'text' in z:
   k=z['technique_id'];line=k+': '+z['text'];piece=V1.cutbytes(line,max(0,remain-1))
   if piece:parts.append(piece);remain-=len(piece.encode())+1;seen.add(k)
 for k in candidates[:20]:
  if k in seen:continue
  if remain<=len(k.encode())+3:break
  # All knowledge, fetched first then static, shares this single byte cap.
  each=max(0,(remain-10*(20-len(seen)))//max(1,20-len(seen)))
  line=k+': '+V1.cutbytes(V1.DOCS[k],each);line=V1.cutbytes(line,max(0,remain-1))
  if line:parts.append(line);remain-=len(line.encode())+1;seen.add(k)
 return '\n'.join(parts)

def feedback(env,visible):
 out=[]
 for t in env.trace:
  z=t.get('result',{});z={k:v for k,v in z.items() if k not in ('events','text')}
  if 'events' in t.get('result',{}):
   z['returned_events']=[{'event_id':e['event_id'],'source_type':e['source_type'],'text_location':'displayed log observations' if e['event_id'] in visible else 'omitted by shared log rendering byte cap','tool_truncated':e.get('truncated',False)} for e in t['result']['events']]
  if t['tool']=='retrieve_attack_technique' and 'text' in t.get('result',{}):z['text_location']='shared public knowledge section; fetched definitions prioritized under 3500 byte total cap'
  out.append({'tool':t['tool'],'arguments':t['arguments'],'status':t['status'],'result':z})
 return json.dumps(out,ensure_ascii=False)

def prompt_final(mode,env,initial,candidates):
 observed=V1.merged(initial,env.trace)
 prompt,schema,visible,proxy,allowed=V1.final_prompt(mode,observed,candidates)
 if mode.startswith('ADAPTIVE'):
  base=V1.knowledge(candidates,20);kn=shared_knowledge(env,candidates)
  prompt=prompt.replace(base,kn,1)+'\nComplete tool feedback (event text is in displayed logs; omitted text is explicitly marked):\n'+feedback(env,visible)
 return prompt,schema,visible,proxy,allowed,observed

def prompt_action(env,observed,candidates):
 prompt,schema=V1.action_prompt(env,observed,candidates)
 _,visible,_=V1.render(observed)
 prompt=prompt.replace(V1.knowledge(candidates,20),shared_knowledge(env,candidates),1)
 return prompt+'\nComplete tool feedback (event text is in displayed logs; omitted text is explicitly marked):\n'+feedback(env,visible),schema

def cached(index,mode,prompt,schema):
 if mode.startswith('ADAPTIVE'):return None
 tag=f'PILOT_{index:04d}_{mode}_final'
 candidates=[(p,x) for p,x in OLD if x.get('tag')==tag]
 if not candidates:return None
 p,x=candidates[0] # first native response only, never choose by output quality
 expected={**client.OPTIONS,'num_predict':512}
 # V1 did not save schema: reconstruct the schema from unchanged V1 final_prompt
 # and the exact same deterministic condition inputs. Native prompt/options must match.
 if x.get('prompt')!=prompt or x.get('prompt_sha256')!=hashlib.sha256(prompt.encode()).hexdigest() or x.get('options')!=expected or x.get('think') is not False or x.get('model_digest')!=client.MODEL_DIGEST:return None
 d=p.with_name(p.stem+'_devices.json')
 if not d.exists():return None
 models=json.loads(d.read_text()).get('models',[])
 if not any(m.get('size_vram')==0 and m.get('digest')==client.MODEL_DIGEST for m in models):return None
 receipt=dict(x);receipt.update(cache_source=str(p),cache_qualification='IDENTICAL_NATIVE_PROMPT_OPTIONS_MODEL_AND_RECONSTRUCTED_FROZEN_V1_SCHEMA',schema_sha256=digest(schema),cache_reused=True)
 return x['response'],receipt

def call(prompt,schema,tag,receipts,max_tokens=512):
 if halted:raise BudgetStop('RUN_HALTED')
 if attempts()>=CAP or remaining()<1:raise BudgetStop('ORIGINAL_GLOBAL_BUDGET_REACHED')
 result,receipt=client.generate(prompt,schema,tag,max_tokens,timeout=min(180.,remaining()))
 receipts.append(receipt) # keep successful native cost even if parsing/context fails
 if result.get('prompt_eval_count',0)+result.get('eval_count',0)>client.OPTIONS['num_ctx']:raise ValueError('Model context accounting overflow')
 return result

def visible_stats(initial,observed):
 text,ids,proxy=V1.render(observed);initial_map={e['event_id']:e['text'] for e in initial};rendered=[];remain=V1.CONFIG['final_prompt_log_render_max_utf8_bytes']
 for e in observed:
  pre='['+e['event_id']+']['+e['source_type']+'] '
  if len(pre.encode())>=remain:break
  t=V1.cutbytes(e['text'],remain-len(pre.encode())-1)
  if not t:continue
  remain-=len((pre+t).encode())+1;old=initial_map.get(e['event_id'],'');extra=t[len(old):] if t.startswith(old) else t
  rendered.append({'event_id':e['event_id'],'visible_text_utf8_bytes':len(t.encode()),'visible_proxy_tokens':proxy_tokens(t),'is_new_event':e['event_id'] not in initial_map,'new_visible_text_utf8_bytes':len(extra.encode()),'new_visible_text_proxy_tokens':proxy_tokens(extra),'text_sha256':hashlib.sha256(t.encode()).hexdigest()})
 return {'rendered_event_ids':ids,'rendered_log_proxy_tokens':proxy,'rendered_log_utf8_bytes':len(text.encode()),'model_visible_event_spans':rendered,'visible_new_event_ids':[e['event_id'] for e in rendered if e['is_new_event']],'visible_additional_text_proxy_tokens':sum(e['new_visible_text_proxy_tokens'] for e in rendered),'visible_additional_text_utf8_bytes':sum(e['new_visible_text_utf8_bytes'] for e in rendered)}

def setup(item,mode):
 env=create_episode(item['episode_index'],'S',initialization_max_proxy_tokens=256);initial=env.initial_observation()['events'];candidates=V1.rank(V1.events_text(initial))
 if mode=='STATIC_EVIDENCE_S':env.call('search_events',{'source_type':'all','keywords':V1.get_keywords(initial) or ['event'],'time_range':None,'max_results':20})
 return env,initial,candidates

def execute(item,mode,cache_only=False):
 global halted
 env,initial,candidates=setup(item,mode);index=item['episode_index'];prefix=f'V2_{index:04d}_{mode}';receipts=[];decisions=[];errors=[];pred=[];evidence=[];limitation='';started=time.time();status='COMPLETED';used_cache=False
 if cache_only:
  if mode.startswith('ADAPTIVE'):return None
  p,s,*_=prompt_final(mode,env,initial,candidates);hit=cached(index,mode,p,s)
  if hit is None:return None
 else:hit=None
 try:
  if hit is not None:result,receipt=hit;receipts.append(receipt);used_cache=True
  else:
   if mode.startswith('ADAPTIVE'):
    for step in range(2):
     observed=V1.merged(initial,env.trace);p,s=prompt_action(env,observed,candidates);result=call(p,s,prefix+f'_action{step}',receipts,256);decision=json.loads(result.get('response',''));decisions.append(decision)
     if decision['tool']=='stop':break
     env.call(decision['tool'],decision['arguments'])
     if env.cost()['returned_log_proxy_tokens']>=env.cost()['returned_log_proxy_token_limit']:break
   p,s,visible,proxy,allowed,observed=prompt_final(mode,env,initial,candidates);result=call(p,s,prefix+'_final',receipts)
  p,s,visible,proxy,allowed,observed=prompt_final(mode,env,initial,candidates);body=json.loads(result.get('response',''));pred=body['techniques'];evidence=body['evidence_ids'];limitation=body['evidence_limitations']
  if len(pred)!=10 or len(set(pred))!=10 or set(pred)-set(allowed):raise ValueError('Malformed or duplicate technique ranking')
  if set(evidence)-set(visible):raise ValueError('Citation outside rendered model observation')
  if not env.call('submit_technique_ranking',{'ranking':pred,'evidence_ids':evidence}).get('accepted'):raise ValueError('Tool submission rejected')
 except BudgetStop as exc:status='INCOMPLETE_BUDGET' if receipts else 'NOT_EXECUTED_BUDGET';errors.append(str(exc));pred=[]
 except KeyboardInterrupt:status='INTERRUPTED';errors.append('KeyboardInterrupt');pred=[];halted=True
 except Exception as exc:
  status='FAILED';errors.append(type(exc).__name__+': '+str(exc));pred=[]
  if isinstance(exc,RuntimeError):halted=True
 observed=V1.merged(initial,env.trace);attempt_files=sorted((R/'experiments').glob(prefix+'*_attempt.json'));ledgers=[json.loads(p.read_text()) for p in attempt_files]
 # Receipts include cache costs; native ledgers retain failed attempts and unknown counts.
 costs=ledgers if ledgers else [{'prompt_tokens':m['response'].get('prompt_eval_count'),'output_tokens':m['response'].get('eval_count'),'wall_seconds':m.get('wall_seconds')} for m in receipts]
 def total(k):return sum(x[k] for x in costs) if costs and all(x.get(k) is not None for x in costs) else None
 row={'sample_id':item['sample_id'],'episode_index':index,'scenario_id':item['scenario_id'],'method':mode,'protocol_version':'V2_TOOL_FEEDBACK_REPAIR','model_id':client.MODEL,'model_digest':client.MODEL_DIGEST,'qualification':'PROJECT_NEW_LOCAL_CPU_LLM_INFERENCE','execution_status':status,'predictions':pred,'evidence_ids':evidence if pred else [],'evidence_limitations':limitation,'failure':status=='FAILED','errors':errors,'query_budget':'S','cost':env.cost(),'model_calls':len(costs),'new_model_call_attempts':len(ledgers),'cache_reused':used_cache,'model_prompt_tokens':total('prompt_tokens'),'model_output_tokens':total('output_tokens'),'model_seconds':total('wall_seconds'),'wall_seconds':time.time()-started,'model_call_record_paths':[str(R/'experiments'/(m['tag']+'.json')) for m in receipts],'attempt_record_paths':[str(p) for p in attempt_files],'cache_sources':[m['cache_source'] for m in receipts if 'cache_source' in m],'initial_candidate_top100':candidates[:100],**visible_stats(initial,observed)}
 if mode.startswith('ADAPTIVE'):
  trajectory={'episode_id':item['sample_id']+'_'+mode+'_V2','execution_step_id':item['sample_id'],'model_id':client.MODEL,'model_digest':client.MODEL_DIGEST,'protocol_version':'V2_TOOL_FEEDBACK_REPAIR','qualification':'REAL_LOCAL_LLM_TOOL_AGENT_EXPERIMENT' if ledgers else 'NOT_EXECUTED_BUDGET','tool_query_decisions':decisions,'tools':env.trace,'final_candidate_ranking':pred,'final_state':row,'model_call_record_paths':row['model_call_record_paths'],'initial_observation_hash':digest(initial)}
 else:trajectory=None
 return row,trajectory

def main():
 roster=json.loads((R/'data_manifests/PILOT_EPISODES.json').read_text());selected=[];seen=set()
 for item in roster:
  if item['scenario_id'] not in seen:selected.append(item);seen.add(item['scenario_id'])
 assert len(selected)==7
 reg={'protocol_version':'V2_TOOL_FEEDBACK_REPAIR','old_protocol_adaptive_qualification':'INVALID_TOOL_RESULT_FORWARDING','original_start_unix':ORIGINAL_START,'original_wall_limit_seconds':WALL,'remaining_at_prepare_seconds':remaining(),'old_attempts_upper_bound':V1_ATTEMPTS,'total_attempt_cap':CAP,'primary_conditions':MODES,'primary_episodes':selected,'planned_conditions':35,'order':'cache first without calls; mode then seven scenarios','model_options':client.OPTIONS,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'knowledge_budget_utf8_bytes':3500,'schema_cache_provenance':'V1 schema reconstructed deterministically from unchanged V1 final_prompt; native V1 stored prompt/options, not schema'}
 (R/'manifests/EXPERIMENT_REGISTRATION_V2.json').write_text(json.dumps(reg,indent=2))
 if '--prepare-only' in sys.argv:print(json.dumps(reg));return
 archive=R/'experiments/PILOT_V1_INVALID_AGENT';archive.mkdir(exist_ok=True)
 for name in ['LLM_TECHNIQUE_PREDICTIONS.jsonl','AGENT_TRAJECTORIES.jsonl']:
  src=R/name;dst=archive/name
  if src.exists():
   if dst.exists():raise RuntimeError('Archive already exists; do not overwrite V1 or V2 output')
   shutil.move(str(src),str(dst))
 rows=[];finished=set();trajectories=[]
 def save(row,trajectory):
  rows.append(row);finished.add((row['episode_index'],row['method']))
  with (R/'LLM_TECHNIQUE_PREDICTIONS.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
  if trajectory:
   trajectories.append(trajectory)
   with (R/'AGENT_TRAJECTORIES.jsonl').open('a') as f:f.write(json.dumps(trajectory)+'\n')
  summary();print(row['sample_id'],row['method'],row['execution_status'],'cache',row['cache_reused'],'remaining',round(remaining(),1),flush=True)
 def summary():
  result={'protocol_version':'V2_TOOL_FEEDBACK_REPAIR','planned_conditions':35,'recorded_conditions':len(rows),'completed_conditions':sum(x['execution_status']=='COMPLETED' for x in rows),'failed_conditions':sum(x['execution_status']=='FAILED' for x in rows),'not_executed_budget_conditions':sum(x['execution_status']=='NOT_EXECUTED_BUDGET' for x in rows),'incomplete_budget_conditions':sum(x['execution_status']=='INCOMPLETE_BUDGET' for x in rows),'interrupted_conditions':sum(x['execution_status']=='INTERRUPTED' for x in rows),'cache_reused_conditions':sum(x['cache_reused'] for x in rows),'new_model_attempts':len(list((R/'experiments').glob('V2_*_attempt.json'))),'total_attempt_upper_bound':attempts(),'remaining_original_wall_seconds':remaining(),'actual_elapsed_from_original_start_seconds':time.time()-ORIGINAL_START,'local_only':True,'new_external_calls':0,'num_gpu':0,'cpu_num_threads':2}
  (R/'results/LOCAL_PILOT_RUN_SUMMARY.json').write_text(json.dumps(result,indent=2));(R/'results/PILOT_PROGRESS.json').write_text(json.dumps(result,indent=2))
 try:
  for mode in MODES:
   for item in selected:
    value=execute(item,mode,True)
    if value:save(*value)
  for mode in ['ADAPTIVE_AGENT_S']+[m for m in MODES if m!='ADAPTIVE_AGENT_S']:
   for item in selected:
    if (item['episode_index'],mode) not in finished:save(*execute(item,mode))
 finally:summary()
if __name__=='__main__':main()
