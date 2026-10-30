# 训练代码只读审查
当前状态以文末“训练前修复复核”为准；前文具体问题保留为初审记录，不代表修复后仍全部开放。
审查日期：2026-10-28。采用 code-review-excellence 流程。未运行训练、未读取新的预测或评价结果、未修改训练源码。本报告依据审查时的源码；真正训练完成与否仍须以未来真实特征和运行回执确认，不能从代码准备状态推出已训练。

范围：`contrastive/numpy_models.py`、`contrastive/train_heads.py`、`manifests/TRAINING_PROTOCOL.json`。为核对依赖，只读了 common、特征提取器、现有梯度测试源码和划分清单元数据；未打开 heldout/validation reference。划分清单当前 SHA256 确实等于协议登记的 `879bac94d85a5106a36345b9d9ce3f85f0b383978d8a6b914bb2cec1374bd96d`。

## 具体问题
### [P1] 特征与 B5 缓存的资格只部分绑定，无法拒绝同 ID 的错误知识/旧模型产物
位置：train_heads.py:15–17、39、59–60。

入口检查了数组形状、技术 ID 顺序以及逐日志 input hash，但没有检查特征提取回执中的权重 SHA、真实提取状态、feature SHA 与当前文件一致性，也未核对提取器已提供的 `knowledge_hashes` 与当前 K2 文本。B8/B9 加载 B5 时仅比较 train sample ID 集合的哈希；B5 npz 没有存储或验证当前特征 SHA、训练文件 SHA、协议 SHA、模型源码 SHA、seed/augmentation 元数据及候选 IDs。即使 train IDs 相同，替换特征或训练标签后遗留的 B5 仍会被接受作困难例来源，或使用同 IDs 的不同知识文本而入口不报错。

这不是已经发现实际污染；在尚未提取真实特征的阶段，当前代码缺少拒绝这种污染的运行门禁。建议正式训练前读取并验证固定 FEATURE_EXTRACTION_RECEIPT，逐项核对 `knowledge_hashes`；B5 检查点或配套不可变回执绑定上述 SHA/配置，并在所有挖掘方法加载前比较。负例回执记录 source checkpoint SHA，而不只记录路径。无需新增训练查询来修复。

### [P1] 协议的总墙钟和磁盘上限未在被审查入口执行
位置：TRAINING_PROTOCOL.json 的 5400 秒/2,000,000,000 bytes；train_heads.py:13、51–52、59–72。

实际只有“当前 run() 开始后1800秒”的 assert，且运行到 epoch 才检查。这个计时涵盖同进程多个 method，而跨 fold/seed/augmentation 重新启动就重新计时；因此不是协议声明的整个本地实验5400秒上限。代码也没有检查项目新增磁盘2GB。不能仅凭此文件宣称已实施总预算硬停。

建议由单一运行控制器维护总体 monotonic 截止时间与磁盘计数，开始每个 method、挖掘及写 checkpoint 前检查，超限停止后续任务并输出部分完成回执。若已有其他控制器负责，需要在报告中引用其实际实现和最终总成本；本次审查没有该证据，不据此断言未来一定超限。

### [P2] cpu_process_seconds 和 peak_rss_bytes 是进程累计值，不是每个方法独立成本
位置：train_heads.py:29、72。

`seconds` 是方法 begin 的墙钟差值，但 `time.process_time()` 没有减方法开始值。默认一次进程跑 B3→B9_CONST，因此 B9 的 CPU 字段累加了之前方法和初始化的 CPU 时间。ru_maxrss 同样是进程从启动以来的峰值，不能把每行当成该方法的独立峰值。macOS 下 ru_maxrss 为 bytes，与当前机器相符；若在 Linux 复用此入口，原字段还会差1024倍。

建议记录每方法 process_time 差值；总进程 CPU 另命名保留。RSS 明确标为 process_cumulative_peak 并统一平台单位；如确需每方法峰值，采用各方法单独进程或采样。现有 mining_seconds 包含少量参数/优化器初始化，并不完全等同挖掘纯耗时，可改名或移动计时起点。

### [P2] CLI 未限制 method/augmentation，拼写错误会执行另一种真实计算并输出错误标签
位置：train_heads.py:31–55、78。

