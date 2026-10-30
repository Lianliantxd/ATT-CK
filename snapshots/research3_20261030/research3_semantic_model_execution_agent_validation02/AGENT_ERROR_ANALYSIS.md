# Agent错误及分母

新增73个条件=1最小门槛+48预注册V3条件+24后注册V4静态控制。有效提交17，失败56：32次最终排序重复ID、20次完整输入在调用前超8192、4次实际请求超时。49份原生final中32份含重复技术ID，共144次重复出现；没有事后去重或补齐。25份其余原生响应为动作决策。超时没有原生final，不能算模型已给出语义错误答案。20个调用前context失败也不能算真实LLM语义0分。

Agent V3十二例有2条合法最终Episode，1条Top10命中。有效分母Top10=50%、MRR=.25；全12个实际调用条件保留失败为8.33%、.041667。差异来自分母，不能用前者与12条静态结果直接比较。主Pilot原始48条件全部登记，但39失败、9完成；加最小门槛才是10/49。V4静态7/24完成，4次超时计费；超时的后台实际结束时刻未知。

| static_scope | static_method | valid_same_case_pairs | static_Top10 | agent_Top10 | static_MRR | agent_MRR |
| --- | --- | --- | --- | --- | --- | --- |
| PAIRED_PILOT | A0_DIRECT | 1 | 0.0 | 0.0 | 0.0 | 0.0 |
| PAIRED_PILOT | A1_STATIC_BM25_LLM | 1 | 0.0 | 0.0 | 0.0 | 0.0 |
| PAIRED_PILOT | A2_FIXED_QUERY_LLM | 0 | NA | NA | NA | NA |
| CONTEXT_FIT_STATIC_V4 | A0_DIRECT | 0 | NA | NA | NA | NA |
| CONTEXT_FIT_STATIC_V4 | A1_STATIC_BM25_LLM | 2 | 0.5 | 0.5 | 0.25 | 0.25 |
| CONTEXT_FIT_STATIC_V4 | A2_FIXED_QUERY_LLM | 0 | NA | NA | NA | NA |

V3严格同案合法A1/Agent交集只有1例，双方Top10=0；V4 A1/Agent交集2例，双方Top10=.5、MRR=.25，简单静态查询复现了唯一命中。A2无合法同案Agent交集，NA。不能用“Agent .5 vs Static 0”的不同有效案例集合宣布收益，也不能据2例宣布Agent普遍无效。

真正可确认的新增能力：固定模型发起授权只读查询，完整反馈进入后续模型输入、合法引用返回事件、提交Top10、独立评价，共3个Episode通过。模型是否理解区别性证据、忽略反馈或因果改变排名仍UNRESOLVED；单纯重复获取、过早停止或查询不相关需要逐条机制判据，不能仅由错分归因。返回完整性已证明，不等于内部语义利用已证明。

新请求78/80，74份原生回执；已知输入342841、输出11981；含4次超时保留上限输入370436、输出14029。请求跨度82.28分钟，全部新请求在90分钟内结束等待。超时后台完成时间无法确认；随后无prompt卸载控制见LOCAL_MODEL_STOP_RECEIPT，ps为空。卸载控制约在首请求后90.9分钟，不能据此虚构超时推理在90分钟前已完成，也没有在90分钟后新增推理请求。
