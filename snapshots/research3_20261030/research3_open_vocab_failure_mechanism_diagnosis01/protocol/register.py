"""Record the received, truncated request and diagnostic-only arithmetic scope."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=Path('/Users/tianxd/.codex/attachments/a57d2c6c-7146-45ba-a092-6d51c5578ef3/已粘贴的文本.txt')
shutil.copyfile(p,R/'inherited/USER_REQUEST_LATEST.txt')
q={'task':'R3_OPEN_VOCAB_FAILURE_MECHANISM_DIAGNOSIS01','created_utc':datetime.now(timezone.utc).isoformat(),'request_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'request_complete':False,'request_ends_at':'section6.1 / lone bullet dash','available_scope':'all received sections1-5 plus frozen-GTE-miss diagnosis described in section6 heading; no claim to unseen remainder','primary_view':'ONE_VIEW_PER_STEP','supplementary_view':'MULTI_VIEW_AUGMENTATION','seeds':[17,42,73],'candidate_count':216,'new_model_calls':0,'new_training_updates':0,'new_parameter_search':0,'server_access':False,'old_assets':'READ_ONLY','tie_rule':'stable descending score, candidate ID ascending','units':['query','query_gold_technique_pair','unique logical step','seed/view config'],'known_counts_are_hypotheses_not_targets':[450,66,384,34,32,0],
 'counterfactuals':{'REMOVE_SEEN_SUPERVISION':'registered zGTE - gamma*seen','REMOVE_SEEN_BIAS':'registered zGTE + lambda*seen*zB3','RESTORE_GTE':'saved raw GTE score; positive-affine normalized rank checked'},
 'component_arithmetic':'retain registered train normalization and selected lambda/gamma; never fit or choose weights',
 'rank_identity':'rank_all216(g)=1+n_unseen_before(g)+n_seen_before(g); within-unseen order invariant for C4; diagnostic counts only, never evaluate filtered-candidate predictions',
 'loss_attribution':'primary SEEN_SCORE_BOOST only when actual lost target restored by removing supervision, relevant seen crossings positive boost; bias/ties/numeric scales reported separately; SCORE_SCALE_MISMATCH not inferred just from different score units; all unsupported semantic causes UNRESOLVED',
 'failure_priority':'quantify exact cross-category rank competition vs within-unseen rank>10 obstruction; inspect frozen view/description limits, cannot assert mechanism absence from Gold alone',
 'statistics':'descriptive, no pvalues or IID CI for five correlated replicas/three reused seeds/seven exposed scenarios; no ranking metric redefinition','evidence_cards':'all primary seed17 ONE GTE-miss queries, lexical order; existing sanitized input and frozen candidate descriptions only, no raw archive or restricted steps','disk_guard_bytes':2000000000}
out=R/'DIAGNOSTIC_PROTOCOL.json';assert not out.exists();out.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
(R/'protocol/PROTOCOL_SHA256.txt').write_text(hashlib.sha256(out.read_bytes()).hexdigest()+'\n')
print('DIAGNOSTIC_SCOPE_RECORDED')
