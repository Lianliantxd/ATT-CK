# Deterministic investigation tool controls

Qualification: **DETERMINISTIC_POLICY_CONTROL_NOT_LLM_AGENT**. No pretrained model, LLM calls, or learned Agent is used. These are resource-ceiling controls, not evidence of LLM reasoning. All predictions were closed on disk before the reference file was opened for evaluation. The developer inspected reference episode 0 schema (including its label) before implementation. A frozen-policy three-episode smoke run was evaluated before the full run; its separate evaluator loaded the complete reference map and joined only those three saved predictions. No policy or vocabulary changes followed that smoke evaluation; only host cloning optimization and reporting fields changed. These exposures are disclosed; fixed generic vocabulary was supplied by the parent task.

All conditions start with the same native sampled view capped at 256 Unicode regex word/punctuation proxy tokens. Final ranking is the frozen K2 CharacterNgramTFIDF implementation. Only initial/tool-returned evidence is concatenated, deduplicated by native event ID (longest observed text retained). Final top-10 and evidence IDs pass the actual submit tool.

NO_EXTRA performs no query. STATIC_BM25 uses initial native word frequency top 32 once, with 20/40 result limits. FIXED_SOURCE uses predeclared audit execve/exe/proctitle, then all failed/download/connection/permission, then all process/command/network/user, then all login/file/service/port. Missing audit source falls back to all. ADAPTIVE_HEURISTIC uses unqueried currently observed native tokens; if fewer than eight are available, public words distinguishing current top-2 K2 descriptions supplement them. After the first query it targets the least represented available native source. These deterministic decisions access no private event pool.

| Condition | Query Top-1 | Query Top-10 | MRR | Step-macro Top-10 | Mean new rows | Mean calls |
|---|---:|---:|---:|---:|---:|---:|
| NO_EXTRA | 0.0701 | 0.2857 | 0.1196 | 0.2582 | 0.00 | 0.00 |
| STATIC_BM25_S | 0.1013 | 0.3143 | 0.1474 | 0.2863 | 10.70 | 1.00 |
| STATIC_BM25_M | 0.0883 | 0.3221 | 0.1433 | 0.2987 | 19.49 | 1.00 |
| FIXED_SOURCE_S | 0.0987 | 0.3117 | 0.1475 | 0.2798 | 12.16 | 2.00 |
| FIXED_SOURCE_M | 0.0987 | 0.3091 | 0.1464 | 0.2733 | 15.49 | 4.00 |
| ADAPTIVE_HEURISTIC_S | 0.0883 | 0.2961 | 0.1385 | 0.2644 | 8.84 | 2.00 |
| ADAPTIVE_HEURISTIC_M | 0.0961 | 0.3195 | 0.1459 | 0.2994 | 12.99 | 4.00 |

The 385 execution–step records are repeated variants of fewer logical steps; report both query and logical-step macro metrics. This is a CAM-LDS-v2 within-source control, not independent external generalization. Resource budgets are maxima: STATIC_BM25 deliberately spends just one query; row/token exhaustion and genuinely small full pools can yield fewer additional rows. Proxy counts exclude JSON envelopes and are not actual model tokenizer counts. Runtime excludes shared index initialization, includes tool/final scoring but excludes shared host episode initialization and cloning (separately recorded), and is not comparable to API latency. No claim of superiority or significance is justified by these point metrics alone.

Artifact audit verified every trajectory: common identical initial evidence per episode, seen-only citations, exact final-submission equality, and exact independent regex token/new-row/call recount under hard budgets.

Artifacts: predictions in experiments/deterministic_controls_predictions.jsonl; exact controlled observations and tool trace in agent_trajectories/DETERMINISTIC_CONTROLS.jsonl; frozen V1 query and logical-step macro results in results/DETERMINISTIC_CONTROL_METRICS.json.
