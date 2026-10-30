# 运行与复现

全部新推理在本地独立算法命名虚拟环境中执行，Python3.12.14、标准库CPU实现、无额外算法依赖。每个预测进程只读prediction_view与公开知识，输出独立experiment JSONL。每次命令、耗时、退出码、stdout/stderr见experiments/*receipt.json；环境实测sys.executable/prefix、pip freeze/check见manifests/ENVIRONMENT_MANIFEST.json。TREC/APTREC只有隔离空环境，不冒充已配置原模型。

| method | view | knowledge | seconds | n |
| --- | --- | --- | --- | --- |
| Random_seed13 | official | fixed candidate IDs only | 0.06038508331403136 | 975 |
| Random_seed42 | official | fixed candidate IDs only | 0.057419332675635815 | 975 |
| Random_seed2026 | official | fixed candidate IDs only | 0.057370082940906286 | 975 |
| Random_seed2718 | official | fixed candidate IDs only | 0.05824883421882987 | 975 |
| Random_seed31415 | official | fixed candidate IDs only | 0.05977408308535814 | 975 |
| Lexical | official | official_names_subnames_tactics | 0.2360327080823481 | 975 |
| TFIDF | official | official_names_subnames_tactics | 0.2791545828804374 | 975 |
| BM25 | official | official_names_subnames_tactics | 0.3097267081029713 | 975 |
| Lexical | strict | official_names_subnames_tactics | 0.23264045780524611 | 975 |
| TFIDF | strict | official_names_subnames_tactics | 0.27646804228425026 | 975 |
| BM25 | strict | official_names_subnames_tactics | 0.3126483750529587 | 975 |
| Lexical_K16_1 | strict | MITRE16.1_description_extension | 0.8448266661725938 | 975 |
| TFIDF_K16_1 | strict | MITRE16.1_description_extension | 1.2598001658916473 | 975 |
| BM25_K16_1 | strict | MITRE16.1_description_extension | 2.178441375028342 | 975 |
| KnowHowDictionaryAdaptation | strict | existing official dictionary; project ranking adaptation | 29.71782024996355 | 975 |

方法总运行时间见results/SUMMARY.json，不含下载、人工核查和报告。实际Token/API成本=0，外部模型调用0，模型权重下载0，服务器写入0。源码中的get_llm_responses.py只做静态阅读，从未import/执行。

重跑：在本目录执行`venvs/Benchmark/bin/python benchmark/test_metrics.py`、`venvs/Benchmark/bin/python benchmark/run_benchmark.py`、`venvs/Benchmark/bin/python method/run_dev.py`、`venvs/Benchmark/bin/python benchmark/write_reports.py`。命令会覆盖本轮生成结果；先复制目录保留当前交付。用户旧研究目录不在写入范围。
