# 2024--2026 年 ATT&CK 相关论文逐篇技术核验表（50 篇）

版本：2026-08-31。本文档是 CSV 的逐篇展开版。每篇都按同一模板回答：方法/模型、输入、输出、数据集、效果、embedding、分类器/推理、ATT&CK 的位置、代码和证据等级。

## 如何读这份表

- `NR`（not reported）表示我在可核验的出版社摘要、会议页面、作者公开稿或仓库中没有找到该字段；这不是“没有使用”，也不是允许我凭经验补写。
- “摘要级”论文只能支持方法方向和 ATT&CK 用法，不能支持未披露的层数、维度、训练/测试划分或完整指标。
- 50 篇是**强相关候选池**，不是声称 50 篇都已经满足中科院一区/二区或 CCF-A/B。CCF-A/B 已确认数、分区核验规则和淘汰风险见 `ATTACK_literature_report_2024_2026.md`。
- DOI/会议页面是文献入口；代码链接只有在能够定位到作者仓库或 artifact 时才写“公开”。

**交叉核验入口**：ATT&CK 应用综述（417 篇同行评审论文）<https://arxiv.org/abs/2502.10825>；公开 ATT&CK/STIX 数据 <https://github.com/mitre-attack/attack-stix-data>；Adema CTI 映射代码 <https://github.com/das-lab/Adema>；Laccolith 仿真代码 <https://github.com/dessertlab/Laccolith>；SAGA 数据站 <https://www.saga-cyber.net/dataset>。

---

## 1. Zero Trust + ATT&CK matrix（IEEE Access, 2024）

- **论文/入口**：Research on Improving Cyber Resilience by Integrating the Zero Trust security model with the MITRE ATT&CK matrix；<https://doi.org/10.1109/ACCESS.2024.3417182>。
- **方法/模型**：零信任架构与 ATT&CK 矩阵的架构整合、控制覆盖分析；不是端到端机器学习模型。
- **输入**：零信任原则、资产/访问控制要求、ATT&CK tactic/technique 矩阵和企业威胁场景。
- **输出**：韧性控制优先级、ATT&CK 覆盖关系和控制缺口。
- **数据集/规模**：企业/零信任案例；公开摘要未给出可复现实验数据集和样本规模。
- **效果**：案例/覆盖分析结果；没有可与分类器比较的 Accuracy、F1 或 AUC（NR）。
- **Embedding**：不适用；使用矩阵、知识条目和控制关系。
- **分类器/推理**：矩阵覆盖与风险/控制推理。
- **ATT&CK 用法**：作为行为分类法和检测/控制覆盖坐标系，不作为监督标签训练神经分类器。
- **代码**：未找到作者公开代码。
- **证据等级**：DOI 和综述条目确认；具体实现细节需全文核验。

## 2. Malware2ATT&CK（Computers & Security, 2024）

- **论文/入口**：Malware2ATT&CK: A sophisticated model for mapping malware to ATT&CK techniques；<https://doi.org/10.1016/j.cose.2024.103772>。
- **方法/模型**：先对恶意软件的汇编指令和 API 调用做预训练特征提取，再按函数构图，用图神经网络融合函数级信息，最后结合 ATT&CK 知识图谱做多标签识别。论文明确把任务定义为 malware-to-technique mapping。
- **输入**：静态分析得到的 assembly instruction 序列、API-call 信息，以及函数间图结构。
- **输出**：一个样本对应的多个 ATT&CK technique 标签；不是单一恶意软件家族标签。
- **数据集/规模**：两个 malware 测试集；摘要确认存在两个测试集，但完整样本数、家族划分和训练/测试协议需全文核验。
- **效果**：两个测试集上的 technique mapping 平均 F1=83.6%。
- **Embedding**：汇编和 API 分别用预训练模型编码；函数级表示再由 GNN 聚合；论文摘要未给出具体预训练模型名称和向量维度。
- **分类器/推理**：GNN 表征 + ATT&CK knowledge graph 关系先验的多标签分类头；每个 technique 独立输出概率。
- **ATT&CK 用法**：既是目标标签空间，又通过 technique 关系建模行为之间的相关性；不是仅用于结果可视化。
- **代码**：未找到官方仓库。
- **证据等级**：出版社全文摘要直接给出方法和 F1；数据规模、层数和超参数需全文核验。

## 3. Attention-Based API Locating for Malware Techniques（IEEE TIFS, 2024）

- **论文/入口**：Attention-Based API Locating for Malware Techniques；<https://doi.org/10.1109/TIFS.2023.3330337>（DOI 年份为 online-first，正式卷期为 2024）。
- **方法/模型**：APILI（attention-based API locating）。在 API 调用、资源/参数和 ATT&CK technique 之间建立多重 attention，用 attention 权重定位技术相关 API；技术表示使用 SVD 处理 technique 共现/关系信息。
- **输入**：恶意软件动态执行产生的 API-call 序列及 API 参数/资源信息。
- **输出**：样本级 ATT&CK technique 预测，以及 API 序列中最能支持该技术的证据位置。
- **数据集/规模**：malware API/行为语料；公开页面未披露完整规模和跨家族划分（NR）。
- **效果**：摘要/索引页没有给出可安全引用的统一 F1 数值；需读取全文表格。
- **Embedding**：参数和资源使用 fine-tuned BERT；technique 表示由 SVD 得到；API 序列由 attention 表征。
- **分类器/推理**：attention scoring 与 technique classifier；具体是 softmax/sigmoid 头以及定位损失需全文核验。
- **ATT&CK 用法**：用 technique 标签监督行为识别，并把技术语义作为 API 定位的查询/对齐对象。
- **代码**：未找到官方代码。
- **证据等级**：IEEE DOI 和摘要级页面确认“attention/API locating/BERT/SVD”；数值指标和标注协议需全文核验。

## 4. Weapon：Early-stage Android ransomware detection（Computers & Security, 2024）

- **论文/入口**：It's too late if exfiltrate: Early stage Android ransomware detection；<https://doi.org/10.1016/j.cose.2024.103819>。
- **方法/模型**：Weapon 将 Android 权限、API 等语义特征与 Android ATT&CK 对齐；对 ATT&CK Android 描述和应用行为做 BERT 语义编码，之后用 MLP 进行早期勒索软件判断。
- **输入**：Android APK 的 permissions、API calls 和可在勒索/加密前观察到的行为特征。
- **输出**：二分类/早期告警（ransomware vs. benign/非勒索），并可追溯到相关 Android ATT&CK 技术。
- **数据集/规模**：Heldroid 和 CCS-CIC-AndMal-2020；论文报告评估中分别包含 2,794 和 5,875 个 ransomware 样本。
- **效果**：预操作阶段识别率 89.82%；对应识别数量为 Heldroid 2,568/2,794、CCS-CIC-AndMal-2020 5,286/5,875。
- **Embedding**：BERT 产生 ATT&CK Android 描述/应用语义的上下文向量；具体 pooling 和维度需全文核验。
- **分类器/推理**：MLP 分类器，输出早期 ransomware 概率/类别。
- **ATT&CK 用法**：作为 Android 行为语义中间层，将权限/API 映射为 technique，再筛选可在数据泄露前观察到的信号；ATT&CK 不是简单的最终标签表。
- **代码**：未找到官方实现。
- **证据等级**：出版社页面/全文摘要同时支持模型、数据集和指标；训练划分及消融仍需全文核验。

## 5. Maze ransomware digital forensics（ESWA, 2024）

- **论文/入口**：Digital forensic of Maze ransomware: A case of electricity distributor enterprise in ASEAN；<https://doi.org/10.1016/j.eswa.2024.123652>。
- **方法/模型**：面向电力分销企业 Maze 事件的数字取证、时间线重建和 ATT&CK 映射；不是学习型分类模型。
- **输入**：企业取证制品、主机/网络痕迹、事件时间线和已知 Maze 行为。
- **输出**：取证时间线、观察到的 ATT&CK 技术及缓解建议。
- **数据集/规模**：单个 ASEAN 电力分销企业案例；无公开 benchmark 规模。
- **效果**：案例结论和取证完整性；没有统一预测分数。
- **Embedding**：不适用。
- **分类器/推理**：基于规则、专家判断和时间线关联。
- **ATT&CK 用法**：将观察到的 procedure 归入 tactic/technique，便于事件解释和防御建议。
- **代码**：未找到公开代码。
- **证据等级**：DOI/摘要确认案例和 ATT&CK 映射；细粒度证据表需全文核验。

