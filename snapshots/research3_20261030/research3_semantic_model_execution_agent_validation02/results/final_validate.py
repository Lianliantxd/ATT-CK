"""Read-only artifact integrity checks, then a delivery receipt. No inference."""
import ast,collections,csv,hashlib,json,math,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from project import ROOT as R,PREVIOUS,BASELINES,sha256,records,fingerprint
from agent_transport.transport import validate_real_episode
def main():
 required='MODEL_ASSET_AUDIT.md MODEL_AUTHORIZATION_REQUEST.md MODEL_ENVIRONMENT_MANIFEST.json MODEL_EXECUTION_STATUS.csv EMBEDDING_REAL_PREDICTIONS.jsonl EMBEDDING_REAL_RESULTS.csv EMBEDDING_CANDIDATE_RECALL.csv EMBEDDING_ERROR_ANALYSIS.md RERANKER_REAL_PREDICTIONS.jsonl RERANKER_REAL_RESULTS.csv RERANKER_CANDIDATE_UPPER_BOUNDS.csv RERANKER_ERROR_ANALYSIS.md LLM_54_RESPONSES_AUDIT.md LLM_VALID_RESPONSE_RESULTS.csv LLM_EXPERIMENT_PROTOCOL_V2.md LLM_INFERENCE_RECEIPTS.jsonl AGENT_TRANSPORT_ROOT_CAUSE.md AGENT_TRANSPORT_FIX_VALIDATION.md AGENT_EPISODE_PROTOCOL.md AGENT_TOOL_SECURITY_TESTS.md AGENT_VALID_EPISODES.jsonl AGENT_PAIRED_COMPARISON.csv AGENT_COST_REPORT.csv AGENT_ERROR_ANALYSIS.md SEMANTIC_MODEL_INCREMENTAL_VALUE.md LLM_AGENT_INCREMENTAL_VALUE.md METHOD_RESEARCH_DECISION.md R3_SEMANTIC_MODEL_EXECUTION_AGENT_VALIDATION_RESULTS.md'.split()
 assert all((R/n).is_file() and (R/n).stat().st_size for n in required)
 inherited_assets=json.loads((R/'manifests/INHERITED_ASSETS.json').read_text());assert len(inherited_assets)==256
 assert all(sha256(Path(x['source']))==x['sha256'] for x in inherited_assets)
 previous=json.loads((PREVIOUS/'manifests/DELIVERY_SHA256.json').read_text());assert all(sha256(PREVIOUS/x['path'])==x['sha256'] for x in previous)
 protocol=json.loads((R/'manifests/LOCAL_AGENT_ACTUAL_PROTOCOL.json').read_text())
 for name,key in [('agent_episodes/run_pilot.py','source_sha256'),('agent_transport/transport.py','transport_sha256'),('agent_environment/token_budget_environment.py','budget_environment_sha256'),('llm/local_client.py','client_sha256')]:assert sha256(R/name)==protocol[key],name
 assert len(records(R/'LLM_INFERENCE_RECEIPTS.jsonl'))==54
 episodes=records(R/'AGENT_VALID_EPISODES.jsonl');assert len(episodes)==3
 for ep in episodes:assert validate_real_episode(ep)['structural_integrity']
 native=[]
 for p in (R/'agent_episodes/native_receipts').glob('*.json'):
  if p.stem.endswith(('_devices','_attempt')):continue
  x=json.loads(p.read_text());assert x['model_digest']==protocol['model_digest'] and x['options']['num_gpu']==0 and x['options']['num_thread']==2
  assert hashlib.sha256(x['prompt'].encode()).hexdigest()==x['prompt_sha256']
  devices=json.loads(p.with_name(p.stem+'_devices.json').read_text())
  assert any(d['digest']==x['model_digest'] and d['size_vram']==0 for d in devices['models']);native.append(x)
 llm=json.loads((R/'results/NEW_LLM_SUMMARY.json').read_text());assert len(native)==llm['native_responses']==74
 assert llm['attempts']==78 and llm['input_tokens_with_unknown_attempt_reservations']<=500000 and llm['output_tokens_with_unknown_attempt_reservations']<=45000 and llm['request_span_seconds']<5400
 stop=json.loads((R/'results/LOCAL_MODEL_STOP_RECEIPT.json').read_text());assert stop['ps_after']=={'models':[]} and stop['unload']['done_reason']=='unload'
 proof=json.loads((R/'results/BACKEND_CONTEXT_FEEDBACK_PROOF.json').read_text());assert len(proof)==74 and all(x['complete_prompt_body_in_backend_context'] for x in proof)
 # Actual native input repair evidence, including unchanged nonempty variants.
 first={x['sample_id']:x for x in records(R/'results/server_gpu_v1/NEURAL_INPUTS.jsonl')};second={x['sample_id']:x for x in records(R/'results/server_gpu/NEURAL_INPUTS.jsonl')}
 changed=[];unchanged=0
 for sid,new in second.items():
  assert new['raw_pool_hash']==first[sid]['raw_pool_hash']
  for rule in ['prefix','window']:
   old=first[sid]['variants'][rule]['views'];now=new['variants'][rule]['views'];assert now['V0']
   if old['V0']:assert old==now;unchanged+=1
   else:changed.append((sid,rule))
  assert max(n for m in new['actual_tokenizer_counts_by_model'].values() for rule in m.values() for n in rule.values())<=2048
 assert len(changed)==17 and unchanged==1933
 assert json.loads((R/'results/server_gpu/NEURAL_RUN_STATUS.json').read_text())['status']=='BOTH_MODELS_FULL_P0_COMPLETE'
 readback=(R/'results/SERVER_FINAL_READBACK.txt').read_text().splitlines();server_bytes=int(readback[0].split()[0]);assert server_bytes<4000000000
 assert len(readback)==4,'Unexpected remaining GPU PID or server readback output'
 for line in readback[1:]:
  expected,path=line.split();assert sha256(R/'results/server_gpu'/Path(path).name)==expected
 assert json.loads((R/'results/server_gpu/manifests/NEURAL_RUNTIME_PROTOCOL.json').read_text())['source_sha256']==sha256(R/'embedding/run_neural_gpu.py')
 marker=json.loads((R/'results/server_gpu/manifests/EMPTY_INPUT_REPAIR_V2_STARTED.json').read_text());assert marker['wrapper_sha256']==sha256(R/'embedding/run_neural_gpu_v2.py')
 for name,methods in [('EMBEDDING_REAL_PREDICTIONS.jsonl',5),('RERANKER_REAL_PREDICTIONS.jsonl',6)]:
  rows=records(R/name);assert len(rows)==methods*975
  assert sha256(R/name)==sha256(R/'results/server_gpu'/name)
  assert len({x['method'] for x in rows})==methods
  for method in {x['method'] for x in rows}:assert len({x['sample_id'] for x in rows if x['method']==method})==975
  assert all(len(x['predictions'])==len(set(x['predictions'])) for x in rows)
 source_count=0
 for p in R.rglob('*.py'):
  if any(x in p.parts for x in ['venvs','__pycache__']):continue
  ast.parse(p.read_text(),filename=str(p));source_count+=1
 report=(R/'R3_SEMANTIC_MODEL_EXECUTION_AGENT_VALIDATION_RESULTS.md').read_text();assert len(re.findall(r'^### \d+\.',report,re.M))==45
 result={'status':'PASS','required_core_files':len(required),'inherited_assets_unchanged':len(inherited_assets),'previous_delivery_files_unchanged':len(previous),'new_native_model_responses_verified':len(native),'new_attempts_including_four_timeouts':78,'model_CPU_device_and_prompt_hashes_all_pass':True,'backend_prompt_proofs':74,'real_agent_episodes_verified':3,'input_repair_changed_empty_variants':len(changed),'previously_nonempty_variants_unchanged':unchanged,'full_P0_each_neural_condition':975,'embedding_conditions':5,'cross_encoder_conditions':6,'frozen_protocol_source_hashes_pass':True,'server_prediction_hashes_match_downloaded_files':True,'server_project_bytes':server_bytes,'server_GPU_experiment_processes_remaining':0,'source_files_syntax_checked':source_count,'report_questions_answered':45,'new_external_LLM_calls':0,'independent_external_test':'NOT_READY','remaining_limits':'Agent valid paired subset tiny;4 timeout backend completion times UNKNOWN; no causal semantic evidence use proof; single-seed EXPOSED_DEV'}
 (R/'results/FINAL_VALIDATION.json').write_text(json.dumps(result,indent=2))
 files=[]
 for p in sorted(R.rglob('*')):
  if not p.is_file() or p.is_symlink() or any(s in p.parts for s in ['venvs','__pycache__','.git']):continue
  if p==R/'manifests/DELIVERY_SHA256.json':continue
  files.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha256(p)})
 (R/'manifests/DELIVERY_SHA256.json').write_text(json.dumps(files,indent=2));print(json.dumps(result,indent=2));print('Delivery indexed files:',len(files))
if __name__=='__main__':main()
