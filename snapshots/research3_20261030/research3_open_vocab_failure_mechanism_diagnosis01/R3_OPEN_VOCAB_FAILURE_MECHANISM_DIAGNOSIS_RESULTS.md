---
type: results-report
date: 2026-10-28
experiment_line: open_vocab_failure_mechanism_diagnosis
round: 01
purpose: frozen-ranking-failure-analysis
status: OFFLINE_DIAGNOSIS_COMPLETED_FOR_RECEIVED_SCOPE
source_artifacts: [reports/analysis-output/analysis-report.md, reports/analysis-output/stats-appendix.md, reports/analysis-output/figure-catalog.md, reports/analysis-output/provenance.json]
linked_experiments: [DIAGNOSTIC_PROTOCOL.json]
linked_results: [INDEPENDENT_HIT_RECOUNT.csv, COUNTERFACTUAL_COMPONENT_DIAGNOSIS.csv]
---
# 开放词表失败机制 / Round 01 / 冻结排名与证据归因 / 2026-10-28

## 执行结论与研究判断

本轮发现了可以比上一轮“基础召回较弱”更精确的边界：**GTE漏掉的384条未见目标查询中，349条的所有正确未见技术在Unseen内部顺序也都排不到前十；只调Seen分数无法挽回。另35条是原GTE的跨Seen/Unseen阻挡候选。C4再破坏了32条原命中，且32条均可定位到监督分数修正。** 三者组成C4的416条漏召回，不能笼统归为“校准不够好”，也不能据此直接归为“预训练语义能力不足”。

主终态OFFLINE_DIAGNOSIS_COMPLETED_FOR_RECEIVED_SCOPE；数值诊断已完成、表示/输入/标签的语义根因仍UNRESOLVED。没有训练、模型调用、参数搜索、服务器访问或历史预测修改。当前应优先把基础语义排序问题与输入/标签对齐问题区分清楚，再决定表示改进；Seen监督分数保真是局部但明确的第二问题。没有证据支持本轮直接LoRA或增加复杂网络。

## 请求范围与资产核验

最新附件`a57d2c6c-7146-45ba-a092-6d51c5578ef3`共11303字节，在第六节6.1的单独项目符号处结束；此前两份也截断，不能声称已收到后续章节或交付要求。已完成收到的1–5节、核心GTE漏召回诊断及可审计中文报告；未知附件尾部保持REQUEST_TAIL_NOT_RECEIVED，未凭空补成用户要求。

上一轮211项交付中210项匹配原SHA，主报告一处空格从“和purge”变成“和 purge”，字节33326→33327、SHA变化；与原哈希匹配的日期镜像逐字差异仅空白。差异在inherited/PRIOR_REPORT_WHITESPACE_DIFF.patch中保留，没有修复或改写旧报告/旧manifest。数值矩阵、预测、参数、代码均未变。领域训练项目1938文件与378份Checkpoint全SHA匹配，仅校验字节，不加载运行模型。

42个fold×seed×view完整矩阵、216候选、Gold/输入与样本ID映射核验。每折Seen由唯一训练逻辑步Gold重算，支持向量与训练集一致；ONE/MULTI使用各自旧头与参数，查询输入仍是同一冻结文本视图，不能把MULTI名称当新日志文本。B3未见评分为NO_SUPERVISED_CLASSIFIER，保留closed-output人为末尾名次仅供审计，不能当语义分数。

历史评价agent预检曾提前读取旧Gold核对规模，其披露继续保留；不能声称整个历史会话未接触Gold。本轮Gold用于明确授权的后验诊断，未传入参数选择或预测流程。原C4参数仅合法内部验证/登记默认，文件SHA未变。

## 独立复算与计数单位

| 视图 | 种子 | Unseen查询/Gold对 | GTE命中/漏掉 | C4命中/漏掉 | 保留/丢失/新增 | 双方漏掉 |
| --- | --- | --- | --- | --- | --- | --- |
| ONE | 17 | 450/605 | 66/384 | 34/416 | 34/32/0 | 384 |
| MULTI | 17 | 450/605 | 66/384 | 35/415 | 35/31/0 | 384 |
| ONE | 42 | 450/605 | 66/384 | 34/416 | 34/32/0 | 384 |
| MULTI | 42 | 450/605 | 66/384 | 35/415 | 35/31/0 | 384 |
| ONE | 73 | 450/605 | 66/384 | 34/416 | 34/32/0 | 384 |
| MULTI | 73 | 450/605 | 66/384 | 35/415 | 35/31/0 | 384 |


