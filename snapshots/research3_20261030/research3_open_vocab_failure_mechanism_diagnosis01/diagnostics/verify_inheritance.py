"""Byte verification only; no old code/model invocation."""
import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def main()->None:
 start=time.monotonic();checks=[];mismatches=[]
 for root,expected in [(P,211),(D,1938)]:
  manifest=root/'manifests/DELIVERY_SHA256.json';entries=json.loads(manifest.read_text());assert len(entries)==expected
  for x in entries:
   p=root/x['path'];actual=sha(p) if p.exists() else None
   if actual!=x['sha256'] or p.stat().st_size!=x['bytes']:mismatches.append({'root':str(root),'path':x['path'],'expected_sha256':x['sha256'],'actual_sha256':actual,'expected_bytes':x['bytes'],'actual_bytes':p.stat().st_size if p.exists() else None})
  checks.append({'root':str(root),'manifest_sha256':sha(manifest),'files_checked':len(entries),'files_matched':len(entries)-sum(x['root']==str(root) for x in mismatches)})
 # A one-space edit in the narrative does not alter frozen numeric assets.
 # Preserve the mismatch and compare with the manifest-matching dated mirror.
 import difflib
 if mismatches:
  assert len(mismatches)==1 and mismatches[0]['root']==str(P) and mismatches[0]['path']=='R3_OPEN_VOCAB_TECHNIQUE_GENERALIZATION_RESULTS.md',mismatches
  a=P/'reports/2026-10-28--open-vocab-technique--r01--seen-unseen-review.md';b=P/mismatches[0]['path']
  assert sha(a)==mismatches[0]['expected_sha256'] and ''.join(a.read_text().split())==''.join(b.read_text().split())
  mismatches[0]['classification']='NARRATIVE_WHITESPACE_ONLY; numeric assets unchanged; old files not repaired'
  (R/'inherited/PRIOR_REPORT_WHITESPACE_DIFF.patch').write_text(''.join(difflib.unified_diff(a.read_text().splitlines(True),b.read_text().splitlines(True))))
 cp=json.loads((D/'CONTRASTIVE_CHECKPOINT_MANIFEST.json').read_text())['checkpoints'];assert len(cp)==378
 for c in cp:assert sha(D/c['checkpoint_path'])==c['sha256']
 source_paths=[P/'results/FINAL_VALIDATION.json',P/'manifests/DELIVERY_SHA256.json',D/'manifests/DELIVERY_SHA256.json',D/'data/P0_INPUTS.jsonl',D/'data/P0_REFERENCE.jsonl',D/'data/KNOWLEDGE_K2.json',D/'embeddings/FROZEN_GTE_FEATURES.npz']
 source_paths+=list((P/'score_matrices').glob('*.npz'))+list((P/'score_matrices').glob('*.json'))
 dump('inherited/ASSET_HASH_AUDIT.json',{'status':'PASS_NUMERIC_ASSETS_WITH_DOCUMENTED_NARRATIVE_WHITESPACE_DRIFT' if mismatches else 'PASS','manifests':checks,'mismatches':mismatches,'checkpoints_verified':378,'new_model_calls':0,'seconds':time.monotonic()-start,'source_files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in source_paths],'previous_Gold_timing_disclosure':json.loads((P/'reports/EVALUATOR_GOLD_ACCESS_TIMING_DISCLOSURE.json').read_text()),'source_sha256':sha(Path(__file__))})
 print('INHERITED_NUMERIC_HASHES_PASS',211,1938,378,'narrative_drifts',len(mismatches))
if __name__=='__main__':main()