## 6. SPP network traffic anomaly characterization（Computers & Security, 2024）

- **论文/入口**：An anomaly behavior characterization method of network traffic based on Spatial Pyramid Pool (SPP)；<https://doi.org/10.1016/j.cose.2024.103809>。
- **方法/模型**：Spatial Pyramid Pool（SPP）提取多尺度时空/统计相关特征，做网络流异常行为刻画；ATT&CK 位于行为解释层。
- **输入**：网络流/会话流特征，可包含单会话和上下文会话关系。
- **输出**：异常/攻击行为类别及其 ATT&CK 技术语义。
- **数据集/规模**：网络流 benchmark；公开摘要未列出完整数据集名称、样本数和划分。
- **效果**：论文摘要未披露可安全转录的完整指标（NR）。
- **Embedding**：SPP 对多尺度特征做聚合；是否有独立 embedding 层、维度和预训练过程需全文核验。
- **分类器/推理**：深度分类/异常检测 backbone；具体 CNN、RNN 或 Transformer 及损失函数 NR。
- **ATT&CK 用法**：将流量行为解释为 technique，而不是将 ATT&CK 当作训练输入的唯一特征。
- **代码**：未找到官方代码。
- **证据等级**：出版社摘要确认 SPP 和网络流任务；模型细节/数据表需全文核验。

## 7. Automated CTI ATT&CK mapping（Computers & Security, 2024）

- **论文/入口**：Automated discovery and mapping ATT&CK tactics and techniques for unstructured cyber threat intelligence；<https://doi.org/10.1016/j.cose.2024.103815>；代码/数据处理仓库：<https://github.com/das-lab/Adema>。
- **方法/模型**：文本去噪/预处理；分别训练 tactic 和 technique 的 sentence-level DistilBERT 多标签分类器；再用标签关系做 relation-based post-processing。
- **输入**：非结构化 CTI 报告句子/文本。
- **输出**：每句或每个文本的 ATT&CK tactic 集合和 technique 集合。
- **数据集/规模**：作者公开 Adema 文件包含 `tram_original.json`、`tram_original_with_labels.json`、`tram_with_all_labels.csv`、ATT&CK 标签表和原始报告；精确训练/验证/测试规模需论文全文核验。
- **效果**：tactic F0.5=85.50%，technique F0.5=75.17%；tactic LRAP 最高 91.34%。F0.5 说明作者更重视 precision 而非单纯 accuracy。
- **Embedding**：DistilBERT token/contextual representation；论文公开摘要未给出 pooling、最大长度和微调层冻结策略。
- **分类器/推理**：两个 sigmoid 多标签头；关系型后处理利用 tactic-technique/标签关系修正不一致预测。
- **ATT&CK 用法**：既是监督标签，又是后处理的本体/关系约束。
- **代码**：有公开仓库（预处理、标签抽取、训练入口和数据文件）；需按仓库许可证复现实验。
- **证据等级**：DOI、论文方法和仓库交叉确认；完整 split 和所有 baseline 需全文核验。

## 8. 6G IT/OT cyber-range framework（IEEE TCE, 2024）

- **论文/入口**：A Cyber Range Framework for Emulating Secure and Private IT/OT Consumer Service Verticals Towards 6G；<https://doi.org/10.1109/TCE.2024.3387055>。
- **方法/模型**：全虚拟化 IT/OT cyber range、场景编排和 ATT&CK-based adversary emulation；没有神经网络分类器。
- **输入**：IT/OT 拓扑、消费服务垂直行业需求、攻击场景配置和遥测。
- **输出**：可重复执行的攻击场景、事件流和 ATT&CK 覆盖评估。
- **数据集/规模**：作者构建的 cyber-range 场景；公开摘要未给出可下载数据集或精确事件数。
- **效果**：场景可重复性、覆盖性和隔离性评估；精确数值 NR。
- **Embedding**：不适用。
- **分类器/推理**：场景编排器/规则引擎。
- **ATT&CK 用法**：定义仿真的 adversary actions、tactic/technique 序列和覆盖清单。
- **代码**：未找到官方完整实现。
- **证据等级**：IEEE 页面和综述确认论文存在及其应用方向；实验表需全文核验。

## 9. Zero-day exploits in network flows（Computer Networks, 2024）

- **论文/入口**：A framework for detecting zero-day exploits in network flows；<https://doi.org/10.1016/j.comnet.2024.110476>。
- **方法/模型**：混合在线监督+无监督 zero-day 流量检测：在线聚类用距离/阈值拆分簇，再用监督验证新簇是否异常。
- **输入**：网络流/会话流特征和在线到达的数据窗口。
- **输出**：zero-day 异常流告警及其 ATT&CK 行为解释。
- **数据集/规模**：IBM 工业真实流量（保密）和 NSL-KDD；论文报告针对目标的 71 条异常流评估。
- **效果**：在线准确率 IBM 数据 98.4%，NSL-KDD 96.6%。
- **Embedding**：流统计特征和在线簇中心；没有报告神经语义 embedding。
- **分类器/推理**：最小距离/阈值在线聚类 + 监督验证，不是单一 softmax 分类器。
- **ATT&CK 用法**：将检测到的 exploit 行为解释为 tactic/technique；不参与 zero-day 训练标签生成。
- **代码**：工业数据保密，未找到官方代码。
- **证据等级**：出版社摘要给出方法、数据来源和两个准确率；详细特征和阈值需全文核验。

## 10. ATT&CK-based APT risk propagation（Computer Networks, 2024）

- **论文/入口**：ATT&CK-based Advanced Persistent Threat attacks risk propagation assessment model for zero trust networks；<https://doi.org/10.1016/j.comnet.2024.110376>。
- **方法/模型**：从 ATT&CK 技术关系/频繁项集挖掘技术关联，构造 technique relationship diagram；再用 Markov chain 预测 tactic 转移，并在零信任网络依赖上做风险传播。
- **输入**：ATT&CK technique 序列、网络资产/依赖、零信任实体和专家风险评分。
- **输出**：技术/战术转移概率、节点风险分数和传播路径。
- **数据集/规模**：零信任网络案例/仿真；不是公开监督学习 benchmark。
- **效果**：风险传播与预测评估；精确数值和对照基线需全文核验。
- **Embedding**：未报告神经 embedding；使用技术关系、状态转移和风险权重。
- **分类器/推理**：Markov chain + 概率风险传播，不是传统分类器。
- **ATT&CK 用法**：技术节点、tactic 阶段和攻击路径先验均来自 ATT&CK。
- **代码**：未找到官方代码。
- **证据等级**：出版社摘要明确给出频繁项集、Markov chain 和 risk propagation；参数估计细节需全文核验。

## 11. Maritime ATT&CK + D3FEND（IJIS, 2024）

- **论文/入口**：From sinking to saving: MITRE ATT&CK and D3FEND frameworks for maritime cybersecurity；<https://doi.org/10.1007/s10207-024-00812-4>。
- **方法/模型**：将海事威胁、ATT&CK 攻击技术与 D3FEND 防御技术建立攻防映射。
- **输入**：海事资产、威胁场景、攻击 procedures 和防御控制。
- **输出**：海事 technique 清单、D3FEND 缓解措施和覆盖缺口。
- **数据集/规模**：海事网络安全场景；未报告公开大规模数据集。
- **效果**：覆盖性/定性案例评价，无统一分类 F1。
- **Embedding**：不适用。
- **分类器/推理**：本体匹配、规则关联和专家推理。
- **ATT&CK 用法**：攻击侧行为词汇；D3FEND 提供防守侧对应关系。
- **代码**：未找到官方代码。
- **证据等级**：出版社页面和摘要级信息；映射表细节需全文核验。

## 12. Hierarchical ICS specification-based IDS（Information Sciences, 2024）

