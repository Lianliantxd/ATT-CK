# R3_ATTACK_TECHNIQUE_BENCHMARK01 实际结果

2026-10-27，主终态 **BASELINES_READY_METHOD_UNPROVEN**。官方受限子集、统一评价与多项离线基线已就绪；外部完整论文复现仍有资产阻断。本轮没有服务器写入、攻击执行、模型下载或外部LLM调用。

## 35项科研问题逐项回答

1. 是，v2 filtered归档本地合法下载并校验；本轮可评分主输入实际为官方v1预制查询，不能混称v2。

2. 是，llm_queries.json，应用作者真实清洗后hash与公开历史prompt配对。

3. 是，labels.json的metadata技术键；与查询GT集合975/975一致。

4. 文件母体198步990查询；本轮排除受限3步后195步975记录，34被抽选模拟标识、7场景。

5. Gold为79父技术、94原技术/子技术ID；候选为216父技术。

6. 285/975=29.23%采样、57/195=29.23%步骤含多个父技术。

7. 是，按父技术归并去重，保留原Gold集合。

8. 是，matrix691原ID归并216父ID；具体ATT&CK发行号未编码，不能认证。

9. 未改官方分类评价脚本实际执行成功；全198步受限，因此仅复现195步分类管线。

10. 可在4868合法响应上复算；Ministral缺7，列可用分母与全975分母。

11. 一致，TopK/P/R/MRR最大绝对差约1.14e-15；不包括官方辅助weighted-MRR/稳定性的独立认证。

12. 结构/目录/显式标签审计完成，原始query确有audit标签；清洗严格等官方历史输入。未穷尽自然语言隐性泄漏。

13. 是，四项均在独立算法环境真实推理，保存每项Top10输出；还运行KnowHow字典适配与知识扩展。

14. Top1/5/10具体值见本报告实测表与BASELINE_RESULTS_P0.csv，非复制作者论文数字。

15. P@1/5/10、R@1/5/10、MRR@10、F1@5均实算保存，见同表/CSV。

16. 采样日志与作者相同清洗，且同受限子集；显式检索知识与LLM内隐知识不同，扩展16.1条件另列。

17. 检索/KnowHow适配是本项目新离线推理；五LLM仅作者历史响应复算，新LLM调用0。

18. 逐技术低召回与支持数见results/per_technique_errors.csv；不能无视低支持和多个Gold给出稳定难度排名。

19. 多Gold分组已列observable_strata；TopK命中掩盖剩余Gold漏识别，不能把所有多标签错误确定归因为多标签。

20. 所有输入有日志；是否缺关键见证未逐条认证，不能把共错样本称为无可见证据。

21. 描述相似是待检验机制；没有逐对受控因果证明。

22. 尚无完整未采样日志对照，无法确定哪些错误由采样造成；590重复样本说明采样独立性受限。

23. 旧审计有298 JSON/约4899万事件；缺认证原算法、图/NOI/标签/划分，空独立环境非模型就绪。

24. 已有20页全文与审计；缺原子图GT/划分、实现、LoRA及确切基础模型，未下载权重。

25. 可参与，已实跑公开字典的项目Top10适配；不是完整KnowHow原论文复现。

26. 本轮运行KnowHowDictionaryAdaptation；TREC/APTREC模型未跑，指标N/A有具体资产原因。

27. 是，每项算法各命名虚拟环境；manifest保留真实解释器和pip check，空环境不被当成完整模型环境。

28. 有scenario/simulation/step字段，可做分组；模板依赖未完整认证，不强造few-shot划分。

29. 原始query存在直接标签风险；作者正则清洗后显式ID残余0；metadata-only弱检索低分仍不能证明完全无捷径。

30. BM25+16.1 Top10=21.23%，作者GPT5.5同子集Top10=66.67%，差45.44个百分点；不是同知识预算因果比较。

31. 有描述性影响：TFIDF Top1由1.13%至5.33%；BM25 Top10由18.05%至21.23%，但场景7BM25 MRR反降。

32. 未能证明“更多日志必然解决”；开发audit-only好于全部而non-audit-only全错，提示输入选择问题；完整检索也仍低分。

33. 存在候选问题但尚无已证实创新：部分可观测多源证据控制与相似技术的证据归因。

34. 下一项优先开发来源内归一化排名/证据融合的固定对照，使用等预算与去标题控制；在独立执行上验证，保留负结果。

35. 保留排名、源哈希、sample_id、执行/步骤及来源；后续另接逐项证据与目标假设，目标GT/目标指标仍须独立认证。

## 实际对照结果

同一195步975记录，父技术216候选。百分比列为百分数，P/R/MRR为0—1。Random为五个预注册seed均值（各seed原始预测均保留）；名称知识与描述扩展分别列出。历史LLM行是公开作者输出复算，未重新调用模型；Ministral缺失按0保留全975分母。

