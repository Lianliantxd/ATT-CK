# 2024--2026 年 MITRE ATT&CK 相关文献复核报告（50 篇）

**交付版本：2026-08-31。** 本报告按“ATT&CK 在正文中承担实质作用”筛选，而不是只在 related work 中提到 ATT&CK。逐篇十字段展开见同目录 [详细核验表](./ATTACK_literature_detailed_2024_2026.md)，机器可读字段见 CSV：

- `ATTACK_literature_2024_2026.csv`

## 1. 先把“50 篇”和“50 篇都达到目标分区”分开

我把 50 篇作为**强相关候选池**交付，并逐篇记录排名状态；没有把未经核验的中科院分区伪装成已达标。按 CCF 2024 官方目录，目前可直接确认的条目为：

- CCF-A：11 篇（TIFS、TDSC、USENIX Security、NDSS）；
- CCF-B：10 篇（Computers & Security、Computer Networks）；
- 其余 29 篇：期刊可能属于中科院一区/二区、CCF-C，或不在 CCF 目录，必须按你们学校采用的最新中科院分区表逐条复核。

因此，这个文件是“50 篇强相关、可核验候选 + 严格等级标记”，不是声称“50 篇全部已经满足 CAS Q1/Q2 或 CCF A/B”。若学院把 50 篇全部设为硬门槛，必须先确认是否允许把 CAS 分区、CCF 目录、系统论文和实证评测混合计数；否则直接承诺 50 篇全部达标是不严谨的。

逐篇字段完整性统计：50 篇中有 28 篇的公开页面没有给出可安全转录的完整效果指标，20 篇没有公开完整数据规模，16 篇没有披露 embedding 细节；只有 6 篇能定位到作者代码或可下载 artifact/数据仓库。因此详细表中的 `NR/需全文核验` 是刻意保留的证据边界，不是漏填。

## 2. 筛选与核验规则

1. 时间窗：2024-01-01 至 2026-08-31（online-first 与卷期年份差异在 CSV 中按正式出版记录处理）。
2. 相关性：ATT&CK 必须用于标签、知识库/本体、攻击阶段语义、攻击图/风险推理、检测评测或数据生成中的至少一项。
3. 证据：优先 DOI/出版社/会议页面；没有全文时不猜测 embedding、分类器和数据规模，写成 `NR/需全文核验`。
4. 排名：CCF 按当前可获取的官方目录版本核对（链接页面为 2024-06-28，PDF首页标注 2022 目录）；中科院分区必须记录具体年份和版本，不能把 JCR、SJR 和中科院分区混写。
5. 代码：只有能定位到作者仓库或 artifact 的才标记为公开；“有 DOI”不等于“有代码”。

## 3. 50 篇清单（详细字段在 CSV）

