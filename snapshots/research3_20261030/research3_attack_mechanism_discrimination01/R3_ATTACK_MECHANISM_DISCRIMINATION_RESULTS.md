---
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

主状态 **NO_SUPPORTED_ALGORITHMIC_GAIN**，表示当前没有建立独立算法贡献，不宣称所有开发对比均为零。机制表示已实现，CPU65条件63375预测、授权GPU16条件15600预测，总81条件78975真实预测，所有975查询均保留。本组神经表示对比没有获得经292项联合Holm校正后显著的正向增益。 独立机制人审仍PENDING，EXTERNAL_TEST_NOT_READY。实验完成后未扩大模型、LLM或训练范围。

最重要的可确认结论是：历史CE候选扩大导致的退化来自竞争集合变化，而非保存记录中同候选分数随K改变。新运行补齐单输出配置与有限batch sanity检查；仍不能据此将失败唯一归因于缺少攻击机制理解。工程引用可追溯不等于语义理解已认证。

## 实验身份、问题与协议

核心问题是同日志/同知识/同固定模型/同预算上限下，显式主体动作对象状态结果关系是否改善技术排名。P0为EXPOSED_DEV：195逻辑步骤×5查询、7场景、34模拟标识、216父技术；295/975（30.26%）查询为多标签；P1/P2=RELATED_DEV，不是独立TEST。752项继承资产/旧评价器和模型预测保持冻结。DGPR Full已REJECT，本轮没有DGPR、RL、反思、多Agent系统或新训练。

16.1知识203项有描述、13缺描述保留，不用203类替代216主空间。生成器只读取已清洗合法原生字段，Gold不进提取器/模型；传感器Txxxx注释等长掩码。当前uid0不推提权，exit0不当成功，同PID不认证生命周期，时间近不推因果，知识兼容不等于观察支持。

日志2000 bytes/知识1000 bytes，实际Token实测且未越2048/1024，但实际长度不相等；共享原生观察也进一步截取，所以不直接把历史27.79%或上一轮29.23%与本轮RAW相减。Embedding全216；CE统一旧E1Top20候选，固定候选Hit20=0.4667。完整Token表和输入哈希见GPU主实验报告。

## Cross-Encoder实现诊断

历史5850条件全部可按ID/logit重建，跨池/20/50/100交集同对最大差0（缓存复用）。固定配置与新前向确认单输出 num_labels=1，断言每批logits形状(B,1)。两组预登记相关/无关对均按高logit正确区分，batch与single最大差 0.0；logits分别为[2.669921875, -2.541015625, 2.1640625, -2.62109375]。模型处于eval。只验证这4对，不宣称全部领域分数校准或完整CAM批次不变性。没有根据CAM成绩选择方向，没有实际运行SentenceTransformers wrapper。

Embedding Top100有101/975完全召回缺失、750/975候选有Gold却最终前十失败。扩大池时T1204、T1601、T1592等高分非步骤Gold候选挤入；这只说明相对步骤标签排名错误，不证明这些技术在某事件中绝无发生。上游知识65项曾截断、领域迁移、标签可观测性和机制绑定都是未完全排除的因素。没有评分反转修复，也不把工程修复当创新。

## 全量结果与主要发现

词汇检索在原描述下：

| 方法 | 视图 | Top10 | MRR |
| --- | --- | --- | --- |
| char | RAW | 14.87% | 0.0516 |
| char | LITERAL | 9.13% | 0.0307 |
| char | LITERAL_PLUS_RELATIONS | 9.85% | 0.0321 |
| char | RAW_PLUS_LITERAL | 13.74% | 0.0353 |
| bm25 | RAW | 13.54% | 0.0356 |
| bm25 | LITERAL | 17.03% | 0.0417 |
| bm25 | LITERAL_PLUS_RELATIONS | 17.03% | 0.0417 |
| bm25 | RAW_PLUS_LITERAL | 16.31% | 0.0365 |


CHAR Literal下降，BM25 Literal数值提升，但95%逻辑步骤CI跨0；当前检索器没有一致表示增益。BM25新增关系/动作标签不在文档posting，关系通道未生效，不能据零差否证关系语义。LiteralMechanismMatching Top10=4.31%。

神经主实验：

