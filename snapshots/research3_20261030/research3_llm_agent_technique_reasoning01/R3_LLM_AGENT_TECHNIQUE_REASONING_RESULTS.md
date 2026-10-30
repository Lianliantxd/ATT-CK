---
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

|method|N_planned|N_executed|N_failed|N_not_executed|top1_accuracy|top10_accuracy|mrr|
|---|---|---|---|---|---|---|---|
|DIRECT216|14|4|4|10|0.0|0.0|0.0|
|FIXED_QUERY_S|14|3|2|11|0.0|0.0|0.0|
|KNOWLEDGE20|14|4|2|10|0.0|0.25|0.027777777777777776|
|RETRIEVAL100|14|4|0|10|0.0|0.0|0.0|
|RETRIEVAL20|14|4|0|10|0.0|0.0|0.0|
|RETRIEVAL50|14|4|0|10|0.0|0.0|0.0|
|STATIC_EVIDENCE_M|14|3|2|11|0.0|0.0|0.0|
|STATIC_EVIDENCE_S|14|4|2|10|0.0|0.0|0.0|

V2修复后事后资源审计（主表标识PRIMARY仅指交付视图，不是确认性预注册；8缓存不与V1相加）：

|method|N_planned|N_executed|N_failed|N_not_executed|top1_accuracy|top10_accuracy|mrr|
|---|---|---|---|---|---|---|---|
|ADAPTIVE_AGENT_S|7|0|0|7|N/A|N/A|N/A|
|DIRECT216|7|2|2|5|0.0|0.0|0.0|
|KNOWLEDGE20|7|2|1|5|0.0|0.0|0.0|
|RETRIEVAL20|7|2|0|5|0.0|0.0|0.0|
|STATIC_EVIDENCE_S|7|2|0|5|0.0|0.0|0.0|

V1有4个DIRECT无效输出；KNOWLEDGE4执行仅1个Top10命中不足以判断知识有效。V1所有adaptive受到知识返回遗漏与错误反馈不全影响，统一隔离。V2未重置原一小时资源时钟，修复后没有新增推理；未执行27条件保留缺失。完整逐样本分类和成本在results/LLM_ERROR_DETAILS.csv与LLM_TOKEN_AND_RUNTIME_REPORT.csv。没有完成按每个技术输出动作、主体、对象、定义映射的完整LLM-EVIDENCE任务，这属于尚未完成的scope，不能用短限制文本替代。

作者GPT-5.5仅P0历史复算Top1=40.92%、Top10=66.67%、MRR约0.496，AUTHOR_HISTORICAL_RECALCULATION；不是本轮新调用，也不与当前P2 pilot同口径比较。

### 全量静态与动态确定性对照

终端同一冻结字符TF-IDF，初始日志最多256regex代理；S cap=2调用/20新增事件/2048日志代理；M=4/40/4096。全385样本七条件均完成，非LLM Agent：

|condition|n_records|top1_accuracy|top10_accuracy|mrr|mean_tool_calls|mean_new_unique_rows|
|---|---|---|---|---|---|---|
|NO_EXTRA|385|0.070130|0.285714|0.119622|0.0|0.0|
|STATIC_BM25_S|385|0.101299|0.314286|0.147408|1.0|10.7012987012987|
|STATIC_BM25_M|385|0.088312|0.322078|0.143334|1.0|19.48831168831169|
|FIXED_SOURCE_S|385|0.098701|0.311688|0.147462|2.0|12.158441558441558|
|FIXED_SOURCE_M|385|0.098701|0.309091|0.146391|4.0|15.49090909090909|
|ADAPTIVE_HEURISTIC_S|385|0.088312|0.296104|0.138544|2.0|8.844155844155845|
|ADAPTIVE_HEURISTIC_M|385|0.096104|0.319481|0.145913|4.0|12.98961038961039|

S动态比静态Top10低1.8182个百分点；M低0.2597个百分点，但M的Top1/MRR稍高，不能宣称静态在所有指标上统治。实际返回量不同，仅共享cap；动态没有稳定支持扩大策略的收益。