- **论文/入口**：Standard specification-based intrusion detection for hierarchical industrial control systems；<https://doi.org/10.1016/j.ins.2024.120102>。
- **方法/模型**：标准/规格驱动、过程感知的分布式 IDS；把安全要求转成运行时 security patterns，并在层级 ICS 上监测。
- **输入**：本地控制环、分布式控制环和 supervisory control 之间的工业协议/遥测事件。
- **输出**：ICS 入侵告警、违反规格的模式以及对应 ATT&CK ICS 语义。
- **数据集/规模**：真实 ICS demonstrator/testbed；公开页面未给出完整事件数。
- **效果**：论文报告响应时间随监控 pattern 数线性增长；完整检测率、误报率需全文核验。
- **Embedding**：协议字段、状态和 pattern 表示；未报告神经 embedding。
- **分类器/推理**：规格匹配、运行时规则和分布式 detector。
- **ATT&CK 用法**：解释 ICS 对手技术和告警语义，不是端到端监督标签。
- **代码**：未找到完整官方代码；可复用的 demonstrator 片段需向作者核验。
- **证据等级**：出版社摘要支持规格驱动方法和实时性结论；指标表需全文核验。

## 13. MetaCluster（IEEE TIFS, 2024）

- **论文/入口**：MetaCluster: a Universal Interpretable Classification Framework for Cybersecurity；<https://doi.org/10.1109/TIFS.2024.3372808>。
- **方法/模型**：可解释 MetaCluster：把特征/行为模式映射为语义 prototype，再进行语义聚合和跨任务分类；应用覆盖恶意软件家族、威胁行为和恶意流量。
- **输入**：不同网络安全任务的事件、流量或恶意软件特征。
- **输出**：攻击/技术类别及可解释 prototype/语义归因。
- **数据集/规模**：多类 cybersecurity 数据集；具体名称、样本数和任务划分需全文核验。
- **效果**：摘要报告参数量减少 79.52%--91.78%、推理速度最高提升 71.37%，F1 稳定或略升，MSE 降低 0.0101--0.1020；逐数据集绝对 F1 需全文核验。
- **Embedding**：学习特征表示并构造语义 prototype；维度、预训练和 prototype 初始化 NR。
- **分类器/推理**：prototype/cluster-based interpretable classifier，而非单纯线性 softmax。
- **ATT&CK 用法**：作为威胁行为的语义标签/解释坐标。
- **代码**：未找到官方实现。
- **证据等级**：IEEE 摘要支持框架和效率数字；ATT&CK 对应任务及具体数据集需全文核验。

## 14. Zero-trust implementation strategy（IEEE Transactions on Reliability, 2024）

- **论文/入口**：Strategy for implementing of zero trust architecture；<https://doi.org/10.1109/TR.2023.3345665>。
- **方法/模型**：零信任实施策略、威胁建模和控制优先级分析。
- **输入**：企业零信任需求、攻击场景、身份/资产/访问控制约束。
- **输出**：实施路线、控制优先级及 ATT&CK 覆盖矩阵。
- **数据集/规模**：企业案例，非公开 ML benchmark。
- **效果**：定性/决策评价；无统一分类指标。
- **Embedding**：不适用。
- **分类器/推理**：矩阵/风险推理。
- **ATT&CK 用法**：将威胁建模标准化，并帮助选择控制措施。
- **代码**：未找到公开代码。
- **证据等级**：DOI/摘要级。

## 15. Behavior-based intranet attacks（IEEE Access, 2024）

- **论文/入口**：An Advanced Approach for Detecting Behavior-Based Intranet Attacks by Machine Learning；<https://doi.org/10.1109/ACCESS.2024.3387016>。
- **方法/模型**：从内网连接行为和主机行为提取特征，比较六类监督机器学习检测器，并将类别映射到 ATT&CK。
- **输入**：Zeek/IDS 连接记录、源/目的 IP、协议、signature 以及连接尝试计数等行为特征。
- **输出**：内网攻击类别/告警及对应 tactic/technique。
- **数据集/规模**：作者构建/整理的 intranet attack 数据集；精确样本数和划分需全文核验。
- **效果**：摘要页面未提供可安全引用的完整指标；需全文表格。
- **Embedding**：手工/统计行为特征；未报告深度语义 embedding。
- **分类器/推理**：六个监督 ML 分类器（论文全文需核对各算法名称）。
- **ATT&CK 用法**：把行为类别解释为 tactic/technique，而非只报告匿名 class-0/class-1。
- **代码**：未找到官方代码；论文声称分享派生数据集，下载入口需核验。
- **证据等级**：IEEE DOI/摘要级。

## 16. Attacker next-action prediction（Computers and Electrical Engineering, 2024）

- **论文/入口**：Cyber attacker's next action prediction on dynamic real-time behavior model；<https://doi.org/10.1016/j.compeleceng.2023.109031>。
- **方法/模型**：动态攻击行为模型（MAGD）从 Cowrie honeypot 日志构造最小攻击图；隐藏 Markov model 预测下一动作，并把动作效果纳入状态。
- **输入**：按时间排序的 honeypot attacker actions；补充 Systrace 与 Java 模拟攻击动作。
- **输出**：下一步攻击动作及其 ATT&CK 技术语义。
- **数据集/规模**：Cowrie honeypot 日志；Systrace/Java 模拟攻击轨迹；完整序列数 NR。
- **效果**：next-action prediction accuracy=95.66%。
- **Embedding**：离散 HMM 状态/动作表示；没有神经 embedding。
- **分类器/推理**：HMM 状态转移概率和最可能下一动作。
- **ATT&CK 用法**：提供动作词汇和 tactic 语义，便于把预测动作解释为技术。
- **代码**：未找到官方代码。
- **证据等级**：摘要/全文片段支持 MAGD、HMM、数据来源和 95.66%。

## 17. Computational cybersecurity risk-management framework（JMIS, 2024）

- **论文/入口**：Improving threat mitigation through a cybersecurity risk management framework: A computational design science approach；<https://doi.org/10.1080/07421222.2023.2301178>。
- **方法/模型**：计算设计科学框架；将威胁情报、组织风险和防御措施结构化。
- **输入**：组织风险、威胁知识、ATT&CK 技术和管理约束。
- **输出**：优先缓解措施、风险决策和战略/运营/战术层 CTI。
- **数据集/规模**：组织案例/设计评估；没有公开标准数据集。
- **效果**：决策质量/框架评估；精确统计值 NR。
- **Embedding**：不适用或知识表示；未报告神经 embedding。
- **分类器/推理**：风险/决策推理。
- **ATT&CK 用法**：提供标准化 threat/mitigation vocabulary，便于把高层风险落到技术级控制。
- **代码**：未找到公开代码。
- **证据等级**：出版社摘要级；不要把它当作 ATT&CK 分类器论文。

## 18. Laccolith（IEEE TDSC, 2024）

- **论文/入口**：Laccolith: Hypervisor-Based Adversary Emulation with Anti-Detection；<https://doi.org/10.1109/TDSC.2024.3376129>；代码：<https://github.com/dessertlab/Laccolith>。
- **方法/模型**：基于 hypervisor 的对手仿真与 anti-detection；在虚拟机外层隐藏仿真活动，比较 CALDERA 与 Laccolith。
- **输入**：ATT&CK procedure 配置、虚拟机/端点执行轨迹和 AV/EDR 观测。
- **输出**：ATT&CK 技术执行结果、对手仿真覆盖和检测抵抗结果。
- **数据集/规模**：五个商业 AV 产品的 adversary-emulation 实验；不是大规模训练数据集。
- **效果**：Laccolith 活动在五个被测 AV 产品中均保持隐藏；完整技术覆盖表和统计显著性需全文核验。
- **Embedding**：不适用。
- **分类器/推理**：emulation rule engine + 检测结果比较。
- **ATT&CK 用法**：定义对手仿真 procedure 序列和覆盖指标。
- **代码**：公开 Laccolith 仓库；另有 <https://github.com/Shotokhan/adversary-emulation> 相关 artifact。
- **证据等级**：IEEE 页面、论文和仓库交叉确认。

