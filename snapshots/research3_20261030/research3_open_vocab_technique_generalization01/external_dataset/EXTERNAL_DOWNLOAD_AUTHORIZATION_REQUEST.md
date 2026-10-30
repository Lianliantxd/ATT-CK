# 单实例公开日志下载授权请求

状态：等待本轮明确授权；未下载任何日志正文。仅申请固定 commit `671f9f5b065f03a5502db07c20f1fe3f620d29d9` 的 Splunk Attack Data 实例 `cc9b25e1-efc9-11eb-926b-550bf0943fbb`，三个 YAML 声明传感器合并为 **1 个 Bag**。

| 文件 | 字节 | 必须匹配的 LFS SHA256 |
|---|---:|---|
| windows-sysmon.log | 12,883,992 | `ee1c7cd9fa20013c82da17f8cb1998197c117ab4c209ab56203290bc90739fda` |
| 4688_windows-security.log | 11,176 | `81e1d4e381f4dc38b97c48f9fa5b0ab0b098810c321b7d4599029a9f22530259` |
| crowdstrike_falcon.log | 10,681 | `c4275ab0ef976b0d00ba7840031a06d9f47d1beeaf4c3056d2fc7bb8fe08b38a` |

合计 **12,905,849 bytes**（约 12.31 MiB）。不拉取仓库、ZIP、同目录其他日志。下载目标为本项目 `external_dataset/raw/`。以下是由已核实路径构造的固定 commit LFS media URL；尚未请求正文，实际可用性须授权后验证。

- [windows-sysmon.log](https://media.githubusercontent.com/media/splunk/attack_data/671f9f5b065f03a5502db07c20f1fe3f620d29d9/datasets/attack_techniques/T1003.003/atomic_red_team/windows-sysmon.log) → `/Users/tianxd/Documents/mid-term/research3_open_vocab_technique_generalization01/external_dataset/raw/windows-sysmon.log`
- [4688_windows-security.log](https://media.githubusercontent.com/media/splunk/attack_data/671f9f5b065f03a5502db07c20f1fe3f620d29d9/datasets/attack_techniques/T1003.003/atomic_red_team/4688_windows-security.log) → `/Users/tianxd/Documents/mid-term/research3_open_vocab_technique_generalization01/external_dataset/raw/4688_windows-security.log`
- [crowdstrike_falcon.log](https://media.githubusercontent.com/media/splunk/attack_data/671f9f5b065f03a5502db07c20f1fe3f620d29d9/datasets/attack_techniques/T1003.003/atomic_red_team/crowdstrike_falcon.log) → `/Users/tianxd/Documents/mid-term/research3_open_vocab_technique_generalization01/external_dataset/raw/crowdstrike_falcon.log`

根 [LICENSE](https://github.com/splunk/attack_data/blob/671f9f5b065f03a5502db07c20f1fe3f620d29d9/LICENSE) 实读为 Apache-2.0，SHA256 `8505946b2464fa90223996d99eecbc7639a86648ca071f0cac21695be2623a0a`。已查看根、datasets、attack_techniques、T1003.003、atomic_red_team 五级目录，无更近 LICENSE/NOTICE；仅根有 LICENSE。研究副本保留许可及出处，修改后的派生输入显式注明变更。本次读取公开元数据，不执行日志内命令。

必要性：只有真实日志取得并核对哈希，才能验证 Bag 边界、处理格式、标签泄漏及执行/脚本依赖。YAML 的 T1003.003 是整个实例声明，不能复制为每条日志 Gold；三个传感器不是三个独立执行。此次仅为有界数据准入与本地静态可行性工作，不含服务器、GPU、新模型、新训练、LLM 或数据上传。主融合的外部 GTE 向量仍缺失，不能在未取得真实向量时填主模型成绩。

取得三个对象后仍不自动成为 E2：单类单 Bag 不能证明216类泛化；与 CAM-LDS 的脚本独立性、日志内规则标签、实际解析边界均需核验。当前 E0 / EXTERNAL_TEST_NOT_READY。

授权要求来源：用户本轮附件 §14.5 写明“只有存在明确下载授权时才执行”；§20.2 写明旧授权“不自动扩展至本轮”。本文件的 authorized=false 不代表拒绝，仅表示尚无本轮日志下载授权。
