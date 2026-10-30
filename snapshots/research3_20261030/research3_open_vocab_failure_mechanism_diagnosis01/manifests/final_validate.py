"""Seal only completed diagnosis; no training, scoring, network or parent writes."""
import ast,csv,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
REQUIRED=['DIAGNOSTIC_PROTOCOL.json','CANDIDATE_COMPARISON.csv.gz','QUERY_DIAGNOSTICS.csv','UNSEEN_GOLD_TECHNIQUE_DIAGNOSTICS.csv','GTE_MISS_GOLD_DIAGNOSTICS.csv','GTE_HIT_C4_LOST_DIAGNOSTICS.csv','GTE_HIT_C4_LOST_CASES.jsonl','LOST_CASES_FULL_ANALYSIS.md','GTE_MISS_EVIDENCE_CARDS.jsonl','QUERY_HIT_MISS_SETS.json','GOLD_TECHNIQUE_HIT_MISS_SETS.json','INDEPENDENT_HIT_RECOUNT.csv','COUNTERFACTUAL_COMPONENT_DIAGNOSIS.csv','INPUT_LABEL_MAPPING_AUDIT.csv','IDENTICAL_VIEW_DIFFERENT_STEP_AUDIT.csv','FAILURE_MECHANISM_RESEARCH_DECISION.md','R3_OPEN_VOCAB_FAILURE_MECHANISM_DIAGNOSIS_RESULTS.md','README.md']
def main():
 start=time.monotonic()
 for n in REQUIRED:assert (R/n).is_file() and (R/n).stat().st_size>0,n
 receipt=json.loads((R/'results/DIAGNOSIS_EXECUTION_RECEIPT.json').read_text());audit=json.loads((R/'results/INDEPENDENT_DIAGNOSTIC_AUDIT.json').read_text());assert receipt['mismatch_count']==0 and audit['status']=='PASS'
 assert receipt['source_sha256']==sha(R/'diagnostics/run_diagnosis.py') and audit['source_sha256']==sha(R/'diagnostics/independent_audit.py')
 assert receipt['protocol_sha256']==sha(R/'DIAGNOSTIC_PROTOCOL.json')==(R/'protocol/PROTOCOL_SHA256.txt').read_text().strip()
 assert receipt['frozen_prediction_sha256']==sha(P/'FUSION_PREDICTIONS.jsonl') and receipt['selected_parameter_sha256']==sha(P/'calibration/SELECTED_PARAMETERS.json')
 assert receipt['new_model_calls']==receipt['new_training_updates']==receipt['new_parameters_fit']==receipt['new_grid_evaluations']==0
 assert not receipt['raw_archives_read'] and not receipt['server_access']
 assert audit['candidate_rows_checked']==receipt['candidate_comparison_rows']==1263600 and audit['query_blocks_checked']==5850 and audit['gold_rows_checked']==3630 and audit['loss_cases_checked']==189
 assert audit['scalar_score_max_abs_error']==0 and audit['within_unseen_rank_identity_verified']
 expected={'QUERY_DIAGNOSTICS.csv':5850,'UNSEEN_GOLD_TECHNIQUE_DIAGNOSTICS.csv':3630,'GTE_MISS_GOLD_DIAGNOSTICS.csv':3234,'GTE_HIT_C4_LOST_DIAGNOSTICS.csv':189,'INPUT_LABEL_MAPPING_AUDIT.csv':975}
 for n,count in expected.items():
  with (R/n).open() as f:assert sum(1 for _ in csv.DictReader(f))==count
 with (R/'INDEPENDENT_HIT_RECOUNT.csv').open() as f:rs=list(csv.DictReader(f))
 assert len(rs)==6
 for r in rs:
  assert int(r['query_count'])==975 and int(r['unseen_target_queries'])==450 and int(r['unseen_gold_pairs'])==605
  assert int(r['gte_hit_queries'])==66 and int(r['gte_miss_queries'])==384 and int(r['gte_miss_with_unseen_order_rank_gt10'])==349 and int(r['gte_miss_with_unseen_order_rank_le10'])==35
  assert int(r['c4_hit_queries'])==(34 if r['view_id']=='ONE_VIEW_PER_STEP' else 35) and int(r['new_hit_queries'])==0
  assert int(r['all_seen_queries'])==525 and int(r['all_unseen_queries'])==305 and int(r['mixed_queries'])==145
 cards=list(jl(R/'GTE_MISS_EVIDENCE_CARDS.jsonl'));assert len(cards)==384
 for c in cards:
  assert not c['sample_id'].startswith(('1-35-','1-36-','1-37-')) and 'CONV-A01' not in c['sample_id']
  assert 'input_is_truncated_existing_frozen_view' not in c and c['input_is_existing_limited_view']
  assert c['whether_current_text_was_actually_cut_short'].startswith('UNRESOLVED') and not c['raw_archive_accessed']
 cardreceipt=json.loads((R/'results/EVIDENCE_CARD_QUALIFICATION_RECEIPT.json').read_text());assert cardreceipt['output_sha256']==sha(R/'GTE_MISS_EVIDENCE_CARDS.jsonl') and cardreceipt['source_sha256']==sha(R/'diagnostics/qualify_evidence_cards.py')
 summary=json.loads((R/'results/EVIDENCE_AND_MAPPING_SUMMARY.json').read_text());assert summary['source_sha256']==sha(R/'diagnostics/summarize_evidence.py') and summary['parent_id_mapping_mismatches']==summary['missing_candidate_gold_ids']==0
 interface=json.loads((R/'results/SOURCE_INTERFACE_AUDIT.json').read_text());assert interface['status']=='PASS' and interface['source_sha256']==sha(R/'diagnostics/audit_input_interface.py') and interface['feature_and_input_hashes_equal'] and interface['matrix_metadata_files_checked']==42
 assert summary['unseen_gold_pairs_order_gt10']==499 and summary['gte_missed_unseen_gold_pairs']==539
 for n in ['analysis-report.md','stats-appendix.md','figure-catalog.md','provenance.json']:assert (R/'reports/analysis-output'/n).stat().st_size>0
 provenance=json.loads((R/'reports/analysis-output/provenance.json').read_text())
 for s in provenance['source_files']+provenance['figures']:assert sha(R/s['path'])==s['sha256'],s['path']
 assert len(provenance['figures'])==9
 for f in provenance['figures']:
  p=R/f['path']
  if p.suffix=='.pdf':assert p.read_bytes().startswith(b'%PDF-')
  if p.suffix=='.png':assert p.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
  if p.suffix=='.svg':assert '<svg' in p.read_text()
 report=(R/'R3_OPEN_VOCAB_FAILURE_MECHANISM_DIAGNOSIS_RESULTS.md').read_text();assert all(t in report for t in ['349','384','32','605','539','REQUEST_TAIL_NOT_RECEIVED','UNRESOLVED','DEVELOPMENT_ONLY','γ','空格'])
 all_files=[p for p in sorted(R.rglob('*')) if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts];source_count=0
 for p in all_files:
  if p.suffix=='.py':ast.parse(p.read_text());source_count+=1
 assert sum(p.stat().st_size for p in all_files)<2000000000
 # Preserve initial report-space drift, verify nothing else in either parent changed.
 initial=json.loads((R/'inherited/ASSET_HASH_AUDIT.json').read_text());known={(x['root'],x['path']):x['actual_sha256'] for x in initial['mismatches']};counts=[]
 for parent,n in [(P,211),(D,1938)]:
  man=json.loads((parent/'manifests/DELIVERY_SHA256.json').read_text());assert len(man)==n
  for e in man:assert sha(parent/e['path'])==known.get((str(parent),e['path']),e['sha256']),e['path']
  counts.append({'root':str(parent),'files_checked':n,'no_changes_since_diagnosis_started':True})
 for source in initial['source_files']:assert sha(Path(source['path']))==source['sha256'],source['path']
 excluded={'manifests/DELIVERY_SHA256.json','results/FINAL_VALIDATION.json'}
 entries=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in all_files if str(p.relative_to(R)) not in excluded and p.suffix!='.log']
 dump('manifests/DELIVERY_SHA256.json',entries)
 final={'status':'PASS_OFFLINE_DIAGNOSIS_FOR_RECEIVED_SCOPE_WITH_DOCUMENTED_LIMITATIONS','scientific_qualification':'DEVELOPMENT_ONLY','request_tail_received':False,'root_artifacts':len(REQUIRED),'new_model_calls':0,'new_training':0,'new_search':0,'server_access':False,'candidate_comparison_rows':1263600,'query_rows':5850,'unseen_gold_rows':3630,'primary_query_partition':{'retained':34,'lost':32,'original_cross_group_block_candidate':35,'within_unseen_order_obstruction':349},'counterfactuals_are_not_new_model_results':True,'all_scores_and_sets_independently_verified':True,'Gold_used_only_for_explicit_posterior_diagnosis':True,'historical_Gold_preflight_timing_deviation_disclosed':True,'parent_recheck':counts,'historical_narrative_whitespace_drift_preserved':len(known),'python_AST_files':source_count,'scientific_figure_formats_verified':9,'evidence_cards':384,'semantic_cause_status':'UNRESOLVED','delivery_files':len(entries),'delivery_manifest_sha256':sha(R/'manifests/DELIVERY_SHA256.json'),'total_new_disk_bytes':sum(p.stat().st_size for p in all_files),'validator_sha256':sha(Path(__file__)),'seconds':time.monotonic()-start}
 dump('results/FINAL_VALIDATION.json',final)
 for e in entries:assert sha(R/e['path'])==e['sha256'],'concurrent write '+e['path']
 print(json.dumps({k:final[k] for k in ['status','delivery_files','candidate_comparison_rows','total_new_disk_bytes','seconds']},ensure_ascii=False))
if __name__=='__main__':main()
