# 外部标签单位审计

当前只推进 Splunk Attack Data 实例 `cc9b25e1-efc9-11eb-926b-550bf0943fbb`，固定版本 `671f9f5b065f03a5502db07c20f1fe3f620d29d9`。本轮重新取得官方 [YAML](https://github.com/splunk/attack_data/blob/671f9f5b065f03a5502db07c20f1fe3f620d29d9/datasets/attack_techniques/T1003.003/atomic_red_team/atomic_red_team.yml)、根许可和三个 Git LFS 指针。三个日志已在用户指定服务器取得并通过大小与SHA256核验，实际解析共7023条记录。

`mitre_technique: T1003.003` 位于整个 YAML 实例层，映射父技术 `T1003`，属于冻结216候选。`datasets` 列出 Sysmon、Windows Security 4688、CrowdStrike 三个传感器输出。YAML 描述多个 Atomic Red Team 测试变体，其中一个结果不明；它没有为单条事件声明技术，不提供每次变体的完整时间边界，也没有穷尽其他可能出现的技术。因此**只能建立一个包含三类日志的 Bag 及一份来源声明正标签**。背景事件是否包含攻击不可由该标签推导。

评价约束已冻结：

- 一个 Bag 计作一个外部评价单位；不将三文件计为三次独立执行，也不按日志条数扩大样本量。
- Gold 参考只存于独立的 `BAG_REFERENCE.jsonl`，模型输入不含仓库目录、原文件名、YAML、测试名和技术标签；输入采用中性 `EXTERNAL_BAG_001` 和传感器编号。
- 原子技术ID、规则命名和检测签名可能直接泄露标签。预处理移除结构化 RuleName、MITRE/technique/signature/test 字段，掩盖任意 T-ID；保留实际观察到的文件/进程/命令内容为惰性字符串，不执行它们。本次实际清洗移除7015个注释字段和105处T-ID；这验证了具体规则已执行，不代表所有隐式标签线索都已穷尽排除。
- 清洗不是把 NTDS 等真实行为证据删掉；它只去除注释/检测标签。若格式或标注字段不能可靠解释，保持 `NEEDS_MANUAL_BOUNDARY_REVIEW`，不得自动评价。
- 不给 Bag 内每条记录复制 `T1003`，不把原始子技术细粒度成绩和父技术成绩混写。
- 来源仅声明一个正类且未给出穷尽标签。若以后评价，优先报告该已声明正类在216候选中的 Rank、Hit@K、MRR@10；其他预测类不能据此被证明为实际假阳性，完整多标签 Precision/F1 的解释不成立。
- 主融合仍需要真实外部冻结 GTE 特征。目前只有 CAM-LDS 的向量，不能将它们替换成外部向量，也不能以 B2/词法可行性结果代替融合结果。

`external_dataset/prepare_bag.py` 已完成解析/标签剥离的受限单元检验：XML规则字段剥离、JSON字段剥离、T-ID掩盖、DTD实体拒绝、NDJSON解析。测试使用自造无攻击行为的解析片段，不是模拟日志实验或识别预测。生产路径首先核验本轮显式授权和三个固定对象的大小、SHA256；服务器生产版本prepare_server_bag.py读取本轮服务器grant，已对真实日志完成静态解析；原prepare_bag.py仍是历史本地入口，其等待授权状态不代表当前server操作未授权。

脚本依赖判定仍为 `UNRESOLVED`：元数据明确来自 `attack_range` / `atomic_red_team`，但没有此次执行所用 Atomic 脚本的固定版本或脚本哈希。CAM-LDS既有审计的脚本身份也为 UNKNOWN。Windows日志与现有Linux日志格式不同，不能替代脚本独立证据。没有已确认的直接执行重复，同时也没有足够证据确认 E2。