| Method | Top-1 % | Top-5 % | Top-10 % | P@5 | R@5 | MRR |
| --- | --- | --- | --- | --- | --- | --- |
| Random (5 registered seeds mean) | 0.45 | 3.22 | 6.52 | 0.0065 | 0.0228 | 0.0177 |
| Lexical | 0.62 | 6.05 | 13.85 | 0.0121 | 0.0605 | 0.0343 |
| TFIDF | 1.13 | 6.15 | 15.79 | 0.0123 | 0.0504 | 0.0372 |
| BM25 | 1.23 | 8.82 | 18.05 | 0.0176 | 0.0727 | 0.0431 |
| Lexical_K16_1 | 3.08 | 8.62 | 16.21 | 0.0172 | 0.0715 | 0.0623 |
| TFIDF_K16_1 | 5.33 | 15.28 | 20.51 | 0.0306 | 0.1356 | 0.0924 |
| BM25_K16_1 | 4.41 | 12.21 | 21.23 | 0.0244 | 0.1032 | 0.0833 |
| KnowHowDictionaryAdaptation | 1.13 | 8.41 | 21.03 | 0.0168 | 0.0694 | 0.0519 |
| qwen/qwen3-32b-04-28 [author historical] | 16.00 | 25.23 | 30.56 | 0.0517 | 0.2038 | 0.1986 |
| openai/gpt-5.2-20251211 [author historical] | 39.90 | 59.49 | 64.51 | 0.1317 | 0.5071 | 0.4810 |
| openai/gpt-5.5-20260423 [author historical] | 40.92 | 60.21 | 66.67 | 0.1327 | 0.5111 | 0.4960 |
| meta-llama/llama-4-maverick-17b-128e-instruct [author historical] | 25.54 | 38.26 | 44.31 | 0.0812 | 0.3153 | 0.3096 |
| mistralai/ministral-3b-2512 [author historical] | 10.15 | 16.21 | 16.82 | 0.0326 | 0.1350 | 0.1248 |

TREC适配、APTREC适配：N/A，缺配套图标签/实现/模型条件。TrainingOnlyPrior与LogInstanceRetrieval：N/A，无独立合法训练集。本文所有检索结果只支持“实测参考线”，不宣称它们已代表当前最先进或已充分调优的强方法。

## 真实性、资格与限制

官方完整198步的论文/README成绩单列PAPER_REPORTED_RESULTS.csv，不能直接与195步表混排比较。P0预制查询来自v1，不是v2；旧v2归档已核验但本轮未读取其成员正文。官方matrix没有描述与版本，16.1扩展203父技术、13缺描述，改变了知识条件。

官方历史输入hash匹配、独立评价器与官方分类指标一致、12项单元测试通过。原始query含直接标签，应用作者清洗后方可用；严格与官方视图本次相同。385不同prompt、590重复项，975不是独立攻击次数。57多Gold步骤要求同时看Recall/F1，且官方预设标签不等于可见证据完整认证。

## 误差与决策

271采样记录中，BM25/TFIDF描述扩展和作者GPT5.5都未在Top10命中任何Gold。它们仍有可见日志，不能断言不可观测。具体技术/来源/多标签分组及证据资格见BASELINE_ERROR_ANALYSIS.md和results/*.csv。未知采样因果、未知完整执行成功状态、未知预训练污染均保留为未验证。

开发场景7只含12步60条。十六进制解码无提升；去标题或audit-only使Top10从8.33%到16.67%，Top1仍0。不能据此声称知识推理/LLM创新已成立。下一步最值得测试固定来源内归一化与证据融合，并用等预算控制及独立执行数据验证。当前不增加复杂Agent。

技术排名与步骤/执行/来源/哈希已保留，为后续证据映射提供接口；本轮没有独立技术证据充分性评分、战术分类成绩或完整操作目标理解成绩。

## 可复核入口

代码：evaluate_techniques.py、benchmark/run_benchmark.py、baselines/predict.py与retrieval.py、method/run_dev.py。数据：STEP_LEVEL_DATASET.jsonl及datasets分离视图。预测：BASELINE_PREDICTIONS.jsonl、experiments各进程输出、method/DEV_PREDICTIONS.jsonl。来源：OFFICIAL_DATA_MANIFEST.json及official_sources固定提交原件。环境/成本/命令：manifests/ENVIRONMENT_MANIFEST.json、experiments/*receipt.json、BASELINE_RUNTIME_REPORT.md。P1来源消融在BASELINE_RESULTS_P1.csv，不能与P0直接同口径。

主要来源：[官方代码与更正](https://github.com/ait-aecid/attack-manifestations-interpretation)、[CAM-LDS v2](https://zenodo.org/records/18861762)、[正式论文全文](https://link.springer.com/article/10.1007/s10207-026-01318-x)、[TREC作者论文](https://nesa.zju.edu.cn/download/TREC.pdf)。APTREC/KnowHow资产依据本地已有原文及官方源码审计，见各自状态报告。
