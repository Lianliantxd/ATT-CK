"""Posterior descriptive summaries; no new scoring method or parameter choice."""
import collections,csv,json,statistics,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def read(n):
 with (R/n).open() as f:return list(csv.DictReader(f))
def yes(v):return str(v) in ['True','1']
def quantiles(values):
 values=sorted(values);return {'min':min(values),'q25':values[int((len(values)-1)*.25)],'median':statistics.median(values),'q75':values[int((len(values)-1)*.75)],'max':max(values)}
def main():
 q=read('QUERY_DIAGNOSTICS.csv');g=read('UNSEEN_GOLD_TECHNIQUE_DIAGNOSTICS.csv');lost=read('GTE_HIT_C4_LOST_DIAGNOSTICS.csv');base=[x for x in q if x['seed']=='17' and x['view_id']=='ONE_VIEW_PER_STEP'];bg=[x for x in g if x['seed']=='17' and x['view_id']=='ONE_VIEW_PER_STEP'];bl=[x for x in lost if x['seed']=='17' and x['view_id']=='ONE_VIEW_PER_STEP']
 refs={x['sample_id']:x for x in jl(D/'data/P0_REFERENCE.jsonl')};inputs={x['sample_id']:x for x in jl(D/'data/P0_INPUTS.jsonl')};knowledge=json.loads((D/'data/KNOWLEDGE_K2.json').read_text());groups=collections.defaultdict(list);mapping=[]
 for x in base:
  sid=x['sample_id'];r=refs[sid];raw={t.split('.')[0] for t in r['raw_ground_truth']};expected=set(r['gold_technique_ids']);valid=raw==expected
  mapping.append({'sample_id':sid,'logical_step_id':x['logical_step_id'],'input_hash':x['input_hash'],'input_utf8_bytes':x['input_utf8_bytes'],'input_view':x['input_view'],'raw_ids':'|'.join(r['raw_ground_truth']),'mapped_parent_ids':'|'.join(sorted(raw)),'frozen_gold_ids':'|'.join(sorted(expected)),'parent_mapping_exact':valid,'all_gold_candidates_exist':all(t in knowledge for t in expected),'full_log_equivalence':'NOT_VERIFIED','label_unit':'AUTHOR_STEP_NOT_EVENT','semantic_alignment':'UNRESOLVED_WITHOUT_INDEPENDENT_EVENT_EVIDENCE'})
  groups[x['input_hash']].append(x)
 collision=[]
 for h,rs in groups.items():
  steps={x['logical_step_id'] for x in rs};labels={x['gold_ids'] for x in rs}
  if len(steps)>1:
   collision.append({'input_hash':h,'query_count':len(rs),'logical_step_count':len(steps),'scenario_count':len({x['scenario_id'] for x in rs}),'logical_steps':'|'.join(sorted(steps)),'distinct_parent_gold_sets':len(labels),'gold_sets':json.dumps(sorted(labels)),'different_step_labels_for_identical_current_view':len(labels)>1,'interpretation':'INPUT_VIEW_AMBIGUITY_CANDIDATE_NOT_PROVEN_ANNOTATION_ERROR'})
 csvout('INPUT_LABEL_MAPPING_AUDIT.csv',mapping);csvout('IDENTICAL_VIEW_DIFFERENT_STEP_AUDIT.csv',collision)
 fold=[]
 for f in sorted({x['fold_id'] for x in base}):
  rs=[x for x in base if x['fold_id']==f and int(x['unseen_gold_count'])];miss=[x for x in rs if not yes(x['gte_unseen_hit10'])]
  fold.append({'fold_id':f,'unseen_query_count':len(rs),'gte_miss':len(miss),'within_unseen_order_gt10':sum(int(x['best_unseen_internal_order_rank'])>10 for x in miss),'cross_group_block_only_candidate':sum(int(x['best_unseen_internal_order_rank'])<=10 for x in miss),'gte_hit_c4_lost':sum(yes(x['D2']) for x in rs),'c4_mixed_seen_hit_unseen_miss':sum(yes(x['D4']) for x in rs)})
 csvout('results/PRIMARY_DIAGNOSIS_BY_SCENE.csv',fold)
 desc=[]
 for label,pred in [('ALL_UNSEEN_GOLD',lambda x:True),('GTE_MISS_GOLD',lambda x:int(x['gte_rank'])>10),('GTE_HIT_C4_LOST',lambda x:yes(x['D2']))]:
  rs=[x for x in bg if pred(x)]
  for field in ['gte_rank','unseen_internal_order_rank','gte_raw_score','gte_gold_minus_rank10_score','description_bytes','input_bytes']:
   desc.append({'stratum':label,'unit':'query_gold_pair','n':len(rs),'field':field,**quantiles([float(x[field]) for x in rs])})
 csvout('results/SCORE_MARGIN_DESCRIPTIVES.csv',desc)
 cf=[]
 for view in ['ONE_VIEW_PER_STEP','MULTI_VIEW_AUGMENTATION']:
  for seed in ['17','42','73']:
   rs=[x for x in lost if x['seed']==seed and x['view_id']==view]
   cf.append({'seed':seed,'view_id':view,'lost_gold_pairs':len(rs),'remove_supervision_restored':sum(int(x['remove_supervision_rank'])<=10 for x in rs),'remove_bias_restored':sum(int(x['remove_bias_rank'])<=10 for x in rs),'restore_gte_restored':sum(int(x['restore_gte_rank'])<=10 for x in rs),'loss_primary_seen_score_boost':sum(x['primary_attribution']=='SEEN_SCORE_BOOST' for x in rs),'lost_cases_with_gamma_zero':sum(float(x['gamma'])==0 for x in rs),'lost_cases_default_parameter':sum('DEFAULT' in x['parameter_source'] for x in rs),'gte_exact_ties':sum(int(x['gte_exact_score_tie_size'])>1 for x in rs),'c4_exact_ties':sum(int(x['c4_exact_score_tie_size'])>1 for x in rs),'not_formal_model_results':True})
 csvout('COUNTERFACTUAL_COMPONENT_DIAGNOSIS.csv',cf)
 steps=collections.defaultdict(list)
 for x in base:
  if int(x['unseen_gold_count']):steps[x['logical_step_id']].append(x)
 summary={'primary_seed_for_case_listing':17,'primary_view':'ONE_VIEW_PER_STEP','unseen_query_gold_pairs_per_seed':len(bg),'unseen_target_logical_steps':len(steps),'steps_all_five_views_within_unseen_order_gt10':sum(all(int(x['best_unseen_internal_order_rank'])>10 for x in v) for v in steps.values()),'steps_any_view_within_unseen_order_gt10':sum(any(int(x['best_unseen_internal_order_rank'])>10 for x in v) for v in steps.values()),'unseen_gold_pairs_order_gt10':sum(int(x['unseen_internal_order_rank'])>10 for x in bg),'gte_missed_unseen_gold_pairs':sum(int(x['gte_rank'])>10 for x in bg),'parent_id_mapping_mismatches':sum(not x['parent_mapping_exact'] for x in mapping),'missing_candidate_gold_ids':sum(not x['all_gold_candidates_exist'] for x in mapping),'identical_view_multi_step_groups':len(collision),'identical_view_multi_step_different_labels_groups':sum(x['different_step_labels_for_identical_current_view'] for x in collision),'affected_distinct_steps':len({s for x in collision if x['different_step_labels_for_identical_current_view'] for s in x['logical_steps'].split('|')}),'input_bytes_distribution':quantiles([int(x['input_utf8_bytes']) for x in base]),'gold_description_bytes_distribution':quantiles([int(x['description_bytes']) for x in bg]),'knowledge_descriptions_exactly1000bytes':sum(len(t.encode())==1000 for t in knowledge.values()),'input_quality_semantic_cause':'UNRESOLVED; no full log or event evidence audited','new_parameters_or_model_inference':0,'source_sha256':sha(Path(__file__))}
 dump('results/EVIDENCE_AND_MAPPING_SUMMARY.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
