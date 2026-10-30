"""Independent final audit of saved predictions. No model, training, or server calls.

Run only after evaluate_saved.py has completed. Writes just two audit artifacts.
Uses independently implemented standard-library metrics, not the project evaluator.
"""
import csv, hashlib, json, math, statistics, traceback
from pathlib import Path
from collections import Counter, defaultdict
ROOT=Path(__file__).resolve().parents[1]
METRICS=['mrr','top1_accuracy','top5_accuracy','top10_accuracy','precision_at_1','precision_at_5','precision_at_10','recall_at_1','recall_at_5','recall_at_10','micro_f1_at_5','macro_f1_at_5_all_candidates','macro_f1_at_5_gold_present']
EXPECTED_METHODS={'B0','B1','B2','B3','B4','B5','B6','B7','B8','B9','B9_CONST'}
MODES=['ONE_VIEW_PER_STEP','MULTI_VIEW_AUGMENTATION'];SEEDS=['17','42','73']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def jl(p):
 with p.open() as f:
  for line in f:
   if line.strip():yield json.loads(line)
def csvrows(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))
def check(condition,message):
 if not condition:raise AssertionError(message)
def close(a,b,label):
 check(math.isfinite(float(a)) and math.isfinite(float(b)) and abs(float(a)-float(b))<1e-11,f'{label}: independently computed {a}, saved {b}')
def key(r,partition=True):return (r['method'],str(r['seed']),r['augmentation'],r['fold_id'])+((r['evaluation_partition'].upper(),) if partition else ())
def canonical_digest(r):return hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest()
class Metrics:
 def __init__(self,ids):self.ids=ids;self.n=0;self.s=Counter();self.tp=Counter();self.fp=Counter();self.fn=Counter();self.gold=set()
 def add(self,pred,gold):
  check(bool(gold),'empty Gold cannot enter evaluator');self.n+=1;self.gold|=gold
  ranks=[i+1 for i,t in enumerate(pred[:10]) if t in gold];self.s['mrr']+=1/min(ranks) if ranks else 0
  for k in [1,5,10]:
   hit=len(set(pred[:k])&gold);self.s[f'top{k}_accuracy']+=int(hit>0);self.s[f'precision_at_{k}']+=hit/k;self.s[f'recall_at_{k}']+=hit/len(gold)
  selected=set(pred[:5]);self.tp.update(selected&gold);self.fp.update(selected-gold);self.fn.update(gold-selected)
 def merge(self,other):
  self.n+=other.n;self.s.update(other.s);self.tp.update(other.tp);self.fp.update(other.fp);self.fn.update(other.fn);self.gold|=other.gold
 def result(self):
  check(self.n>0,'empty metric aggregate')
  def f1(t):
   den=2*self.tp[t]+self.fp[t]+self.fn[t];return 2*self.tp[t]/den if den else 0
  out={'n_records':self.n,**{m:self.s[m]/self.n for m in METRICS if m in self.s}}
  den=2*sum(self.tp.values())+sum(self.fp.values())+sum(self.fn.values())
  out.update(micro_f1_at_5=2*sum(self.tp.values())/den,macro_f1_at_5_all_candidates=sum(f1(t) for t in self.ids)/len(self.ids),macro_f1_at_5_gold_present=sum(f1(t) for t in self.gold)/len(self.gold))
  return out

