---
type: results-report
date: 2026-10-27
experiment_line: R3_semantic_model_agent
round: validation02
purpose: actual-model-and-agent-validation
status: complete_with_pilot_qualification_limits
source_artifacts:
  - reports/analysis-output/analysis-report.md
  - reports/analysis-output/stats-appendix.md
  - reports/analysis-output/figure-catalog.md
  - reports/analysis-output/provenance.json
linked_experiments:
  - manifests/NEURAL_RUNTIME_PROTOCOL.json
linked_results:
  - EMBEDDING_REAL_RESULTS.csv
  - RERANKER_REAL_RESULTS.csv
  - AGENT_PAIRED_COMPARISON.csv
---

# R3 预训练语义模型实测与Agent验证结果

主状态 **RERANKER_BASELINE_READY**。次状态 **SEMANTIC_EMBEDDING_BASELINE_READY**、**AGENT_END_TO_END_VALIDATED**。两种真实预训练模型完成全P0统一评价；本地小LLM完成3个有效Agent Episode。配对矩阵全部登记，但大量输出与上下文失败使完整科学比较仍不充分。没有已证明的Agent增益，也没有独立外部测试。

本轮最重要的变化是“没有模型实测”已被解决。GTE具有较高Top100候选覆盖，但早期排名未稳定超越词法基线；CE在Embed20改善Top10、损害MRR，候选增大后明显退化。当前证据支持优先研究技术机制判别和可观测证据约束，暂不支持增加Agent复杂度或宣布新算法创新。

## 实验资格、权限与输入

P0共195合法逻辑步骤、975查询、7场景、34执行标识、216父技术，是EXPOSED_DEV。P1/P2来自相关CAM-LDS执行，为RELATED_DEVELOPMENT_DATA，不是三个独立数据集。P2合法池680280行这一继承事实未用重复385×7实验替代新结果。旧目录保持只读，最终校验256份继承资产；受限场景1 PwnKit步骤35–37及别名没有读取/上传，CONV-A01仍未授权。

用户后续明确授权覆盖原服务器只读限制，仅在指定项目安装两种GPU模型及项目名venv；另外明确批准上传975条清洗P0预测输入与公开K2。上传不含Gold和原始归档。授权前自动审查曾因缺少日志外传授权拒绝上传；取得用户明确批准后才成功，未绕过。安装/下载的网络超时和tokenizer续传尺寸错误均保存并有限恢复，最终固定权重官方哈希通过。

所有GTE条件共用同一原生观察片段和公开知识文本：日志同时满足两个实际tokenizer的2048上限，知识定义1024实际Token上限，216候选不变。E1原生前缀；E2真实字段/来源元数据加完整native（有重复，无新增观察）；E3固定窗口直接编码；E4/E5同窗口的256实际Token分块max/mean。原始日志长度分词触发过8192警告，实际forward另有长度断言，未把超长原文送入模型。

Embedding官方CLS+L2；CE是联合编码分类raw logit，分别重排canonical E1 Embedding和matched lexical的Top20/50/100。选择canonical E1池在Gold前固定，没有根据最佳Embedding成绩换池。FP16、batch8、GPU0、CPU2线程，离线加载、禁止远程代码。两模型先单例/8例预检后全量；耗时54.46/1046.70秒，54,958个唯一pair。服务器未加载Gold，预测固定后本地冻结V1父技术评价，MRR为前10截断。

## 完整模型结果

