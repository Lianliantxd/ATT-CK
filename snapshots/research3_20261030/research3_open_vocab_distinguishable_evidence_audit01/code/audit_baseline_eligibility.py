"""Post semantic-seal protocol/qualification audit,no model outcome expansion."""
import hashlib,json,csv
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];B=R.parent
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for v in iter(lambda:f.read(1048576),b''):h.update(v)
 return h.hexdigest()
def dump(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def load(p):return json.loads(p.read_text())
def main():
 seal=load(R/'audit/SECOND_PASS_SEAL.json');assert all(sha(R/x['path'])==x['sha256'] for x in seal['files'])
 cases=[json.loads(s) for s in (R/'review/CASE_EVIDENCE_AUDIT.jsonl').read_text().splitlines()]
 competitors=[json.loads(s) for s in (R/'review/COMPETING_TECHNIQUE_AUDIT.jsonl').read_text().splitlines()]
 # All named primary assets are checked,not silently assumed to exist. Full
 # delivery manifests are read as version metadata; prediction bytes hashed
 # without opening new outcome values for ineligible queries.
 roots=['research3_open_vocab_technique_generalization01','research3_open_vocab_failure_mechanism_diagnosis01',
        'research3_open_vocab_384_case_blind_review01','research3_method_hypothesis_gate01']
 assets={};expected={}
 def add(p,role):
  p=Path(p).resolve();k=str(p)
  if k not in assets:assets[k]={'path':k,'role':role,'exists':p.is_file(),'sha256':sha(p) if p.is_file() else None,'bytes':p.stat().st_size if p.is_file() else None}
  return p
 for name in roots:
  root=B/name;mp=root/('audit/DELIVERY_SHA256.json' if name=='research3_method_hypothesis_gate01' else 'manifests/DELIVERY_SHA256.json')
  add(mp,'legacy version manifest only')
  for x in load(mp):
   p=add(root/x['path'],'historical frozen asset;hash only unless named as semantic input or protocol metadata')
   expected[str(p)]=x['sha256']
 P=B/'research3_domain_adaptive_contrastive_learning01/data';S=B/'research3_technique_strong_baselines_generalization02'
 for p in [P/'P0_INPUTS.jsonl',P/'KNOWLEDGE_K2.json',S/'datasets/p0_native.jsonl',S/'knowledge/K2_DESCRIPTION_16_1.json',
           S/'experiments/P0_bm25_K2_DESCRIPTION_16_1_native.jsonl',S/'experiments/P0_char_K2_DESCRIPTION_16_1_native.jsonl',
           S/'STRONG_BASELINE_RESULTS_P0.csv']:
  add(p,'historical baseline input/version hash;no new outcome evaluation')
 qi={x['sample_id']:x for x in map(json.loads,(P/'P0_INPUTS.jsonl').read_text().splitlines())}
 ql={x['sample_id']:x for x in map(json.loads,(S/'datasets/p0_native.jsonl').read_text().splitlines())}
 kg,kl=load(P/'KNOWLEDGE_K2.json'),load(S/'knowledge/K2_DESCRIPTION_16_1.json')
 knowledge_same=kg==kl
 per=[]
 for q,c in zip(cases,competitors):
  sid=q['sample_id'];same=qi[sid]['input_log_text']==ql[sid]['text'];assert qi[sid]['input_hash']==q['input_view_hash']
  per.append({'sample_id':sid,'logical_step_id':q['logical_step_id'],'primary_diagnosis':q['primary_diagnosis'],
   'residual_error_classification':'REFERENCE_INSUFFICIENT','secondary_protocol_classification':'CROSS_PROTOCOL_NOT_COMPARABLE' if not same or not knowledge_same else 'MATCHED_PROTOCOL_NOT_SEMANTICALLY_QUALIFIED',
   'gte_Unseen_miss_as_frozen_selection':True,'gte_target_semantic_correctness':'NOT_AVAILABLE',
   'Gold_vs_entire_selected_subset_distinguishable_AI_only':q['distinguishable_AI_only'],
   'qualified_independent_reference_available':False,'qualified_residual_ranking_error':'NOT_AVAILABLE',
   'strong_lexical_correct_ranking_qualified':'NOT_AVAILABLE','C4_rank_change_in_this_task':'NOT_EVALUATED_NO_QUALIFIED_CASE',
   'baseline_outcome_rows_newly_read_for_this_case':False,
   'exact_native_lexical_query_text_match':same,'full216_knowledge_text_match':knowledge_same,
   'current_query_input_hash':q['input_view_hash'],'lexical_query_sha256':hashlib.sha256(ql[sid]['text'].encode()).hexdigest(),
   'candidate_definitions_without_body':c['missing_body_candidate_ids'],
   'reason':'没有合格独立参考，不能把AI配对结果补成可验证排序错误；整组候选区分未获资格，因此不扩大读取该例C4/词法结果。历史全216词法知识/输入另有实际字节差异。',
   'historical_outcome_comparison_completed':False})
 with (R/'review/BASELINE_RESIDUAL_ERROR_AUDIT.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(per[0]));w.writeheader()
  for x in per:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,list) else v for k,v in x.items()})
 for x in assets.values():
  x['expected_sha256']=expected.get(x['path']);x['version_status']='MATCH' if x['expected_sha256']==x['sha256'] else 'MISMATCH' if x['expected_sha256'] else 'CURRENT_HASH_PINNED'
 drift=[x for x in assets.values() if x['version_status']=='MISMATCH']
 dump('audit/OLD_ASSET_HASH_SNAPSHOT.json',{'created_utc':datetime.now(timezone.utc).isoformat(),
   'timing':'core semantic inputs also pinned beforefirstpass;broader version inventory created aftersemanticseals;not a start-of-entire-task OS snapshot',
   'assets':list(assets.values()),'legacy_version_differences':drift})
 dump('audit/BASELINE_QUALIFICATION_SUMMARY.json',{'post_semantic_seal_verified':True,'cases_recorded':len(per),
  'qualified_reference_supported_cases_documented':0,'actual_qualified_residual_ranking_errors':'NOT_AVAILABLE',
  'actual_qualified_baseline_recoveries':'NOT_AVAILABLE','new_case_outcome_comparisons_completed':0,
  'outcome_comparison_not_performed_reason':'no full-subset distinguishable qualified-reference cases;do not invent or read broader outcomes to fill unknown',
  'native_lexical_query_text_matches_within384':sum(x['exact_native_lexical_query_text_match'] for x in per),
  'native_lexical_cross_protocol_queries':sum(x['secondary_protocol_classification']=='CROSS_PROTOCOL_NOT_COMPARABLE' for x in per),
  'knowledge_documents_identical_out_of216':sum(kg[k]==kl[k] for k in kg),'candidate_ID_set_equal':set(kg)==set(kl),
  'saved_baseline_files_exist_and_hashed':True,'legacy_hash_difference_count':len(drift),
  'source_qualification':'already exposed development,no independent test,no new model or metric computation'})
 print(json.dumps({'assets_checked':len(assets),'legacy_hash_differences':len(drift),'cross_protocol_queries':sum(x['secondary_protocol_classification']=='CROSS_PROTOCOL_NOT_COMPARABLE' for x in per),
  'baseline_outcome_comparisons':0,'qualified_residual_count':'NOT_AVAILABLE'},ensure_ascii=False))
if __name__=='__main__':main()
