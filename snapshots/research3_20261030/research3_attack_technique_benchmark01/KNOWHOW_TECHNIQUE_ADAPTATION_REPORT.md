# KnowHow知识字典适配

复用../research3_baseline_reproduction01/algorithms/KnowHow/original_source/tech_dic.txt，哈希见manifests/KNOWHOW_ADAPTATION.json。固定已有官方提交19a549cf3e8affd8da66004dbf2d566a34f0589c。安全ast.literal_eval读取纯字典，没有运行eval、日志命令或原techtag入口。185父技术、11803非空短语（保留原重复），只允许216候选；其余候选得0。

适配评分：严格公共日志正文中每短语出现记1，跨子技术父级累加，按得分降序及ID升序Top10。这是本项目改写排名接口，不是作者原字段分数、完整嵌入KnowHow、原论文图/攻击意图结果。独立KnowHow环境运行，输入与其他方法相同，日志标签不进入。

Top1=1.13%，Top5=8.41%，Top10=21.03%，MRR=0.0519。词典存在短片段、重复及一般词，共现可能产生弱区分性；本轮未手工删改以迎合测试答案。其知识量、来源版本与BM25不同，不能归因全为排名机制。

完整KnowHow仍缺CTI/CKD、模型/训练、配套原始图标签和评价配置。旧139 Fact上的分数未混入本表。
