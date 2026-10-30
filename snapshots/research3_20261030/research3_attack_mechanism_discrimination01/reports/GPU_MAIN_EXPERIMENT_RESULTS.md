# 授权GPU主实验与严格分析

主实验真实完成：2固定模型×4视图×2知识=16条件，每条件975查询，共15600预测；合计CPU65+GPU16=81条件、78975条预测。所有Gold只在本地后评价读取。其余24神经条件不在此次授权内，保持NA。

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

本组神经表示对比没有获得经292项联合Holm校正后显著的正向增益。 正向显著表示检验0项，负向显著0项（Top10与MRR分别计数）。完整原始效应、SD、CI和p见ALL_CPU_GPU_CONTRASTS，不能按结果筛选最优条件作为确认性结论。

## 可比性与预算

Embedding对全部216技术排序。CE每条件使用**完全相同的旧canonical E1 Top20**，而非分别用新视图重取候选；候选Hit20=0.466667、Recall20=0.391420，构成CE最终命中的候选限制。CE与全空间检索比较是整体管线差异，不能全归因于评分器。旧原始E1排名与候选生成文本不等于本轮RAW。

四视图共享选定原生事实；冻结日志2000 UTF8 bytes、知识1000 bytes，不再按结果改前缀。实际Token已测并均未超过日志2048/知识1024；最大知识Token 278。Tokenizer truncation=False，无运行期静默截断。**同一上限不等于相同实际Token长度**；Literal的字段清洗、UNKNOWN和结构标签会改变信息表达、Token组成与长度，因此不能单独归因机制推理。有效原生事件与选取/截断位置见INPUT_BUDGETS、MECHANISM_SOURCE_TRACE和MECHANISM_LITERAL的char_range；所有模型共用这些冻结输入。

| tokenizer | view | N | mean | median | min | max | limit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| embedding | RAW | 975 | 322.0225641025641 | 339.0 | 73 | 561 | 2048 |
| embedding | LITERAL | 975 | 427.374358974359 | 465.0 | 83 | 521 | 2048 |
| embedding | LITERAL_PLUS_RELATIONS | 975 | 442.59076923076924 | 474.0 | 83 | 575 | 2048 |
| embedding | RAW_PLUS_LITERAL | 975 | 750.396923076923 | 801.0 | 157 | 905 | 2048 |
| reranker | RAW | 975 | 322.0225641025641 | 339.0 | 73 | 561 | 2048 |
| reranker | LITERAL | 975 | 427.374358974359 | 465.0 | 83 | 521 | 2048 |
| reranker | LITERAL_PLUS_RELATIONS | 975 | 442.59076923076924 | 474.0 | 83 | 575 | 2048 |
| reranker | RAW_PLUS_LITERAL | 975 | 750.396923076923 | 801.0 | 157 | 905 | 2048 |

机制卡与K2版本相同，但卡片可取完整知识后部，而原描述是前缀；标题、术语和可见知识分配仍有混杂。CPU已执行visible-prefix与同词频乱序控制；神经模型本次只授权两知识条件，未执行这些扩展控制，不能声称神经卡片收益已排除词汇因素。

## 评分语义

固定配置与新前向确认单输出 num_labels=1，断言每批logits形状(B,1)。两组预登记相关/无关对均按高logit正确区分，batch与single最大差 0.0；logits分别为[2.669921875, -2.541015625, 2.1640625, -2.62109375]。模型处于eval。只验证这4对，不宣称全部领域分数校准或完整CAM批次不变性。没有根据CAM成绩选择方向，没有实际运行SentenceTransformers wrapper。

历史5850条CE结果按原始ID/分数可重建。跨候选池同对分数最大差0来自缓存复用；新sanity批次测试是另一项有限范围检查，不能将二者混称为全量独立重复实验。上游截取的领域证据损失仍不能排除。

## 统计

神经分析问题在读取新GPU指标前登记于GPU_ANALYSIS_REGISTRATION：20组表示/知识、32组同视图神经对词汇、8组CE对Embedding，共60对比×Top10/MRR=120检验。与既有172项联合Holm校正292项；CPU原172项校正独立保留用于追溯。195个scenario+step簇，各5查询先平均；seed42，2000次bootstrap、5000次双侧signflip加1校正，不假设正态；一套确定性权重，无跨seed训练重复。脚本/场景依赖仍可能违反交换性，全部P0 EXPOSED_DEV，p和CI只作条件开发分析。

## 资源与权限

GPU0 A40；总实验墙钟 395.27秒；Embedding 227批；CE 54836个去重候选对、8248批，另8次公开sanity pair；峰值allocated 479.49MiB、reserved 728.00MiB。 新项目同名venv只读链接旧依赖；2模型权重SHA256与冻结记录相同；运行前四文件哈希逐项一致。无模型下载、无新增LLM、无Gold上传。新增磁盘实测见REMOTE_FINAL_RESOURCE_RECEIPT。授权范围2小时/156000候选对/1GB，完成后未扩大实验。

## 科研判断

NO-GO当前组合直接作为独立算法贡献。即使某个开发条件有数值提高，仍需排除清洗、Token与知识信息分配，完成独立证据审查和外部评价。BM25关系/动作标签没有文档posting，是评分接口未生效；神经模型可接收这些文本，但新增标签不自动成为合法技术约束。没有真实人工机制Gold，不能把原生引用一致性当语义支持准确率，也不能从技术错分直接定位“证据不可观察”。当前领域适配、标签可观测性和细粒度机制绑定仍是待区分的假设，本轮不启动训练/新规则。
