# 工具安全资格

本轮22项工程回放全部通过；证据为 `agent_transport/test_replay.py`、`results/REPLAY_TEST_RESULTS.json` 和两种REPLAY_TRACE。回放中model_calls=0、model_performance=N/A。上一轮36项测试及385×7启发式结果仅继承，没有重复当成本轮模型结果。

确认的宿主边界：逐步骤白名单、参数Schema、受限范围拒绝、真实事件前缀、工具调用计费、2次查询和证据预算、同call_id幂等、变化参数同ID拒绝、未见事件引用拒绝、Gold/shell/write/network工具拒绝。日志中的恶意指令只作为data封装，伪造tool消息会被完整性校验拒绝。

未验证：真实LLM面对恶意日志文本的服从/抗注入能力、长期多轮越权尝试。不能从宿主回放测试推导LLM鲁棒性。CONV-A01=NOT_AUTHORIZED；受限步骤正文没有读取、索引或上传。
