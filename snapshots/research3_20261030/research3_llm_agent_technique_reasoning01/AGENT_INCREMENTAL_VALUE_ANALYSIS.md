# Agent增量判断

结论：AGENT_NO_SUPPORTED_INCREMENTAL_GAIN，含义是目前证据不支持收益，不是证明Agent无效。修复后有效LLM Agent executed=0，不能把未执行当Top10=0；同模型静态/动态有效配对交集N=0。早期6条真实adaptive条件因工具反馈协议缺陷隔离，得分N/A；它们的查询、耗时仍是真实成本。未执行V2状态保存在results/AGENT_NOT_EXECUTED_CONDITIONS.jsonl，不伪造轨迹。主AGENT_TRAJECTORIES.jsonl为空；V1真实无效轨迹位于experiments/PILOT_V1_INVALID_AGENT/AGENT_TRAJECTORIES.jsonl。

全部385个P2 episode的7条件确定性对照已经完成；终端排序同一字符TF-IDF、初始256代理日志、共享合法池。动态启发式依据观察实体与竞争技术描述选查询，是可复现工具策略，不是LLM Agent。S：动态Top1/Top10/MRR=0.088312/0.296104/0.138544，静态=0.101299/0.314286/0.147408。M：动态=0.096104/0.319481/0.145913，静态=0.088312/0.322078/0.143334。M动态Top1/MRR稍高但Top10低，无一致优势。

相同采集上限不等于相同消耗：S静态/动态平均返回1374.19/1357.72代理、新事件10.70/8.84；M为2325.46/2458.91、新事件19.49/12.99。这些对照说明更多查询/动态选词未自动转为收益，不证明“区别性证据”策略的必要条件已经被充分检验。七场景簇敏感性分析与图在analysis-output，无独立泛化主张。

没有有效固定LLM配对、未运行Embedding、未完成独立测试，因此不提出新算法贡献，不增加反思角色或强化学习。