## 统计验证与两幅图的解释

来自analysis-output严格分析：一次确定性运行；385样本有195步骤/34执行/7场景依赖，不做独立查询bootstrap。事后按7场景簇20,000次重采样：S动态−静态Top10差95%描述区间[-4.6693,0]个百分点，M[-2.9851,0.9479]；仅7关联开发簇，区间不是独立测试保证。六项探索符号翻转Holm校正均p=1，交换对称/簇独立无法充分确认，因此不作显著优越或等效结论。完整Top1/MRR区间和场景差分SD在stats-appendix.md；没有随机种子重复方差。

![全量P2确定性对照](/Users/tianxd/Documents/mid-term/research3_llm_agent_technique_reasoning01/analysis-output/figures/figure-01-controls.png)

图1展示七条件Top10点估计（无误差棒，差值区间另报）。应注意S动态低于简单静态、M接近；它改变的是是否继续扩展启发式策略的判断，不能用于评价LLM Agent。

![P0词汇候选上界](/Users/tianxd/Documents/mid-term/research3_llm_agent_technique_reasoning01/analysis-output/figures/figure-02-candidate-ceiling.png)

图2展示任何Gold与全部Gold覆盖随候选扩大提高。它要求先分离召回瓶颈与排序错误，不能将低Top10都归因于LLM推理。图不是神经模型准确率。

## 失败、成本及可观测性限制

54条唯一原生研究响应累计130642输入、8265输出Token，已知API wall=1999.4605秒。全部CPU证明，至多1中断请求Token/耗时未知，attempt上界55；合成preflight另计。4222.93秒为包括修复和等待的总经过，不是推理耗时。8缓存成本只计原响应一次，修复后Agent增量费用/收益比N/A。

日志中有事件不代表技术完整发生，尝试不代表成功；官方步骤Gold与证据充分性不同。未做逐Gold必要动作/结果的机制审计，不能量化“不可观测性造成了多少错判”。截断已测但不是因果归因。错误分类ERROR_SOURCE_TAXONOMY.csv把已测现象、工程缺陷、资源缺失与无法解释的语义错误分开。

受测工具无Gold、无文件路径/shell/SQL/外网，允许成员核验先于指定JSON正文解析；26安全测试通过，全部2695真实策略轨迹重新审计预算与可见引用。宿主Python是可信代码，环境不是OS隔离沙箱。服务器未连接、未修改；受限PwnKit步骤35–37及别名/副本未读。工程开发者曾见reference schema首行和3例固定策略smoke评分，未据此改查询策略；仍按已暴露开发处理，不能声称盲测。

## 44个研究问题逐项回答

### 1. 本地实际有哪些可用的预训练模型？

已验证可运行的是本地Ollama deepseek-r1:1.5b（实际1.777B、Q4_K_M），本地7b仅发现资产条目，未完成准入。六种指定Embedding/reranker完整资产未发现。见模型资产审计。

### 2. 哪些模型具备合法使用授权？

1.5b的本地MIT许可证、全部manifest组件与权重哈希已核实，获准低资源CPU推理。候选公开许可证不等于本地部署完成，也不授权新下载。Jina准确候选为677M、CC-BY-NC4.0，使用范围需遵循非商业条款。

### 3. 哪些模型完成真实推理？

deepseek-r1:1.5b实际产生54条研究原生响应，另有非研究合成preflight；54/54设备证明CPU。没有Embedding或Cross-Encoder真实推理。

### 4. 哪些模型仅完成接口准备？

GTE/Qwen embedding和GTE reranker离线入口已写但未权重实测；BGE三模式、Jina、Qwen reranker为INTERFACE_PENDING；通用LLM证据字段模板亦仅准备。

### 5. Qwen3-Embedding是否实际运行？

没有。缺完整权重/tokenizer，未下载，所有成绩N/A。

