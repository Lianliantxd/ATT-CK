"""Post-seal candidate packaging; same-context shuffling,not independent blind."""
import hashlib,json,random
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 seal=json.loads((R/'audit/FIRST_PASS_SEAL.json').read_text())
 assert all(sha(R/x['path'])==x['sha256'] for x in seal['files'])
 source=B/'research3_open_vocab_failure_mechanism_diagnosis01/GTE_MISS_EVIDENCE_CARDS.jsonl'
 rows=[json.loads(s) for s in source.read_text().splitlines()];frozen=json.loads((R/'inputs/FROZEN_CASE_MANIFEST.json').read_text())
 assert [x['sample_id'] for x in rows]==[x['sample_id'] for x in frozen['cases']]
 corpus=json.loads((B/'research3_domain_adaptive_contrastive_learning01/data/KNOWLEDGE_K2.json').read_text())
 packets=[];defs={};sets=[]
 for x in rows:
  competitors=[]
  for c in x['gte_top10']:
   t=c['id'];d=c['description'];assert t in corpus and d==corpus[t]
   assert t not in defs or defs[t]==d;defs[t]=d;competitors.append({'technique_id':t,'frozen_description':d,'description_sha256':hashlib.sha256(d.encode()).hexdigest()})
  assert len({c['technique_id'] for c in competitors})==10
  seed=int(hashlib.sha256(('DEA01|20261029|'+x['sample_id']).encode()).hexdigest()[:16],16)
  competitors.sort(key=lambda c:c['technique_id']);random.Random(seed).shuffle(competitors)
  gold=[c['id'] for c in x['unseen_gold']];ids=[c['technique_id'] for c in competitors]
  assert not set(gold)&set(ids)
  packets.append({'sample_id':x['sample_id'],'logical_step_id':x['logical_step_id'],'gold_technique_ids':gold,
   'competitors_in_actual_review_order':competitors,'shuffle_seed':seed,'coordinator_independent':False,
   'selection_bias':'model-selected candidate set remains biased even without rank/score display',
   'candidate_scope':'Gold targets plus10 shuffled frozen historical candidates;subset of216',
   'candidate_count_reviewed_planned':len(gold)+10,'all_216_reviewed':False,'unreviewed_candidate_count':216-len(gold)-10,
   'blinding_status':'INDEPENDENT_BLIND_REVIEW_NOT_AVAILABLE'})
  sets.append(tuple(sorted(ids)))
 (R/'inputs/SHUFFLED_COMPETITOR_PACKETS.jsonl').write_text(''.join(json.dumps(p,ensure_ascii=False,separators=(',',':'))+'\n' for p in packets))
 dump('inputs/COMPETITOR_FROZEN_DEFINITIONS.json',defs)
 dump('audit/CANDIDATE_PACKAGING_RECEIPT.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'first_pass_seal_sha256':sha(R/'audit/FIRST_PASS_SEAL.json'),
  'first_pass_integrity_verified':True,'source_path':str(source),'source_sha256':sha(source),'packets':len(packets),'candidate_ids':len(defs),
  'unique_candidate_sets':len(set(sets)),'rank_and_score_fields_emitted':False,'independent_coordinator':False,
  'candidate_order_file_sha256':sha(R/'inputs/SHUFFLED_COMPETITOR_PACKETS.jsonl'),'actual_seed_recorded_per_case':True,'new_model_calls':0})
 print(json.dumps({'packets':len(packets),'unique_candidate_ids':len(defs),'unique_candidate_sets':len(set(sets)),'candidate_ids':sorted(defs)}))
if __name__=='__main__':main()
