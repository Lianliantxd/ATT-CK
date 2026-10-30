# R3_TECHNIQUE_STRONG_BASELINES_AND_GENERALIZATION02

主状态 **STRONG_BASELINES_EXTENDED**。辅状态 **RESAMPLING_AND_V2_PROTOCOLS_READY**、**PARTIAL_COMPLETION_WITH_DOCUMENTED_BLOCKERS**。完整候选机制尚未证明优于合理强基线；独立泛化未证明。

1. 是，21项旧输入/标签/成绩/代码按SHA256冻结，195步975记录，旧目录未修改。

2. 是，官方清洗prompt仍为385不同、590重复；不是975次独立攻击。

3. 取得固定commit官方resample脚本；仅在安全包装器中运行原采样函数做6项等价测试，未执行无权限过滤的原main。

4. P1主195逻辑步975查询；另有保持P0变体的975条fresh-window控制。

5. P1主767不同输入、208重复；固定变体控制792不同、183重复。

6. 是，每重复重新选择每source随机连续10行；但底层为v2，P0/P1还混合版本/变体/标题变化，不能归因纯采样。

7. 是，复用已核验213,771,977字节v2 ZIP，无重复下载/覆盖。

8. 是，预先元数据白名单；受限场景1的35—37全部变体不读取，其他不确定成员也不读取。

9. P2为385个执行-step、195个逻辑step、34模拟；Sampled与Full各385条。

10. 实际来源含audit、authentication、web_access、application、wazuh、suricata、system、other；主体与细映射差异均保存。

11. v2场景7steps3/6/8/10/13确实观察runc+init；无完整v1日志，不能证明P0未采样到的内容均为版本新增。

12. 主协议216不变；K4仅203候选分析，不混入主成绩。

13. 13缺口保留名称/战术；全79 Gold都覆盖在203内，K4控制改变负候选与IDF而非删除难Gold。

14. 是，3—5字符ngram、仅公开知识拟合IDF，保存975条Top10及P1/P2新预测。

15. 是，host-file分源BM25，公开216全候选源分数保存。

16. 是，host-file分源词级TF-IDF，公开216源分数保存。

17. 是，Max、Mean、RRF、SourceScoreNormalization四项固定规则均跑，另跑候选与三消融。

18. 全部P0条件（含预算/知识/消融）最高Top1为CharacterNgramTFIDF，K2_DESCRIPTION_16_1/native，8.62%；同K2非消融主对照另列，不能混候选空间。

19. 全部条件最高Top10为CharacterNgramTFIDF，K2_DESCRIPTION_16_1/native，27.79%；消融最佳不升级主机制。

20. 全部条件最高MRR为CharacterNgramTFIDF，K2_DESCRIPTION_16_1/native，0.1294；同K2非消融最高见主表。

21. 同view/同K2/216候选确有部分简单融合收益；预算对照见reports/BUDGET_CONTROL_REPORT.md，不能宣称所有指标/协议全面提升。

22. K3已运行，去显式标题后仍有检索命中，完整候选机制没有全面压过简单对照；正文内自然名称仍存在。

23. COMMON_COVERAGE_203_RESULTS.csv保存4表示同975样本结果；Gold无需删除，候选数和IDF变化另列。

24. audit-only与non-audit-only及8源单独运行；空来源单列，见来源表和预算报告，不把空输入当语义失误。

25. 部分指标胜直接拼接；native控制也改善全文BM25，来源融合收益不能全归因于融合模块。

26. 完整候选有Top10改善但Top1/MRR下降；未证明超越RRF及最强简单归一化/字符基线。

27. 有方向相反的场景变化，全部7场景及执行指标保留，不只报有利场景；见SCENARIO_COMPARISON.csv。

28. 排名稳定性确有描述性变化；未做独立攻击显著性推断，不使用“显著”统计结论。

29. 同一确定性算法在不同窗口/变体中变化属于输入敏感性；IDENTICAL_INPUT与DIFFERENT_LOG_SAMPLE分别保存。

30. 本轮没有认证真正未曝光独立测试执行。

31. 完成按scenario/execution的分组开发评价，列类别交集/其他组未见类、步数与多标签比例；不是监督训练测试。

32. 没有，EXTERNAL_TEST_NOT_READY；v2共享原执行不充当外部集。

33. KnowHow继承公开字典适配，不冒称完整模型；TREC/APTREC无新认证配套资产；OCR-APT仅已有组件资格，未新增完整复现。