### 6. BGE-M3是否实际运行？

没有。Dense/Sparse/Multi-vector均未执行，不将Dense接口准备冒充三模式实验。

### 7. GTE-ModernBERT是否实际运行？

没有。Embedding与reranker均缺合法完整本地资产。

### 8. 当前最强Embedding的Top-1、Top-10和MRR是多少？

N/A。没有实际Embedding预测，不能命名“最强Embedding”，空JSONL代表阻断而非零分。

### 9. 是否超过CharacterNgramTFIDF？

暂无法判断。冻结P0字符参照Top1=8.6154%、Top10=27.7949%、MRR=0.129372；未有同输入Embedding对照。

### 10. 增益是否来自额外日志或额外知识？

没有已成立的语义增益可归因。确定性额外日志对照确有输入变化，不能归于编码；LLM知识是部分描述，tiny pilot不能区分作用。

### 11. 日志结构化是否改善语义识别？

暂无法判断。V1只保留真实原生字段、全2335输入映射通过，未有语义模型结构化消融。

### 12. 分块是否优于直接长文本编码？

暂无法判断。prefix/window及Max/Mean聚合接口已测，非真实Embedding实验。

### 13. 是否测得Top20/50/100候选召回上界？

测得冻结词汇候选上界，P0 Hit20/50/100=38.9744%/67.5897%/82.2564%；P2=40.5195%/67.7922%/83.1169%。不属于Embedding召回。

### 14. 正确技术有多少未进入候选集合？

P0 Top20有595/975查询完全无Gold，漏1005/1405个Gold出现项；Top100仍173查询完全无Gold、漏407项。P1 Top100无Gold172查询、漏408项；P2无Gold65查询、漏164/566项。

### 15. 是否实际运行Cross-Encoder？

没有。生成式LLM候选排序不冒充Cross-Encoder。

### 16. Cross-Encoder是否改善Top-1？

N/A，没有可合法加载的Cross-Encoder实测。

### 17. Cross-Encoder是否改善Top-10？

N/A，同上。候选上界与真实重排成绩严格区分。

### 18. 是否存在Reranker错误降级正确技术？

Cross-Encoder未执行，因此不能声称发生或没有发生错误降级。已保存原始候选与LLM探索错误供逐样本审核。

### 19. 是否存在可合法运行的生成式LLM？

存在：已核实本地MIT权重的deepseek-r1:1.5b，单独命名venv、CPU两线程、digest固定。

### 20. 是否实际完成新的LLM推理？

完成54条研究native响应；V1非adaptive真实结果另列。V2复用8条件（5有效输出、3原始失败），新调用0，其余27条件未执行。不是完整7/14/385 episode LLM矩阵。

### 21. 当前LLM与作者历史GPT-5.5参照是否同口径？

不同口径。作者历史是P0 975查询，当前为P2少量执行—步骤、不同模型/视图/知识/预算，不作差值结论。

### 22. ATT&CK知识是否提供独立增益？

没有可靠独立增益证据。V1 KNOWLEDGE20仅4执行、2失败，Top10=25%、MRR=0.027778；V2两个已执行episode各单轮条件都Top10=0，缺失及样本过少。

### 23. LLM是否表现出超越检索相似度的语义判断能力？

尚未证明。需要相同候选、实际可见日志、知识和有效输出配对；不能仅凭模型解释判定逻辑推理或世界知识能力。

### 24. P2动态日志检索环境是否真实建立？

真实建立。385个允许执行—步骤、同执行—步骤Sampled起始与Full-Authorized可检索池，非原始完整攻击历史。

### 25. 工具是否严格限制在授权执行—步骤？

工具入口先对元数据允许表核验再解析指定记录，只允许当前执行—步骤、已知来源和事件上下文；26项安全/边界测试通过。

### 26. 工具是否无法访问Gold？

受测模型工具输出不含Gold且无文件、SQL、shell或外网入口。评价器单独读取reference；开发者已暴露的P0/P1/P2不能因此变独立测试。Python宿主是可信边界，工具不是抵抗恶意宿主的OS沙箱。

