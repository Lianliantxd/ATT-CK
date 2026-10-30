先说明核验结论：**截至2026年10月29日，我确认 CAM-LDS 的原始数据论文已经正式发表；找到的三项后续使用研究目前是预印本。尚未核实到它已被多篇安全顶会或高水平期刊论文广泛采用，不能把“有相关预印本”说成“已有成熟的顶会基准体系”。**

以下把数据、标签、论文和结果分开介绍。

**一、CAM-LDS是什么？**

CAM-LDS 全称是 **Cyber Attack Manifestations – Log Data Set**，由奥地利 AIT Austrian Institute of Technology 团队构建。它在可复现的 Linux 企业网络环境中执行攻击，收集攻击留下的日志、告警和网络记录，主要服务于“从记录解释攻击行为”的研究。[数据发布页](https://zenodo.org/records/18861762)

它的正式论文是：

> Landauer 等，*CAM-LDS: Cyber Attack Manifestations for Automatic Interpretation of System Logs and Security Alerts*，**International Journal of Information Security，25，文章148，2026年8月26日发表**。[正式论文](https://doi.org/10.1007/s10207-026-01318-x)

需要把几个数字区分开：

| 数字 | 实际含义 |
|---|---|
| **7个场景** | 七类多步骤攻击链 |
| **34次场景变体运行** | 不同入口、提权、持久化方式等组合 |
| **81种技术、13种战术** | 作者报告的数据覆盖范围 |
| **18类数据来源** | 主机、应用、网络及安全工具产生的记录 |
| **198个步骤** | 原论文LLM实验中产生可用日志的步骤 |
| **216个候选父技术** | 原论文排序任务的候选空间，**不是数据中实际覆盖216类攻击** |

前四项来自数据说明；198和216属于论文实验设置。[数据说明](https://zenodo.org/records/18861762)、[论文实验部分](https://link.springer.com/article/10.1007/s10207-026-01318-x#Sec30)

**它是仿真环境中真实执行攻击得到的数据，不是生产企业遭受真实APT入侵的现场数据。** 因而，“存在完整攻击链”与“可以证明真实APT泛化能力”是两个不同判断。

**二、七个攻击场景具体是什么？**

| 场景 | 主要内容 | 运行变体数 |
|---|---|---:|
| 1. 视频服务器攻击 | 侦察、Web漏洞利用、提权、持久化及发现 | 18 |
| 2. Linux恶意软件 | 植入、Rootkit、发现和外传 | 2 |
| 3. 横向移动 | 凭据获取、跨主机移动、数据收集及破坏 | 6 |
| 4. 网络攻击 | 端口敲门、权限利用、防火墙规则修改 | 1 |
| 5. 网络嗅探 | 流量嗅探、访问令牌复用 | 1 |
| 6. 客户端攻击 | 恶意文件或插件、远程控制、持久化及收集 | 5 |
| 7. Docker攻击 | 服务探测、凭据攻击、应用利用及容器逃逸 | 1 |
| **合计** |  | **34** |

这些变体共享不少环境和攻击步骤，因此不能视为34个完全独立、互不相关的攻击家族。[官方场景说明](https://zenodo.org/records/18861762)

**三、数据里究竟有什么？**

按用途，可以分成四部分：

| 数据部分 | 典型内容 | 能支持什么 |
|---|---|---|
| 主机日志 | Linux audit、认证、syslog、软件包管理、cron等 | 进程执行、身份、文件与系统活动分析 |
| 应用日志 | Apache、ZoneMinder、FTP、Puppet、Docker、Nextcloud、邮件等 | 应用访问、服务行为和跨主机关联 |
| 安全与网络记录 | Wazuh、Suricata告警、网络流、PCAP | 告警解释、通信分析和多源关联 |
| 环境与执行资料 | 服务配置、主机facts、攻击执行时间和输出 | 解释环境条件、定位步骤和建立标签 |

作者还收集了 collectd 性能数据。PCAP单独发布，避免日志仓库过大。[论文数据采集说明](https://link.springer.com/article/10.1007/s10207-026-01318-x)、[PCAP发布页](https://zenodo.org/records/18701095)

文件组织大致如下：

```text
某个场景变体/
├── 某主机/logs/                 日志及告警
├── 某主机/configs/              服务配置
├── 某主机/facts.json            主机配置摘要
└── attacker/logs/
    ├── attackmate.json         攻击执行及时间标签
    └── output.log              攻击执行输出
```

此外提供两种按步骤切分的数据：

- **manifestations_raw**：根据攻击步骤的时间区间抽取记录。
- **manifestations_filtered**：在此基础上过滤周期性、已知系统背景活动。

它们又按 `steps`、`sequences`、`techniques`组织。**不同目录可能包含同一批日志的重复表示，不能直接混合后随机划分训练集和测试集。** [目录与过滤说明](https://zenodo.org/records/18861762)

还有一个限制：采集时**没有模拟正常用户业务活动**，但有系统空闲背景活动。因此，它适合研究攻击表现与解释；单独用它衡量真实SOC环境中的误报率、正常业务区分能力，证据不足。[数据发布说明](https://zenodo.org/records/18861762)

**四、标签是什么？标到哪一层？**

核心是 **攻击步骤对应的MITRE ATT&CK技术标签**，可以包含：

| 标签/字段 | 含义 |
|---|---|
| 场景、变体、步骤ID | 发生在哪条攻击路径的哪一步 |
| 技术ID | 如父技术 `Txxxx` |
| 子技术ID | 如 `Txxxx.xxx` |
| 战术 | 技术所属的攻击阶段或目的分类 |
| 执行时间 | 用于把攻击步骤与日志时间区间关联 |

**一个步骤可以有多个技术标签，不是严格单标签分类。** 作者的标签可以从攻击执行记录以及公开的 `labels.json`取得。[标签入口](https://zenodo.org/records/18861762)、[作者代码仓库](https://github.com/ait-aecid/attack-manifestations-interpretation)

这里最容易产生误解：

> 标签表明作者执行的这个攻击步骤对应哪些技术，不保证从这个步骤随机抽出的十几行日志，就能充分证明所有标签。

另外，原论文在评价时把子技术归并到父技术，并去重。例如子技术与其父技术最终按父技术层级比较。因此，**原论文的主要结果是父技术排序结果，不是精确子技术识别结果**。[原论文评价定义](https://link.springer.com/article/10.1007/s10207-026-01318-x)

**五、原论文怎么评价？**

原论文使用五个LLM进行零样本解释：

1. 给出一个步骤的日志片段。
2. 输出最相关的10个ATT&CK技术，按可能性排序。
3. 输出攻击/正常活动的置信判断。
4. 给出简短解释。

论文描述每个“主机—日志来源”最多抽取10行，并对198个步骤重复5次；单个完整模型对应990条记录。**990条不是990个独立攻击步骤。**

同时，官方仓库后来明确说明：保存的 `llm_queries.json`基于数据集v1，原生成脚本重复选中同一变体时可能得到相同提示；另提供了重新采样脚本。复现实验必须同时注明数据版本和采样脚本。[论文设置](https://link.springer.com/article/10.1007/s10207-026-01318-x)、[官方复现说明](https://github.com/ait-aecid/attack-manifestations-interpretation#creating-llm-prompts)

主要指标含义如下：

| 指标 | 含义 |
|---|---|
| **Top-1 Accuracy** | 第一名是否命中任意一个真实技术 |
| **Top-5 / Top-10 Accuracy** | 前5/10名中是否至少命中一个真实技术 |
| **Precision@k** | 前k个预测中，有多少比例是正确技术 |
| **Recall@k** | 所有真实技术中，有多少比例出现在前k名 |
| **MRR@10** | 第一个正确答案排名的倒数取平均；前10无命中记0 |

原论文还评价重复运行的稳定性：Same-Top-1、Pair-Top-1、Fleiss’ Kappa和正确答案排名波动。**稳定不代表正确，模型也可能稳定地预测错误。** [指标定义](https://link.springer.com/article/10.1007/s10207-026-01318-x)、[官方评价代码](https://raw.githubusercontent.com/ait-aecid/attack-manifestations-interpretation/main/get_statistics.py)

**六、原论文对应的指标是多少？**

下面是作者官方仓库公布的结果，百分比保留两位，MRR保留四位。**这是作者结果，不是我们项目重跑的结果。**

| 模型 | 记录数 | Top-1 | Top-5 | Top-10 | MRR@10 | Precision@10 | Recall@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **GPT-5.5** | 990 | **41.82%** | **60.81%** | **67.17%** | **0.5036** | **7.82%** | **58.52%** |
| GPT-5.2 | 990 | 40.40% | 60.10% | 65.05% | 0.4869 | 7.51% | 57.10% |
| Llama-4 Maverick | 990 | 25.66% | 38.69% | 44.65% | 0.3125 | 5.01% | 37.42% |
| Qwen3-32B | 990 | 16.06% | 25.45% | 30.91% | 0.1998 | 3.18% | 25.03% |
| Ministral-3B | 983 | 10.07% | 16.07% | 16.68% | 0.1238 | 1.68% | 13.94% |
| 随机基线 | 4943 | 0.67% | 3.29% | 6.50% | 0.0193 | 0.67% | 4.63% |

来源：[作者公布的完整结果表](https://github.com/ait-aecid/attack-manifestations-interpretation#computing-classification-accuracy)。

**67.17%的Top-10命中率不能解释为“67.17%的攻击技术被完整识别”。** 它只要求每条记录前十个预测中至少命中一个标签；GPT-5.5的Recall@10是58.52%，是另一个指标。

这些结果也**不是Seen/Unseen划分实验**：原论文采用零样本提示，没有用我们后来建立的监督训练划分来评价未见类别泛化。

**七、到目前为止，哪些论文实际使用了它？**

我核实到以下四项。发表状态严格分开，不能都称为“已发表高质量论文”。

| 研究 | 截至核验日期的状态 | 实际任务 |
|---|---|---|
| **CAM-LDS原始论文** | **已正式发表于IJIS，2026-08-26** | 日志片段→ATT&CK技术排序 |
| **Just Testing, Move Along: Evasion of LLM-based System Log Interpretation by Prompt Injection** | arXiv预印本，2026-07-27；未核实正式录用 | 日志提示注入与规避 |
| **Mapping Linux Auditd Telemetry to MITRE ATT&CK Techniques with a Locally Deployed Small Language Model** | Preprints.org，2026-09-21；页面明确未同行评审 | auditd→整场攻击技术集合 |
| **CyberClear: A Benchmark for LLM Agent Systems on APT Attack Chain Provenance** | arXiv预印本，2026-09-26；未核实正式录用 | 长日志→攻击链溯源图 |

来源：[原始论文](https://doi.org/10.1007/s10207-026-01318-x)、[Just Testing](https://arxiv.org/abs/2607.24174)、[Auditd研究](https://www.preprints.org/manuscript/202609.1848)、[CyberClear](https://arxiv.org/abs/2609.32424)。

如果“高质量”严格指安全顶会、CCF-A或指定期刊分区，**目前这次检索没有证据支持列出多篇符合该条件的后续使用论文**。这不等于不存在遗漏，但不能补造名单。

**八、后续研究的指标与数据**

**1. 本地小模型处理auditd**

使用规则筛选、聚合，再交给Qwen2.5-7B；评价29个场景变体的整场技术集合。

| 方法 | Macro Precision | Macro Recall | Macro-F1 | Micro-F1 |
|---|---:|---:|---:|---:|
| 仅确定性规则目录 | 50.5% | **83.6%** | **62.4%** | 未在此处确认 |
| 规则＋Qwen2.5-7B | **54.2%** | 56.5% | 54.2% | 58.5% |

这篇研究一个重要的负结果是：**加入小模型后，Precision略升，但Recall明显下降，Macro-F1反而低于规则目录。** Macro-F1是各变体F1的平均，不能用表中的平均Precision和Recall重新计算替代。[原文结果与消融](https://www.preprints.org/manuscript/202609.1848)

它按**整场攻击**计分，且使用不同的父子技术匹配规则，不能与原论文逐步骤的67.17% Top-10直接比较。

**2. 日志提示注入研究**

该研究混合使用CAM-LDS和AIT-LDSv2，评估15个攻击案例，指标是把攻击误判为正常的 **攻击成功率ASR**。

其上下文增强注入报告：

| 被测模型 | ASR |
|---|---:|
| GPT-5.2 | 66.7% |
| Devstral-2 | 73.3% |
| Llama-3.3 | 86.7% |
| Qwen系列对应模型 | 86.7% |

这里**越高表示防守模型越容易被规避**；这些数值是混合案例结果，不是CAM-LDS全量技术识别准确率。[原文实验与结果](https://arxiv.org/html/2607.24174v1#S4)

**3. CyberClear攻击链重建**

它使用CAM-LDS和PROVCON构建派生基准，报告450个样本：318个单步骤、132个多步骤。评价图代码质量和五项LLM语义评分。

论文附录给出的 **CyberProvenance＋GPT-5.6-Terra** 一组结果为：

| 指标 | 数值 |
|---|---:|
| BLEU | 0.4952 |
| ROUGE-L | 0.6968 |
| CodeBLEU | 0.7016 |
| Pass@1：图代码可编译 | 0.9333 |
| Single：单步骤语义 | 0.8897 |
| Loose：多步骤识别 | 0.7438 |
| Strict：时序及因果一致性 | 0.6337 |
| Detail：实体关系细节 | 0.6124 |
| Scenario：整体攻击叙事 | 0.7263 |

**这些是整个派生基准的结果，不能写成CAM-LDS单独结果；语义分数也不是人工确认的正确率。** [CyberClear原文及附录表5](https://arxiv.org/html/2609.32424v1#A1.T5)

**九、这些信息对我们当前项目意味着什么？**

我们当前使用的是 **CAM-LDS的项目派生输入**：195个步骤、975条记录，后期又进一步限制日志和知识长度；384条则是诊断子集。这些设置与作者198步骤的零样本实验不同，依据见[本地实际输入](/Users/tianxd/Documents/mid-term/research3_domain_adaptive_contrastive_learning01/data/P0_INPUTS.jsonl)和[最新来源审计](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/INPUT_LABEL_SCOPE_AUDIT_REPORT.md)。

因此，论文中可以把CAM-LDS用于**受控Linux环境下的技术识别和多源证据研究**；但若要声称解决真实APT意图理解、Seen/Unseen泛化或生产环境误报问题，还需要相应的划分、独立参考与额外验证。作者的67.17%、后续工作的54.2%，以及我们的历史结果，必须连同各自的输入和评价单位一起报告。
