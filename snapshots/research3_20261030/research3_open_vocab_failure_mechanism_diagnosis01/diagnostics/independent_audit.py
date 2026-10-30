"""Independent scalar/rank recomputation against immutable saved predictions.

No import of run_diagnosis, no model/code loading, no parameter fitting.
"""
import collections,csv,gzip,json,math,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import R,P,D,jl,sha,dump
def csvrows(n):
 with (R/n).open() as f:return list(csv.DictReader(f))
def main()->None:
 begin=time.monotonic();saved={}
 for r in jl(P/'FUSION_PREDICTIONS.jsonl'):
  if r['method'] in ['Z0','S0','C4']:saved[r['fold_id'],str(r['seed']),r['view_id'],r['sample_id'],r['method']]=r
 selected={(r['fold_id'],str(r['seed']),r['view_id']):r for r in json.loads((P/'calibration/SELECTED_PARAMETERS.json').read_text()) if r['method']=='C4'}
 refs={r['sample_id']:r for r in jl(D/'data/P0_REFERENCE.jsonl')};query={tuple(r[k] for k in ['fold_id','seed','view_id','sample_id']):r for r in csvrows('QUERY_DIAGNOSTICS.csv')};assert len(query)==5850
 goldrows={(r['fold_id'],r['seed'],r['view_id'],r['sample_id'],r['candidate_technique_id']):r for r in csvrows('UNSEEN_GOLD_TECHNIQUE_DIAGNOSTICS.csv')};assert len(goldrows)==3630
 count=0;chunks=0;goldchecked=0;maxerr=0.;all_counts=collections.defaultdict(collections.Counter);current=None;block=[]
 def check_block(key,rows):
  nonlocal chunks,goldchecked,maxerr
  assert len(rows)==216;ids=[r['candidate_technique_id'] for r in rows];assert ids==sorted(set(ids));qrow=query[key];s=selected[key[:3]];n=s['normalization'];la=s['parameters']['lambda'];ga=s['parameters']['gamma']
  gte=saved[*key,'Z0'];c4=saved[*key,'C4'];b3=saved[*key,'S0'];seen=[r['candidate_seen_in_training']=='True' for r in rows]
  gi={t:i+1 for i,t in enumerate(gte['ranking_all216'])};ci={t:i+1 for i,t in enumerate(c4['ranking_all216'])};bi={t:i+1 for i,t in enumerate(b3['ranking_all216'])};zi={t:i for i,t in enumerate(ids)}
  none_sup=[];none_bias=[]
  for j,row in enumerate(rows):
   t=ids[j];q=gte['scores_all216'][j];b=b3['scores_all216'][j];zq=(q-n['gte']['mean'])/n['gte']['sd'];su=la*(b-n['b3']['mean'])/n['b3']['sd'] if seen[j] else 0.;bias=-ga if seen[j] else 0.
   # Scalar algebra is independent of NumPy vector implementation. A tolerance
   # admits equivalent operation ordering, never changes the stored rank.
   expected={'gte_raw_score':q,'gte_normalized_contribution':zq,'c4_supervised_correction':su,'c4_seen_bias_correction':bias,'c4_frozen_score':c4['scores_all216'][j],'remove_supervision_score':zq+bias,'remove_bias_score':zq+su}
   for k,v in expected.items():
    err=abs(float(row[k])-v);maxerr=max(maxerr,err);assert err<2e-14,(key,t,k,err)
   assert abs((zq+su+bias)-c4['scores_all216'][j])<2e-14
   assert int(row['gte_rank'])==gi[t] and int(row['c4_rank'])==ci[t] and int(row['b3_closed_output_rank'])==bi[t]
   assert (b is not None)==seen[j] and (row['b3_availability']=='AVAILABLE')==seen[j]
   if b is not None:assert float(row['b3_score'])==b
   else:assert row['b3_score']==''
   none_sup.append((zq+bias,t));none_bias.append((zq+su,t))
  nr={t:i+1 for i,(_,t) in enumerate(sorted(none_sup,key=lambda x:(-x[0],x[1])))};br={t:i+1 for i,(_,t) in enumerate(sorted(none_bias,key=lambda x:(-x[0],x[1])))}
  for row in rows:assert int(row['remove_supervision_rank'])==nr[row['candidate_technique_id']] and int(row['remove_bias_rank'])==br[row['candidate_technique_id']]
  gold=set(refs[key[3]]['gold_technique_ids']);ug={t for j,t in enumerate(ids) if not seen[j] and t in gold};sg=gold-ug
  uorder=[t for t in gte['ranking_all216'] if not seen[zi[t]]];assert uorder==[t for t in c4['ranking_all216'] if not seen[zi[t]]];ur={t:i+1 for i,t in enumerate(uorder)}
  actual_type='MIXED' if sg and ug else 'ALL_SEEN' if sg else 'ALL_UNSEEN';assert qrow['sample_type']==actual_type
  c=all_counts[key[1:3]];c['query_count']+=1;c['all_seen_queries']+=actual_type=='ALL_SEEN';c['all_unseen_queries']+=actual_type=='ALL_UNSEEN';c['mixed_queries']+=actual_type=='MIXED'
  if ug:
   g=bool(ug&set(gte['predictions']));v=bool(ug&set(c4['predictions']));c['unseen_target_queries']+=1;c['gte_hit_queries']+=g;c['gte_miss_queries']+=not g;c['c4_hit_queries']+=v;c['c4_miss_queries']+=not v;c['retained_hit_queries']+=g and v;c['lost_hit_queries']+=g and not v;c['new_hit_queries']+=not g and v;c['both_miss_queries']+=not g and not v;c['unseen_gold_pairs']+=len(ug)
   assert qrow['gte_unseen_hit10']==str(g) and qrow['c4_unseen_hit10']==str(v) and int(qrow['best_unseen_internal_order_rank'])==min(ur[t] for t in ug)
   for t in ug:
    out=goldrows[*key,t];j=zi[t];goldchecked+=1
    assert int(out['gte_rank'])==gi[t] and int(out['c4_rank'])==ci[t] and int(out['unseen_internal_order_rank'])==ur[t]
    gseen=sum(seen[zi[k]] for k in gte['ranking_all216'][:gi[t]-1]);cseen=sum(seen[zi[k]] for k in c4['ranking_all216'][:ci[t]-1]);assert gi[t]==ur[t]+gseen and ci[t]==ur[t]+cseen
    assert int(out['gte_seen_before_gold'])==gseen and int(out['c4_seen_before_gold'])==cseen and int(out['rank_change_from_seen_crossings'])==cseen-gseen
    assert int(out['remove_supervision_rank'])==nr[t] and int(out['remove_bias_rank'])==br[t]
    assert gi[t]>10 or nr[t]<=10  # remove nonnegative seen bias cannot hurt an originally hit unseen target
   if not g:c['gte_miss_with_unseen_order_rank_gt10']+=min(ur[t] for t in ug)>10;c['gte_miss_with_unseen_order_rank_le10']+=min(ur[t] for t in ug)<=10
   if not v:c['c4_miss_with_unseen_order_rank_gt10']+=min(ur[t] for t in ug)>10;c['c4_miss_with_unseen_order_rank_le10']+=min(ur[t] for t in ug)<=10
  chunks+=1
 with gzip.open(R/'CANDIDATE_COMPARISON.csv.gz','rt') as f:
  for row in csv.DictReader(f):
   key=tuple(row[k] for k in ['fold_id','seed','view_id','sample_id'])
   if current is not None and key!=current:check_block(current,block);block=[]
   current=key;block.append(row);count+=1
 if block:check_block(current,block)
 for r in csvrows('INDEPENDENT_HIT_RECOUNT.csv'):
  c=all_counts[r['seed'],r['view_id']]
  for k,v in c.items():assert int(r[k])==v,(k,r[k],v)
 # Explicit query/pair set arithmetic against saved predictions.
 for name,unit in [('QUERY_HIT_MISS_SETS.json','QUERY'),('GOLD_TECHNIQUE_HIT_MISS_SETS.json','QUERY_GOLD_TECHNIQUE_PAIR')]:
  for s in json.loads((R/name).read_text()):
   assert s['unit']==unit and s['count']==len(s['members']);members=[]
   for key,qrow in query.items():
    if key[:3]!=(s['fold_id'],str(s['seed']),s['view_id']):continue
    ids_seen={t for t in qrow['seen_gold_ids'].split('|') if t};ug=set(refs[key[3]]['gold_technique_ids'])-ids_seen
    for t in (sorted(ug) if unit!='QUERY' else [None] if ug else []):
     g=bool(set(saved[*key,'Z0']['predictions'])&(ug if t is None else {t}));v=bool(set(saved[*key,'C4']['predictions'])&(ug if t is None else {t}))
     flags={'GTE_UNSEEN_HIT_QUERY_SET':g,'GTE_UNSEEN_MISS_QUERY_SET':not g,'C4_UNSEEN_HIT_QUERY_SET':v,'C4_UNSEEN_MISS_QUERY_SET':not v,'GTE_HIT_C4_LOST_SET':g and not v,'GTE_MISS_C4_NEW_HIT_SET':not g and v,'GTE_HIT':g,'GTE_MISS':not g,'C4_HIT':v,'C4_MISS':not v,'LOST':g and not v,'NEW':not g and v}
     if flags[s['set_name']]:members.append(key[3] if t is None else [key[3],t])
   assert sorted(s['members'])==sorted(members)
 losses=list(jl(R/'GTE_HIT_C4_LOST_CASES.jsonl'))
 for row in losses:
  assert row['gte_rank']<=10<row['c4_rank'];assert row['remove_supervision_rank']<=10 and row['primary_attribution']=='SEEN_SCORE_BOOST'
  assert any(x['seen'] and x['supervised_delta']+x['bias_delta']>0 for x in row['crossing_seen_candidates'])
  assert not row['scale_mismatch_identified'] and not row['rank_fusion_effect_applicable']
 dump('results/INDEPENDENT_DIAGNOSTIC_AUDIT.json',{'status':'PASS','candidate_rows_checked':count,'query_blocks_checked':chunks,'gold_rows_checked':goldchecked,'loss_cases_checked':len(losses),'scalar_score_max_abs_error':maxerr,'all_query_and_gold_sets_recreated_from_frozen_predictions':True,'within_unseen_rank_identity_verified':True,'counterfactuals_are_diagnostics_only':True,'heldout_Gold_used_for_posterior_diagnosis_only':True,'new_model_calls':0,'new_parameters_fit':0,'seconds':time.monotonic()-begin,'source_sha256':sha(Path(__file__))})
 print('INDEPENDENT_DIAGNOSTIC_AUDIT_PASS',count,chunks,goldchecked,len(losses))
if __name__=='__main__':main()