34. 是，5新增算法命名独立环境；旧BM25/TFIDF环境只读复用，未造TREC/APTREC空新环境。

35. 没有可完成新日志编码的本地语义嵌入模型。

36. HF仅ref无权重/tokenizer/license；旧KnowHow有技术向量无日志编码器/主权重，依赖也缺；不下载模型。

37. 作者GPT5.5历史Top10=66.67%；同216/K2正式非消融基线Top10最高27.79%，差38.87个百分点。不是本项目新调用LLM。

38. 8个固定顺序案例保留命令/告警原生候选行与hash，例如下载文件行为可观察但不自动证明加载/持久化成功。

39. 案例显示候选匹配可由auth/com/is等泛词驱动；“描述语义重叠”仍是需受控验证的解释，不由错预测自动认证。

40. 部分来源/采样控制改变排序，支持敏感性现象；不能据此断言关键日志缺失或标签错。

41. 验证了确定性模块对排名有影响；没有证明完整候选是独立有效的新算法贡献。

42. 同K2/同native预算对照排除新增知识/日志作为某些差异的原因；跨知识/Full/203条件不能据此归因算法。

43. 有候选hit而RRF miss的具体例子，也有反例；整体未胜强对照，不足主张解决简单方法不能解决的问题。

44. 有值得研究的实际错配/候选证据案例，但尚无Agent必要性证据。当前不新增调用，不强建多Agent算法。

45. 可整理baseline与采样协议研究结果；尚不具备以本候选新机制和外部泛化作为正式论文核心结论的证据。

## P0：固定公开开发输入

195逻辑步×5=975查询，7场景，216父技术，K2知识条件。P0主表为query-weighted，因每步同5条也等于对应step-macro；F1@5等详细指标在CSV。SourceWise的输入是相同native事件，native对照另列用于排除去标题影响。

| Method | Protocol | View | N | Top1% | Top5% | Top10% | StepMacroTop10% | P@5 | R@5 | MRR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BM25 | P0 | all | 975 | 4.41 | 12.21 | 21.23 | 21.23 | 0.0244 | 0.1032 | 0.0833 |
| BM25 | P0 | native | 975 | 6.05 | 15.79 | 23.69 | 23.69 | 0.0316 | 0.1330 | 0.1055 |
| CharacterNgramTFIDF | P0 | all | 975 | 2.26 | 9.23 | 25.44 | 25.44 | 0.0185 | 0.0838 | 0.0707 |
| CharacterNgramTFIDF | P0 | native | 975 | 8.62 | 16.31 | 27.79 | 27.79 | 0.0326 | 0.1462 | 0.1294 |
| WordCharacterHybrid | P0 | all | 975 | 3.90 | 13.44 | 23.28 | 23.28 | 0.0269 | 0.1181 | 0.0845 |
| WordCharacterHybrid | P0 | native | 975 | 5.54 | 16.92 | 25.54 | 25.54 | 0.0338 | 0.1533 | 0.1063 |
| TFIDF | P0 | all | 975 | 5.33 | 15.28 | 20.51 | 20.51 | 0.0306 | 0.1356 | 0.0924 |
| TFIDF | P0 | native | 975 | 5.95 | 17.33 | 22.67 | 22.67 | 0.0347 | 0.1517 | 0.1007 |
| SourceWiseBM25_Max | P0 | sourcewise_same_native_content | 975 | 3.18 | 14.56 | 25.44 | 25.44 | 0.0302 | 0.1216 | 0.0849 |
| SourceWiseBM25_Mean | P0 | sourcewise_same_native_content | 975 | 6.46 | 17.23 | 24.10 | 24.10 | 0.0345 | 0.1448 | 0.1116 |
| SourceWiseBM25_RRF | P0 | sourcewise_same_native_content | 975 | 6.97 | 14.77 | 22.87 | 22.87 | 0.0295 | 0.1344 | 0.1065 |
| SourceWiseBM25_SourceScoreNormalization | P0 | sourcewise_same_native_content | 975 | 6.87 | 17.64 | 24.31 | 24.31 | 0.0353 | 0.1515 | 0.1118 |
| EvidenceLineFusion_bm25 | P0 | sourcewise_same_native_content | 975 | 2.67 | 15.28 | 24.21 | 24.21 | 0.0306 | 0.1306 | 0.0813 |
| SourceWiseTFIDF_SourceScoreNormalization | P0 | sourcewise_same_native_content | 975 | 4.62 | 15.90 | 25.54 | 25.54 | 0.0318 | 0.1472 | 0.0960 |
| EvidenceLineFusion_word | P0 | sourcewise_same_native_content | 975 | 3.08 | 13.95 | 25.03 | 25.03 | 0.0279 | 0.1239 | 0.0787 |
| SourceWiseBM25_Max | P0 | native | 975 | 3.18 | 14.56 | 25.44 | 25.44 | 0.0302 | 0.1216 | 0.0849 |
| SourceWiseBM25_Mean | P0 | native | 975 | 6.46 | 17.23 | 24.10 | 24.10 | 0.0345 | 0.1448 | 0.1116 |
| SourceWiseBM25_RRF | P0 | native | 975 | 6.97 | 14.77 | 22.87 | 22.87 | 0.0295 | 0.1344 | 0.1065 |
| SourceWiseBM25_SourceScoreNormalization | P0 | native | 975 | 6.87 | 17.64 | 24.31 | 24.31 | 0.0353 | 0.1515 | 0.1118 |
| EvidenceLineFusion_bm25 | P0 | native | 975 | 2.67 | 15.28 | 24.21 | 24.21 | 0.0306 | 0.1306 | 0.0813 |