| 方法 | N | Top1 | Top10 | MRR@10 |
| --- | --- | --- | --- | --- |
| E1_NATIVE_PREFIX | 975 | 3.79% | 28.00% | 0.1031 |
| E2_NATIVE_FIELDS_PREFIX | 975 | 3.08% | 22.67% | 0.0797 |
| E3_NATIVE_WINDOW_DIRECT | 975 | 6.15% | 29.85% | 0.1246 |
| E4_NATIVE_WINDOW_CHUNK_MAX | 975 | 3.79% | 27.18% | 0.0982 |
| E5_NATIVE_WINDOW_CHUNK_MEAN | 975 | 2.36% | 28.72% | 0.0913 |
| M0_MATCHED_E1_NATIVE_PREFIX | 975 | 9.23% | 28.51% | 0.1385 |
| M0_MATCHED_E2_NATIVE_FIELDS_PREFIX | 975 | 5.03% | 26.77% | 0.1008 |
| M0_MATCHED_E3_NATIVE_WINDOW_DIRECT | 975 | 8.41% | 26.67% | 0.1260 |
| GTE_RERANKER_EMBEDDING_TOP100 | 975 | 2.05% | 12.72% | 0.0427 |
| GTE_RERANKER_EMBEDDING_TOP20 | 975 | 2.05% | 33.03% | 0.0874 |
| GTE_RERANKER_EMBEDDING_TOP50 | 975 | 2.26% | 16.41% | 0.0522 |
| GTE_RERANKER_LEXICAL_TOP100 | 975 | 1.33% | 9.85% | 0.0295 |
| GTE_RERANKER_LEXICAL_TOP20 | 975 | 2.36% | 20.82% | 0.0582 |
| GTE_RERANKER_LEXICAL_TOP50 | 975 | 1.23% | 12.72% | 0.0357 |

原最强CharacterNgramTFIDF P0 Top1=8.62%、Top10=27.79%、MRR=.1294是继承的不同完整输入协议；本轮matched输入/知识预算下的TF-IDF见表，不混用。作者GPT-5.5历史预测40.92%/66.67%/.4960仅是作者公开预测复算，本轮没有外部模型调用。

E1 GTE未超过matched lexical；E3 Top10较matched窗口高3.18个百分点，但Top1低、MRR几乎持平且略低。字段展开、chunk max/mean没有一致收益。CE Embed20相对E1 Top10净增49条（5.03个百分点），但Top1/MRR下降；其余5种CE均没有稳定排序收益。

## 候选上界与误差

| 候选池 | K | CandidateHit | 无正确候选 | 重排Top10 | 升入Top10 | 跌出Top10 |
| --- | --- | --- | --- | --- | --- | --- |
| LEXICAL | 20 | 40.92% | 59.08% | 20.82% | 60 | 135 |
| LEXICAL | 50 | 61.44% | 38.56% | 12.72% | 65 | 219 |
| LEXICAL | 100 | 80.51% | 19.49% | 9.85% | 65 | 247 |
| EMBEDDING | 20 | 45.64% | 54.36% | 33.03% | 104 | 55 |
| EMBEDDING | 50 | 66.87% | 33.13% | 16.41% | 79 | 192 |
| EMBEDDING | 100 | 89.64% | 10.36% | 12.72% | 76 | 225 |

E1 Embedding Top100的any-Gold覆盖89.64%，多标签全部覆盖74.05%；窗口E3分别91.69%/76.41%。这是覆盖能力，不能等同技术正确判别。Embed100重排中有750条候选有Gold却没进入前十；词法100为689条。结构/命令/主体对象/尝试与成功等具体语义原因标UNRESOLVED，不能由分数反推日志缺失。

## 图与统计解释

![覆盖与排序](reports/analysis-output/figures/figure-01-main.png)

图1同时显示Top1、Top10和MRR：单看Top10会掩盖CE的靠前排序退化。它改变的研究判断是优先查候选内机制判别，而非只追求更大召回。

![候选上界与实际重排](reports/analysis-output/figures/figure-02-candidates.png)

图2将any-Gold候选上界与真实Top10分开：候选变多，正确技术进入池的机会增加，排序转化却下降。它不能证明某一具体语义原因，只定位失败发生的阶段。两图均为全975查询描述统计、单seed、无独立测试含义；矢量PDF/SVG同时交付。

