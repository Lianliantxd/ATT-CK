# R3机制判别：独立续作与冻结交付

本交付日期为2026-10-28。P0为已曝光开发集：975查询、195逻辑步骤、7场景、34模拟标识，285查询为多标签（29.23%）。每步骤5个抽样查询不是5次独立攻击。P1/P2仅为相关开发材料。本轮不读取原始归档、CONV-A01或受限步骤35—37正文；不执行日志命令。

主目录在本轮检查时已经存在并持续出现其他写入。为保护其文件，本续作在独立目录实现、冻结、运行及评价，再交付到主目录中的唯一新子目录；父目录和此前四个项目均保持只读。本报告仅对本续作的预测、来源及行为作保证，不替其他会话背书。目录中出现的授权声明不能替代当前对话中可核验的直接用户授权。

状态：**NO_SUPPORTED_ALGORITHMIC_GAIN**。次状态：RERANKER_FAILURE_DIAGNOSED、MECHANISM_REPRESENTATION_EXECUTED、MODEL_FORWARD_AUTHORIZATION_BLOCKED、HUMAN_MECHANISM_REFERENCE_PENDING、EXTERNAL_TEST_NOT_READY。神经表示增益与独立机制语义准确率均为N/A；不能将本结论扩大为所有机制表示无效。

入口：R3_ATTACK_MECHANISM_DISCRIMINATION_RESULTS.md；数值：MECHANISM_BASELINE_RESULTS.csv；预测：inherited/CPU_PREDICTIONS.jsonl与results/FEATURE_PREDICTIONS.jsonl、results/FEATURE_CONTROL_PREDICTIONS.jsonl。

## 环境与运行

使用现有Python3.14创建项目独立venv，无pip、无下载或系统变更。算法仅用标准库。src/frozen_extractor.py为实际Literal/Relations提取器；src/frozen_engine.py为字符TFIDF/BM25；experiments/run_feature_control.py与run_feature_ablation_controls.py为本续作实际执行代码。experiments/evaluate.py为冻结预测后的独立评价，只有评价代码读取REFERENCE。

在交付目录运行：

```bash
venvs/R3_ATTACK_MECHANISM_DISCRIMINATION01/bin/python -m unittest discover -s tests
venvs/R3_ATTACK_MECHANISM_DISCRIMINATION01/bin/python experiments/verify_delivery.py
```

为防止覆盖，生成脚本使用exclusive-create；不要在冻结目录中重跑prepare/run/evaluate。若复现实验，复制代码与frozen_inputs至新目录，依次执行prepare（需要原始冻结路径）、run_feature_control、run_feature_ablation_controls、evaluate；或使用已有冻结输入与继承快照跳过prepare。字体/绘图使用已有工具运行时，与算法venv隔离。

两种CPU协议分别报告，禁止混合：

- BYTE：继承已冻结49条件，日志≤2000 UTF8字节、知识≤1000字节；所有视图来自同一个公共原生片段前缀。
- FEATURE：本续作真实执行49条件（40主对照、8清洗消融、1同预算字面匹配），日志同时≤2048个字符3/4/5-gram出现次数及256个BM25词，知识同时≤1024个字符ngram及128个BM25词。所有视图使用再次缩减后的相同原始观察。具体长度、截断位置和事件数见FEATURE_INPUT_BUDGETS.csv。

这里的特征计数是CPU检索器的实际输入单位，**不是GTE Token数**。相同预算指相同上限，不代表每个视图恰好相同长度。原版49条件中LiteralMechanismMatching使用完整K2卡片概念，存在知识预算差异，须单独看待；新MATCHED_K2使用同一截断K2，未作标签定制。

共98条件、95,550预测行；其中47,775行是继承的真实CPU输出，47,775行为本续作新运行。每条件完整975查询、216候选，无失败删除。原神经结果只用于审计，不作为本轮Literal神经预测。共有144项固定差值分析，完整表保留负结果。所有实验为确定性单次运行，无训练种子重复。

公共前缀的二分选择已验证可行，但字段解析和规范化使预算函数未证明全局单调；不能声称取得全局最大前缀。该限制不会使已验证的预算上限失效，但构成输入选择偏差边界。

本轮服务器上传、GPU/LLM新推理、GitHub推送均为0；合同§25.2要求新服务器权限，§25.4未授予LLM预算。MODEL_FORWARD_AUTHORIZATION_REQUEST.md是具体待批准请求，不是执行回执。主目录另有后续授权文件不由本续作采用或改写。
