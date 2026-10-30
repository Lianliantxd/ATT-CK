"""Final evidence bundle after the explicitly authorized GPU experiment."""
import csv,json,re,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
from reports.build_report import table,pct
def read(n:str)->list[dict]:return list(csv.DictReader((ROOT/n).open()))
def main()->None:
 s=json.loads((ROOT/'results/NEURAL_EVALUATION_SUMMARY.json').read_text());run=json.loads((ROOT/'results/gpu/GPU_RUN_COMPLETE.json').read_text());sanity=json.loads((ROOT/'results/gpu/SCORING_SANITY.json').read_text());env=json.loads((ROOT/'results/gpu/manifests/ACTUAL_ENVIRONMENT_AND_DOC_TOKENS.json').read_text());m={r['method']:r for r in read('MECHANISM_BASELINE_RESULTS.csv')};stats=read('results/ALL_CPU_GPU_CONTRASTS.csv');tokens=read('results/ACTUAL_TOKEN_SUMMARY.csv');ks=['K2_DESCRIPTION_16_1','MECHANISM_CARD'];views=['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL']
 def metric(model:str,v:str,k:str)->str:
  r=m[f'{model}__{v}__{k}'];return f"Top1 {pct(r['top1_accuracy'])}，Top10 {pct(r['top10_accuracy'])}，MRR@10 {float(r['mrr']):.4f}"
 def delta(model:str,k:str,v:str='LITERAL',b:str='RAW')->str:
  x=next(x for x in stats if x['method']==f'{model}__{v}__{k}' and x['baseline']==f'{model}__{b}__{k}' and x['metric']=='top10');return f"Top10差 {float(x['delta_mean'])*100:+.2f}个百分点，95%CI[{float(x['CI95_low'])*100:.2f}, {float(x['CI95_high'])*100:.2f}]，Holm(292) p={float(x['Holm_p_all292']):.4f}"
 neural=[m[f'{model}__{v}__{k}'] for model in ['GTE_EMBEDDING','GTE_CE'] for k in ks for v in views]
 nt=table([{'方法':r['algorithm'],'日志':r['input_view'],'知识':r['knowledge'],'N':r['n_records'],'Top1':pct(r['top1_accuracy']),'Top10':pct(r['top10_accuracy']),'MRR@10':f"{float(r['mrr']):.4f}"} for r in neural],['方法','日志','知识','N','Top1','Top10','MRR@10'])
 ttable=table(tokens,['tokenizer','view','N','mean','median','min','max','limit'])
 inputstats=[r for r in stats if r['contrast']=='NEURAL_INPUT'];positive=[r for r in inputstats if float(r['delta_mean'])>0 and float(r['Holm_p_all292'])<.05];negative=[r for r in inputstats if float(r['delta_mean'])<0 and float(r['Holm_p_all292'])<.05]
 # A positive development contrast is reported as such, never upgraded to independent algorithmic contribution.
 gaintext='存在通过本组探索性多重校正的正向表示对比，必须逐项结合原始视图、知识与Token差异解释。' if positive else '本组神经表示对比没有获得经292项联合Holm校正后显著的正向增益。'
 findings='\n'.join(f"- {model} / {k}：RAW {metric(model,'RAW',k)}；Literal {metric(model,'LITERAL',k)}；{delta(model,k)}；关系相对Literal：{delta(model,k,'LITERAL_PLUS_RELATIONS','LITERAL')}。" for model in ['GTE_EMBEDDING','GTE_CE'] for k in ks)
 runtime=f"GPU0 A40；总实验墙钟 {run['total_seconds']:.2f}秒；Embedding {run['embedding_forward_batches']}批；CE {run['CE_unique_pairs']}个去重候选对、{run['CE_batches']}批，另8次公开sanity pair；峰值allocated {run['GPU_peak_allocated_bytes']/1048576:.2f}MiB、reserved {run['GPU_peak_reserved_bytes']/1048576:.2f}MiB。"
 sanitytext=f"固定配置与新前向确认单输出 num_labels=1，断言每批logits形状(B,1)。两组预登记相关/无关对均按高logit正确区分，batch与single最大差 {sanity['max_batch_single_delta']}；logits分别为{sanity['batched_logits']}。模型处于eval。只验证这4对，不宣称全部领域分数校准或完整CAM批次不变性。没有根据CAM成绩选择方向，没有实际运行SentenceTransformers wrapper。"
 ng=f'''# 授权GPU主实验与严格分析

主实验真实完成：2固定模型×4视图×2知识=16条件，每条件975查询，共15600预测；合计CPU65+GPU16=81条件、78975条预测。所有Gold只在本地后评价读取。其余24神经条件不在此次授权内，保持NA。

{nt}

{findings}

{gaintext} 正向显著表示检验{len(positive)}项，负向显著{len(negative)}项（Top10与MRR分别计数）。完整原始效应、SD、CI和p见ALL_CPU_GPU_CONTRASTS，不能按结果筛选最优条件作为确认性结论。

## 可比性与预算

Embedding对全部216技术排序。CE每条件使用**完全相同的旧canonical E1 Top20**，而非分别用新视图重取候选；候选Hit20={s['candidate_hit20']:.6f}、Recall20={s['candidate_recall20']:.6f}，构成CE最终命中的候选限制。CE与全空间检索比较是整体管线差异，不能全归因于评分器。旧原始E1排名与候选生成文本不等于本轮RAW。

四视图共享选定原生事实；冻结日志2000 UTF8 bytes、知识1000 bytes，不再按结果改前缀。实际Token已测并均未超过日志2048/知识1024；最大知识Token {max(x['tokens'] for x in env['knowledge_actual_tokens'])}。Tokenizer truncation=False，无运行期静默截断。**同一上限不等于相同实际Token长度**；Literal的字段清洗、UNKNOWN和结构标签会改变信息表达、Token组成与长度，因此不能单独归因机制推理。有效原生事件与选取/截断位置见INPUT_BUDGETS、MECHANISM_SOURCE_TRACE和MECHANISM_LITERAL的char_range；所有模型共用这些冻结输入。

{ttable}

机制卡与K2版本相同，但卡片可取完整知识后部，而原描述是前缀；标题、术语和可见知识分配仍有混杂。CPU已执行visible-prefix与同词频乱序控制；神经模型本次只授权两知识条件，未执行这些扩展控制，不能声称神经卡片收益已排除词汇因素。

## 评分语义

{sanitytext}

历史5850条CE结果按原始ID/分数可重建。跨候选池同对分数最大差0来自缓存复用；新sanity批次测试是另一项有限范围检查，不能将二者混称为全量独立重复实验。上游截取的领域证据损失仍不能排除。

## 统计

神经分析问题在读取新GPU指标前登记于GPU_ANALYSIS_REGISTRATION：20组表示/知识、32组同视图神经对词汇、8组CE对Embedding，共60对比×Top10/MRR=120检验。与既有172项联合Holm校正292项；CPU原172项校正独立保留用于追溯。195个scenario+step簇，各5查询先平均；seed42，2000次bootstrap、5000次双侧signflip加1校正，不假设正态；一套确定性权重，无跨seed训练重复。脚本/场景依赖仍可能违反交换性，全部P0 EXPOSED_DEV，p和CI只作条件开发分析。

## 资源与权限

{runtime} 新项目同名venv只读链接旧依赖；2模型权重SHA256与冻结记录相同；运行前四文件哈希逐项一致。无模型下载、无新增LLM、无Gold上传。新增磁盘实测见REMOTE_FINAL_RESOURCE_RECEIPT。授权范围2小时/156000候选对/1GB，完成后未扩大实验。

## 科研判断

NO-GO当前组合直接作为独立算法贡献。即使某个开发条件有数值提高，仍需排除清洗、Token与知识信息分配，完成独立证据审查和外部评价。BM25关系/动作标签没有文档posting，是评分接口未生效；神经模型可接收这些文本，但新增标签不自动成为合法技术约束。没有真实人工机制Gold，不能把原生引用一致性当语义支持准确率，也不能从技术错分直接定位“证据不可观察”。当前领域适配、标签可观测性和细粒度机制绑定仍是待区分的假设，本轮不启动训练/新规则。
'''
 md('reports/GPU_MAIN_EXPERIMENT_RESULTS.md',ng)
 # Upgrade the forensic facts while retaining old evidence and exact caveats.
 audit=json.loads((ROOT/'RERANKER_SCORING_VALIDATION.json').read_text());audit.update(runtime_config_or_independent_batch_rescore='NEW_AUTHORIZED_SANITY_VERIFIED_4_PUBLIC_PAIRS_ONLY',num_labels_dimension='runtime config single label and assertions(B,1) on all new CE batches',cross_batch_stability='4 public pairs batch versus single max_delta='+str(sanity['max_batch_single_delta'])+'; not full CAM stability test',new_model_forwards={'embedding_batches':run['embedding_forward_batches'],'CE_batches':run['CE_batches'],'CE_candidate_pairs':run['CE_unique_pairs'],'public_sanity_pair_evaluations':8},new_runtime_sanity=sanity)
 updates={1:('NEW_RUNTIME_EVAL_VERIFIED','新sanity探针eval=true；历史eval仍基于冻结源码'),5:('RUNTIME_SINGLE_OUTPUT_VERIFIED','固定config单标签；所有新批次断言logits(B,1)'),6:('DOCUMENT_AND_PUBLIC_SANITY_SUPPORTED','高logit区分两组预登记相关/无关对；不依CAM方向选择'),8:('SINGLE_OUTPUT_NO_CLASS_SELECTION','只有一维logit，无正负类别切片'),11:('LIMITED_PUBLIC_BATCH_SINGLE_VERIFIED','4公开对batch/single差0；历史同对缓存一致不等于全量独立复测')}
 for c in audit['twenty_checks']:
  if c['item'] in updates:c['status'],c['evidence_limit']=updates[c['item']]
 save('RERANKER_SCORING_VALIDATION.json',audit)
 checks=table([{'项目':x['item'],'检查':x['check'],'状态':x['status'],'边界':x['evidence_limit']} for x in audit['twenty_checks']],['项目','检查','状态','边界'])
 md('CROSS_ENCODER_FORENSIC_AUDIT.md',f'''# Cross-Encoder实现与适配审计（授权主实验后）

历史保存分数/索引/排序未发现足以解释候选池扩大的实现错误。{sanitytext}

{checks}

官方[固定revision模型卡](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base/blob/f7481e6055501a30fb19d090657df9ec1f79ab2c/README.md?code=true)支持Transformers raw logits高值相关评分；[CrossEncoder接口](https://sbert.net/docs/package_reference/cross_encoder/model.html)的单调activation并不要求反转排序。当前实际实现为固定Transformers pair评分，不声称执行了wrapper对照。历史保存记录与新运行配置、sanity分别保留，未修改旧结果。

本轮实际无Tokenizer静默截断，输入前缀/字节分配仍会损失信息。未将域错配、截取、标签可观测性或机制理解中的任一假设当成已确认原因。''')
 p=ROOT/'RERANKER_FAILURE_DIAGNOSIS.md';t=p.read_text().replace('新GPU调用为0。','历史D1—D6仍为离线复算；新授权GPU主实验及sanity另见reports/GPU_MAIN_EXPERIMENT_RESULTS.md。');p.write_text(t)
 p=ROOT/'MECHANISM_EXTRACTION_VALIDATION.md';t=p.read_text().replace('实际模型Token未取得，必须记NA','实际模型Token已通过两种固定tokenizer测量，见results/ACTUAL_TOKEN_SUMMARY.csv；同上限不等于同实际长度');p.write_text(t)
 p=ROOT/'METHOD_FORMAL_PROBLEM.md';t=p.read_text().replace('本轮theta只有冻结CharacterNgramTFIDF、BM25与简单动作/对象Jaccard；未训练新参数，未新增GTE前向','本轮theta包含冻结CharacterNgramTFIDF、BM25、简单动作/对象Jaccard及两种固定GTE前向；未训练新参数');p.write_text(t)
 md('METHOD_RESEARCH_DECISION.md',f'''# GO / NO-GO

主状态：NO_SUPPORTED_ALGORITHMIC_GAIN（未建立独立算法贡献，不等于所有开发差为零）。次状态：MECHANISM_REPRESENTATION_EXECUTED、RERANKER_FAILURE_DIAGNOSED、EXTERNAL_TEST_NOT_READY。

授权主实验已完成，非MODEL_FORWARD_AUTHORIZATION_BLOCKED。{gaintext} 完整量化对比见reports/GPU_MAIN_EXPERIMENT_RESULTS.md及292项统计。当前仍不能将清洗/元字段/不同实际Token或知识可见内容的差异归因于攻击机制推理。关系文本的因果、身份和必要条件没有额外认证；BM25关系标签接口未生效。

NO-GO：继续堆叠现有规则、关系图、Agent、Reflection、RL或DGPR；不将卡片与成熟检索器组合称独立创新。

条件GO：保留IR作证据审查资产，完成已冻结30例的真实独立人审，区分标签不可观察、主体对象绑定与领域排序偏差。若要修正renderer使动作/关系有匹配知识通道，必须作为新工程版本单独冻结，不能回改本轮输入或成绩。若无法证实有独立机制信息，再另立领域对比学习/困难负例适配实验；本轮不自动训练。外部TEST及机制语义评价仍未就绪。
''')
 p=ROOT/'MECHANISM_ERROR_ANALYSIS.md';t=(ROOT/'reports/OFFLINE_SNAPSHOT/MECHANISM_ERROR_ANALYSIS.md').read_text().replace('新GTE/CE机制条件没有授权而未执行，不能以旧RAW输出替代。','本轮GTE/CE主实验已获新授权并实际执行，所有16条件及逐样本/分场景结果另见results/NEURAL_*；不能用旧RAW输入成绩替代。');p.write_text(t+'\n\n'+findings+'\n\n'+gaintext+'\n')
 # Reuse unchanged answers from the frozen offline snapshot; replace only facts changed by actual GPU evidence.
 old=(ROOT/'reports/OFFLINE_SNAPSHOT/R3_ATTACK_MECHANISM_DISCRIMINATION_RESULTS.md').read_text();qa=re.findall(r'^### (\d+)\. ([^\n]+)\n\n(.*?)(?=\n### |\n## |\Z)',old,re.M|re.S);assert len(qa)==36
 changes={1:'历史保存分数/排序未发现明显实现错误；新授权配置和全部CE批次确认单输出(B,1)，4公开对batch/single一致。不能由有限sanity排除所有领域适配问题。',2:'官方高raw logit方向与两组公开相关/无关对一致；未按CAM分数选方向。',6:'K特有输入变化和保存索引错配解释不受保存记录支持；新单输出与4对batch校验已完成。上游截取造成的语义信息损失仍不能排除。',19:'是，Embedding和CE各4视图×2知识，共16条件15600真实预测，每条件975。',20:'新授权已收到并执行；其余3种知识×4视图×2模型=24条件超出授权主实验，保持NA。',21:'；'.join(f'{k}：{delta("GTE_EMBEDDING",k)}' for k in ks)+'。详见完整指标，不能作独立泛化结论。',22:'；'.join(f'{k}：{delta("GTE_CE",k)}' for k in ks)+'。固定同一旧E1Top20，禁止把候选来源变化误当评分收益。',23:'；'.join(f'{model}/{k}：{delta(model,k,"LITERAL_PLUS_RELATIONS","LITERAL")}' for model in ['GTE_EMBEDDING','GTE_CE'] for k in ks)+'。BM25标签接口未生效；任何神经数值变化仍不是关系推理因果认证。',24:'不能完全排除。真实Token已测，四视图长度不同但均低于同上限；清洗、元字段、可见知识与词汇都可能解释差异，CPU控制未穷尽神经模型混杂。',25:'两个固定GTE的描述/卡片实测完整保存；卡片可见内容分配与词汇混杂仍在。CPU同词频乱序复现BM25全排名，不能声称知识结构独立贡献。',28:'历史Top100有750候选内前十失败；本轮CE所有条件同一固定Top20，逐例候选Hit/Recall、Gold排名和相对原池序升降级见NEURAL_CANDIDATE_DIAGNOSTICS。具体语义原因仍不能只由步骤标签确定。',35:'没有建立可信独立新算法贡献。'+gaintext+' 工程IR可保留，机制语义、人审、外部和信息预算混杂尚未解决。',36:'停止堆叠现有机制规则。先完成30例独立证据审查和机制特征与评分通道核验，判断是否存在未被词汇解释的机制信息；若无，再单独立项领域适配/困难负例训练，本轮不自动启动。'}
 answers='\n\n'.join(f'### {i}. {q}\n\n{changes.get(int(i),a.strip())}' for i,q,a in qa)
 cpu_table=table([{'方法':r['algorithm'],'视图':r['input_view'],'Top10':pct(r['top10_accuracy']),'MRR':f"{float(r['mrr']):.4f}"} for r in m.values() if r['algorithm'] in ['char','bm25'] and r['knowledge']=='K2_DESCRIPTION_16_1' and r['input_view'] in views],['方法','视图','Top10','MRR'])
 main=f'''---
type: results-report
date: 2026-10-28
experiment_line: attack_mechanism_discrimination
round: 01
purpose: mechanism-and-reranker-diagnosis
status: completed_authorized_main
source_artifacts: [reports/analysis-output/analysis-report.md, reports/analysis-output/stats-appendix.md, reports/analysis-output/figure-catalog.md, reports/analysis-output/provenance.json]
linked_experiments: [manifests/EXPERIMENT_REGISTRATION.json, manifests/GPU_ANALYSIS_REGISTRATION.json]
linked_results: [MECHANISM_BASELINE_RESULTS.csv, results/NEURAL_BASELINE_RESULTS.csv, RERANKER_SCORING_VALIDATION.json]
---
# R3 攻击行为机制表示与ATT&CK技术判别 / Round 01 / 2026-10-28

## 执行结论

主状态 **NO_SUPPORTED_ALGORITHMIC_GAIN**，表示当前没有建立独立算法贡献，不宣称所有开发对比均为零。机制表示已实现，CPU65条件63375预测、授权GPU16条件15600预测，总81条件78975真实预测，所有975查询均保留。{gaintext} 独立机制人审仍PENDING，EXTERNAL_TEST_NOT_READY。实验完成后未扩大模型、LLM或训练范围。

最重要的可确认结论是：历史CE候选扩大导致的退化来自竞争集合变化，而非保存记录中同候选分数随K改变。新运行补齐单输出配置与有限batch sanity检查；仍不能据此将失败唯一归因于缺少攻击机制理解。工程引用可追溯不等于语义理解已认证。

## 实验身份、问题与协议

核心问题是同日志/同知识/同固定模型/同预算上限下，显式主体动作对象状态结果关系是否改善技术排名。P0为EXPOSED_DEV：195逻辑步骤×5查询、7场景、34模拟标识、216父技术；295/975（30.26%）查询为多标签；P1/P2=RELATED_DEV，不是独立TEST。752项继承资产/旧评价器和模型预测保持冻结。DGPR Full已REJECT，本轮没有DGPR、RL、反思、多Agent系统或新训练。

16.1知识203项有描述、13缺描述保留，不用203类替代216主空间。生成器只读取已清洗合法原生字段，Gold不进提取器/模型；传感器Txxxx注释等长掩码。当前uid0不推提权，exit0不当成功，同PID不认证生命周期，时间近不推因果，知识兼容不等于观察支持。

日志2000 bytes/知识1000 bytes，实际Token实测且未越2048/1024，但实际长度不相等；共享原生观察也进一步截取，所以不直接把历史27.79%或上一轮29.23%与本轮RAW相减。Embedding全216；CE统一旧E1Top20候选，固定候选Hit20={s['candidate_hit20']:.4f}。完整Token表和输入哈希见GPU主实验报告。

## Cross-Encoder实现诊断

历史5850条件全部可按ID/logit重建，跨池/20/50/100交集同对最大差0（缓存复用）。{sanitytext}

Embedding Top100有101/975完全召回缺失、750/975候选有Gold却最终前十失败。扩大池时T1204、T1601、T1592等高分非步骤Gold候选挤入；这只说明相对步骤标签排名错误，不证明这些技术在某事件中绝无发生。上游知识65项曾截断、领域迁移、标签可观测性和机制绑定都是未完全排除的因素。没有评分反转修复，也不把工程修复当创新。

## 全量结果与主要发现

词汇检索在原描述下：

{cpu_table}

CHAR Literal下降，BM25 Literal数值提升，但95%逻辑步骤CI跨0；当前检索器没有一致表示增益。BM25新增关系/动作标签不在文档posting，关系通道未生效，不能据零差否证关系语义。LiteralMechanismMatching Top10=4.31%。

神经主实验：

{nt}

{findings}

机制卡部分数值变化仍有标题、词汇与完整源知识后部提取的混杂；CPU后注册prefix/乱序控制16条件与主49条件分开登记。同词频乱序使BM25四视图975例完整216排名全部一致，说明该模型没有利用卡片词序结构。神经扩展知识控制本次未授权，不能假定同样机制解释已验证。

## 统计验证

在读取GPU指标前登记60对比×2指标=120新检验，与CPU172项合为292项统一Holm。195逻辑步骤内5查询先平均，2000次bootstrap95%CI、5000次signflip，seed42；完整效应mean/SD/CI/原始p和校正p均交付。单固定权重协议无训练seed重复，脚本/场景依赖尚在，交换性假设可能不满足；统计仅属曝光开发集条件分析，不支持泛化和机制因果结论。

## 图及解释

![CPU表示对照]({ROOT}/reports/analysis-output/figures/figure-01-mechanism.png)

图1：Literal效果随检索器变化，当前CPU结果不支持稳定机制收益；BM25关系通道未生效。

![知识混杂]({ROOT}/reports/analysis-output/figures/figure-02-knowledge-control.png)

图2：可见知识分配/词频与词序控制影响成绩，最高柱不能自动解释为新知识推理。

![神经表示对照]({ROOT}/reports/analysis-output/figures/figure-03-neural.png)

图3：同固定模型和候选协议的真实16条件开发结果。每柱975查询，是描述统计；区间、脚本依赖和多重检验见统计附录。

## 30例、失败归因与语义限制

30个不同逻辑步骤在新输出前按旧结果固定：10降级/6提升/6共同失败/4共同正确/4召回失败，覆盖7场景；全部属于EXPOSED_DEVELOPMENT_DIAGNOSTIC。34510原生字段、997关系、1866卡片词形源回查和12项安全不变量通过，这是工程一致性，不是机制语义准确率。逐案native字段与CPU/神经排名见diagnostic_30；不根据新结果替换样本或补Gold规则。

盲审包隔离Gold/分层/模型结果，真实人审30例均PENDING。因此证据不可观察、主体对象歧义、机制支持与因果/成功语义错误不能由步骤Gold直接裁定；保留UNRESOLVED，不制造机制Precision/Recall。

## 权限、环境与外部数据

用户明确批准4个冻结文件9597914字节上传指定新项目，创建项目同名venv，只读复用两模型与依赖。4文件和2权重哈希均已核验；Gold只在本地。{runtime} 新增磁盘及权限收据完整保存；无新模型下载/LLM、无旧环境修改。

外部资格实际核查本地Mordor APT29的26步派生标签与元数据。原生日志/原计划、许可、脚本独立性和旧ID映射尚未齐备，且副本已在其他项目曝光，不能称独立TEST。ExCyTIn现有图QA不匹配原生日志技术步骤任务。网络访问失败未被误写为数据不存在；未下载大归档。CONV-A01及受限PwnKit步骤/别名正文仍未读取。

## 决策、信念更新与下一步

GO仅限保留可追溯IR作诊断资产；NO-GO当前组合作独立算法创新。评分维度和有限batch疑点已得到新实测澄清；这增强了“保存/排序错误不足以解释退化”的判断，却没有证明领域瓶颈一定是机制推理。新增关系符号需要合法知识对应与有效评分接口，不能靠结构外观证明贡献。

下一步由真实独立30例审查区分可观测性与排序问题；若要修正renderer/知识适配，另冻结工程版本，不能回改本轮输入。只有排除信息预算和词汇混杂后才继续机制判别；否则另立领域对比学习/困难负例适配。本轮完成后停止，不自动启动后续训练。

## 36项逐条回答

{answers}

## 复现与交付索引

主结果MECHANISM_BASELINE_RESULTS汇总81条件；CPU主47775预测、posthoc15600、GPU15600逐行预测分别保留。GPU_MAIN_EXPERIMENT_RESULTS提供完整新实测、Token、配置、资源与比较边界。ALL_CPU_GPU_CONTRASTS保留292项统计，NEURAL_PER_SAMPLE/SCENARIO/CANDIDATE_DIAGNOSTICS和30例表提供错误分析。源码、来源、版本和哈希均在各目录及manifests。最终完整性见FINAL_VALIDATION与DELIVERY_SHA256；授权前报告仅作为OFFLINE_SNAPSHOT历史记录。
'''
 md('R3_ATTACK_MECHANISM_DISCRIMINATION_RESULTS.md',main)
 ao='reports/analysis-output/'
 md(ao+'analysis-report.md',ng+'''\n## Claim candidates与表述边界

- 保存层候选分数随K不变：来源CANDIDATE_SCORE_CONSISTENCY，允许称缓存记录一致，禁止称全量独立运行稳定性；keep。
- 新scalar输出和公开对方向正确：来源OFFICIAL_FIXED_CONFIG/SCORING_SANITY，允许称4对有限探针通过，禁止称领域语义正确已证实；keep。
- 机制表示效果：来源完整16条件及292项统计，允许逐项报告曝光开发效应，禁止称新独立泛化/机制因果；weaken。
- 知识卡结构贡献：CPU词序控制可复现BM25结果，神经同类扩展控制未运行，不能宣称深层知识约束贡献；revise。
- 字段/关系源一致：34510字段/997关系可追溯，独立人审PENDING，禁止把工程一致当语义100%；weaken。
''')
 md(ao+'stats-appendix.md','# 统计附录\n\n'+ng.split('## 统计')[1].split('## 资源与权限')[0]+'\n\n完整292检验见results/ALL_CPU_GPU_CONTRASTS.csv。正向或负向报告均保留，不事后删除不利结果。实际Token逐视图表见results/ACTUAL_TOKEN_SUMMARY.csv。\n')
 p=ROOT/(ao+'figure-catalog.md');t=p.read_text().split('\nfigure-03-neural.pdf/svg/png：')[0];p.write_text(t+'\nfigure-03-neural.pdf/svg/png：真实固定GTE Embedding/CE的4日志×2知识Top10；数据NEURAL_BASELINE_RESULTS，刻度一致，无误差条。CE所有视图统一旧Top20，与Embedding全216不可解释为纯模型能力差。观察同模型表示变化；按292联合检验与Token信息预算边界解释，不选择最高柱宣称泛化。\n')
 save(ao+'provenance.json',{'source_files':[{'path':str(ROOT/n),'sha256':sha256(ROOT/n)} for n in ['MECHANISM_BASELINE_PREDICTIONS.jsonl','experiments/KNOWLEDGE_CONTROL_PREDICTIONS.jsonl','results/gpu/NEW_EMBEDDING_PREDICTIONS.jsonl','results/gpu/NEW_RERANKER_PREDICTIONS.jsonl','frozen_inputs/PREDICTION_INPUTS.jsonl','attack_knowledge/KNOWLEDGE_TEXTS.json','experiments/evaluate_gpu.py','manifests/GPU_ANALYSIS_REGISTRATION.json']],'Gold_path':str(BASELINES/'datasets/p0_reference.jsonl'),'Gold_host':'LOCAL_ONLY','new_GPU_experiments':1,'GPU_runtime':run,'new_LLM_calls':0,'new_model_downloads':0,'split':'P0_EXPOSED_DEV'})
 p=ROOT/'MODEL_FORWARD_AUTHORIZATION_REQUEST.md';t=(ROOT/'reports/OFFLINE_SNAPSHOT/MODEL_FORWARD_AUTHORIZATION_REQUEST.md').read_text();p.write_text('> 当前状态：用户已明确批准并已完成推荐主实验。以下保留原始请求；全知识可选方案未批准。实际授权见manifests/NEW_GPU_AUTHORIZATION.json。\n\n'+t)
 save('results/FINAL_RESEARCH_DECISION.json',{'main_state':'NO_SUPPORTED_ALGORITHMIC_GAIN','secondary':['MECHANISM_REPRESENTATION_EXECUTED','RERANKER_FAILURE_DIAGNOSED','EXTERNAL_TEST_NOT_READY'],'positive_significant_neural_input_tests':len(positive),'negative_significant_neural_input_tests':len(negative),'no_independent_algorithm_contribution':True,'human_reference':'PENDING','no_external_test':True,'no_followup_training_started':True})
 print('Generated final authorized GPU evidence bundle and36 updated answers')
if __name__=='__main__':main()
