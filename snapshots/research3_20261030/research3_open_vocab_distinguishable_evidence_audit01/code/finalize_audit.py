"""Final file/hash seal;no scientific qualification is upgraded."""
import csv,hashlib,json,platform,sys
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def entry(p):return {'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}
def main():
 v=load(R/'results/FINAL_VALIDATION.json');assert v['failed_check_count']==0 and v['status']=='PASS_MECHANICAL_AUDIT_WITH_SCIENTIFIC_BLOCKERS'
 assert all(v['required_artifacts_present'].values()) and v['old_files_modified']==0
 m=load(R/'RUN_MANIFEST.json');assert m['final_decision']==v['final_decision']=='GO_AFTER_INPUT_OR_LABEL_AUDIT'
 outputs=[entry(p) for p in sorted(R.rglob('*')) if p.is_file() and p.name not in ['RUN_MANIFEST.json','DELIVERY_SHA256.json']]
 parsed={}
 for e in outputs:
  p=R/e['path']
  if p.suffix=='.json':load(p);parsed[e['path']]='JSON_OK'
  elif p.suffix=='.jsonl':parsed[e['path']]=sum(1 for s in p.read_text().splitlines() if s.strip() and isinstance(json.loads(s),dict))
  elif p.suffix=='.csv':
   with p.open(newline='') as f:z=list(csv.DictReader(f))
   assert all(None not in x for x in z);parsed[e['path']]=len(z)
 m['input_output_code_hashes']={'core_inputs':load(R/'audit/FIRST_PASS_SOURCE_HASHES.json'),
   'old_asset_inputs':load(R/'audit/OLD_ASSET_HASH_SNAPSHOT.json')['assets'],
   'outputs':outputs,'code':[e for e in outputs if e['path'].startswith('code/')],
   'self_reference_rule':'RUN_MANIFEST and DELIVERY_SHA256 excluded from embedded outputs;delivery list includes RUN_MANIFEST and all other files,excluding its own self hash'}
 m.update({'manifest_phase':'SEALED_LIMITED_AUDIT_NOT_INDEPENDENT_REFERENCE','sealed_utc':datetime.now(timezone.utc).isoformat(),
  'old_files_modified':0,'validation_status':v['status'],'mechanical_check_count':v['check_count'],
  'runtime':{'python':platform.python_version(),'executable':sys.executable,'dependencies':'existing standard library only',
   'model_checkpoint_loading':False,'log_commands_executed':False,'peak_CPU_memory_and_current_assistant_tokens_independently_metered':False},
  'AI_usage_boundary':'current assistant semantic reasoning is AI pre-audit;0 refers to additional programmatic model/agent calls,not human review or absence of AI',
  'parsed_outputs':parsed,'semantic_certification':'NOT_INDEPENDENTLY_VALIDATED_NOT_GOLD',
  'new_experiment_executed':False,'new_predictions_created':False,'scientific_qualification':v['scientific_qualification'],
  'completion_limit':'384limitedaudit records,5200pairattempts;only3208supplied-predicatepairs evaluable;0newcasebaselineoutcomes compared;formalresidual countNOT_AVAILABLE'})
 m['actual_commands'] += ['python3 -B research3_open_vocab_distinguishable_evidence_audit01/code/validate_audit.py',
                          'python3 -B research3_open_vocab_distinguishable_evidence_audit01/code/finalize_audit.py']
 m['command_inventory_scope']='main artifact-producing/validation commands;exploratory read transcript not exhaustively reconstructed;firstpassv1 retained and amended beforecandidateaccess'
 mp=R/'RUN_MANIFEST.json';dp=R/'audit/DELIVERY_SHA256.json'
 def sealcheck():
  dump(mp,m);entries=outputs+[entry(mp)];entries.sort(key=lambda e:e['path']);dump(dp,entries)
  z=load(dp);actual={str(p.relative_to(R)) for p in R.rglob('*') if p.is_file() and p!=dp}
  assert {e['path'] for e in z}==actual
  assert all((R/e['path']).stat().st_size==e['bytes'] and sha(R/e['path'])==e['sha256'] for e in z)
  return z
 z=sealcheck();m['delivery_readback_first_pass']='PASS_FILE_HASH_CHECK_ONLY';z=sealcheck()
 print(json.dumps({'execution_status':m['execution_status'],'final_decision':m['final_decision'],
  'required_artifacts':17,'delivered_files_including_checksum_list':len(z)+1,
  'delivered_bytes':sum(e['bytes'] for e in z)+dp.stat().st_size,'delivery_readback_hash_check':'PASS',
  'delivery_list_sha256':sha(dp),'qualified_residual_error_count':'NOT_AVAILABLE',
  'new_model_calls':0,'new_agent_calls':0,'new_training_runs':0,'server_access':False,'old_files_modified':0},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
