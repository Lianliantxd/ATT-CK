"""Offline final validation. Reads only frozen derived inputs, not raw archives."""
import ast,csv,hashlib,importlib.util,json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R.parent/'research3_technique_strong_baselines_generalization02'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for z in iter(lambda:f.read(1024*1024),b''):h.update(z)
 return h.hexdigest()
def load(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
checks={};inherited=json.loads((R/'manifests/INHERITED_ASSETS.json').read_text())
checks['inherited_source_hashes_unchanged']=all(sha(Path(x['source']))==x['sha256'] for x in inherited)
checks['inherited_frozen_copies_match']=all(sha(Path(x['frozen']))==x['sha256'] for x in inherited if 'frozen' in x)
assert checks['inherited_source_hashes_unchanged'] and checks['inherited_frozen_copies_match']
required='''MODEL_ASSET_AUTHORIZATION_AUDIT.md PRETRAINED_MODEL_REGISTER.csv MODEL_LICENSE_AND_RESOURCE_REPORT.md MODEL_ENVIRONMENT_MANIFEST.json
EMBEDDING_BASELINE_RESULTS.csv EMBEDDING_PREDICTIONS.jsonl EMBEDDING_CANDIDATE_RECALL.csv EMBEDDING_INPUT_ABLATION.csv EMBEDDING_ERROR_ANALYSIS.md
RERANKER_RESULTS.csv RERANKER_PREDICTIONS.jsonl CANDIDATE_RECALL_UPPER_BOUNDS.csv RERANKER_ERROR_ANALYSIS.md
LLM_EXPERIMENT_PROTOCOL.md LLM_PROMPTS.md LLM_TECHNIQUE_RESULTS.csv LLM_TECHNIQUE_PREDICTIONS.jsonl LLM_TOKEN_AND_RUNTIME_REPORT.csv
AGENT_ENVIRONMENT_SPEC.md AGENT_TOOL_SCHEMAS.json AGENT_BUDGET_PROTOCOL.md AGENT_TOOL_SECURITY_TESTS.md STATIC_RETRIEVAL_AGENT_CONTROLS.csv AGENT_TRAJECTORIES.jsonl AGENT_TECHNIQUE_RESULTS.csv AGENT_COST_BENEFIT_ANALYSIS.md
SEMANTIC_REPRESENTATION_COMPARISON.md LLM_INCREMENTAL_VALUE_ANALYSIS.md AGENT_INCREMENTAL_VALUE_ANALYSIS.md ERROR_SOURCE_TAXONOMY.csv METHOD_HYPOTHESIS_AND_FORMULATION.md METHOD_RESEARCH_DECISION.md R3_LLM_AGENT_TECHNIQUE_REASONING_RESULTS.md'''.split()
assert len(required)==33
checks['required_files_exist']=all((R/p).is_file() for p in required)
checks['blocked_predictions_empty']=all((R/p).stat().st_size==0 for p in ['EMBEDDING_PREDICTIONS.jsonl','RERANKER_PREDICTIONS.jsonl','AGENT_TRAJECTORIES.jsonl'])
for p in ['EMBEDDING_BASELINE_RESULTS.csv','RERANKER_RESULTS.csv']:
 assert all(x['N_executed']=='0' and x['top1']=='N/A' for x in csv.DictReader((R/p).open()))
parsed=[]
for p in R.rglob('*.py'):
 if 'venvs' in p.parts or 'frozen_baselines' in p.parts:continue
 compile(p.read_text(),str(p),'exec');parsed.append(str(p.relative_to(R)))
checks['python_compile_pass']=True
checks['tool_security_26_pass']=bool(re.search(r'Ran 26 tests.*\n\nOK',(R/'results/tool_security_final.log').read_text(),re.S))
checks['adapter_interface_10_pass']=bool(re.search(r'Ran 10 tests.*\n\nOK',(R/'results/interface_final.log').read_text(),re.S))
det=json.loads((R/'results/DETERMINISTIC_CONTROL_METRICS.json').read_text())
checks['all_2695_real_tool_traces_pass']=det['artifact_audit']['checked_trajectories']==2695 and det['artifact_audit']['budgets_and_proxy_recount_exact'] and det['artifact_audit']['all_evidence_seen_and_submissions_match']
refs={x['sample_id']:x for x in load(B/'datasets/p2_v2/reference_sampled.jsonl')}
universe=json.loads((B/'knowledge/K2_DESCRIPTION_16_1.json').read_text())
sp=importlib.util.spec_from_file_location('frozen',R/'frozen_baselines/research3_attack_technique_benchmark01/evaluate_techniques.py');ev=importlib.util.module_from_spec(sp);sp.loader.exec_module(ev)
checks['evaluator_matches_B_frozen_p0']=sha(B/'frozen_p0/evaluate_techniques.py')==sha(R/'frozen_baselines/research3_attack_technique_benchmark01/evaluate_techniques.py')
rows=load(R/'LLM_TECHNIQUE_PREDICTIONS.jsonl');summary=json.loads((R/'results/LOCAL_PILOT_RUN_SUMMARY.json').read_text())
assert len(rows)==35 and sum(x['execution_status']=='NOT_EXECUTED_BUDGET' for x in rows)==27
assert sum(x['execution_status']=='FAILED' for x in rows)==3 and sum(x['execution_status']=='COMPLETED' for x in rows)==5
checks['v2_status_ledger_exact']=summary['new_model_attempts']==0 and sum(x['cache_reused'] for x in rows)==8
metricrows=[x for x in csv.DictReader((R/'LLM_TECHNIQUE_RESULTS.csv').open()) if x['protocol']=='V2_PRIMARY_RESOURCE_LIMITED' and x['analysis_unit']=='QUERY_EXECUTED']
for z in metricrows:
 selected=[x for x in rows if x['method']==z['method'] and x['model_calls']>0]
 if not selected:assert z['top10_accuracy']=='N/A';continue
 records=[{'ground_truth':refs[x['sample_id']]['ground_truth'],'predictions':x['predictions'] if x['execution_status']=='COMPLETED' else []} for x in selected]
 m=ev.summarize(records,universe)
 for k in ['top1_accuracy','top5_accuracy','top10_accuracy','mrr']:assert abs(float(z[k])-m[k])<1e-12
checks['LLM_frozen_evaluator_recheck']=True
allcand=list(csv.DictReader((R/'CANDIDATE_RECALL_UPPER_BOUNDS.csv').open()))
for protocol,refp in [('P0','datasets/p0_reference.jsonl'),('P1','datasets/p1_resampled/reference.jsonl'),('P2_SAMPLED','datasets/p2_v2/reference_sampled.jsonl')]:
 reference={x['sample_id']:x for x in load(B/refp)};pred=load(R/f'rerankers/CANDIDATES_{protocol}.jsonl')
 assert len(reference)==len(pred)
 for k in [20,50,100]:
  matches=[];rec=[];allg=[];miss=0;zero=0
  for x in pred:
   assert len(x['predictions'])==216 and set(x['predictions'])==set(universe)
   g={ev.normalize_technique_id(t) for t in reference[x['sample_id']]['ground_truth']};assert None not in g
   f=g&set(x['predictions'][:k]);matches.append(bool(f));rec.append(len(f)/len(g));allg.append(f==g);miss+=len(g-f);zero+=not f
  row=next(x for x in allcand if x['protocol']==protocol and int(x['k'])==k)
  for key,value in [('candidate_hit_at_k',sum(matches)/len(pred)),('candidate_recall_at_k',sum(rec)/len(pred)),('all_gold_recalled_fraction',sum(allg)/len(pred))]:assert abs(float(row[key])-value)<1e-12
  assert int(row['unrecalled_gold_occurrences'])==miss and int(row['zero_gold_candidate_queries'])==zero
checks['candidate_all9_metrics_recomputed']=True
native=[];device_sizes=[]
for p in (R/'experiments').glob('PILOT_*.json'):
 x=json.loads(p.read_text())
 if not isinstance(x.get('response'),dict):continue
 native.append(x);devices=json.loads(p.with_name(p.stem+'_devices.json').read_text())['models']
 target=[v for v in devices if v.get('digest')==x['model_digest']]
 assert target and all(v.get('size_vram') is not None and v['size_vram']==0 for v in target)
 device_sizes.extend(v['size'] for v in target if isinstance(v.get('size'),(int,float)))
assert len(native)==54 and sum(x['response']['prompt_eval_count'] for x in native)==130642 and sum(x['response']['eval_count'] for x in native)==8265
checks['all54_native_CPU_and_costs_verified']=True
text=(R/'R3_LLM_AGENT_TECHNIQUE_REASONING_RESULTS.md').read_text();qa=re.findall(r'^### (\d+)\. ',text,re.M)
assert list(map(int,qa))==list(range(1,45));checks['all44_questions_answered']=True
checks['two_figures_rendered']=all((R/f'analysis-output/figures/{n}.{s}').is_file() for n in ['figure-01-controls','figure-02-candidate-ceiling'] for s in ['pdf','png'])
assert all(checks.values()),checks
payload={'status':'PASS_WITH_DECLARED_EXPERIMENT_BLOCKERS','primary_research_status':'PARTIAL_COMPLETION_WITH_DOCUMENTED_BLOCKERS','checks':checks,'inherited_assets_checked':len(inherited),'required_files_checked':len(required),'python_sources_compiled':len(parsed),'actual_native_research_responses':54,'interrupted_requests_upper_bound':1,'interrupted_cost':'UNKNOWN','LLM_API_reported_model_allocation_bytes_min':min(device_sizes) if device_sizes else None,'LLM_API_reported_model_allocation_bytes_max':max(device_sizes) if device_sizes else None,'memory_qualification':'Ollama model allocation size, not process RSS or measured peak RAM','peak_process_RSS':'NOT_MEASURED','external_llm_calls':0,'new_model_downloads':0,'new_V2_inference_calls':0,'valid_repaired_LLM_agent_episodes':0,'agent_performance':'N/A','known_API_prompt_tokens':130642,'known_API_output_tokens':8265,'known_API_wall_seconds':sum(x['wall_seconds'] for x in native),'synthetic_preflight_excluded':True,'not_execution_completion_claim':'Files/checks pass; Embedding/CrossEncoder and valid Agent comparisons remain unexecuted. No independent generalization or innovation claim.'}
(R/'results/DELIVERY_VALIDATION.json').write_text(json.dumps(payload,indent=2))
manifest=[]
for p in sorted(R.rglob('*')):
 if not p.is_file() or 'venvs' in p.parts or '__pycache__' in p.parts or p.name=='DELIVERY_SHA256.json':continue
 manifest.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)})
(R/'manifests/DELIVERY_SHA256.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(payload,indent=2))
