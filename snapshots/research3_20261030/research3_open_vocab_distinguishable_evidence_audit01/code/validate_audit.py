"""Independent structural/source/qualification checks,not semantic adjudication."""
import ast,csv,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R.parent
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def load(n):return json.loads((R/n).read_text())
def lines(n):return [json.loads(s) for s in (R/n).read_text().splitlines() if s.strip()]
def csvrows(n):
 with (R/n).open(newline='') as f:return list(csv.DictReader(f))
def main():
 checks=[];xref=[];refcount=0
 def check(n,b):checks.append({'check':n,'passed':bool(b)})
 frozen=load('inputs/FROZEN_CASE_MANIFEST.json')['cases'];inputs=lines('inputs/FIRST_PASS_INPUTS.jsonl')
 first=lines('review/FIRST_PASS_CASE_EVIDENCE.jsonl');q=lines('review/CASE_EVIDENCE_AUDIT.jsonl');comp=lines('review/COMPETING_TECHNIQUE_AUDIT.jsonl')
 packets=lines('inputs/SHUFFLED_COMPETITOR_PACKETS.jsonl');facts={f['fact_id']:f for f in lines('inputs/VISIBLE_FACT_REGISTRY.jsonl')}
 pair=lines('review/GOLD_COMPETITOR_PAIR_AUDIT.jsonl');counts=load('results/QUERY_AGGREGATE_COUNTS.json');cat=load('review/COMPETITOR_DEFINITION_AUDIT.json')
 gold=load('review/GOLD_CONDITION_REGISTRY.json');corp=json.loads((B/'research3_domain_adaptive_contrastive_learning01/data/KNOWLEDGE_K2.json').read_text())
 ids=[x['sample_id'] for x in q];expected=[x['sample_id'] for x in frozen];missing=sorted(set(expected)-set(ids));dups=[k for k,v in Counter(ids).items() if v>1]
 check('384exact unique output order',len(q)==len(set(ids))==len(frozen)==384 and ids==expected and not missing and not dups)
 check('all independent phase file seals unchanged',all(sha(R/e['path'])==e['sha256'] for n in ['audit/FIRST_PASS_SEAL.json','audit/SECOND_PASS_SEAL.json'] for e in load(n)['files']))
 check('phase ordering verified by timestamps/hash pointers',load('audit/FIRST_PASS_SEAL.json')['created_utc']<=load('audit/CANDIDATE_PACKAGING_RECEIPT.json')['created_utc']<=load('audit/SECOND_PASS_SEAL.json')['created_utc'] and
  load('audit/CANDIDATE_PACKAGING_RECEIPT.json')['first_pass_seal_sha256']==sha(R/'audit/FIRST_PASS_SEAL.json'))
 v1root=R/'audit/phase1_v1_superseded';v1=json.loads((v1root/'FIRST_PASS_SEAL.json').read_text())
 check('pre-candidate superseded wording version preserved',all(sha(v1root/Path(e['path']).name)==e['sha256'] for e in v1['files']))
 oldfirst=[json.loads(s) for s in (v1root/'FIRST_PASS_CASE_EVIDENCE.jsonl').read_text().splitlines()]
 check('v1-v2 did not change literal evidence or target judgments',all(x['gold_audits']==y['gold_audits'] and x['visible_facts']==y['visible_facts'] for x,y in zip(oldfirst,first)))
 check('all125candidate and54Gold definitions unchanged',all(d['frozen_description']==corp[t] and d['description_sha256']==hashlib.sha256(d['frozen_description'].encode()).hexdigest() for t,d in cat.items()) and
       all(d['frozen_description']==corp[t] for t,d in gold.items()))
 check('candidate scope limited,not all216',len(cat)==125 and len(set(cat)|set(gold))==145 and all(not x['all_216_reviewed'] for x in q))
 enums={'DIRECTLY_SUPPORTED','PARTIALLY_SUPPORTED','EXPLICITLY_CONTRADICTED','NOT_ESTABLISHED','NOT_OBSERVABLE_IN_CURRENT_VIEW','NOT_EVALUABLE'}
 source_enums={'NATIVE_LOG_RECORD','RECORDED_RELATION','DERIVED_PATTERN','SOURCE_METADATA','PUBLIC_TECHNIQUE_DESCRIPTION','OTHER_DOCUMENTED_SOURCE','NO_SUPPORTING_SOURCE'}
 pair_enums={'DISTINGUISHABLE_SUPPORT_FOR_GOLD','DISTINGUISHABLE_SUPPORT_FOR_COMPETITOR','BOTH_COMPATIBLE_NOT_DISTINGUISHABLE','NEITHER_SUFFICIENTLY_SUPPORTED','INSUFFICIENT_INPUT','NOT_EVALUABLE'}
 def refs(owner,z):
  nonlocal refcount
  for key in ['supporting_fact_ids','contradicting_fact_ids','context_fact_ids','gold_relevant_fact_ids','competitor_relevant_fact_ids','shared_fact_ids','relevant_fact_ids']:
   for fid in z.get(key,[]):
    refcount+=1
    ok=fid in facts and facts[fid]['sample_id']==owner
    check('ref:'+owner+':'+fid,ok)
    if not ok:xref.append({'sample_id':owner,'fact_id':fid})
 for src,f,a,c,p in zip(inputs,first,q,comp,packets):
  sid=a['sample_id'];own=set(src['visible_fact_ids']);rawlines=src['frozen_input_text'].splitlines()
  check(sid+':allphases ordered and scoped',sid==src['sample_id']==f['sample_id']==c['sample_id']==p['sample_id'] and f['first_pass_complete'] and a['audit_complete'] and c['second_pass_audit_complete'])
  for k in ['logical_step_id','scenario_id','execution_id','view_id','fold_id','input_view','input_view_hash','gold_technique_ids']:
   check(sid+':source_metadata:'+k,src[k]==a[k])
  check(sid+':text hash/coverage',hashlib.sha256(src['frozen_input_text'].encode()).hexdigest()==a['input_view_hash'] and a['visible_scope']['visible_record_count']==len(rawlines) and a['visible_scope']['omitted_record_count'] is None)
  check(sid+':nonindependent notGold',a['blinding_status']==c['blinding_status']=='INDEPENDENT_BLIND_REVIEW_NOT_AVAILABLE' and a['review_status']=='NONINDEPENDENT_AI_EVIDENCE_AUDIT_NOT_GOLD' and a['human_review_required'])
  for vf in a['visible_facts']:
   x=facts[vf['fact_id']]
   check(vf['fact_id']+':literal owner and locator nature',x['sample_id']==sid and x['text']==vf['text']==rawlines[x['line_number']-1] and vf['fact_id_kind']=='DERIVED_SOURCE_LOCATOR_NOT_NATIVE_EVENT_ID')
   if '[**]' in vf['text'] or '"rule":' in vf['text']:check(vf['fact_id']+':derived source tagged',vf['source_type']=='DERIVED_PATTERN')
  check(sid+':Gold target condition coverage',set(g['technique_id'] for g in a['gold_audits'])==set(src['gold_technique_ids']) and all(g['condition_ids'] for g in a['gold_audits']))
  for z in a['gold_conditions']:
   refs(sid,z);check(z['condition_id']+':enum and source fields',z['evidence_status'] in enums and set(z['supporting_source_type'])<=source_enums and z['reasoning'] and z['scope_limitations'])
   check(z['condition_id']+':binding states present',all(z[k] for k in ['subject_binding_status','asset_binding_status','temporal_binding_status']))
   if z['evidence_status'] in {'DIRECTLY_SUPPORTED','PARTIALLY_SUPPORTED'}:check(z['condition_id']+':positive has current references',bool(z['supporting_fact_ids']) and 'NO_SUPPORTING_SOURCE' not in z['supporting_source_type'])
   elif z['evidence_status']=='EXPLICITLY_CONTRADICTED':check(z['condition_id']+':strictcounterfactrefs',bool(z['contradicting_fact_ids']))
   else:check(z['condition_id']+':unknown not covert counterevidence',bool(z['missing_information']) and not z['contradicting_fact_ids'])
  sequence=[x['technique_id'] for x in p['competitors_in_actual_review_order']]
  check(sid+':candidate IDs/order/count',sequence==c['competitors_in_actual_serialized_comparison_order']==[x['technique_id'] for x in c['candidate_assessments']] and len(sequence)==len(set(sequence))==10 and not set(sequence)&set(src['gold_technique_ids']))
  check(sid+':scope arithmetic',c['candidate_count_reviewed']==10+len(src['gold_technique_ids']) and c['unreviewed_candidate_count']==216-c['candidate_count_reviewed'] and c['all_216_reviewed'] is False)
  for x in c['candidate_assessments']:
   check(sid+':candidate frozen definition:'+x['technique_id'],x['description_sha256']==cat[x['technique_id']]['description_sha256'])
   check(sid+':candidate examined conditions:'+x['technique_id'],len(x['conditions'])>=2)
   refs(sid,x)
   for z in x['conditions']:
    refs(sid,z);check(z['condition_id']+':candidate status/source/reason',z['evidence_status'] in enums and set(z['supporting_source_type'])<=source_enums and z['reasoning'] and z['missing_information'])
    if z['condition_text'] is None:check(z['condition_id']+':absent proposition explicitly unevaluable',not x['definition_behavior_body_available'] and z['evidence_status']=='NOT_EVALUABLE')
  check(sid+':Gold competitor Cartesian coverage',len(c['pairwise_comparisons'])==10*len(src['gold_technique_ids']) and
   {(z['gold_technique_id'],z['competitor_technique_id']) for z in c['pairwise_comparisons']}=={(g,t) for g in src['gold_technique_ids'] for t in sequence})
  for z in c['pairwise_comparisons']:
   refs(sid,z);check(sid+':pair:'+z['gold_technique_id']+':'+z['competitor_technique_id'],z['comparison_label'] in pair_enums and z['qualified_independent_reference'] is False and z['can_exclude_competitor_as_having_occurred'] is False)
  check(sid+':no unknown-body entire subset exclusion',not c['missing_body_candidate_ids'] or a['distinguishable_AI_only'] is False)
 check('5200pairs output reproduces nested records',pair==[z for c in comp for z in c['pairwise_comparisons']] and len(pair)==5200)
 flat=csvrows('review/CONDITION_EVIDENCE_MATRIX.csv')
 check('2555Gold condition instances not old2618',len(flat)==2555==sum(len(a['gold_conditions']) for a in q) and len({z['condition_id'] for z in flat})==2555)
 check('1905necessary observable instances',sum(z['required_for_observable_behavior_contract']=='True' for z in flat)==1905)
 check('primary diagnoses exhaustive exclusive counts',sum(counts['primary_diagnosis_counts_exclusive'].values())==384 and dict(Counter(a['primary_diagnosis'] for a in q))=={k:v for k,v in counts['primary_diagnosis_counts_exclusive'].items() if v})
 eligibility=csvrows('review/CASE_EVALUATION_ELIGIBILITY.csv');baseline=csvrows('review/BASELINE_RESIDUAL_ERROR_AUDIT.csv')
 for n,rr in [('eligibility',eligibility),('baseline',baseline),('querysummary',csvrows('results/QUERY_SUMMARY.csv')),('humanqueue',csvrows('protocol/HUMAN_REVIEW_QUEUE.csv'))]:
  check(n+':384exactorderedrows',[x['sample_id'] for x in rr]==expected)
 check('unqualified cases excluded from metrics',all(x['eligible_for_algorithm_error_analysis']=='False' and x['eligible_for_confirmatory_primary_metric']=='False' for x in eligibility))
 check('unknown residuals never zero and no new outcomes claimed',all(x['qualified_residual_ranking_error']=='NOT_AVAILABLE' and x['strong_lexical_correct_ranking_qualified']=='NOT_AVAILABLE' and x['historical_outcome_comparison_completed']=='False' for x in baseline))
 check('formal counts distinguish workload zeros from unknown truth',counts['actual_qualified_residual_ranking_error_count']=='NOT_AVAILABLE' and counts['qualified_Gold_vs_competitor_distinguishability']=='NOT_AVAILABLE' and counts['full_Gold_semantic_sufficiency_qualified']=='NOT_AVAILABLE')
 check('12missing body types and379 affected queries',sum(not x['behavior_body_available'] for x in cat.values())==12 and sum(bool(x['missing_body_candidate_ids']) for x in comp)==379)
 check('query and technical summary units',len(csvrows('results/GOLD_TECHNIQUE_SUMMARY.csv'))==54 and sum(int(x['query_count']) for x in csvrows('results/GOLD_TECHNIQUE_SUMMARY.csv'))==520 and len(csvrows('results/CONDITION_SUMMARY.csv'))==18)
 check('earlycoreinputhashesunchanged',all(Path(x['path']).is_file() and sha(Path(x['path']))==x['sha256'] for x in load('audit/FIRST_PASS_SOURCE_HASHES.json')))
 old=load('audit/OLD_ASSET_HASH_SNAPSHOT.json');changed=[];oldmissing=[]
 for x in old['assets']:
  p=Path(x['path'])
  if not p.is_file():oldmissing.append(str(p))
  elif sha(p)!=x['sha256']:changed.append(str(p))
 check('all353checkedoldassetsunchanged',not changed and not oldmissing and len(old['assets'])==353)
 v=json.loads((B/'research3_open_vocab_384_case_blind_review01/results/OLD_ASSET_INTEGRITY_AUDIT.json').read_text());prior={x['path']:x for z in v['legacy_manifest_comparisons'] for x in z['mismatches']}
 drift=old['legacy_version_differences'];check('legacydriftonlyknownexception',len(drift)==1 and all(x['path'] in prior and x['sha256']==prior[x['path']]['current_sha256'] for x in drift))
 manifest=load('RUN_MANIFEST.json')
 check('one decision,resources0,notalgorithmexperiment',manifest['final_decision']=='GO_AFTER_INPUT_OR_LABEL_AUDIT' and all(manifest[k]==0 for k in ['new_model_calls','new_agent_calls','new_training_runs','downloads','GPU_tasks']) and not manifest['network_access'] and not manifest['server_access'])
 presence={n:(R/n).is_file() and (R/n).stat().st_size>40 for n in manifest['required_artifact_paths'] if n!='results/FINAL_VALIDATION.json'}
 check('sixteenotherrequiredartifactsnonempty',len(presence)==16 and all(presence.values()))
 parsed={}
 for p in sorted(R.rglob('*')):
  if not p.is_file() or p.name in {'FINAL_VALIDATION.json','VALIDATION_CHECK_DETAILS.json'}:continue
  if p.suffix=='.json':json.loads(p.read_text());parsed[str(p.relative_to(R))]='JSON_OK'
  elif p.suffix=='.jsonl':parsed[str(p.relative_to(R))]=sum(1 for s in p.read_text().splitlines() if s.strip() and isinstance(json.loads(s),dict))
  elif p.suffix=='.csv':
   with p.open(newline='') as f:rr=list(csv.DictReader(f))
   check(str(p.relative_to(R))+':CSVparse_nooverflow',all(None not in x for x in rr));parsed[str(p.relative_to(R))]=len(rr)
  elif p.suffix=='.py':ast.parse(p.read_text());parsed[str(p.relative_to(R))]='AST_OK_NO_HISTORICAL_CODE_EXECUTED'
 failed=[x['check'] for x in checks if not x['passed']]
 (R/'audit/VALIDATION_CHECK_DETAILS.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
 final={'status':'PASS_MECHANICAL_AUDIT_WITH_SCIENTIFIC_BLOCKERS' if not failed else 'FAIL_MECHANICAL_VALIDATION',
  'execution_status':'PARTIAL_WITH_REFERENCE_AND_DEFINITION_BLOCKERS','expected_unique_queries':384,'actual_unique_queries':len(set(ids)),
  'completed_queries':sum(a['audit_complete'] for a in q),'completion_scope':'bounded same-context audit/definition checks and explicit unevaluable reasons;not qualified semantic or all-pairs-evaluable review',
  'missing_queries':missing,'duplicate_queries':dups,'unfinished_query_records':[],
  'condition_records':len(flat),'required_observable_condition_records':1905,
  'competing_technique_records':len(comp),'competitor_assessment_instances':3840,'Gold_competitor_pair_attempts':len(pair),
  'evaluable_supplied_predicate_pairs':counts['evaluable_supplied_predicate_pair_comparisons'],
  'primary_diagnosis_counts':counts['primary_diagnosis_counts_exclusive'],
  'fact_reference_checks':{'reference_instances_checked':refcount,'qualification':'existence/owner/literal/source-locator checks only;not independent semantic validation'},
  'cross_query_reference_errors':len(xref),'cross_query_reference_error_details':xref,
  'candidate_scope':'Gold+10 frozen shuffled candidates per query;11to17total;199to205unreviewed;all216false',
  'blinding_status':'INDEPENDENT_BLIND_REVIEW_NOT_AVAILABLE','human_adjudication_completed':0,
  'qualified_residual_error_count':'NOT_AVAILABLE','qualified_baseline_recovery_count':'NOT_AVAILABLE',
  'new_model_calls':0,'new_agent_calls':0,'new_training_runs':0,'downloads':0,'GPU_tasks':0,'network_access':False,'server_access':False,
  'old_files_modified':len(changed),'old_modified_paths':changed,'old_assets_checked':len(old['assets']),'old_missing_assets':oldmissing,
  'known_preexisting_version_differences':drift,'required_artifacts_present':presence,
  'scientific_qualification':'NONINDEPENDENT_AI_PRE_AUDIT_NOT_GOLD;EXPOSED_GTE_MISS_SELECTED_DEVELOPMENT;NOT_INDEPENDENT_TEST',
  'final_decision':manifest['final_decision'],'check_count':len(checks),'failed_check_count':len(failed),'failed_checks':failed,
  'parsed_artifacts':parsed,
  'limitations':['current context previously exposed;no independent reviewer/coordinator/humanreference',
   'all384boundedrecords completed but1964pairsunevaluable and28inputinsufficient;no all216 exclusion',
   '12candidate types lack usable behavior body,affect379queries',
   '31AIvisible-core-support records do not certify fullGoldorattackintent',
   'case-level aggregated selected reference lists include context forBROAD/PREPARATORY/SCOPE;only conditionstatus supporting_fact_idsassertcondition support',
   'native type means frozen native-format copy,not independently certified source or event identity',
   'candidate definition/index reading also canonicalIDordered;randomized serialization not independent cognitive blindorder',
   'historical outcome comparisons deliberately not performed for ineligible cases;qualified error countsNOT_AVAILABLE',
   'late broader oldhashsnapshot is not full-task-start snapshot;core inputs pinned earlier',
   'one known old report hash drift preserved;no newsemanticaccuracy ormethodmetrics'],
  'delivery_seal':'finalize_audit.py verifies final artifact hash list afterthischeck;selfhash conventionally excluded'}
 path=R/'results/FINAL_VALIDATION.json';path.write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n')
 final['required_artifacts_present']['results/FINAL_VALIDATION.json']=path.is_file() and path.stat().st_size>40
 path.write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:final[k] for k in ['status','completed_queries','condition_records','check_count','failed_check_count','cross_query_reference_errors','old_files_modified','final_decision']},ensure_ascii=False,indent=2))
 if failed:raise SystemExit(1)
if __name__=='__main__':main()
