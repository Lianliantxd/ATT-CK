# 官方与独立评价器核验

未改get_statistics.py成功执行，命令/退出码见results/OFFICIAL_RUN.json，输出见results/official_stdout.txt及官方CSV。历史模型输入为排除受限步骤后的4868条，标签来自官方metadata键。random-trials显式设5，仅控制官方附加随机比较，不影响五模型的确定性评价行；不冒充README默认1000次随机试验。

独立evaluate_techniques.py在official_compat模式对五模型的Top1/5/10、P@1/5/10、R@1/5/10及MRR全部一致，最大绝对差约1.14e-15，见results/evaluator_deltas.json。扩展F1@5非官方脚本输出。官方weighted_MRR未列为本项目主指标；保持官方原CSV，不自行宣称该辅助项已独立验证。

README全量数字只存PAPER_REPORTED_RESULTS.csv。完整4943响应/198步未重算，因为必须排除受限正文；本轮不能宣称原论文完整复现。按975全分母的Ministral行另列，不能强行与其官方968有效响应行一致。

官方稳定性代码还有可能的问题：run_id按scenario_variant计数而stability按scenario-step聚合；rank_stdev某些组重复append，且实现用样本标准差。未修补/宣称稳定性完全复现，本轮仅验证分类指标。
