"""Final integrity gate for the completed authorized frozen-feature/CPU-head stage.

No training, forward passes, server access, or repeated full numerical/negative audits.
Verifies immutable evidence bindings, actual asset counts and selected metric recomputation.
"""
import ast,csv,hashlib,json,math,os,re,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
WEIGHT_SHA='3e85899d5728cb7de79781c0c3acfb91ccef9f875f1f7e0b3c9f3dd4b6a724ba'
REVISION='e7f32e3c00f91d699e8c43b53106206bcc72bb22'
SPLIT_SHA='879bac94d85a5106a36345b9d9ce3f85f0b383978d8a6b914bb2cec1374bd96d'
PROTOCOL_SHA='d38359359b6d2db8f2be223847efb420b6afc0b8a862673c78900b9f618a4d3a'
REQUIRED='TRAINING_DATA_QUALIFICATION.md LABEL_COUNT_RECONCILIATION.md MULTILABEL_DISTRIBUTION.csv SCENARIO_DEPENDENCY_GROUPS.csv GROUPED_TRAIN_VALIDATION_SPLITS.json TRAINING_DATA_MANIFEST.json SUPERVISED_LINEAR_RESULTS.csv FROZEN_GTE_LINEAR_RESULTS.csv TRAINABLE_PROJECTION_RESULTS.csv TRAINING_BASELINE_PREDICTIONS.jsonl STANDARD_CONTRASTIVE_PROTOCOL.md STANDARD_CONTRASTIVE_RESULTS.csv CONTRASTIVE_TRAINING_LOGS.csv CONTRASTIVE_CHECKPOINT_MANIFEST.json HARD_NEGATIVE_MINING_PROTOCOL.md NEGATIVE_SAMPLE_QUALIFICATION.csv HARD_NEGATIVE_TRAINING_RESULTS.csv FALSE_NEGATIVE_RISK_AUDIT.md HARD_NEGATIVE_ABLATION.csv TRAINING_ENVIRONMENT_MANIFEST.json MODEL_TRAINING_RECEIPTS.jsonl GPU_TRAINING_AUTHORIZATION_REQUEST.md TRAINING_RESOURCE_REPORT.md GROUPED_VALIDATION_RESULTS.csv SEEN_UNSEEN_TECHNIQUE_RESULTS.csv EXTERNAL_DATASET_QUALIFICATION.md EXTERNAL_GENERALIZATION_RESULTS.csv DOMAIN_ADAPTATION_ERROR_ANALYSIS.md DOMAIN_ADAPTATION_ABLATION.md METHOD_RESEARCH_DECISION.md R3_DOMAIN_ADAPTIVE_CONTRASTIVE_LEARNING_RESULTS.md'.split()
HASH_CACHE={}
def sha(p):
 p=Path(p);s=p.stat();key=(str(p),s.st_size,s.st_mtime_ns)
 if key not in HASH_CACHE:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  HASH_CACHE[key]=h.hexdigest()
 return HASH_CACHE[key]
def check(ok,message):
 if not ok:raise AssertionError(message)
def readj(p):return json.loads((ROOT/p).read_text())
def rows(p):
 with (ROOT/p).open() as f:
  for line in f:
   if line.strip():yield json.loads(line)
def csvrows(p):
 with (ROOT/p).open(newline='') as f:return list(csv.DictReader(f))
def close(a,b,message):check(math.isfinite(float(a)) and abs(float(a)-float(b))<1e-11,message)
def regular_files():
 for directory,dirs,files in os.walk(ROOT,followlinks=False):
  dirs[:]=sorted(d for d in dirs if d not in ['venvs','__pycache__','.git'] and not (Path(directory)/d).is_symlink())
  for name in sorted(files):
   p=Path(directory)/name
   if p.is_file() and not p.is_symlink():yield p

