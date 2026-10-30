# Cross-Encoder取证审计

结论：未在冻结源码和保存分数中发现评分方向、索引或候选归一化错误；未重新执行模型，不能给出完整运行时无缺陷证明。

官方[模型卡](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base)使用eval模式、query在前document在后及标量raw logit。更高分代表更相关，方向未按CAM分数事后选择。固定[revision配置](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base/blob/f7481e6055501a30fb19d090657df9ec1f79ab2c/config.json)为ModernBertForSequenceClassification，单LABEL_0，8192位置；此次核查是官方格式化页面静态配置，不是新下载权重运行。

20项检查：eval/inference_mode、对应tokenizer及revision、query-doc顺序、文本对格式、单标量维度、方向、无取负、无错误正负类、无非单调变换、降序、batch输出reshape、ID-score绑定、截断、描述保留、固定候选文本、固定候选分数、无重复、父技术归一、候选合法性、评价索引。源码与5850保存行一致。原始sigmoid在精确数学上单调，不改变排序；单logit不应作单元素Softmax。未进行新的单例/批量forward，故批次稳定性尚未独立验证。

独立复算140,015个去重(sample,technique)分数，跨池差0；5850行均按(-score,techniqueID)还原。相同候选文本和分数被缓存复用，因此一致性不能冒充独立批次重测。存在fp16分数并列；新增候选既可能以更高分，也可能通过同分ID次序占位。

pair tokenizer为truncation=False、pair≤8192；上游日志2048实际Token、技术描述1024实际Token，65项描述曾截断。K增加不改变相同pair，故排除“因K改变同pair截断而降级”这一解释；**不能排除上游截断造成普遍信息损失**，不能排除领域适配问题。

来源为旧项目冻结run_neural_gpu.py、运行协议、模型下载回执、NEURAL_INPUTS和完整raw_logits；不更新模型。固定CE revision f7481e6055501a30fb19d090657df9ec1f79ab2c；Embedding e7f32e3c00f91d699e8c43b53106206bcc72bb22。

原Embedding固定窗口E3 Top10=30.26%不是本CE候选的E1前缀。匹配候选输入E1 Top10=28.72%，Top1=3.79%，MRR@10=.10667。不能把E3、旧历史词汇8.62%与本次不同预算CPU表当成同输入因果对照。

详见RERANKER_SCORING_VALIDATION.json、CANDIDATE_SCORE_CONSISTENCY.csv、CANDIDATE_RANK_TRANSITIONS.csv及results/NEURAL_CANDIDATE_DIAGNOSTICS.csv。
