# 输入泄漏审计

原始llm_queries正文中检测到2844次T四位数字串，882条查询经作者清洗后改变。历史响应存储的prompt是清洗后的文本：因此直接拿query原文做基线会与LLM历史输入不一致，并可能泄漏audit key答案。本轮严格照get_llm_responses.py八条正则复刻，所有可用历史prompt逐条配对成功。

Clean Official View和Strict No-Label View都不含ground_truth/metadata/scenario/variant/step/cmd/AttackMate字段，固定指令前缀移除。严格视图补删显式技术ID及mitre/technique/tactic字段。本次两视图完全相同（strict_changed=0；正则T-ID残余0）。命令、路径、程序名、端口、系统调用、Web请求仍保留。

预测器独立进程只接受{sample_id,text}；sample_id原样返回，不用于排名；worker不打开标签、历史响应或测试映射。公开候选文档来源与版本冻结，ID用于索引不拼进检索正文。KnowHow使用公开字典，不读测试GT。评价由父进程单独配回Reference View。

Metadata-only诊断只用simulation_id和step_id经同一BM25名称检索，Top1=0.5128%、Top10=5.6410%。这一个弱诊断不能证明不存在更复杂捷径；若允许用官方label_key查表会得到答案，该行为明确禁止。

本轮已做结构与显式标签字段审计；未对全部自然语言嵌入答案逐人工复审，不能认证完全无隐性提示词泄漏。仓库公开历史模型也可能有预训练污染，无法据现有材料排除。
