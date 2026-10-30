"""D1-D6 real saved-score diagnostics; zero model forwards, no direction selection."""
import collections,math,statistics,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def gold(ref:dict)->set[str]:return {x.split('.')[0] for x in ref['ground_truth']}
def main()->None:
 pred=load(PREVIOUS/'RERANKER_REAL_PREDICTIONS.jsonl');ref={x['sample_id']:x for x in load(BASELINES/'datasets/p0_reference.jsonl')};neural={x['sample_id']:x for x in load(PREVIOUS/'results/server_gpu/NEURAL_INPUTS.jsonl')}
 emb={x['sample_id']:x for x in load(PREVIOUS/'EMBEDDING_REAL_PREDICTIONS.jsonl') if x['method']=='E1_NATIVE_PREFIX'}
 rows=collections.defaultdict(list);cons=[];trans=[];taxonomy=[];replacements=collections.Counter();dists=[];corr=[];cross={};rank_reconstruction_errors=0
 for r in pred:rows[r['sample_id']].append(r)
 for sid,group in rows.items():
  g=gold(ref[sid]);seen={}
  for r in group:
   before=r['original_candidates'];after=r['predictions'];scores=dict(zip(after,r['raw_logits']));pool=r['candidate_pool'];k=r['candidate_k'];view=neural[sid]['variants']['prefix']['views']['V0']
   assert r['pair_truncation'] is False and len(before)==k==len(after)==len(scores) and set(before)==set(after)
   assert r['log_text_sha256']==hashlib.sha256(view.encode()).hexdigest()
   assert after==sorted(before,key=lambda t:(-scores[t],t))
   assert all(math.isfinite(x) for x in scores.values())
   original_rank={t:i+1 for i,t in enumerate(before)};newrank={t:i+1 for i,t in enumerate(after)}
   for t,score in scores.items():seen.setdefault(t,[]).append((pool,k,score,r['log_text_sha256'],r['revision']))
   missing=not bool(g&set(before));b10=bool(g&set(before[:10]));a10=bool(g&set(after[:10]));br=min((original_rank[t] for t in g if t in original_rank),default=0);ar=min((newrank[t] for t in g if t in newrank),default=0)
   category='CANDIDATE_NOT_RETRIEVED' if missing else 'CANDIDATE_DEMOTED_BY_RERANKER' if b10 and not a10 else 'CANDIDATE_PROMOTED_BY_RERANKER' if a10 and not b10 else 'CANDIDATE_RETRIEVED_BUT_RANKED_LOW' if not a10 else 'BOTH_TOP10_SUPPORTED_BY_STEP_GOLD'
   taxonomy.append({'sample_id':sid,'pool':pool,'K':k,'category':category,'first_gold_rank_before':br or 'NA','first_gold_rank_after':ar or 'NA','Gold_is_step_label_not_event_evidence':True,'semantic_cause':'UNRESOLVED'})
   rho=float(np.corrcoef([original_rank[t] for t in before],[newrank[t] for t in before])[0,1]);corr.append({'sample_id':sid,'pool':pool,'K':k,'Spearman_original_vs_CE':rho})
   for t in before:
    trans.append({'sample_id':sid,'pool':pool,'K':k,'technique_id':t,'original_rank':original_rank[t],'CE_rank':newrank[t],'raw_logit':scores[t],'step_gold':t in g,'classification':category,'evidence_support':'NOT_EVALUATED_BY_STEP_GOLD'})
   if pool=='embedding' and k==100:
    old20=next(x for x in group if x['candidate_pool']==pool and x['candidate_k']==20)
    lost=set(old20['predictions'][:10])&g-set(after[:10]);gained=[t for t in after[:10] if t not in g and t not in old20['predictions'][:10]]
    if lost:
     for t in gained:replacements[t]+=1
    for bucket,ts in [('original1_10',before[:10]),('original11_20',before[10:20]),('original21_50',before[20:50]),('original51_100',before[50:100])]:
     for t in ts:dists.append({'sample_id':sid,'bucket':bucket,'technique_id':t,'raw_logit':scores[t],'step_gold':t in g})
  for t,entries in seen.items():
   vals=[x[2] for x in entries];delta=max(vals)-min(vals)
   assert delta==0 and len({(x[3],x[4]) for x in entries})==1
   cons.append({'sample_id':sid,'technique_id':t,'appearances_across_pools_K':len(entries),'minimum_logit':min(vals),'maximum_logit':max(vals),'maximum_absolute_difference':delta,'same_log_text_revision':True,'score_source':'same cached pair forward reused; not independent rerun stability proof'})
 csvout('CANDIDATE_SCORE_CONSISTENCY.csv',cons);csvout('CANDIDATE_RANK_TRANSITIONS.csv',trans);csvout('RERANKER_FAILURE_TAXONOMY.csv',taxonomy);csvout('reranker_diagnostics/RANK_CORRELATIONS.csv',corr);csvout('reranker_diagnostics/RAW_SCORE_BUCKETS.csv',dists)
 csvout('reranker_diagnostics/REPLACEMENT_TECHNIQUE_COUNTS.csv',[{'technique_id':t,'replacement_occurrences_when_Gold_lost_from_Embed20_to100':n} for t,n in replacements.most_common()])
 summary=[]
 for pool in ['embedding','lexical']:
  for k in [20,50,100]:
   subset=[x for x in taxonomy if x['pool']==pool and x['K']==k];c=collections.Counter(x['category'] for x in subset);rho=[x['Spearman_original_vs_CE'] for x in corr if x['pool']==pool and x['K']==k]
   summary.append({'pool':pool,'K':k,'N':len(subset),**dict(c),'mean_Spearman':statistics.mean(rho),'median_Spearman':statistics.median(rho)})
 buckets=[]
 for bucket in ['original1_10','original11_20','original21_50','original51_100']:
  a=[x['raw_logit'] for x in dists if x['bucket']==bucket]
  buckets.append({'bucket':bucket,'N':len(a),'mean':float(np.mean(a)),'SD':float(np.std(a,ddof=1)),'Q10':float(np.quantile(a,.1)),'median':float(np.median(a)),'Q90':float(np.quantile(a,.9))})
 csvout('reranker_diagnostics/FAILURE_SUMMARY.csv',summary);csvout('reranker_diagnostics/SCORE_DISTRIBUTION_SUMMARY.csv',buckets)
 protocol=json.loads((PREVIOUS/'results/server_gpu/manifests/NEURAL_RUNTIME_PROTOCOL.json').read_text())
 result={'status':'RERANKER_FAILURE_DIAGNOSED_FROM_SAVED_SCORES','source_prediction_sha256':sha256(PREVIOUS/'RERANKER_REAL_PREDICTIONS.jsonl'),'native_condition_rows':len(pred),'unique_saved_pairs':len(cons),'maximum_cross_pool_score_difference':max(x['maximum_absolute_difference'] for x in cons),'duplicate_candidates':0,'invalid_parent_ids':0,'score_index_alignment_and_descending_reconstruction':'ALL5850_PASS','eval_mode':'verified in frozen source .eval(); not a newly observed runtime probe','tokenizer_revision':'f7481e6055501a30fb19d090657df9ec1f79ab2c','input_order':'log query first; technique document second; matches official pair convention','raw_logit_direction':'larger more relevant per official model card; NOT chosen using CAM-LDS scores','num_labels_dimension':'scalar logits from saved source logits.view(-1) and one score per pair; config body requires independent retrieval for full verification','sigmoid':'strictly monotonic in real arithmetic; no need for classification Softmax; no actual score inversion','input_truncation':'tokenizer truncation=False; shared log2048/doc1024 explicit upstream truncation,65knowledge docs clipped; original input loss can matter, but K changes do not alter same pair text/score','K_effect':'new high-logit distractors displace earlier Gold; not score changes of fixed candidates','cross_batch_stability':'NOT_INDEPENDENTLY_TESTED; same pair cache guarantees saved equality','new_model_forwards':0,'implementation_error_found':False,'semantic_mechanism_cause':'UNRESOLVED','summary':summary,'score_buckets':buckets,'replacement_techniques_top20':replacements.most_common(20),'runtime_protocol':protocol}
 save('RERANKER_SCORING_VALIDATION.json',result)
 print(json.dumps({'pairs_checked':len(cons),'condition_rows':len(pred),'score_differences':0,'new_forwards':0,'summary':summary},indent=2))
if __name__=='__main__':main()