逻辑步骤聚合195组，保留5查询相关性；13对比×2指标的探索性bootstrap CI、SD、sign-flip p和Holm p完整保存。CE Embed20 Top10差95%CI [.0021,.0985]、raw p=.0537、Holm p=.5906；不能只用正CI宣称确认性显著。场景/脚本共享还会违反步骤独立假设，因此所有推断限于暴露开发数据，不能写成外部泛化。无跨seed重复，不虚构mean±std；详细统计限制见stats-appendix。

## 历史LLM与本轮真实Agent

旧54原生响应中36final、18action；只有18个final科学合格（16静态RAG、2共享知识Direct）。24回传协议无效、12输出契约失败。知识/日志条件不统一，4个逻辑步骤、2场景，未证明LLM独立收益。历史成本与本轮分开，旧失败轨迹未修成有效结果。

新传输修复22项回放通过，0模型调用；真实原生模型响应另计74份、78次尝试。完整GGUF输入正文与后端context前缀74/74一致。3个有效Episode包括最小门槛、v2_sampled_0297和v2_sampled_0326；模型发起只读查询、接收实际完整反馈、引用合法返回事件、提交Top10并独立评价。结构性闭环成立，但内部语义利用及因果排序更新未由此证明。

V3预注册12例×4条件已全记录；A0共享相同部分公开知识，没有额外日志；A1 BM25、A2固定关键词、A3模型选择查询。额外证据同时cap2048实际GGUF与2048 regex代理、20新行、2查询；计算调用另记。V3静态完整封装导致上下文溢出，另注册V4全部24静态控制，减少最大条数，不增加Token预算、不重跑Agent、不查看GT修改案例，不重置额度。V4为posthoc开发性工程控制，不能冒充预注册。

73条件中17有效、56失败：32重复ID、20调用前上下文失败、4实际请求超时。严格有效同案比较：

| static_scope | static_method | valid_same_case_pairs | static_Top10 | agent_Top10 | static_MRR | agent_MRR |
| --- | --- | --- | --- | --- | --- | --- |
| PAIRED_PILOT | A0_DIRECT | 1 | 0.0 | 0.0 | 0.0 | 0.0 |
| PAIRED_PILOT | A1_STATIC_BM25_LLM | 1 | 0.0 | 0.0 | 0.0 | 0.0 |
| PAIRED_PILOT | A2_FIXED_QUERY_LLM | 0 | NA | NA | NA | NA |
| CONTEXT_FIT_STATIC_V4 | A0_DIRECT | 0 | NA | NA | NA | NA |
| CONTEXT_FIT_STATIC_V4 | A1_STATIC_BM25_LLM | 2 | 0.5 | 0.5 | 0.25 | 0.25 |
| CONTEXT_FIT_STATIC_V4 | A2_FIXED_QUERY_LLM | 0 | NA | NA | NA | NA |

V3 A1/Agent N1均未命中；V4 N2均Top10=.5、MRR=.25。A2同案合法交集为空，NA。Agent有效分母2例Top10=.5，与全12例实际调用条件失败保留Top10=.0833不能混用。当前为“未支持Agent独立增益”，不是普遍否定。完整48条件登记不等于全部12组均具评价资格，不选择AGENT_PAIRED_PILOT_COMPLETED或AGENT_INCREMENTAL_GAIN_SUPPORTED_ON_DEV作为终态。

## 调用、Token与预算