def audit():
 ids=json.loads((ROOT/'data/CANDIDATE_TECHNIQUE_IDS.json').read_text());universe=set(ids);check(len(ids)==len(universe)==216,'candidate universe216')
 refs={r['sample_id']:r for r in jl(ROOT/'data/P0_REFERENCE.jsonl')};check(len(refs)==975,'975 original queries')
 protocol=json.loads((ROOT/'manifests/TRAINING_PROTOCOL.json').read_text());splitsha=sha(ROOT/'GROUPED_TRAIN_VALIDATION_SPLITS.json')
 check(splitsha==protocol['split_file_sha256']==sha(ROOT/'splits/GROUPED_TRAIN_VALIDATION_SPLITS.json'),'registered split hashes changed')
 folds={f['fold_id']:f for f in json.loads((ROOT/'GROUPED_TRAIN_VALIDATION_SPLITS.json').read_text())['folds']}
 allheld=[];fold_expected={};fold_seen={}
 for fid,f in folds.items():
  train=list(jl(ROOT/f['paths']['train']));val=list(jl(ROOT/f['paths']['validation_inputs']));held=list(jl(ROOT/f['paths']['heldout_inputs']))
  roles={'TRAIN':[r['sample_id'] for r in train],'VALIDATION':[r['sample_id'] for r in val],'HELDOUT':[r['sample_id'] for r in held]}
  rolelogic=[{r['logical_step_id'] for r in rr} for rr in [train,val,held]]
  check(not(rolelogic[0]&rolelogic[1] or rolelogic[0]&rolelogic[2] or rolelogic[1]&rolelogic[2]),fid+' role logical overlap')
  for rr in [train,val,held]:check(set(Counter(r['logical_step_id'] for r in rr).values())=={5},fid+' replicas split')
  check(all('gold_technique_ids' not in r for r in val+held),fid+' Gold in input files')
  seen={t for r in train for t in r['gold_technique_ids']};check(seen==set(f['train_seen_techniques']),fid+' seen labels changed');fold_seen[fid]=seen
  for role,ss in roles.items():check(set(ss)==set(f[role.lower()+'_sample_ids']),fid+' saved IDs differ')
  expected={k:set(v) for k,v in roles.items()};expected['INNER_VALIDATION']=expected['VALIDATION'];expected['TRAIN_DIAGNOSTIC_R0']={r['sample_id'] for r in train if r['sampling_replica_id']==0};fold_expected[fid]=expected
  allheld+=roles['HELDOUT']
 check(Counter(allheld)==Counter(refs.keys()),'outer folds must evaluate all original queries once')
 shared=json.loads((ROOT/'data/manifests/SHARED_CONTENT_AUDIT.json').read_text())['normalized_cross_scenario_groups']
 for fid,e in fold_expected.items():
  sets=[{refs[s]['logical_step_id'] for s in e[role]} for role in ['TRAIN','VALIDATION','HELDOUT']]
  for shared_group in shared:check(sum(bool(set(shared_group['logical_steps'])&s) for s in sets)<=1,fid+' identified shared content across roles')
 tokenpath=ROOT.parent/'research3_attack_mechanism_discrimination01/results/gpu/ACTUAL_MODEL_INPUT_TOKENS.json'
 tokens={(x['sample_id'],x['view']):x['actual_token_counts']['embedding'] for x in json.loads(tokenpath.read_text())}
 groups={};strata={};membership=defaultdict(set);held_details={};export_hashes={};pred_manifest=[];raw_partitions=Counter();methods=set();rowtotal=0
 def accumulator(mapping,k):
  if k not in mapping:mapping[k]=Metrics(ids)
  return mapping[k]
 for directory in ['runs_frozen','runs_B2','runs_heads']:
  paths=sorted((ROOT/'results'/directory).glob('*_predictions.jsonl'));check(bool(paths),'missing saved predictions in '+directory)
  for path in paths:
   digest=hashlib.sha256()
   with path.open('rb') as handle:
    for line in handle:
     digest.update(line)
     if not line.strip():continue
     r=json.loads(line);raw_partitions[r['evaluation_partition']]+=1;r['evaluation_partition']=r['evaluation_partition'].upper();k=key(r);sid=r['sample_id'];rowtotal+=1;methods.add(r['method'])
     check(k[3] in folds and k[4] in fold_expected[k[3]],'unknown fold or partition '+str(k))
     check(sid in fold_expected[k[3]][k[4]],'prediction escaped legal role: '+str(k)+' '+sid)
     check(sid not in membership[k],'duplicate row in condition '+str(k));membership[k].add(sid)
     rank=r['ranking_all216'];check(len(rank)==len(set(rank))==216 and set(rank)==universe,'candidate removed/duplicated/added')
     check(r['predictions']==rank[:10],'Top10 does not match full216');g=set(refs[sid]['gold_technique_ids']);check(g<=universe,'invalid normalized Gold')
     accumulator(groups,k).add(r['predictions'],g)
     if k[4]!='HELDOUT':continue
     seen=fold_seen[k[3]];b=k[:4];seen_gold=g&seen;unseen_gold=g-seen
     labels=[('SINGLE_LABEL' if len(g)==1 else 'MULTILABEL',g),('ALL_GOLD_SEEN' if not unseen_gold else 'ALL_GOLD_UNSEEN' if not seen_gold else 'MIXED_SEEN_UNSEEN',g)]
     if seen_gold:labels.append(('SEEN_GOLD_SUBSET',seen_gold))
     if unseen_gold:labels.append(('UNSEEN_GOLD_SUBSET',unseen_gold))
     length=tokens[sid,'RAW'];labels.append(('TOKENS_LE256' if length<=256 else 'TOKENS257_512' if length<=512 else 'TOKENS_GT512',g))
     for category,gg in labels:accumulator(strata,b+(category,)).add(r['predictions'],gg)
     ranks=[i+1 for i,t in enumerate(rank[:10]) if t in g];d={'top1':int(rank[0] in g),'top10':int(bool(ranks)),'mrr':1/min(ranks) if ranks else 0,'gold_seen_count':len(seen_gold),'gold_unseen_count':len(unseen_gold),'best_gold_rank_all216':min(i+1 for i,t in enumerate(rank) if t in g),'candidate_hit20':int(bool(set(rank[:20])&g)),'label_count':len(g)}
     detail_key=b+(sid,);check(detail_key not in held_details,'duplicate heldout key');held_details[detail_key]=d;export_hashes[detail_key]=canonical_digest(r)
   pred_manifest.append({'path':str(path.relative_to(ROOT)),'sha256':digest.hexdigest(),'bytes':path.stat().st_size})
 check(methods==EXPECTED_METHODS,'expected methods not all executed: '+str(methods));check(len(groups)==1106,'expected1106 evaluation conditions; actual '+str(len(groups)));check(len(held_details)==54600,'expected54600 heldout predictions')
 check(sum(k[4]=='HELDOUT' for k in groups)==392,'expected392 heldout conditions')
 for k,ss in membership.items():check(ss==fold_expected[k[3]][k[4]],'condition missing legal expected samples: '+str(k))
 def verify_metrics(saved,computed,label):
  check(int(saved['n_records'])==computed['n_records'],label+' n_records')
  for m in METRICS:close(saved[m],computed[m],label+' '+m)
 saved_groups={}
 for r in csvrows(ROOT/'GROUPED_VALIDATION_RESULTS.csv'):
  k=key(r);check(k not in saved_groups,'duplicate saved group');saved_groups[k]=r;check(k in groups,'unexpected saved condition');verify_metrics(r,groups[k].result(),str(k));check(int(r['candidate_count'])==216,'saved candidate count')
 check(set(saved_groups)==set(groups),'saved condition coverage mismatch')
 saved_strata={}
 for r in csvrows(ROOT/'SEEN_UNSEEN_TECHNIQUE_RESULTS.csv'):
  k=key(r,False)+(r['stratum'],);check(k not in saved_strata,'duplicate stratum');saved_strata[k]=r;check(k in strata,'unexpected saved stratum');verify_metrics(r,strata[k].result(),str(k))
  if r['stratum'] in ['SEEN_GOLD_SUBSET','UNSEEN_GOLD_SUBSET']:check('full216' in r['subset_qualification'] and 'both' in r['subset_qualification'],'subset must disclose nonexclusive mixed labels')
 check(set(saved_strata)==set(strata),'stratum coverage mismatch')
 byseed={};overall={}
 for b in sorted({k[:3] for k in groups}):
  ks=[k for k in groups if k[:3]==b and k[4]=='HELDOUT'];check(len(ks)==7,'missing outer fold for method seed mode');counter=Counter(s for k in ks for s in membership[k]);check(counter==Counter(refs.keys()),'each method seed mode must cover975 once')
  if b[0] not in ['B0','B1']:check(b[1] in SEEDS and b[2] in MODES,'unexpected trained seed/mode')
  agg=Metrics(ids)
  for k in ks:agg.merge(groups[k])
  result=agg.result();foldm=[groups[k].result() for k in ks];result.update(mrr_equal_scene_mean=statistics.mean(m['mrr'] for m in foldm),mrr_scene_SD=statistics.stdev(m['mrr'] for m in foldm),top10_equal_scene_mean=statistics.mean(m['top10_accuracy'] for m in foldm));byseed[b]=result
 saved_byseed={}
 for r in csvrows(ROOT/'results/OVERALL_RESULTS_BY_SEED.csv'):
  b=(r['method'],r['seed'],r['augmentation']);check(b not in saved_byseed and b in byseed,'unknown/duplicate seed summary');saved_byseed[b]=r;verify_metrics(r,byseed[b],str(b))
  for m in ['mrr_equal_scene_mean','mrr_scene_SD','top10_equal_scene_mean']:close(r[m],byseed[b][m],str(b)+' '+m)
 check(set(saved_byseed)==set(byseed),'seed summary coverage')
 average_metrics=['mrr','top1_accuracy','top5_accuracy','top10_accuracy','precision_at_5','recall_at_5','micro_f1_at_5','macro_f1_at_5_all_candidates','mrr_equal_scene_mean','top10_equal_scene_mean']
 for r in csvrows(ROOT/'results/OVERALL_RESULTS.csv'):
  b=(r['method'],r['augmentation']);check(b not in overall,'duplicate averaged result');ss=[v for k,v in byseed.items() if (k[0],k[2])==b];check(int(r['seeds'])==len(ss),'seed count mismatch');overall[b]=r
  for m in average_metrics:
   close(r[m],statistics.mean(s[m] for s in ss),str(b)+' seed mean '+m)
   if len(ss)>1:close(r[m+'_seed_SD'],statistics.stdev(s[m] for s in ss),str(b)+' seed SD '+m)
   else:check(r[m+'_seed_SD']=='NA_FROZEN_NO_STOCHASTIC_TRAINING','frozen uncertainty must not be invented')
 check(len(byseed)==56 and len(overall)==20,'all expected seed/method/mode summaries')
 primary=[];primary_rows=csvrows(ROOT/'results/FOUR_PRIMARY_HYPOTHESES.csv');check(len(primary_rows)==56,'exactly4 hypotheses x2modes x7scenes')
 for row in primary_rows:
  hyp=row['hypothesis'];a,b={'H1':('B4','B1'),'H2':('B5','B4'),'H3':('B7','B6'),'H4':('B9','B8')}[hyp];mode=row['augmentation'];scene=row['scenario'];fid=next(k for k,f in folds.items() if f['heldout_scenario']==scene)
  aks=[k for k in groups if k[0]==a and k[2]==mode and k[3]==fid and k[4]=='HELDOUT'];bks=[k for k in groups if k[0]==b and (k[2]==mode or b=='B1') and k[3]==fid and k[4]=='HELDOUT'];check(len(aks)==3 and len(bks)==(1 if b=='B1' else 3),'hypothesis seed coverage')
  delta={m:statistics.mean(groups[k].result()[m] for k in aks)-statistics.mean(groups[k].result()[m] for k in bks) for m in ['mrr','top10_accuracy']}
  close(row['mrr_delta_seed_mean'],delta['mrr'],'primary '+str(row));close(row['top10_delta_seed_mean'],delta['top10_accuracy'],'primary Top10');check(row['status']=='EXECUTED','primary not executed');check(row['confirmatory_p_value'].startswith('NOT_COMPUTED'),'inappropriate confirmatory p-value');primary.append({'hypothesis':hyp,'augmentation':mode,'scene':scene,**delta})
 check(len({(r['hypothesis'],r['augmentation'],r['scene']) for r in primary})==56,'duplicate/missing primary comparisons')
 detail_seen=set()
 for r in csvrows(ROOT/'results/PER_SAMPLE_RESULTS.csv'):
  k=key(r,False)+(r['sample_id'],);check(k in held_details and k not in detail_seen,'detail coverage/duplicate');detail_seen.add(k)
  for field,value in held_details[k].items():close(r[field],value,'per-sample '+field)
 check(detail_seen==set(held_details),'per-sample table coverage')
 exported=set()
 for r in jl(ROOT/'TRAINING_BASELINE_PREDICTIONS.jsonl'):
  check(r['evaluation_partition']=='HELDOUT','export includes non-heldout');k=key(r,False)+(r['sample_id'],);check(k in export_hashes and k not in exported,'export coverage/duplicate');check(canonical_digest(r)==export_hashes[k],'export changed prediction');exported.add(k)
 check(exported==set(export_hashes),'export incomplete')
 receipt=json.loads((ROOT/'results/EVALUATION_RECEIPT.json').read_text());check(receipt['heldout_prediction_rows']==54600 and receipt['fold_seed_mode_partition_conditions']==1106,'main evaluation receipt counts');check(receipt['scenarios_independent_confirmatory_tests'] is False,'independence overclaim');check(receipt['source_sha256']==sha(ROOT/'evaluation/evaluate_saved.py'),'evaluated source no longer matches receipt')
 return {'status':'PASS_WITH_DOCUMENTED_LIMITATIONS','audit_date':'2026-10-28','audit_scope':'INDEPENDENT_SAVED_PREDICTION_AND_DATA_BOUNDARY_CHECK','independent_implementation':'stdlib metrics; no project evaluator import; no model forward or training','split_sha256':splitsha,'audit_source_sha256':sha(Path(__file__)),'main_evaluator_sha256':sha(ROOT/'evaluation/evaluate_saved.py'),'methods':sorted(methods),'prediction_file_count':len(pred_manifest),'all_partition_prediction_rows':rowtotal,'raw_partition_counts':dict(raw_partitions),'evaluation_groups':len(groups),'heldout_groups':392,'heldout_rows':len(held_details),'unique_queries_per_method_seed_mode':975,'logical_steps':195,'outer_scenarios':7,'candidate_universe':216,'seed_summaries':len(byseed),'method_mode_summaries':len(overall),'stratum_groups_independently_recomputed':len(strata),'primary_hypothesis_scene_mode_rows_recomputed':len(primary),'primary_contrasts':primary,'checks':{'registered_and_mirrored_split_hashes_match':True,'all_predictions_preserve_full216':True,'all_partitions_match_legal_IDs_including_train_r0':True,'no_duplicate_predictions_per_condition':True,'all_five_sampling_queries_grouped':True,'purged_shared_full_window_content_not_cross_roles':True,'seen_labels_derived_from_fold_train_only':True,'mixed_gold_subset_rankings_keep216_and_overlap_disclosed':True,'full_metrics_and_strata_independently_recomputed':True,'seed_scene_and_overall_summaries_independently_recomputed':True,'per_sample_table_and_export_verified':True,'four_primary_hypotheses_seed_means_recomputed':True,'no_confirmatory_p_values':True},'limitations':['PUBLIC_EXPOSED_DEVELOPMENT; not independent external test','Exact original script identity UNKNOWN; full-window purge does not establish absence of shared script/partial-log leakage','Seeds and five samples are repeated observations, not independent attacks','LOSO training sets overlap;7scenarios support descriptive grouped development only','Scene5 has2logical steps; inner validation of fold4 is extremely small','Gold-subset P/F1 counts other-subset true labels outside the current target; subset MRR/Top10 have clearer interpretation','Author-assigned step labels are not observation-verified mechanism annotations'],'prediction_sources':pred_manifest}

