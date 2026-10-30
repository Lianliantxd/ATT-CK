"""Source/length and hard-candidate diagnostics on fixed saved predictions only."""
import collections,csv,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
E=mod(BENCH/'evaluate_techniques.py','extra_strata_frozen_v1')
def main():
 refs={r['sample_id']:r for r in load(ROOT/'data/P0_REFERENCE.jsonl')};ids=json.loads((ROOT/'data/CANDIDATE_TECHNIQUE_IDS.json').read_text());sources={r['sample_id']:sorted({e['source_type'] for e in r['events']}) for r in load(OLD/'MECHANISM_LITERAL.jsonl')};groups=collections.defaultdict(list)
 for r in load(ROOT/'TRAINING_BASELINE_PREDICTIONS.jsonl'):groups[r['method'],str(r['seed']),r['augmentation']].append(r)
 out=[]
 for (method,seed,aug),rs in groups.items():
  for source in sorted({s for vv in sources.values() for s in vv}):
   rr=[r for r in rs if source in sources[r['sample_id']]]
   if rr:
    m=E.summarize([{'ground_truth':refs[r['sample_id']]['gold_technique_ids'],'predictions':r['predictions']} for r in rr],ids);out.append({'method':method,'seed':seed,'augmentation':aug,'source_type_present':source,'qualification':'SOURCE_PRESENCE_STRATA_OVERLAP; not source-only input intervention; no cross-platform transfer',**m})
 csvout('results/SOURCE_TYPE_RESULTS.csv',out)
 # Ranking ability conditional on the SAME original frozen GTE Top20; pool never uses heldout Gold.
 frozen={r['sample_id']:r for r in load(ROOT/'TRAINING_BASELINE_PREDICTIONS.jsonl') if r['method']=='B1'};hard=[]
 for (method,seed,aug),rs in groups.items():
  eligible=[]
  for r in rs:
   g=set(refs[r['sample_id']]['gold_technique_ids']);pool=frozen[r['sample_id']]['ranking_all216'][:20]
   if g&set(pool):
    ranking=[t for t in r['ranking_all216'] if t in set(pool)];eligible.append({'ground_truth':list(g),'predictions':ranking[:10]})
  m=E.summarize(eligible,ids);hard.append({'method':method,'seed':seed,'augmentation':aug,'pool':'same original current-view frozen GTE Top20 across all methods','qualification':'conditional on Gold in pool, descriptive selection not full-population metric',**m})
 csvout('results/FIXED_HARD_CANDIDATE_RANKING.csv',hard)
 print('source and fixed candidate strata saved')
if __name__=='__main__':main()