| scope | method | planned_conditions | completed | attempted_model_requests | native_calls | unknown_timeout_requests | input_tokens | output_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONTEXT_FIT_STATIC_V4 | A1_STATIC_BM25_LLM | 12 | 4 | 11 | 9 | 2 | 55949 | 1874 |
| CONTEXT_FIT_STATIC_V4 | A2_FIXED_QUERY_LLM | 12 | 3 | 12 | 10 | 2 | 69890 | 2144 |
| MINIMAL_GATE | A3_ADAPTIVE_LLM_AGENT | 1 | 1 | 2 | 2 | 0 | 7688 | 254 |
| PAIRED_PILOT | A0_DIRECT | 12 | 5 | 12 | 12 | 0 | 37090 | 2654 |
| PAIRED_PILOT | A1_STATIC_BM25_LLM | 12 | 2 | 5 | 5 | 0 | 30001 | 1045 |
| PAIRED_PILOT | A2_FIXED_QUERY_LLM | 12 | 0 | 0 | 0 | 0 | 0 | 0 |
| PAIRED_PILOT | A3_ADAPTIVE_LLM_AGENT | 12 | 2 | 36 | 36 | 0 | 142223 | 4010 |

全新78/80次推理尝试，74条原生回执；输入342841、输出11981，4次超时实际成本未知。按请求预留上限计输入370436/500000、输出14029/45000；失败不按0消费。首请求至最后等待结束82.28分钟。没有重置旧预算或在结束后追加推理。卸载控制（无prompt）约在首请求90.9分钟完成，ps为空；4次超时后台真实结束时刻无法核实，不能声称后台耗时已严格验证。详见逐请求ledger、LOCAL_MODEL_STOP_RECEIPT和成本CSV。

Agent V3调用36次，对比A0 12次为3倍；输入约3.83倍，额外日志cap相等不等计算相等。静态调用前失败造成低计算量，不能解释成低成本同质量。GPU forward与本地生成模型请求分开计量。

## 科研结论与下一步

已确认：真实模型基线、候选内排序失败定位、完整Agent工程闭环。合理推测：通用相关性与日志机制/证据可观测性存在错配。研究判断：优先机制判别与领域表示诊断，暂停增加Agent角色、reflection和RL。没有正式验证的新算法机制。EXTERNAL_TEST_NOT_READY。

下一轮先冻结30个开发诊断步骤，盲标主体/动作/对象、尝试/结果及不足证据，固定原文与可追溯literal机制视图，比较TF-IDF/GTE/CE同预算；该诊断不当测试集。再资格核查真正独立执行/脚本或外部数据。固定小LLM需先解决输出可靠性、完整上下文容量与超时终止验证，才能扩大同预算Agent比较。新增推理须新预算，当前额度不续用。

## 45项逐条回答

### 1. 当前是否真正具备可运行的Embedding权重？

是；服务器两份固定GTE权重均完整并匹配官方SHA256，实际forward成功。

### 2. 具体有哪些完整模型？

GTE-ModernBERT Embedding、GTE-ModernBERT-Reranker及既有本地DeepSeek-R1-1.5B；7b已有缓存但本轮未使用。

### 3. 哪些模型只有配置或引用？

DistilBERT仅revision引用/锁文件；Qwen3-Embedding和BGE-M3在检查范围没有完整资产。

### 4. 哪些模型需要新增下载授权？

本轮两种GTE已获明确授权并下载，无需再次申请；其他新增模型未获本轮下载授权。

### 5. 本地计算资源是否满足运行条件？

本机M3/24GB统一内存已能运行小LLM CPU；GTE本轮使用授权A40 GPU，真实预检与资源峰值通过。

### 6. 是否真实运行Qwen3-Embedding？

否。未下载、未运行Qwen3-Embedding。

### 7. 是否真实运行GTE-ModernBERT？

是。固定revision e7f32e3c00f91d699e8c43b53106206bcc72bb22。

### 8. 是否真实运行BGE-M3？

否。未下载、未运行BGE-M3。

### 9. 最终实际选择了什么Embedding模型？

Alibaba-NLP/gte-modernbert-base，官方CLS+L2、768维、FP16模型/float32 cosine。

### 10. 是否完成全P0合法步骤评价？

是。全195合法逻辑步骤、975查询、216父技术、7场景、34执行标识；受限步骤未纳入。

### 11. Embedding的Top-1、Top-10、MRR分别是多少？