## 19. AUTOMA（IEEE TNSM, 2024）

- **论文/入口**：AUTOMA: Automated Generation of Attack Hypotheses and Their Variants for Threat Hunting Using Knowledge Discovery；<https://doi.org/10.1109/TNSM.2024.3378972>。
- **方法/模型**：从 CTI/ATT&CK 关系做 knowledge discovery，自动生成 threat-hunting attack hypotheses 及其变体。
- **输入**：ATT&CK technique/procedure 关系、遥测/CTI 上下文和狩猎需求。
- **输出**：可执行的狩猎假设、ATT&CK 变体和搜索条件。
- **数据集/规模**：ATT&CK 知识库 + threat-hunting 案例；精确案例数 NR。
- **效果**：假设生成覆盖/有效性；精确数值需全文核验。
- **Embedding**：知识图谱/语义特征；是否使用向量模型 NR。
- **分类器/推理**：规则、知识发现和约束推理，不是标准监督分类。
- **ATT&CK 用法**：假设词汇、关系约束和技术变体来源。
- **代码**：未找到官方代码。
- **证据等级**：IEEE DOI/摘要级；论文在 CCF 官方目录中为 CCF-C，不能写成 CCF-B。

## 20. PARGMF（JISA, 2024）

- **论文/入口**：PARGMF: A provenance-enabled automated rule generation and matching framework with multi-level attack description model；<https://doi.org/10.1016/j.jisa.2023.103682>。
- **方法/模型**：安全日志解析为 provenance graph；从关注节点前向 BFS 生成 attack graph；构造 full/behavioral/structural 多级攻击描述，并生成 `(source_id, edge_type, target_id)` 规则元组。
- **输入**：provenance events、实体关系和安全规则/攻击描述。
- **输出**：规则匹配结果（match/investigate/no_match）、攻击阶段和 provenance 证据。
- **数据集/规模**：provenance/security-event 案例；公开摘要未给出统一数据集规模。
- **效果**：规则匹配/案例评估；完整 precision、recall 和开销需全文核验。
- **Embedding**：图/溯源结构表示；未报告神经 embedding。
- **分类器/推理**：图搜索 + 规则匹配 + 多级攻击描述推理。
- **ATT&CK 用法**：提供攻击级/技术级语义，用于把低层 provenance 匹配结果提升到高层攻击描述。
- **代码**：未找到官方代码。
- **证据等级**：出版社页面/摘要确认图构造与规则元组；实验表需全文核验。

## 21. ProvIoT（ACNS, 2024）

- **论文/入口**：ProvIoT: Detecting Stealthy Attacks in IoT through Federated Edge-Cloud Security；<https://doi.org/10.1007/978-3-031-54776-8_10>。
- **方法/模型**：联邦 edge-cloud 检测框架；各 IoT 客户端本地训练，再聚合模型/表示，攻击标签与 ATT&CK 对齐。
- **输入**：IoT 边缘/云端遥测、网络流和设备行为。
- **输出**：隐蔽 IoT 攻击告警/类别及技术解释。
- **数据集/规模**：IoT testbed/federated clients；公开摘要未给出客户端数和样本数。
- **效果**：F1、AUC 和通信开销的精确值 NR。
- **Embedding**：联邦本地模型表示；具体 encoder NR。
- **分类器/推理**：联邦监督/异常 detector。
- **ATT&CK 用法**：对齐 IoT 行为、攻击技术和缓解语义。
- **代码**：未确认公开代码。
- **证据等级**：出版社 DOI/摘要级；会议分区也需单独核验。

## 22. Debapt（Computers & Security, 2026）

- **论文/入口**：Debapt: Ontology-driven multi-agent debate for APT adversary profile construction from cyber threat intelligence；<https://doi.org/10.1016/j.cose.2026.104988>。
- **方法/模型**：多个 LLM agent 分工抽取实体、关系和 TTP，再通过 ontology-driven debate 互相质询、校验和合并。
- **输入**：长篇 CTI 报告及上下文。
- **输出**：结构化 APT adversary profile、实体关系、tactic/technique/procedure。
- **数据集/规模**：CTI 报告和案例研究；基础 LLM、报告数量和划分需全文核验。
- **效果**：案例质量/一致性评估；摘要未给出可引用的完整 F1。
- **Embedding**：LLM token 表示 + ATT&CK ontology 约束；独立向量库和维度 NR。
- **分类器/推理**：多智能体 debate、结构化抽取和本体一致性推理，不是传统分类头。
- **ATT&CK 用法**：TTP 词汇、实体类型、关系约束和输出 schema。
- **代码**：未找到官方代码。
- **证据等级**：DOI/摘要级；不能据此声称已验证可复现。

## 23. APT cyber-range scenarios（IEEE Access, 2024）

- **论文/入口**：Design and Evaluation of Advanced Persistent Threat Scenarios for Cyber Ranges；<https://doi.org/10.1109/ACCESS.2024.3402744>。
- **方法/模型**：用 Diamond Model/activity threads 形式化两个真实 APT 场景和一个抽象场景，并自动化到全虚拟化 cyber range。
- **输入**：场景描述、资产/拓扑、ATT&CK TTP 序列和仿真配置。
- **输出**：可重复的 APT campaign、遥测和 ATT&CK 覆盖报告。
- **数据集/规模**：三个 cyber-range 场景；不是监督学习数据集。
- **效果**：场景可重复性、覆盖和可用性；精确数字需全文核验。
- **Embedding**：不适用。
- **分类器/推理**：场景生成、约束和规则引擎。
- **ATT&CK 用法**：定义 kill-chain/lifecycle 的 tactics/techniques 和仿真步骤。
- **代码**：未找到完整官方代码。
- **证据等级**：IEEE DOI/摘要级。

## 24. MITREtrieval（IEEE TNSM, 2024）

- **论文/入口**：MITREtrieval: Retrieving MITRE Techniques From Unstructured Threat Reports by Fusion of Deep Learning and Ontology；<https://doi.org/10.1109/TNSM.2024.3401200>。
- **方法/模型**：句子级 BERT 识别候选 technique，再融合 ATT&CK ontology，最后用 voting/多模型融合提高检索稳定性。
- **输入**：非结构化 CTI 报告句子/段落。
- **输出**：多标签 ATT&CK technique 检索结果。
- **数据集/规模**：三组 CTI 报告，规模分别为 113、46、23 篇。
- **效果**：三组 F2 分数分别为 58%、62%、69%。F2 体现对召回率的更高权重。
- **Embedding**：BERT sentence embedding + ATT&CK ontology representation。
- **分类器/推理**：多标签分类器 + voting；具体阈值和 ontology 融合算子需全文核验。
- **ATT&CK 用法**：同时是目标标签集合和本体约束。
- **代码**：未找到官方代码。
- **证据等级**：IEEE 摘要直接给出数据量和 F2；论文在 CCF 官方目录中是 CCF-C。

## 25. Lifecycle-based IDS（IEEE TMLCN, 2024）

- **论文/入口**：Improving Generalization of ML-based IDS with Lifecycle-based Dataset, Auto-Learning Features, and Deep Learning；<https://doi.org/10.1109/TMLCN.2024.3402158>。
- **方法/模型**：构造按攻击生命周期组织的数据集；使用 auto-learning feature extraction 和深度 IDS，目标是跨生命周期/场景泛化。
- **输入**：UWF-ZeekDataFall22 网络流及生命周期/阶段元数据。
- **输出**：攻击/阶段标签和 IDS 告警。
- **数据集/规模**：UWF-ZeekDataFall22；完整流数量和各阶段比例需全文核验。
- **效果**：泛化实验和深度模型对比；绝对 Accuracy/F1/AUC NR。
- **Embedding**：自动学习的流特征；具体 backbone/维度 NR。
- **分类器/推理**：深度监督分类器。
- **ATT&CK 用法**：以 tactic/lifecycle 语义组织攻击阶段，帮助定义标签和跨阶段评估。
- **代码**：未找到官方代码。
- **证据等级**：IEEE DOI/摘要级。

## 26. Removing user-land hooks（IEEE Access, 2024）