### 27. Agent是否使用了固定模型和固定工具？

V1固定1.5b digest与五工具、预算、选项；V2修复另列版本。未让当前编码Agent代替受测模型回答。

### 28. Agent是否实际开展多轮查询？

V1确有多轮真实模型查询（6个完成记录的adaptive条件，另中断未知请求），但反馈协议无效。V2没有实际Agent调用，不伪造修复后轨迹。

### 29. Agent能否准确定位区别性证据？

暂无法验证。有效协议下执行0；V1有无效参数和知识回传丢失，工具结果存在不等于模型取得区别性证据。

### 30. 动态Agent是否优于同模型静态检索？

没有支持证据。修复后同模型静态/Agent有效配对N=0，不能把Agent算0分。确定性动态启发式在385样本无稳定优势，另表而非LLM成绩。

### 31. 这些收益是否在相同证据预算下成立？

没有已成立的LLM Agent收益。确定性对照相同cap：S2/20/2048、M4/40/4096；实际返回Token/事件仍不同，不能称严格等实际消耗。

### 32. Agent是否只是看到了更多日志？

无法建立LLM Agent因果判断。确定性M动态平均返回2458.91代理高于静态2325.46而Top10仍略低；更多日志不自动改善，不能由此排除所有主动查询价值。

### 33. Agent的额外Token和延迟成本是多少？

全研究已知130642输入+8265输出Token、1999.4605秒，另至多1中断成本未知。有效Agent相对静态增量N/A；无效Agent真实成本保留在成本表，不重复计8缓存。

### 34. Agent是否改善了不同技术之间的混淆？

暂无法验证。无有效LLM Agent配对，不从无效轨迹选择混淆改善案例。

### 35. 哪些错误来自候选召回？

固定TopN无Gold是直接可核查召回失败，详见逐样本LEXICAL_CANDIDATE_FAILURES.csv；P0 Top100仍173查询。LLM限定候选错误也在LLM_ERROR_DETAILS.csv。

### 36. 哪些错误来自语义重排序？

Cross-Encoder未执行，语义重排因果错误未知。LLM候选有Gold而Top10错列为RANKING_MISS，只是现象；重复ID失败另归输出契约错误。

### 37. 哪些错误来自日志可观测性？

可以确认截断与来源缺失属性，不能确认某次错判必然由不可观测性导致。尚缺逐Gold必要动作/结果的原生证据审计，不能把不命中都归于日志缺失。

### 38. 哪些错误仍然无法解释？

即使Gold在候选内仍错排的具体原因、知识截断、表示限制、训练记忆和原生步骤标签可观测性的相对作用尚未消融，保留UNKNOWN而不编故事。

### 39. 是否具有真正独立的外部测试？

没有。P0已暴露开发，P1/P2同源关联开发；7场景34执行195步骤非三个独立外部数据集。

### 40. 当前能否证明某项新算法机制有独立贡献？

不能。没有真实Embedding/CE比较，LLM极小且无有效Agent配对，现有检索动态无稳定优势。

### 41. 是否有必要继续引入强化学习？

目前没有必要。先有可复现的有效固定策略配对和可学习的查询收益，再考虑RL；RL不是Agent必要条件。

### 42. 是否有必要构建多Agent？

目前没有必要构建多Agent算法。并行工程协作不等于研究中的多Agent方法；没有任务收益证据支撑增加角色。

### 43. 是否具备形成论文核心算法的实验证据？

尚不具备。工程环境、候选上界与负/阻断结果有价值，但不是核心算法独立贡献证据。

### 44. 下一阶段最值得开发的具体机制是什么？

优先补一个合法Embedding的完整共享输入召回实验；召回充分后，再检验公开定义差异→必要证据需求→预算内查询→候选更新。保留静态、固定、启发式和同模型单轮对照，独立冻结测试；本轮不擅自下载或加预算。

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
