"""Assemble evidence-backed Chinese delivery. Does not run models or read raw archives."""
import csv, hashlib, json, re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def write(p,t): (R/p).write_text(t.rstrip()+'\n',encoding='utf8')
def table(rows,keys,labels=None):
 s='|'+'|'.join(labels or keys)+'|\n|'+'|'.join('---' for _ in keys)+'|\n'
 for row in rows:s+='|'+'|'.join(str(row.get(k,'N/A')) for k in keys)+'|\n'
 return s
def outcsv(p,rows):
 with (R/p).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
models=['Alibaba-NLP/gte-modernbert-base','Qwen/Qwen3-Embedding-0.6B','BAAI/bge-m3','jinaai/jina-embeddings-v5-text-small']
blocked='NEURAL_MODEL_EXECUTION_BLOCKED';reason='No complete cached weights/tokenizer; new weight downloads NOT_AUTHORIZED'
base=[dict(model=m,protocol=p,status=blocked,N_planned=n,N_executed=0,top1='N/A',top5='N/A',top10='N/A',precision_at_5='N/A',recall_at_5='N/A',mrr='N/A',micro_f1_at_5='N/A',inference_seconds='N/A',model_memory_bytes='N/A',actual_input_tokens='N/A',truncation_fraction='N/A',failed_samples='N/A',blocker=reason) for m in models for p,n in [('P0',975),('P1',975),('P2_SAMPLED',385)]]
outcsv('EMBEDDING_BASELINE_RESULTS.csv',base)
for p in ['EMBEDDING_PREDICTIONS.jsonl','RERANKER_PREDICTIONS.jsonl']:write(p,'')
# Keep genuinely empty JSONL, rather than a fake status prediction.
for p in ['EMBEDDING_PREDICTIONS.jsonl','RERANKER_PREDICTIONS.jsonl']:(R/p).write_bytes(b'')
outcsv('EMBEDDING_CANDIDATE_RECALL.csv',[dict(model=m,protocol=p,k=k,status=blocked,N_executed=0,candidate_hit='N/A',candidate_recall='N/A',all_gold_covered='N/A',blocker=reason) for m in models for p in ['P0','P1','P2_SAMPLED'] for k in [20,50,100]])
outcsv('EMBEDDING_INPUT_ABLATION.csv',[dict(model=m,view=v,selection=s,aggregation=a,status=blocked,N_executed=0,max_log_regex_proxy_tokens=2048,actual_model_tokenizer='UNAVAILABLE',top1='N/A',top10='N/A',mrr='N/A',qualification='INPUTS_PREPARED_NOT_MODEL_RESULTS') for m in models for v in ['V0_NATIVE','V1_NATIVE_FIELDS','V2_CHUNKS','V3_SOURCES'] for s in ['PREFIX','WINDOW'] for a in (['MAX','MEAN'] if v in ['V2_CHUNKS','V3_SOURCES'] else ['DIRECT'])])
outcsv('RERANKER_RESULTS.csv',[dict(model=m,protocol=p,candidate_k=k,status=blocked,N_executed=0,top1='N/A',top10='N/A',mrr='N/A',inference_seconds='N/A',blocker=reason) for m in ['Alibaba-NLP/gte-reranker-modernbert-base','Qwen/Qwen3-Reranker-0.6B'] for p in ['P0','P1','P2_SAMPLED'] for k in [20,50,100]])
write('EMBEDDING_ERROR_ANALYSIS.md','''# Embedding执行阻断与可分析范围

四种候选Embedding均未发现完整的合法本地权重/tokenizer；新模型下载未获授权。真实Embedding预测0，所有准确率、召回、模型Token、内存与模型错误数均为N/A，而非0。没有可命名的“最强Embedding”，不能评价是否超过字符TF-IDF。

输入工程已经完成：P0 975、P1 975、P2 Sampled 385，共2335条；V0–V3共享选中片段，prefix/window各最多2048 regex代理Token。截断281/975、274/975、103/385；不是实际模型tokenizer计数。片段来源、行号、char区间及哈希保存在semantic_models/input_views与data_manifests/NEURAL_INPUT_PROTOCOL.json。无法以输入文件存在证明结构化或分块有效。

GTE/Qwen embedding与GTE reranker有未经过真实权重的离线适配入口。BGE Dense/Sparse/Multi-vector、Jina及Qwen reranker保留INTERFACE_PENDING；没有把未实现的模型接口宣称已部署。手工数值聚合测试不是向量实验。

当前仅可分析冻结词汇召回错误（见results/LEXICAL_CANDIDATE_FAILURES.csv）；不能把它归因于预训练语义模型。未创建空模型环境冒充部署。''')
write('RERANKER_ERROR_ANALYSIS.md','''# 候选召回与重排序错误

两种Cross-Encoder没有完整本地权重，未执行。Top1/Top10/MRR、错误升级与错误降级均N/A；生成式LLM RETRIEVAL条件不属于Cross-Encoder实测。

已运行冻结CharacterNgramTFIDF，保存全部216候选排序、Top20/50/100上界。P0 Top20任何Gold覆盖38.9744%，全部Gold覆盖26.2564%，宏平均Gold召回32.1880%；Top100仍有173/975查询一个Gold都没有，407/1405个Gold出现项不在候选。P1 Top100对应172/975和408/1405；P2 Sampled对应65/385和164/566。Gold只在预测文件关闭后的独立评价中加入。

受限Top20后续任何重排的Top10不可能高于候选Hit@20。38.97%甚至低于P0作者历史GPT-5.5 Top10 66.67%，说明当前小候选限制有结构性瓶颈，不能把所有低分归为推理失败。该比较只是候选上限事实，不是本轮LLM与历史LLM公平性能比较。

已召回但未排进Top10称RANKING_MISS，缺失称RETRIEVAL_FAILURE；前者不足以单凭预测断定缺少语义机制。逐样本表记录现象与限制，不编造技术机制因果解释。''')
protocol='''# 本地LLM研究试验协议与实际执行

日期2026-10-27。合法本地生成模型已实际推理；Embedding与Cross-Encoder仍NEURAL_MODEL_EXECUTION_BLOCKED。不是LLM全局授权阻断。外部模型调用0，模型权重下载0，GPU推理0。

## 模型与冻结输入

唯一准入模型`deepseek-r1:1.5b`，实际1,777,088,000参数，Qwen2架构，Q4_K_M。固定manifest digest `a42b25d8c10a841bd24724309898ae851466696a7d7f3a0a408b895538ccbc96`；GGUF SHA256 `aabd4debf0c8f08881923f2c25fc0fdeed24435271c2b3e92c4af36704040dbc`。上游HF commit未知；以本地完整manifest、blob和内嵌tokenizer固定资产，不虚构revision。

Ollama0.35.1，仅127.0.0.1:11434，禁用代理与HTTP重定向。独立环境`venvs/DeepSeek-R1-1.5B-OllamaCPU`，Python3.12，客户端标准库。Apple M3、24GB统一内存；num_gpu=0，CPU线程2，并发1，temperature0、seed42、repeat_penalty1.05、num_ctx8192，final max512、action max256输出Token；think:false是请求参数，不是对模型内部过程的额外证明。54/54原生响应的设备记录均digest吻合且size_vram显式为0。

216父技术候选。P2起始观察固定最多256 regex词/标点代理Token，所有策略相同；这与未运行的Embedding2048代理输入准备不同。不得把代理计数当作真实模型Token。K2 ATT&CK16.1文档由继承哈希固定。日志prompt最多5000 UTF8 bytes；知识最多约3500 UTF8 bytes，描述截断，均不是完整216定义。实际API prompt_eval_count/eval_count另存原生响应与成本表。

DIRECT216仅216允许ID与相同日志；KNOWLEDGE20提供冻结词汇Top20的部分描述，但输出仍216；RETRIEVAL20/50/100硬限制对应TopN候选、共享3500bytes知识cap，N越大描述越短，因此同时改变候选限制和每候选知识长度，不能孤立归因为推理能力。STATIC_EVIDENCE_S/M用初始词频Top32一次BM25取20/40行；FIXED_QUERY_S固定两次关键词；ADAPTIVE使用相同基础模型按闭集JSON最多2/4次只读工具。所有final只要求10个不同ID、最多5个可见event_id与限制说明；没有完成逐技术action/subject/object/definition映射的完整LLM-EVIDENCE实验。

S新增证据cap：2次read尝试、20个新事件、2048日志代理Token；M为4/40/4096。知识预算4096代理Token且消耗共享查询次数。实际获取量、可见日志与模型重复输入成本分别报告；相同上限不代表相同实际消耗。

## V1与V2、预算及缺失

V1登记在首次研究推理前：14个metadata-only选取的episode（7场景各simulation/step字典序前2），10条件；最多240次请求，一小时停止启动阈值，每请求超时180秒。实际只完成一部分。V1不是跨场景随机代表样本。设备/上下文异常和截止前启动的调用可能超过阈值；总经过4222.93秒含修复、等待及工程，不能称模型运行4222.93秒或严格一小时完成。

独立代码审计发现V1动态知识工具结果与错误反馈未完整传入后续模型。V1所有adaptive条件一律`INVALID_TOOL_RESULT_FORWARDING`，真实调用与成本保留，分类不进入收益分析。知识工具可能在某些轨迹被选中与否不用于事后豁免。程序中断时尚有至多一个请求成本未知。

V2修复知识和全部工具反馈、可见事件统计、失败请求ledger及剩余预算timeout；沿用V1原始时钟，未重置预算。V2是修复后事后缩小的7场景各第1episode×5条件审计视图，不是先验确认试验。仅复用8个完全相同prompt/options/model的V1非自适应响应，含3原始失败；schema由未改动V1构造逻辑重建（原生V1未保存schema），这一溯源限制公开保留。5条件有效输出，3失败；另外27条件未执行，新V2模型请求0，Agent有效执行0。预算未执行不属于模型失败，不给0分。未来运行需另行登记，不在本轮自动增加预算。

## 输出、评分与隐私

重复ID、候选外ID、不可见引用、无效JSON均空预测保留；无Gold修复、无隐藏重试。已调用但输出无效纳入其执行分母；未执行不入分母，仍报告planned/executed/missing。冻结V1评价器用于Top1/5/10、P/R、MRR及F1@5；同时存逻辑步骤宏、场景/执行分组。V1探索非自适应另列，不能与V2缓存相加扩大样本。

唯一54原生研究响应：130642输入、8265输出Token，已知调用wall1999.460475713秒；另至多1中断请求未知，不写成0。合成preflight32/22token、4.1515秒单列非研究；8缓存成本不重复计为新调用。没有全量独立测试或显著性收益主张。预测、工具、prompt不含Gold；Gold仅在离线评价端。服务器没有连接，受限原始成员未读取。

`llm/protocol.py`与`llm/FROZEN_PROMPT_TEMPLATES.json`是通用接口准备快照（原拟1024输出、2048初始代理、216完整知识），不等于本次实际试验。实际参数以manifests/EXPERIMENT_REGISTRATION*.json、原生prompt与本协议为准。
'''
write('LLM_EXPERIMENT_PROTOCOL.md',protocol)
src=R/'llm/run_local_pilot.py';src2=R/'llm/run_local_pilot_v2.py'
v1=src.read_text();v2=src2.read_text()
write('LLM_PROMPTS.md','''# 实际提示词与schema溯源

本轮真实本地LLM已调用；通用模板不是实测prompt。固定候选216、真实运行条件、输出与截断详见LLM_EXPERIMENT_PROTOCOL.md。所有原生`experiments/PILOT_*_final.json`保存完整prompt、SHA、选项、响应与API计数；`_action*.json`是实际工具决策。不得把原生响应当作正确标签。

V1精确final与action构造如下。结构化JSON格式约束与本地validator共同约束候选和引用；JSON schema未保证uniqueItems，因此validator会拒绝重复技术ID，原始失败不修复。

```python
'''+v1[v1.index('def final_prompt'):v1.index('def select_episodes')]+'''\n```

V2完整知识反馈修复（没有新增V2模型响应，不声称修复后行为已实测）：

```python
'''+v2[v2.index('def shared_knowledge'):v2.index('def cached')]+'''\n```

通用接口模板保留于`llm/FROZEN_PROMPT_TEMPLATES.json`，仅NOT_MODEL_INFERENCE。V1源码SHA256：`'''+hashlib.sha256(src.read_bytes()).hexdigest()+'`；V2源码SHA256：`'+hashlib.sha256(src2.read_bytes()).hexdigest()+'`。V2缓存schema为确定性重建，不冒充原生V1保存过的schema。')
write('SEMANTIC_REPRESENTATION_COMPARISON.md','''# 表示比较：已确认与不可判断

已确认：2335条合法输入生成V0原生、V1真实字段、V2来源内分块、V3来源分组；prefix/window共用2048代理上限，映射与哈希测试通过。没有实际Embedding，因此不存在V0–V3效果排名，Max/Mean手工聚合测试也不是神经结果。

冻结词汇检索P0 Top1/Top10/MRR=0.086154/0.277949/0.129372；P2 Sampled=0.096104/0.301299/约0.1452。不得将新256代理初始调查对照（Top10=0.285714）说成同输入的全Sampled成绩下降；它主动缩小观察。

LLM pilot使用另行冻结的256代理初始视图、5000bytes日志渲染、部分3500bytes知识；不属于V0–V3语义编码消融。结构化、分块、来源表示是否改善技术识别均暂无法验证。下一步须在准入编码器上按真实tokenizer重建共享输入，再同时比较prefix、window、Max/Mean，先固定候选知识与预算，不能选择性报告最好配置。''')
write('LLM_INCREMENTAL_VALUE_ANALYSIS.md','''# LLM增量价值

真实本地固定模型已完成研究推理，但没有支持语义能力增益的充分证据。V2事后资源审计视图仅两个episode有四个单轮条件；DIRECT、KNOWLEDGE20、RETRIEVAL20、STATIC_S Top1/Top10/MRR均0，已调用失败保留，另外五场景的缺失不计0分。不是全量开发成绩，更不是外部测试。

V1非自适应探索中DIRECT4/14已执行且4个重复ID等无效失败；KNOWLEDGE4执行2失败，Top10=1/4、MRR=1/36；RETRIEVAL20/50/100各4执行、Top10均0；STATIC_S4执行2失败、Top10=0。完整Top5、P/R/F1、逐失败、分组和真实成本见LLM_TECHNIQUE_RESULTS.csv与results/LLM_ERROR_DETAILS.csv。某个技术进入Top9不证明知识独立作用；极小样本、失败和顺序缺失会主导比例。

这不是“LLM普遍弱于字符检索”的证据；小型量化模型、短观察、部分知识、structured JSON限制、输出验证失败和候选缺失都可能影响结果，尚未有逐机制因果消融。RETRIEVAL改变候选大小与描述长度，不能纯归因语义重排。不能从模型解释推断真实逻辑推理过程。

作者历史GPT-5.5仅AUTHOR_HISTORICAL_RECALCULATION、P0 975查询，Top1/Top10/MRR=40.92%/66.67%/约0.496；新本地模型是P2小pilot，模型、输入、预算、候选知识、数据版本皆不同，不作性能差值或泛化比较。''')
write('AGENT_INCREMENTAL_VALUE_ANALYSIS.md','''# Agent增量判断

结论：AGENT_NO_SUPPORTED_INCREMENTAL_GAIN，含义是目前证据不支持收益，不是证明Agent无效。修复后有效LLM Agent executed=0，不能把未执行当Top10=0；同模型静态/动态有效配对交集N=0。早期6条真实adaptive条件因工具反馈协议缺陷隔离，得分N/A；它们的查询、耗时仍是真实成本。未执行V2状态保存在results/AGENT_NOT_EXECUTED_CONDITIONS.jsonl，不伪造轨迹。主AGENT_TRAJECTORIES.jsonl为空；V1真实无效轨迹位于experiments/PILOT_V1_INVALID_AGENT/AGENT_TRAJECTORIES.jsonl。

全部385个P2 episode的7条件确定性对照已经完成；终端排序同一字符TF-IDF、初始256代理日志、共享合法池。动态启发式依据观察实体与竞争技术描述选查询，是可复现工具策略，不是LLM Agent。S：动态Top1/Top10/MRR=0.088312/0.296104/0.138544，静态=0.101299/0.314286/0.147408。M：动态=0.096104/0.319481/0.145913，静态=0.088312/0.322078/0.143334。M动态Top1/MRR稍高但Top10低，无一致优势。

相同采集上限不等于相同消耗：S静态/动态平均返回1374.19/1357.72代理、新事件10.70/8.84；M为2325.46/2458.91、新事件19.49/12.99。这些对照说明更多查询/动态选词未自动转为收益，不证明“区别性证据”策略的必要条件已经被充分检验。七场景簇敏感性分析与图在analysis-output，无独立泛化主张。

没有有效固定LLM配对、未运行Embedding、未完成独立测试，因此不提出新算法贡献，不增加反思角色或强化学习。''')
write('AGENT_COST_BENEFIT_ANALYSIS.md','''# Agent成本与收益

唯一研究native响应54：130642输入Token、8265输出Token、1999.4605秒已知API wall。54/54设备记录size_vram=0，CPU2线程。至多1中断请求Token/时间未知，attempt上界55；合成preflight另列。总经过4222.93秒包含开发修复和等待，不是API耗时。V2复用8个旧响应、新调用0；不得将V1和缓存成本相加。

成本表LLM_TOKEN_AND_RUNTIME_REPORT.csv同时保留无效Agent的真实调用开销，以及已获取日志、实际渲染日志和实际API Token。V1知识回传缺陷使成本真实、收益无效；不能据此计算每提高一个准确率百分点的成本。修复后Agent0执行，同模型静态配对0，增量Token/延迟及收益比均N/A。知识工具返回不等于该定义进入模型；V2修复代码存在不等于已完成验证。

确定性全量对照不是LLM成本。S动态2次平均查询，静态1次；M动态4次、静态1次；2695条件的检索/排序耗时、返回行、重复比例与代理预算完整在STATIC_RETRIEVAL_AGENT_CONTROLS.csv。该秒数不含全部主机加载/克隆；逐记录另存host_setup_seconds/host_clone_seconds，不能将其称为完整用户端延迟。所有日志读取均在本地已授权过滤数据上，没有网络日志传输。''')
taxonomy=[
 ('RETRIEVAL_FAILURE','MEASURED','Gold不在固定TopN候选','results/LEXICAL_CANDIDATE_FAILURES.csv','不能由限定候选重排修复'),
 ('RANKING_MISS','MEASURED_DESCRIPTIVE','候选有Gold但Top10未命中','results/LLM_ERROR_DETAILS.csv','不能仅凭现象断言语义理解失败'),
 ('OUTPUT_CONTRACT_FAILURE','MEASURED','重复技术ID或无效JSON/引用','results/LLM_ERROR_DETAILS.csv','失败保留空预测，不用Gold补答案'),
 ('INVALID_TOOL_RESULT_FORWARDING','CONFIRMED_CODE_DEFECT','V1知识与错误反馈遗漏','reports/LOCAL_PILOT_CODE_AUDIT.md','V1所有adaptive收益无效，成本仍真实'),
 ('MODEL_ASSET_UNAVAILABLE','CONFIRMED_SCOPED_AUDIT','本地未找到完整Embedding/CrossEncoder资产','MODEL_ASSET_AUTHORIZATION_AUDIT.md','非模型预测错误，指标N/A'),
 ('NOT_EXECUTED_BUDGET','CONFIRMED_EXECUTION_STATUS','V2原预算截止未启动','results/AGENT_NOT_EXECUTED_CONDITIONS.jsonl','不是模型失败或0分'),
 ('INPUT_TRUNCATION','MEASURED_INPUT_PROPERTY','可见片段小于已授权日志','data_manifests/NEURAL_INPUT_PROTOCOL.json','不证明Gold所需事件必然缺失'),
 ('OBSERVABILITY_GAP','UNRESOLVED_CAUSAL_HYPOTHESIS','原生过滤日志可能缺主体/动作/结果','AGENT_ENVIRONMENT_SPEC.md','无逐Gold机制可观测性审计，不能归因计数'),
 ('ATTEMPT_SUCCESS_AMBIGUITY','UNRESOLVED_CAUSAL_HYPOTHESIS','执行尝试不等于成功','LLM_EXPERIMENT_PROTOCOL.md','官方步骤标签与证据充分性不同'),
 ('UNEXPLAINED_SEMANTIC_MISS','UNRESOLVED','排除候选及格式故障后的错排','results/LLM_ERROR_DETAILS.csv','可能短观察/记忆/知识截断等，未做因果消融')]
