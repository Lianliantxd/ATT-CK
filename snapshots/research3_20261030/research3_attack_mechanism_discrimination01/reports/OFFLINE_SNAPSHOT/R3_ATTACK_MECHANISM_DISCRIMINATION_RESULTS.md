---
type: results-report
date: 2026-10-28
experiment_line: attack_mechanism_discrimination
round: 01
purpose: mechanism-and-reranker-diagnosis
status: offline_completed_with_forward_authorization_blocker
source_artifacts: [reports/analysis-output/analysis-report.md, reports/analysis-output/stats-appendix.md, reports/analysis-output/figure-catalog.md, reports/analysis-output/provenance.json]
linked_experiments: [manifests/EXPERIMENT_REGISTRATION.json, manifests/POSTHOC_KNOWLEDGE_CONTROLS.json]
linked_results: [MECHANISM_BASELINE_RESULTS.csv, RERANKER_SCORING_VALIDATION.json]
---

# R3 攻击行为机制表示与ATT&CK技术判别

主状态 **MECHANISM_REPRESENTATION_EXECUTED**。已完成全部可授权离线工作：Cross-Encoder分数诊断、30逻辑步骤冻结、机制提取与关系来源检查、216知识卡、49主实验加16后注册混杂控制，共63375条真实非神经预测。**没有证明新的独立算法贡献**。新GTE/CE机制前向未获得覆盖本轮授权，全部NA；独立人审PENDING，外部TEST未就绪。

当前判断：不继续增加规则、关系图或DGPR模块。当前BM25关系/动作标签的评分通道未生效，先解决表示接口、独立证据参考和同固定模型对照资格；若机制表示仍无收益，再考虑领域适配，而非把工程来源一致性包装成机制理解。

## 继承与实验协议

核验冻结752个既有资产，旧目录/评价器/预测保持不变。P0仍为195逻辑步骤、975查询、216父技术、7场景、34执行。P0=EXPOSED_DEV，P1/P2=RELATED_DEV。DGPR背景文件确认REJECT当前Full、EARLY_STOP_FIX_ONLY，没有新DGPR、Agent、RL或训练。

日志只来自上一轮V2 prefix已授权P0片段，RAW/LITERAL/LITERAL+RELATIONS/RAW+LITERAL及清洗/去角色/去结果/去动作控制共享同一进一步选取的原生事实。所有日志视图≤2000 UTF8 bytes、知识≤1000 bytes。**字节cap不是实际GTE Token测量**，实际Token长度当前NA；不能声称严格等Token神经实验。由于共同cap，RAW也更短，不与上一轮29.23%或历史27.79%直接比增益。

16.1原知识203描述/13缺失保留全部216。卡片只取通用词形与源片段，不写Gold规则或普遍必要条件；与观察分离，条件不确定保留UNKNOWN。传感器自带Txxxx注释在预测文本中等长掩码。Gold仅用于旧结果分层及输出固定后的评价，不进入提取器/模型输入。

## Cross-Encoder实际诊断

5850条件按ID与raw logit完全重建；固定对跨20/50/100及两池分数最大差0，原因是原运行复用cache。这排除了K特有的保存分数变化，但不构成新的批次稳定性复测。原实现query/log在前、技术描述在后、eval、无跨候选Softmax、降序rank均在冻结源码中可核查；官方模型卡支持高logit方向。没有按CAM得分反转排名。

**输出维度/config正文和独立单例/批次forward尚未重新验证**。Token truncation=False与输入长度断言可见；上游日志预算截取和65份知识描述截取真实存在，整体语义影响未排除。因此结论限定保存记录层面“未发现足以解释退化的实现错误”，不能声称完全排除适配问题。

Embedding Top100有101/975完全召回缺失，750/975有Gold候选而最终Top10失败。随着池扩大，更多非步骤Gold的高分候选挤入：T1204、T1601、T1592等最常见，精确排名和分数分布全交付。它们是相对步骤标签的错误候选，不是逐行已证明不可能发生的技术。机制原因仍UNRESOLVED。

## 真实机制结果

