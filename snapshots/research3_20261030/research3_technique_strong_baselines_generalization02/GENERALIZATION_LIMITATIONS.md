# 泛化资格

本轮所有P0结果均为PUBLIC_EXPOSED_DEVELOPMENT；P1和P2与之共享执行，不是独立TEST。GT只在数据配对和评价中读取，不进入预测器。未经授权的场景1步骤35—37全部变体在ZIP成员正文读取前排除；无模型API、无权重下载、无服务器修改。

P0重新分组仍是开发诊断。P1同源重新抽样，与模型能力变化不同；变体选择变化也会改变Gold/行为。固定变体控制只控制执行，不控制v1/v2内容和P0标题差异。v2不是独立外部集。P2的385执行-step对195逻辑step不等权，必须同时查看query与Step-macro。

GROUPED_VALIDATION_RESULTS.csv包含每场景/执行的实际步数、类别、未见类、TopK/P/R/MRR/F1与多标签比例；没有用这些标签训练模型。DATASET_DEPENDENCY_GROUPS.csv固定logic-step/execution/scenario/hash组。没有把五replica拆入训练测试。脚本模板独立性未认证，不声称EXTERNAL_TEST。当前EXTERNAL_TEST_NOT_READY。

来源类型细分类的P0/v2映射差异19种path、76文件已另存；audit/non-audit主体一致，算法本身以host-file分组、不按类型给权，因此主融合排序不受类型映射影响，但细来源跨版本分布不可直接因果比较。

仅7场景，不进行975独立样本bootstrap或精确跨场景显著性主张。重采样输出变化为描述性敏感性，未做跨独立攻击的显著性检验。
