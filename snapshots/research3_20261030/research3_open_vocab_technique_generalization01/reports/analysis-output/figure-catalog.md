# 图目录与解释要求

全部图为实际保存结果，提供PDF、SVG与100dpi PNG。主图ONE、曲线同时ONE/MULTI。颜色仅区分方法/目标，不表示统计显著性。

## figure01_main_seen_unseen

- 文件：figures/figure01_main_seen_unseen.pdf / .svg / .png
- 内容：总体/Seen/Unseen三面板。数据源：FUSION_RESULTS.csv。
- 为什么绘制：说明总体MRR收益与Unseen恢复是否兼得。
- 应注意：S0总体/Seen最强但U=0；C4恢复部分U，仍损失约40.7%Seen且仅保留约51.8%Z0的U。
- 对判断的影响：需保留S0强基线及S/U绝对指标，不能只比较C4对Z0总体增益。
- 图注必须保留：DEVELOPMENT_ONLY；216完整候选；975查询/195步骤/7场景；3-seed SD不是独立样本置信区间；无新增训练。
- 核查：刻度/零值/分母/视图与表一致；图2统一gamma诊断与正式fold-specific gamma明确区分；图4类等权不冒充查询加权。

## figure02_seen_unseen_tradeoff

- 文件：figures/figure02_seen_unseen_tradeoff.pdf / .svg / .png
- 内容：固定偏置曲线及正式方法点。数据源：SEEN_UNSEEN_TRADEOFF.csv; FUSION_RESULTS.csv。
- 为什么绘制：展示Seen/Unseen取舍与内验证选参位置。
- 应注意：正式C4低于Z0 H；gamma=.4诊断点有更高H但仍未满足U80%阈值；C3/C4相近。
- 对判断的影响：不能用诊断点事后替代C4；不能声称整个简单融合族不可能改善H。需要未来独立验证校准稳定性。
- 图注必须保留：DEVELOPMENT_ONLY；216完整候选；975查询/195步骤/7场景；3-seed SD不是独立样本置信区间；无新增训练。
- 核查：刻度/零值/分母/视图与表一致；图2统一gamma诊断与正式fold-specific gamma明确区分；图4类等权不冒充查询加权。

## figure03_mixed_coverage

- 文件：figures/figure03_mixed_coverage.pdf / .svg / .png
- 内容：Mixed Seen/Unseen/双命中覆盖。数据源：MIXED_SAMPLE_COVERAGE.csv; FUSION_RESULTS.csv。
- 为什么绘制：检验Hit-any是否掩盖混合标签遗漏。
- 应注意：C4双命中0，Z0为4.14%；C4的Seen覆盖提高没有产生两组联合覆盖。
- 对判断的影响：将Mixed双命中作为完整识别的必要诊断，而不是仅汇报总体命中。
- 图注必须保留：DEVELOPMENT_ONLY；216完整候选；975查询/195步骤/7场景；3-seed SD不是独立样本置信区间；无新增训练。
- 核查：刻度/零值/分母/视图与表一致；图2统一gamma诊断与正式fold-specific gamma明确区分；图4类等权不冒充查询加权。

## figure04_long_tail_class_mrr

- 文件：figures/figure04_long_tail_class_mrr.pdf / .svg / .png
- 内容：按训练支持桶的类等权MRR。数据源：LONG_TAIL_TECHNIQUE_RESULTS.csv。
- 为什么绘制：防止查询加权指标掩盖频率先验与尾部弱点。
- 应注意：C0在More-shot类等权MRR很高，One-shot为0；C3/C4在One/Few改善而Unseen仍低于Z0。
- 对判断的影响：频率是强对照；泛化论断必须报告类等权与全216Macro-F1。
- 图注必须保留：DEVELOPMENT_ONLY；216完整候选；975查询/195步骤/7场景；3-seed SD不是独立样本置信区间；无新增训练。
- 核查：刻度/零值/分母/视图与表一致；图2统一gamma诊断与正式fold-specific gamma明确区分；图4类等权不冒充查询加权。

视觉QA：评估agent逐张检查4张PNG；root另行逐张检查，均清晰无重叠或截断。此项仅证明可读性，不替代数学评价核验。首次Poppler字体缓存警告通过独立临时字体缓存修复，同一数据同一布局重新导出；最终tradeoff图再次检查。
