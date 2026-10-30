# P1：v2合法日志上的真实重采样协议

本轮P1已实际生成975条查询，覆盖195个逻辑攻击步骤、7场景。输入来自本地CAM-LDS v2，**不是v1原始日志的纯重采样**，也不是独立测试。主状态为 PUBLIC_EXPOSED_DEVELOPMENT。

官方参照代码为 `ait-aecid/attack-manifestations-interpretation` 固定提交 `42bbd2cf8409f64a1e6c8fc936c91725e8c558b2` 的 `create_llm_prompt_resample.py`，保存于 `datasets/create_llm_prompt_resample_official_42bbd2c.py`。对其进行了静态阅读，并只提取 `sample_log_file` 函数进行6种长度的采样等价检查；**没有运行缺少授权过滤的官方main**。安全适配实现在 `datasets/build_v2.py`。

采样冻结如下：

1. 先基于ZIP中央目录元数据建立允许清单，再读取正文。仅允许P0真实选中过的385个 `(simulation_id, step_id)` 组合，34个模拟执行标识。场景1步骤35/36/37所有可识别变体在正文读取前排除；无法安全映射的成员拒绝。仅读steps下victim/logs；attacker、AttackMate、output、collectd等排除；不解压、不执行日志。
2. 文件顺序固定为ZIP完整成员路径字典序，模拟目录顺序等价于官方排序。官方rglob文件顺序依赖文件系统，本实现改为显式排序，并记录这一实现差异。
3. Python Random种子42。每次replica遍历全部允许step-variant及其host-source，若原文件行数大于10，均匀抽取 `randint(0, n-10)` 起点及其后连续10行；短文件保留全部行。随后对每个逻辑步骤从允许变体池随机choice。重复5次，每次真正重新抽取所有窗口。
4. 保留官方逐行UTF-8 errors=ignore、通用换行及rstrip换行语义。清洗逐原始行执行，不删行、不改变原始行数、顺序和line_id；清洗后空字符串仍占用原预算。因此不会按清洗后空行重新采样。
5. 预测视图应用官方八条清洗正则，另移除嵌套MITRE/technique/tactic注释完整值及所有直接T四数字ID（包含下划线边界）。原680,280行中101,179行被修改；直接ID由101,759处降为0。`raw_text_hash`保留原行哈希，`text_hash`仅对应清洗文本。
6. Prediction View仅有sample_id/text/sources，source_id为不含模拟标签的opaque散列；sources包含source_type及line_id/text/text_hash/raw_text_hash。Reference View独立保存GT和scenario、step、simulation、variant、replica、input_hash。Gold只取官方labels.json对应metadata键；父技术ID作为主Gold，原子技术另存。

输出：

- `datasets/p1_resampled/prediction.jsonl` 与 `reference.jsonl`：官方fresh-sampling核心流程在受限变体池上的主P1，975条，767个不同规范化内容哈希、208条重复记录。
- `datasets/p1_resampled/prediction_fixed_variant.jsonl` 与 `reference_fixed_variant.jsonl`：额外控制，冻结P0每条查询实际选用的变体、仅重新抽取行窗口，975条，792个不同规范化内容哈希、183条重复记录。它是本项目适配控制，**不是官方默认随机变体流程**。
- `datasets/manifests/SOURCE_PROVENANCE.jsonl` 与 `ALLOWLISTED_MEMBERS.jsonl`：原成员hash、来源、行数和授权读取范围。
- `datasets/manifests/STABLE_CLEANED.json`：四个预测输入文件的完整hash及清洗审计通过标记。

input_hash由有序source_type及clean line text_hash列表构成，排除line_id、文件路径和标签元数据；它用于标记同一可见内容，不能据此宣称独立攻击执行。相同短文件或偶然相同窗口仍可产生重复输入，重复不作为鲁棒性证明。

主P1相对P0同时改变了v1/v2日志版本、真实窗口抽样和变体选择，不能把成绩变化因果归于单一采样因素。固定变体控制消除了变体选择变化，仍保留版本及抽样差异。P2-Sampled与P1同属v2，但两者执行-step分布和权重也不同；配对时需明确同模拟、同step、同预算并以逻辑步骤或场景汇总。

初次本轮构建曾缺少标签清洗，该临时构建已经被严格清洗版本覆盖，相关早期预测不具有效性。所有可报告的P1/P2结果必须对应 STABLE_CLEANED_V1 文件hash；禁止使用初次未清洗数据的成绩。
