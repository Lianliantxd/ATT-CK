import csv,json,hashlib,sys,py_compile,subprocess,re
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'frozen_p0'),str(R/'baselines')]
from evaluate_techniques import summarize,normalize_technique_id

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def read(path):
 with Path(path).open() as f:return [json.loads(x) for x in f]
required='''P0_FROZEN_BASELINE_AUDIT.md P1_RESAMPLING_PROTOCOL.md P1_RESAMPLED_DATA_MANIFEST.json P2_V2_DATA_MANIFEST.json P2_AUTHORIZED_STEP_MANIFEST.csv P0_P1_P2_COMPARABILITY_REPORT.md KNOWLEDGE_COVERAGE_REPORT.md DATASET_DEPENDENCY_GROUPS.csv STRONG_BASELINE_REGISTER_V2.csv STRONG_BASELINE_PREDICTIONS.jsonl STRONG_BASELINE_RESULTS_P0.csv STRONG_BASELINE_RESULTS_P1.csv STRONG_BASELINE_RESULTS_P2.csv BASELINE_REPRODUCTION_STATUS_V2.csv BASELINE_RUNTIME_REPORT.md SOURCE_TYPE_STATISTICS.csv SOURCE_LEVEL_TECHNIQUE_SCORES.jsonl SOURCE_FUSION_RESULTS.csv SOURCE_FUSION_ABLATION.csv SOURCE_EVIDENCE_TRACES.jsonl SOURCE_FUSION_ERROR_ANALYSIS.md ATTACK_KNOWLEDGE_CONTROL_RESULTS.csv DESCRIPTION_COVERAGE_AUDIT.md TITLE_LEAKAGE_CONTROL.md COMMON_COVERAGE_203_RESULTS.csv RESAMPLING_STABILITY_RESULTS.csv GROUPED_VALIDATION_RESULTS.csv P0_P1_PAIRED_COMPARISON.csv P0_P2_VERSION_COMPARISON.csv GENERALIZATION_LIMITATIONS.md METHOD_HYPOTHESIS_V2.md METHOD_FORMAL_DEFINITION.md METHOD_DEV_RESULTS.csv METHOD_ABLATION_RESULTS.csv METHOD_ERROR_ANALYSIS.md METHOD_RESEARCH_DECISION.md R3_TECHNIQUE_STRONG_BASELINES_GENERALIZATION_RESULTS.md'''.split()
checks={'all_required_artifacts_present':all((R/n).is_file() and (R/n).stat().st_size>0 for n in required)}
freeze=json.loads((R/'manifests/P0_FREEZE.json').read_text());checks['all21_old_source_and_frozen_hashes_unchanged']=all(sha(x['source'])==sha(x['frozen_path'])==x['sha256'] for x in freeze)
refs=read(R/'datasets/p0_reference.jsonl');checks['P0_975_unique_ids_195_steps_385prompts']=len(refs)==len({r['sample_id'] for r in refs})==975 and len({(r['scenario_id'],r['step_id']) for r in refs})==195 and len({r['input_hash'] for r in refs})==385
stable=json.loads((R/'datasets/manifests/STABLE_CLEANED.json').read_text());checks['cleaned_data_checksums_match']=all(sha(R/'datasets'/name)==v['sha256'] for name,v in stable.items() if isinstance(v,dict) and 'sha256' in v)
checks['v2_cleaned_direct_label_ids_zero']=stable['cleaning_summary']['direct_ids_after']==0
allow=read(R/'datasets/manifests/ALLOWLISTED_MEMBERS.jsonl');checks['allowlist_1136_and_no_forbidden_steps']=len(allow)==1136 and all(not (r['simulation_id'].split('_')[0]=='1' and r['step_id'] in ['35','36','37']) for r in allow)
checks['all_protocol_reference_ids_and_ban_filter']=True
for p in [R/'datasets/p0_reference.jsonl',R/'datasets/p1_resampled/reference.jsonl',R/'datasets/p1_resampled/reference_fixed_variant.jsonl',R/'datasets/p2_v2/reference_sampled.jsonl',R/'datasets/p2_v2/reference_full.jsonl']:
 rr=read(p);checks['all_protocol_reference_ids_and_ban_filter'] &= len(rr)==len({r['sample_id'] for r in rr}) and not any(r['scenario_id']=='1' and str(r['step_id']).split('_')[0] in ['35','36','37'] for r in rr)
