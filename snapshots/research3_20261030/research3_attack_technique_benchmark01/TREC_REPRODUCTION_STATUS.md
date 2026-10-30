# TREC复现状态

本轮重新访问作者17页PDF https://nesa.zju.edu.cn/download/TREC.pdf ，确认原始任务是溯源子图、恶意节点/子图采样、Siamese few-shot识别。DOI10.1145/3658644.3690221，CCS2024。它不能接任意文本就称原方法。

已存在的本地审计：../provenance_baserepro_11/reports/TREC_FULL_AUDIT_SUMMARY.json；../provenance_baserepro_11/delivery/TREC/results/REPRO_REPORT.md。旧审计完成298 JSON成员、48,987,382事件、43技术目录；这是历史数据审计，不是本轮重读全量或模型运行。技术目录是脚本类别元数据，不能当成已认证473图样本/NOI/图边界/划分。

本轮新增TREC专属本地标准库环境，未安装替代GNN，无原模型推理。缺认证官方方法源码/模型、论文图标签/NOI边界、few-shot代表集与划分、CAM输入到对应图及标签的有效转换。P0成绩N/A，状态PARTIAL_REPRODUCTION_WITH_BLOCKERS。未发作者邮件。