| 方法 | 日志 | 知识 | N | Top1 | Top10 | MRR@10 |
| --- | --- | --- | --- | --- | --- | --- |
| char | RAW | K2_DESCRIPTION_16_1 | 975 | 1.85% | 14.87% | 0.0516 |
| char | LITERAL | K2_DESCRIPTION_16_1 | 975 | 0.82% | 9.13% | 0.0307 |
| char | LITERAL_PLUS_RELATIONS | K2_DESCRIPTION_16_1 | 975 | 0.82% | 9.85% | 0.0321 |
| char | RAW_PLUS_LITERAL | K2_DESCRIPTION_16_1 | 975 | 0.92% | 13.74% | 0.0353 |
| char | RAW | MECHANISM_CARD | 975 | 5.33% | 16.82% | 0.0825 |
| char | LITERAL | MECHANISM_CARD | 975 | 0.41% | 15.59% | 0.0373 |
| char | LITERAL_PLUS_RELATIONS | MECHANISM_CARD | 975 | 0.41% | 15.18% | 0.0377 |
| char | RAW_PLUS_LITERAL | MECHANISM_CARD | 975 | 1.85% | 18.56% | 0.0565 |
| bm25 | RAW | K2_DESCRIPTION_16_1 | 975 | 1.23% | 13.54% | 0.0356 |
| bm25 | LITERAL | K2_DESCRIPTION_16_1 | 975 | 1.13% | 17.03% | 0.0417 |
| bm25 | LITERAL_PLUS_RELATIONS | K2_DESCRIPTION_16_1 | 975 | 1.13% | 17.03% | 0.0417 |
| bm25 | RAW_PLUS_LITERAL | K2_DESCRIPTION_16_1 | 975 | 0.72% | 16.31% | 0.0365 |
| bm25 | RAW | MECHANISM_CARD | 975 | 4.10% | 15.90% | 0.0691 |
| bm25 | LITERAL | MECHANISM_CARD | 975 | 2.97% | 16.82% | 0.0600 |
| bm25 | LITERAL_PLUS_RELATIONS | MECHANISM_CARD | 975 | 2.97% | 16.82% | 0.0600 |
| bm25 | RAW_PLUS_LITERAL | MECHANISM_CARD | 975 | 3.59% | 15.49% | 0.0646 |
| generic_action_object_Jaccard_equal_weight | LITERAL | MECHANISM_CARD | 975 | 0.51% | 4.31% | 0.0123 |

全部65条件、Top1/5/10、Precision/Recall/F1、逐样本和分场景结果见CSV。主49条件在任何本轮输出前固定；额外16条件在观察主结果后登记，专门检查知识来源范围与词序混杂，不冒充预注册结论。

原描述下BM25 Literal Top10从13.54%到17.03%，MRR .0356到.0417；95%Top10差CI[-.0062,.0790]、Holm p1。CHAR从14.87%降至9.13%。关系没有改变BM25 Literal排名；SCORER_CHANNEL_AUDIT发现新增关系/动作标签在知识词表中均无posting，因此BM25忽略这些特征，不能将其零差异解读为关系语义无用。简单机制匹配Top10=4.31%。没有稳定跨检索器/场景的机制增益。

知识卡有部分数值提升，但其可见片段来自完整K2，而原描述有1000字节前缀限制。CARD_PREFIX_ONLY控制仍有不同变化；保留词频打乱卡片词序后，BM25在4视图×975样本完整216排名**全部一致**。所以不能把BM25卡片成绩归因结构推理。CHAR变化也可能仅来自n-gram邻接，不足以证明语义关系。

## 图与统计

![表示对照](/Users/tianxd/Documents/mid-term/research3_attack_mechanism_discrimination01/reports/analysis-output/figures/figure-01-mechanism.png)

图1应看到Literal效果随检索器改变；BM25的关系通道未生效，CHAR变化不足归因。先查表示—评分器接口，当前不扩充关系复杂度。

![知识混杂控制](/Users/tianxd/Documents/mid-term/research3_attack_mechanism_discrimination01/reports/analysis-output/figures/figure-02-knowledge-control.png)

图2应看到知识内容分配和词序/词袋因素足以改变或保持成绩；不能据最高柱选择新算法。两图为描述统计，无独立测试含义。

统计按195逻辑步骤先聚合5查询，单协议一次确定性计算，非975独立样本。2000 bootstrap、5000 signflip、172项统一Holm；包含后注册控制，均属探索性。共享场景/脚本可能违反交换性假设，不能作泛化推断。详细mean/SD、CI、效应差和p均保存；无机制语义参考，不给支持判断准确率。

## 30例与来源合法性

冻结30不同步骤，实际10降级/6提升/6共同失败/4共同正确/4召回失败，场景分布{'6': 5, '2': 5, '7': 4, '1': 5, '3': 5, '4': 4, '5': 2}。全量评价不只用这30例。逐例CASE_ANALYSIS只报告原生字段和排名变化，不从错分推断缺日志或机制不存在。

34510字段/997关系/1866知识提及可源回查，12项安全不变量通过。只有同源原生audit key成员关系和明确时间BEFORE，不以PID相等、名称或时间近认证生命周期/因果。uid0只是状态；success字段只认证该syscall报告，exit0未自动成功。工程一致性不等于语义准确率。