| 方法 | 日志 | 知识 | N | Top1 | Top10 | MRR@10 |
| --- | --- | --- | --- | --- | --- | --- |
| GTE_EMBEDDING | RAW | K2_DESCRIPTION_16_1 | 975 | 1.54% | 20.10% | 0.0583 |
| GTE_EMBEDDING | LITERAL | K2_DESCRIPTION_16_1 | 975 | 2.36% | 10.77% | 0.0406 |
| GTE_EMBEDDING | LITERAL_PLUS_RELATIONS | K2_DESCRIPTION_16_1 | 975 | 2.15% | 9.33% | 0.0381 |
| GTE_EMBEDDING | RAW_PLUS_LITERAL | K2_DESCRIPTION_16_1 | 975 | 0.92% | 17.44% | 0.0420 |
| GTE_EMBEDDING | RAW | MECHANISM_CARD | 975 | 5.23% | 24.62% | 0.0948 |
| GTE_EMBEDDING | LITERAL | MECHANISM_CARD | 975 | 1.95% | 22.05% | 0.0613 |
| GTE_EMBEDDING | LITERAL_PLUS_RELATIONS | MECHANISM_CARD | 975 | 0.51% | 21.85% | 0.0538 |
| GTE_EMBEDDING | RAW_PLUS_LITERAL | MECHANISM_CARD | 975 | 1.95% | 24.31% | 0.0730 |
| GTE_CE | RAW | K2_DESCRIPTION_16_1 | 975 | 2.26% | 25.74% | 0.0749 |
| GTE_CE | LITERAL | K2_DESCRIPTION_16_1 | 975 | 2.15% | 27.79% | 0.0807 |
| GTE_CE | LITERAL_PLUS_RELATIONS | K2_DESCRIPTION_16_1 | 975 | 3.49% | 25.54% | 0.0852 |
| GTE_CE | RAW_PLUS_LITERAL | K2_DESCRIPTION_16_1 | 975 | 2.46% | 28.51% | 0.0850 |
| GTE_CE | RAW | MECHANISM_CARD | 975 | 2.36% | 19.49% | 0.0584 |
| GTE_CE | LITERAL | MECHANISM_CARD | 975 | 1.13% | 17.44% | 0.0436 |
| GTE_CE | LITERAL_PLUS_RELATIONS | MECHANISM_CARD | 975 | 2.46% | 19.38% | 0.0553 |
| GTE_CE | RAW_PLUS_LITERAL | MECHANISM_CARD | 975 | 2.67% | 24.72% | 0.0689 |

- GTE_EMBEDDING / K2_DESCRIPTION_16_1：RAW Top1 1.54%，Top10 20.10%，MRR@10 0.0583；Literal Top1 2.36%，Top10 10.77%，MRR@10 0.0406；Top10差 -9.33个百分点，95%CI[-14.67, -3.90]，Holm(292) p=0.3251；关系相对Literal：Top10差 -1.44个百分点，95%CI[-3.38, 0.21]，Holm(292) p=1.0000。
- GTE_EMBEDDING / MECHANISM_CARD：RAW Top1 5.23%，Top10 24.62%，MRR@10 0.0948；Literal Top1 1.95%，Top10 22.05%，MRR@10 0.0613；Top10差 -2.56个百分点，95%CI[-8.62, 3.18]，Holm(292) p=1.0000；关系相对Literal：Top10差 -0.21个百分点，95%CI[-3.49, 3.18]，Holm(292) p=1.0000。
- GTE_CE / K2_DESCRIPTION_16_1：RAW Top1 2.26%，Top10 25.74%，MRR@10 0.0749；Literal Top1 2.15%，Top10 27.79%，MRR@10 0.0807；Top10差 +2.05个百分点，95%CI[-2.67, 6.56]，Holm(292) p=1.0000；关系相对Literal：Top10差 -2.26个百分点，95%CI[-6.15, 1.33]，Holm(292) p=1.0000。
- GTE_CE / MECHANISM_CARD：RAW Top1 2.36%，Top10 19.49%，MRR@10 0.0584；Literal Top1 1.13%，Top10 17.44%，MRR@10 0.0436；Top10差 -2.05个百分点，95%CI[-6.87, 2.57]，Holm(292) p=1.0000；关系相对Literal：Top10差 +1.95个百分点，95%CI[-1.44, 5.33]，Holm(292) p=1.0000。

机制卡部分数值变化仍有标题、词汇与完整源知识后部提取的混杂；CPU后注册prefix/乱序控制16条件与主49条件分开登记。同词频乱序使BM25四视图975例完整216排名全部一致，说明该模型没有利用卡片词序结构。神经扩展知识控制本次未授权，不能假定同样机制解释已验证。

## 统计验证

