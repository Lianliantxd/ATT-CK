# Local CPU pilot independent code audit

Audit date: 2026-10-27. Scope: read-only source review of `llm/run_local_pilot.py`, `llm/local_ollama.py`, and `agent_environment/environment.py`. No reference/Gold read, no research predictions inspected, no model calls made. This is a software protocol audit, not an assessment of experiment accuracy.

## P1: retrieved ATT&CK knowledge is discarded

`merged()` only copies `record.result.events`. The knowledge tool returns `{technique_id,text,...}`, so its result is absent from merged observations. `action_prompt()` retains only prior tool/arguments/status, and `final_prompt()` renders only logs plus the initial fixed top-20 knowledge. Consequently, dynamically retrieved technique definitions reach neither the next action nor final inference. This is a real information-flow defect: the model spends a query/knowledge budget without observing that result. Existing trajectories remain real model calls, but cannot establish the performance of the intended complete knowledge-retrieval Agent. Mark affected protocol version explicitly; do not silently mix reruns after a patch with prior cases.

## P1: global budget RuntimeError can omit the current condition

`guarded_generate()` raises RuntimeError on call/time cap. CPU-only verification also raises RuntimeError. The per-condition except clause handles ValueError/KeyError/TypeError/TimeoutError/OSError, not RuntimeError. Such termination exits before the current failure row, progress update, and final summary. Preserve partial native responses and distinguish completed conditions, attempted-but-unfinished conditions, and never-started registered conditions. A planned 14-by-mode matrix must not be reported as completed. Runtime/device failures should stop further model calls while still saving a terminal status and cost ledger.

## P1: failed attempted calls are underrepresented in row costs

The global CALLS counter increments before inference; `row.model_calls` is only len(models), which counts returned receipts appended by the caller. A timeout therefore counts globally but contributes no row attempt/time record. More subtly, if the API returns successfully but `guarded_generate()` detects context overflow, it raises before `models.append(receipt)`: native prompt/output/cost exists on disk but row sums omit it. Similarly device verification may fail after a response is saved. Reconcile the attempt ledger against all native receipts; report unknown output tokens as unknown rather than zero, and retain elapsed time for failed calls. Do not call successful-receipt counts total inference attempts.

## P2: action feedback omits structured result status information

Events are merged, but rejection reasons (`result.error`) and `lexical_match` are not sent back. A zero-match BM25 request still returns stable top event IDs from the pool; without the false lexical-match flag, the Agent cannot directly distinguish matched retrieval from fallback tie results. The resulting policy is still executable but should be described accurately, and rejected-call reasons should be exposed in subsequent tool observations.

## P2: acquired evidence differs from model-visible evidence

`render()` traverses initial then acquired events under a global 5000 UTF-8-byte cap. Some returned rows can be omitted or clipped before model inference. `merged()` can replace an initially clipped event with a longer returned row, increasing its early prefix and crowding out later evidence. Saving `rendered_event_ids` helps, but returned-log tokens/rows alone do not establish model access to those rows or their complete text. Compare static/adaptive effects using actual prompt text and visible event spans; equal acquisition caps do not imply equal visible evidence. The current byte cap also differs from regex budget and actual tokenizer count, which must remain separately labeled.

## P2: wall budget is a pre-call guard, not a hard deadline

A call may start just before 3600 seconds and run to its 180-second timeout, so 3600 seconds is a stop-launching threshold rather than a hard wall-time cap. Report actual runtime and avoid asserting strict completion inside the threshold. No additional inference is needed to establish this source-level fact.

## Confirmed safeguards

The updated local client disables proxies and redirects, fixes 127.0.0.1:11434, verifies response host/port, requests num_gpu=0/two CPU threads, and rejects a missing or nonzero size_vram. Model digest is checked on startup; device digest is checked when present. The policy exposes only closed JSON investigation tools, not a shell/filesystem/network action. Prediction parsing enforces ten unique candidate IDs and rendered evidence IDs; duplicate/invalid ranking failures become empty predictions in the current condition's denominator for handled exceptions. These source observations do not replace the environment security tests.

## Recommended disposition

Keep native receipts and partial pilot outputs. Label the existing frozen protocol with the knowledge-result omission. Repair information flow in a new explicit protocol revision before claiming complete Agent comparisons; include returned knowledge in action/final contexts under a fixed shared knowledge budget and allow the same knowledge access for appropriate static controls. Fix terminal bookkeeping and reconcile failed-call costs before presenting cost-benefit conclusions. This audit does not propose selecting episodes, model prompts, or outcomes based on Gold.

Audited source SHA256: `ee2873c4af4cbf6924bb4b7b8e33ab59e86beecfa5d033f9c839db2179ac5e5b`. Source anchors: {'def merged': 35, 'def guarded_generate': 46, 'def final_prompt': 54, 'def action_prompt': 64, 'except (ValueError': 110, 'models.append(receipt)': 99, 'def run': 82}.
