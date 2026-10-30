# LLM增量价值

真实本地固定模型已完成研究推理，但没有支持语义能力增益的充分证据。V2事后资源审计视图仅两个episode有四个单轮条件；DIRECT、KNOWLEDGE20、RETRIEVAL20、STATIC_S Top1/Top10/MRR均0，已调用失败保留，另外五场景的缺失不计0分。不是全量开发成绩，更不是外部测试。

V1非自适应探索中DIRECT4/14已执行且4个重复ID等无效失败；KNOWLEDGE4执行2失败，Top10=1/4、MRR=1/36；RETRIEVAL20/50/100各4执行、Top10均0；STATIC_S4执行2失败、Top10=0。完整Top5、P/R/F1、逐失败、分组和真实成本见LLM_TECHNIQUE_RESULTS.csv与results/LLM_ERROR_DETAILS.csv。某个技术进入Top9不证明知识独立作用；极小样本、失败和顺序缺失会主导比例。

这不是“LLM普遍弱于字符检索”的证据；小型量化模型、短观察、部分知识、structured JSON限制、输出验证失败和候选缺失都可能影响结果，尚未有逐机制因果消融。RETRIEVAL改变候选大小与描述长度，不能纯归因语义重排。不能从模型解释推断真实逻辑推理过程。

作者历史GPT-5.5仅AUTHOR_HISTORICAL_RECALCULATION、P0 975查询，Top1/Top10/MRR=40.92%/66.67%/约0.496；新本地模型是P2小pilot，模型、输入、预算、候选知识、数据版本皆不同，不作性能差值或泛化比较。
