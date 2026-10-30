# 语义模型独立能力判断

已确认：固定GTE Embedding与真实Cross-Encoder均完成975查询/195逻辑步骤评价，候选216父技术。Embedding E1比matched TF-IDF的Top100 CandidateHit高9.13个百分点（89.64% vs80.51%），表明更广候选覆盖的开发性价值；早期排名没有稳定增益。窗口E3提高部分Top10，但MRR不超过matched TF-IDF。字段展开与max/mean分块没有一致改善。

真实CE仅在Embedding Top20带来Top10开发性净增5.03个百分点，MRR下降；Top50/100明显退化。它不是稳定排序改进，更不是创新或泛化证据。正确候选进入池后仍大规模排错，研究重点应从“继续扩大召回”转向机制判别及可观测证据与定义的对应。该解释是研究决策，具体错误语义原因尚未验证。

P0=EXPOSED_DEV，P1/P2=RELATED_DEVELOPMENT_DATA。作者GPT-5.5历史Top10=66.67%属于公开预测复算，没有本轮外部模型调用，不能做新LLM成绩。外部独立测试未就绪。
