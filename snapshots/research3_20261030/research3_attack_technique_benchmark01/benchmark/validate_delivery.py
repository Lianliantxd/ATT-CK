import csv,json,hashlib,py_compile,sys
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[1];checks={}
required='''OFFICIAL_DATA_ASSET_AUDIT.md OFFICIAL_DATA_MANIFEST.json OFFICIAL_SAMPLE_LABEL_COUNTS.csv DATA_ACQUISITION_LOG.md STEP_LEVEL_DATASET.jsonl LABEL_NORMALIZATION_RULES.md ATTACK_KNOWLEDGE_VERSION.json DATASET_SPLITS.json ATTACK_TECHNIQUE_EVALUATION_PROTOCOL_V1.md METRIC_SPECIFICATION.json evaluate_techniques.py METRIC_UNIT_TEST_REPORT.md OFFICIAL_METRIC_RECALCULATION.csv OFFICIAL_VS_LOCAL_EVALUATOR_CHECK.md OFFICIAL_PREDICTION_COUNTS.csv STRONG_BASELINE_REGISTER.csv BASELINE_PREDICTIONS.jsonl BASELINE_RESULTS_P0.csv BASELINE_RESULTS_P1.csv BASELINE_RUNTIME_REPORT.md BASELINE_ERROR_ANALYSIS.md LABEL_LEAKAGE_AUDIT.md INPUT_VIEW_MANIFEST.json METADATA_ONLY_DIAGNOSTIC.csv EXECUTION_GROUP_LEAKAGE_AUDIT.md GENERALIZATION_PROTOCOL.md TREC_REPRODUCTION_STATUS.md APTREC_REPRODUCTION_STATUS.md KNOWHOW_TECHNIQUE_ADAPTATION_REPORT.md METHOD_HYPOTHESIS.md BASELINE_FAILURE_TAXONOMY.md METHOD_DEV_EXPERIMENTS.csv METHOD_ABLATION_RESULTS.csv METHOD_RESEARCH_DECISION.md PAPER_REPORTED_RESULTS.csv R3_ATTACK_TECHNIQUE_BENCHMARK_RESULTS.md'''.split()
checks['all_required_artifacts_present']=all((R/n).is_file() and (R/n).stat().st_size for n in required)
qs=[json.loads(x) for x in (R/'STEP_LEVEL_DATASET.jsonl').read_text().splitlines()]
checks['975_unique_ids']=len(qs)==len({q['sample_id'] for q in qs})==975
checks['195_steps_five_replicas']=set(Counter((q['scenario_id'],q['step_id']) for q in qs).values())=={5}
checks['restricted_steps_absent']=not any(q['scenario_id']=='1' and q['step_id'].split('_')[0] in {'35','36','37'} for q in qs)
inputs=[json.loads(x) for x in (R/'datasets/prediction_view_strict.jsonl').read_text().splitlines()]
checks['prediction_schema_text_only']=all(set(q)=={'sample_id','text'} for q in inputs)
checks['views_equal']= (R/'datasets/prediction_view_strict.jsonl').read_bytes()==(R/'datasets/prediction_view_official.jsonl').read_bytes()
preds=[json.loads(x) for x in (R/'BASELINE_PREDICTIONS.jsonl').read_text().splitlines()]
checks['15_conditions_14625_predictions']=len(preds)==14625
universe=set(json.loads((R/'datasets/official_knowledge_documents.json').read_text()))
checks['all_top10_valid_unique_candidates']=all(len(x['predictions'])==len(set(x['predictions']))==10 and set(x['predictions'])<=universe for x in preds)
checks['official_evaluator_success']=json.loads((R/'results/OFFICIAL_RUN.json').read_text())['exit_code']==0
checks['all_model_evaluations_agree']=all(x['max_abs_delta']<1e-12 for x in json.loads((R/'results/evaluator_deltas.json').read_text()))
checks['all_prediction_processes_succeeded']=all(json.loads(p.read_text())['exit_code']==0 for p in (R/'experiments').glob('*receipt.json'))
checks['unit_tests_pass']='Ran 12 tests' in (R/'results/unit_tests.log').read_text() and '\nOK\n' in (R/'results/unit_tests.log').read_text()
checks['source_git_blobs_match']=all(x['git_blob_matches'] for x in json.loads((R/'manifests/GIT_BLOB_VERIFICATION.json').read_text()))
leak=list(csv.DictReader((R/'datasets/manifests/input_leakage.csv').open()))
checks['at_most_10_records_per_host_source']=max(int(x['max_lines_per_source']) for x in leak)<=10
checks['dev_five_conditions_60_records']=len(list(csv.DictReader((R/'METHOD_ABLATION_RESULTS.csv').open())))==5
for p in [R/'evaluate_techniques.py',*(R/'benchmark').glob('*.py'),*(R/'baselines').glob('*.py'),*(R/'method').glob('*.py')]:py_compile.compile(str(p),doraise=True)
checks['all_project_python_compiles']=True
# Recompute all stored result metrics from saved predictions and separately held references.
sys.path.insert(0,str(R));from evaluate_techniques import summarize
reference={q['sample_id']:q['official_technique_labels'] for q in qs}
rows=list(csv.DictReader((R/'BASELINE_RESULTS_P0.csv').open()));maximum=0
for row in rows:
 group=[x for x in preds if x['method']==row['method'] and x['input_view']==row['input_view']]
 result=summarize([{'ground_truth':reference[x['sample_id']],'predictions':x['predictions']} for x in group],universe)
 for k,v in result.items():maximum=max(maximum,abs(v-float(row[k])))
checks['saved_predictions_reproduce_all_metrics']=maximum<1e-12
result={'passed':all(checks.values()),'checks':checks,'metric_recomputation_max_delta':maximum,'required_artifact_count':len(required)}
(R/'results/DELIVERY_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if not result['passed']:raise SystemExit(1)
# Integrity index excludes itself, caches and portable environments.
files=[p for p in R.rglob('*') if p.is_file() and 'venvs' not in p.parts and '__pycache__' not in p.parts and p.name!='DELIVERY_SHA256SUMS.txt']
(R/'manifests/DELIVERY_SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(R))+'\n' for p in sorted(files)))