outcsv('ERROR_SOURCE_TAXONOMY.csv',[dict(error_source=a,evidence_status=b,definition=c,evidence=d,inference_limit=e) for a,b,c,d,e in taxonomy])
write('METHOD_HYPOTHESIS_AND_FORMULATION.md',r'''# H1：区别性证据假设，尚未成立

假设：多个父技术与当前观察相容时，根据竞争机制的必要行为差异获取证据，比只取相关日志更能改善排序。本轮没有有效LLM Agent配对支持，不能将H1命名为已验证算法，更不能以Embedding+RAG+LLM+Agent组合作为创新。

工作性形式化（研究设计，不是已训练模型）：状态 $s_t=(O_t,C_t,B_t,H_t)$，分别为可见事件及映射、候选分数、剩余预算和完整工具历史。技术分数不是已校准后验概率。证据需求 $d_{ij}$ 必须来自公开定义中的动作/对象/状态差异，不得来自Gold。动作 $a_t$ 为五个闭集工具之一，环境只在当前执行—步骤授权池内产生观察 $o_{t+1}$。更新 $O_{t+1}=O_t\cup o_{t+1}$，重复内容也记成本，原生观察与模型渲染分开计数。

拟优化 $\Delta\mathrm{ranking}-\lambda_q\,\mathrm{queries}-\lambda_T\,\mathrm{modelTokens}-\lambda_\tau\,\mathrm{latency}$。此式只是目标定义；权重未训练、没有用当前Gold反推。当前冻结策略不是强化学习，也没有测得信息增益。工具预算用完、模型主动停止、没有合法可获取的新证据或模型总资源截止时停止，最终提交十个不同父技术及可见引用。

最小可证伪对照：同一合法语义候选、同一模型、起始输入、知识文本与访问机会、日志池、证据上限，比较静态检索、固定关键词、普通自适应与定义差异驱动查询；另控制实际返回Token并记录候选是否可恢复。必须优于简单对照且跨独立场景成立，再考虑算法化。当前词汇候选Top20上限与无效工具反馈使其尚不足以立项。''')
write('METHOD_RESEARCH_DECISION.md','''# 科研决策

主状态：PARTIAL_COMPLETION_WITH_DOCUMENTED_BLOCKERS。

已成立的工程状态：AGENT_ENVIRONMENT_READY。生成式LLM真实推理与极小开发pilot评分已完成；不能将LLM_TECHNIQUE_BASELINES_READY解释为全量强基线。Embedding/Cross-Encoder仍NEURAL_MODEL_EXECUTION_BLOCKED。Agent收益：AGENT_NO_SUPPORTED_INCREMENTAL_GAIN（未有有效配对，不等于证伪）。

目前没有论文核心算法的充分实验证据。停止围绕旧EvidenceLineFusion调权，停止增加Agent角色、反思轮数和强化学习。M预算动态启发式不同指标方向不一致，不能通过挑选Top1单项宣称胜出。

建议下一项最小研究：取得明确准入的一个Embedding资产后，固定输入及K2文本测全量语义候选召回，先确认是否突破P0 Top20 38.97%的词汇上界；再补受控Cross-Encoder。若召回已充分且静态LLM仍存在可观测、可恢复的候选混淆，再用修复后工具协议测试定义差异驱动证据需求。保留静态/固定/启发式对照与失败率；独立测试来源须另行冻结。本轮不自动下载、不新增预算、不运行后续试验。

语义召回是否提升、知识是否独立有效、有效Agent是否定位区别性证据均暂无法验证。H1是研究候选而非已证明贡献。''')
llm=list(csv.DictReader((R/'LLM_TECHNIQUE_RESULTS.csv').open()))
v1rows=[x for x in llm if x['protocol']=='V1_EXPLORATORY_NONADAPTIVE' and x['analysis_unit']=='QUERY_EXECUTED' and not x['method'].startswith('ADAPTIVE')]
v2rows=[x for x in llm if x['protocol']=='V2_PRIMARY_RESOURCE_LIMITED' and x['analysis_unit']=='QUERY_EXECUTED']
controls=list(csv.DictReader((R/'STATIC_RETRIEVAL_AGENT_CONTROLS.csv').open()));cr=[]
for x in controls:cr.append({k:(f'{float(x[k]):.6f}' if k in ['top1_accuracy','top10_accuracy','mrr'] else x[k]) for k in ['condition','n_records','top1_accuracy','top10_accuracy','mrr','mean_tool_calls','mean_new_unique_rows']})
answers=[
 '已验证可运行的是本地Ollama deepseek-r1:1.5b（实际1.777B、Q4_K_M），本地7b仅发现资产条目，未完成准入。六种指定Embedding/reranker完整资产未发现。见模型资产审计。',
 '1.5b的本地MIT许可证、全部manifest组件与权重哈希已核实，获准低资源CPU推理。候选公开许可证不等于本地部署完成，也不授权新下载。Jina准确候选为677M、CC-BY-NC4.0，使用范围需遵循非商业条款。',
 'deepseek-r1:1.5b实际产生54条研究原生响应，另有非研究合成preflight；54/54设备证明CPU。没有Embedding或Cross-Encoder真实推理。',
 'GTE/Qwen embedding和GTE reranker离线入口已写但未权重实测；BGE三模式、Jina、Qwen reranker为INTERFACE_PENDING；通用LLM证据字段模板亦仅准备。',
 '没有。缺完整权重/tokenizer，未下载，所有成绩N/A。',
 '没有。Dense/Sparse/Multi-vector均未执行，不将Dense接口准备冒充三模式实验。',
 '没有。Embedding与reranker均缺合法完整本地资产。',
 'N/A。没有实际Embedding预测，不能命名“最强Embedding”，空JSONL代表阻断而非零分。',
 '暂无法判断。冻结P0字符参照Top1=8.6154%、Top10=27.7949%、MRR=0.129372；未有同输入Embedding对照。',
 '没有已成立的语义增益可归因。确定性额外日志对照确有输入变化，不能归于编码；LLM知识是部分描述，tiny pilot不能区分作用。',
 '暂无法判断。V1只保留真实原生字段、全2335输入映射通过，未有语义模型结构化消融。',
 '暂无法判断。prefix/window及Max/Mean聚合接口已测，非真实Embedding实验。',
 '测得冻结词汇候选上界，P0 Hit20/50/100=38.9744%/67.5897%/82.2564%；P2=40.5195%/67.7922%/83.1169%。不属于Embedding召回。',
 'P0 Top20有595/975查询完全无Gold，漏1005/1405个Gold出现项；Top100仍173查询完全无Gold、漏407项。P1 Top100无Gold172查询、漏408项；P2无Gold65查询、漏164/566项。',
 '没有。生成式LLM候选排序不冒充Cross-Encoder。',
 'N/A，没有可合法加载的Cross-Encoder实测。',
 'N/A，同上。候选上界与真实重排成绩严格区分。',
 'Cross-Encoder未执行，因此不能声称发生或没有发生错误降级。已保存原始候选与LLM探索错误供逐样本审核。',
 '存在：已核实本地MIT权重的deepseek-r1:1.5b，单独命名venv、CPU两线程、digest固定。',
 '完成54条研究native响应；V1非adaptive真实结果另列。V2复用8条件（5有效输出、3原始失败），新调用0，其余27条件未执行。不是完整7/14/385 episode LLM矩阵。',
 '不同口径。作者历史是P0 975查询，当前为P2少量执行—步骤、不同模型/视图/知识/预算，不作差值结论。',
 '没有可靠独立增益证据。V1 KNOWLEDGE20仅4执行、2失败，Top10=25%、MRR=0.027778；V2两个已执行episode各单轮条件都Top10=0，缺失及样本过少。',
 '尚未证明。需要相同候选、实际可见日志、知识和有效输出配对；不能仅凭模型解释判定逻辑推理或世界知识能力。',
 '真实建立。385个允许执行—步骤、同执行—步骤Sampled起始与Full-Authorized可检索池，非原始完整攻击历史。',
 '工具入口先对元数据允许表核验再解析指定记录，只允许当前执行—步骤、已知来源和事件上下文；26项安全/边界测试通过。',
 '受测模型工具输出不含Gold且无文件、SQL、shell或外网入口。评价器单独读取reference；开发者已暴露的P0/P1/P2不能因此变独立测试。Python宿主是可信边界，工具不是抵抗恶意宿主的OS沙箱。',
 'V1固定1.5b digest与五工具、预算、选项；V2修复另列版本。未让当前编码Agent代替受测模型回答。',
 'V1确有多轮真实模型查询（6个完成记录的adaptive条件，另中断未知请求），但反馈协议无效。V2没有实际Agent调用，不伪造修复后轨迹。',
 '暂无法验证。有效协议下执行0；V1有无效参数和知识回传丢失，工具结果存在不等于模型取得区别性证据。',
 '没有支持证据。修复后同模型静态/Agent有效配对N=0，不能把Agent算0分。确定性动态启发式在385样本无稳定优势，另表而非LLM成绩。',
 '没有已成立的LLM Agent收益。确定性对照相同cap：S2/20/2048、M4/40/4096；实际返回Token/事件仍不同，不能称严格等实际消耗。',
 '无法建立LLM Agent因果判断。确定性M动态平均返回2458.91代理高于静态2325.46而Top10仍略低；更多日志不自动改善，不能由此排除所有主动查询价值。',
 '全研究已知130642输入+8265输出Token、1999.4605秒，另至多1中断成本未知。有效Agent相对静态增量N/A；无效Agent真实成本保留在成本表，不重复计8缓存。',
 '暂无法验证。无有效LLM Agent配对，不从无效轨迹选择混淆改善案例。',
 '固定TopN无Gold是直接可核查召回失败，详见逐样本LEXICAL_CANDIDATE_FAILURES.csv；P0 Top100仍173查询。LLM限定候选错误也在LLM_ERROR_DETAILS.csv。',
 'Cross-Encoder未执行，语义重排因果错误未知。LLM候选有Gold而Top10错列为RANKING_MISS，只是现象；重复ID失败另归输出契约错误。',
 '可以确认截断与来源缺失属性，不能确认某次错判必然由不可观测性导致。尚缺逐Gold必要动作/结果的原生证据审计，不能把不命中都归于日志缺失。',
 '即使Gold在候选内仍错排的具体原因、知识截断、表示限制、训练记忆和原生步骤标签可观测性的相对作用尚未消融，保留UNKNOWN而不编故事。',
 '没有。P0已暴露开发，P1/P2同源关联开发；7场景34执行195步骤非三个独立外部数据集。',
 '不能。没有真实Embedding/CE比较，LLM极小且无有效Agent配对，现有检索动态无稳定优势。',
 '目前没有必要。先有可复现的有效固定策略配对和可学习的查询收益，再考虑RL；RL不是Agent必要条件。',
 '目前没有必要构建多Agent算法。并行工程协作不等于研究中的多Agent方法；没有任务收益证据支撑增加角色。',
 '尚不具备。工程环境、候选上界与负/阻断结果有价值，但不是核心算法独立贡献证据。',
 '优先补一个合法Embedding的完整共享输入召回实验；召回充分后，再检验公开定义差异→必要证据需求→预算内查询→候选更新。保留静态、固定、启发式和同模型单轮对照，独立冻结测试；本轮不擅自下载或加预算。'
]
assert len(answers)==44
attachment=Path('/Users/tianxd/.codex/attachments/7acc5050-f778-4420-8c82-6704cb0d92b3/已粘贴的文本.txt').read_text()
section=attachment.split('# 二十五、最终报告必须回答的研究问题')[1].split('# 二十六')[0]
questions=re.findall(r'^\d+\. (.+)$',section,re.M);assert len(questions)==44
qa='\n\n'.join(f'### {i}. {q}\n\n{a}' for i,(q,a) in enumerate(zip(questions,answers),1))
main='''---
type: results-report
date: 2026-10-27
experiment_line: R3_LLM_AGENT_TECHNIQUE_REASONING01
round: 1
purpose: round-review
status: partial_with_documented_blockers
source_artifacts:
  - analysis-output/analysis-report.md
  - analysis-output/stats-appendix.md
  - analysis-output/figure-catalog.md
linked_experiments:
  - manifests/EXPERIMENT_REGISTRATION.json
  - manifests/EXPERIMENT_REGISTRATION_V2.json
linked_results:
  - LLM_TECHNIQUE_RESULTS.csv
  - STATIC_RETRIEVAL_AGENT_CONTROLS.csv
---
# R3语义模型与受控Agent实验 / Round 1 / 2026-10-27

## 执行结论

主状态：**PARTIAL_COMPLETION_WITH_DOCUMENTED_BLOCKERS**。次要状态：**AGENT_ENVIRONMENT_READY**；固定本地LLM已完成真实小规模开发pilot及评分，**Embedding/Cross-Encoder未运行**；**AGENT_NO_SUPPORTED_INCREMENTAL_GAIN**表示尚无有效收益证据，不能解释为“已证明Agent无效”。

本轮没有建立强语义召回基线或论文核心算法。已完成：冻结旧成果、模型资产审计、2335条输入视图、词汇候选召回上界、54条本地CPU模型原生响应、受限P2调查工具、385个episode×7确定性对照，以及逐失败和成本审计。缺少完整Embedding/CE资产，下载未授权；修复后LLM Agent因原资源预算耗尽未执行。未用接口文件数替代算法完成度。

## 研究对象与评价协议

P0=975查询/385不同Prompt/195逻辑步骤/7场景/34执行；P1=975查询/767不同输入；P2 Sampled=385执行—步骤/195逻辑步骤，Full-Authorized=680280合法过滤行。三者关联，不是独立外部集。预测均216 ATT&CK父技术，K2_DESCRIPTION_16_1文档哈希固定。全部新文件在本目录；旧A/B目录未覆盖，继承26资产的前后哈希复核见results/DELIVERY_VALIDATION.json。

M0保留旧CharacterNgramTFIDF/BM25/SourceWise/RRF/Normalization；旧EvidenceLineFusion冻结。本轮M1无实际模型，M2仅小本地生成模型，M3环境完成但无修复后有效LLM Agent性能评价。官方TopK为至少一个Gold命中，MRR为首个Gold倒数；多标签Recall与全部Gold覆盖另报，失败空预测保留。未执行/协议无效不计成质量0分。

## 分层结果

|层级|实际执行|结论|
|---|---|---|
|M0|冻结基线+本轮全量词汇候选及2695对照预测|可复核，有输入预算差异，不能混作语义提升|
|M1 Embedding|0|无完整本地权重，指标N/A；下载未授权|
|M2 Cross-Encoder|0|指标N/A；Top20/50/100候选上界已测|
|M2本地LLM|54 native响应，V1非adaptive探索与V2缓存审计分列|极小样本、格式失败多，未证明知识独立收益|
|M3固定LLM Agent|V1六条件协议无效；V2有效执行0|同模型有效配对N=0，收益N/A|

### 词汇候选召回与限制

P0 Hit@20/50/100=38.9744%/67.5897%/82.2564%；对应宏平均Gold Recall=32.1880%/58.7087%/74.6995%，全部Gold覆盖26.2564%/49.7436%/66.3590%。Top100仍173/975查询完全没有Gold。Top20限定重排即使完美，Top10也不能超过38.9744%。所有协议完整值与逐错误见CANDIDATE_RECALL_UPPER_BOUNDS.csv、results/LEXICAL_CANDIDATE_FAILURES.csv；不是Embedding成绩。

### 本地LLM真实探索

唯一准入deepseek-r1:1.5b实际1.777B、Q4_K_M，Ollama0.35.1，CPU2线程，context8192、temperature0、seed42、final512输出上限。实际日志最多256初始regex代理，额外证据工具cap另计，知识部分描述3500bytes，非完整216定义。完整prompt/模型哈希/可见输入/API Token保留。以下不称完整强基线：

V1非adaptive探索（无效adaptive不评分）：

'''+table(v1rows,['method','N_planned','N_executed','N_failed','N_not_executed','top1_accuracy','top10_accuracy','mrr'])+'''
V2修复后事后资源审计（主表标识PRIMARY仅指交付视图，不是确认性预注册；8缓存不与V1相加）：

'''+table(v2rows,['method','N_planned','N_executed','N_failed','N_not_executed','top1_accuracy','top10_accuracy','mrr'])+'''
V1有4个DIRECT无效输出；KNOWLEDGE4执行仅1个Top10命中不足以判断知识有效。V1所有adaptive受到知识返回遗漏与错误反馈不全影响，统一隔离。V2未重置原一小时资源时钟，修复后没有新增推理；未执行27条件保留缺失。完整逐样本分类和成本在results/LLM_ERROR_DETAILS.csv与LLM_TOKEN_AND_RUNTIME_REPORT.csv。没有完成按每个技术输出动作、主体、对象、定义映射的完整LLM-EVIDENCE任务，这属于尚未完成的scope，不能用短限制文本替代。

作者GPT-5.5仅P0历史复算Top1=40.92%、Top10=66.67%、MRR约0.496，AUTHOR_HISTORICAL_RECALCULATION；不是本轮新调用，也不与当前P2 pilot同口径比较。

### 全量静态与动态确定性对照

终端同一冻结字符TF-IDF，初始日志最多256regex代理；S cap=2调用/20新增事件/2048日志代理；M=4/40/4096。全385样本七条件均完成，非LLM Agent：

'''+table(cr,['condition','n_records','top1_accuracy','top10_accuracy','mrr','mean_tool_calls','mean_new_unique_rows'])+'''
S动态比静态Top10低1.8182个百分点；M低0.2597个百分点，但M的Top1/MRR稍高，不能宣称静态在所有指标上统治。实际返回量不同，仅共享cap；动态没有稳定支持扩大策略的收益。

## 统计验证与两幅图的解释

来自analysis-output严格分析：一次确定性运行；385样本有195步骤/34执行/7场景依赖，不做独立查询bootstrap。事后按7场景簇20,000次重采样：S动态−静态Top10差95%描述区间[-4.6693,0]个百分点，M[-2.9851,0.9479]；仅7关联开发簇，区间不是独立测试保证。六项探索符号翻转Holm校正均p=1，交换对称/簇独立无法充分确认，因此不作显著优越或等效结论。完整Top1/MRR区间和场景差分SD在stats-appendix.md；没有随机种子重复方差。

![全量P2确定性对照](analysis-output/figures/figure-01-controls.png)

图1展示七条件Top10点估计（无误差棒，差值区间另报）。应注意S动态低于简单静态、M接近；它改变的是是否继续扩展启发式策略的判断，不能用于评价LLM Agent。

![P0词汇候选上界](analysis-output/figures/figure-02-candidate-ceiling.png)

图2展示任何Gold与全部Gold覆盖随候选扩大提高。它要求先分离召回瓶颈与排序错误，不能将低Top10都归因于LLM推理。图不是神经模型准确率。

## 失败、成本及可观测性限制

54条唯一原生研究响应累计130642输入、8265输出Token，已知API wall=1999.4605秒。全部CPU证明，至多1中断请求Token/耗时未知，attempt上界55；合成preflight另计。4222.93秒为包括修复和等待的总经过，不是推理耗时。8缓存成本只计原响应一次，修复后Agent增量费用/收益比N/A。

日志中有事件不代表技术完整发生，尝试不代表成功；官方步骤Gold与证据充分性不同。未做逐Gold必要动作/结果的机制审计，不能量化“不可观测性造成了多少错判”。截断已测但不是因果归因。错误分类ERROR_SOURCE_TAXONOMY.csv把已测现象、工程缺陷、资源缺失与无法解释的语义错误分开。

受测工具无Gold、无文件路径/shell/SQL/外网，允许成员核验先于指定JSON正文解析；26安全测试通过，全部2695真实策略轨迹重新审计预算与可见引用。宿主Python是可信代码，环境不是OS隔离沙箱。服务器未连接、未修改；受限PwnKit步骤35–37及别名/副本未读。工程开发者曾见reference schema首行和3例固定策略smoke评分，未据此改查询策略；仍按已暴露开发处理，不能声称盲测。

## 44个研究问题逐项回答

'''+qa+'''

## 改变的判断与后续决策

已确认本地存在可运行合法LLM，原先“所有神经模型不可运行”的笼统说法不成立；但是Embedding/CE资产依旧缺失。真实pilot暴露输出契约与工具信息流问题，不支持以增加轮次声称收益。全量确定性动态策略没有稳定超越静态。H1区别性证据仍待验证，尚不能形成论文核心算法。

优先补合法语义召回，再检验静态语义判别的剩余可恢复错误，然后才测试定义差异驱动查询。暂停强化学习、多Agent算法与旧来源融合调权。本轮不增加模型资源预算、不下载、不调用外部API，交付后停止。

## 复现与交付索引

- 模型与设备：MODEL_*、PRETRAINED_MODEL_REGISTER.csv、manifests/MODEL_AUDIT_EVIDENCE.json及原生devices记录。
- 输入：data_manifests/NEURAL_INPUT_PROTOCOL.json、semantic_models/input_views/，10项接口验证。
- 候选：rerankers/candidate_recall.py、CANDIDATE_RECALL_UPPER_BOUNDS.csv、rerankers/CANDIDATES_*.jsonl。
- LLM：LLM_EXPERIMENT_PROTOCOL.md、LLM_PROMPTS.md、LLM_TECHNIQUE_RESULTS.csv、LLM_TECHNIQUE_PREDICTIONS.jsonl、LLM_TOKEN_AND_RUNTIME_REPORT.csv；复算用llm/evaluate_pilot.py，不会调用模型。
- 工具：AGENT_ENVIRONMENT_SPEC.md、AGENT_TOOL_SCHEMAS.json、AGENT_BUDGET_PROTOCOL.md、AGENT_TOOL_SECURITY_TESTS.md、agent_tools/test_security.py。
- 全量对照：STATIC_RETRIEVAL_AGENT_CONTROLS.csv、experiments/deterministic_controls_predictions.jsonl、agent_trajectories/DETERMINISTIC_CONTROLS.jsonl；run_deterministic_controls.py --evaluate-only只复算。
- Agent主轨迹为空（有效实际执行0）；V1真实无效轨迹在experiments/PILOT_V1_INVALID_AGENT/；未执行状态单列results/AGENT_NOT_EXECUTED_CONDITIONS.jsonl。
- 统计及图：analysis-output/{analysis-report,stats-appendix,figure-catalog}.md，results/analyze_controls.py，figures两份PDF与PNG。
- 校验：results/DELIVERY_VALIDATION.json、manifests/DELIVERY_SHA256.json；大文件与空阻断JSONL均可核查。

按用户指定目录和文件名交付，未尝试Obsidian写回。后续实际模型试验须另行准入与登记，不在此报告中补造。
'''
main=main.replace('](analysis-output/figures/',']('+str(R)+'/analysis-output/figures/')
write('R3_LLM_AGENT_TECHNIQUE_REASONING_RESULTS.md',main)
write('reports/DELIVERY_STATUS.md','''# 交付状态

PARTIAL_COMPLETION_WITH_DOCUMENTED_BLOCKERS。Embedding/CrossEncoder无完整资产；新下载未授权。新本地LLM研究推理已发生，极小探索结果已评分；修复后Agent0执行，主trajectory空文件是真实状态，未执行记录独立列出。所有必需文件见主报告索引，N/A表示未测，0仅用于已执行的真实质量零分。旧成果不改。
''')
print(json.dumps({'main_report_questions':len(answers),'blocked_embedding_rows':len(base),'status':'PARTIAL_COMPLETION_WITH_DOCUMENTED_BLOCKERS'},ensure_ascii=False))
