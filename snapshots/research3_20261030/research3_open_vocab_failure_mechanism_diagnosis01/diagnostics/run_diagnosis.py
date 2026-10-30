"""Frozen score arithmetic and posterior reference analysis. No model invocation."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='2'
import collections,csv,gzip,json,resource,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def ranks(z:np.ndarray)->tuple[np.ndarray,np.ndarray]:
 order=np.argsort(-np.where(np.isnan(z),-np.inf,z),kind='stable');pos=np.empty(216,dtype=int);pos[order]=np.arange(1,217);return order,pos
def clean(v):return None if isinstance(v,float) and not np.isfinite(v) else v
def emit(f,obj):f.write(json.dumps(obj,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
def main()->None:
 begin=time.monotonic();assert json.loads((R/'inherited/ASSET_HASH_AUDIT.json').read_text())['status'].startswith('PASS')
 # Exact sanitized parent inputs were hash-verified before these bodies are read.
 features=np.load(D/'embeddings/FROZEN_GTE_FEATURES.npz',allow_pickle=False);allowed=set(features['sample_ids'].tolist())
 assert len(allowed)==975 and not any(s.startswith(('1-35-','1-36-','1-37-')) or 'CONV-A01' in s for s in allowed)
 inputs={r['sample_id']:r for r in jl(D/'data/P0_INPUTS.jsonl')};refs={r['sample_id']:r for r in jl(D/'data/P0_REFERENCE.jsonl')};assert set(inputs)==set(refs)==allowed
 knowledge=json.loads((D/'data/KNOWLEDGE_K2.json').read_text());selected=json.loads((P/'calibration/SELECTED_PARAMETERS.json').read_text())
 selected={(s['fold_id'],s['seed'],s['view_id']):s for s in selected if s['method']=='C4'};assert len(selected)==42
 saved={}
 for row in jl(P/'FUSION_PREDICTIONS.jsonl'):
  if row['method'] in ['Z0','S0','C4']:saved[row['fold_id'],row['seed'],row['view_id'],row['sample_id'],row['method']]=row
 assert len(saved)==17550
 folds=json.loads((P/'inherited/SPLITS_WITHOUT_EVALUATION_LABEL_SUMMARIES.json').read_text())['folds'];folds={f['fold_id']:f for f in folds}
 queryrows=[];goldrows=[];lossrows=[];missrows=[];summaries=[];pairsets=[];setrecords=[];cards=[];rankchecks=0;scorechecks=0;mismatches=[];candidate_rows=0
 candidate_columns=['fold_id','seed','view_id','sample_id','candidate_technique_id','logical_step_id','candidate_seen_in_training','training_class_support','gold_in_posterior_reference','gte_raw_score','gte_rank','gte_normalized_contribution','b3_score','b3_availability','b3_closed_output_rank','b3_normalized_score','c4_supervised_correction','c4_seen_bias_correction','c4_frozen_score','c4_rank','remove_supervision_score','remove_supervision_rank','remove_bias_score','remove_bias_rank']
 with gzip.open(R/'CANDIDATE_COMPARISON.csv.gz','wt',newline='') as candout,(R/'GTE_HIT_C4_LOST_CASES.jsonl').open('w') as lostout:
  cw=csv.DictWriter(candout,candidate_columns);cw.writeheader()
  for path in sorted((P/'score_matrices').glob('*.npz')):
   meta=json.loads(path.with_suffix('.json').read_text());d=dict(np.load(path,allow_pickle=False));ids=d['technique_ids'].tolist();ididx={t:i for i,t in enumerate(ids)};seen=d['seen'];support=d['support'];config=(meta['fold_id'],meta['seed'],meta['augmentation']);s=selected[config];f=folds[config[0]]
   assert sha(path)==s['matrix_sha256'];assert ids==sorted(knowledge) and len(ids)==216
   train=list(jl(D/f['one_view_train_path']));unique={r['logical_step_id']:r for r in train};assert len(unique)==len(train)
   counts=collections.Counter(t for r in train for t in set(r['gold_technique_ids']));assert all(support[j]==counts[t] for j,t in enumerate(ids)) and np.array_equal(seen,support>0)
   norm=s['normalization'];lam=s['parameters']['lambda'];gamma=s['parameters']['gamma'];sets={n:set() for n in ['GTE_UNSEEN_HIT_QUERY_SET','GTE_UNSEEN_MISS_QUERY_SET','C4_UNSEEN_HIT_QUERY_SET','C4_UNSEEN_MISS_QUERY_SET','GTE_HIT_C4_LOST_SET','GTE_MISS_C4_NEW_HIT_SET']};ps={n:set() for n in ['GTE_HIT','GTE_MISS','C4_HIT','C4_MISS','LOST','NEW']};qr=[];gr=[]
   for ii in np.flatnonzero(d['partitions']=='HELDOUT'):
    sid=str(d['sample_ids'][ii]);inp=inputs[sid];ref=refs[sid];assert inp['logical_step_id']==ref['logical_step_id']==str(d['logical_step_ids'][ii])
    assert inp['input_hash']==sha_bytes(inp['input_log_text'].encode())
    gold={ididx[t] for t in ref['gold_technique_ids']};sg=gold&set(np.flatnonzero(seen));ug=gold-sg;mixed=bool(sg and ug)
    q=d['gte_scores'][ii].astype(float);b=d['b3_scores'][ii];zq=(q-norm['gte']['mean'])/norm['gte']['sd'];zb=np.zeros(216);zb[seen]=(b[seen]-norm['b3']['mean'])/norm['b3']['sd'];sup=lam*zb;bias=-gamma*seen.astype(float)
    computed=zq+sup+bias;ss=saved[*config,sid,'C4'];c4=np.array(ss['scores_all216'],dtype=float);no_sup=zq+bias;no_bias=zq+sup
    og,rg=ranks(q);oc,rc=ranks(c4);ob,rb=ranks(b);ons,rns=ranks(no_sup);onb,rnb=ranks(no_bias)
    orders={'Z0':og,'S0':ob,'C4':oc}
    for method,order in orders.items():
     old=saved[*config,sid,method];expected=[ids[j] for j in order];rankchecks+=1
     if old['ranking_all216']!=expected:mismatches.append({'config':config,'sample_id':sid,'method':method,'kind':'RANK_DISAGREEMENT'})
    for name,actual,expect in [('C4',c4,computed),('Z0',np.array(saved[*config,sid,'Z0']['scores_all216']),q)]:
     delta=float(np.max(np.abs(actual-expect)));scorechecks+=216
     if delta!=0:mismatches.append({'config':config,'sample_id':sid,'method':name,'kind':'SCORE_DISAGREEMENT','max_abs_error':delta})
    bsave=saved[*config,sid,'S0']['scores_all216'];assert all((v is None and not seen[j]) or (seen[j] and v==b[j]) for j,v in enumerate(bsave))
    assert [j for j in og if not seen[j]]==[j for j in oc if not seen[j]]
    within={j:k+1 for k,j in enumerate(j for j in og if not seen[j])};best=lambda rr,gg:min((int(rr[j]) for j in gg),default=None)
    hit=lambda rr,gg,k=10:any(rr[j]<=k for j in gg)
    common={'fold_id':config[0],'seed':config[1],'view_id':config[2],'sample_id':sid,'logical_step_id':inp['logical_step_id'],'scenario_id':inp['scenario_id'],'simulation_id':inp['simulation_id'],'variant_id':inp['variant_id'],'script_group_id':inp['script_group_id'],'script_identity_status':inp['script_identity_status']}
    gh=hit(rg,ug);ch=hit(rc,ug);base={**common,'gold_ids':'|'.join(ids[j] for j in sorted(gold)),'seen_gold_ids':'|'.join(ids[j] for j in sorted(sg)),'unseen_gold_ids':'|'.join(ids[j] for j in sorted(ug)),'gold_count':len(gold),'unseen_gold_count':len(ug),'is_mixed':mixed,'sample_type':'MIXED' if mixed else 'ALL_SEEN' if sg else 'ALL_UNSEEN','gte_unseen_hit10':gh if ug else None,'c4_unseen_hit10':ch if ug else None,'gte_unseen_best_rank':best(rg,ug),'c4_unseen_best_rank':best(rc,ug),'gte_seen_hit10':hit(rg,sg) if sg else None,'c4_seen_hit10':hit(rc,sg) if sg else None,'gte_seen_in_top10':sum(seen[og[:10]]),'c4_seen_in_top10':sum(seen[oc[:10]]),'best_unseen_internal_order_rank':min((within[j] for j in ug),default=None),'remove_supervision_unseen_best_rank':best(rns,ug),'remove_bias_unseen_best_rank':best(rnb,ug),'D1':bool(ug),'D2':bool(ug and gh and not ch),'D3':bool(ug and not gh),'D4':bool(mixed and hit(rc,sg) and not ch),'input_view':inp['input_view'],'input_utf8_bytes':len(inp['input_log_text'].encode()),'input_characters':len(inp['input_log_text']),'input_hash':inp['input_hash'],'development_status':inp['development_status'],'source_reference_label_unit':'AUTHOR_LOGICAL_STEP_LABEL_NOT_EVENT_MECHANISM_CERTIFICATE','semantic_cause':'UNRESOLVED'}
    queryrows.append(base);qr.append(base)
    for n,v in [('GTE_UNSEEN_HIT_QUERY_SET',gh),('GTE_UNSEEN_MISS_QUERY_SET',not gh),('C4_UNSEEN_HIT_QUERY_SET',ch),('C4_UNSEEN_MISS_QUERY_SET',not ch),('GTE_HIT_C4_LOST_SET',gh and not ch),('GTE_MISS_C4_NEW_HIT_SET',not gh and ch)]:
     if ug and v:sets[n].add(sid)
    for j,t in enumerate(ids):
     cw.writerow({**{k:common[k] for k in ['fold_id','seed','view_id','sample_id','logical_step_id']},'candidate_technique_id':t,'candidate_seen_in_training':bool(seen[j]),'training_class_support':int(support[j]),'gold_in_posterior_reference':j in gold,'gte_raw_score':float(q[j]),'gte_rank':int(rg[j]),'gte_normalized_contribution':float(zq[j]),'b3_score':float(b[j]) if seen[j] else None,'b3_availability':'AVAILABLE' if seen[j] else 'NO_SUPERVISED_CLASSIFIER','b3_closed_output_rank':int(rb[j]),'b3_normalized_score':float(zb[j]) if seen[j] else None,'c4_supervised_correction':float(sup[j]),'c4_seen_bias_correction':float(bias[j]),'c4_frozen_score':float(c4[j]),'c4_rank':int(rc[j]),'remove_supervision_score':float(no_sup[j]),'remove_supervision_rank':int(rns[j]),'remove_bias_score':float(no_bias[j]),'remove_bias_rank':int(rnb[j])});candidate_rows+=1
    topfields={}
    for prefix,order in [('gte',og),('b3',ob),('c4',oc)]:
     for k in [1,5,10]:topfields[f'{prefix}_top{k}']='|'.join(ids[j] for j in order[:k])
    for j in sorted(ug):
     t=ids[j];pair=(sid,t);ps['GTE_HIT' if rg[j]<=10 else 'GTE_MISS'].add(pair);ps['C4_HIT' if rc[j]<=10 else 'C4_MISS'].add(pair)
     if rg[j]<=10<rc[j]:ps['LOST'].add(pair)
     if rc[j]<=10<rg[j]:ps['NEW'].add(pair)
     before_unseen=sum(not seen[k] for k in og[:rg[j]-1]);before_seen=int(rg[j])-1-before_unseen;cbefore_unseen=sum(not seen[k] for k in oc[:rc[j]-1]);cbefore_seen=int(rc[j])-1-cbefore_unseen
     assert before_unseen==cbefore_unseen==within[j]-1 and int(rg[j])==1+before_unseen+before_seen
     row={**common,'candidate_technique_id':t,'gold_is_unseen':True,'training_class_support':int(support[j]),'gte_raw_score':float(q[j]),'gte_rank':int(rg[j]),'b3_score':None,'b3_state':'NO_SUPERVISED_CLASSIFIER','b3_closed_output_rank':int(rb[j]),'c4_score':float(c4[j]),'c4_rank':int(rc[j]),'gte_standardized_contribution':float(zq[j]),'c4_supervised_correction':float(sup[j]),'c4_seen_bias_correction':float(bias[j]),'unseen_internal_order_rank':within[j],'gte_seen_before_gold':before_seen,'gte_unseen_before_gold':before_unseen,'c4_seen_before_gold':cbefore_seen,'c4_unseen_before_gold':cbefore_unseen,'rank_change_from_seen_crossings':cbefore_seen-before_seen,'gte_gold_minus_top1_score':float(q[j]-q[og[0]]),'gte_gold_minus_rank10_score':float(q[j]-q[og[9]]),'c4_gold_minus_top1_score':float(c4[j]-c4[oc[0]]),'c4_gold_minus_rank10_score':float(c4[j]-c4[oc[9]]),'gte_exact_score_tie_size':int(np.sum(q==q[j])),'c4_exact_score_tie_size':int(np.sum(c4==c4[j])),'remove_supervision_rank':int(rns[j]),'remove_bias_rank':int(rnb[j]),'restore_gte_rank':int(rg[j]),'lambda':lam,'gamma':gamma,'parameter_source':s['selection_reason'],'parameter_file_sha256':sha(P/'calibration/SELECTED_PARAMETERS.json'),'gold_count':len(gold),'is_mixed':mixed,'input_view':inp['input_view'],'input_bytes':len(inp['input_log_text'].encode()),'knowledge_version':inp['knowledge_version'],'description_bytes':len(knowledge[t].encode()),'description_characters':len(knowledge[t]),'D1':True,'D2':bool(rg[j]<=10<rc[j]),'D3':bool(rg[j]>10),'D4_query':base['D4'],'semantic_cause':'UNRESOLVED','prior_development_exposure':True,**topfields}
     wrong=[k for k in range(216) if k not in gold];nearest=min(wrong,key=lambda k:(abs(q[k]-q[j]),ids[k]));row['nearest_wrong_candidate_id']=ids[nearest];row['gte_gold_minus_nearest_wrong_score']=float(q[j]-q[nearest])
     for prefix,rr in [('gte',rg),('c4',rc)]:
      for k in [1,5,10]:row[f'{prefix}_hit{k}']=bool(rr[j]<=k)
     goldrows.append(row);gr.append(row)
     if rg[j]>10:missrows.append(row.copy())
     if rg[j]<=10<rc[j]:
      entered=[k for k in oc[:10] if k not in set(og[:10])];cross=[k for k in oc[:rc[j]-1] if seen[k] and rg[k]>rg[j]]
      restored=rns[j]<=10;primary='SEEN_SCORE_BOOST' if restored and any(sup[k]+bias[k]>0 for k in cross) else 'UNRESOLVED'
      detail={**row,'primary_attribution':primary,'secondary_attributions':['MIXED_LABEL_COMPETITION'] if mixed else [],'query_level_all_unseen_hit_lost':base['D2'],'numeric_interpretation':'registered_component_removal_only; no attack-semantic causal claim','scale_mismatch_identified':False,'rank_fusion_effect_applicable':False,'bias_direction_for_unseen':'nonnegative_gamma_penalizes_seen; cannot alone demote_unseen','alternative_explanations':'relative component scale influences strength but no independent calibration evidence proves scale mismatch; input/label semantic cause unresolved','source_formula':'z_gte+lambda*seen*z_b3-gamma*seen','competitors_new_to_top10':[],'crossing_seen_candidates':[]}
      def component(k):return {'candidate_id':ids[k],'seen':bool(seen[k]),'support':int(support[k]),'gte_raw':float(q[k]),'gte_rank':int(rg[k]),'gte_normalized':float(zq[k]),'b3_logit':float(b[k]) if seen[k] else None,'b3_normalized':float(zb[k]) if seen[k] else None,'supervised_delta':float(sup[k]),'bias_delta':float(bias[k]),'c4_score':float(c4[k]),'c4_rank':int(rc[k]),'c4_margin_over_gold':float(c4[k]-c4[j]),'remove_supervision_rank':int(rns[k]),'remove_bias_rank':int(rnb[k])}
      detail['competitors_new_to_top10']=[component(k) for k in entered];detail['crossing_seen_candidates']=[component(k) for k in cross];emit(lostout,detail)
      lossrows.append({**row,'primary_attribution':primary,'query_level_all_unseen_hit_lost':base['D2'],'new_top10_competitors':'|'.join(ids[k] for k in entered),'new_top10_seen_count':int(sum(seen[k] for k in entered)),'crossing_seen_count':len(cross),'removing_supervision_restores_gold_top10':bool(restored),'bias_removal_rank_change':int(rnb[j]-rc[j]),'attribution_is_computational_not_semantic_causal':True})
    if config[1]==17 and config[2]=='ONE_VIEW_PER_STEP' and ug and not gh:
     cards.append({**common,'input_view':inp['input_view'],'input_hash':inp['input_hash'],'frozen_input_text':inp['input_log_text'],'input_original_upstream_hash':inp['upstream_reference_input_hash'],'unseen_gold':[{'id':ids[j],'description':knowledge[ids[j]],'gte_score':float(q[j]),'gte_rank':int(rg[j]),'unseen_order_rank':within[j],'c4_rank':int(rc[j])} for j in sorted(ug)],'gte_top10':[{'id':ids[j],'description':knowledge[ids[j]],'score':float(q[j]),'seen':bool(seen[j])} for j in og[:10]],'annotation_or_semantic_cause':'UNRESOLVED_NO_INDEPENDENT_EVENT_EVIDENCE','input_is_truncated_existing_frozen_view':True,'raw_archive_accessed':False})
   unseenn=[x for x in qr if x['unseen_gold_count']];den=len(unseenn);gmiss=[x for x in unseenn if not x['gte_unseen_hit10']];cmiss=[x for x in unseenn if not x['c4_unseen_hit10']]
   summary={'fold_id':config[0],'seed':config[1],'view_id':config[2],'query_count':len(qr),'logical_steps':len({x['logical_step_id'] for x in qr}),'unseen_target_queries':den,'unseen_gold_pairs':len(gr),'gte_hit_queries':len(sets['GTE_UNSEEN_HIT_QUERY_SET']),'gte_miss_queries':len(sets['GTE_UNSEEN_MISS_QUERY_SET']),'c4_hit_queries':len(sets['C4_UNSEEN_HIT_QUERY_SET']),'c4_miss_queries':len(sets['C4_UNSEEN_MISS_QUERY_SET']),'retained_hit_queries':len(sets['GTE_UNSEEN_HIT_QUERY_SET']&sets['C4_UNSEEN_HIT_QUERY_SET']),'lost_hit_queries':len(sets['GTE_HIT_C4_LOST_SET']),'new_hit_queries':len(sets['GTE_MISS_C4_NEW_HIT_SET']),'both_miss_queries':len(sets['GTE_UNSEEN_MISS_QUERY_SET']&sets['C4_UNSEEN_MISS_QUERY_SET']),'gte_miss_with_unseen_order_rank_gt10':sum(x['best_unseen_internal_order_rank']>10 for x in gmiss),'gte_miss_with_unseen_order_rank_le10':sum(x['best_unseen_internal_order_rank']<=10 for x in gmiss),'c4_miss_with_unseen_order_rank_gt10':sum(x['best_unseen_internal_order_rank']>10 for x in cmiss),'c4_miss_with_unseen_order_rank_le10':sum(x['best_unseen_internal_order_rank']<=10 for x in cmiss),'mixed_queries':sum(x['is_mixed'] for x in qr),'mixed_both_gold_groups_hit_c4':sum(x['is_mixed'] and x['c4_unseen_hit10'] and x['c4_seen_hit10'] for x in qr),'D4_queries':sum(x['D4'] for x in qr),'all_seen_queries':sum(x['sample_type']=='ALL_SEEN' for x in qr),'all_unseen_queries':sum(x['sample_type']=='ALL_UNSEEN' for x in qr)}
   summaries.append(summary)
   for name,members in sets.items():setrecords.append({'fold_id':config[0],'seed':config[1],'view_id':config[2],'set_name':name,'unit':'QUERY','members':sorted(members),'count':len(members)})
   for name,members in ps.items():
    pairsets.append({'fold_id':config[0],'seed':config[1],'view_id':config[2],'set_name':name,'unit':'QUERY_GOLD_TECHNIQUE_PAIR','members':[list(x) for x in sorted(members)],'count':len(members)})
   print('DIAGNOSED',*config,len(qr),flush=True)
   assert sum(p.stat().st_size for p in R.rglob('*') if p.is_file())<2000000000
 csvout('QUERY_DIAGNOSTICS.csv',queryrows);csvout('UNSEEN_GOLD_TECHNIQUE_DIAGNOSTICS.csv',goldrows);csvout('GTE_MISS_GOLD_DIAGNOSTICS.csv',missrows);csvout('GTE_HIT_C4_LOST_DIAGNOSTICS.csv',lossrows);csvout('results/HIT_COUNTS_BY_FOLD_SEED_VIEW.csv',summaries)
 dump('QUERY_HIT_MISS_SETS.json',setrecords);dump('GOLD_TECHNIQUE_HIT_MISS_SETS.json',pairsets)
 with (R/'GTE_MISS_EVIDENCE_CARDS.jsonl').open('w') as f:
  for c in sorted(cards,key=lambda x:(x['fold_id'],x['sample_id'])):emit(f,c)
 grouped=[]
 for seed in [17,42,73]:
  for view in ['ONE_VIEW_PER_STEP','MULTI_VIEW_AUGMENTATION']:
   rs=[r for r in summaries if r['seed']==seed and r['view_id']==view];out={'seed':seed,'view_id':view}
   for k in summaries[0]:
    if k not in ['fold_id','seed','view_id']:out[k]=sum(r[k] for r in rs)
   for name in ['GTE_HIT','GTE_MISS','C4_HIT','C4_MISS','LOST','NEW']:out[name+'_gold_pairs']=sum(x['count'] for x in pairsets if x['seed']==seed and x['view_id']==view and x['set_name']==name)
   grouped.append(out)
 csvout('INDEPENDENT_HIT_RECOUNT.csv',grouped);csvout('results/INPUT_OR_SCORE_MISMATCHES.csv',mismatches)
 dump('results/DIAGNOSIS_EXECUTION_RECEIPT.json',{'status':'COMPLETED' if not mismatches else 'COMPLETED_WITH_DOCUMENTED_SCORE_MISMATCHES','candidate_comparison_rows':candidate_rows,'query_rows':len(queryrows),'unseen_gold_pair_rows':len(goldrows),'gte_missed_gold_rows':len(missrows),'lost_gold_pair_rows':len(lossrows),'evidence_cards_primary_seed17_ONE':len(cards),'ranking_checks':rankchecks,'score_cells_checked':scorechecks,'mismatch_count':len(mismatches),'within_unseen_order_identical_all_queries':True,'counterfactual_use':'DIAGNOSIS_ONLY_NOT_FORMAL_MODEL_RESULTS','new_model_calls':0,'new_training_updates':0,'new_parameters_fit':0,'new_grid_evaluations':0,'raw_archives_read':False,'server_access':False,'seconds':time.monotonic()-begin,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'source_sha256':sha(Path(__file__)),'protocol_sha256':sha(R/'DIAGNOSTIC_PROTOCOL.json'),'frozen_prediction_sha256':sha(P/'FUSION_PREDICTIONS.jsonl'),'selected_parameter_sha256':sha(P/'calibration/SELECTED_PARAMETERS.json')})
 print(json.dumps(grouped,ensure_ascii=False))
def sha_bytes(b:bytes)->str:
 import hashlib
 return hashlib.sha256(b).hexdigest()
if __name__=='__main__':main()
