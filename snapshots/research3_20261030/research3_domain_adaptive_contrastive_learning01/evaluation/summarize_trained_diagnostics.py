"""Small descriptive family: four hypotheses, train gaps, subset and seed effects."""
import csv,collections,sys,json
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def read(n):return list(csv.DictReader((ROOT/n).open()))
def main():
 overall=read('results/OVERALL_RESULTS.csv');o={(r['method'],r['augmentation']):r for r in overall};h=read('results/FOUR_PRIMARY_HYPOTHESES.csv');primary=[]
 for mode in ['ONE_VIEW_PER_STEP','MULTI_VIEW_AUGMENTATION']:
  for hyp,a,b in [('H1','B4','B1'),('H2','B5','B4'),('H3','B7','B6'),('H4','B9','B8')]:
   rr=[r for r in h if r['augmentation']==mode and r['hypothesis']==hyp];d=np.array([float(r['mrr_delta_seed_mean']) for r in rr]);base=o[b,'SHARED' if b=='B1' else mode];method=o[a,mode]
   primary.append({'hypothesis':hyp,'method':a,'baseline':b,'augmentation':mode,'scenes':7,'MRR_delta_query_weighted':float(method['mrr'])-float(base['mrr']),'MRR_delta_equal_scene_mean':float(d.mean()),'MRR_delta_scene_SD':float(d.std(ddof=1)),'MRR_delta_scene_min':float(d.min()),'MRR_delta_scene_max':float(d.max()),'positive_scenes':int(sum(d>1e-12)),'negative_scenes':int(sum(d< -1e-12)),'tied_scenes':int(sum(abs(d)<=1e-12)),'Top10_delta_query_weighted':float(method['top10_accuracy'])-float(base['top10_accuracy']),'confidence_interval':'NOT_ESTIMATED7EXPOSED_DEPENDENT_SCENARIOS','confirmatory_p':'NOT_COMPUTED'})
 csvout('results/FOUR_PRIMARY_DESCRIPTIVE_SUMMARY.csv',primary)
 grouped=read('GROUPED_VALIDATION_RESULTS.csv');g={(r['method'],r['seed'],r['augmentation'],r['fold_id'],r['evaluation_partition']):r for r in grouped};gaps=[]
 for r in grouped:
  if r['evaluation_partition']!='TRAIN_DIAGNOSTIC_R0':continue
  key=r['method'],r['seed'],r['augmentation'],r['fold_id'];held=g[*key,'HELDOUT'];valid=g[*key,'INNER_VALIDATION'];gaps.append({'method':r['method'],'seed':r['seed'],'augmentation':r['augmentation'],'fold_id':r['fold_id'],'train_mrr':r['mrr'],'validation_mrr':valid['mrr'],'heldout_mrr':held['mrr'],'train_minus_heldout_mrr':float(r['mrr'])-float(held['mrr']),'train_top10':r['top10_accuracy'],'heldout_top10':held['top10_accuracy'],'scope':'train r0 / heldout5 correlated samples; descriptive gap, not causal proof of script memory'})
 for r in read('results/B2_TRAIN_GENERALIZATION_GAP.csv'):gaps.append(r)
 csvout('results/ALL_TRAIN_GENERALIZATION_GAPS.csv',gaps)
 byseed=read('results/OVERALL_RESULTS_BY_SEED.csv');seed_index={(r['method'],r['seed'],r['augmentation']):r for r in byseed};diag=[]
 for mode in ['ONE_VIEW_PER_STEP','MULTI_VIEW_AUGMENTATION']:
  for a,b in [('B8','B7'),('B9','B7'),('B9','B8'),('B9','B9_CONST'),('B5','B3')]:
   for seed in ['17','42','73']:
    x,y=seed_index[a,seed,mode],seed_index[b,seed,mode];diag.append({'method':a,'baseline':b,'seed':seed,'augmentation':mode,'mrr_delta':float(x['mrr'])-float(y['mrr']),'top10_delta':float(x['top10_accuracy'])-float(y['top10_accuracy']),'qualification':'diagnostic registered contrasts; seed not independent attack'})
 csvout('results/REGISTERED_DIAGNOSTIC_DELTAS.csv',diag)
 # Numerical baseline re-extraction differences are kept separate from training gains.
 E=mod(BENCH/'evaluate_techniques.py','domain_b1_reextraction_evaluator');refs={r['sample_id']:r for r in load(ROOT/'data/P0_REFERENCE.jsonl')};ids=json.loads((ROOT/'data/CANDIDATE_TECHNIQUE_IDS.json').read_text());old=load(ROOT/'inherited/CPU_ONLY_B1_PREDICTIONS.jsonl');new=load(ROOT/'results/runs_frozen/B1_predictions.jsonl');om={r['sample_id']:r for r in old};nm={r['sample_id']:r for r in new}
 scores={}
 for name,rs in [('old',old),('current_same_feature_baseline',new)]:scores[name]=E.summarize([{'ground_truth':refs[r['sample_id']]['gold_technique_ids'],'predictions':r['predictions']} for r in rs],ids)
 dump('results/B1_REEXTRACTION_DIFFERENCE.json',{'metrics':scores,'changed_top10_order_queries':sum(om[s]['predictions']!=nm[s]['predictions'] for s in om),'changed_top10_membership_queries':sum(set(om[s]['predictions'])!=set(nm[s]['predictions']) for s in om),'causal_status':'different FP16 batching is a plausible numerical explanation, not separately isolated','no_Gold_selection_of_B1_version':True,'reason_for_current_B1':'same authentic input feature matrix used by every trainable GTE head'})
 print('four hypotheses and numerical-baseline/gap diagnostics saved')
if __name__=='__main__':main()