- **论文/入口**：Effects of Removing User-Land Hooks in Endpoint Protection During Attack Experiments；<https://doi.org/10.1109/ACCESS.2024.3357525>。
- **方法/模型**：在开源 EDR 上做受控实验，执行 ATT&CK 技术链；比较正常 user-land hooks 与移除 hooks 的检测能力。
- **输入**：端点攻击实验遥测、EDR 告警和 ATT&CK procedure 序列。
- **输出**：每个攻击技术是否被发现、hooks 移除造成的检测下降。
- **数据集/规模**：受控端点实验；公开摘要未给出完整样本/重复次数。
- **效果**：基线检测 6 条攻击链中的 1 条；移除 hooks 后检测 8 条攻击中的 0 条（具体统计口径需全文核验）。
- **Embedding**：不适用。
- **分类器/推理**：比较性统计分析，不是训练分类器。
- **ATT&CK 用法**：标准化测试动作和覆盖维度。
- **代码**：未找到官方训练代码。
- **证据等级**：IEEE 摘要/实验描述支持上述结果。

## 27. Sysmon + ELK malware sandbox（IEEE Access, 2024）

- **论文/入口**：Redefining Malware Sandboxing: Enhancing Analysis through Sysmon and ELK Integration；<https://doi.org/10.1109/ACCESS.2024.3400167>；数据仓库：<https://github.com/rasmim/malwareDatasets>。
- **方法/模型**：在 sandbox 中用 Sysmon 采集 Windows 事件，经 Elasticsearch/Logstash/Kibana（ELK）检索、聚合，再按 ATT&CK 解释行为。
- **输入**：恶意程序执行期间产生的 Sysmon/ELK JSON 日志。
- **输出**：恶意软件行为报告、事件时间线和 technique 标签。
- **数据集/规模**：AAU_MalData，约 2,800 个 malware，单次执行约 25 分钟；包含 benign/malicious JSON，公开目录有 `AAU_MalData_Contagious`、`AAU_MalData_Pure`、`AAU_MalData_Synthetic`。
- **效果**：主要是采集和分析能力评估；没有公开统一的端到端分类 F1（NR）。
- **Embedding**：日志字段/事件特征；未报告神经 embedding。
- **分类器/推理**：ELK 查询、规则和 analytics pipeline，而不是学习型 classifier。
- **ATT&CK 用法**：把 Sysmon 观察到的持久化、C2 等行为关联到 ATT&CK 技术。
- **代码**：数据公开；论文分析代码未确认公开。
- **证据等级**：IEEE DOI、全文数据描述和仓库交叉确认。

## 28. OpenPLC security（IEEE Access, 2024）

- **论文/入口**：Investigating the Security of OpenPLC: Vulnerabilities, Attacks, and Mitigation Solutions；<https://doi.org/10.1109/ACCESS.2024.3356051>。
- **方法/模型**：OpenPLC/ICS 漏洞分析、PoC 攻击实验和 ATT&CK technique/mitigation 对照。
- **输入**：PLC 固件/配置、网络交互、攻击代码和实验痕迹。
- **输出**：攻击路径、漏洞影响和缓解措施。
- **数据集/规模**：OpenPLC/ICS 案例；不是公开大规模 ML 数据集。
- **效果**：定性与实验性安全结果；无单一分类 F1。
- **Embedding**：不适用。
- **分类器/推理**：攻击图、规则和专家推理。
- **ATT&CK 用法**：例如把凭据窃取、网络嗅探、密码破解映射到 ATT&CK ICS/Enterprise 技术并连接缓解措施。
- **代码**：未找到官方完整代码；论文中的 PoC 需核验是否随附。
- **证据等级**：IEEE DOI/摘要级。

## 29. E-XAI（IEEE Access, 2024）

- **论文/入口**：E-XAI: Evaluating Black-Box Explainable AI Frameworks for Network Intrusion Detection；<https://doi.org/10.1109/ACCESS.2024.3365140>。
- **方法/模型**：比较黑盒网络 IDS 与多种 XAI explainer，再用 ATT&CK 词汇解释模型为何把流量判为某类攻击。
- **输入**：网络流特征、IDS 黑盒预测及其候选解释。
- **输出**：特征重要性/解释，以及 tactic/technique 级语义。
- **数据集/规模**：多个网络 IDS 数据集；完整名称、样本数和模型组合需全文核验。
- **效果**：解释 fidelity、稳定性等指标；具体数值 NR。
- **Embedding**：依赖每个黑盒 IDS 的特征表示；未报告统一 ATT&CK embedding。
- **分类器/推理**：黑盒 IDS 分类器 + LIME/SHAP 等 XAI（具体 explainer 需全文核验）。
- **ATT&CK 用法**：解释标签词汇和语义层，不承担训练监督。
- **代码**：未找到官方代码。
- **证据等级**：IEEE DOI/摘要级。

## 30. MGDA（Computer Networks, 2026 卷期）

- **论文/入口**：MGDA: A provenance graph-based framework for threat detection and attack scenario reconstruction；<https://doi.org/10.1016/j.comnet.2025.111806>。
- **方法/模型**：①把 Windows ETW、Linux Audit、CamFlow 日志统一为 provenance graph；②多视图 masked graph autoencoder（GraphMAE-style）同时重构节点语义和邻接结构；③异常/离群检测；④前后向 K-hop 关联、剪枝、白名单和敏感文件/IOC 规则；⑤用 TTP 规则给重构子图补 ATT&CK 语义。
- **输入**：`(subject, relation, object, timestamp)` 审计元组；节点包括 process/file/socket，边包括 fork/read/write/open/execute/connect/send/receive，另有 path、filename、cmdline、IP 等属性。
- **输出**：异常节点/事件、压缩攻击场景图、攻击阶段和 ATT&CK tactic/technique。
- **数据集/规模**：StreamSpot、Unicorn Wget，以及 DARPA E3 CADETS/THEIA/TRACE 等三类广泛使用的 provenance 数据；完整样本数按数据集不同，需论文表格核验。
- **效果**：平均 AP=97.58%，F1=98.03%，训练最高约快 3 倍；论文还报告相对 ShadeWatcher 约百倍速度优势、相对 APT-MGL 更快（具体设置需全文）。
- **Embedding**：轻量节点/边语义编码 + masked graph representation；摘要未给 embedding 维度和具体初始化。
- **分类器/推理**：自监督图重构产生 anomaly score，再用动态阈值判异常；场景重构阶段是符号 TTP-rule matching，不是 ATT&CK 监督分类头。
- **ATT&CK 用法**：只在检测后的上下文关联/规则匹配中补充高层语义和攻击阶段，避免把 ATT&CK 标签误当作 provenance 边真值。
- **代码**：未确认官方代码。
- **证据等级**：出版社摘要和方法页同时支持数据类型、架构和指标；各数据集准确样本数需全文核验。

## 31. Logging maturity and IDS selection（Computers & Security, 2024）

- **论文/入口**：A logging maturity and decision model for the selection of intrusion detection cyber security solutions；<https://doi.org/10.1016/j.cose.2024.103844>。
- **方法/模型**：日志成熟度模型 + 多准则决策分析。
- **输入**：组织日志能力、候选 IDS 方案、部署约束和 ATT&CK 覆盖信息。
- **输出**：方案选择、日志建设优先级和覆盖缺口。
- **数据集/规模**：组织决策场景；无公开 ML 数据集。
- **效果**：决策分析结果；精确数值 NR。
- **Embedding**：不适用。
- **分类器/推理**：multi-criteria decision inference。
- **ATT&CK 用法**：把 technique 覆盖作为 IDS 选择的评价准则。
- **代码**：未找到公开代码。
- **证据等级**：出版社摘要级。

## 32. PLC obfuscation/honeypot（IEEE TNSM, 2024）

