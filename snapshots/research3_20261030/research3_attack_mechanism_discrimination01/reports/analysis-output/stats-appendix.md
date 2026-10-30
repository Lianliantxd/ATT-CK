# 统计附录

神经分析问题在读取新GPU指标前登记于GPU_ANALYSIS_REGISTRATION：20组表示/知识、32组同视图神经对词汇、8组CE对Embedding，共60对比×Top10/MRR=120检验。与既有172项联合Holm校正292项；CPU原172项校正独立保留用于追溯。195个scenario+step簇，各5查询先平均；seed42，2000次bootstrap、5000次双侧signflip加1校正，不假设正态；一套确定性权重，无跨seed训练重复。脚本/场景依赖仍可能违反交换性，全部P0 EXPOSED_DEV，p和CI只作条件开发分析。



完整292检验见results/ALL_CPU_GPU_CONTRASTS.csv。正向或负向报告均保留，不事后删除不利结果。实际Token逐视图表见results/ACTUAL_TOKEN_SUMMARY.csv。