作者GPT-5.5历史参照：Top1=40.92%、Top5=60.21%、Top10=66.67%、MRR≈0.4960，仅AUTHOR_HISTORICAL_RECALCULATION。不移植到P1/P2。旧Random/Lexical/KnowHow成绩全部冻结可查，不修改、不冒充本轮重推。

全部20项知识×表示初始对照与预算/来源/消融条件均保留STRONG_BASELINE_RESULTS_P0.csv；不以挑最优K/候选数取代主表。

## P1：真实重复抽样，v2底层

主协议195逻辑步975查询，767不同输入、208重复；固定变体附加控制975/792不同。每replica重新采样，短源可能仍重复。官方连续窗口核心经6项等价验证，文件顺序固定。受限variant池与安全ZIP读取使其不是原main无改运行。

| Method | Protocol | View | N | Top1% | Top5% | Top10% | StepMacroTop10% | P@5 | R@5 | MRR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BM25 | P1 | fresh_windows_v2 | 975 | 5.23 | 15.28 | 23.28 | 23.28 | 0.0306 | 0.1284 | 0.0971 |
| CharacterNgramTFIDF | P1 | fresh_windows_v2 | 975 | 8.31 | 16.21 | 28.21 | 28.21 | 0.0326 | 0.1467 | 0.1273 |
| WordCharacterHybrid | P1 | fresh_windows_v2 | 975 | 5.23 | 16.51 | 24.92 | 24.92 | 0.0330 | 0.1468 | 0.1032 |
| TFIDF | P1 | fresh_windows_v2 | 975 | 5.03 | 15.79 | 23.69 | 23.69 | 0.0316 | 0.1384 | 0.0964 |
| SourceWiseBM25_Max | P1 | fresh_windows_v2 | 975 | 3.59 | 15.49 | 25.13 | 25.13 | 0.0320 | 0.1278 | 0.0878 |
| SourceWiseBM25_Mean | P1 | fresh_windows_v2 | 975 | 6.26 | 17.74 | 24.10 | 24.10 | 0.0355 | 0.1509 | 0.1099 |
| SourceWiseBM25_RRF | P1 | fresh_windows_v2 | 975 | 6.67 | 15.69 | 22.46 | 22.46 | 0.0314 | 0.1386 | 0.1070 |
| SourceWiseBM25_SourceScoreNormalization | P1 | fresh_windows_v2 | 975 | 6.56 | 18.36 | 24.10 | 24.10 | 0.0367 | 0.1561 | 0.1122 |
| EvidenceLineFusion_bm25 | P1 | fresh_windows_v2 | 975 | 3.08 | 15.08 | 24.31 | 24.31 | 0.0302 | 0.1325 | 0.0844 |
| SourceWiseTFIDF_SourceScoreNormalization | P1 | fresh_windows_v2 | 975 | 4.62 | 16.41 | 24.92 | 24.92 | 0.0328 | 0.1458 | 0.0968 |
| EvidenceLineFusion_word | P1 | fresh_windows_v2 | 975 | 3.69 | 13.85 | 25.23 | 25.23 | 0.0277 | 0.1232 | 0.0833 |