- **论文/入口**：These Aren't the PLCs you're looking for: Obfuscating PLCs to mimic honeypots；<https://doi.org/10.1109/TNSM.2024.3361915>。
- **方法/模型**：PLC 欺骗/混淆，使真实控制器行为看起来像 honeypot，并用攻击者行为分析评估 deception。
- **输入**：PLC/honeypot 网络交互、扫描和攻击请求。
- **输出**：欺骗有效性、攻击者行为变化和 technique 覆盖。
- **数据集/规模**：PLC honeypot 实验；非公开标准 ML 数据集。
- **效果**：实验/覆盖比较；具体数值 NR。
- **Embedding**：不适用。
- **分类器/推理**：实验规则和行为分析。
- **ATT&CK 用法**：描述攻击 PLC/honeypot 的 tactic/technique。
- **代码**：未找到官方代码。
- **证据等级**：IEEE DOI/摘要级；TNSM 在官方 CCF 目录中为 CCF-C。

## 33. SPEDIA dataset（Computers & Security, 2025）

- **论文/入口**：Design and generation of a dataset for training insider threat prevention and detection models: The SPEDIA dataset；<https://doi.org/10.1016/j.cose.2025.104743>。
- **方法/模型**：混合数据集生成方法：角色驱动的用户活动模拟 + 封闭网络安全演练中的真实用户活动 + 现有数据集整合；按 ATT&CK 对恶意行为做事件级标注。
- **输入**：用户命令、文件操作、服务使用、网络行为和 Email 活动日志，以及角色/场景配置。
- **输出**：训练/评测用的 event-level insider-threat 标签、ATT&CK tactic/technique 注释和多源日志。
- **数据集/规模**：合成、真实演练和复用数据的混合语料；论文公开摘要未给出最终事件总数。
- **效果**：论文明确说明 Accuracy、Precision、Recall、F1 等模型验证属于后续工作；本论文主要验证数据生成方案，而不是报告 SOTA 分类分数。
- **Embedding**：未报告 neural embedding；提供结构化事件字段供后续模型使用。
- **分类器/推理**：没有最终分类器，核心贡献是数据生成和标注管线。
- **ATT&CK 用法**：将演练/模拟的 insider actions 对齐到 tactic/technique，形成事件级监督接口。
- **代码**：未找到官方完整代码。
- **证据等级**：出版社开放获取页面/摘要确认 2025 年、混合生成方法、ATT&CK 映射和“模型指标留待后续”。

## 34. Automated ATT&CK Technique Chaining（Digital Threats, 2024）

- **论文/入口**：Automated ATT&CK Technique Chaining；<https://doi.org/10.1145/3696013>。
- **方法/模型**：在 ATT&CK procedure 示例和 technique 图上做自动技术链构造，使用图/序列约束筛选可行转移。
- **输入**：ATT&CK technique、tactic、procedure 序列和关系图。
- **输出**：链式 ATT&CK attack paths、可能的阶段转移。
- **数据集/规模**：ATT&CK 知识库和 procedure examples；不是事件日志 benchmark。
- **效果**：链覆盖/一致性评估；精确指标 NR。
- **Embedding**：technique graph representation；未报告神经 embedding。
- **分类器/推理**：图搜索、约束满足和路径评分。
- **ATT&CK 用法**：同时是输入知识库、链词汇和转移约束。
- **代码**：未确认公开代码。
- **证据等级**：ACM DOI/摘要级；venue 分区需核验。

## 35. MITRE Engenuity EDR evaluation analysis（ACM AsiaCCS, 2024）

- **论文/入口**：Decoding the MITRE engenuity ATT&CK evaluation: An analysis of EDR performance in real-world environments；<https://doi.org/10.1145/3634737.3645012>。
- **方法/模型**：对 MITRE Engenuity 评测结果做经验测量、统计比较和产品可见性分析。
- **输入**：多个轮次/产品的 MITRE Engenuity EDR 评测结果。
- **输出**：技术覆盖、检测可见性、告警延迟/性能比较。
- **数据集/规模**：四轮 MITRE Engenuity 评测及产品结果；具体产品数和行数需全文核验。
- **效果**：覆盖率和性能统计；完整数字在论文表格中。
- **Embedding**：不适用。
- **分类器/推理**：统计分析，不训练分类器。
- **ATT&CK 用法**：ATT&CK 是评测 protocol 和 technique index，而不是模型标签。
- **代码**：未确认 artifact/代码公开。
- **证据等级**：ACM DOI/摘要级。

## 36. Endpoint Detection use of ATT&CK（USENIX Security, 2024）

- **论文/入口**：How does Endpoint Detection use the MITRE ATT&CK Framework?；<https://www.usenix.org/conference/usenixsecurity24/presentation/virkud>；artifact：<https://github.com/avirkud/endpoint-detection-mitreattack>。
- **方法/模型**：对 Carbon Black、Splunk、Elastic、Sigma 四类检测规则进行经验审计，检查 ATT&CK 标签质量、覆盖和跨产品一致性。
- **输入**：四套带 ATT&CK 标注的 EDR/检测规则及其 technique/tactic 元数据。
- **输出**：覆盖率、标签质量、规则间一致性和 ATT&CK 映射缺陷。
- **数据集/规模**：四个产品/规则集合；完整规则数需论文/仓库核验。
- **效果**：报告覆盖和一致性统计；不是 Accuracy/F1 任务。
- **Embedding**：不适用。
- **分类器/推理**：统计测量、标签审计和规则比较。
- **ATT&CK 用法**：ATT&CK 是审计轴；论文研究“检测产品如何使用 ATT&CK”，不是用 ATT&CK 训练检测器。
- **代码**：有公开 artifact/分析代码。
- **证据等级**：USENIX 论文页和 GitHub artifact 直接确认。

## 37. VTT-LLM（Mathematics, 2024）

- **论文/入口**：VTT-LLM: Advancing Vulnerability-to-Tactic-and-Technique Mapping through Fine-Tuning of Large Language Model；<https://doi.org/10.3390/math12091286>。
- **方法/模型**：两阶段 VTT-LLM：第一阶段把 CVE、CWE、CAPEC、ATT&CK 组织成 chain-template instruction，微调 Bloom 系列 decoder LLM；第二阶段把模型生成的 technique description 与 ATT&CK technique description 做文本 embedding 相似度匹配。
- **输入**：CVE/vulnerability description，以及由 CWE/CAPEC/ATT&CK 提供的中间语义和关系。
- **输出**：ATT&CK tactic 和 technique 映射。
- **数据集/规模**：Dataset 2（ChatGPT-VDMEval/BRON-derived）包含 25,439 条 CVE 描述及 ATT&CK technique；评估使用 2021 年及历史年份数据。
- **效果**：相对 CVET 准确率提升 13.69%，相对直接 ChatGPT 提升 54.42%；chain template 在不同 LLM 上平均再提升 9.24%。
- **Embedding**：decoder LLM 产生技术描述/隐藏表示；再用文本 embedding 与 ATT&CK 描述匹配；具体 embedding 模型和维度需全文表格核验。
- **分类器/推理**：LLM 生成 + semantic-similarity matching，不是传统 softmax 分类头。
- **ATT&CK 用法**：目标 ontology；同时提供 technique 描述和 tactic 层级，CWE/CAPEC 关系作为中间推理上下文。
- **代码**：论文说明 fine-tuned model、代码和数据可向作者索取，未找到公开仓库。
- **证据等级**：MDPI 全文/DOI 支持方法、25,439 和相对指标；许可证/请求流程需作者确认。

## 38. Genics（Applied Sciences, 2024）

- **论文/入口**：Genics: a framework for generating attack scenarios for cybersecurity exercises on industrial control systems；<https://doi.org/10.3390/app14020768>。
- **方法/模型**：根据 ICS 资产模型和练习要求，使用 ATT&CK 约束生成攻击场景。
- **输入**：ICS 拓扑/资产、练习目标、攻击者能力和 ATT&CK technique 序列。
- **输出**：合成 ICS attack scenarios、练习脚本和覆盖说明。
- **数据集/规模**：ICS exercise/testbed 场景；非标准训练集。
- **效果**：场景有效性、可执行性和覆盖评价；精确数值 NR。
- **Embedding**：不适用。
- **分类器/推理**：constraint/rule-based generation。
- **ATT&CK 用法**：定义场景 tactic/technique 和生成合法性约束。
- **代码**：未找到官方代码。
- **证据等级**：出版社摘要级。

