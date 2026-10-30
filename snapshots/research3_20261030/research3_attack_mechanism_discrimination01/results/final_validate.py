"""Integrity and reproducibility gate; zero model calls, no external state changes."""
import ast,csv,json,math,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def main()->None:
 required='CROSS_ENCODER_FORENSIC_AUDIT.md RERANKER_SCORING_VALIDATION.json CANDIDATE_SCORE_CONSISTENCY.csv CANDIDATE_RANK_TRANSITIONS.csv RERANKER_FAILURE_TAXONOMY.csv RERANKER_FAILURE_DIAGNOSIS.md DIAGNOSTIC_30_SELECTION_PROTOCOL.md DIAGNOSTIC_30_FROZEN_IDS.json DIAGNOSTIC_30_CASES.jsonl DIAGNOSTIC_30_DEPENDENCY_AUDIT.csv MECHANISM_IR_SCHEMA.json MECHANISM_LITERAL.jsonl MECHANISM_RELATIONS.jsonl MECHANISM_EXTRACTION_VALIDATION.md MECHANISM_SOURCE_TRACE.csv TECHNIQUE_MECHANISM_CARDS.jsonl KNOWLEDGE_VERSION_MANIFEST.json KNOWLEDGE_COVERAGE_AUDIT.md MECHANISM_CARD_SOURCE_AUDIT.csv MECHANISM_BASELINE_PREDICTIONS.jsonl MECHANISM_BASELINE_RESULTS.csv MECHANISM_INPUT_ABLATIONS.csv MECHANISM_KNOWLEDGE_ABLATIONS.csv MECHANISM_ERROR_ANALYSIS.md MECHANISM_BLIND_REVIEW_PACKETS.jsonl MECHANISM_REVIEW_GUIDELINES.md MECHANISM_HUMAN_REVIEW_STATUS.csv EXTERNAL_ATTACK_TECHNIQUE_DATASET_CANDIDATES.md EXTERNAL_REFERENCE_QUALIFICATION.csv EXTERNAL_DATASET_DECISION.md METHOD_FORMAL_PROBLEM.md METHOD_RESEARCH_DECISION.md R3_ATTACK_MECHANISM_DISCRIMINATION_RESULTS.md'.split()
 assert all((ROOT/n).is_file() and (ROOT/n).stat().st_size for n in required)
 assets=json.loads((ROOT/'manifests/INHERITED_ASSETS.json').read_text());assert all(sha256(Path(x['source']))==x['sha256'] for x in assets)
 external=json.loads((ROOT/'external_dataset/LOCAL_SOURCE_QUALIFICATION.json').read_text());assert all(sha256(Path(x['path']))==x['sha256'] for x in external['source_receipts'])
 auth=json.loads((ROOT/'manifests/AUTHORIZATION_SCOPE.json').read_text());assert auth['new_GPU_forward'] and auth['new_server_write'] and auth['new_data_upload'] and not auth['new_model_download'] and auth['new_LLM_budget']==0
 proposal=json.loads((ROOT/'manifests/PROPOSED_GPU_TRANSFER.json').read_text());assert not proposal['authorized'] and sum(x['bytes'] for x in proposal['files'])==9597914
 for x in proposal['files']:assert sha256(Path(x['path']))==x['sha256']
 main_receipt=json.loads((ROOT/'results/CPU_RUN_RECEIPT.json').read_text());assert main_receipt['predictor_source_sha256']==sha256(ROOT/'baselines/run_offline.py') and main_receipt['input_sha256']==sha256(ROOT/'frozen_inputs/PREDICTION_INPUTS.jsonl') and main_receipt['knowledge_sha256']==sha256(ROOT/'attack_knowledge/KNOWLEDGE_TEXTS.json')
 build=json.loads((ROOT/'manifests/INPUT_BUILD_RECEIPT.json').read_text());assert build['extractor_sha256']==sha256(ROOT/'mechanism_ir/extractor.py') and build['builder_sha256']==sha256(ROOT/'mechanism_ir/build_inputs.py')
 val=json.loads((ROOT/'results/MECHANISM_VALIDATION.json').read_text());assert val['test_status']=='PASS' and val['unit_tests']==12 and val['native_fields_verified']==34510 and val['native_relations_verified']==997
 ids=set(json.loads((BASELINES/'knowledge/K2_DESCRIPTION_16_1.json').read_text()));ref={x['sample_id']:x for x in load(BASELINES/'datasets/p0_reference.jsonl')};E=module(BENCHMARK/'evaluate_techniques.py','final_frozen_v1_evaluator');pred=load(ROOT/'MECHANISM_BASELINE_PREDICTIONS.jsonl')+load(ROOT/'experiments/KNOWLEDGE_CONTROL_PREDICTIONS.jsonl');groups={}
 for r in pred:
  assert len(r['predictions'])==len(set(r['predictions']))==10 and set(r['ranking_all216'])==ids and len(r['ranking_all216'])==216
  assert all(math.isfinite(v) for v in r['scores_top10']);groups.setdefault(r['method'],[]).append(r)
 saved={x['method']:x for x in csv.DictReader((ROOT/'MECHANISM_BASELINE_RESULTS.csv').open())};assert len(groups)==65 and len(saved)==81 and len(pred)==63375
 for method,rows in groups.items():
  assert len(rows)==975==len({r['sample_id'] for r in rows})
  m=E.summarize([{'ground_truth':ref[r['sample_id']]['ground_truth'],'predictions':r['predictions']} for r in rows],ids)
  for metric in ['mrr','top1_accuracy','top5_accuracy','top10_accuracy','recall_at_10','precision_at_10']:assert abs(float(saved[method][metric])-m[metric])<1e-12
 old=load(PREVIOUS/'RERANKER_REAL_PREDICTIONS.jsonl')
 for r in old:
  assert len(r['predictions'])==len(set(r['predictions']))==r['candidate_k'] and set(r['predictions'])<=ids
  scores=dict(zip(r['predictions'],r['raw_logits']));assert r['predictions']==sorted(r['original_candidates'],key=lambda t:(-scores[t],t))
 selection=json.loads((ROOT/'DIAGNOSTIC_30_FROZEN_IDS.json').read_text());assert len(set(selection['logical_step_keys']))==30 and len(selection['scene_counts'])==7
 packets=load(ROOT/'MECHANISM_BLIND_REVIEW_PACKETS.jsonl');assert len(packets)==30 and all(not any(k in r for k in ['sample_id','ground_truth','stratum','predictions']) and r['human_reference_status']=='PENDING' for r in packets)
 neural=list(csv.DictReader((ROOT/'experiments/NEURAL_CONDITION_STATUS.csv').open()));assert len(neural)==40 and sum(r['status']=='EXECUTED' and r['N']=='975' for r in neural)==16 and sum(r['status']=='OUTSIDE_AUTHORIZED_MAIN_SCOPE' and r['N']=='NA' for r in neural)==24
 new=load(ROOT/'results/gpu/NEW_EMBEDDING_PREDICTIONS.jsonl')+load(ROOT/'results/gpu/NEW_RERANKER_PREDICTIONS.jsonl');ng={}
 pools=json.loads((ROOT/'frozen_inputs/NEURAL_FIXED_CANDIDATES.json').read_text())
 for r in new:
  ranking=r['predictions'];scores=r.get('scores',r.get('raw_logits'));assert len(ranking)==len(set(ranking))==len(scores) and all(math.isfinite(v) for v in scores)
  byid=dict(zip(ranking,scores));assert ranking==sorted(ranking,key=lambda t:(-byid[t],t));assert set(ranking)==(ids if r['method'].startswith('GTE_EMBEDDING') else set(pools[r['sample_id']]))
  ng.setdefault(r['method'],[]).append(r)
 assert len(ng)==16 and len(new)==15600
 for method,rows in ng.items():
  assert len(rows)==975==len({r['sample_id'] for r in rows})
  m=E.summarize([{'ground_truth':ref[r['sample_id']]['ground_truth'],'predictions':r['predictions'][:10]} for r in rows],ids)
  for metric,value in m.items():assert abs(float(saved[method][metric])-value)<1e-12
 grant=json.loads((ROOT/'manifests/NEW_GPU_AUTHORIZATION.json').read_text());assert grant['authorized'] and grant['max_pair_evaluations']==156000 and grant['wall_seconds_limit']==7200
 run=json.loads((ROOT/'results/gpu/GPU_RUN_COMPLETE.json').read_text());assert run['status']=='ALL_AUTHORIZED_CONDITIONS_COMPLETE' and run['total_seconds']<7200 and run['CE_unique_pairs']<=156000 and not run['Gold_loaded']
 resource=json.loads((ROOT/'results/gpu/manifests/REMOTE_FINAL_RESOURCE_RECEIPT.json').read_text());assert resource['project_disk_allocated_bytes']<1000000000
 transfer=json.loads((ROOT/'results/gpu/manifests/TRANSFER_VERIFIED.json').read_text());assert set(transfer['hashes'].values())=={x['sha256'] for x in proposal['files']}
 launch=json.loads((ROOT/'results/gpu/manifests/RUN_STARTED.json').read_text());assert launch['source_sha256']==sha256(ROOT/'experiments/run_gpu_if_authorized.py')
 sanity=json.loads((ROOT/'results/gpu/SCORING_SANITY.json').read_text());assert sanity['num_labels']==1 and sanity['eval_mode'] and all(sanity['relevant_gt_irrelevant']) and sanity['max_batch_single_delta']==0
 env=json.loads((ROOT/'results/gpu/manifests/ACTUAL_ENVIRONMENT_AND_DOC_TOKENS.json').read_text());assert len(env['knowledge_actual_tokens'])==864 and max(x['tokens'] for x in env['knowledge_actual_tokens'])<=1024
 tokens=json.loads((ROOT/'results/gpu/ACTUAL_MODEL_INPUT_TOKENS.json').read_text());assert len(tokens)==3900
 native={x['sample_id']:x['views'] for x in load(ROOT/'frozen_inputs/PREDICTION_INPUTS.jsonl')}
 import hashlib
 for t in tokens:assert t['text_sha256']==hashlib.sha256(native[t['sample_id']][t['view']].encode()).hexdigest() and max(t['actual_token_counts'].values())<=2048
 statistics=list(csv.DictReader((ROOT/'results/ALL_CPU_GPU_CONTRASTS.csv').open()));assert len(statistics)==292 and all(0<=float(x['signflip_p'])<=float(x['Holm_p_all292'])<=1 for x in statistics)
 assert len(list(csv.DictReader((ROOT/'diagnostic_30/NEURAL_CASE_ANALYSIS.csv').open())))==480
 channel=json.loads((ROOT/'results/SCORER_CHANNEL_AUDIT.json').read_text());assert all(not x['relation_added_tokens_in_doc_vocab'] and not x['normalized_action_tokens_in_doc_vocab'] for x in channel['checks'])
 n=0
 for p in ROOT.rglob('*.py'):
  if 'venvs' in p.parts or '__pycache__' in p.parts:continue
  ast.parse(p.read_text(),filename=str(p));n+=1
 report=(ROOT/'R3_ATTACK_MECHANISM_DISCRIMINATION_RESULTS.md').read_text();assert len(re.findall(r'^### \d+\.',report,re.M))==36
 for name in ['analysis-report.md','stats-appendix.md','figure-catalog.md','provenance.json']:assert (ROOT/'reports/analysis-output'/name).exists()
 result={'status':'PASS','required_core_files':len(required),'inherited_assets_unchanged':len(assets),'additional_external_metadata_sources_unchanged':len(external['source_receipts']),'real_CPU_prediction_conditions':65,'main_prediction_rows':47775,'posthoc_prediction_rows':15600,'total_prediction_rows':len(pred)+len(new),'total_conditions':81,'full_query_denominator_each_condition':975,'all_saved_metrics_independently_recomputed':True,'frozen_thirty_logical_steps':30,'diagnostic_scenarios':7,'source_fields_checked':34510,'native_relations_checked':997,'safety_unit_tests':12,'actual_GTE_new_representation_conditions':16,'actual_GTE_new_representation_predictions':15600,'GPU_experiments':1,'GPU_CE_unique_candidate_pairs':run['CE_unique_pairs'],'GPU_CE_batches':run['CE_batches'],'GPU_embedding_batches':run['embedding_forward_batches'],'GPU_wall_seconds':run['total_seconds'],'new_LLM_calls':0,'server_writes_or_uploads':'EXPLICITLY_AUTHORIZED_4_FROZEN_ARTIFACTS_PLUS_CONTROL_MANIFESTS','new_model_downloads':0,'actual_GTE_Token_lengths':'MEASURED3900VIEWS_WITH2TOKENIZERS_PLUS864DOC_COUNTS','BM25_new_relation_action_label_channel':'INACTIVE_NOT_A_VALID_SEMANTIC_NEGATIVE_TEST','human_review_status':'PENDING','external_test':'NOT_READY','report_questions_answered':36,'source_files_syntax_checked':n,'limitations':['only16mainneuralconditions authorized;24extensionsNA','4public batch/single pairs are not full CAM stability proof','no independent mechanism semantic reference','same byte/Token cap does not equal identical actual Token length','P0 exposure and script dependence','card source content and lexical confounds']}
 save('results/FINAL_VALIDATION.json',result)
 files=[]
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file() or p.is_symlink() or any(k in p.parts for k in ['venvs','__pycache__','.git']):continue
  if p in [ROOT/'manifests/DELIVERY_SHA256.json',ROOT/'results/final_validation.log']:continue
  files.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha256(p)})
 save('manifests/DELIVERY_SHA256.json',files);print(json.dumps(result,indent=2));print('Delivery files:',len(files))
if __name__=='__main__':main()