E1原生前缀3.79%/28.00%/.1031；E3窗口6.15%/29.85%/.1246；其余全条件见表。MRR为MRR@10。

### 12. 是否超过CharacterNgramTFIDF？

未稳定超过。E1 matched TF-IDF为9.23%/28.51%/.1385；E3 matched为8.41%/26.67%/.1260，Top10提升而Top1/MRR没有提升。历史27.79%输入预算不同。

### 13. 输入结构化是否提供增益？

未观察到本方案增益。共享片段字段展开E2 Top10=22.67%、MRR=.0797，比E1下降；原因未因果确认。

### 14. 长日志分块是否改善结果？

本方案没有。相同窗口直接编码Top10=29.85%，chunk-max27.18%、mean28.72%，MRR两者也低。

### 15. 是否完成Top20/50/100候选召回上界？

是，全部Embedding和matched TF-IDF在20/50/100的CandidateHit、macro label recall、all-Gold coverage已交付。

### 16. 是否存在合法可运行的Cross-Encoder？

是，固定GTE-reranker-modernbert-base，完整分类权重哈希通过。

### 17. Cross-Encoder是否完成真实推理？

是，两池×三个K，各975查询，真实联合编码logit，不是Embedding替代。

### 18. Cross-Encoder是否改善技术排序？

仅Embedding Top20的Top10升至33.03%，但Top1=2.05%、MRR=.0874均低于原E1；更大K退化，不能称全面排序改善。

### 19. 正确技术没有进入候选的比例是多少？

E1 Embedding Top20/50/100全无Gold比例54.36%/33.13%/10.36%；词法59.08%/38.56%/19.49%。这指任一Gold都没有，不等于漏掉任一多标签。

### 20. 上一轮54条LLM响应有多少具备有效评价资格？

18个最终排序合格：静态RAG16、共享知识Direct2；54中另有24回传协议无效、12输出契约无效。

### 21. 这些LLM响应是否真正使用相同输入条件？

没有全部同输入。知识、检索候选、额外日志及协议不同；不能汇总为同输入LLM语义收益。

### 22. 是否存在可确认的LLM额外语义收益？

没有可确认的独立收益。旧样本少且不等条件；本轮输出失败多，合法严格配对不足，未做证据因果干预。

### 23. 旧Agent工具回传问题的根本原因是什么？

V1只合并events，丢knowledge text/error/lexical metadata；V2仍在3500 bytes截知识，工具声明与模型所见不一致。

### 24. 修复后的工具结果是否真正进入模型下一轮输入？

是。完整消息哈希和原生后端context正文前缀在74/74原生响应逐条一致；有效Episode还核对实际tool结果及提交。

### 25. 工程回放测试是否通过？

是，22/22工程回放，0模型调用；与真实Episode分开记录。

### 26. 是否完成至少一个真实有效Agent Episode？

是，共3个：最小门槛1、主Pilot2。原生调用、完整回传、合法引用、Top10和独立评价俱全。内部语义利用仍未证明。

### 27. 如未完成，准确阻断是什么？

端到端门槛已完成；剩余阻断是大多数条件的输出重复、完整上下文容量和4次超时，正式完整有效配对不足。

### 28. 是否完成预先固定的小规模配对Pilot？

预先固定12例×4方法的48条件已全记录，但39失败。另V4后注册24静态条件7有效；不能说12组全合法完成。

### 29. 静态检索与动态Agent是否使用相同模型？

是，同本地固定DeepSeek digest、CPU设置、上下文及最终输出合同；静态方法与Agent均无外部LLM。

### 30. 是否保持相同合法日志池？

是，同一步Full-Authorized合法池，未读Gold/其他步骤/受限正文。

### 31. 是否保持相同新增证据预算？

是，同2查询、20新行、2048实际BPE与2048代理上限；不是实际内容完全相同。V4额外把最大可能返回数统一到10。

### 32. Agent是否能够主动查询区别性证据？

