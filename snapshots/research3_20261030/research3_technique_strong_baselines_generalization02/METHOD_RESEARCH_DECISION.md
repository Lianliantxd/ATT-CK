# 科研决策

主状态STRONG_BASELINES_EXTENDED；辅状态RESAMPLING_AND_V2_PROTOCOLS_READY、PARTIAL_COMPLETION_WITH_DOCUMENTED_BLOCKERS。来源感知简单基线在部分指标有开发收益；完整新候选机制未证明优于合理最强同知识基线，所以新机制NO-GO为当前论文核心。独立泛化未证明。

同216候选/K2下，正式非消融方法最高Top1=CharacterNgramTFIDF(8.62%)，最高Top10=CharacterNgramTFIDF(27.79%)，最高MRR=CharacterNgramTFIDF(0.1294)。候选EvidenceLineFusion在某些Top10条件胜RRF，但Top1/MRR明显下降；NoSourceCalibration是预设消融，不事后升级为主方法。

相同native输入的全文对照已运行，预算40record/2048regex-token亦运行，不能只对原18.05%弱参考说改进。知识K0—K4控制显示变化不等于知识推理；原生格式/来源标题本身改变检索结果。P1/P2的字符表示往往更有竞争力，融合不能跨采样全面稳定压过它。

下一步若研究LLM，先围绕真实错误案例验证执行证据与知识语义脱节、泛词匹配、源内结果状态，不增加无证据Agent。现有错误trace只是候选排序证据，不是独立Gold；没有依据授予新模型调用权限。外部完整TREC/APTREC仍需数据/模型配套，语义嵌入仍资源受阻。

可以进入可复核baseline/数据协议实验整理阶段；尚不能把本候选机制作为已证实创新写入正式性能主张，也不能宣称外部泛化。保留负结果、所有失败与无效初跑记录。
