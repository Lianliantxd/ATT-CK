# Embedding真实错误与不可归因部分

原生前缀E1的Top100仍无任一Gold比例10.36%；窗口E3为8.31%。Top100 CandidateHit分别89.64%/91.69%，不等于多标签全覆盖（74.05%/76.41%）。Hit、macro label recall、all-Gold coverage按不同定义全部交付。

E1与相同输入/知识预算的TF-IDF比较，Top10 28.00% vs28.51%，MRR .1031 vs.1385；E3与匹配窗口TF-IDF比较Top10 29.85% vs26.67%，MRR .1246 vs.1260。不能只挑Top10说模型全面改进。原历史最强TF-IDF 27.79%使用不同输入预算，保留但不是本轮matched对照。

共享原始片段的字段展开E2 Top10下降至22.67%；加入真实source/event_id/literal_fields及重复native没有新增观察，仍可能改变模型注意分布。这是合理假设，未被因果干预确认。窗口max/mean分块分别27.18%/28.72%，均低于同一窗口直接编码29.85%；分块输入相同，差别在聚合，但不能泛化所有分块方法。

逐样本可确认事实为候选缺失、Gold排名、实际可见Token、是否截断；见results/EMBEDDING_PER_SAMPLE_ERROR_AUDIT.csv和服务器NEURAL_INPUTS映射。相似技术混淆、命令语义未识别、关键证据被截断、标签不可观测、结构化理解失败都需要额外语义标注/受控反事实。本轮全部标UNRESOLVED，不用预测错误反推“日志必然缺失”。