P1_FIXED独立标在同CSV内，绝不与主P1合并。P0/P1变化还混有v1/v2、variant与标题差异；固定变体控制只移除variant变化，不能生成缺失的完整v1对照。

## P2：真实v2步骤日志

白名单1,136个victim文本成员；读取前排除受限步骤与别名/不确定路径，未全解压。385执行-step对195逻辑step、34模拟，Sampled7,339行、Full680,280行。Sampled每源10行，Full仅获准filtered步骤，并非全部原始攻击历史。

| Method | Protocol | View | N | Top1% | Top5% | Top10% | StepMacroTop10% | P@5 | R@5 | MRR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BM25 | P2_FULL | full_authorized_filtered | 385 | 5.45 | 12.73 | 23.64 | 25.15 | 0.0255 | 0.1126 | 0.0936 |
| CharacterNgramTFIDF | P2_FULL | full_authorized_filtered | 385 | 9.09 | 17.92 | 30.65 | 27.74 | 0.0364 | 0.1675 | 0.1431 |
| TFIDF | P2_FULL | full_authorized_filtered | 385 | 4.16 | 15.58 | 23.12 | 23.59 | 0.0312 | 0.1431 | 0.0870 |
| BM25 | P2 | sampled10_per_source | 385 | 5.19 | 12.99 | 21.30 | 22.43 | 0.0260 | 0.1152 | 0.0883 |
| CharacterNgramTFIDF | P2 | sampled10_per_source | 385 | 9.61 | 18.18 | 30.13 | 26.92 | 0.0364 | 0.1649 | 0.1452 |
| WordCharacterHybrid | P2 | sampled10_per_source | 385 | 5.45 | 17.14 | 26.23 | 25.20 | 0.0343 | 0.1541 | 0.1050 |
| TFIDF | P2 | sampled10_per_source | 385 | 4.42 | 15.06 | 24.42 | 24.82 | 0.0301 | 0.1355 | 0.0904 |
| SourceWiseBM25_Max | P2 | sampled10_per_source | 385 | 2.86 | 13.77 | 22.60 | 24.44 | 0.0281 | 0.1199 | 0.0759 |
| SourceWiseBM25_Mean | P2 | sampled10_per_source | 385 | 6.75 | 15.32 | 23.12 | 23.97 | 0.0306 | 0.1342 | 0.1075 |
| SourceWiseBM25_RRF | P2 | sampled10_per_source | 385 | 7.27 | 14.81 | 21.82 | 22.35 | 0.0296 | 0.1316 | 0.1072 |
| SourceWiseBM25_SourceScoreNormalization | P2 | sampled10_per_source | 385 | 7.79 | 17.40 | 22.34 | 23.55 | 0.0348 | 0.1481 | 0.1129 |
| EvidenceLineFusion_bm25 | P2 | sampled10_per_source | 385 | 3.38 | 15.84 | 24.68 | 24.62 | 0.0317 | 0.1390 | 0.0881 |
| SourceWiseTFIDF_SourceScoreNormalization | P2 | sampled10_per_source | 385 | 4.94 | 17.40 | 25.45 | 25.21 | 0.0348 | 0.1532 | 0.0973 |
| EvidenceLineFusion_word | P2 | sampled10_per_source | 385 | 4.42 | 16.36 | 25.19 | 24.21 | 0.0327 | 0.1420 | 0.0897 |

P2的query与step-macro可能明显不同，必须保留两列。不同版本共享大量原执行，当前没有外部测试。完整日志未稳定全面胜过采样，信息增量与计算成本不能伪装算法增益。

## 来源、知识、预算与负结果

四种简单来源融合及字符表示已构成比旧词汇参考更充分的对照。K2最高MRR的简单归一化来源BM25优于旧BM25；但对去标题native的收益较小，且字符表示在P1/P2常更强。候选行级区分性/来源校准完整机制没有压过合理最强基线。NoSourceCalibration某Top10较高，不据此事后改主方法。

知识K0—K4均实测。K3删显式标题但不保证正文没有名称；13缺描述候选保留在主216空间，K4仅分析删负候选/改变IDF的影响。输入记录40与2048非空白regex-token的固定预算控制见reports/BUDGET_CONTROL_REPORT.md，所有比较方法共用相同source内容。

