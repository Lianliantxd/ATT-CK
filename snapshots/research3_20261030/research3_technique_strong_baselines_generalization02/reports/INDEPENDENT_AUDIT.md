# 独立研究诚信与接口复核

2026-10-27。只读复核现有新目录代码、冻结哈希、合法清洗后 prediction/reference 及结果；没有访问受限 PwnKit 35—37 正文，没有加载外部模型或调用服务。唯一新增产物为本报告。

结论：**冻结、清洗标记、预测/标签分离、当前结果分母及抽样来源贡献检查通过。未发现当前成绩由标签泄漏、协议误配或错误分母造成的直接证据。** 发现过融合方法漏入配对分析的接口问题，已即时通知执行者并确认修复。仍有证据 trace 解释及登记器防护的限制，见后文；本审计不是独立泛化性能认证。

## 实际检查结果

| 检查 | 结果 |
|---|---|
| P0 冻结清单 | `manifests/P0_FREEZE.json` 共21项；逐项重新计算 source 与 frozen_path SHA256，均等于冻结值，0不一致 |
| 清洗稳定标记 | `datasets/manifests/STABLE_CLEANED.json` 存在，状态 STABLE_CLEANED_V1 |
| P1 primary | 975记录、19,959源内行；当前文件 SHA256、记录数与行数均匹配稳定清单 |
| P1 fixed variant | 975记录、19,992源内行；当前文件 SHA256、记录数与行数均匹配稳定清单 |
| P2 sampled | 385记录、7,339源内行；当前文件 SHA256、记录数与行数均匹配稳定清单 |
| P2 full | 385记录、680,280源内行；当前文件 SHA256、记录数与行数均匹配稳定清单 |
| 上述四个 prediction 文件 | 顶层仅 sample_id/text/sources；非法顶层字段计数0；逐源行文本正则 T-ID 残留计数0 |
| reference ID 与授权元数据 | P1两视图各975唯一ID，P2两视图各385唯一ID；scenario1 step35/36/37记录数0 |
| 当前主结果 CSV | P0 100行；P1/P1_FIXED 合计40行；P2/P2_FULL 合计23行；所有行 missing_predictions=0，N_Queries=n_records |
| 203共同覆盖条件 | 独立 knowledge_view 与 KnowledgeCoverage=203；评价器先排除含覆盖外Gold的记录并保存排除计数，主216候选成绩未被此过滤替换；当前该条件N仍为975 |
| 主结果资格 | P0均PUBLIC_EXPOSED_DEVELOPMENT，P1/P2均SHARED_EXECUTION_DEVELOPMENT；未将本轮变体重抽或v2称为独立测试 |
| 来源贡献数值 | 5个融合条件×4种方法×前3个样本×Top10，共600个候选分数；sum(source contributions) 与保存scores最大绝对误差约3.55×10⁻¹⁵ |
| 证据资格 | 有trace的抽样记录均 RANKING_EVIDENCE_CANDIDATE；P1无trace的followup由skip-evidence明确产生，不伪造逐行证据Gold |

## 代码层核查

`datasets/build_v2.py` 先对ZIP成员元数据执行授权/路径/类型/尺寸过滤，只有allowlist后才调用z.read，无全量解压。正文清洗逐原行生成一条 ll 记录（即使清洗后为空也保留），然后对该行列表作相同连续窗口截取；因此清洗不靠删行改变采样行号或行数。源内原始哈希仅作溯源，不输入GT。代码对抽样核心作6种长度的官方函数等价核查；本次只读审计没有再次读ZIP正文或复跑构建。

`baselines/engine.py` 与 `source_fusion.py` 的预测入口仅打开 --inputs、--knowledge 和输出文件，且拒绝 sample_id/text/sources 之外的顶层字段；未发现读取reference、标签文件或历史作者预测的预测路径。GT只在数据参考构建及评价程序进入；公开ATT&CK候选知识本身是任务允许的候选信息，不是样本Gold。