能够主动选工具、取回并引用事件；没有充分证据证明查询针对竞争技术的区别性条件或因果改变排名。

### 33. 动态Agent是否超越静态检索？

未证明。V3严格A1配对N1均未命中；V4 N2双方Top10=.5、MRR=.25。不能外推普遍无效。

### 34. 改善是否主要来自额外日志信息？

没有已成立的动态收益可供归因；缺少同事实删除/替换干预，不能判断来自额外日志还是语义判别。

### 35. Agent增加了多少模型调用与Token成本？

主Pilot Agent36调用、142223输入/4010输出；A0 12调用、37090/2654。调用3倍、输入3.83倍，成本不等。完整逐条件与超时预留见CSV。

### 36. 是否存在简单固定策略能够复现Agent收益？

在V4合法同案N2，简单BM25静态策略复现同样命中与MRR；只支持这两例。

### 37. 哪些错误来自候选召回不足？

可确认的E1 Top100完全召回缺失101/975；词法190/975。逐样本索引已保存。

### 38. 哪些错误来自LLM语义判别？

32个真实final因重复ID违反合同；合法错误排名存在，但主体/对象、状态变化等语义原因仍UNRESOLVED。不能由错分直接确定认知原因。

### 39. 哪些错误来自Agent查询策略？

策略层未证明区别性目标；成本增加已确认。错误查询、过早停止、忽略证据的因果归因尚未充分验证。

### 40. 哪些错误仍然无法归因？

标签可观测性、命令机制混淆、长文本截断是否删了关键证据、知识—动作错配、LLM内部证据利用等仍UNRESOLVED。

### 41. 当前是否有独立外部测试？

没有。EXTERNAL_TEST_NOT_READY；P0暴露开发，P1/P2相关执行数据不是独立外部测试。

### 42. 哪种方法具备继续研究的价值？

优先机制判别和证据可观测性约束，保留GTE候选覆盖的基线价值；领域表示需后续受控实验。

### 43. 是否存在能够正式提出的新算法机制？

尚无足够证据正式提出已验证新算法；成熟组件组合、工程修复、查询概率符号本身不是创新。

### 44. 是否需要继续研究Agent，还是优先研究领域语义表示？

暂停扩大Agent复杂度；优先领域机制/表示诊断，Agent保留到证据干预与更可靠输出后再检验。

### 45. 下一轮最应该开展的具体实验是什么？

冻结30个开发诊断步骤、盲标主体/动作/对象/尝试结果与不足证据，raw对literal机制表示、TF-IDF/GTE/CE固定预算对照；之后资格核查独立执行/外部数据。新增推理需新预算授权。

## 复现与交付索引

模型：MODEL_ASSET_AUDIT、MODEL_ENVIRONMENT_MANIFEST、MODEL_LOAD_TESTS、MODEL_DEPENDENCIES、MODEL_EXECUTION_STATUS；授权见三个manifests；服务器原生结果/输入映射/锁文件在results/server_gpu，代码固定SHA见运行协议。

预测与评价：EMBEDDING_REAL_PREDICTIONS/RESULTS/CANDIDATE_RECALL，RERANKER_REAL_PREDICTIONS/RESULTS/CANDIDATE_UPPER_BOUNDS；逐样本错误、排名转移、分场景/执行表和探索性统计在results。

LLM/Agent：旧54资格与回执审计；新native_receipts逐请求原生文件；AGENT_VALID_EPISODES、AGENT_PAIRED_COMPARISON、AGENT_COST_REPORT、NEW_LLM_CONDITION_RESULTS及ERRORS；V3/V4注册和源码哈希、回放测试及原生后端输入证明。

严格分析bundle为reports/analysis-output四份文档/溯源及两幅图。最终交付哈希和旧资产完整性以manifests/DELIVERY_SHA256.json及results/FINAL_VALIDATION.json为准。所有源码、预测、错误及负结果保留；完成后停止，不创建自动任务。