| 统计单位 | 分母 | GTE命中 | GTE漏掉 | C4命中 | C4漏掉 | 丢失/新增 |
| --- | --- | --- | --- | --- | --- | --- |
| 查询 | 450 | 66 | 384 | 34 | 416 | 32 / 0 |
| 查询×Unseen Gold技术 | 605 | 66 | 539 | 34 | 571 | 32 / 0 |


975条是逻辑查询视图，不是975个独立攻击：对应195逻辑步骤、每步5采样。含Unseen450查询对应90步骤和605个query×Gold技术对。查询命中定义为至少一个当前Unseen Gold在全216 Top10；Gold对命中只看该技术。当前两种单位恰好命中同为66/34，不等于两种分母可交换。集合交并差完整保存QUERY_HIT_MISS_SETS.json与GOLD_TECHNIQUE_HIT_MISS_SETS.json，键含fold、seed、view、sample，未跨配置拼接。

所有原排名按分数降序、技术ID字典序同分规则重建。17550条GTE/B3/C4排名和2527200个GTE/C4分数单元无差异；独立第二实现进一步逐行验证1263600候选表行、5850查询块、3630 Gold行与189丢失案例，最大标量差0。基于分数/排名的D1–D4允许重叠，不相加当独立错误数。

## D1：结构性排除与C4公式

B3只为训练已见类别存在合法logit。未见类别无分类器，因此Unseen Top10=0；本轮未运行或改变GTE，不能写“主干遗忘”。C4的真实公式：

`sC4(t)=zGTE(t)+λ·Iseen(t)·zB3(t)−γ·Iseen(t)`。

zGTE、zB3的mean/SD来自原合法训练r0，当前只读取已保存值。没有重新拟合归一化。对任何Unseen候选，监督贡献和偏置贡献均为0；zGTE是原余弦的正仿射变换，所以未见类之间的全部先后次序保持。不同原始cosine与logit数值不能直接相加或比较，分量均在CANDIDATE_COMPARISON.csv.gz中逐位对齐。

## D2：32条丢失的组件归因

| 视图 | 种子 | 丢失Gold对 | 移除Seen监督后恢复 | 移除Seen偏置后恢复 | 恢复GTE后命中 | γ=0案例 | 默认参数案例 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ONE | 17 | 32 | 32 | 0 | 32 | 32 | 0 |
| ONE | 42 | 32 | 32 | 0 | 32 | 32 | 0 |
| ONE | 73 | 32 | 32 | 0 | 32 | 32 | 0 |
| MULTI | 17 | 31 | 31 | 0 | 31 | 31 | 0 |
| MULTI | 42 | 31 | 31 | 0 | 31 | 31 | 0 |
| MULTI | 73 | 31 | 31 | 0 | 31 | 31 | 0 |


ONE 32/32的主要程序性标签均为SEEN_SCORE_BOOST：在保留原γ、其他分量和全部216候选时，移除监督修正使正确Gold重新进入Top10。移除偏置0/32恢复，因为这32例原γ全部为0，参数来自合法内部验证，默认参数案例为0。未见Gold没有精确分数并列；实际C4不是RRF，因此无法归因RANK_FUSION_EFFECT。不能因为分数类型不同就认证SCORE_SCALE_MISMATCH；当前只确认标准化后监督分量怎样改变相对排名。

案例`1-2-r3`的Gold `T1595`：GTE原始分数0.598945558，全216排名9；C4 Gold分数1.893860657，排名19。Unseen内部名次始终6，Gold之前的Seen从3变成13，精确贡献10个名次。移除监督恢复9，移除偏置仍19。这解释了算式层面的丢失，不解释为何日志真实机制/标签如此。

全部32例逐例中文说明见LOST_CASES_FULL_ANALYSIS.md；全189个seed/view案例的竞争候选、原始分数、原GTE贡献、监督/偏置修正、变换后分数、排名、参数与来源在GTE_HIT_C4_LOST_CASES.jsonl。没有只挑有利例子替代全量归因。

## D3：基础召回失败的严格分解

对未见Gold g，有精确恒等式：

`rank_all216(g)=1 + 排在g前面的Unseen数量 + 排在g前面的Seen数量`。

C4没有改变Unseen内部顺序，因而`rankC4−rankGTE = Seen_before_C4−Seen_before_GTE`，对全部3630未见Gold行逐项成立。这是排名代数，不是对攻击语义做因果推理。

