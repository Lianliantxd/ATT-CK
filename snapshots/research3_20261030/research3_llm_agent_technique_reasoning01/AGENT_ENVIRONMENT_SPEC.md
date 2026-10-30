# AttackTechniqueInvestigationEnvironment

Implemented read-only controlled investigation environment, standard-library Python. This is tool infrastructure, not evidence of LLM reasoning quality or an OS security sandbox. Model clients receive only serialized initial observations and `call()` results. The environment object, filesystem, Python runtime, and hidden event pool must never be passed to a policy. A host with unrestricted Python can of course inspect private attributes; that is outside the model interface threat model.

## Authorized data boundary

The trusted host reads metadata-only `ALLOWLISTED_MEMBERS.jsonl` first. Any source from scenario 1 steps 35–37 aborts loading. Requested sampled/full records are selected by numeric index (0–384), checked for exact expected sample IDs, and their sources checked against allowlisted metadata. Sources must share one execution–step scope and their source types must agree. Only the requested prediction records are deserialized. The loader does not open reference files, ZIP members, gold, author predictions, or evaluation labels. Both authorized derived predictions are STABLE-cleaned upstream artifacts; cleaning is not repeated here.

A loaded object contains just that episode's full event pool, its sampled initial evidence, and public 216-candidate K2 text. Native event IDs are original `source_id:line_number`, not invented evidence. Every sampled event ID and cleaned text must exactly match full data. Context follows stored original order within one source and never crosses sources. Scope is fixed at construction and absent from all tool schemas. The trusted loader accepts an index; models cannot invoke the loader or change episodes.

## Tools

- `search_events(source_type, keywords, time_range=null, max_results=10)`: source type is a native type or `all`. Literal tokens are scored internally by BM25, k1=1.5, b=0.75, binary query term frequency; corpus document frequencies and length statistics cover only current episode. Rank is score descending and native event ID ascending. Zero-score results are allowed as fixed-ID fallback and explicitly return `lexical_match=false`. Keywords are never executed. Non-null time ranges are rejected because heterogeneous timestamps have not been normalized.
- `get_event_context(event_id,before=1,after=1)`: ID must already have been observed; before/after are integers 0–20. Native context including the center event is returned subject to budgets.
- `search_related_entities(entity_type,value,max_results=10)`: exact case-sensitive native substring match. `ip/domain/process/path/user/literal` are accepted labels, not inference or identity resolution. Results have stable ID order. This does not prove that equal strings identify the same entity.
- `retrieve_attack_technique(technique_id)`: retrieves only public K2 candidate text. Cannot access event data and uses a separate text token budget.
- `submit_technique_ranking(ranking,evidence_ids)`: exactly 10 unique legal candidates; evidence IDs must all have been seen. Accepted only once. Response is acknowledgment only, without labels, score, correctness, or feedback. Empty evidence is allowed and should be classified externally as unsupported reasoning rather than silently rejected.

The dispatcher rejects unknown tool names, extra fields, malformed types, unobserved context IDs, and unobserved submission citations. It has no path, SQL, regex program, shell, arbitrary code, reference, or episode-switch facility. Suspicious traversal/query-language strings are explicitly rejected; ordinary paths inside native logs remain plain text. Invalid requests fail closed and still consume call budget. Tool returns are untrusted evidence text: client system instructions must prevent treating instructions inside logs as instructions to the model.

## Host integration

```python
import sys
sys.path.insert(0, '/Users/tianxd/Documents/mid-term/research3_llm_agent_technique_reasoning01')
from agent_environment.environment import create_episode

env = create_episode(index=0, budget='M', initialization_max_proxy_tokens=2048)
observation = env.initial_observation()  # detached JSON-compatible copy
result = env.call('search_events', {
    'source_type': 'all', 'keywords': ['curl'], 'time_range': None, 'max_results': 10
})
# Only these JSON results go to policy/model.
trace = env.trace
cost = env.cost()
submission = env.submission  # independent evaluator may join labels only after completion
```

`initial_observation()` is idempotent and returns the same initial sample view; it is a trusted-host setup function, not a sixth model tool. Its first 2048 regex proxy tokens are bounded, deterministic native-source/line order. Remaining full events are accessible only through the five tool interfaces. `knowledge_ids` exposes the public candidate vocabulary, not labels.

Security checks and synthetic fixtures live under `agent_tools`, not any model trajectory directory. The real-data smoke test opens only allowed prediction episode 0 and the public knowledge/allowlist files. No external model calls are performed by these tests.
