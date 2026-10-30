# 外部数据资格：2026-10-28
本轮状态为 `EXTERNAL_TEST_NOT_READY`。已完成两个指定来源的具体元数据核查，未下载日志体、未引入外部训练样本、未执行外部预测。CSV 中留空指标表示未运行，不能解释成零分。外部数据准备不阻塞 CAM-LDS 合法分组开发训练。

## 可验证来源与固定版本
本轮 web 工具成功读取官方仓库、许可及 Splunk 的示例 YAML；GitHub connector 进一步固定了原始元数据与日志 LFS 指针。所有新增副本均位于 `data/external_candidates/`，来源与本地哈希见该目录回执。

| 来源 | 本轮 connector 解析的 master commit | 已确认事实 | 当前资格 |
|---|---|---|---|
| OTRF/Security-Datasets | d9d40ef123d2c87d5d3df28c96bcab4f0faccc87 | APT29 Day1 主机归档与模拟计划路径存在；现有本地计划及派生数据已在其他研究中曝光 | RELATED_SOURCE_DEVELOPMENT；INSUFFICIENT_INDEPENDENCE；LABEL_MAPPING_UNCERTAIN |
| splunk/attack_data | 671f9f5b065f03a5502db07c20f1fe3f620d29d9 | 一个固定 YAML 声明 T1003.003 与三类对应日志；根 LICENSE 为 Apache-2.0 | DATASET_LEVEL_LABEL_ONLY；独立评价尚未准入 |

这里的 commit 是本轮读取时的固定快照，不声称永远是最新版本。web 缓存的 Splunk 提交列表落后于 connector 的分支引用，未用缓存页替代版本冻结。web 直接读取固定 Splunk YAML 有 cache miss，connector 固定 SHA URL 的读取成功；OTRF 二进制计划内容请求失败，但目录元数据可读。这些错误不能推导出数据不存在。

