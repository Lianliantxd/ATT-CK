# 冻结模型继承与完整分数重建审计

状态：SCORE_RECONSTRUCTION_READY。旧交付清单1938项内容SHA-256及字节数全部匹配；378份checkpoint全部存在、哈希相符、可加载且数值有限。通过只读绝对路径继承，未复制或改写旧权重。

复用真实975×768日志向量与216×768公开技术向量；没有新GPU前向、模型下载、训练更新或LLM调用。ATT&CK知识版本为ATTACK_16_1；源知识及模型修订、权重、特征、训练代码、split与各checkpoint哈希见FULL_216_SCORE_MATRIX_MANIFEST.json。

| 折 | 唯一训练步 | Seen技术 | Unseen技术 | 内验证查询 | 外保留查询 |
|---|---:|---:|---:|---:|---:|
| fold_heldout_1 | 124 | 56 | 160 | 125 | 220 |
| fold_heldout_2 | 122 | 60 | 156 | 225 | 130 |
| fold_heldout_3 | 128 | 66 | 150 | 95 | 230 |
| fold_heldout_4 | 174 | 75 | 141 | 10 | 95 |
| fold_heldout_5 | 147 | 69 | 147 | 230 | 10 |
| fold_heldout_6 | 137 | 66 | 150 | 60 | 230 |
| fold_heldout_7 | 137 | 56 | 160 | 220 | 60 |

Seen/support仅逐折读取合法one_view_train的标签，支持单位为唯一逻辑步骤。五个replica未重复计数。训练r0、全部内验证及全部外保留查询分别按旧推理批次形状计算，输出42份统一NPZ、126个B3/B4/B5模型条件。各NPZ的完整列顺序固定为216技术ID字典序。训练和验证/保留元数据字段经过白名单，仅训练Gold进入类别统计；没有打开内验证/外保留reference文件。历史split JSON本身包含旧标签汇总，程序只取字段白名单，未使用这些汇总。

B3在未见类别无分类器：NPZ写NaN、JSON写null，availability=false，状态NO_SUPERVISED_CLASSIFIER。旧-1e6只在历史输出复算副本内重建以核对旧排名，未写入可融合B3矩阵。这确认STRUCTURAL_UNSEEN_EXCLUSION，而非GTE主干遗忘。B4/B5为所有216类计算有效投影分数，其未见排序退化需要后续独立评价解释。

共比较53337条历史预测（含B1全部975条以及B3/B4/B5训练r0、内验证和外保留行），完整216排名差异0条，已保存Top10分数非零差异0条，最大绝对差0。逐条差异保留于inherited/PREDICTION_RECONSTRUCTION_DIFFERENCES.jsonl；不修分数、不改排序。历史文件仅保存Top10分数与Top216排名，所以数值一致性核验限于保存的Top10位置；完整216数值来自真实checkpoint重新前向，未由Top10反推。

NPZ内含sample_ids、logical_step_ids、partitions、technique_ids、gte_scores（float32）、b3_scores/b4_scores/b5_scores（float64）、seen与support。partitions为TRAIN、VALIDATION、HELDOUT。JSONL为查询级向量格式，每行的technique_ids与各score/support/availability列表逐位对齐；不含该查询Gold。FROZEN_GTE_SCORES有2909行，B3_SUPERVISED_SCORES有17454行。

TRAINING_CLASS_PRIORS保存训练步prevalence、标签总质量比例以及明确命名的Laplace平滑列；这些是统计输出，具体融合用哪一列由主任务预注册，不在本脚本内根据结果选择。

本重建器未执行新融合、参数选择或性能评估。新结果资格仍为已曝光场景的开发研究。