def main():
 try:result=audit()
 except Exception as error:
  result={'status':'FAIL','audit_date':'2026-10-28','error_type':type(error).__name__,'error':str(error),'traceback':traceback.format_exc(),'audit_source_sha256':sha(Path(__file__))}
 (ROOT/'results/FINAL_EVALUATION_INDEPENDENT_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 lines=['# 最终评价与数据边界独立复算','',f"审查状态：**{result['status']}**。"]
 if result['status'].startswith('PASS'):
  lines+=['','仅读取本地已保存预测和数据协议，以独立标准库实现重算排名、多标签Precision/Recall/F1及汇总；未调用项目评价器实现，未训练、未进行模型前向、未访问服务器。',f"\n核实{result['prediction_file_count']}个预测文件、{result['evaluation_groups']}个评价分区条件；外层{result['heldout_groups']}条件共{result['heldout_rows']:,}条预测。每个方法/种子/增强恰好覆盖975条保留查询，完整216候选未删减。",f"\n全部{result['stratum_groups_independently_recomputed']}个分层条件、56个种子汇总和20个方法/增强汇总完成独立复算；逐样本表及最终导出与源预测一致。4项主假设×2增强×7场景的56行种子均值差均复算一致，没有确认性p值。",f"\n注册划分及双份实际文件SHA256一致：`{result['split_sha256']}`。训练、验证、保留分区与合法ID完全对应，训练诊断限r0，已识别共享全窗口不跨角色。",'','必须保留的解释限制：','']+['- '+x for x in result['limitations']]
 else:lines+=['',result['error_type']+': '+result['error'],'','FAIL不改写根评价表或预测；应核对上述保存资产后再处理。']
 (ROOT/'reports/FINAL_EVALUATION_INDEPENDENT_AUDIT.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k in ['status','error','evaluation_groups','heldout_rows','stratum_groups_independently_recomputed']},ensure_ascii=False))
 if result['status']=='FAIL':raise SystemExit(1)
if __name__=='__main__':main()