在读取GPU指标前登记60对比×2指标=120新检验，与CPU172项合为292项统一Holm。195逻辑步骤内5查询先平均，2000次bootstrap95%CI、5000次signflip，seed42；完整效应mean/SD/CI/原始p和校正p均交付。单固定权重协议无训练seed重复，脚本/场景依赖尚在，交换性假设可能不满足；统计仅属曝光开发集条件分析，不支持泛化和机制因果结论。

## 图及解释

![CPU表示对照](/Users/tianxd/Documents/mid-term/research3_attack_mechanism_discrimination01/reports/analysis-output/figures/figure-01-mechanism.png)

图1：Literal效果随检索器变化，当前CPU结果不支持稳定机制收益；BM25关系通道未生效。

![知识混杂](/Users/tianxd/Documents/mid-term/research3_attack_mechanism_discrimination01/reports/analysis-output/figures/figure-02-knowledge-control.png)

图2：可见知识分配/词频与词序控制影响成绩，最高柱不能自动解释为新知识推理。

![神经表示对照](/Users/tianxd/Documents/mid-term/research3_attack_mechanism_discrimination01/reports/analysis-output/figures/figure-03-neural.png)

图3：同固定模型和候选协议的真实16条件开发结果。每柱975查询，是描述统计；区间、脚本依赖和多重检验见统计附录。

## 30例、失败归因与语义限制

30个不同逻辑步骤在新输出前按旧结果固定：10降级/6提升/6共同失败/4共同正确/4召回失败，覆盖7场景；全部属于EXPOSED_DEVELOPMENT_DIAGNOSTIC。34510原生字段、997关系、1866卡片词形源回查和12项安全不变量通过，这是工程一致性，不是机制语义准确率。逐案native字段与CPU/神经排名见diagnostic_30；不根据新结果替换样本或补Gold规则。

盲审包隔离Gold/分层/模型结果，真实人审30例均PENDING。因此证据不可观察、主体对象歧义、机制支持与因果/成功语义错误不能由步骤Gold直接裁定；保留UNRESOLVED，不制造机制Precision/Recall。

## 权限、环境与外部数据

用户明确批准4个冻结文件9597914字节上传指定新项目，创建项目同名venv，只读复用两模型与依赖。4文件和2权重哈希均已核验；Gold只在本地。GPU0 A40；总实验墙钟 395.27秒；Embedding 227批；CE 54836个去重候选对、8248批，另8次公开sanity pair；峰值allocated 479.49MiB、reserved 728.00MiB。 新增磁盘及权限收据完整保存；无新模型下载/LLM、无旧环境修改。

外部资格实际核查本地Mordor APT29的26步派生标签与元数据。原生日志/原计划、许可、脚本独立性和旧ID映射尚未齐备，且副本已在其他项目曝光，不能称独立TEST。ExCyTIn现有图QA不匹配原生日志技术步骤任务。网络访问失败未被误写为数据不存在；未下载大归档。CONV-A01及受限PwnKit步骤/别名正文仍未读取。

## 决策、信念更新与下一步

GO仅限保留可追溯IR作诊断资产；NO-GO当前组合作独立算法创新。评分维度和有限batch疑点已得到新实测澄清；这增强了“保存/排序错误不足以解释退化”的判断，却没有证明领域瓶颈一定是机制推理。新增关系符号需要合法知识对应与有效评分接口，不能靠结构外观证明贡献。

下一步由真实独立30例审查区分可观测性与排序问题；若要修正renderer/知识适配，另冻结工程版本，不能回改本轮输入。只有排除信息预算和词汇混杂后才继续机制判别；否则另立领域对比学习/困难负例适配。本轮完成后停止，不自动启动后续训练。

## 36项逐条回答

### 1. Cross-Encoder是否存在评分实现错误？

历史保存分数/排序未发现明显实现错误；新授权配置和全部CE批次确认单输出(B,1)，4公开对batch/single一致。不能由有限sanity排除所有领域适配问题。

### 2. 原始raw logit是否与官方排序语义一致？

官方高raw logit方向与两组公开相关/无关对一致；未按CAM分数选方向。

### 3. 相同候选在Top20/50/100池中的分数是否一致？

一致，所有保存交集最大差0；这是缓存复用一致性，不是独立重复forward试验。

### 4. 扩大候选池后，哪些错误技术取代了正确技术？

新增高分非步骤Gold候选替换部分Gold；T1204/T1601/T1592等出现较多，精确逐候选替换与分布已保存。非Gold不等于事件中该技术绝不发生。

### 5. 候选召回不足与候选内排序失败分别占多少？

Embedding Top100无Gold101/975=10.36%；候选有Gold而最终前十未命中750/975=76.92%，二者分开。

