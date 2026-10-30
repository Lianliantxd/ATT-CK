# Controlled tool security checks

Classification: **SYNTHETIC_TOOL_TEST_NOT_MODEL_EXPERIMENT**.

Executed 26 checks; failures=0, errors=0. These checks establish interface behavior, not reasoning quality or complete security proof. One real episode loader smoke check is included; the other checks use synthetic native-row fixtures.

- test_arbitrary_episode_index_rejected
- test_bm25_zero_match_declared
- test_budget_invalid_calls_count
- test_context_native_order
- test_cross_episode_id
- test_evidence_unseen
- test_initial_is_copy
- test_invalid_candidate
- test_knowledge_counts_query_calls
- test_literal_no_regex_execution
- test_new_row_limit
- test_path_traversal
- test_public_knowledge_separate_budget
- test_ranking_duplicate
- test_ranking_length
- test_real_native_evidence
- test_repeated_query_counts
- test_sql_literal_rejected
- test_submit_once_no_gold_feedback
- test_time_range_explicit_rejection
- test_token_limit_truncates
- test_unknown_context_id
- test_unknown_field_gold
- test_unknown_source
- test_unknown_tool
- test_unseen_context_id

Run: `python3 agent_tools/test_security.py` from the new project root. Machine-readable results: `results/tool_security_tests.json`; verbose runner log: `results/tool_security_tests.log`. No gold/reference reads, model calls, or AGENT_TRAJECTORIES output occur in this test suite.