| 互斥查询分组 | 数量 | 占450查询 | 所能支持的判断 |
| --- | --- | --- | --- |
| GTE命中且C4保留 | 34 | 7.56% | 未见排名保留 |
| GTE命中但C4丢失 | 32 | 7.11% | 监督修正引起的可定位排名损失 |
| GTE已漏掉，但至少一个正确未见类的内部次序≤10 | 35 | 7.78% | 跨Seen/Unseen竞争候选；并不保证兼顾Seen可修复 |
| 所有正确未见类的内部次序均>10 | 349 | 77.56% | 保持未见内部次序的Seen调分无法使其命中Top10 |


349条查询的最靠前正确Unseen在内部也>10，所以至少已有10个错误Unseen在它前面；即便Seen全部移到后面，该正确类也不可能进入全216 Top10。这里**没有将候选空间过滤后计算新的模型成绩**，也没有Gold路由、阈值选择或“oracle模型”提交。此约束适用于当前固定Unseen顺序的所有Seen调分，不是整个任务不可解的证明。

另35条GTE原漏召回，内部至少一个正确类≤10，是跨组阻挡候选；需要兼顾Seen时未必能同时挽回。C4漏掉的416条恰为349+35+32：前349条超出只调Seen的能力边界，后67条存在排名空间上的局部可调条件，不能把67当作实际已恢复结果。

Gold对口径：605对中499对内部序>10；GTE漏539对，其中另40对在内部前十却没进全216前十。查询口径35和Gold对口径40不能互换。65/90个含未见步骤五个视图均有内部序障碍，74/90至少一个视图有障碍，说明不能只把问题归为偶然采样；但仍不能把90步骤当90独立执行。

| 场景 | 含Unseen查询 | GTE漏掉 | 内部次序>10 | 仅跨类阻挡候选 | 融合丢失 | Mixed中仅命中Seen |
| --- | --- | --- | --- | --- | --- | --- |
| fold_heldout_1 | 95 | 87 | 76 | 11 | 6 | 33 |
| fold_heldout_2 | 50 | 50 | 48 | 2 | 0 | 0 |
| fold_heldout_3 | 90 | 73 | 68 | 5 | 12 | 20 |
| fold_heldout_4 | 25 | 20 | 20 | 0 | 0 | 0 |
| fold_heldout_5 | 10 | 10 | 10 | 0 | 0 | 0 |
| fold_heldout_6 | 150 | 119 | 102 | 17 | 14 | 29 |
| fold_heldout_7 | 30 | 25 | 25 | 0 | 0 | 0 |


Gold漏召回的全216名次中位72，内部次序中位44，Gold比全候选第10名cosine低的中位差为−.0532113。该差描述当前相对排序，不存在一个被认证的绝对“语义不足分数阈值”。全部539个Gold漏召回记录的原始分数、最近错误候选、边界差、文本/描述长度、Top1/5/10与视图信息均保存，未用这些统计更改模型。

## D4：Mixed覆盖

145条Mixed中，C4有82条只命中Seen而未命中Unseen，双命中为0。Seen候选得分高不意味着该候选一定是正确Seen Gold；需要区分训练类身份与正确标签身份。D2是原未见命中丢失，D4是当前Mixed覆盖，两者可以重叠但不是同一事件集合。现象不能证明某攻击机制没有发生或日志缺证据。

## 数据与标签映射：能排除与不能排除的部分

975查询原始子技术归并到父技术与冻结Gold全部一致，Gold均在216候选内；输入Hash与样本匹配，没有检测到同一冻结文本跨不同逻辑步骤对应不同Gold的精确冲突组。结果是NO_DETECTED_ID_INTERFACE_ERROR，不能写“标签完全正确”。

标签单位为作者步骤，模型看到的是冻结有限日志视图。当前输入202–1580 UTF8 bytes；216项描述中174项恰1000 bytes。构建预算、窗口、描述长度可能影响信息，**仅凭长度不能确认某例实际被截断，更不能确认丢失了技术证据**。384条主协议GTE漏查询各有全量证据卡GTE_MISS_EVIDENCE_CARDS.jsonl，包含本轮已授权的冻结文本、Gold描述与Top10候选描述，具体语义原因均UNRESOLVED，未新造机制Gold。

证据卡原生成阶段把有限视图直接写成“已截断”，在终稿前已用专门资格修正步骤改为“有限视图已确认、实际截断未知”，修正前后SHA和变更范围见EVIDENCE_CARD_QUALIFICATION_RECEIPT。未改文本内容、分数、标签或排名。此区分避免把预算标签当作每例真实证据。

