"""Freeze thirty logical steps from old outputs BEFORE any new mechanism ranking."""
import collections,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def main()->None:
 assert not (ROOT/'DIAGNOSTIC_30_FROZEN_IDS.json').exists()
 ref={x['sample_id']:x for x in load(BASELINES/'datasets/p0_reference.jsonl')}
 emb={x['sample_id']:x for x in load(PREVIOUS/'EMBEDDING_REAL_PREDICTIONS.jsonl') if x['method']=='E1_NATIVE_PREFIX'}
 ce={x['sample_id']:x for x in load(PREVIOUS/'RERANKER_REAL_PREDICTIONS.jsonl') if x['method']=='GTE_RERANKER_EMBEDDING_TOP20'}
 units=collections.defaultdict(list)
 for sid,x in ref.items():units[x['scenario_id'],x['step_id']].append(sid)
 groups=collections.defaultdict(list)
 for key,sids in units.items():
  sid=sorted(sids)[0];x=ref[sid];g={t.split('.')[0] for t in x['ground_truth']};b=bool(g&set(emb[sid]['predictions'][:10]));a=bool(g&set(ce[sid]['predictions'][:10]));hit=bool(g&set(ce[sid]['original_candidates']))
  typ='CE_DEMOTION' if b and not a else 'CE_PROMOTION' if a and not b else 'BOTH_CORRECT' if b and a else 'CANDIDATE_MISS20' if not hit else 'BOTH_FAIL_WITH_CANDIDATE'
  groups[typ].append({**x,'stratum':typ,'logical_step_key':':'.join(key),'representative_rule':'lexicographically first replica; all5replicas retained in full benchmark','old_embedding_top10_hit':b,'old_CE_top10_hit':a,'old_candidate20_hit':hit})
 quotas={'CE_DEMOTION':10,'CE_PROMOTION':6,'BOTH_FAIL_WITH_CANDIDATE':6,'BOTH_CORRECT':4,'CANDIDATE_MISS20':4};selected=[];scenes=collections.Counter();scripts=collections.Counter();actual={}
 for typ,quota in quotas.items():
  available=list(groups[typ]);chosen=[]
  while available and len(chosen)<quota:
   x=min(available,key=lambda x:(scenes[x['scenario_id']],scripts[x['simulation_id']],digest({'seed':'MECHANISM01_SELECTION','sample_id':x['sample_id']})))
   available.remove(x);chosen.append(x);scenes[x['scenario_id']]+=1;scripts[x['simulation_id']]+=1
  selected.extend(chosen);actual[typ]=len(chosen)
 if len(selected)<30:
  used={x['logical_step_key'] for x in selected};left=[x for g in groups.values() for x in g if x['logical_step_key'] not in used]
  while len(selected)<30:
   x=min(left,key=lambda x:(scenes[x['scenario_id']],scripts[x['simulation_id']],digest(x['sample_id'])));left.remove(x);selected.append(x);scenes[x['scenario_id']]+=1;scripts[x['simulation_id']]+=1
 assert len(selected)==len({x['logical_step_key'] for x in selected})==30
 save('DIAGNOSTIC_30_FROZEN_IDS.json',{'scope':'EXPOSED_DEVELOPMENT_DIAGNOSTIC','selection_source':'frozen previous V2 E1 and CE Embed20 only','new_mechanism_predictions_seen':False,'target_quotas':quotas,'available_by_stratum':{k:len(v) for k,v in groups.items()},'realized_initial_quotas':actual,'fallback':'if shortage, fill from all remaining strata by scene/simulation balance then SHA256','scene_counts':dict(scenes),'sample_ids':[x['sample_id'] for x in selected],'logical_step_keys':[x['logical_step_key'] for x in selected],'cases':selected,'selection_source_sha256':sha256(Path(__file__))})
 csvout('DIAGNOSTIC_30_DEPENDENCY_AUDIT.csv',[{'sample_id':x['sample_id'],'logical_step':x['logical_step_key'],'scenario':x['scenario_id'],'simulation':x['simulation_id'],'variant':x.get('variant_id'),'stratum':x['stratum'],'parent_techniques':'|'.join(sorted({t.split('.')[0] for t in x['ground_truth']})),'multi_label':len({t.split('.')[0] for t in x['ground_truth']})>1,'script_dependence':'same scenario/variant is dependence proxy; exact script identity NOT independently established','independent_test':False} for x in selected])
 md('DIAGNOSTIC_30_SELECTION_PROTOCOL.md',f'''# 30逻辑步骤冻结协议

先按scenario+step聚合195个逻辑步骤，每组用字典序首个查询作为诊断代表；全量评价仍保留全部5查询。只依据上一轮冻结的E1和CE Embed20结果分层，不看本轮新预测。优先各层目标10/6/6/4/4，每次选当前出现最少的scene、再最少simulation，再固定SHA256破同分。实际层数与不足替代规则全部保存在ID JSON。不得在新结果后换样。

实际共30个不同逻辑步骤，场景计数{dict(scenes)}。7场景覆盖情况按真实记录，不制造独立执行。variant/simulation是脚本依赖代理，未核验精确脚本同一性。诊断集EXPOSED_DEVELOPMENT_DIAGNOSTIC，基于旧结果分层会产生选择偏差，不能报告其总体准确率代表全部P0。

Gold只供选取分层和独立评价/分析；生成器只接收预测日志。盲审包另用匿名packet_id，隐藏Gold、层别、模型名次和sample_id；管理映射与审查包分离。独立人工审查PENDING不阻断技术分类。''')
 print({'selected':30,'scenes':dict(scenes),'strata':actual})
if __name__=='__main__':main()
