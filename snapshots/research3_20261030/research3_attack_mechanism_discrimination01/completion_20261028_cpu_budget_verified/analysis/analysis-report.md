# 冻结开发实验分析

问题：同公共观察、同候选和同检索器时，Literal/原生关系能否超越RAW？完整数值如下。

|预算协议|方法|输入|Top1 %|Top10 %|MRR@10|
|---|---|---|---:|---:|---:|
|BYTE|bm25|LITERAL_PLUS_RELATIONS|1.128|17.026|0.04166|
|BYTE|bm25|LITERAL|1.128|17.026|0.04166|
|BYTE|bm25|RAW_PLUS_LITERAL|0.718|16.308|0.03646|
|BYTE|bm25|RAW|1.231|13.538|0.03564|
|BYTE|char|LITERAL_PLUS_RELATIONS|0.821|9.846|0.03209|
|BYTE|char|LITERAL|0.821|9.128|0.03066|
|BYTE|char|RAW_PLUS_LITERAL|0.923|13.744|0.03533|
|BYTE|char|RAW|1.846|14.872|0.05164|
|FEATURE|bm25|LITERAL_PLUS_RELATIONS|1.026|9.231|0.02994|
|FEATURE|bm25|LITERAL|1.026|9.231|0.02994|
|FEATURE|bm25|RAW_PLUS_LITERAL|1.026|9.333|0.03235|
|FEATURE|bm25|RAW|1.436|11.077|0.03749|
|FEATURE|char|LITERAL_PLUS_RELATIONS|0.615|3.385|0.01072|
|FEATURE|char|LITERAL|0.615|3.385|0.01072|
|FEATURE|char|RAW_PLUS_LITERAL|1.641|6.667|0.02423|
|FEATURE|char|RAW|2.872|11.692|0.04614|
|FEATURE|literal_jaccard|LITERAL|0.410|7.077|0.02227|


BYTE BM25 Literal的Top10差+3.487个百分点，FEATURE差-1.846个百分点；关系无已证实独立增益。95,550行不是独立攻击样本；这是98个确定性条件在同975抽样查询的重复评价。7场景是依赖分块而非经抽样确认独立总体。144项差值、条件bootstrap与Holm校正完整保留，不能挑p值证实泛化。

Claim：本实现未显示稳定机制表示增益。证据：全条件表及两个预算敏感性协议。允许措辞：“在已曝光P0和这些CPU检索器中未证实稳定增益”；禁止：“机制理解无价值”。不确定性：神经尚未跑、BM25关系通道不活跃；决定：保留弱结论。

Claim：候选池扩大时固定pair分数不变而最终排序退化。证据：140015去重保存分数、5850池输出。允许：保存结果层面的候选竞争解释；禁止：已完成跨batch重测或已证明模型缺机制理解。不确定性：缓存、上游截断/域失配；决定：保留。

两张图为实际数值绘制，不含模型未执行成绩。无人工语义结果，无外部测试结论。
