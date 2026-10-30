"""Real frozen lexical candidate recall; never mislabeled embedding inference."""
import json,csv,sys,time,statistics,hashlib
from pathlib import Path
from collections import defaultdict
R=Path(__file__).resolve().parents[1];OLD=R.parent/'research3_technique_strong_baselines_generalization02';sys.path.insert(0,str(R/'frozen_baselines'/OLD.name/'baselines'))
from engine import Index,rank

def csvout(n,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with (R/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def main():
 docs=json.loads((OLD/'knowledge/K2_DESCRIPTION_16_1.json').read_text());idx=Index(docs,'char');results=[];errors=[]
 protocols=[('P0','datasets/p0_prediction.jsonl','datasets/p0_reference.jsonl'),('P1','datasets/p1_resampled/prediction.jsonl','datasets/p1_resampled/reference.jsonl'),('P2_SAMPLED','datasets/p2_v2/prediction_sampled.jsonl','datasets/p2_v2/reference_sampled.jsonl')]
 for protocol,predpath,refpath in protocols:
  start=time.perf_counter();outpath=R/'rerankers'/('CANDIDATES_'+protocol+'.jsonl');native=[]
  # Prediction process receives text and public documents only, reference loaded afterwards.
  with (OLD/predpath).open() as inp,outpath.open('w') as out:
   for line in inp:
    sample=json.loads(line);text='\n'.join(l['text'] for s in sample['sources'] for l in s['lines']);scores=idx.score(text);ordering=sorted(range(len(idx.ids)),key=lambda i:(-scores[i],idx.ids[i]));pred=[idx.ids[i] for i in ordering]
    row={'sample_id':sample['sample_id'],'method':'M0_FROZEN_CHARACTER_CANDIDATES','qualification':'PROJECT_NEW_NONNEURAL_INFERENCE','predictions':pred,'scores':[scores[i] for i in ordering],'input_sha256':hashlib.sha256(text.encode()).hexdigest()};out.write(json.dumps(row)+'\n');native.append(row)
  refs={x['sample_id']:x for x in map(json.loads,(OLD/refpath).read_text().splitlines())}
  for k in [20,50,100]:
   step=defaultdict(list);hit=[];rec=[];allhit=[];miss=0;goldtotal=0
   for row in native:
    r=refs[row['sample_id']];g={x.split('.')[0] for x in r['ground_truth']};found=g&set(row['predictions'][:k]);h=int(bool(found));v=len(found)/len(g);a=int(found==g);hit.append(h);rec.append(v);allhit.append(a);miss+=len(g-found);goldtotal+=len(g);step[(r['scenario_id'],r['step_id'])].append((h,v,a))
    if k==100 and not h:errors.append({'protocol':protocol,'sample_id':r['sample_id'],'scenario_id':r['scenario_id'],'step_id':r['step_id'],'gold':';'.join(sorted(g)),'error_type':'RETRIEVAL_FAILURE_TOP100','attribution':'Measured absence from frozen lexical candidates; not semantic model failure'})
   results.append({'method':'CharacterNgramTFIDF','protocol':protocol,'qualification':'NONNEURAL_CANDIDATE_UPPER_BOUND_NOT_RERANKER','k':k,'N_queries':len(native),'N_logic_steps':len(step),'candidate_hit_at_k':statistics.mean(hit),'candidate_recall_at_k':statistics.mean(rec),'all_gold_recalled_fraction':statistics.mean(allhit),'step_macro_hit_at_k':statistics.mean(statistics.mean(x[0] for x in rr) for rr in step.values()),'step_macro_recall_at_k':statistics.mean(statistics.mean(x[1] for x in rr) for rr in step.values()),'unrecalled_gold_occurrences':miss,'total_gold_occurrences':goldtotal,'zero_gold_candidate_queries':sum(not x for x in hit),'inference_seconds':time.perf_counter()-start})
  print(protocol,len(native),round(time.perf_counter()-start,3),flush=True)
 csvout('CANDIDATE_RECALL_UPPER_BOUNDS.csv',results);csvout('results/LEXICAL_CANDIDATE_FAILURES.csv',errors)
if __name__=='__main__':main()