| protocol | method | logical_steps | mean_top1_pair_agreement | mean_top10_jaccard | mean_mrr_variance | distinct_input_sum |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | BM25 | 195 | 0.8974358974358975 | 0.9465746219592374 | 0.0011941859022811404 | 385 |
| P0 | CharacterNgramTFIDF | 195 | 0.9076923076923077 | 0.9316626962780808 | 0.0015596621250589505 | 385 |
| P0 | SourceWiseBM25_RRF | 195 | 0.8461538461538461 | 0.9083343319994903 | 0.0048327402755974185 | 385 |
| P0 | EvidenceLineFusion_bm25 | 195 | 0.8671794871794872 | 0.9011198881560872 | 0.003093462087589072 | 385 |
| P1 | BM25 | 195 | 0.6912820512820513 | 0.8545899299292965 | 0.007683354006369879 | 767 |
| P1 | CharacterNgramTFIDF | 195 | 0.6907692307692308 | 0.8187014719820149 | 0.011114092615203726 | 767 |
| P1 | SourceWiseBM25_RRF | 195 | 0.7841025641025641 | 0.8413550761288318 | 0.003250831637498304 | 767 |
| P1 | EvidenceLineFusion_bm25 | 195 | 0.7389743589743589 | 0.8451695765270426 | 0.0028183491934285583 | 767 |
| P1_FIXED | BM25 | 195 | 0.6887179487179487 | 0.8444187136899688 | 0.006859366759049299 | 792 |
| P1_FIXED | CharacterNgramTFIDF | 195 | 0.6661538461538462 | 0.8069801063692467 | 0.010740109373283976 | 792 |
| P1_FIXED | SourceWiseBM25_RRF | 195 | 0.7584615384615384 | 0.8337381842311588 | 0.005001575156178331 | 792 |
| P1_FIXED | EvidenceLineFusion_bm25 | 195 | 0.7220512820512821 | 0.8281105797169146 | 0.0033637329689710643 | 792 |

相同输入确定性一致性与不同样本重叠分别列RESAMPLING_STABILITY_RESULTS.csv。这里只报告描述性变化，不用975查询当独立试验做显著性。7场景/执行分组见GROUPED_VALIDATION_RESULTS.csv；未见技术与依赖未认证问题均保留。

## 泄漏、错误与复现资格

v2原生日志中的audit/告警确实携带标签。初次未清洗试跑已作废隔离，最终全部用逐原行清洗重建输入重跑；修改101,179行、原直接ID101,759处，残余0。行数/索引保留，空行不删除，不改变窗口随机消费。P0旧目录/成绩未修改，21项源hash最终复核。

SOURCE_EVIDENCE_TRACES.jsonl保存实际候选top3行ID/hash、源贡献、公开知识哈希；独立重算62,560条来源trace的预测分数重构误差0。这仍是RANKING_EVIDENCE_CANDIDATE，不是证据Gold。原实验trace还保留代表性单行供检索说明，不能把它当完整逐行分解。8个真实错误案例见METHOD_ERROR_ANALYSIS.md：泛词可驱动误排，行为可观察不等于最终结果已实现。没有自动把未命中判为不可观测/标签错误。

本地语义模型EMBEDDING_BASELINE_RESOURCE_BLOCKED；TREC/APTREC无新认证核心资产，OCR-APT只有已有组件，KnowHow仅旧字典适配资格。具体阻断见reports/EXTERNAL_METHOD_STATUS.md与BASELINE_REPRODUCTION_STATUS_V2.csv。算法环境/完整预测/命令/共享批次耗时及NOT_CAPTURED退出码均如实保存。

## 下一阶段决定

候选机制作为本轮论文核心 **NO-GO**，不以弱BM25对照或单个Top10消融制造创新。下一步需要冻结独立执行/新数据及合格语义模型资源，围绕可审查错误验证行为证据而非泛词相关性；只有真实单轮证据缺口与合理调用授权俱备时才考虑LLM/Agent。当前可发表性尚需独立算法增量、强语义对照及独立泛化证据。

代码在baselines/、method/、datasets/build_v2.py；全部有效预测STRONG_BASELINE_PREDICTIONS.jsonl，原生来源向量SOURCE_LEVEL_TECHNIQUE_SCORES.jsonl，完整输入/版本/授权manifest均保留。旧研究不动，服务器不写，模型调用0。完成后停止。
