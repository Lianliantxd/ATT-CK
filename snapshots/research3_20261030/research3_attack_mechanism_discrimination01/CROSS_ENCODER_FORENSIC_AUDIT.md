# Cross-Encoder实现与适配审计（授权主实验后）

历史保存分数/索引/排序未发现足以解释候选池扩大的实现错误。固定配置与新前向确认单输出 num_labels=1，断言每批logits形状(B,1)。两组预登记相关/无关对均按高logit正确区分，batch与single最大差 0.0；logits分别为[2.669921875, -2.541015625, 2.1640625, -2.62109375]。模型处于eval。只验证这4对，不宣称全部领域分数校准或完整CAM批次不变性。没有根据CAM成绩选择方向，没有实际运行SentenceTransformers wrapper。

| 项目 | 检查 | 状态 | 边界 |
| --- | --- | --- | --- |
| 1 | eval模式 | NEW_RUNTIME_EVAL_VERIFIED | 新sanity探针eval=true；历史eval仍基于冻结源码 |
| 2 | Tokenizer | SOURCE_AND_REVISION_VERIFIED | 两个模型各自固定目录；hash收据继承 |
| 3 | 文本顺序 | SOURCE_VERIFIED | 日志query在前、技术document在后，与模型卡pair语义一致 |
| 4 | 文本对格式 | SOURCE_VERIFIED | Tokenizer(query_list,document_list)，无自定义prompt/instruction |
| 5 | 输出维度/标签 | RUNTIME_SINGLE_OUTPUT_VERIFIED | 固定config单标签；所有新批次断言logits(B,1) |
| 6 | raw logit方向 | DOCUMENT_AND_PUBLIC_SANITY_SUPPORTED | 高logit区分两组预登记相关/无关对；不依CAM方向选择 |
| 7 | 分数反转 | SOURCE_VERIFIED_ABSENT | 无取负数或低分优先 |
| 8 | 正负类别 | SINGLE_OUTPUT_NO_CLASS_SELECTION | 只有一维logit，无正负类别切片 |
| 9 | Softmax/Sigmoid | SOURCE_VERIFIED | 未跨候选Softmax，未作非单调分数处理；单调Sigmoid不改变精确实数排名 |
| 10 | 排序方向 | SAVED_SCORES_ALL_PASS | 按(-score,ID)重建5850条件完全一致 |
| 11 | 跨批次 | LIMITED_PUBLIC_BATCH_SINGLE_VERIFIED | 4公开对batch/single差0；历史同对缓存一致不等于全量独立复测 |
| 12 | ID与分数索引 | SAVED_RECORDS_ALL_PASS | 每候选唯一ID对应raw_logit，按ID重建 |
| 13 | 模型输入截断 | SOURCE_VERIFIED_FALSE | Tokenizer truncation=False、pair长度断言；上游日志显式预算截取存在 |
| 14 | 描述截断 | UPSTREAM_TRUNCATION_PRESENT | 65份知识描述在共同1024token预算下截取，整体影响UNRESOLVED |
| 15 | 不同K输入 | HASHES_ALL_PASS | 同对日志hash/revision一致；知识版本与预算固定 |
| 16 | 不同K分数 | ALL_EXACT_EQUAL | 交集对最大差0；来源是同一cached forward |
| 17 | 重复候选 | SAVED_SETS_ALL_PASS | 每池K个不同候选 |
| 18 | 父技术 | SAVED_IDS_ALL_PASS | 216父技术，不新增子技术归一化 |
| 19 | 无效候选 | SAVED_IDS_ALL_PASS | 候选ID来自冻结216集合 |
| 20 | 评价索引 | RECONSTRUCTED | 同sample_id与冻结Gold独立关联；旧MRR@10口径保留 |

官方[固定revision模型卡](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base/blob/f7481e6055501a30fb19d090657df9ec1f79ab2c/README.md?code=true)支持Transformers raw logits高值相关评分；[CrossEncoder接口](https://sbert.net/docs/package_reference/cross_encoder/model.html)的单调activation并不要求反转排序。当前实际实现为固定Transformers pair评分，不声称执行了wrapper对照。历史保存记录与新运行配置、sanity分别保留，未修改旧结果。

本轮实际无Tokenizer静默截断，输入前缀/字节分配仍会损失信息。未将域错配、截取、标签可观测性或机制理解中的任一假设当成已确认原因。
