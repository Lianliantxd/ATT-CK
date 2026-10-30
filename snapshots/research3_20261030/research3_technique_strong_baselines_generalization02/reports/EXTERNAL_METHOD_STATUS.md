# 外部方法状态增量核查

2026-10-27。本轮复用既有审计，按本地目录/文件名及明确报告作有限增量核查。**未发现可使 TREC/APTREC 完整模型或 KnowHow 语义分支进入本轮本机预测的新增完整资产。** 这是有范围的本地结论，不是对最新官方发布的断言；没有重新下载、联系作者、连接服务器或试跑缺输入主入口。

| 方法 | 已取得与可复用 | 本轮实质增量 | CAM-LDS 成绩资格与具体阻断 |
|---|---|---|---|
| KnowHow | 固定官方源码、词典组件、已建隔离环境；旧项目技术排序适配已输出 P0 预测 | 核清本地只有历史预计算技术向量，缺日志编码模型；确认不能以服务器历史 FastText 替代本轮本机推理 | 原 P0 Top-10 21.03% 是 **ADAPTED_BASELINE**，不是论文完整模型性能；新语义推理 N/A。主模型与 n-gram sidecar 留服务器，授权仅只读核查且本轮未连接；许可状态也不完整 |
| TREC | 论文、历史数据审计及 298 JSON/43 技术目录的元数据报告 | 未新增认证核心实现、对应图包或原模型；不重复读取约 4,899 万事件 | **NOT_EXECUTED / PARTIAL_REPRODUCTION_WITH_BLOCKERS**。缺认证方法源码/模型、NOI 与图边界、few-shot 代表集和划分，以及 CAM-LDS 日志到对应图语义的有效适配；不能将技术目录当成 473 个认证图样本 |
| APTREC | 20 页正式全文及既有全文配置/数值审计 | 无新增匹配图集、规则/权重/核心实现；不重建空环境 | **NOT_EXECUTED / PARTIAL_REPRODUCTION_WITH_BLOCKERS**。缺原始图/GT/划分、认证实现、确切基础模型修订号与 LoRA、1862 规则、完整配置；旧材料记载数据需向作者索取。图示 Prompt 不能替代可执行套件 |
| OCR-APT | 固定官方源码 `d927daf6057c80a46bdc5e44d7aa373d4a3ad5d3`，旧纯函数执行回执 | 保留源码存在的事实；无新匹配输入/服务/调用授权 | **OFFICIAL_COMPONENT_ONLY**；旧回执是 Prompt/IOC/查询模板组件，并非完整检测器或 investigator 推理。缺匹配异常子图、描述/统计、动态查询响应和检索上下文；本轮新 LLM 调用未授权，未启动 GraphDB |

## 依据及复用资格

- `research3_attack_technique_benchmark01/TREC_REPRODUCTION_STATUS.md` 与 `APTREC_REPRODUCTION_STATUS.md`：继承上一轮任务/阻断说明；不据此重报本轮推理。
- `research3_baseline_reproduction01/OCR_APT_REPRODUCTION_STATUS.md`：区分真实源码与运行数据/服务缺口；不能写成“官方代码全部缺失”。
- `research3_baseline_reproduction01/environment_manifests/KnowHow_environment.json`、`research3_benchmark_baselines_parallel01/KnowHow_ENVIRONMENT_MANIFEST.json`：固定源码/本地环境；旧 pip check 成功仅证明当时组件环境一致，不能证明当前完整神经模型依赖已就绪。
- `provenance_baserepro_07/delivery/reproduction_reports/continuation_07/CONTINUATION_REPORT.md`、`EMBEDDING_MANIFEST.json`：历史 FastText 是独立 MITRE 语料训练组件，主模型/sidecar 未随本地交付。历史成功训练不等于本轮 CAM-LDS 识别成功。
- `provenance_baserepro_11/reports/TREC_FULL_AUDIT_SUMMARY.json`、`APTREC_REPRODUCTION_REQUIREMENTS.md`：复用历史资产审计，不执行原日志全扫。

本轮未新增这些外部算法的环境；已有环境不重复创建，也未修改。只对真实运行的新算法登记独立环境及推理回执。语义强基线缺口见 `SEMANTIC_ASSET_AUDIT.md`；不得以字符 n-gram、BM25 或空环境充作已复现的外部预训练语义模型。

本地证据路径与哈希见 `manifests/SEMANTIC_ASSET_AUDIT.json`。旧论文正式发表/原始任务资格继承已保存全文或报告，本轮不声称重新在线核验最新资产。