|编号|年份|论文（简称）|venue|ATT&CK 用法|等级状态|证据级别|
|---:|---:|---|---|---|---|---|
|1|2024|Zero Trust + ATT&CK matrix|IEEE Access|韧性/控制覆盖|待核验 CAS|摘要级|
|2|2024|Malware2ATT&CK|Computers & Security|恶意软件→技术多标签|CCF-B|方法+指标|
|3|2024|Attention-Based API Locating|IEEE TIFS|API证据定位|CCF-A|摘要级|
|4|2024|Early Android ransomware detection|Computers & Security|Weapon：BERT+MLP+Android ATT&CK|CCF-B|全文+指标|
|5|2024|Maze ransomware forensics|ESWA|取证过程映射|待核验 CAS|摘要级|
|6|2024|SPP network traffic anomaly|Computers & Security|流量行为解释|CCF-B|摘要级|
|7|2024|Automated CTI ATT&CK mapping|Computers & Security|CTI→tactic/technique|CCF-B|方法+指标|
|8|2024|6G IT/OT cyber range|IEEE TCE|攻击仿真标签|待核验 CAS|摘要级|
|9|2024|Zero-day exploits in flows|Computer Networks|流量检测→技术|CCF-B|摘要级|
|10|2024|APT risk propagation|Computer Networks|ATT&CK攻击图风险|CCF-B|摘要级|
|11|2024|Maritime ATT&CK+D3FEND|IJIS|攻防知识映射|待核验 CAS|摘要级|
|12|2024|Hierarchical ICS IDS|Information Sciences|ICS检测语义|待核验 CAS|摘要级|
|13|2024|MetaCluster|IEEE TIFS|可解释分类标签|CCF-A|摘要级|
|14|2024|Zero-trust implementation strategy|IEEE TR|威胁建模/控制选择|待核验 CAS|摘要级|
|15|2024|Behavior-based intranet attacks|IEEE Access|行为分类|待核验 CAS|摘要级|
|16|2024|Attacker next-action prediction|Computers & EE|动作序列预测|待核验 CAS|摘要级|
|17|2024|Cybersecurity risk-management framework|JMIS|风险/缓解推理|待核验 CAS|摘要级|
|18|2024|Laccolith adversary emulation|IEEE TDSC|对抗仿真程序|CCF-A|摘要级|
|19|2024|AUTOMA|IEEE TNSM|威胁狩猎假设|CAS/CCF-C待核验|摘要级|
|20|2024|PARGMF|JISA|溯源规则匹配|待核验 CAS|摘要级|
|21|2024|ProvIoT|ACNS|联邦 IoT 检测|会议等级待核验|摘要级|
|22|2026|Debapt|Computers & Security|多智能体LLM+ATT&CK本体|CCF-B|摘要级|
|23|2024|APT cyber-range scenarios|IEEE Access|场景生成/覆盖|待核验 CAS|摘要级|
|24|2024|MITREtrieval|IEEE TNSM|BERT+本体 CTI检索|CAS/CCF-C待核验|方法+指标|
|25|2024|Lifecycle-based IDS|IEEE TMLCN|阶段化流量检测|待核验 CAS|摘要级|
|26|2024|Removing user-land hooks|IEEE Access|EDR实验程序|待核验 CAS|摘要级|
|27|2024|Sysmon+ELK malware sandbox|IEEE Access|日志行为标注|待核验 CAS|摘要级|
|28|2024|OpenPLC security|IEEE Access|PLC攻击/缓解映射|待核验 CAS|摘要级|
|29|2024|E-XAI|IEEE Access|IDS解释语义|待核验 CAS|摘要级|
|30|2025|MGDA|Computer Networks|溯源图检测+场景重构|CCF-B|摘要+指标|
|31|2024|Logging maturity model|Computers & Security|日志能力与覆盖|CCF-B|摘要级|
|32|2024|PLC obfuscation/honeypot|IEEE TNSM|ICS deception|CAS/CCF-C待核验|摘要级|
|33|2025|SPEDIA insider-threat dataset|Computers & Security|事件级 ATT&CK 标注数据集|CCF-B|摘要+方法|
|34|2024|Automated ATT&CK Technique Chaining|Digital Threats|技术链图推理|venue待核验|摘要级|
|35|2024|MITRE Engenuity EDR evaluation|ACM AsiaCCS|EDR覆盖测量|会议等级待核验|摘要级|
|36|2024|How does Endpoint Detection use ATT&CK?|USENIX Security|规则覆盖/一致性审计|CCF-A|全文+artifact|
|37|2024|VTT-LLM|Mathematics|漏洞→TTP微调|待核验 CAS|摘要级|
|38|2024|Genics|Applied Sciences|ICS场景生成|待核验 CAS|摘要级|
|39|2024|CVE→ATT&CK tactics|Information|漏洞→战术映射|待核验 CAS|摘要级|
|40|2024|Automated malware-report labels|Digital Threats|恶意软件报告标签|venue待核验|摘要级|
|41|2025|OT Bayesian networks|IEEE TIFS|ATT&CK ICS + 后验置信度|CCF-A|摘要/方法|
|42|2025|TRACE|IEEE TDSC|SBERT因果图|CCF-A|全文+指标|
|43|2025|Traffic2Chain|IEEE TIFS|无监督流量→阶段/子技术|CCF-A|摘要+指标|
|44|2025|MuCamp|IEEE TIFS|TTP增强与归因|CCF-A|作者全文|
|45|2026|SAGA|IEEE TDSC|ATT&CK生成审计日志|CCF-A|论文+公开数据站|
|46|2026|APTREC|Computer Networks|溯源子图→TTP|CCF-B|摘要级|
|47|2026|ICSThreatQA|ESWA|ATT&CK ICS KG-RAG|待核验 CAS|摘要+指标|
|48|2026|NEXUS|NDSS|CVE→TTP|CCF-A|摘要+指标|
|49|2026|RACONTEUR|NDSS|命令解释→ATT&CK|CCF-A|摘要级|
|50|2026|Dynamic characterisation + mitigation|FGCS|流量TTP识别+本体决策|待核验 CAS|全文/摘要|

## 4. 对你课题最值得优先精读的 10 篇

1. **SAGA（TDSC 2026）**：最接近日志输入、细粒度 ATT&CK 标签和未见技术泛化；可作为你研究内容3的合成数据/弱标注基线，但不能把合成日志当成真实世界真值。
2. **APTREC（Computer Networks 2026）**：最接近“恶意溯源子图→ATT&CK tactic/technique”的任务，但需要重点检查其子图构造是否有独立标注。
3. **OT Bayesian Networks（TIFS 2025）**：支持把 ATT&CK 节点作为概率图中的语义节点，与你想加入的置信度层直接相关。
4. **Traffic2Chain（TIFS 2025）**：说明流量侧可以做无监督多阶段关联，但其任务和你的日志溯源图仍有明显数据模态差异。
5. **TRACE（TDSC 2025）**：可借鉴“语义表示 + 关系/因果图”，但输入是 CTI 文本而不是系统事件图。
6. **Malware2ATT&CK（C&S 2024）**：可借鉴“预训练表示 + 图模型 + ATT&CK 知识图谱多标签”。
7. **MITREtrieval（TNSM 2024）**：可借鉴“BERT + ontology + voting”，但 TNSM 在 CCF 2024 官方目录中是 CCF-C，不能当 CCF-B 写。
8. **Automated CTI mapping（C&S 2024）**：可作为多标签文本映射基线，报告了 tactic/technique F0.5。
9. **How does Endpoint Detection use ATT&CK?（USENIX Security 2024）**：提醒你必须单独评估 ATT&CK 标签一致性和规则覆盖，不要只报告分类 F1。
10. **NEXUS（NDSS 2026）**：可参考大规模漏洞→TTP映射的数据构造和跨实体泛化评价。

