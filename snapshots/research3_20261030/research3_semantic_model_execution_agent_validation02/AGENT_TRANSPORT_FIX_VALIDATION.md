# 修复验证

`results/REPLAY_TEST_RESULTS.json`：22/22通过，0次模型调用，类别REPLAY_TOOL_TEST。覆盖知识全文、错误及无匹配反馈、超长消息拒绝、call_id关联和幂等、预算、跨步骤访问拒绝、Gold/shell/write/network拒绝、伪造工具消息拒绝及原生日志前缀一致性。

`AGENT_VALID_EPISODES.jsonl` 保存另行完成的真实固定模型Episode。每条记录由原生请求/响应及device回执、完整消息哈希、call_id、实际返回事件、合法Top10提交和独立评价回执共同验证。`results/BACKEND_CONTEXT_FEEDBACK_PROOF.json` 逐条重建GGUF tokenizer的完整输入正文，并与后端响应context token前缀核对；最终数量以该文件及NEW_LLM_SUMMARY.json为准。

这是模型确实接收并引用返回证据的结构性证明。内部是否对该证据形成了正确机制推理、是否因果改变排序，仍需删除/替换证据等干预；本轮没有相应充分证据。