当前不能在“基础表示不足”和“日志窗口/步骤Gold不对齐”之间作最终归因。349条数学边界约束的是当前分数与参考的关系，不证明这些参考在日志中可观测。没有独立事件级证据或完整允许范围的上游核验时，应保持UNRESOLVED。

## 科研图与统计说明

![失败分解](/Users/tianxd/Documents/mid-term/research3_open_vocab_failure_mechanism_diagnosis01/reports/analysis-output/figures/figure01_unseen_failure_partition.png)

图1把450条分成四个互斥组，作用是区分新增破坏与原始基础障碍，不能把所有384条原失败都归为Seen竞争。

![组件归因](/Users/tianxd/Documents/mid-term/research3_open_vocab_failure_mechanism_diagnosis01/reports/analysis-output/figures/figure02_component_removal.png)

图2仅比较已丢失32例的组件移除，表示程序性归因，不是新模型正式成绩，也不把恢复GTE排名包装成算法增益。

![场景分解](/Users/tianxd/Documents/mid-term/research3_open_vocab_failure_mechanism_diagnosis01/reports/analysis-output/figures/figure03_scene_failure_partition.png)

图3保留7个场景及不同分母。共享训练、五采样、旧种子和已曝光场景不支持普通IID推断，所以不提供确认性p值或95%CI。所有计数、逐场景差异、ONE/MULTI与种子均完整保留；当前结论只用于DEVELOPMENT_ONLY诊断。

## 后续优先级与明确停止点

**第一优先：证据对齐核验与基础语义排序问题的区分。** 用现有384张全量证据卡定位哪些输入实际包含技术可观测证据；若缺独立参考则继续标未知。只有确认Gold在输入中可识别后，才把349类内部排序失败归为表示/描述改进问题。当前没有证据支持直接修改数据标签或启动模型训练。

**第二优先：监督融合的未见排名保真。** 32条原命中损失可计算定位，未来方法必须保留这个强基线约束，同时报告Seen代价。不得只靠总体MRR提升掩盖破坏。35条原跨类阻挡候选与32条新增损失应分别研究，不能扩大当前参数网格把开发集最好点当成功。

**不支持：** 把γ偏置项、默认小验证折或同分规则作为32条损失已证实原因；把所有未见错误归为“预训练模型不懂安全”；把SCORE_SCALE_MISMATCH或机制未发生写成事实；把组件移除计数当正式新算法成绩；自动LoRA、服务器前向或新增LLM。

本轮完成收到范围内的诊断后停止。请求尾部仍未收到，不声称覆盖未知章节。报告写在本地指定研究工作区，没有Obsidian或外部Page回写。

## 工件、成本与复现

主要工件：DIAGNOSTIC_PROTOCOL.json、inherited/ASSET_HASH_AUDIT.json、CANDIDATE_COMPARISON.csv.gz（1263600行）、QUERY_DIAGNOSTICS.csv（5850行）、UNSEEN_GOLD_TECHNIQUE_DIAGNOSTICS.csv（3630行）、INDEPENDENT_HIT_RECOUNT.csv、两类集合JSON、GTE_HIT_C4_LOST_CASES.jsonl（189例）、LOST_CASES_FULL_ANALYSIS.md（ONE seed17全32例）、GTE_MISS_GOLD_DIAGNOSTICS.csv（3234行）、GTE_MISS_EVIDENCE_CARDS.jsonl（384查询）、COUNTERFACTUAL_COMPONENT_DIAGNOSIS.csv、INPUT_LABEL_MAPPING_AUDIT.csv、IDENTICAL_VIEW_DIFFERENT_STEP_AUDIT.csv、严格分析bundle、独立审计与最终哈希清单。

诊断主脚本wall48.13秒，峰值RSS498008064字节；独立最终审核wall35.48秒。旧Checkpoint只SHA读取，没有模型前向；本轮算术只用保存分数，不重建embedding、不装新包、CPU2线程。Tokenizer输入成本不适用，不能声称对新文本做了零成本模型推理。

复现顺序：verify_inheritance.py → run_diagnosis.py → qualify_evidence_cards.py → summarize_evidence.py → independent_audit.py → make_figures.py → build_reports.py → manifests/final_validate.py。运行前应使用新的派生目录，避免覆盖封存诊断。所有Python用-B，旧目录不生成pycache。
