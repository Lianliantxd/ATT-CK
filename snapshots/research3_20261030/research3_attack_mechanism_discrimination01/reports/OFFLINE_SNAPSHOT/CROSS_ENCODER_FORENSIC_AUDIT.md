# Cross-Encoder实现与适配审计

结论：已保存的5850个条件能够按原始分数和ID完全重建，固定日志—候选对跨K/池分数最大差0；未发现足以解释扩大池退化的保存/排序错误。**不等于所有运行时适配问题已被独立排除**：本轮无新forward，未取得固定config正文或独立单例/批次对照。不得凭source flatten就宣称输出维度已重新验证。

| 项目 | 检查 | 状态 | 证据与边界 |
| --- | --- | --- | --- |
| 1 | eval模式 | SOURCE_VERIFIED | 冻结源码调用.eval；本轮无新运行时探针 |
| 2 | Tokenizer | SOURCE_AND_REVISION_VERIFIED | 两个模型各自固定目录；hash收据继承 |
| 3 | 文本顺序 | SOURCE_VERIFIED | 日志query在前、技术document在后，与模型卡pair语义一致 |
| 4 | 文本对格式 | SOURCE_VERIFIED | Tokenizer(query_list,document_list)，无自定义prompt/instruction |
| 5 | 输出维度/标签 | PARTIALLY_VERIFIED | 保存一对一scalar分数；未新forward，config正文未成功取回，不能独立排除原始flatten维度假设 |
| 6 | raw logit方向 | DOCUMENT_SUPPORTED | 官方模型卡以logits评分；高值相关，不按CAM得分选方向 |
| 7 | 分数反转 | SOURCE_VERIFIED_ABSENT | 无取负数或低分优先 |
| 8 | 正负类别 | NO_CLASS_SELECTION_IN_SOURCE | 源代码flatten；单输出维度仍待独立config核验 |
| 9 | Softmax/Sigmoid | SOURCE_VERIFIED | 未跨候选Softmax，未作非单调分数处理；单调Sigmoid不改变精确实数排名 |
| 10 | 排序方向 | SAVED_SCORES_ALL_PASS | 按(-score,ID)重建5850条件完全一致 |
| 11 | 跨批次 | SAVED_CACHE_CONSISTENT | 同一对缓存分数稳定；独立single/batch复测没有授权，不能称实测通过 |
| 12 | ID与分数索引 | SAVED_RECORDS_ALL_PASS | 每候选唯一ID对应raw_logit，按ID重建 |
| 13 | 模型输入截断 | SOURCE_VERIFIED_FALSE | Tokenizer truncation=False、pair长度断言；上游日志显式预算截取存在 |
| 14 | 描述截断 | UPSTREAM_TRUNCATION_PRESENT | 65份知识描述在共同1024token预算下截取，整体影响UNRESOLVED |
| 15 | 不同K输入 | HASHES_ALL_PASS | 同对日志hash/revision一致；知识版本与预算固定 |
| 16 | 不同K分数 | ALL_EXACT_EQUAL | 交集对最大差0；来源是同一cached forward |
| 17 | 重复候选 | SAVED_SETS_ALL_PASS | 每池K个不同候选 |
| 18 | 父技术 | SAVED_IDS_ALL_PASS | 216父技术，不新增子技术归一化 |
| 19 | 无效候选 | SAVED_IDS_ALL_PASS | 候选ID来自冻结216集合 |
| 20 | 评价索引 | RECONSTRUCTED | 同sample_id与冻结Gold独立关联；旧MRR@10口径保留 |

官方[固定revision模型卡](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base/blob/f7481e6055501a30fb19d090657df9ec1f79ab2c/README.md?code=true)给出Transformers logits和CrossEncoder用法；当前[CrossEncoder接口文档](https://sbert.net/docs/package_reference/cross_encoder/model.html)说明activation_fn作用于logits，单输出默认Sigmoid、允许模型配置覆盖。本轮不是实际运行SentenceTransformers wrapper；比较的是冻结Transformers实现与公开接口语义。Sigmoid的单调性只能说明排序不必反向，不能证明模型已校准或每对正确。

浏览器/联网连接失败，备用只读下载自动审查两次超时；没有权重/数据下载，也没有为了提高CAM分数反转logit。保留SCORING_DIMENSION_RUNTIME_NOT_REVERIFIED这个缺口。