## 39. CVE to ATT&CK tactics（Information, 2024）

- **论文/入口**：Automated Mapping of Common Vulnerabilities and Exposures to MITRE ATT&CK Tactics；<https://doi.org/10.3390/info15040214>。
- **方法/模型**：CVE 文本到 ATT&CK tactic 的自动语义映射。
- **输入**：CVE description、漏洞影响和利用条件。
- **输出**：一个或多个 ATT&CK tactic 标签。
- **数据集/规模**：CVE corpus；精确样本数和人工标注策略 NR。
- **效果**：论文完整评分需全文核验；摘要页面未提供统一可引用分数。
- **Embedding**：文本语义表示；具体 TF-IDF、BERT 或 sentence encoder NR。
- **分类器/推理**：分类/语义匹配模型；算法名称需全文核验。
- **ATT&CK 用法**：目标 tactic ontology。
- **代码**：未找到官方代码。
- **证据等级**：DOI/摘要级。

## 40. Automated labeling for malware reports（Digital Threats, 2024）

- **论文/入口**：Improving Automated Labeling for ATT&CK Tactics in Malware Threat Reports；<https://doi.org/10.1145/3594553>。
- **方法/模型**：面向恶意软件报告的自动 tactic 标注、taxonomy-aware 文本分析。
- **输入**：malware threat report 文本。
- **输出**：ATT&CK tactic 多标签。
- **数据集/规模**：恶意软件报告语料；样本数、标注者和 split NR。
- **效果**：F1/precision/recall 需全文核验。
- **Embedding**：文本 embedding；具体 encoder NR。
- **分类器/推理**：多标签文本分类器及 taxonomy-aware 后处理（具体实现 NR）。
- **ATT&CK 用法**：监督标签和层次 taxonomy。
- **代码**：未找到官方代码。
- **证据等级**：ACM DOI/摘要级。

## 41. OT Bayesian Networks（IEEE TIFS, 2025）

- **论文/入口**：Identifying Adversarial Cyber-Activity in Operational Technology Environments Using Bayesian Networks；<https://doi.org/10.1109/TIFS.2025.3607241>。
- **方法/模型**：把 OT 过程阶段、观测变量和 ATT&CK ICS 技术组织成 Bayesian Network，按观测证据计算后验。
- **输入**：OT 过程/网络观测、设备状态、阶段证据和 technique 关系。
- **输出**：tactic/technique 后验概率、阶段判断和 OT 风险。
- **数据集/规模**：OT 过程/事件观测；精确实验规模需全文核验。
- **效果**：后验风险识别/推理评估；摘要未给完整 F1/AUC。
- **Embedding**：没有神经 embedding；用离散证据节点、条件概率表和 ATT&CK 语义。
- **分类器/推理**：Bayesian-network inference，输出可解释 posterior。
- **ATT&CK 用法**：ATT&CK ICS 提供 BN 节点语义、阶段/技术层次和先验结构。
- **代码**：未找到官方代码。
- **证据等级**：IEEE DOI/摘要支持 BN 与 ATT&CK ICS；概率表和数据需全文核验。

## 42. TRACE（IEEE TDSC, 2025）

- **论文/入口**：TRACE: Relationship Analysis and Causal Factor Extraction in Cyber Threat Intelligence Reports；<https://doi.org/10.1109/TDSC.2025.3532885>。
- **方法/模型**：规则/模式与 tag 抽取实体，SBERT 编码句子，BiLSTM/知识映射识别关系，再构造 causal graph。
- **输入**：CTI 报告文本、句子和实体/事件关系。
- **输出**：因果因素、攻击技术节点和关系图。
- **数据集/规模**：710 篇 CTI reports。
- **效果**：论文报告关系/因果抽取 F1=0.87（任务级细分需全文核验）。
- **Embedding**：SBERT sentence embeddings，再用知识映射增强。
- **分类器/推理**：BiLSTM/深度关系与序列分类器，随后图推理。
- **ATT&CK 用法**：技术作为因果图节点/语义锚点，不是日志边的直接真值。
- **代码**：未找到官方代码。
- **证据等级**：IEEE DOI 和作者全文 PDF 支持模型、710 reports、F1。

## 43. Traffic2Chain（IEEE TIFS, 2025）

- **论文/入口**：Traffic2Chain: Revealing Covert Multi-Step Attacks Through Unsupervised Traffic Behaviour Correlation；<https://doi.org/10.1109/TIFS.2025.3601396>。
- **方法/模型**：无监督多层次流量行为关联；用 SimCSE 对事件/行为语义编码并聚类，再用 LLM 生成事件描述。
- **输入**：连续网络流量行为流、会话上下文和事件序列。
- **输出**：实时多阶段告警、攻击阶段和 ATT&CK sub-technique 注释。
- **数据集/规模**：流量 traces；论文报告面向 40-Gbps 能力的评估，具体流量量和场景需全文核验。
- **效果**：F1=98.36%。
- **Embedding**：SimCSE sentence embedding；LLM 进一步为聚合事件生成自然语言语义。
- **分类器/推理**：无监督 clustering/correlation，不是常规监督 softmax classifier。
- **ATT&CK 用法**：行为关联后做 tactic/sub-technique 注释和解释，避免把 ATT&CK 当作无监督训练标签。
- **代码**：未找到官方代码。
- **证据等级**：IEEE DOI/摘要支持方法和 F1；数据协议需全文核验。

## 44. MuCamp（IEEE TIFS, 2025）

- **论文/入口**：MuCamp: Generating Cyber Campaign Variants via TTP Synonym Replacement for Group Attribution；<https://doi.org/10.1109/TIFS.2025.3578233>；作者 PDF：<https://insuplee.github.io/files/2025_mucamp_tifs.pdf>。
- **方法/模型**：在 ATT&CK v10.1 的 TTP 序列上做同义技术替换/增强，生成 campaign variants，再进行攻击者/组织归因。
- **输入**：campaign TTP 序列、专家标签和 ATT&CK technique/tactic 关系。
- **输出**：增强后的战役变体、campaign embedding 和 adversary-group attribution。
- **数据集/规模**：858 个专家标注的真实 campaign；覆盖 14 tactics、206 techniques（作者 PDF口径）。
- **效果**：报告 embedding 和 group-attribution 提升；逐任务 F1/Recall 需全文表格核验。
- **Embedding**：campaign/TTP sequence embedding；具体 RNN/Transformer、维度和 pooling 需全文核验。
- **分类器/推理**：embedding 相似度 + attribution classifier，具体分类头 NR。
- **ATT&CK 用法**：ATT&CK v10.1 提供 TTP 词汇、父子技术关系和可替换/不可替换的同义约束。
- **代码**：作者 PDF 可得；未确认官方代码。
- **证据等级**：作者全文和 DOI 支持版本、数据量和方法。

## 45. SAGA（IEEE TDSC, 2026 卷期）

- **论文/入口**：SAGA: Synthetic Audit Log Generation for APT Campaigns；<https://doi.org/10.1109/TDSC.2025.3640696>；数据站：<https://www.saga-cyber.net/dataset>；预印本：<https://arxiv.org/abs/2411.13138>。
- **方法/模型**：可配置的合成审计日志生成器，把 benign system activity 与按 Mandiant adversary lifecycle/ATT&CK procedure 生成的恶意活动混合；提供单 campaign 和多 campaign 融合。
- **输入**：攻击 campaign 配置、时间窗（1 小时/1 天）、主机/应用行为模板和 ATT&CK technique procedure。
- **输出**：按事件级/技术级标注的 audit logs，用于 event-based technique hunting 和 APT campaign detection。
- **数据集/规模**：公开简单评估 v1（5 campaigns，恶意事件低于 1%）；完整评估 v2（28 个独立 synthetic base campaigns + 10 个 3-campaign mixed campaigns，约 120 万以上事件、14.5 GB）；训练语料 1000 single-campaign + 100 mixed-campaign logs，约 5.1 TB。
- **效果**：论文用 event-based hunting 和 campaign detection baseline 展示未见 technique 检测；公开摘要未给出全部模型的统一分数，必须看全文实验表。
- **Embedding**：事件/节点特征表示；具体编码器、维度和预训练策略 NR。
- **分类器/推理**：数据站对应 event-level hunting、深度 campaign detector baseline；生成器本身不是分类器。
- **ATT&CK 用法**：定义恶意 procedure、生命周期顺序和细粒度事件标签，是合成数据的生成约束。
- **代码**：公开数据站和 JSON schema；生成器代码/完整 benchmark runner 未确认公开。
- **证据等级**：论文 DOI、预印本和数据站交叉确认；合成真值不能替代独立真实测试集。

