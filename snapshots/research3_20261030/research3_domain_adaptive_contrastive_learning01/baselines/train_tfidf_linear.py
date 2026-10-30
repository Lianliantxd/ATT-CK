"""Fixed-budget grouped multilabel TF-IDF logistic training; NumPy only.

Only train JSONL labels are opened. Heldout/validation input-only files are
predicted after fitting. Each epoch contributes one equal-weight view per step.
"""
from __future__ import annotations

import os
os.environ.update(OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', MKL_NUM_THREADS='2', VECLIB_MAXIMUM_THREADS='2', PYTHONDONTWRITEBYTECODE='1')
import csv
import hashlib
import json
import resource
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/runs_B2'
CHECKPOINTS = ROOT / 'checkpoints/B2'
EPOCHS = 120
SEEDS = (17, 42, 73)
MODES = ('ONE_VIEW_PER_STEP', 'MULTI_VIEW_AUGMENTATION')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def array_digest(*values: np.ndarray) -> str:
    h = hashlib.sha256()
    for value in values:
        h.update(np.ascontiguousarray(value).tobytes())
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def grams(text: str) -> Counter:
    text = text.lower()
    return Counter(text[i:i+n] for n in (3, 4, 5) for i in range(len(text)-n+1))


def fit_vectorizer(rows: list[dict]) -> tuple[list[str], np.ndarray]:
    df: Counter = Counter()
    for row in rows:
        df.update(grams(row['input_log_text']).keys())
    vocab = sorted((gram for gram, count in df.items() if count >= 2), key=lambda gram: (-df[gram], gram))[:2048]
    idf = np.asarray([np.log((1+len(rows))/(1+df[gram])) + 1 for gram in vocab], dtype=np.float32)
    assert vocab and np.isfinite(idf).all()
    return vocab, idf


def transform(rows: list[dict], vocab: list[str], idf: np.ndarray) -> np.ndarray:
    lookup = {gram: i for i, gram in enumerate(vocab)}
    matrix = np.zeros((len(rows), len(vocab)), dtype=np.float32)
    for i, row in enumerate(rows):
        for gram, count in grams(row['input_log_text']).items():
            j = lookup.get(gram)
            if j is not None:
                matrix[i, j] = (1 + np.log(count)) * idf[j]
    matrix /= np.maximum(np.linalg.norm(matrix, axis=1, keepdims=True), 1e-12)
    return matrix


def ranking(scores: np.ndarray, candidates: list[str]) -> list[int]:
    return sorted(range(len(candidates)), key=lambda j: (-float(scores[j]), candidates[j]))


def train_one(fold: dict, seed: int, mode: str, candidates: list[str], canonical: list[dict], all_train: list[dict], vocab: list[str], idf: np.ndarray, features: np.ndarray, eval_rows: list[dict], eval_features: np.ndarray) -> dict:
    tag = f"{fold['fold_id']}__seed{seed}__{mode}"
    receipt_path = OUT / f'{tag}_receipt.json'
    assert not receipt_path.exists(), 'Refuse silent rerun/overwrite of completed configuration'
    started = time.perf_counter()
    cpu_started = time.process_time()
    seen = sorted({label for row in canonical for label in row['gold_technique_ids']})
    assert set(seen) <= set(candidates)
    labels = np.asarray([[float(label in row['gold_technique_ids']) for label in seen] for row in canonical], dtype=np.float32)
    positive_weight = (len(canonical) - labels.sum(axis=0)) / labels.sum(axis=0)
    assert np.all(positive_weight >= 0)
    by_step: dict[str, dict[int, int]] = defaultdict(dict)
    for i, row in enumerate(all_train):
        by_step[row['logical_step_id']][int(row['sampling_replica_id'])] = i
    assert all(set(by_step[row['logical_step_id']]) == set(range(5)) for row in canonical)
    rng = np.random.default_rng(seed)
    weight = rng.normal(0, .001, (len(vocab), len(seen))).astype(np.float32)
    bias = np.zeros(len(seen), dtype=np.float32)
    initial_weight, initial_bias = weight.copy(), bias.copy()
    initial_hash = array_digest(weight, bias)
    wm = np.zeros_like(weight); wv = np.zeros_like(weight)
    bm = np.zeros_like(bias); bv = np.zeros_like(bias)
    history = []
    train_ids_used: set[str] = set()
    for epoch in range(EPOCHS):
        replica = 0 if mode == 'ONE_VIEW_PER_STEP' else (epoch + seed) % 5
        indices = [by_step[row['logical_step_id']][replica] for row in canonical]
        train_ids_used.update(all_train[i]['sample_id'] for i in indices)
        x = features[indices]
        logits = x @ weight + bias
        probability = 1 / (1 + np.exp(-np.clip(logits, -50, 50)))
        per_element = labels * positive_weight * np.logaddexp(0, -logits) + (1-labels) * np.logaddexp(0, logits)
        loss = float(per_element.mean() + .0005 * np.square(weight).sum())
        delta = ((1-labels)*probability + positive_weight*labels*(probability-1)) / labels.size
        gw = x.T @ delta + .001 * weight
        gb = delta.sum(axis=0)
        assert np.isfinite(loss) and np.isfinite(gw).all() and np.isfinite(gb).all(), 'Nonfinite training loss/gradient'
        t = epoch + 1
        for parameter, gradient, momentum, velocity in ((weight, gw, wm, wv), (bias, gb, bm, bv)):
            momentum *= .9; momentum += .1 * gradient
            velocity *= .999; velocity += .001 * np.square(gradient)
            parameter -= .03 * (momentum/(1-.9**t)) / (np.sqrt(velocity/(1-.999**t)) + 1e-8)
        if epoch == 0 or t % 10 == 0:
            history.append({'epoch': t, 'loss_before_update': loss, 'gradient_l2': float(np.sqrt(np.square(gw).sum()+np.square(gb).sum())), 'replica': replica, 'wall_seconds': time.perf_counter()-started})
    final_hash = array_digest(weight, bias)
    assert final_hash != initial_hash and not np.array_equal(weight, initial_weight)
    checkpoint = CHECKPOINTS / f'{tag}.npz'
    np.savez_compressed(checkpoint, W=weight, b=bias, initial_W=initial_weight, initial_b=initial_bias, vocab=np.asarray(vocab), idf=idf, labels=np.asarray(seen), candidate_ids=np.asarray(candidates), positive_weight=positive_weight)
    logits_original = eval_features @ weight + bias
    with np.load(checkpoint, allow_pickle=False) as saved:
        restored_x = transform(eval_rows, saved['vocab'].tolist(), saved['idf'])
        restored_logits = restored_x @ saved['W'] + saved['b']
    reload_diff = float(np.max(np.abs(logits_original-restored_logits)))
    assert reload_diff == 0
    inference_start = time.perf_counter()
    full_scores = np.full((len(eval_rows), len(candidates)), -1e6, dtype=np.float32)
    columns = [candidates.index(label) for label in seen]
    full_scores[:, columns] = eval_features @ weight + bias
    prediction_path = OUT / f'{tag}_predictions.jsonl'
    with prediction_path.open('w') as handle:
        for row, scores in zip(eval_rows, full_scores):
            order = ranking(scores, candidates)
            record = {'method': 'B2', 'seed': seed, 'augmentation': mode, 'fold_id': fold['fold_id'], 'evaluation_partition': row['_partition'], 'sample_id': row['sample_id'], 'predictions': [candidates[i] for i in order[:10]], 'ranking_all216': [candidates[i] for i in order], 'scores_top10': [float(scores[i]) for i in order[:10]], 'checkpoint_path': str(checkpoint.relative_to(ROOT))}
            handle.write(json.dumps(record) + '\n')
    inference_seconds = time.perf_counter()-inference_start
    receipt = {'method': 'B2', 'status': 'ACTUALLY_TRAINED_AND_RELOADED', 'fold_id': fold['fold_id'], 'seed': seed, 'augmentation': mode, 'train_sample_ids': sorted(train_ids_used), 'train_step_count': len(canonical), 'training_available_replica_count': len(all_train), 'seen_labels': seen, 'candidate_count': len(candidates), 'unseen_score': -1e6, 'epochs': EPOCHS, 'optimizer_updates': EPOCHS, 'trainable_parameters': int(weight.size+bias.size), 'W_changed': True, 'parameters_changed': True, 'initial_parameter_sha256': initial_hash, 'final_parameter_sha256': final_hash, 'parameter_l2_change': float(np.sqrt(np.square(weight-initial_weight).sum()+np.square(bias-initial_bias).sum())), 'reload_max_abs_diff': reload_diff, 'loss_gradient_all_finite': True, 'training_tokens': 'N/A_NO_NLP_TOKENIZER', 'cpu_seconds': time.process_time()-cpu_started, 'wall_seconds': time.perf_counter()-started, 'peak_process_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'checkpoint_path': str(checkpoint.relative_to(ROOT)), 'checkpoint_bytes': checkpoint.stat().st_size, 'checkpoint_sha256': digest(checkpoint), 'inference_seconds': inference_seconds, 'inference_queries': len(eval_rows), 'inference_latency_seconds_per_query': inference_seconds/len(eval_rows), 'validation_or_heldout_reference_opened': False, 'vectorizer_fit_rows': len(canonical), 'vectorizer_fit_unit': 'ONE_R0_VIEW_PER_TRAIN_STEP_SAME_FOR_BOTH_MODES', 'vocabulary_size': len(vocab), 'vectorizer_sha256': array_digest(np.asarray(vocab), idf), 'source_sha256': digest(Path(__file__)), 'loss_formula': 'mean[y*pos_weight*softplus(-logit)+(1-y)*softplus(logit)] + .001/2 * sum(W**2); pos_weight=(N-positive_count)/positive_count; only train-seen classes', 'optimizer': {'name': 'Adam', 'lr': .03, 'beta1': .9, 'beta2': .999, 'epsilon': 1e-8, 'L2_W': .001, 'bias_regularization': 0}, 'training_logs': history}
    write_json(receipt_path, receipt)
    with (OUT/f'{tag}_training_logs.csv').open('w') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(history[0])); writer.writeheader(); writer.writerows(history)
    print(json.dumps({'completed': tag, 'seconds': round(receipt['wall_seconds'], 3), 'loss_initial': history[0]['loss_before_update'], 'loss_final': history[-1]['loss_before_update'], 'reload_diff': reload_diff}), flush=True)
    return receipt


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True); CHECKPOINTS.mkdir(parents=True, exist_ok=True)
    split_path = ROOT/'GROUPED_TRAIN_VALIDATION_SPLITS.json'
    splits = json.loads(split_path.read_text())
    candidates = sorted(json.loads((ROOT/'data/CANDIDATE_TECHNIQUE_IDS.json').read_text()))
    assert len(candidates) == len(set(candidates)) == 216
    completed = []
    for fold in splits['folds']:
        canonical = read_jsonl(ROOT/fold['one_view_train_path'])
        all_train = read_jsonl(ROOT/fold['paths']['train'])
        assert len({row['logical_step_id'] for row in canonical}) == len(canonical)
        assert all(int(row['sampling_replica_id']) == 0 for row in canonical)
        vocab, idf = fit_vectorizer(canonical)
        features = transform(all_train, vocab, idf)
        eval_rows = []
        for partition in ('heldout', 'validation'):
            rows = read_jsonl(ROOT/fold['paths'][partition+'_inputs'])
            assert all('gold_technique_ids' not in row for row in rows)
            for row in rows: row['_partition'] = partition
            eval_rows.extend(rows)
        eval_features = transform(eval_rows, vocab, idf)
        assert not ({r['sample_id'] for r in all_train} & {r['sample_id'] for r in eval_rows})
        for seed in SEEDS:
            for mode in MODES:
                tag = f"{fold['fold_id']}__seed{seed}__{mode}"
                try:
                    completed.append(train_one(fold, seed, mode, candidates, canonical, all_train, vocab, idf, features, eval_rows, eval_features))
                except Exception as error:
                    write_json(OUT/f'{tag}_FAILURE.json', {'configuration': tag, 'error': type(error).__name__+': '+str(error), 'source_sha256': digest(Path(__file__)), 'automatic_parameter_changes': False})
                    raise
    write_json(OUT/'B2_COMPLETION.json', {'status': 'ALL_42_CONFIGURATIONS_TRAINED', 'configurations': len(completed), 'split_sha256': digest(split_path), 'source_sha256': digest(Path(__file__)), 'receipt_paths': [str((OUT/f"{r['fold_id']}__seed{r['seed']}__{r['augmentation']}_receipt.json").relative_to(ROOT)) for r in completed]})


if __name__ == '__main__':
    main()