## 5. 对研究内容3的直接启示

- 不要把 `Y_scene` 或 `M_partial` 写成公开数据集自带字段；它们应被写成你定义的监督接口，并保存来源、ATT&CK版本、标注者、证据片段和置信度。
- SAGA 的公开数据站可以用于预训练/压力测试，但真实测试集必须来自独立来源，且要做工具、脚本、主机和采集器的跨域拆分。
- ATT&CK 只能提供技术语义和先验，不能替代“哪条日志/哪条边是证据”的真值。定位指标必须有独立人工复核或可审计的 procedure-to-event 对齐。
- 如果最终加入贝叶斯层，建议输出 `P(technique | event/subgraph, context)`、校准曲线、Brier score、ECE 和 selective risk，而不是只给一个未经校准的 softmax 分数。

## 6. 来源与可复现性说明

- 公开 ATT&CK 系统综述及其 412 篇候选论文库：<https://arxiv.org/html/2502.10825>、<https://github.com/Yuning-J/MITRE-review-papers>。
- CCF 官方目录网页（2024-06-28）：<https://www.ccf.org.cn/Academic_Evaluation/By_category/2024-06-28/825349.shtml>；可获取的网络安全分类 PDF（首页标注 CCF 2022 目录）：<https://ai.cust.edu.cn/docs/2024-07/4a21fbb381f44225bcb98dcb2b2c9c59.pdf>。
- SAGA 数据站：<https://www.saga-cyber.net/dataset>。
- USENIX EDR artifact：<https://github.com/avirkud/endpoint-detection-mitreattack/releases/tag/sec24-ae-final>。

排名核验日期统一记录为 2026-08-31。中科院分区不是永久属性，提交论文前应以学院/图书馆指定的最新版本重新截图或导出证明。

## 7. 跨论文方法矩阵

|任务族|典型输入|代表模型/方法|典型输出|ATT&CK所在位置|
|---|---|---|---|---|
|CTI/CVE文本映射|CTI报告、CVE描述、命令文本|BERT/DistilBERT/SBERT、LLM微调、检索增强|tactic/technique多标签、解释文本|监督标签、ontology、检索约束|
|恶意软件/APP技术识别|汇编、API、权限、运行时行为|预训练编码器、GNN、BERT+MLP、注意力网络|恶意软件技术集合、API证据位置、早期告警|目标标签、语义特征和知识图谱先验|
|流量与日志检测|网络流、Sysmon/审计日志、端点遥测|SPP、深度IDS、GraphMAE、自监督异常检测|异常分数、阶段告警、技术标签|行为解释、阶段标签或TTP规则|
|溯源图/攻击链重构|系统实体关系图、事件子图|溯源图相关、前后向搜索、规则图推理、LLM|攻击场景子图、证据链、战术/技术|图节点语义、TTP匹配规则和攻击链约束|
|风险与置信度推理|OT观测、资产依赖、技术关系|Bayesian network、风险传播、D3FEND/KG|后验概率、风险、缓解动作|概率节点、先验关系、攻防知识库|
|场景生成/归因|攻击场景、TTP序列、仿真配置|规则/约束生成、TTP同义替换、LLM多智能体|合成日志、战役变体、攻击者画像|生成模板、技术序列和归因语义|

### 7.1 Embedding 与分类器的共同规律

- 文本类最多使用 BERT 家族（DistilBERT、BERT、SBERT）或 LLM；ATT&CK 技术描述通常作为第二路文本、ontology 检索文档或标签语义向量。
- 图类通常把实体/事件作为节点，把系统调用、因果、网络关系作为边；GraphMAE/图编码器学习表示，ATT&CK 规则在推理或后处理阶段注入，而不是把 ATT&CK ID 当普通 token。
- 多标签任务常用 sigmoid 输出每个 technique 的独立概率；少数工作用 voting、规则约束或知识图谱传播修正结果。
- 无监督工作（Traffic2Chain、MGDA 部分流程）先学习异常/相关性，再用 ATT&CK 做语义标注；这与“直接监督预测 ATT&CK ID”必须区分。
- 概率图工作（OT Bayesian Networks）不依赖神经 embedding，而是把可观测证据映射到 ATT&CK/阶段节点，通过条件概率得到后验置信度。

### 7.2 代码和数据集现实情况

公开、可直接复现实验代码非常少。明确可定位的开放资产主要是 USENIX EDR 评测 artifact 和 SAGA 数据站；其余条目多数只有 DOI/作者 PDF，或者仅公开数据说明而没有训练代码。因而论文复现时应把“论文声称的效果”和“你能独立复现的效果”分开记录。
