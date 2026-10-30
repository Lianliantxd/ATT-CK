# 实际资格核查：OTRF/Mordor APT29

主候选为[OTRF Security-Datasets](https://github.com/OTRF/Security-Datasets)的compound/apt29。联网公开README/许可/仓库元数据读取连续失败，浏览器也导航超时；备用文档读取自动审查两次超时，没有下载归档。不能声称已经核实当前上游许可、体积或提交。

实际找到本地派生参考 `/Users/tianxd/Documents/mid-term/intent_rd1_20261017/source/mordor-apt29-day1.L-noisy.gt.json`（84616 bytes），26个事件/步骤，声明来源为原仿真计划apt29.xlsx。包含21个非UNKNOWN技术ID及UNKNOWN；与现216候选实际相交12个，集合差为['T1035', 'T1045', 'T1050', 'T1077', 'T1081', 'T1086', 'T1107', 'T1122', 'T1145', 'UNKNOWN']。准确列表与哈希在LOCAL_SOURCE_QUALIFICATION。没有根据旧技术名猜映射，也未将UNKNOWN删掉制造分数。

参考文件自称human_reviewed，生成器说明最初为透明规则对齐草稿，并有人审后版本元数据；本轮没有取得审查者/原始记录凭证，不把它作为本轮新增独立人工语义参考。其输入还有实体替换和L-noisy适配，不能冒充原生日志。代码期待的datasets/Security-Datasets/.../apt29路径在所检查本地位置不存在，匹配原始计划/原生事件未就绪。

可执行判断：适合作为后续资格核查对象；当前不能运行严格216父技术外部测试。下一步仅需先取得原始计划、matching native logs、许可和脚本清单，确认标签窗口与传感器ID泄漏；大型归档仍需新授权。不能从Windows平台不同直接推导脚本独立。现有副本已在别的项目使用，因此即使恢复观察，也应先标EXPOSED_EXTERNAL_REFERENCE。

另核查现有ExCyTIn-Bench本地manifest和作者README/许可快照：这里只有派生告警图与作者LLM问答，不是本任务所需步骤级ATTACK原生日志标签；完整数据库未取得，故不合格为当前技术分类测试。
