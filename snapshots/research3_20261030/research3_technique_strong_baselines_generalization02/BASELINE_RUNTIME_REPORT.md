# 运行与环境

五个新增算法环境：CharacterNgramTFIDF、WordCharacterHybrid、SourceWiseBM25、SourceWiseTFIDF、EvidenceLineFusion；各自Python3.12.14、标准库实现。TFIDF/BM25复用旧独立环境只读运行，未安装包或写旧目录。解释器、前缀、pip freeze/check保存在manifests/ENVIRONMENT_MANIFEST_V2.json。没有预训练嵌入权重可执行，不能把字符表示叫语义模型。

有效推理条件163项、Top10预测145355行；数字仅描述覆盖，不代表科研质量。每项命令/真实独立子进程退出码与输出见experiments/*receipt.json；P0六批融合的单独退出码未捕获，标NOT_CAPTURED，依完成run摘要、975输出数、知识/输入hash和逐条可评分完整性认证，未补造退出码。后续批次真实退出码均保存。

SOURCE融合InferenceTime为共享批次耗时（四方法一次执行），不可把各行相加当总耗时。详见results/RUNTIME_DETAILS.csv；原生run.json与stdout保留。耗时不是同运行成本比较。完整v2字符推理约122秒，资源本地CPU有界。

初次P1/P2未清洗输入的输出全部放experiments/INVALID_UNCLEANED_FIRST_RUN，状态INVALID_UNCLEANED_INPUT_DO_NOT_REPORT。它们未用于调参或最终表，修复后全部重建与重跑。没有以不合法初分数选优。

新LLM/API调用0、Token/API费用0、模型下载0、服务器修改0。日志/原攻击脚本从未执行。普通算法代码与经AST单独提取的官方采样函数等价检查不是攻击执行。

重跑按序：prepare_inputs.py、prepare_controls.py；数据安全读取datasets/build_v2.py；run_matrix.py、run_extensions.py、run_fusion_followups.py；register_fusion_runs.py、evaluate_runs.py、compare_protocols.py、method/exact_evidence_traces.py、summarize_delivery.py。P0六批主融合命令见各实验日志及METHOD_FORMAL_DEFINITION，CLI参数同followup。重跑会覆盖本轮派生文件，先复制本目录；不覆盖旧目录。
