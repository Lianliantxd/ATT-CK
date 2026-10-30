# Embedding执行阻断与可分析范围

四种候选Embedding均未发现完整的合法本地权重/tokenizer；新模型下载未获授权。真实Embedding预测0，所有准确率、召回、模型Token、内存与模型错误数均为N/A，而非0。没有可命名的“最强Embedding”，不能评价是否超过字符TF-IDF。

输入工程已经完成：P0 975、P1 975、P2 Sampled 385，共2335条；V0–V3共享选中片段，prefix/window各最多2048 regex代理Token。截断281/975、274/975、103/385；不是实际模型tokenizer计数。片段来源、行号、char区间及哈希保存在semantic_models/input_views与data_manifests/NEURAL_INPUT_PROTOCOL.json。无法以输入文件存在证明结构化或分块有效。

GTE/Qwen embedding与GTE reranker有未经过真实权重的离线适配入口。BGE Dense/Sparse/Multi-vector、Jina及Qwen reranker保留INTERFACE_PENDING；没有把未实现的模型接口宣称已部署。手工数值聚合测试不是向量实验。

当前仅可分析冻结词汇召回错误（见results/LEXICAL_CANDIDATE_FAILURES.csv）；不能把它归因于预训练语义模型。未创建空模型环境冒充部署。