maxdelta=0;conditions=0;candidatevalid=True;missing=False;idmatch=True;refcache={};flatrows=0
# Recompute all metrics from stored Top10 and separate references, including step macro.
for receipt in sorted((R/'experiments').glob('*_receipt.json')):
 m=json.loads(receipt.read_text())
 if 'representation' not in m or (m.get('exit_code')!=0 and not m.get('completion_verified')):continue
 conditions+=1;rp=m.get('reference_path',str(R/'datasets/p0_reference.jsonl'));refcache.setdefault(rp,read(rp));rr=refcache[rp];universe=json.loads((R/'knowledge'/(m['knowledge_view']+'.json')).read_text());ps={}
 with Path(m['output']).open() as f:
  for line in f:
   pred=json.loads(line);idmatch &= pred['sample_id'] not in ps;ps[pred['sample_id']]=pred['predictions'];flatrows+=1
   candidatevalid &= len(pred['predictions'])==len(set(pred['predictions']))==10 and set(pred['predictions'])<=set(universe)
 if len(universe)==203:rr=[r for r in rr if {normalize_technique_id(x) for x in r['ground_truth']}<=set(universe)]
 idmatch &= set(ps)=={r['sample_id'] for r in refcache[rp]}
 records=[{'ground_truth':r['ground_truth'],'predictions':ps.get(r['sample_id'],[])} for r in rr];missing |= any(r['sample_id'] not in ps for r in rr)
 metrics=summarize(records,universe);filename='STRONG_BASELINE_RESULTS_'+('P0' if m['protocol']=='P0' else 'P1' if m['protocol'].startswith('P1') else 'P2')+'.csv'
 rows=list(csv.DictReader((R/filename).open()));row=next(x for x in rows if all(x[k]==m[k] for k in ['method','protocol','input_view','knowledge_view']))
 for k,v in metrics.items():maxdelta=max(maxdelta,abs(v-float(row[k])))
checks['all_condition_metrics_recompute_exactly']=maxdelta<1e-12;checks['all_prediction_ids_complete_unique']=idmatch and not missing;checks['all_top10_unique_valid_candidates']=candidatevalid
checks['flat_prediction_index_count']=sum(1 for _ in (R/'STRONG_BASELINE_PREDICTIONS.jsonl').open())==flatrows
checks['candidate_top3_score_reconstruction']=json.loads((R/'results/EXACT_EVIDENCE_VALIDATION.json').read_text())['max_score_reconstruction_error']<1e-12
# Confirm representation implementation regression agrees with old frozen rankings.
old=read(R/'frozen_p0/BASELINE_PREDICTIONS.jsonl');agree=True
for method,mode in [('BM25_K16_1','bm25'),('TFIDF_K16_1','word')]:
 ps={x['sample_id']:x['predictions'] for x in read(R/'experiments'/f'P0_{mode}_K2_DESCRIPTION_16_1_all.jsonl')}
 agree &= all(ps[x['sample_id']]==x['predictions'] for x in old if x['method']==method and x['input_view']=='strict')
checks['old_BM25_TFIDF_all975_rankings_reproduced']=agree
# Test metrics and source pooling logic without modifying old Python caches.
unit=subprocess.run([str(R/'venvs/CharacterNgramTFIDF/bin/python'),'-B',str(R/'frozen_p0/benchmark/test_metrics.py')],capture_output=True,text=True)
(R/'results/evaluator_v1_tests.log').write_text(unit.stdout+unit.stderr)
checks['metric_12_tests_pass']=unit.returncode==0 and 'Ran 12 tests' in unit.stderr
fusiontest=subprocess.run([str(R/'venvs/SourceWiseBM25/bin/python'),'-B',str(R/'method/test_source_fusion.py')],capture_output=True,text=True)
(R/'results/fusion_unit_tests.log').write_text(fusiontest.stdout+fusiontest.stderr);checks['fusion_logic_tests_pass']=fusiontest.returncode==0
for directory in ['baselines','method','datasets']:
 for p in (R/directory).glob('*.py'):
  if p.name.startswith('create_llm_prompt_resample'):continue
  py_compile.compile(str(p),doraise=True)
checks['all_project_code_compiles']=True
stability=list(csv.DictReader((R/'RESAMPLING_STABILITY_RESULTS.csv').open()));checks['deterministic_identical_input_top1_consistent']=all(r['identical_input_top1_agreement']=='N/A' or abs(float(r['identical_input_top1_agreement'])-1)<1e-12 for r in stability)
checks['no_incomplete_or_invalid_initial_runs_in_result_paths']=all('INVALID_UNCLEANED' not in str(json.loads(p.read_text()).get('output','')) for p in (R/'experiments').glob('*_receipt.json'))
result={'passed':all(checks.values()),'required_files':len(required),'conditions':conditions,'predictions':flatrows,'metric_recomputation_max_delta':maxdelta,'checks':checks,'qualifications':['P0 six fusion batch individual exitcode NOT_CAPTURED; completed outputs/hash verified','No independent generalization claim','Rank evidence is not independent gold','Source isolation is code/schema, not OS sandbox']}
(R/'results/DELIVERY_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if not result['passed']:raise SystemExit(1)
paths=[p for p in R.rglob('*') if p.is_file() and 'venvs' not in p.parts and '__pycache__' not in p.parts and p.name!='DELIVERY_SHA256SUMS.txt']
(R/'manifests/DELIVERY_SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in sorted(paths)))