盲审包不含Gold、sample_id、层别和模型结果，管理映射隔离；30例均PENDING，没有开发Agent冒充人工。真实独立人审尚无，不评分机制支持Precision/Recall/语义正确率。

## 权限与外部数据

没有新增模型/权重下载、GPU/LLM前向或服务器写入/上传。上一轮预算未重置。新的具体授权请求已准备：4文件9597914字节，指定新服务器项目、同名venv、只读固定模型和依赖、GPU0显存15%/CPU2线程/batch8等全部列明；截至本报告未获得覆盖本轮的明确答复，新表示神经条件为MODEL_FORWARD_NOT_AUTHORIZED。官方文档访问与备用下载存在连接/自动审查超时，没有绕过。

实际核查OTRF/Mordor APT29本地26步派生参考：存在技术标签与自称human_reviewed元数据，但原生日志/原计划、许可、脚本独立性和旧ID映射未完整资格认证，且副本已暴露；不能作为新独立TEST。另核查ExCyTIn现有图QA，任务单位不是ATTACK原生日志步骤标签，拒作该任务TEST。未下载大型归档。CONV-A01及受限PwnKit步骤/别名仍未授权且未读取正文。

## 决策与局限

NO-GO当前组合作为独立算法贡献；保留IR作诊断。BM25的局部数值提升不稳健，关系/动作标签通道未生效；卡片/关系贡献未排除词汇、清洗与知识选择混杂。若取得本轮GPU明确授权，只执行已冻结同模型对照，不改方向或挑样本；否则神经结论保持NA。下一步先独立审查30例、区分标签可观测性与模型排序；在此基础上决定机制判别还是领域适配。本轮不自动启动新训练或大型数据下载。

## 36项逐条回答

### 1. Cross-Encoder是否存在评分实现错误？

未发现保存分数/排序层面的实现错误；但没有新前向和config正文，输出维度及独立批次稳定性仍未重新验证，不能宣称全部实现问题都排除。

### 2. 原始raw logit是否与官方排序语义一致？

官方模型卡支持以raw logit高值排序；本实现不做方向反转。没有依据CAM准确率挑评分方向。

### 3. 相同候选在Top20/50/100池中的分数是否一致？

一致，所有保存交集最大差0；这是缓存复用一致性，不是独立重复forward试验。

### 4. 扩大候选池后，哪些错误技术取代了正确技术？

新增高分非步骤Gold候选替换部分Gold；T1204/T1601/T1592等出现较多，精确逐候选替换与分布已保存。非Gold不等于事件中该技术绝不发生。

### 5. 候选召回不足与候选内排序失败分别占多少？

Embedding Top100无Gold101/975=10.36%；候选有Gold而最终前十未命中750/975=76.92%，二者分开。

### 6. 能否确认排序退化不是输入截断或索引错误？

可排除K特有的文本变化/保存索引变化解释：同对hash和分数不变；不能排除上游截取对整体任务的影响（65份知识曾截断），也未新测batch/维度。

### 7. 是否固定30个开发诊断步骤？

是，30个不同scenario+step，在新机制预测前冻结。

### 8. 30例是否覆盖不同错误类型与场景？

是，10降级/6提升/6共同失败/4共同正确/4召回失败，覆盖7场景；仍有脚本依赖，非独立测试。

### 9. 是否建立了真实可运行的Mechanism-Literal？

是，975查询实际提取，运行代码和数据齐全。

### 10. 是否建立了具有合法原生关系的Mechanism-Relations？

是，997条同source原生audit key/时间关系；不以同PID认证生命周期，不从时间近推因果。

### 11. 是否存在机制字段无法追溯到原始日志？

34510个字段逐一回查原始span/JSON pointer，未发现未追溯项；这不证明语义解释100%正确。

### 12. 是否存在从当前状态错误推断状态变化？

当前实现未作该推断；uid/euid保留观察状态，没有提权发生或跨生命周期状态变化结论。

### 13. 是否存在把尝试错误认定为成功？

没有自动升级；仅native success=yes/no认证本记录报告状态，exit0等未认证返回语义仍未知。

### 14. 是否建立ATT&CK机制知识卡？

是，216卡片，16.1固定；203完整描述、13缺描述仍保留。

### 15. 机制知识卡是否引入了原始知识没有的推断？

不新增测试Gold规则；卡片词形/片段可追溯。必要/可选条件无法认证时留空或descriptive，不当普遍必要条件；语义词义仍待人工。

### 16. 是否存在测试Gold泄漏？

生成器不读官方Gold；预测文本Txxxx传感器注释已掩码，输入Schema/GT注入不变测试通过。Gold只在分层选取与独立评价侧。

