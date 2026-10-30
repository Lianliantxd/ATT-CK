# Controlled investigation budget protocol

| Budget | Shared read/query tool attempts | New unique native rows | Returned log text regex proxy tokens |
|---|---:|---:|---:|
| S | 2 | 20 | 2048 |
| M | 4 | 40 | 4096 |

All four read tools (`search_events`, context, entities, knowledge) share the call-attempt cap. Unknown/invalid calls and repeated calls also count. An over-cap call increments the attempted-call counter and returns an error without evidence. Successful final submission is separate from read-query cap; submission attempts are audited and only one successful submission is allowed. Calls after submission are rejected.

Initial sampled observation has a separate default 2048 proxy-token cap (host may set 0–8192) and is recorded in `initial_proxy_tokens/initial_rows`. Public K2 knowledge has an additional 4096 text proxy-token cap, separately recorded. It never shares the log text budget, but retrieval consumes a shared query call. Candidate IDs and tool envelopes are not included in these text-content counters. The model runner must additionally record its true tokenizer/API input/output usage or explicitly indicate that it is unavailable. Do not equate these counters to actual model tokens or wall-clock costs.

Proxy tokenizer is nonempty Unicode regex `\w+|[^\w\s]`; clipping retains complete matched units and intervening whitespace up to the last allowed match. This is explicitly `regex_proxy_NOT_MODEL_TOKENS`. It counts punctuation and Unicode word units, unlike whitespace-only counting, but is still not a pretrained model tokenizer.

Every returned text occurrence consumes returned-text budget, including repeated events and repeated text. `new_unique_rows` counts newly observed IDs only; `returned_rows` counts all tool-returned rows, `duplicate_rows` counts IDs returned before (including initial view), and `duplicate_text_rows` separately counts identical returned text strings. A clipped long row is marked `truncated=true` and its native ID becomes seen; a later context return consumes the token budget again. New rows cease at the unique-row limit; content ceases at the text-token limit. These hard limits are applied after deterministic search ranking, so repeated/long evidence can exhaust useful budget. Empty responses remain charged.

Trace entries preserve attempted tool arguments, accepted/rejected status, exact returned observations, and cumulative cost. Error messages contain no event bodies, gold, ranks, labels, or filesystem paths. Explicit time-range rejection prevents reporting fictitious timestamp filtering. Security fixtures must carry `SYNTHETIC_TOOL_TEST_NOT_MODEL_EXPERIMENT`; they are never model/Agent experiment trajectories.
