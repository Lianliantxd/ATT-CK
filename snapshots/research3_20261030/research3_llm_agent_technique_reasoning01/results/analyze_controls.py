"""Post-hoc descriptive scene-cluster analysis; never a held-out test."""
import csv, hashlib, itertools, json, random, statistics
from pathlib import Path
import numpy as np
from reportlab.graphics.shapes import Drawing, String, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF, renderPM
from reportlab.lib import colors

R=Path(__file__).resolve().parents[1]
O=R/'analysis-output'; (O/'figures').mkdir(parents=True,exist_ok=True)
B=R.parent/'research3_technique_strong_baselines_generalization02'
ref={x['sample_id']:x for x in map(json.loads,(B/'datasets/p2_v2/reference_sampled.jsonl').open())}
pred=list(map(json.loads,(R/'experiments/deterministic_controls_predictions.jsonl').open()))
methods=list(dict.fromkeys(x['condition'] for x in pred)); scenes=sorted({v['scenario_id'] for v in ref.values()})
vals={}
for x in pred:
 g=set(ref[x['sample_id']]['ground_truth']);p=x['predictions'];r=next((i+1 for i,t in enumerate(p) if t in g),None)
 vals[x['sample_id'],x['condition']]={'top1':float(bool(g.intersection(p[:1]))),'top10':float(bool(g.intersection(p[:10]))),'mrr':1/r if r else 0.}
rows=[]
for m in methods:
 for s in scenes:
  ids=[k for k,v in ref.items() if v['scenario_id']==s]
  rows.append({'method':m,'scenario':s,'n':len(ids),**{k:statistics.mean(vals[i,m][k] for i in ids) for k in ['top1','top10','mrr']}})
