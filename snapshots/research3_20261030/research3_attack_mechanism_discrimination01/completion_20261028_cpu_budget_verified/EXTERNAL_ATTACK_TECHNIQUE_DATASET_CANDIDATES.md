# 有界外部来源核查

核查日期2026-10-28，只查看公开页面/普通元数据，无下载原始数据。

1. [OTRF APT29](https://github.com/OTRF/Security-Datasets/tree/master/datasets/compound/apt29)：作者发布raw通道日志及Day1约367M/Day2约1.6GB归档链接；[emulationplans](https://github.com/OTRF/Security-Datasets/tree/master/datasets/compound/apt29/emulationplans)确有apt29.xlsx。没有完成表格步骤与原始事件绑定，不能仅据目录名认定可评分。[根LICENSE为MIT](https://raw.githubusercontent.com/OTRF/Security-Datasets/master/LICENSE)，而README文字写GPL3，须保留不一致并核查具体数据条款。
2. [OTRF atomic/Windows execution host](https://github.com/OTRF/Security-Datasets/tree/master/datasets/atomic/windows/execution/host)实际存在ZIP目录，旧small路径404不等于数据不存在。当前只核实文件清单，没有建立可信事件/步骤标签映射。
3. [AttackMate v4](https://zenodo.org/records/19810174)有原始日志、三场景及playbook元数据，但CAM-LDS同样使用AttackMate/AttackBed，因此不应当作已独立的新分布。[CAM-LDS论文](https://link.springer.com/article/10.1007/s10207-026-01318-x)与[当前发布](https://zenodo.org/records/18861762)不能取代本轮固定16.1知识。

本机已知Mordor Day1派生26步参考是经规则处理和实体替换的事件卡，不能冒充原始日志；21个技术ID加UNKNOWN中仅12在本216空间，其他9个历史ID与UNKNOWN未自动猜测映射。目录登记的原始路径未找到，但并未声称全机不存在副本。本轮不因该缺口扩大搜索或读取归档。人工审查标记的历史文件不等于本轮独立人工Gold。