## OTRF / Mordor：只能保留为已曝光开发候选
[固定 APT29 目录](https://github.com/OTRF/Security-Datasets/tree/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87/datasets/compound/apt29) 包含 Day1、Day2 及 emulationplans。Day1 对应 `datasets/compound/apt29/day1/apt29_evals_day1_manual.zip`，Git blob 为 `7352679a173ec0310f9d0ed587782545182dd394`，目录 API 报告压缩 blob 为 13,944,973 bytes；[Day1 README](https://github.com/OTRF/Security-Datasets/blob/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87/datasets/compound/apt29/day1/README.md) 的历史大小文本为 367M。两者含义未核对，不能将其直接当成解压后大小或当前下载预算。未打开或下载该归档。

计划路径为 `datasets/compound/apt29/emulationplans/apt29.xlsx`，官方固定 blob 为 `e2b95dc306967a6a2d9af033cf1fe7c3ad155c13`，25,051 bytes。本地发现两份同 SHA256 的旧计划，各 25,050 bytes；其 Git blob SHA1 为 `41cb7225de70b188f6a8c230331fef0f1b9bcd23`，与固定官方 blob 不同。这里只读取 XLSX 元数据、列头及步骤/技术名称列，不读取日志归档。两个工作表为 32、35 行（含表头），标签列主要为旧技术名称，没有显式 T-ID；不会凭名称或描述正文中出现的 ID 自动构造权威映射。

继承的 26 步派生参考含 21 个非 UNKNOWN 技术 ID，其中 12 个与冻结 216 候选直接相交，9 个旧 ID 不在候选中，另有 UNKNOWN。它们已经被其他项目接触，且是规则辅助事件卡，不能认定为新增、未见、事件级 Gold。旧报告中的 expected raw path 不存在，仅说明那个指定路径；本轮文件名检索发现其他旧归档路径，但未读取，不能把“指定路径缺失”写成“全机无副本”。

官方仓库根 [LICENSE](https://github.com/OTRF/Security-Datasets/blob/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87/LICENSE) 是 MIT；[仓库 README](https://github.com/OTRF/Security-Datasets) 仍写 GPL-3.0。此处如实记录文本冲突；未核实归档中是否另有数据许可，不把元数据的可访问性扩大为日志再分发资格。

Windows 主机记录与 CAM-LDS 存在平台差异，这可形成跨域候选，但不能证明脚本独立。原始步骤时间窗、日志对应、脚本/命令复用及旧技术 ID 跨版本语义均未通过。即使恢复对应关系，也优先用于 `RELATED_SOURCE_DEVELOPMENT`；不得重新命名为未见 TEST。

## Splunk：一个具体、可限额申请的 Bag 候选
固定元数据：[atomic_red_team.yml](https://github.com/splunk/attack_data/blob/671f9f5b065f03a5502db07c20f1fe3f620d29d9/datasets/attack_techniques/T1003.003/atomic_red_team/atomic_red_team.yml)。dataset id=`cc9b25e1-efc9-11eb-926b-550bf0943fbb`，元数据日期 2020-10-08，environment=`attack_range`，directory=`atomic_red_team`，唯一声明技术为 `T1003.003`。其父技术 `T1003` 确实存在于本地冻结的 216 候选词典；此映射仅完成本条标签的父层次对齐。

YAML 描述同一技术的多个 Atomic Red Team 测试变体并包含结果不明项，`mitre_technique` 位于整份数据集层级。未提供每个事件的技术标签或穷尽背景事件标注。必须将对应日志组成一个数据集 Bag，不能为每条事件复制 T1003 Gold，也不能把同一次执行的三种传感器拆为独立测试样本。其三条声明日志在固定目录中存在，已读取的仅为 130–133 bytes LFS 指针：

| 相对目录末尾 | sourcetype / source | LFS 对象 bytes | LFS SHA256 |
|---|---|---:|---|
| windows-sysmon.log | XmlWinEventLog / Microsoft-Windows-Sysmon Operational | 12,883,992 | ee1c7cd9fa20013c82da17f8cb1998197c117ab4c209ab56203290bc90739fda |
| 4688_windows-security.log | XmlWinEventLog / Security | 11,176 | 81e1d4e381f4dc38b97c48f9fa5b0ab0b098810c321b7d4599029a9f22530259 |
| crowdstrike_falcon.log | crowdstrike:events:sensor / crowdstrike | 10,681 | c4275ab0ef976b0d00ba7840031a06d9f47d1beeaf4c3056d2fc7bb8fe08b38a |

三者均位于 `datasets/attack_techniques/T1003.003/atomic_red_team/`，合计 12,905,849 bytes，未下载 LFS 对象。固定根 [LICENSE](https://github.com/splunk/attack_data/blob/671f9f5b065f03a5502db07c20f1fe3f620d29d9/LICENSE) 为 Apache-2.0。本轮未找到完整的 Splunk 本地副本；这是有界文件名检索结果，不是全机不存在的证明。

这一项可作为后续有界下载申请对象，但单个技术、单组 Bag 无法证明 216 类泛化。Windows/多传感器分布不同也不等同于攻击脚本独立；CAM 具体脚本与 Atomic 测试的重合仍未核实。当前不得加入训练或用于模型选择，也没有外部成绩。

## 后续准入条件与用途分离
OTRF 先核对计划版本、标签跨版本映射及日志步骤对应；Splunk 如有必要，应单独申请以上三个固定 LFS 对象的 12,905,849 bytes 日志下载，再验证哈希、背景事件、执行重复及 Bag 边界。当前授权不自动覆盖日志下载，未为等待授权暂停本轮 CAM 开发训练。

若外部资源准备用于训练，先核实监督单位与来源，记录与 CAM 标签交集，然后标为开发数据。若用于独立测试，须在最终算法选择前冻结，记录未参与训练、困难负例、参数搜索或选择；看到标签错误并用于调参后即转为开发。现有 OTRF 已曝光参考不满足未见资格，Splunk 元数据也尚不足以认定正式独立 TEST。

目前外部训练样本=0，评价样本=0，新增日志下载=0；`EXTERNAL_GENERALIZATION_RESULTS.csv` 仅记录资格和未运行状态，不报告泛化提升。

