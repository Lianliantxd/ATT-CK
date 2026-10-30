# 外部数据实例资格：真实服务器取得与Bag配对

**三份真实日志已取得并通过SHA256核验，1个Bag已完成静态配对；主模型外部评价仍未执行。** 数据准入标记E1_BAG_FEASIBILITY_DATA_READY_NO_MODEL_EVALUATION，它只表示数据/接口可行性候选，不表示已经完成E1开发性能评价；独立测试仍EXTERNAL_TEST_NOT_READY。

用户本轮明确回复“保存在服务器上，/home/tianxiaodan/code/ATT/，本地没路径”。据此原始与清洗正文仅保存在`/home/tianxiaodan/code/ATT/R3_OPEN_VOCAB_TECHNIQUE_GENERALIZATION01/external_dataset/`；本地仅有代码、公开元数据、下载与清洗统计回执，不保存这些日志正文。首次40秒读取超时失败保留在SERVER_DOWNLOAD_FAILURE_V1.json，后续同三对象有界重试成功，下载器实际wall747.45秒。授权、manifest与代码SHA绑定一致。历史提案authorized=false及E0快照保留，不能据此覆盖本轮后续grant；SERVER_DOWNLOAD_MANIFEST内继承的“not_included: GPU or server operation”是原提案文字残留，具体用户服务器目的地授权与当前grant只覆盖下载/静态准入，不包含GPU/模型前向。

| 项目 | 已确认事实与限制 |
|---|---|
| 来源 | splunk/attack_data，固定commit `671f9f5b065f03a5502db07c20f1fe3f620d29d9`，实例 `cc9b25e1-efc9-11eb-926b-550bf0943fbb` |
| 真实对象 | Sysmon 12,883,992 bytes；Security 11,176；CrowdStrike 10,681；共12,905,849 bytes，各SHA匹配固定LFS指针 |
| 许可 | 固定根Apache-2.0，五级祖先目录无更近LICENSE/NOTICE；许可与出处随服务器副本保留 |
| 标签 | 官方YAML在实例级声明T1003.003→父T1003，属于216候选；单正类非穷尽Bag标签 |
| 评价单位 | 三传感器合成一个Bag，不把7023条记录或3文件当独立攻击样本 |
| 解析 | Sysmon7010个XML事件、Security8个XML事件、CrowdStrike5个NDJSON记录；XML未解析残余0 |
| 标签剥离 | 移除7015注释字段、105处技术ID；模型输入使用中性Bag及传感器ID，参考文件隔离 |
| 派生输入 | 服务器processed/BAG_INPUT.jsonl，15,236,232 bytes，SHA `5b97effee468ef68851f114391381145ac8355b2b2b47faeedc7a3335bbba1cd` |
| 配对参考 | 服务器processed/BAG_REFERENCE.jsonl，235 bytes，SHA `46411d80dc49361e1c390575222808f97548f630272a208101cc2ff597934f4e` |
| 解析资格 | STRUCTURE_PARSED_NOT_SEMANTICALLY_VALIDATED，不宣称隐式标签线索全部消除 |
| 脚本/执行独立性 | UNRESOLVED；没有此次Atomic脚本固定版本或SHA，CAM-LDS对应脚本身份也不完整 |
| 真实模型外评 | 无外部GTE特征，没有运行B3/GTE/融合；预测0行，9个NOT_EXECUTED结果为N/A |

公开元数据与固定许可来自[根LICENSE](https://github.com/splunk/attack_data/blob/671f9f5b065f03a5502db07c20f1fe3f620d29d9/LICENSE)、[官方YAML](https://github.com/splunk/attack_data/blob/671f9f5b065f03a5502db07c20f1fe3f620d29d9/datasets/attack_techniques/T1003.003/atomic_red_team/atomic_red_team.yml)。五个Git blob逐字校验的原审计保留于METADATA_ONLY_QUALIFICATION_AUDIT.json；本轮成功下载的精确对象、来源URL和SHA在server_receipts/SERVER_DOWNLOAD_RECEIPT.json。PREPROCESS_AUDIT.json是实际服务器文件取回；额外SERVER_INTEGRITY_STDOUT_CAPTURE.json明确是成功SSH输出转录，不能冒充第三份服务器原文件。

只运行惰性文本/XML/JSON解析，没有执行日志中的命令，没有新包、模型下载、训练、GPU或LLM。7023个记录没有逐事件Gold。来源只声明一个正类，未来可以报告声明正类的Rank/Hit/MRR；不能将其他候选都当真实FP进而宣称完整多标签Precision/F1。

E2仍缺执行/脚本依赖核验、可靠的多技术覆盖和真实完整预测。这个单类单Bag即使进一步完成模型前向，也只能作为有限迁移测例，不能证明216类总体泛化。用户下载/静态准入授权不自动涵盖新GTE前向；当前不另开模型预算。

OTRF/Mordor继承原审计，计划字节差异、已曝光APT29派生、步骤映射及许可文本冲突仍在；本轮没有读其日志或重编号TEST。原研究目录保持只读。
