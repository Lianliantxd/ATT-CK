"""Frozen V1 evaluator and grouped descriptive summaries. No training or inference."""
import collections,csv,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
E=mod(BENCH/'evaluate_techniques.py','domain_frozen_v1_evaluator')
def main():
 refs={r['sample_id']:r for r in load(ROOT/'data/P0_REFERENCE.jsonl')};inputs={r['sample_id']:r for r in load(ROOT/'data/P0_INPUTS.jsonl')};ids=sorted(json.loads((ROOT/'data/CANDIDATE_TECHNIQUE_IDS.json').read_text()));folds={f['fold_id']:f for f in json.loads((ROOT/'GROUPED_TRAIN_VALIDATION_SPLITS.json').read_text())['folds']};allrows=[]
 for directory in ['runs_frozen','runs_B2','runs_heads']:
  for p in sorted((ROOT/'results'/directory).glob('*_predictions.jsonl')):
   for r in load(p):r['evaluation_partition']=r['evaluation_partition'].upper();allrows.append(r)
 groups=collections.defaultdict(list)
 for r in allrows:
  assert r['predictions']==r['ranking_all216'][:10] and len(r['ranking_all216'])==len(set(r['ranking_all216']))==216 and set(r['ranking_all216'])==set(ids);groups[r['method'],str(r['seed']),r['augmentation'],r['fold_id'],r['evaluation_partition']].append(r)
 def evaluate(rows,gold_override=None):
  return E.summarize([{'ground_truth':gold_override[r['sample_id']] if gold_override else refs[r['sample_id']]['gold_technique_ids'],'predictions':r['predictions']} for r in rows],ids)
 results=[];strata=[];details=[];tokens={(x['sample_id'],x['view']):x for x in json.loads((OLD/'results/gpu/ACTUAL_MODEL_INPUT_TOKENS.json').read_text())}
 for (method,seed,aug,fold,partition),rs in groups.items():
  f=folds[fold];seen=set(f['train_seen_techniques']);m=evaluate(rs);row={'method':method,'seed':seed,'augmentation':aug,'fold_id':fold,'evaluation_partition':partition,'scenario':f['heldout_scenario'] if partition=='HELDOUT' else f['validation_scenario'] if partition=='VALIDATION' or partition=='INNER_VALIDATION' else 'TRAIN','candidate_count':216,'training_seen_classes':len(seen),'evaluation_qualification':'GROUPED_DEVELOPMENT_VALIDATION',**m};results.append(row)
  if partition!='HELDOUT':continue
  assert {x['sample_id'] for x in rs}==set(f['heldout_sample_ids'])
  for category,pred in [('SINGLE_LABEL',lambda g:len(g)==1),('MULTILABEL',lambda g:len(g)>1),('ALL_GOLD_SEEN',lambda g:g<=seen),('ALL_GOLD_UNSEEN',lambda g:not(g&seen)),('MIXED_SEEN_UNSEEN',lambda g:bool(g&seen) and not(g<=seen))]:
   rr=[r for r in rs if pred(set(refs[r['sample_id']]['gold_technique_ids']))]
   if rr:strata.append({**{k:row[k] for k in ['method','seed','augmentation','fold_id']},'stratum':category,**evaluate(rr)})
  for category,labelset in [('SEEN_GOLD_SUBSET',seen),('UNSEEN_GOLD_SUBSET',set(ids)-seen)]:
   gold={r['sample_id']:sorted(set(refs[r['sample_id']]['gold_technique_ids'])&labelset) for r in rs};rr=[r for r in rs if gold[r['sample_id']]]
   if rr:strata.append({**{k:row[k] for k in ['method','seed','augmentation','fold_id']},'stratum':category,'subset_qualification':'same full216 prediction, only Gold subset restricted; mixed-label queries appear in both subsets',**evaluate(rr,gold)})
  for category,low,high in [('TOKENS_LE256',0,256),('TOKENS257_512',256,512),('TOKENS_GT512',512,99999)]:
   rr=[r for r in rs if low<tokens[r['sample_id'],'RAW']['actual_token_counts']['embedding']<=high]
   if rr:strata.append({**{k:row[k] for k in ['method','seed','augmentation','fold_id']},'stratum':category,**evaluate(rr)})
  for r in rs:
   g=set(refs[r['sample_id']]['gold_technique_ids']);rank=min((i+1 for i,t in enumerate(r['predictions']) if t in g),default=0);details.append({'method':method,'seed':seed,'augmentation':aug,'fold_id':fold,'sample_id':r['sample_id'],'scenario':f['heldout_scenario'],'logical_step_id':refs[r['sample_id']]['logical_step_id'],'top1':int(r['predictions'][0] in g),'top10':int(rank>0),'mrr':1/rank if rank else 0,'gold_seen_count':len(g&seen),'gold_unseen_count':len(g-seen),'best_gold_rank_all216':min(i+1 for i,t in enumerate(r['ranking_all216']) if t in g),'candidate_hit20':int(bool(set(r['ranking_all216'][:20])&g)),'label_count':len(g),'mechanism_observability':'UNKNOWN_NOT_INFERRED_FROM_STEP_LABELS'})
 csvout('GROUPED_VALIDATION_RESULTS.csv',results);csvout('SEEN_UNSEEN_TECHNIQUE_RESULTS.csv',strata);csvout('results/PER_SAMPLE_RESULTS.csv',details)
 summaries=[]
 for method,seed,aug in sorted({(r['method'],str(r['seed']),r['augmentation']) for r in allrows}):
  rs=[r for r in allrows if r['method']==method and str(r['seed'])==seed and r['augmentation']==aug and r['evaluation_partition']=='HELDOUT'];assert len(rs)==975 and len({x['sample_id'] for x in rs})==975
  fm=[x for x in results if x['method']==method and str(x['seed'])==seed and x['augmentation']==aug and x['evaluation_partition']=='HELDOUT'];summaries.append({'method':method,'seed':seed,'augmentation':aug,'outer_folds':7,'queries':975,'logical_steps':195,'mrr_equal_scene_mean':float(np.mean([x['mrr'] for x in fm])),'mrr_scene_SD':float(np.std([x['mrr'] for x in fm],ddof=1)),'top10_equal_scene_mean':float(np.mean([x['top10_accuracy'] for x in fm])),**evaluate(rs)})
 csvout('results/OVERALL_RESULTS_BY_SEED.csv',summaries)
 average=[]
 for method,aug in sorted({(x['method'],x['augmentation']) for x in summaries}):
  rs=[x for x in summaries if x['method']==method and x['augmentation']==aug];out={'method':method,'augmentation':aug,'seeds':len(rs),'queries_each_seed':975,'folds_each_seed':7}
  for metric in ['mrr','top1_accuracy','top5_accuracy','top10_accuracy','precision_at_5','recall_at_5','micro_f1_at_5','macro_f1_at_5_all_candidates','mrr_equal_scene_mean','top10_equal_scene_mean']:
   a=[x[metric] for x in rs];out[metric]=float(np.mean(a));out[metric+'_seed_SD']=float(np.std(a,ddof=1)) if len(a)>1 else 'NA_FROZEN_NO_STOCHASTIC_TRAINING'
  average.append(out)
 csvout('results/OVERALL_RESULTS.csv',average)
 names={'SUPERVISED_LINEAR_RESULTS.csv':['B2'],'FROZEN_GTE_LINEAR_RESULTS.csv':['B3'],'TRAINABLE_PROJECTION_RESULTS.csv':['B4'],'STANDARD_CONTRASTIVE_RESULTS.csv':['B5'],'HARD_NEGATIVE_TRAINING_RESULTS.csv':['B6','B7','B8','B9','B9_CONST']}
 for filename,methods in names.items():
  rr=[x for x in results if x['method'] in methods]
  csvout(filename,rr or [{'method':x,'status':'BLOCKED_MISSING_AUTHENTIC_GTE_FEATURES_PENDING_NEW_FORWARD_AUTHORIZATION','n_records':'NA','mrr':'NA','top10_accuracy':'NA'} for x in methods])
 # Exactly four primary questions; no292 tests or pseudo-independent seeds.
 primary=[]
 for aug in ['ONE_VIEW_PER_STEP','MULTI_VIEW_AUGMENTATION']:
  for hypothesis,a,b in [('H1','B4','B1'),('H2','B5','B4'),('H3','B7','B6'),('H4','B9','B8')]:
   for scene in sorted({x['scenario'] for x in results if x['evaluation_partition']=='HELDOUT'}):
    ar=[x for x in results if x['method']==a and x['augmentation']==aug and x['scenario']==scene and x['evaluation_partition']=='HELDOUT'];br=[x for x in results if x['method']==b and (x['augmentation']==aug or b=='B1') and x['scenario']==scene and x['evaluation_partition']=='HELDOUT']
    primary.append({'hypothesis':hypothesis,'method':a,'baseline':b,'augmentation':aug,'scenario':scene,'status':'EXECUTED' if ar and br else 'NA_RESOURCE_BLOCKED','mrr_delta_seed_mean':float(np.mean([x['mrr'] for x in ar])-np.mean([x['mrr'] for x in br])) if ar and br else 'NA','top10_delta_seed_mean':float(np.mean([x['top10_accuracy'] for x in ar])-np.mean([x['top10_accuracy'] for x in br])) if ar and br else 'NA','confirmatory_p_value':'NOT_COMPUTED7EXPOSED_SCENARIOS_DEPENDENT_SEEDS'})
 csvout('results/FOUR_PRIMARY_HYPOTHESES.csv',primary)
 with (ROOT/'TRAINING_BASELINE_PREDICTIONS.jsonl').open('w') as f:
  for r in allrows:
   if r['evaluation_partition']=='HELDOUT':f.write(json.dumps(r)+'\n')
 dump('results/EVALUATION_RECEIPT.json',{'status':'ACTUAL_SAVED_PREDICTIONS_EVALUATED','methods_executed':sorted({r['method'] for r in allrows}),'heldout_prediction_rows':len(details),'fold_seed_mode_partition_conditions':len(groups),'all_queries_each_seed':975,'frozen_evaluator_sha256':sha(BENCH/'evaluate_techniques.py'),'source_sha256':sha(Path(__file__)),'metrics_from_saved_predictions_only':True,'Gold_never_sent_to_GPU_server':True,'scenarios_independent_confirmatory_tests':False})
 print(json.dumps(average,indent=2))
if __name__=='__main__':main()