augmentation 只判断是否恰好等于 ONE_VIEW_PER_STEP，任意其他字符串都按多视图执行；method 不是 B3 且不在负例列表时，都会按全216正例对比训练执行。例如传入 B10，会训练32维投影却把结果命名 B10。建议 argparse choices 或入口 assert 确保 augmentation 属于协议两项、method 属于 METHODS、且没有重复项；明确 B8/B9 必须先有合格 B5。正确默认参数路径不受此问题影响。

## 已确认的隔离和公平性
- train_heads.py:14 从 train 文件取标签；held/valid 只加载 inputs 并使用 log text hash。审查源码没有读取 heldout_reference 或 validation_reference，也没有根据验证指标早停或择参。公开知识全部216个类别可被训练使用，这是公开候选知识，并非 heldout Gold 泄漏。一次性冻结推理全部输入向量本身不等同于使用 heldout 标签训练。
- 场景隔离有入口 assert；五视图先按 logical_step_id 分组，每步每次更新只取一个视图。共现 `co=y.astype(float).T@y` 的 y 仅来自 train 的唯一逻辑步骤，一步五采样没有重复计权。不能从这段代码额外宣称脚本独立性已被证明；完整 purge 仍依赖上游划分与验证清单。
- 已知全部正例先编码到216列布尔 y；B6–B9 的 eligible=`~y[i]`，mask 初值为 y，正例权重保持1。损失还 assert 每个正例都在 mask 中。没有把一个多标签步骤的另一已知正例当负例。协议未声明的未知等价关系不被自动合并，未标注候选仍明确不是证据认证负例。
- B6/B7/B8/B9/B9_CONST 每步均32个候选；B4–B9 同 seed 时投影初始化完全相同，都是两套768×32矩阵、120次 full-batch 更新。B8/B9/B9_CONST 使用同名 B5 的 r0 训练步挖掘分数与一致 tie-break，不读取 heldout 分数；当前确定性路径下候选集合相同。建议实际运行时再输出/校验 pool SHA 作为回执，但未发现当前构造逻辑破坏该对照。
- B9 仅改变 B8 固定池中的负例权重：1−0.75 max P_train(j|positive)，范围[0.25,1]；B9_CONST 同池常数0.5。它控制了统一降低负例力度这一替代解释，但共现风险不是负例真假概率；也不是独立人工机制参考。
- B8/B9 的上游 B5 成本确实额外存在，协议明确承认总 pipeline 成本不相等。B9 相对 B8 使用相同上游来源，可比较增量；若只列各自120次更新而省去 B5 则不能声称总计算预算完全相同。

## 参数更新与保存的静态判断
numpy_models.py 中给出对比、平衡 BCE、分类 BCE 的解析梯度，normalize 的反向传播包含球面切向投影；多正例损失使用全部正例均匀目标。Adam.step 在原参数数组上执行更新，检查梯度及更新后参数有限值。train_heads.py 比较初末参数哈希并要求变化，记录L2变化，将参数保存为 npz，再重新加载后比较 heldout 输入上的分数完全一致。两投影头的可训练参数为 2×768×32=49,152，骨干没有进入训练参数列表。

这些路径能产生真实参数优化、持久化及复载证据，不能称为完整 GTE 微调。参数改变本身也可能包含 L2 收缩，不能单独证明学习了领域判别；应同时检查梯度/训练损失与真实对照结果。现有 test_gradients.py 写有有限差分与全正例掩码测试，本次仅阅读，未重新运行，故不宣称测试通过。

## 审查结论
当前没有发现训练代码显式读取 heldout/validation Gold，B8/B9 采样、全多正例掩码和 train-only 共现的实现与登记机制一致。正式 B3–B9 运行前应补足特征/B5产物资格校验及总预算控制；成本字段与 CLI 校验建议同步修正。真实 GTE 特征仍待新授权，本报告不把准备好的代码登记成已完成训练。

## 训练前修复复核：2026-10-28
本次仍为只读复核，没有运行训练、没有读取预测/评价结果。实际特征文件 FROZEN_GTE_FEATURES.npz 与 FEATURE_EXTRACTION_RECEIPT.json 在复核时均不存在，因此不存在以本轮特征完成的头训练证据。3份相关 Python 源码仅执行 AST 解析，语法通过；没有把静态检查写成训练或数值测试通过。

已解决的初审事项：

