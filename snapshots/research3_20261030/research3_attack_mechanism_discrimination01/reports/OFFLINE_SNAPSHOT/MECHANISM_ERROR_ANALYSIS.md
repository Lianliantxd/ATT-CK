# 实际错误与可确认范围

原描述下CHAR Raw14.87%→Literal9.13%，BM25 Raw13.54%→Literal17.03%；后一差的95%逻辑步骤bootstrap CI跨0、Holm p1。关系后BM25与Literal完全相同；实际词表审计发现新增关系/动作规范化标记没有知识文档posting，BM25忽略该通道。这是接口未生效，不是关系语义的有效否证。CHAR有小幅变化但不足归因。不能据此扩充关系图或断言所有关系模型无效。

可确认原因包括：输入进一步截取；许多行缺少可解析动作/主体/对象，Literal会显式UNKNOWN并丢掉未结构化文本；元字段与normalized标签占用文本。是否因此丢了区分具体技术的关键证据，需要独立人工证据判断，不能由错分反推。FILE_PATH_ROLE_UNRESOLVED和PROCESS_REFERENCE_UNBOUND_LIFECYCLE都没有被提升成攻击结果。

机制卡有若干开发性数值提升，但标题、术语、1000字节分配和源片段选择共同改变。词序控制下BM25四视图全部975例完整216排名一致，说明当前检索不利用卡片结构。CARD_PREFIX_ONLY有时更好、有时更差，不能挑一个最高值当新算法。LiteralMechanismMatching Top10仅4.31%，不是可靠技术机制支持判别器；Jaccard分母是相似度长度归一化，不能解读为缺失日志对技术的反证。

30例逐案记录在diagnostic_30/CASE_ANALYSIS.csv，按旧输出分层且已暴露，不能从30例推总体准确率。步骤Gold仅评价技术排名，不认证逐行主体/对象/成功或因果。当前“证据不可观察”、语义歧义、时序/身份不足、标签—日志对齐问题全部仍UNRESOLVED，人工状态PENDING。新GTE/CE机制条件没有授权而未执行，不能以旧RAW输出替代。