`baselines/evaluate_runs.py` 复用冻结V1评价器；缺失预测不会删除样本，而是记空预测与missing_predictions。步骤宏平均按(scenario_id,step_id)聚合，执行/场景组分析标记 GROUPED_DEVELOPMENT_NO_SUPERVISED_TRAINING；没有以975条记录当独立训练/测试样本做显著性Bootstrap。203候选条件的过滤和分母另列。P1与P1_FIXED、P2与P2_FULL输出进各自总CSV，但protocol/input_view仍分列，汇总报告必须继续分开展示，不能平均成单一协议成绩。

`baselines/compare_protocols.py` 按logical step及replica配对P0/P1；P2按同一execution-step配对并明确保留P0副本权重。变化资格标记 VERSION_VARIANT_AND_WINDOW_CHANGE 或 VERSION_AND_WINDOW_CHANGE，并未把版本变化解释为纯重采样效应。当前配对表为P0/P1 39,000行、P0/P2 19,500行，各20方法；含融合条件。这些行数是“方法×配对记录数”，不是真实独立攻击执行数。

## 已发现并确认修复

初查compare_protocols仅接受全文检索all视图，不接受P0融合的sourcewise_same_native_content，造成融合P1/P2虽可评价但不能与P0配对。已通知执行者；复查当前过滤已加入该主视图，且native/预算视图不进入同method/protocol主登记，避免覆盖。最新配对表已含 SourceWise 与 EvidenceLineFusion 方法；此问题不再是当前交付阻断。

## 尚需准确披露的限制

1. **trace不是候选算法的完整逐行分解。** `source_fusion.py` 的 line_fusions 对discriminative行分数取Top3聚合；evidence()却统一选原始BM25/TFIDF最高的单行，把整源fusion_contribution附在该候选行上。因此它可解释为“相关候选行＋来源贡献”，不能声称保存了实际参与Top3聚合的全部行，也不能把单行贡献解释为整源因果贡献。抽样贡献求和通过的是来源层数值一致性。所有trace仍应保持 RANKING_EVIDENCE_CANDIDATE。
2. **登记防护仍可加强，未发现已影响当前结果。** register_fusion_runs仅凭run.json生成成功exit_code=0；并不独立验证每方法输出存在且完整。当前主结果missing_predictions均0，未发现缺失样本；未来应在登记时复核run n、输出ID集合、输入/知识哈希与进程回执，避免旧run.json残留误登记。
3. **运行时间资格不要丢失。** 注册receipt说明InferenceTime为shared batch time，非逐方法可相加时间；evaluate_runs主CSV仅带seconds，没有传递该文本资格。最终运行时间报告应写清此口径，不能把同批总时间当各方法独占时间比较。
4. **本地文件系统可读并非进程强隔离。** 代码路径和prediction schema提供可审查的逻辑隔离；不是OS强制禁止预测进程读取其他文件。本审计未见此类读取，不应夸大为沙箱证明。
5. **无独立泛化结论。** 分组汇总及重采样表是开发分析；同一P0执行在v2和多个副本中复用。7场景与有限执行组不足以据此宣称新任务分布性能显著。

本报告记录的是审计时快照。没有改变代码、预测、旧成绩、标签或任何其他产物。后续若修改数据或评分入口，必须重新核验对应SHA、分母与登记关系。


## 根代理修正附录（审计快照之后）

登记器现复核每方法完整输出行数和input/knowledge SHA256；原P0单独进程退出码确未捕获，现如实标NOT_CAPTURED，后续跟进进程有真实回执。主CSV已传递shared-batch耗时资格。融合跨协议配对遗漏已修复。新增SOURCE_EVIDENCE_TRACES.jsonl按真实候选公式重建实际top3行，62,560来源trace的候选总分重构最大误差0，见results/EXACT_EVIDENCE_VALIDATION.json；原代表行trace保持原资格。上述为根代理实施记录，独立审核的原快照保持在前文，最终再验证结果见results/DELIVERY_VALIDATION.json。