def main():
 check(len(REQUIRED)==31 and all((ROOT/n).is_file() and (ROOT/n).stat().st_size for n in REQUIRED),'31 root deliverables')
 inherited=readj('inherited/PRIOR_IMMUTABLE_ASSETS.json');check(len(inherited)==1029,'1029 inherited assets')
 for x in inherited:check(sha(Path(x['source']))==x['sha256'],'old asset changed: '+x['source'])
 data=readj('data/manifests/GROUPED_DATA_VALIDATION.json');check(data['status']=='PASS' and data['parent_multilabel_queries']==285 and data['query_count']==975,'grouped data audit')
 reference={r['sample_id']:r for r in rows('data/P0_REFERENCE.jsonl')};inputs={r['sample_id']:r for r in rows('data/P0_INPUTS.jsonl')}
 check(len(reference)==975 and len(inputs)==975,'P0 queries');check(len({r['logical_step_id'] for r in reference.values()})==195,'P0 logical steps')
 check(sum(len(set(r['gold_technique_ids']))>1 for r in reference.values())==285,'parent multilabel285');check(sum(len(set(r['raw_ground_truth']))>1 for r in reference.values())==295,'raw multilabel295')
 check(all('gold_technique_ids' not in r for r in inputs.values()),'Gold in input view')
 check(sha(ROOT/'GROUPED_TRAIN_VALIDATION_SPLITS.json')==sha(ROOT/'splits/GROUPED_TRAIN_VALIDATION_SPLITS.json')==SPLIT_SHA,'frozen split hashes');check(sha(ROOT/'manifests/TRAINING_PROTOCOL.json')==PROTOCOL_SHA,'original registered protocol hash')
 protocol=readj('manifests/TRAINING_PROTOCOL.json');check(protocol['split_file_sha256']==SPLIT_SHA,'protocol split binding')
 folds={f['fold_id']:f for f in readj('GROUPED_TRAIN_VALIDATION_SPLITS.json')['folds']};ids=readj('data/CANDIDATE_TECHNIQUE_IDS.json');universe=set(ids);check(len(ids)==len(universe)==216,'216 candidates')
 for f in folds.values():
  train=list(rows(f['paths']['train']));held=list(rows(f['paths']['heldout_inputs']));valid=list(rows(f['paths']['validation_inputs']));sets=[{r['logical_step_id'] for r in rr} for rr in [train,held,valid]]
  check(not(sets[0]&sets[1] or sets[0]&sets[2] or sets[1]&sets[2]),'fold leakage');check(all('gold_technique_ids' not in r for r in held+valid),'fold reference isolation')
 auth=readj('manifests/FEATURE_EXTRACTION_AUTHORIZATION.json');proposal=readj('manifests/FEATURE_EXTRACTION_PROPOSAL.json')
 check(auth['authorized'] is True and proposal['authorized'] is False,'current grant/historical proposal distinction')
 for k,value in {'trainable_parameters':0,'Gold_upload':False,'GPU':0,'GPU_memory_fraction':.15,'CPU_threads':2,'batch':8,'max_wall_seconds':900,'max_tokens':1000000,'max_disk_bytes':200000000,'new_LLM_calls':0,'new_packages':False,'new_model_downloads':False,'GPU_parameter_training_authorized':False}.items():check(auth[k]==value,'authorization scope '+k)
 check(auth['revision']==REVISION and auth['server']=='tianxiaodan@10.109.119.118','fixed model/server scope')
 for x in auth['upload_files']:check(sha(Path(x['path']))==x['sha256'] and Path(x['path']).stat().st_size==x['bytes'],'authorized extractor hash')
 feature_path=ROOT/'embeddings/FROZEN_GTE_FEATURES.npz';feature_sha=sha(feature_path);feature_receipt=readj('embeddings/FEATURE_EXTRACTION_RECEIPT.json');feature_audit=readj('embeddings/FEATURE_QUALIFICATION_VALIDATION.json');capture=readj('embeddings/server_manifests/RESOURCE_CHECK_STDOUT_CAPTURE.json')
 check(feature_receipt['status']=='COMPLETE_FROZEN_FEATURES_ONLY' and feature_receipt['model_revision']==REVISION and feature_receipt['weight_sha256']==WEIGHT_SHA,'fixed frozen GTE receipt')
 check(feature_receipt['feature_sha256']==feature_sha==feature_audit['features_sha256'],'features hash binding');check(feature_receipt['source_sha256']==sha(ROOT/'embeddings/extract_frozen_gte.py'),'feature source binding')
 check(feature_receipt['trainable_parameters']==0 and feature_receipt['Gold_loaded'] is False and feature_receipt['new_model_downloads']==0,'frozen feature-only run')
 check(feature_receipt['actual_tokens']==sum(feature_receipt['token_counts'])<=auth['max_tokens'],'actual token budget');check(feature_receipt['seconds']<900 and abs(feature_receipt['seconds']-13.209157302044332)<1e-6,'actual forward wall budget')
 check(capture['disk_bytes']==3653632<=auth['max_disk_bytes'],'actual server disk');check(capture['weight_sha256_after']==WEIGHT_SHA and capture['no_Gold_upload'] and capture['no_GPU_training'],'after-forward model/scope')
 check('NOT a downloaded remote file' in capture['capture_kind'],'resource evidence must be stdout capture');check(capture['additional_manifest_scp_status'].startswith('BLOCKED_AUTOMATIC_REVIEW'),'extra scp not successful')
 check(set(capture['already_downloaded'])=={'FROZEN_GTE_FEATURES.npz','FEATURE_EXTRACTION_RECEIPT.json'},'only core artifacts claimed copied')
 knowledge=readj('data/KNOWLEDGE_K2.json')
 with np.load(feature_path,allow_pickle=False) as z:
  check(z['log_vectors'].shape==(975,768) and z['knowledge_vectors'].shape==(216,768),'actual feature shapes')
  check(len(set(z['sample_ids'].tolist()))==975 and set(z['sample_ids'].tolist())==set(reference),'feature query IDs')
  check(z['technique_ids'].tolist()==ids,'feature candidate order')
  for array in ['log_vectors','knowledge_vectors']:check(np.isfinite(z[array]).all() and np.max(np.abs(np.linalg.norm(z[array],axis=1)-1))<1e-5,'finite unit-normalized '+array)
  for sid,h in zip(z['sample_ids'].tolist(),z['input_hashes'].tolist()):check(h==hashlib.sha256(inputs[sid]['input_log_text'].encode()).hexdigest()==inputs[sid]['input_hash'],'feature input text hash')
  for tid,h in zip(z['technique_ids'].tolist(),z['knowledge_hashes'].tolist()):check(h==hashlib.sha256(knowledge[tid].encode()).hexdigest(),'feature knowledge hash')
 check(feature_audit['status']=='PASS' and feature_audit['B1_recomputed_from_same_features_as_trainable_heads'] and feature_audit['queries_with_changed_B1_top10_order']==49,'current B1 feature qualification')
 heads=readj('results/TRAINED_HEADS_INDEPENDENT_AUDIT.json');negative=readj('results/NEGATIVE_MINING_AUDIT.json');evaluation=readj('results/FINAL_EVALUATION_INDEPENDENT_AUDIT.json');complete=readj('results/HEADS_MATRIX_COMPLETE.json')
 check(heads['status']=='PASS' and heads['new_head_configurations_audited']==336 and heads['B2_original_configurations_preserved']==42 and heads['total_updates_including_B2']==45360,'trained head independent audit')
 expected={'feature_sha256':feature_sha,'protocol_sha256':PROTOCOL_SHA,'trainer_sha256':sha(ROOT/'contrastive/train_heads.py'),'math_source_sha256':sha(ROOT/'contrastive/numpy_models.py')}
 for k,value in expected.items():check(heads['source_hashes'][k]==value and negative[k]==value,'current head/negative source '+k)
 check(negative['status']=='PASS' and negative['total_negative_rows']==930240 and negative['negative_files']==210 and negative['head_configurations']==336,'negative audit totals')
 check(negative['split_sha256']==SPLIT_SHA and negative['audit_source_sha256']==sha(ROOT/'hard_negatives/audit_mined_negatives.py'),'negative audit source binding')
 check(evaluation['status']=='PASS_WITH_DOCUMENTED_LIMITATIONS' and evaluation['evaluation_groups']==1106 and evaluation['heldout_groups']==392 and evaluation['heldout_rows']==54600 and evaluation['stratum_groups_independently_recomputed']==3472 and evaluation['primary_hypothesis_scene_mode_rows_recomputed']==56,'independent final metrics audit')
 check(evaluation['split_sha256']==SPLIT_SHA and evaluation['audit_source_sha256']==sha(ROOT/'evaluation/validate_final_metrics.py') and evaluation['main_evaluator_sha256']==sha(ROOT/'evaluation/evaluate_saved.py'),'evaluation source bindings')
 check(complete['configurations']==336 and complete['total_optimizer_updates']==40320 and complete['new_GPU_training'] is False,'matrix completion')
 receipts=list(rows('MODEL_TRAINING_RECEIPTS.jsonl'));check(len(receipts)==378,'378 actual training receipts');by_method=Counter(r['method'] for r in receipts);check(set(by_method)=={'B2','B3','B4','B5','B6','B7','B8','B9','B9_CONST'} and set(by_method.values())=={42},'full registered training grid')
 audited={(x['method'],x['fold_id'],int(x['seed']),x['augmentation']):x for x in heads['configurations']};updates=0;checkpoint_paths=set()
 for r in receipts:
  b2=r['method']=='B2';cp=ROOT/(r['checkpoint_path'] if b2 else f"checkpoints/heads/{r['method']}_{r['fold_id']}_seed{r['seed']}_{r['augmentation']}.npz")
  check(cp not in checkpoint_paths and sha(cp)==r['checkpoint_sha256'],'checkpoint changed/duplicate');checkpoint_paths.add(cp);check(r['epochs']==120,'registered epochs');updates+=r['optimizer_updates'] if b2 else r['updates']
  actual=readj(r['receipt_file']);check(all(actual[k]==v for k,v in r.items() if k!='receipt_file'),'aggregate receipt differs from original')
  check(r['source_sha256']==sha(ROOT/('baselines/train_tfidf_linear.py' if b2 else 'contrastive/train_heads.py')),'current training source differs')
  if b2:check(r['W_changed'] and r['reload_max_abs_diff']==0 and r['optimizer_updates']==120,'B2 preserved checkpoint proof')
  else:
   a=audited[r['method'],r['fold_id'],int(r['seed']),r['augmentation']];check(a['checkpoint_sha256']==sha(cp) and a['receipt_sha256']==sha(ROOT/r['receipt_file']),'independent checkpoint/receipt evidence changed')
   check(r['train_parameters_updated'] and r['GTE_backbone_trainable'] is False and r['checkpoint_reload_score_max_abs_delta']==0 and r['feature_source_sha256']==feature_sha,'actual CPU head training')
 check(updates==45360 and len(checkpoint_paths)==378,'45360 updates and378 checkpoints')
 for c in negative['configurations']:
  for f in c['files']:check(sha(ROOT/f['path'])==f['sha256'] and (ROOT/f['path']).stat().st_size==f['bytes'],'audited negative asset changed')
 for p in evaluation['prediction_sources']:check(sha(ROOT/p['path'])==p['sha256'] and (ROOT/p['path']).stat().st_size==p['bytes'],'audited prediction changed')
 # Basic full-export rank/count checks plus bounded metric spot checks; do not rerun full audits.
 groups=defaultdict(list);count=0;methods=Counter()
 for r in rows('TRAINING_BASELINE_PREDICTIONS.jsonl'):
  check(r['evaluation_partition']=='HELDOUT','export partition');ranking=r['ranking_all216'];check(len(ranking)==len(set(ranking))==216 and set(ranking)==universe and r['predictions']==ranking[:10],'export rank integrity')
  k=(r['method'],str(r['seed']),r['augmentation'],r['fold_id']);groups[k].append(r['sample_id']);count+=1;methods[r['method']]+=1
 check(count==54600 and len(groups)==392,'actual final export counts')
 for k,ss in groups.items():check(len(ss)==len(set(ss)) and set(ss)==set(folds[k[3]]['heldout_sample_ids']),'final export fold IDs')
 saved={(r['method'],r['seed'],r['augmentation'],r['fold_id']):r for r in csvrows('GROUPED_VALIDATION_RESULTS.csv') if r['evaluation_partition']=='HELDOUT'};check(set(saved)==set(groups),'saved heldout group coverage')
 selected={k for k in groups if k[0] in ['B0','B1'] or (k[0] in ['B2','B3','B5','B7','B9'] and k[1]=='17' and k[2]=='ONE_VIEW_PER_STEP' and k[3]=='fold_heldout_1')};stats=defaultdict(lambda:[0,0.0,0])
 for r in rows('TRAINING_BASELINE_PREDICTIONS.jsonl'):
  k=(r['method'],str(r['seed']),r['augmentation'],r['fold_id'])
  if k in selected:
   g=set(reference[r['sample_id']]['gold_technique_ids']);rank=next((i+1 for i,t in enumerate(r['predictions']) if t in g),0);s=stats[k];s[0]+=1;s[1]+=1/rank if rank else 0;s[2]+=int(rank>0)
 for k,(n,mrr,top10) in stats.items():close(saved[k]['mrr'],mrr/n,'spot MRR');close(saved[k]['top10_accuracy'],top10/n,'spot Top10')
 check(len(csvrows('results/OVERALL_RESULTS.csv'))==20 and len(csvrows('results/OVERALL_RESULTS_BY_SEED.csv'))==56,'complete summary table counts')
 hypotheses=csvrows('results/FOUR_PRIMARY_HYPOTHESES.csv');check(len(hypotheses)==56 and all(x['status']=='EXECUTED' and x['confirmatory_p_value'].startswith('NOT_COMPUTED') for x in hypotheses),'four primary hypotheses reporting')
 ext=readj('data/external_candidates/QUALIFICATION_DECISION.json');check(ext['external_evaluation_examples']==ext['external_training_examples_admitted']==ext['new_log_bytes_downloaded']==0,'external qualification')
 files=list(regular_files());disk_bytes=sum(p.stat().st_size for p in files);check(disk_bytes<=2000000000,'local nonvenv disk exceeds2GB');syntax=0
 for p in files:
  if p.suffix=='.py':ast.parse(p.read_text());syntax+=1
 previous=readj('results/FINAL_VALIDATION.json');check(str(previous.get('gradient_tests','')).startswith('3PASS'),'pre-existing three-gradient-test pass receipt')
 report=(ROOT/'R3_DOMAIN_ADAPTIVE_CONTRASTIVE_LEARNING_RESULTS.md').read_text();readme=(ROOT/'README.md').read_text();check(len(re.findall(r'^### \d+\.',report,re.M))==45,'45 final report questions')
 check('主状态 **HARD_NEGATIVE_ADAPTATION_EVALUATED**' in report and '最终主状态HARD_NEGATIVE_ADAPTATION_EVALUATED' in readme,'current final state');check('LoRA B10未授权未执行' in report and 'B3–B9已执行' in readme,'current execution/LoRA distinction')
 for n in ['analysis-report.md','stats-appendix.md','figure-catalog.md','provenance.json']:check((ROOT/'reports/analysis-output'/n).is_file(),'analysis artifact '+n)
 check(len(list((ROOT/'reports/analysis-output/figures').glob('*.pdf')))>=4,'four actual final scientific figures')
 state={'status':'PASS_FOR_COMPLETED_AUTHORIZED_SCOPE','main_research_status':'HARD_NEGATIVE_ADAPTATION_EVALUATED','required_root_deliverables':31,'old_assets_unchanged':1029,'P0_queries':975,'logical_steps':195,'parent_multilabel_queries':285,'parent_multilabel_steps':57,'subtechnique_multilabel_queries':295,'candidate_count':216,'LOSO_folds':7,'registered_split_sha256':SPLIT_SHA,'registered_protocol_sha256':PROTOCOL_SHA,'trained_B2_configurations_preserved':42,'trained_new_GTE_head_configurations':336,'total_trained_configurations':378,'checkpoint_files_verified':378,'optimizer_updates':45360,'heldout_predictions':54600,'heldout_method_seed_fold_conditions':392,'evaluation_conditions':1106,'independent_stratum_conditions':3472,'primary_hypothesis_scene_mode_rows':56,'independent_audits_bound_to_current_sources':True,'complete_numeric_and_negative_audits_rerun':False,'final_metric_spotcheck_conditions':len(stats),'negative_rows_previously_independently_verified':930240,'real_GTE_projection_or_contrastive_training':True,'GTE_backbone_parameters_updated':False,'new_GPU_frozen_feature_extractions':1,'new_GPU_parameter_training':0,'new_Gold_upload':0,'new_LLM_calls':0,'feature_sha256':feature_sha,'fixed_model_weight_sha256':WEIGHT_SHA,'actual_feature_extraction_seconds':feature_receipt['seconds'],'actual_feature_tokens':feature_receipt['actual_tokens'],'server_project_disk_bytes_from_stdout_capture':capture['disk_bytes'],'server_resource_evidence':'SUCCESSFUL_STDOUT_CAPTURE_NOT_DOWNLOADED_REMOTE_FILE','additional_server_manifest_scp':'FAILED_AUTO_REVIEW_CONNECTION_OR_TIMEOUT_NO_COPY_CLAIM','core_features_and_receipt_downloaded':True,'local_nonvenv_regular_file_bytes':disk_bytes,'local_disk_budget_bytes':2000000000,'external_test_examples':0,'python_source_syntax_checked':syntax,'report_questions':45,'gradient_tests':'3PASS_PREVIOUSLY_EXECUTED_NOT_REPEATED','LoRA_B10':'NOT_AUTHORIZED_NOT_EXECUTED','limitations':['7 exposed development scenarios; exact original script identity UNKNOWN','Seeds/five sampling views are not independent attacks','Unseen target degradation and weak-negative uncertainty','No qualified independent external test','Extra remote manifest copies failed; resource metadata is a stdout capture','Historical protocol pending scope preserved; current separate frozen-feature grant is authoritative']}
 (ROOT/'results/FINAL_VALIDATION.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
 excluded={ROOT/'manifests/DELIVERY_SHA256.json',ROOT/'results/final_validation.log'};delivery=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(regular_files()) if p not in excluded]
 (ROOT/'manifests/DELIVERY_SHA256.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(state,ensure_ascii=False,indent=2));print('DELIVERY_FILES',len(delivery))
if __name__=='__main__':main()