- 特征入口现在核对 receipt.feature_sha256、固定 GTE weight SHA、model revision 与 Gold_loaded=false，并逐项核对 knowledge_hashes 与当前 K2 文本。B5 npz 保存并在挖掘前核对 feature/train-file/protocol/trainer SHA，已阻断初审指出的“同 ID 不同特征或训练标签”静默复用。原有逐日志 input hash 检查保留。
- 新 run_heads_matrix.py 只创建一次 HEADS_TRAINING_RUN_CONTROL.json，存在时拒绝重置。各训练子进程 check_budget() 读取同一 start_unix，方法开始和每10轮检查累计5400秒与整个项目非venv、非软链接文件2GB；不再是每个子进程各自获得5400秒。按固定顺序先跑 B5 后跑 B8/B9，对失败立即终止矩阵，没有隐式调参重试。
- CPU 成本已经改为 time.process_time()-cpu_begin 的每方法差值，RSS 加入 cumulative process high-water mark 的明确范围说明，初审中错误的“方法CPU累计值”字段已修正。
- argparse 已对 methods 和 augmentation 加入 choices，未知 B10 或拼错 augmentation 不能再被 CLI 静默归类为投影/多视图。重复 method 会被既有禁止覆盖检查阻止，不会产生第二次隐藏训练。

未改变的科学边界：B8/B9 同池、多正例掩码和训练步骤共现公式未修改，没有发现该修复引入 heldout Gold 依赖。共现仍只是风险代理、未知候选仍不是认证负例，独立外部测试仍不能由这些工程检查获得。

剩余实现边界（不应夸大为已发生污染或超限）：

1. 总预算目前是定期检查后停止，不是严格不越界的原子硬限：每10轮检查之间可能跨过截止时间，最后一次检查后还会执行剩余轮次、推理及文件写入；磁盘检查也没有预留下一次写入大小。报告应写“全局预算监测/超限停止”，如要求任一时刻绝不超过上限，应由父控制器用剩余秒数设置子进程 timeout，并在保存前复查/预留磁盘。尚无运行，故未发现实际超限。
2. peak_rss_bytes 当前数值在 macOS 可按 bytes 解释；若将训练入口搬到 Linux，仍需将 ru_maxrss 的 KiB 乘1024。累计范围标签已正确，本轮本地 macOS 路径不受此跨平台边界影响。
3. B5 lineage 已绑定 train_heads.py，但解析梯度位于 numpy_models.py，尚未将该依赖源码 SHA 一并存入检查点。当前依赖源码未改变，故没有实际陈旧依赖证据；后续修改该文件后复用检查点时应重新资格校验或统一绑定代码清单。负例记录目前仍主要保存来源路径，最终回执可补 source checkpoint SHA/pool SHA 以便离线直接验证同池。

复核源码 SHA256：train_heads.py=5960021e41a0c6975168b7870958fc6b7c2e81b7e89ba62cb613f6fbb725524a；numpy_models.py=cfa3bdcbdd26206ecf38082673afff2fd1d5aa8e0b8739ce92b95d1a5fdf2711；run_heads_matrix.py=722bd43bc18f30436e919e65e7e10afefa0687032aa1c05c6e148e25886a02ec；TRAINING_PROTOCOL.json=d38359359b6d2db8f2be223847efb420b6afc0b8a862673c78900b9f618a4d3a。

当前结论：初审4类问题的主问题均已在真实 GTE 头训练前修复；剩余3点是应在资源硬限和跨版本复用表述中保留的边界。模型尚未训练，不能报告领域对齐增益。

### 最后一次训练前硬化复核：2026-10-28
只读复核确认，前次剩余项中两条现已处理：B5 检查点保存并在挖掘加载时核对 numpy_models.py 的 math_source_sha256，梯度模块变更后的旧检查点不能再静默复用；controller 按全局剩余秒数设置 subprocess timeout=min(1800, remaining)，训练入口在保存检查点、推理、写预测前也新增 check_budget。相关两份 Python AST 解析通过，未运行训练或读取模型/预测文件。前文关于这两条仍缺失的描述仅为历史审查记录，不再是当前开放问题。

仍保留：磁盘是定期/阶段性监测，不是为下一次写入预留空间的原子文件系统配额，因此不能宣称任意时刻绝不超过2GB；Linux 上 ru_maxrss 需将 KiB 换算为 bytes，当前 macOS 本地执行不受此单位问题影响。子进程全局剩余时间控制已有实现，不再将“仅每10轮检查墙钟”列为当前缺口。

至此停止审查；未修改任何训练代码、模型、检查点或评价结果。

