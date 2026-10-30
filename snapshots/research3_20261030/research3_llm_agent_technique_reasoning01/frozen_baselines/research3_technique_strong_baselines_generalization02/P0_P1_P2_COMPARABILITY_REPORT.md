# P0、P1与P2可比性审计

三者都是开发条件，不能当作三个独立测试集。P0旧数据和结果保持冻结；本轮派生数据均另存，v2原归档未修改。

| 条件 | 输入与样本量 | 可用于什么 | 不能推断什么 |
|---|---|---|---|
| P0 | 官方v1预制查询，975查询/195逻辑step/385执行-step/34模拟 | 曝光开发比较、作者历史LLM参照 | 未见测试或975个独立执行 |
| P1主协议 | v2，5次fresh-window并随机选择允许变体；975查询，767不同内容 | 重新抽样与输入变化的开发稳定性 | 与P0差异全由采样引起 |
| P1固定变体控制 | v2，冻结P0每replica变体；975查询，792不同内容 | 在已选执行组合内观察窗口敏感性 | 排除v1/v2内容差异 |
| P2-Sampled | v2，每个P0选中过的执行-step一次，385查询/195逻辑step；7,339行 | 同源、固定10行/host-source预算参考 | 固定总行数或固定总token预算 |
| P2-Full-Authorized | 同385执行-step一次；680,280行 | 合法过滤日志中的完整可见输入上限、多源证据开发 | 全部原始攻击历史；相对采样输入的算法等预算增益 |

P0与P1都覆盖195逻辑step，但P2包含每个P0实际选过的执行-step各一次，共385条。因此P2 query-weighted均值对变体多的步骤给了更大权重；必须另报先执行/replica聚合、再按scenario+step计算的step-macro，不能以385当独立攻击step。

P1/P2的技术空间延续216父技术；GT只来自官方metadata标签键。分组元数据与GT仅在Reference；预测视图没有scenario/variant/step/路径答案。原行只通过opaque source_id和原行序号作审计追踪。官方标签不是逐行证据Gold。

v2 ZIP中央目录有42,596成员，仅1,136个victim日志成员被允许读取，共200,542,770原始字节。其余成员在正文读取前排除；可识别受限step普通文件72个均被拒绝。sequence目录完全未读取正文，不能利用混合sequence绕过受限step。最大单成员32MiB、压缩比1000、路径/符号链接/执行标记/文件后缀检查与控制日志排除均在正文前实施。归档SHA-256为 `ba824f500af6d64925792d6a693e54afb761d1cfb5fe515efb2206035772bade`。

v2实际source文件类型为audit420、authentication87、web_access69、application85、wazuh111、suricata68、system287、other9。来源不是每step都齐全；缺失source不提供负证据。P0 parser和P2 parser对部分应用/system/other路径存在19种路径映射差异，完整对照见 `datasets/manifests/SOURCE_TYPE_MAPPING_DIFFERENCES.json`。audit/authentication/suricata/Wazuh等主类型映射一致，host-file排名融合不依赖这些类型名称；跨协议详细来源比例和各应用源的可比性仍应谨慎解释。

全部P1/P2输入经官方八正则及严格残余注释清洗，680,280原行保持行数和行索引，101,179行改变；direct-ID残余为0。逐文件flattened text和每source逐行均通过独立核验，见 `datasets/manifests/STABLE_CLEANED.json`。初次临时未清洗构建作废，不应报告其指标。

现有材料没有完整v1过滤日志；只能将P0已采样行与v2合法完整日志进行观察重叠检查，不能计算完整版本差分。`datasets/manifests/VERSION_CONTENT_AUDIT.json`按同simulation+step+host+source记录可见行hash交并集；v2 full未在P0稀疏采样中出现的行，不能直接称为v2新增行。

P0的20,077个采样行出现次数中，12,858次在同host/source的v2清洗后完整日志中精确出现；90次来自本轮排除或无法对应的source。只有51条查询所有行精确对应，其余924条至少有一行未匹配。未匹配可能涉及版本内容、清洗差异、控制来源排除或匹配限制，不能自动归因于日志新增或丢失。

v2场景7在step3/6/8/10/13中共检出258行同时含runc和init的事件文字；这是本地v2实际存在的事实。P0是否没采到同类事件，只是采样观察；没有完整v1，无法独立证实它们全部是v2新增。具体分步计数与无正文的line/hash索引见VERSION_CONTENT_AUDIT及V2_RUNC_INIT_LINE_INDEX。

所有成绩应分别标明协议、知识条件、样本权重、预算和推理资格。P0作者历史GPT-5.5预测不得带入P1/P2排行榜。P0/P1/P2均含共享执行和已曝光方法开发，不支持正式外部泛化或跨场景显著性结论。

完整385个配对执行-step的host-source-clean行hash集合统计为：P0已观察独特行7,228，v2完整独特行678,972，交集4,585，并集681,615。该集合指标去除了P0重复抽样出现次数，与上述20,077行出现次数的分母不同。v2完整集合更大主要体现观察预算差异，不能用其低Jaccard断言跨版本大规模漂移。

场景7分步runc+init行计数：step3=152、step6=15、step8=15、step10=61、step13=15；P0五次采样对应观察均为0。来源映射差异涉及76个source文件（19种path），不是新的数据成员读取。