with (O/'scene_metrics.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
contrasts=[]; rng=np.random.default_rng(20261027)
for budget in ['S','M']:
 a='ADAPTIVE_HEURISTIC_'+budget;b='STATIC_BM25_'+budget
 for metric in ['top1','top10','mrr']:
  sums=np.array([sum(vals[i,a][metric]-vals[i,b][metric] for i in ref if ref[i]['scenario_id']==s) for s in scenes])
  ns=np.array([sum(v['scenario_id']==s for v in ref.values()) for s in scenes]);point=float(sums.sum()/ns.sum())
  picks=rng.integers(0,len(scenes),(20000,len(scenes)));boot=sums[picks].sum(axis=1)/ns[picks].sum(axis=1)
  signstats=[abs(float((sums*np.array(signs)).sum()/ns.sum())) for signs in itertools.product([-1,1],repeat=len(scenes))]
  p=sum(t>=abs(point)-1e-12 for t in signstats)/len(signstats)
  scene_delta=sums/ns
  contrasts.append({'adaptive':a,'static':b,'metric':metric,'execution_weighted_delta':point,'scene_macro_delta':float(scene_delta.mean()),'scene_delta_sd':float(scene_delta.std(ddof=1)),'cluster_percentile95_low':float(np.quantile(boot,.025)),'cluster_percentile95_high':float(np.quantile(boot,.975)),'exact_scene_signflip_p':p,'clusters':7,'bootstrap_draws':20000,'seed':20261027})
# Six exploratory comparisons; Holm controls this family only under stated exchangeability.
order=sorted(range(len(contrasts)),key=lambda i:contrasts[i]['exact_scene_signflip_p']);prev=0
for j,i in enumerate(order):
 prev=max(prev,min(1,(len(order)-j)*contrasts[i]['exact_scene_signflip_p']));contrasts[i]['holm_p']=prev
(O/'statistics.json').write_text(json.dumps({'scope':'EXPLORATORY_EXPOSED_DEV_ONLY','primary_descriptive_question':'Does adaptive heuristic improve Top10 over static BM25 at each equal acquisition cap?','formal_preregistration':False,'seed_repeats':1,'contrasts':contrasts},indent=2))
table='|Condition|Top-1|Top-10|MRR|\n|---|---:|---:|---:|\n'
for m in methods:
 table+=f"|{m}|"+'|'.join(f'{statistics.mean(vals[i,m][k] for i in ref):.6f}' for k in ['top1','top10','mrr'])+'|\n'
def chart(name,title,labels,data,ylab,ymax):
 d=Drawing(760,340);d.add(Rect(0,0,760,340,fillColor=colors.white,strokeColor=None));bc=VerticalBarChart();bc.x=65;bc.y=80;bc.width=660;bc.height=210;bc.data=data;bc.categoryAxis.categoryNames=labels;bc.categoryAxis.labels.angle=25;bc.categoryAxis.labels.fontSize=8;bc.categoryAxis.labels.dy=-12;bc.valueAxis.valueMin=0;bc.valueAxis.valueMax=ymax;bc.valueAxis.valueStep=ymax/5;bc.valueAxis.labels.fontSize=8;bc.bars[0].fillColor=colors.HexColor('#346895');bc.bars[1].fillColor=colors.HexColor('#ad623b') if len(data)>1 else colors.HexColor('#346895');d.add(bc);d.add(String(65,316,title,fontSize=13));d.add(String(65,299,ylab,fontSize=9));d.add(String(65,15,'Exposed related development data; one deterministic run; no independent-test claim.',fontSize=8));renderPDF.drawToFile(d,str(O/'figures'/name))
 try: renderPM.drawToFile(d,str((O/'figures'/name).with_suffix('.png')),fmt='PNG',dpi=140)
 except Exception as e: print('PNG renderer unavailable:',type(e).__name__,str(e)[:120])
chart('figure-01-controls.pdf','Static and adaptive retrieval controls: 385 P2 execution-steps',['None','Static S','Static M','Fixed S','Fixed M','Adaptive S','Adaptive M'],[[statistics.mean(vals[i,m]['top10'] for i in ref) for m in methods]],'Top-10 hit fraction; point estimates (no error bars)',.4)
cand=list(csv.DictReader((R/'CANDIDATE_RECALL_UPPER_BOUNDS.csv').open()));cs=[x for x in cand if x['protocol']=='P0']
chart('figure-02-candidate-ceiling.pdf','Lexical candidate ceiling: 975 P0 queries',['Top20','Top50','Top100'],[[float(x['candidate_hit_at_k']) for x in cs],[float(x['all_gold_recalled_fraction']) for x in cs]],'Blue: any Gold included; brown: all Gold included; point estimates',1.)
(O/'analysis-report.md').write_text('# 已暴露开发集的严格分析\n\n主问题：相同新增证据上限下，动态启发式能否超过静态BM25？两预算均以Top10为描述主指标，Top1/MRR为并列辅助。不是LLM Agent测试。\n\n'+table+'\n385个执行—步骤重复覆盖195个逻辑步骤、34执行、7场景；不把385视作独立实验。一次确定性运行，无多seed方差。按场景汇总并保留全部关联样本；事后20,000次场景簇bootstrap仅反映7场景组合敏感性。\n\n## Claim Candidates\n\n- Claim: 当前动态启发式没有稳定超过静态检索。\n  - Source evidence: statistics.json、scene_metrics.csv及完整2695条预测。\n  - Allowed wording: S下点估计较低，M下Top10略低但Top1/MRR略高，没有一致优势。\n  - Forbidden stronger wording: 所有Agent无效、静态方法普遍优越、独立泛化已证明。\n  - Uncertainty: 仅7关联开发场景，一次冻结策略，实际消耗预算不完全相同。\n  - Next check: 合法语义召回及有效固定LLM受控配对。\n  - Decision: keep\n\n- Claim: P0 Top20词汇候选的任何Gold覆盖只有38.9744%。\n  - Source evidence: CANDIDATE_RECALL_UPPER_BOUNDS.csv。\n  - Allowed wording: 限定该候选的完美重排Top10仍不可能超过38.9744%。\n  - Forbidden stronger wording: 所有语义检索均受此上限约束、证明LLM推理无效。\n  - Uncertainty: 仅当前冻结字符检索及合法P0。\n  - Next check: 更好的候选召回。\n  - Decision: keep\n',encoding='utf8')
stats='\n'.join(f"- {c['adaptive']}−{c['static']} {c['metric']}: Δ={c['execution_weighted_delta']:.6f}; 95% cluster interval [{c['cluster_percentile95_low']:.6f}, {c['cluster_percentile95_high']:.6f}]; scene macro Δ±SD={c['scene_macro_delta']:.6f}±{c['scene_delta_sd']:.6f}; exact signflip p={c['exact_scene_signflip_p']:.6f}, Holm p={c['holm_p']:.6f}." for c in contrasts)
(O/'stats-appendix.md').write_text('# 统计附录\n\n'+stats+'\n\nBootstrap重抽7场景并将簇内执行—步骤一起保留，分母随抽取簇大小变化。区间为事后描述性敏感性分析；7簇过少、场景并非随机独立抽样，因此不作总体保证。符号翻转枚举128种、双侧，以簇内配对差和为统计量；要求场景差分交换对称且场景独立，当前不能充分确认。六比较Holm校正仅为探索信息，不生成显著性或泛化结论。未使用t检验，不声称正态；不因正态性检验未拒绝就认定正态。Δ是原始效应量；场景SD不是随机种子SD。LLM小样本且缺失不均，禁止显著性与收益结论。\n',encoding='utf8')
(O/'figure-catalog.md').write_text('# 图目录\n\n1. figures/figure-01-controls.pdf：展示全部七条件Top10。数据来自2695条真实预测；无误差棒，完整差值区间在stats-appendix。S动态低于静态、M接近，故不支持扩大动态策略。不能解读为LLM Agent能力。\n2. figures/figure-02-candidate-ceiling.pdf：P0 Top20/50/100候选任何Gold与全部Gold覆盖。上限随候选增多而提高，说明须分离召回缺失和排序错误。无误差棒，无模型推理结果；不能移作Embedding成绩。\n',encoding='utf8')
print(json.dumps({'contrasts':contrasts,'predictions':len(pred),'figures':2},indent=2))