### 17. 字符TF-IDF在Literal输入上的表现如何？

原描述Literal CHAR：Top1 .82%、Top10 9.13%、MRR .0307；同观察RAW为1.85%/14.87%/.0516。

### 18. 机制表示是否改善传统检索？

不稳定。BM25原描述Top10 13.54%→17.03%，CI跨0、Holm1；CHAR退化，不能宣布稳健表示增益。

### 19. 是否实际运行GTE的机制表示输入？

否，没有本轮新GPU明确授权，GTE新表示未运行；旧RAW分数仅做继承诊断。

### 20. 如果未运行，是否明确说明新推理授权阻断？

是，精确文件/哈希、目的地、项目venv、固定模型、GPU和上限已列MODEL_FORWARD_AUTHORIZATION_REQUEST；等待明确答复。

### 21. 机制表示是否改善Embedding排序？

NA，未运行，不能用旧模型RAW预测推断Literal成绩。

### 22. 机制表示是否改善Cross-Encoder排序？

NA，未运行；旧CE的候选内排序诊断不是新表示CE实验。

### 23. 关系信息是否具有独立增益？

当前未证明独立收益。BM25新增关系/动作标签不在文档词表，通道未生效，所以相同结果不能否证关系语义；CHAR小幅变化不足归因。

### 24. 改进是否只是文本长度或字段清洗带来的收益？

尚不能完全排除，来源/清洗、元字段和字节分配会改变文本，实际GTE Token数未测；CLEAN_FIELDS/去角色/去结果/去动作等控制已保存。

### 25. ATT&CK Mechanism Card是否具有额外价值？

有部分开发数值变化，但词汇、标题、长度与源片段分配未被充分排除；同词频乱序使BM25全部排名不变，不能称机制知识推理贡献。

### 26. 简单机制字段匹配是否能复现新方法效果？

通用动作对象Jaccard Top10=4.31%，并未复现较好检索；这不意味着复杂机制成立。词序控制能复现全部BM25卡片成绩，说明词袋解释仍在。

### 27. 哪些错误源于候选召回？

继承E1 Top100的101例完全候选缺失可确认；各K分类全部交付，不当作机制语义错误。

### 28. 哪些错误源于模型排序？

继承Top100的750例候选内前十失败可确认，新CPU排名错误也逐样本保存；具体语义原因尚不能仅凭标签确定。

### 29. 哪些错误源于证据无法观察？

无独立事件/机制参考，不能确认哪些Gold机制在截取日志中不可观察；原始范围不完整不构成技术未发生。

### 30. 哪些错误无法归因？

主体对象歧义、状态/结果解释、标签可观测性、域错配、关键证据截取等仍UNRESOLVED。

### 31. 是否实际获得独立人工机制参考？

没有本轮30例新增独立人工参考，全部PENDING。外部派生文件自称human_reviewed，其凭证本轮未独立核实，也未拿来当30例人审。

### 32. 如果没有，哪些证据评价仍不能评分？

机制支持Precision/Recall、语义正确率、因果/状态变化判断一致性等不能评分；来源回查与预算工程一致性可报告。

### 33. 是否存在合格的外部ATT&CK标注日志来源？

OTRF/Mordor APT29有可查本地26步派生标签，是具体候选；匹配原生日志/原计划、许可、脚本独立性和旧ID处理未资格确认，目前不是合格TEST。

### 34. 当前是否具备真正独立测试条件？

没有。P0曝光，P1/P2相关；Mordor派生副本也在其他项目已见，ExCyTIn图QA任务不匹配。EXTERNAL_TEST_NOT_READY。

### 35. 是否已经找到值得开发的新算法机制？

没有找到已验证的独立新算法机制；可追溯IR是诊断资产，成熟检索+卡片组合不等于创新。

### 36. 下一轮应该继续机制判别，还是转向领域适配？

NO-GO继续堆叠当前Literal/Relations规则；先确认表示新增特征进入评分，再人审与有授权的同模型对照；若仍无收益，转向领域适配/困难负例训练的后续立项，本轮不自动训练。

## 复现与交付索引

原始分数诊断、consistency/rank transitions/failure taxonomy；30例ID/依赖/盲包；IR/schema/source trace/源码；16.1卡片和覆盖；主47775预测在MECHANISM_BASELINE_PREDICTIONS，posthoc15600预测在experiments/KNOWLEDGE_CONTROL_PREDICTIONS；65条件统一结果与消融；source/统计/图在reports/analysis-output；外部资格与新GPU精确请求均独立保存。最终完整性以results/FINAL_VALIDATION.json与manifests/DELIVERY_SHA256.json为准。
