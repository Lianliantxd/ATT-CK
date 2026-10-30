# 完整训练图解释

figure04_all_trained_mrr.pdf/svg/png：全部20方法/视图条件MRR，冻结单柱，训练双柱mean±3seedSD；误差不表示独立泛化CI。目的：检查普通监督强基线是否被忽略；需结合未见/宏平均指标，不能只挑一个视图最优。

figure05_trained_seen_unseen.pdf/svg/png：ONE协议同216排名Seen/Unseen Gold目标，670/450查询含145mixed重叠。目的：检查训练是否保持未见排序。目标子集非互斥样本，P/F1定义需另说明；图用MRR。

figure06_reliability_scene_deltas.pdf/svg/png：7场景B9−B8，ONE/MULTI均为seed均值，无推断误差条。目的：检查同池风险权重是否有一致增量。多数场景负或平，不选查询加权微正解释为稳定贡献。

figure07_contrastive_training_loss.pdf/svg/png：seed42、ONE协议，B5/B7/B9在7重叠训练折上的loss均值曲线。仅看优化趋势，不比较不同目标loss绝对高低，不把下降当泛化。旧figure01–03为CPU监督阶段历史图，最终结论以04–07及完整表为准。