### 6. 能否确认排序退化不是输入截断或索引错误？

K特有输入变化和保存索引错配解释不受保存记录支持；新单输出与4对batch校验已完成。上游截取造成的语义信息损失仍不能排除。

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

是，Embedding和CE各4视图×2知识，共16条件15600真实预测，每条件975。

### 20. 如果未运行，是否明确说明新推理授权阻断？

新授权已收到并执行；其余3种知识×4视图×2模型=24条件超出授权主实验，保持NA。

### 21. 机制表示是否改善Embedding排序？

K2_DESCRIPTION_16_1：Top10差 -9.33个百分点，95%CI[-14.67, -3.90]，Holm(292) p=0.3251；MECHANISM_CARD：Top10差 -2.56个百分点，95%CI[-8.62, 3.18]，Holm(292) p=1.0000。详见完整指标，不能作独立泛化结论。

### 22. 机制表示是否改善Cross-Encoder排序？

K2_DESCRIPTION_16_1：Top10差 +2.05个百分点，95%CI[-2.67, 6.56]，Holm(292) p=1.0000；MECHANISM_CARD：Top10差 -2.05个百分点，95%CI[-6.87, 2.57]，Holm(292) p=1.0000。固定同一旧E1Top20，禁止把候选来源变化误当评分收益。

### 23. 关系信息是否具有独立增益？

GTE_EMBEDDING/K2_DESCRIPTION_16_1：Top10差 -1.44个百分点，95%CI[-3.38, 0.21]，Holm(292) p=1.0000；GTE_EMBEDDING/MECHANISM_CARD：Top10差 -0.21个百分点，95%CI[-3.49, 3.18]，Holm(292) p=1.0000；GTE_CE/K2_DESCRIPTION_16_1：Top10差 -2.26个百分点，95%CI[-6.15, 1.33]，Holm(292) p=1.0000；GTE_CE/MECHANISM_CARD：Top10差 +1.95个百分点，95%CI[-1.44, 5.33]，Holm(292) p=1.0000。BM25标签接口未生效；任何神经数值变化仍不是关系推理因果认证。

### 24. 改进是否只是文本长度或字段清洗带来的收益？

不能完全排除。真实Token已测，四视图长度不同但均低于同上限；清洗、元字段、可见知识与词汇都可能解释差异，CPU控制未穷尽神经模型混杂。

### 25. ATT&CK Mechanism Card是否具有额外价值？

两个固定GTE的描述/卡片实测完整保存；卡片可见内容分配与词汇混杂仍在。CPU同词频乱序复现BM25全排名，不能声称知识结构独立贡献。

### 26. 简单机制字段匹配是否能复现新方法效果？

通用动作对象Jaccard Top10=4.31%，并未复现较好检索；这不意味着复杂机制成立。词序控制能复现全部BM25卡片成绩，说明词袋解释仍在。

### 27. 哪些错误源于候选召回？

继承E1 Top100的101例完全候选缺失可确认；各K分类全部交付，不当作机制语义错误。

### 28. 哪些错误源于模型排序？

历史Top100有750候选内前十失败；本轮CE所有条件同一固定Top20，逐例候选Hit/Recall、Gold排名和相对原池序升降级见NEURAL_CANDIDATE_DIAGNOSTICS。具体语义原因仍不能只由步骤标签确定。

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

没有建立可信独立新算法贡献。本组神经表示对比没有获得经292项联合Holm校正后显著的正向增益。 工程IR可保留，机制语义、人审、外部和信息预算混杂尚未解决。

### 36. 下一轮应该继续机制判别，还是转向领域适配？

停止堆叠现有机制规则。先完成30例独立证据审查和机制特征与评分通道核验，判断是否存在未被词汇解释的机制信息；若无，再单独立项领域适配/困难负例训练，本轮不自动启动。

## 复现与交付索引

主结果MECHANISM_BASELINE_RESULTS汇总81条件；CPU主47775预测、posthoc15600、GPU15600逐行预测分别保留。GPU_MAIN_EXPERIMENT_RESULTS提供完整新实测、Token、配置、资源与比较边界。ALL_CPU_GPU_CONTRASTS保留292项统计，NEURAL_PER_SAMPLE/SCENARIO/CANDIDATE_DIAGNOSTICS和30例表提供错误分析。源码、来源、版本和哈希均在各目录及manifests。最终完整性见FINAL_VALIDATION与DELIVERY_SHA256；授权前报告仅作为OFFLINE_SNAPSHOT历史记录。