## 46. APTREC（Computer Networks, 2026）

- **论文/入口**：APTREC: APT tactic/technique recognition based on large language model；<https://doi.org/10.1016/j.comnet.2026.112146>。
- **方法/模型**：把恶意 provenance 子图/日志证据组织成上下文，由 LLM 识别 ATT&CK tactic/technique，并生成可解释归因。
- **输入**：恶意 provenance subgraphs、事件证据和上下文描述。
- **输出**：technique、tactic 和可解释的攻击归因/证据说明。
- **数据集/规模**：APT provenance/scenario 数据；摘要没有披露完整场景数、节点数和独立标注协议。
- **效果**：摘要报告相对基线 F1 提升约 13%，recall 提升约 9%；绝对分数需全文核验。
- **Embedding**：LLM 的图/文本上下文表示；底座 LLM、图序列化和向量维度 NR。
- **分类器/推理**：LLM classification/reasoning head，可能包含 prompt/结构化解码；需全文核验。
- **ATT&CK 用法**：标签 ontology、attack-pattern 上下文和归因语义。
- **代码**：未找到官方代码。
- **证据等级**：出版社摘要支持任务和相对提升；不能据此宣称有细粒度边级真值。

## 47. ICSThreatQA（ESWA, 2026 卷期）

- **论文/入口**：ICSThreatQA: a knowledge-graph enhanced question answering model for industrial control system threat intelligence；<https://doi.org/10.1016/j.eswa.2025.130180>。
- **方法/模型**：构建 ATT&CK ICS threat KG，比较 KG-RAG 与其他 RAG；检索相关实体/关系，再交给 LLM 生成答案并回填证据。
- **输入**：ICS 威胁情报问题、ATT&CK ICS 实体/关系和检索上下文。
- **输出**：带 ATT&CK 证据 grounding 的自然语言答案。
- **数据集/规模**：620 个专家验证 QA 对，来源于 MITRE ATT&CK ICS。
- **效果**：KG-RAG relevance=0.968，correctness=0.660；两者不同，不能把 relevance 当作正确率。
- **Embedding**：KG entity/relation embedding + LLM retrieval context；具体 TransE/RotatE/文本编码器需全文核验。
- **分类器/推理**：RAG 检索、重排序和生成，不是传统分类器。
- **ATT&CK 用法**：填充 ICS 知识图谱、实体关系和答案证据。
- **代码**：未确认公开代码。
- **证据等级**：出版社摘要支持 620、0.968、0.660；KG 构建细节需全文核验。

## 48. NEXUS（NDSS, 2026）

- **论文/入口**：NEXUS: Towards Accurate and Scalable Mapping between Vulnerabilities and Attack Techniques；<https://www.ndss-symposium.org/ndss-paper/nexus-towards-accurate-and-scalable-mapping-between-vulnerabilities-and-attack-techniques/>。
- **方法/模型**：面向大规模 vulnerability-to-TTP 映射的可扩展框架。
- **输入**：CVE/vulnerability 文本、漏洞上下文和候选 ATT&CK/TTP。
- **输出**：CVE 到 ATT&CK technique/TTP 的多标签映射。
- **数据集/规模**：超过 92,000 个 CVE、208 个 TTP。
- **效果**：最大 F1=97.94%；具体 micro/macro、zero-shot 和跨年份划分需论文全文核验。
- **Embedding**：文本 encoder 表示；具体 encoder、负样本和向量维度 NR。
- **分类器/推理**：多标签 classifier；具体架构和阈值需全文核验。
- **ATT&CK 用法**：目标标签集/候选 TTP ontology。
- **代码**：NDSS 页面需要进一步确认 artifact 状态，当前不标“有代码”。
- **证据等级**：NDSS 页面/摘要确认数据规模和 F1；复现实验配置需全文核验。

## 49. RACONTEUR（NDSS, 2026）

- **论文/入口**：RACONTEUR: A Knowledgeable, Insightful, and Portable LLM-Powered Shell Command Explainer；<https://www.ndss-symposium.org/ndss-paper/raconteur-a-knowledgeable-insightful-and-portable-llm-powered-shell-command-explainer/>。
- **方法/模型**：shell-command 文档/知识检索器 + LLM 解释器；将命令意图与 ATT&CK tactic/technique 对齐。
- **输入**：shell command、参数、执行上下文和可检索文档。
- **输出**：自然语言命令解释、风险说明和 ATT&CK tactic/technique。
- **数据集/规模**：大规模 shell-command corpus；完整规模、恶意/良性比例和人工评测集需全文核验。
- **效果**：解释质量/可迁移性评估；精确分数 NR。
- **Embedding**：retriever 的文本向量 + LLM token representation；具体 embedding model NR。
- **分类器/推理**：retrieval/reranking + LLM generation，不是独立 softmax 分类器。
- **ATT&CK 用法**：命令意图标签、解释结构和安全知识 grounding。
- **代码**：NDSS artifact 状态需页面进一步确认。
- **证据等级**：NDSS 页面/摘要级；不要补写未公开的模型名和数据量。

## 50. Dynamic characterisation + mitigation（FGCS, 2026 卷期）

- **论文/入口**：Dynamic characterisation of cyberattacks based on the MITRE ATT&CK framework applied to the optimisation of a mitigation selection process；<https://doi.org/10.1016/j.future.2025.108272>。
- **方法/模型**：ML technique recognizer 先从流量/事件识别行为，再通过 ATT&CK/CAPEC ontology inference 计算残余风险并选择缓解措施。
- **输入**：UWF-ZeekDataFall22 网络流/incident logs 和工业用例上下文。
- **输出**：TTP 识别、动态攻击刻画、残余风险和 mitigation recommendation。
- **数据集/规模**：UWF-ZeekDataFall22 + industrial use case；完整流数量和场景划分需全文核验。
- **效果**：模型识别和决策支持验证；摘要未给完整 F1/AUC/决策收益数字。
- **Embedding**：流统计/行为特征表示；具体神经 embedding NR。
- **分类器/推理**：ML classifier + ontology inference/决策层。
- **ATT&CK 用法**：把低层流量行为连接到 technique、mitigation 和 CAPEC 关系，形成闭环决策。
- **代码**：文章开放获取，但未确认作者代码。
- **证据等级**：出版社全文/摘要确认数据集和两阶段架构；实验细节需全文核验。

---

## 结论：这 50 篇对你的研究最重要的可复用模式

1. **监督标签**：Malware2ATT&CK、Weapon、Automated CTI mapping、MITREtrieval、NEXUS；ATT&CK 是样本级多标签，但通常不是事件边级真值。
2. **知识库/推理约束**：Malware2ATT&CK、MITREtrieval、AUTOMA、ICSThreatQA、Debapt；关键是本体关系用于候选筛选、一致性修正或检索 grounding。
3. **阶段语义**：SAGA、MGDA、Traffic2Chain、APT cyber-range；ATT&CK 用于定义生命周期/阶段和事件解释。
4. **概率/置信度**：OT Bayesian Networks、风险传播模型；输出 posterior/risk，而不是未经校准的 softmax。
5. **归因/攻击者画像**：MuCamp、TRACE、APTREC、Debapt；需要把技术识别与 group attribution 分开评估。

对你研究内容 3 的直接约束是：`Y_scene`、部分 technique-evidence 标注和边级证据都应由你定义并记录 provenance；不能声称它们是 ATT&CK 或 SAGA 自动提供的现成真值。对研究内容 4，若采用 Bayesian layer，至少应报告 calibration curve、Brier score、ECE、selective risk 和跨工具/跨场景测试。
