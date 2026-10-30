"""Independent, full-candidate generalized-zero-shot evaluation of saved ranks.

No training, score construction, calibration, network, or model calls.  Only this
post-prediction module reads outer-heldout references.  All summaries preserve
the 216-candidate prediction and restrict Gold only for target-stratum metrics.
"""
import csv
import hashlib
import importlib.util
import json
import math
import os
import resource
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path

for _name in ['OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS']:
    os.environ[_name] = '2'
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parent / 'research3_domain_adaptive_contrastive_learning01'
BENCH = ROOT.parent / 'research3_attack_technique_benchmark01'
METHODS = ['Z0', 'S0', 'C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'P2', 'C6_B4', 'C6_B5']
VIEWS = ['ONE_VIEW_PER_STEP', 'MULTI_VIEW_AUGMENTATION']
SEEDS = ['17', '42', '73']
STRATA = ['ALL', 'SEEN_TARGET', 'UNSEEN_TARGET', 'ALL_SEEN', 'ALL_UNSEEN', 'MIXED',
          'SINGLE_LABEL', 'MULTILABEL', 'SUPPORT_0', 'SUPPORT_1', 'SUPPORT_2_4', 'SUPPORT_GE5']
METRICS = ['mrr', 'top1_accuracy', 'top5_accuracy', 'top10_accuracy',
           'precision_at_1', 'precision_at_5', 'precision_at_10',
           'recall_at_1', 'recall_at_5', 'recall_at_10', 'micro_f1_at_5',
           'macro_f1_at_5_all_candidates', 'macro_f1_at_5_gold_present']
NA = 'NA'
REGISTRATION_SHA256 = 'cceb35fc46eaeb5cc4db5973e315ab0a7288cbac5a1d0d1722031944a42289e3'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def jl(path):
    with path.open() as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def readcsv(path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


def csvout(name, rows):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError('Refuse empty result table: ' + name)
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def numeric(value):
    return isinstance(value, (int, float)) and math.isfinite(value)


def mean(values):
    good = [x for x in values if numeric(x)]
    return statistics.mean(good) if good else NA


def harmonic(a, b):
    if not numeric(a) or not numeric(b):
        return NA
    return 2 * a * b / (a + b) if a + b else 0.0


def bucket(count):
    return 'SUPPORT_0' if count == 0 else 'SUPPORT_1' if count == 1 else 'SUPPORT_2_4' if count <= 4 else 'SUPPORT_GE5'


class Metrics:
    """Standard-library independent implementation, including classwise F1."""
    def __init__(self, ids):
        self.ids = ids
        self.n = 0
        self.sums = Counter()
        self.tp, self.fp, self.fn = Counter(), Counter(), Counter()
        self.gold_classes, self.steps, self.target_step_pairs = set(), set(), set()

    def add(self, rank, gold, step):
        check(bool(gold), 'No empty target enters an accumulator')
        self.n += 1
        self.steps.add(step)
        self.gold_classes.update(gold)
        self.target_step_pairs.update((step, t) for t in gold)
        rr = [i + 1 for i, t in enumerate(rank[:10]) if t in gold]
        self.sums['mrr'] += 1 / min(rr) if rr else 0
        for k in [1, 5, 10]:
            hits = len(set(rank[:k]) & gold)
            self.sums[f'top{k}_accuracy'] += int(hits > 0)
            self.sums[f'precision_at_{k}'] += hits / k
            self.sums[f'recall_at_{k}'] += hits / len(gold)
        selected = set(rank[:5])
        self.tp.update(selected & gold)
        self.fp.update(selected - gold)
        self.fn.update(gold - selected)

    def merge(self, other):
        self.n += other.n
        self.sums.update(other.sums)
        self.tp.update(other.tp)
        self.fp.update(other.fp)
        self.fn.update(other.fn)
        self.steps.update(other.steps)
        self.gold_classes.update(other.gold_classes)
        self.target_step_pairs.update(other.target_step_pairs)
        return self

    def result(self):
        out = {'n_records': self.n, 'logical_steps': len(self.steps),
               'target_technique_count': len(self.gold_classes), 'target_step_technique_pairs': len(self.target_step_pairs)}
        if not self.n:
            return {**out, **{m: NA for m in METRICS}}
        out.update({m: self.sums[m] / self.n for m in METRICS[:10]})
        def f1(t):
            den = 2 * self.tp[t] + self.fp[t] + self.fn[t]
            return 2 * self.tp[t] / den if den else 0.0
        den = 2 * sum(self.tp.values()) + sum(self.fp.values()) + sum(self.fn.values())
        out['micro_f1_at_5'] = 2 * sum(self.tp.values()) / den if den else 0.0
        out['macro_f1_at_5_all_candidates'] = sum(f1(t) for t in self.ids) / len(self.ids)
        out['macro_f1_at_5_gold_present'] = sum(f1(t) for t in self.gold_classes) / len(self.gold_classes)
        return out


class Group:
    def __init__(self, ids):
        self.ids = ids
        self.metrics = {s: Metrics(ids) for s in STRATA}
        self.bias = Counter()
        self.samples, self.full_gold_refs = set(), []
        self.class_n, self.class_mrr, self.class_hit = Counter(), Counter(), Counter()
        self.class_steps = defaultdict(set)

    def add(self, row, ref, seen, support):
        sid, step = row['sample_id'], ref['logical_step_id']
        check(sid not in self.samples, 'Duplicate sample in condition ' + sid)
        self.samples.add(sid)
        rank = row['ranking_all216']
        gold = set(ref['gold_technique_ids'])
        sg, ug = gold & seen, gold - seen
        subsets = [('ALL', gold), ('SINGLE_LABEL' if len(gold) == 1 else 'MULTILABEL', gold),
                   ('ALL_SEEN' if not ug else 'ALL_UNSEEN' if not sg else 'MIXED', gold)]
        if sg:
            subsets.append(('SEEN_TARGET', sg))
        if ug:
            subsets.append(('UNSEEN_TARGET', ug))
        for b in STRATA[8:]:
            target = {t for t in gold if bucket(support[t]) == b}
            if target:
                subsets.append((b, target))
        for stratum, target in subsets:
            self.metrics[stratum].add(rank, target, step)
        top10 = set(rank[:10])
        self.bias['top1_seen'] += int(rank[0] in seen)
        self.bias['top10_seen_count'] += len(top10 & seen)
        if sg and ug:
            self.bias['mixed_n'] += 1
            self.bias['mixed_any_hit'] += int(bool(top10 & gold))
            self.bias['mixed_seen_hit'] += int(bool(top10 & sg))
            self.bias['mixed_unseen_hit'] += int(bool(top10 & ug))
            self.bias['mixed_both_hit'] += int(bool(top10 & sg) and bool(top10 & ug))
            self.bias['mixed_seen_recall'] += len(top10 & sg) / len(sg)
            self.bias['mixed_unseen_recall'] += len(top10 & ug) / len(ug)
        positions = {t: i + 1 for i, t in enumerate(rank)}
        for t in gold:
            self.class_n[t] += 1
            self.class_steps[t].add(step)
            self.class_mrr[t] += 1 / positions[t] if positions[t] <= 10 else 0
            self.class_hit[t] += int(positions[t] <= 10)
        self.full_gold_refs.append({'sample_id': sid, 'ground_truth': sorted(gold), 'predictions': rank[:10]})

    def merge(self, other):
        check(not self.samples & other.samples, 'Merged scenes duplicate samples')
        self.samples.update(other.samples)
        for s in STRATA:
            self.metrics[s].merge(other.metrics[s])
        self.bias.update(other.bias)
        self.class_n.update(other.class_n)
        self.class_mrr.update(other.class_mrr)
        self.class_hit.update(other.class_hit)
        for t, steps in other.class_steps.items():
            self.class_steps[t].update(steps)
        return self

    def result(self):
        out = self.metrics['ALL'].result()
        n = out['n_records']
        for s, prefix in [('SEEN_TARGET', 'seen_target'), ('UNSEEN_TARGET', 'unseen_target')]:
            m = self.metrics[s].result()
            out[prefix + '_queries'] = m['n_records']
            out[prefix + '_mrr'] = m['mrr']
            out[prefix + '_top10'] = m['top10_accuracy']
            out[prefix + '_recall10'] = m['recall_at_10']
        for name, metric in [('H_MRR', 'mrr'), ('H_Top10', 'top10'), ('H_Recall10', 'recall10')]:
            out[name] = harmonic(out['seen_target_' + metric], out['unseen_target_' + metric])
        out['top1_seen_rate'] = self.bias['top1_seen'] / n if n else NA
        out['top10_seen_count_mean'] = self.bias['top10_seen_count'] / n if n else NA
        mn = self.bias['mixed_n']
        out['mixed_queries'] = mn
        for name in ['any_hit', 'seen_hit', 'unseen_hit', 'both_hit', 'seen_recall', 'unseen_recall']:
            out['mixed_' + name + '10'] = self.bias['mixed_' + name] / mn if mn else NA
        return out


def setup():
    check(sha(ROOT / 'FUSION_PARAMETER_REGISTRATION.json') == REGISTRATION_SHA256, 'Pre-result registration changed')
    ids = sorted(json.loads((OLD / 'data/CANDIDATE_TECHNIQUE_IDS.json').read_text()))
    check(len(ids) == len(set(ids)) == 216, 'Candidate universe must contain 216 parents')
    folds = {f['fold_id']: f for f in json.loads((OLD / 'GROUPED_TRAIN_VALIDATION_SPLITS.json').read_text())['folds']}
    refs, foldrefs = {}, {}
    for fid, fold in folds.items():
        rr = {r['sample_id']: r for r in jl(OLD / fold['paths']['heldout_reference'])}
        check(set(rr) == set(fold['heldout_sample_ids']), 'Heldout reference IDs changed')
        check(not set(refs) & set(rr), 'Heldout query assigned to more than one fold')
        refs.update(rr)
        foldrefs[fid] = rr
    check(len(refs) == 975 and len({r['logical_step_id'] for r in refs.values()}) == 195, 'Reference counts')
    spec = importlib.util.spec_from_file_location('prior_frozen_evaluator_readonly', BENCH / 'evaluate_techniques.py')
    frozen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(frozen)
    return ids, folds, refs, foldrefs, frozen


def seedmean(rows, dimensions):
    grouped = defaultdict(list)
    for row in rows:
        grouped[tuple(row[k] for k in dimensions)].append(row)
    out = []
    excluded = set(dimensions) | {'seed', 'aggregation'}
    for k, rr in sorted(grouped.items()):
        result = dict(zip(dimensions, k))
        result.update(aggregation='THREE_SEED_MEAN', seeds=len(rr),
                      uncertainty='seed_SD_is_training_or_calibration_variability_not_independent_attacks')
        for field in list(dict.fromkeys(f for r in rr for f in r)):
            if field in excluded:
                continue
            vv = [r.get(field, NA) for r in rr]
            nums = [x for x in vv if numeric(x)]
            if nums:
                result[field] = statistics.mean(nums)
                result[field + '_seed_SD'] = statistics.stdev(nums) if len(nums) > 1 else NA
                if len(nums) != len(rr):
                    result[field + '_defined_seeds'] = len(nums)
            elif all(x == NA for x in vv):
                result[field] = NA
            elif len(set(map(str, vv))) == 1:
                result[field] = vv[0]
        out.append(result)
    return out


def summarize(groups, ids, folds, methodlist):
    scenes, byseed, stratum_scenes, stratum_seeds, classrows = [], [], [], [], []
    aggregates = {}
    for (method, seed, view, fid), group in sorted(groups.items()):
        base = {'method': method, 'seed': seed, 'view_id': view, 'fold_id': fid,
                'scenario': folds[fid]['heldout_scenario'], 'aggregation': 'SCENE'}
        scenes.append({**base, **group.result()})
        for stratum in STRATA[1:]:
            stratum_scenes.append({**base, 'stratum': stratum, **group.metrics[stratum].result()})
    for method in methodlist:
        for seed in SEEDS:
            for view in VIEWS:
                sub = [(fid, groups[method, seed, view, fid]) for fid in folds]
                merged = Group(ids)
                for fid, group in sub:
                    merged.merge(group)
                check(len(merged.samples) == 975, 'Every method/seed/view must cover all975 heldout queries')
                aggregates[method, seed, view] = merged
                base = {'method': method, 'seed': seed, 'view_id': view, 'aggregation': 'QUERY_WEIGHTED', 'outer_folds': 7}
                result = merged.result()
                sr = [g.result() for _, g in sub]
                for metric in METRICS + ['seen_target_mrr', 'unseen_target_mrr', 'seen_target_top10', 'unseen_target_top10',
                                         'seen_target_recall10', 'unseen_target_recall10', 'H_MRR', 'H_Top10', 'H_Recall10',
                                         'top1_seen_rate', 'top10_seen_count_mean', 'mixed_both_hit10']:
                    values = [r[metric] for r in sr]
                    result[metric + '_equal_scene_mean'] = mean(values)
                    result[metric + '_defined_scene_count'] = sum(numeric(v) for v in values)
                result['harmonic_of_equal_scene_MRR'] = harmonic(result['seen_target_mrr_equal_scene_mean'], result['unseen_target_mrr_equal_scene_mean'])
                result['mrr_scene_SD'] = statistics.stdev([r['mrr'] for r in sr])
                byseed.append({**base, **result})
                for stratum in STRATA[1:]:
                    rm = merged.metrics[stratum].result()
                    for metric in METRICS:
                        vals = [g.metrics[stratum].result()[metric] for _, g in sub]
                        rm[metric + '_equal_scene_mean'] = mean(vals)
                    rm['defined_scenes'] = sum(g.metrics[stratum].n > 0 for _, g in sub)
                    stratum_seeds.append({**base, 'stratum': stratum, **rm})
    return scenes, byseed, stratum_scenes, stratum_seeds, aggregates


def evaluate(path, tradeoff=False):
    wall_start, cpu_start = time.perf_counter(), time.process_time()
    check(path.is_file() and path.stat().st_size > 0, 'Saved prediction file required before formal evaluation reads heldout references')
    ids, folds, refs, foldrefs, frozen = setup()
    universe = set(ids)
    groups, supports, seenby, matrices = {}, {}, {}, {}
    details, classrows = [], []
    for fid in folds:
        for seed in SEEDS:
            for view in VIEWS:
                npz = ROOT / 'score_matrices' / f'{fid}_seed{seed}_{view}.npz'
                with np.load(npz, allow_pickle=False) as z:
                    zids = list(map(str, z['technique_ids']))
                    seen = {t for t, flag in zip(zids, z['seen']) if flag}
                    support = {t: int(v) for t, v in zip(zids, z['support'])}
                check(set(zids) == universe and len(zids) == 216, 'NPZ candidate universe')
                check(seen == set(folds[fid]['train_seen_techniques']), 'NPZ seen set differs from frozen training set')
                check({t for t, count in support.items() if count > 0} == seen, 'Support and seen mismatch')
                supports[fid, seed, view], seenby[fid, seed, view] = support, seen
                matrices[fid, seed, view] = {'path': str(npz.relative_to(ROOT)), 'sha256': sha(npz)}
    nrows = 0
    for row in jl(path):
        nrows += 1
        method = row['method']
        if tradeoff:
            check(method == 'C4', 'Tradeoff restricted to selected-lambda C4')
            method = 'C4_gamma_' + format(float(row['gamma']), '.12g')
        else:
            check(method in METHODS, 'Unexpected prediction method ' + method)
        seed, view, fid, sid = str(row['seed']), row['view_id'], row['fold_id'], row['sample_id']
        check(seed in SEEDS and view in VIEWS and fid in folds, 'Unknown config')
        check(sid in foldrefs[fid], 'Prediction outside legal heldout set')
        check(row['logical_step_id'] == refs[sid]['logical_step_id'], 'Logical step mismatch')
        rank, scores = row['ranking_all216'], row['scores_all216']
        check(len(rank) == len(set(rank)) == 216 and set(rank) == universe, 'Invalid full216 ranking')
        check(row['predictions'] == rank[:10], 'Top10 inconsistent with full216 ranking')
        check(len(scores) == 216 and all(v is None or math.isfinite(v) for v in scores), 'Invalid full216 score vector')
        key = method, seed, view, fid
        if key not in groups:
            groups[key] = Group(ids)
        group = groups[key]
        seen, support = seenby[fid, seed, view], supports[fid, seed, view]
        group.add(row, refs[sid], seen, support)
        if not tradeoff:
            positions = {t: i + 1 for i, t in enumerate(rank)}
            gold = set(refs[sid]['gold_technique_ids'])
            sg, ug, top10 = gold & seen, gold - seen, set(rank[:10])
            def best(target):
                return min(positions[t] for t in target) if target else NA
            def rr(target):
                b = best(target)
                return (1 / b if b <= 10 else 0) if numeric(b) else NA
            details.append({'method': method, 'seed': seed, 'view_id': view, 'fold_id': fid, 'scenario': folds[fid]['heldout_scenario'],
                            'sample_id': sid, 'logical_step_id': row['logical_step_id'],
                            'gold_technique_ids': '|'.join(sorted(gold)), 'seen_gold': '|'.join(sorted(sg)), 'unseen_gold': '|'.join(sorted(ug)),
                            'gold_count': len(gold), 'seen_gold_count': len(sg), 'unseen_gold_count': len(ug),
                            'sample_type': 'ALL_SEEN' if not ug else 'ALL_UNSEEN' if not sg else 'MIXED',
                            'top1': int(rank[0] in gold), 'top5': int(bool(set(rank[:5]) & gold)), 'top10': int(bool(top10 & gold)),
                            'mrr': rr(gold), 'best_gold_rank216': best(gold), 'seen_target_mrr': rr(sg), 'unseen_target_mrr': rr(ug),
                            'seen_best_rank216': best(sg), 'unseen_best_rank216': best(ug),
                            'seen_hit10': int(bool(top10 & sg)) if sg else NA, 'unseen_hit10': int(bool(top10 & ug)) if ug else NA,
                            'seen_recall10': len(top10 & sg) / len(sg) if sg else NA, 'unseen_recall10': len(top10 & ug) / len(ug) if ug else NA,
                            'both_seen_unseen_hit10': int(bool(top10 & sg) and bool(top10 & ug)) if sg and ug else NA,
                            'top1_seen': int(rank[0] in seen), 'top10_seen_count': len(top10 & seen),
                            'ranked_top10': '|'.join(rank[:10]), 'semantic_cause': 'UNRESOLVED'})
    methodlist = sorted({k[0] for k in groups})
    check(set(methodlist) == ({'C4_gamma_' + format(v, '.12g') for v in [0, .1, .2, .4]} if tradeoff else set(METHODS)), 'Methods/grid not complete')
    check(len(groups) == len(methodlist) * 42, 'Incomplete method/fold/seed/view matrix')
    frozen_checks = 0
    frozen_stratum_checks = 0
    max_metric_error = 0.0
    for key, group in sorted(groups.items()):
        method, seed, view, fid = key
        check(group.samples == set(foldrefs[fid]), 'Missing heldout sample')
        frozen_result = frozen.summarize(group.full_gold_refs, ids)
        independent_result = group.metrics['ALL'].result()
        for metric in METRICS:
            err = abs(frozen_result[metric] - independent_result[metric])
            max_metric_error = max(max_metric_error, err)
            check(err < 1e-12, 'Independent metric differs from frozen evaluator: ' + metric)
            frozen_checks += 1
        # Recompute all target/sample/support strata with the independent frozen
        # evaluator using an independently constructed filtered reference list.
        seen = seenby[fid, seed, view]
        support = supports[fid, seed, view]
        for stratum in STRATA[1:]:
            source = []
            for saved in group.full_gold_refs:
                gold = set(saved['ground_truth'])
                sg, ug = gold & seen, gold - seen
                target = gold
                if stratum == 'SEEN_TARGET':
                    target = sg
                elif stratum == 'UNSEEN_TARGET':
                    target = ug
                elif stratum == 'ALL_SEEN' and ug:
                    continue
                elif stratum == 'ALL_UNSEEN' and sg:
                    continue
                elif stratum == 'MIXED' and not (sg and ug):
                    continue
                elif stratum == 'SINGLE_LABEL' and len(gold) != 1:
                    continue
                elif stratum == 'MULTILABEL' and len(gold) <= 1:
                    continue
                elif stratum.startswith('SUPPORT_'):
                    target = {t for t in gold if bucket(support[t]) == stratum}
                if target:
                    source.append({'ground_truth': sorted(target), 'predictions': saved['predictions']})
            actual = group.metrics[stratum].result()
            check(actual['n_records'] == len(source), 'Independent stratum count')
            if not source:
                check(all(actual[m] == NA for m in METRICS), 'Empty stratum must beNA')
                continue
            expected = frozen.summarize(source, ids)
            for metric in METRICS:
                err = abs(actual[metric] - expected[metric])
                max_metric_error = max(max_metric_error, err)
                check(err < 1e-12, 'Independent stratum metric: ' + stratum + '/' + metric)
                frozen_stratum_checks += 1
        if not tradeoff:
            support = supports[fid, seed, view]
            for t in ids:
                n = group.class_n[t]
                a, b, c = group.metrics['ALL'].tp[t], group.metrics['ALL'].fp[t], group.metrics['ALL'].fn[t]
                den = 2 * a + b + c
                classrows.append({'method': method, 'seed': seed, 'view_id': view, 'fold_id': fid, 'scenario': folds[fid]['heldout_scenario'],
                                  'technique_id': t, 'training_class_support': support[t], 'support_bucket': bucket(support[t]),
                                  'candidate_seen_in_training': support[t] > 0, 'gold_queries': n, 'gold_logical_steps': len(group.class_steps[t]),
                                  'class_mrr': group.class_mrr[t] / n if n else NA, 'class_top10': group.class_hit[t] / n if n else NA,
                                  'class_recall10': group.class_hit[t] / n if n else NA, 'TP_at5': a, 'FP_at5': b, 'FN_at5': c,
                                  'class_f1_at5': 2 * a / den if den else 0.0})
    scenes, byseed, stratum_scenes, stratum_seeds, aggregates = summarize(groups, ids, folds, methodlist)
    if not tradeoff:
        class_by_condition_bucket = defaultdict(list)
        for r in classrows:
            class_by_condition_bucket[r['method'], r['seed'], r['view_id'], r['fold_id'], r['support_bucket']].append(r)
        for row in stratum_scenes:
            if not row['stratum'].startswith('SUPPORT_'):
                continue
            rr = class_by_condition_bucket[row['method'], row['seed'], row['view_id'], row['fold_id'], row['stratum']]
            present = [r for r in rr if r['gold_queries'] > 0]
            row['candidate_technique_count_in_bucket'] = len(rr)
            row['class_macro_mrr'] = mean([r['class_mrr'] for r in present])
            row['class_macro_recall10'] = mean([r['class_recall10'] for r in present])
        for row in stratum_seeds:
            if not row['stratum'].startswith('SUPPORT_'):
                continue
            rr = [r for fid in folds for r in class_by_condition_bucket[row['method'], row['seed'], row['view_id'], fid, row['stratum']]]
            present = [r for r in rr if r['gold_queries'] > 0]
            row['candidate_fold_technique_pairs'] = len(rr)
            row['target_fold_technique_pairs'] = len(present)
            row['candidate_techniques_unique_across_folds'] = len({r['technique_id'] for r in rr})
            row['class_macro_mrr'] = mean([r['class_mrr'] for r in present])
            row['class_macro_recall10'] = mean([r['class_recall10'] for r in present])
            row['class_macro_unit'] = 'EQUAL_OBSERVED_FOLD_TECHNIQUE_PAIR'
    averages = seedmean(byseed, ['method', 'view_id'])
    for row in averages:
        row['seed_role'] = ('DETERMINISTIC_REPETITION_FOR_PAIRED_COMPARISON' if row['method'] in ['Z0', 'C0', 'C1', 'C5']
                            else 'INHERITED_TRAINED_HEAD_SEED_NO_NEW_TRAINING')
    stratum_avg = seedmean(stratum_seeds, ['method', 'view_id', 'stratum'])
    if tradeoff:
        for table in [scenes, byseed, averages]:
            for row in table:
                row['gamma'] = float(row['method'].split('_gamma_')[1])
                row['method'] = 'C4'
                row['qualification'] = 'DESCRIPTIVE_OUTER_TRADEOFF_NOT_USED_FOR_PARAMETER_SELECTION'
        csvout('results/TRADEOFF_BY_SCENE.csv', scenes)
        csvout('results/TRADEOFF_BY_SEED.csv', byseed)
        csvout('SEEN_UNSEEN_TRADEOFF.csv', averages)
    else:
        csvout('FUSION_RESULTS.csv', averages)
        csvout('results/OVERALL_RESULTS_BY_SEED.csv', byseed)
        csvout('results/SCENE_RESULTS.csv', scenes)
        csvout('results/STRATA_BY_SCENE.csv', stratum_scenes)
        csvout('results/STRATA_BY_SEED.csv', stratum_seeds)
        csvout('results/PER_SAMPLE_RESULTS.csv', details)
        csvout('results/PER_CLASS_RESULTS.csv', classrows)
        z0_details = {(r['seed'], r['view_id'], r['sample_id']): r for r in details if r['method'] == 'Z0'}
        phenomena, phenomenon_sums = [], defaultdict(Counter)
        for r in details:
            if not r['unseen_gold_count']:
                continue
            z = z0_details[r['seed'], r['view_id'], r['sample_id']]
            missed = not r['unseen_hit10']
            structural = r['method'] in ['S0', 'P2']
            d1 = structural
            d2 = (r['method'] in ['C1', 'C2', 'C3', 'C4', 'C5', 'C6_B4', 'C6_B5']
                  and missed and bool(z['unseen_hit10']) and r['top10_seen_count'] > 0)
            d3 = missed and not z['unseen_hit10']
            d4 = r['sample_type'] == 'MIXED' and bool(r['seen_hit10']) and missed
            labels = [name for name, yes in [
                ('STRUCTURAL_UNSEEN_EXCLUSION', d1),
                ('SEEN_CLASS_SCORE_BIAS_CANDIDATE', d2),
                ('ZERO_SHOT_REPRESENTATION_LIMIT_CANDIDATE', d3),
                ('MIXED_LABEL_RANK_COMPETITION', d4)] if yes]
            phenomena.append({k: r[k] for k in ['method', 'seed', 'view_id', 'fold_id', 'scenario', 'sample_id', 'logical_step_id', 'sample_type',
                                                       'seen_gold', 'unseen_gold', 'unseen_hit10', 'unseen_target_mrr', 'unseen_best_rank216', 'top10_seen_count']})
            phenomena[-1].update(z0_unseen_hit10=z['unseen_hit10'], z0_unseen_target_mrr=z['unseen_target_mrr'], z0_unseen_best_rank216=z['unseen_best_rank216'],
                                 unseen_best_rank_delta_vs_Z0=r['unseen_best_rank216'] - z['unseen_best_rank216'],
                                 D1_structural_unseen_exclusion=int(d1), D2_seen_score_bias_candidate=int(d2),
                                 D3_zero_shot_representation_limit_candidate=int(d3), D4_mixed_label_rank_competition=int(d4),
                                 nonexclusive_phenomena='|'.join(labels) if labels else 'NONE_OF_FOUR_DEFINED_PHENOMENA',
                                 semantic_or_causal_explanation='UNRESOLVED',
                                 qualifier='Ranking_observations_only; overlapping_flags; no_claim_that_attack_mechanism_absent')
            c = phenomenon_sums[r['method'], r['seed'], r['view_id']]
            c['unseen_target_queries'] += 1
            c['unseen_top10_misses'] += int(missed)
            c['D1_count'] += int(d1)
            c['D2_count'] += int(d2)
            c['D3_count'] += int(d3)
            c['D4_count'] += int(d4)
            c['recovered_unseen_hit_vs_Z0'] += int(bool(r['unseen_hit10']) and not z['unseen_hit10'])
            c['lost_unseen_hit_vs_Z0'] += int(missed and bool(z['unseen_hit10']))
        phenomenon_seeds = []
        for (method, seed, view), counts in sorted(phenomenon_sums.items()):
            n = counts['unseen_target_queries']
            check(n == 450, 'Phenomenon denominator450')
            item = {'method': method, 'seed': seed, 'view_id': view, **counts}
            for label in ['D1', 'D2', 'D3', 'D4']:
                item[label + '_fraction_of_unseen_target_queries'] = counts[label + '_count'] / n
            phenomenon_seeds.append(item)
        csvout('results/RANK_FAILURE_PHENOMENA.csv', phenomena)
        csvout('results/RANK_FAILURE_PHENOMENA_BY_SEED.csv', phenomenon_seeds)
        csvout('results/RANK_FAILURE_PHENOMENA_SUMMARY.csv', seedmean(phenomenon_seeds, ['method', 'view_id']))
        csvout('SEEN_UNSEEN_MIXED_RESULTS.csv', [r for r in stratum_avg if r['stratum'] in STRATA[1:8]])
        csvout('LONG_TAIL_TECHNIQUE_RESULTS.csv', [r for r in stratum_avg if r['stratum'] in STRATA[8:]])
        csvout('MIXED_SAMPLE_COVERAGE.csv', [{k: v for k, v in r.items() if k in ['method', 'view_id', 'aggregation', 'seeds', 'uncertainty'] or k.startswith('mixed_')} for r in averages])
        csvout('MACRO_F1_COMPARISON.csv', [{k: v for k, v in r.items() if k in ['method', 'view_id', 'aggregation', 'seeds', 'uncertainty'] or 'macro_f1' in k or 'micro_f1' in k} for r in averages])
        csvout('PRIOR_BASELINE_RESULTS.csv', [r for r in averages if r['method'] in ['C0', 'C5', 'P2', 'Z0', 'S0']])
        primary, sensitivity = [], []
        contrasts = [('H1', 'C4', 'Z0'), ('H2', 'C4', 'S0'), ('H3', 'C1', 'Z0')]
        compare_metrics = ['mrr', 'top1_accuracy', 'top10_accuracy', 'macro_f1_at_5_all_candidates', 'seen_target_mrr', 'unseen_target_mrr', 'H_MRR', 'mixed_both_hit10']
        for hyp, method, baseline in contrasts:
            for view in VIEWS:
                for fid, fold in folds.items():
                    result = {'hypothesis': hyp, 'method': method, 'baseline': baseline, 'view_id': view, 'fold_id': fid, 'scenario': fold['heldout_scenario'],
                              'confirmatory_p_value': 'NOT_COMPUTED_DEPENDENT_EXPOSED_SCENARIOS', 'qualification': 'DEVELOPMENT_ONLY'}
                    for metric in compare_metrics:
                        av = mean([groups[method, s, view, fid].result()[metric] for s in SEEDS])
                        bv = mean([groups[baseline, s, view, fid].result()[metric] for s in SEEDS])
                        result[metric + '_delta_seed_mean'] = av - bv if numeric(av) and numeric(bv) else NA
                    primary.append(result)
                for omitted in folds:
                    result = {'hypothesis': hyp, 'method': method, 'baseline': baseline, 'view_id': view, 'omitted_scenario': folds[omitted]['heldout_scenario'],
                              'qualification': 'DELETE_ONE_SCENE_DESCRIPTIVE_SENSITIVITY_NOT_CONFIDENCE_INTERVAL'}
                    records = {}
                    scene_records = {}
                    for name in [method, baseline]:
                        records[name], scene_records[name] = [], []
                        for seed in SEEDS:
                            merged = Group(ids)
                            selected = [g for k, g in groups.items() if k[0] == name and k[1] == seed and k[2] == view and k[3] != omitted]
                            for group in selected:
                                merged.merge(group)
                            records[name].append(merged.result())
                            scene_records[name].append({m: mean([g.result()[m] for g in selected]) for m in compare_metrics})
                    for metric in compare_metrics:
                        for tag, source in [('query_weighted', records), ('equal_scene', scene_records)]:
                            av, bv = mean([r[metric] for r in source[method]]), mean([r[metric] for r in source[baseline]])
                            result[metric + '_' + tag + '_delta'] = av - bv if numeric(av) and numeric(bv) else NA
                    sensitivity.append(result)
        csvout('results/PRIMARY_HYPOTHESES_BY_SCENE.csv', primary)
        csvout('results/DELETE_ONE_SCENE_SENSITIVITY.csv', sensitivity)
        average_lookup = {(r['method'], r['view_id']): r for r in averages}
        primary_summary = []
        for hyp, method, baseline in contrasts:
            for view in VIEWS:
                av, bv, z0, s0 = [average_lookup[name, view] for name in [method, baseline, 'Z0', 'S0']]
                item = {'hypothesis': hyp, 'method': method, 'baseline': baseline, 'view_id': view,
                        'qualification': 'DESCRIPTIVE_DEVELOPMENT_CRITERIA_NOT_STATISTICAL_SIGNIFICANCE',
                        'confirmatory_p_value': 'NOT_COMPUTED_DEPENDENT_EXPOSED_SCENARIOS'}
                for metric in compare_metrics:
                    a, b = av[metric], bv[metric]
                    item['method_' + metric], item['baseline_' + metric] = a, b
                    item[metric + '_delta'] = a - b if numeric(a) and numeric(b) else NA
                    changes = [r[metric + '_delta_seed_mean'] for r in primary if r['hypothesis'] == hyp and r['view_id'] == view]
                    item[metric + '_positive_scenes'] = sum(numeric(x) and x > 1e-12 for x in changes)
                    item[metric + '_negative_scenes'] = sum(numeric(x) and x < -1e-12 for x in changes)
                    item[metric + '_tied_scenes'] = sum(numeric(x) and abs(x) <= 1e-12 for x in changes)
                    item[metric + '_undefined_scenes'] = sum(not numeric(x) for x in changes)
                    for tag in ['query_weighted', 'equal_scene']:
                        values = [r[metric + '_' + tag + '_delta'] for r in sensitivity if r['hypothesis'] == hyp and r['view_id'] == view]
                        values = [x for x in values if numeric(x)]
                        item[metric + '_' + tag + '_delete_one_min'] = min(values) if values else NA
                        item[metric + '_' + tag + '_delete_one_max'] = max(values) if values else NA
                item['seen_mrr_retained_fraction_of_S0'] = av['seen_target_mrr'] / s0['seen_target_mrr'] if s0['seen_target_mrr'] else NA
                item['unseen_mrr_retained_fraction_of_Z0'] = av['unseen_target_mrr'] / z0['unseen_target_mrr'] if z0['unseen_target_mrr'] else NA
                if hyp == 'H1':
                    passed = av['mrr'] > bv['mrr'] and av['unseen_target_mrr'] > 0
                    criterion = 'overall_MRR_gt_Z0_AND_unseen_MRR_gt_0'
                elif hyp == 'H2':
                    passed = (av['unseen_target_mrr'] > bv['unseen_target_mrr']
                              and item['seen_mrr_retained_fraction_of_S0'] >= .5
                              and item['unseen_mrr_retained_fraction_of_Z0'] >= .8)
                    criterion = 'unseen_MRR_gt_S0_AND_seen_retention_ge_0.5_S0_AND_unseen_retention_ge_0.8_Z0'
                else:
                    passed = av['unseen_target_mrr'] > bv['unseen_target_mrr']
                    criterion = 'unseen_MRR_gt_Z0'
                item['registered_criterion'], item['passes_registered_development_criterion'] = criterion, passed
                primary_summary.append(item)
        csvout('results/PRIMARY_HYPOTHESIS_SUMMARY.csv', primary_summary)
        prior_check = []
        oldrows = readcsv(OLD / 'results/OVERALL_RESULTS_BY_SEED.csv')
        for row in byseed:
            if row['method'] not in ['Z0', 'S0', 'C6_B4', 'C6_B5']:
                continue
            oldmethod = {'Z0': 'B1', 'S0': 'B3', 'C6_B4': 'B4', 'C6_B5': 'B5'}[row['method']]
            saved = [r for r in oldrows if r['method'] == oldmethod and (oldmethod == 'B1' or (r['seed'] == row['seed'] and r['augmentation'] == row['view_id']))]
            check(len(saved) == 1, 'Unique historical baseline')
            errors = {metric: row[metric] - float(saved[0][metric]) for metric in METRICS}
            check(max(abs(v) for v in errors.values()) < 1e-11, 'Reconstructed baseline metric changed: ' + str((oldmethod, row['seed'], row['view_id'], errors)))
            prior_check.append({'new_method': row['method'], 'old_method': oldmethod, 'seed': row['seed'], 'view_id': row['view_id'], 'max_metric_absolute_difference': max(abs(v) for v in errors.values())})
        csvout('results/HISTORICAL_BASELINE_METRIC_RECONSTRUCTION.csv', prior_check)
        for key, group in aggregates.items():
            check(group.metrics['ALL_SEEN'].n == 525 and group.metrics['ALL_UNSEEN'].n == 305 and group.metrics['MIXED'].n == 145, 'Global sample strata counts changed')
            check(group.metrics['SEEN_TARGET'].n == 670 and group.metrics['UNSEEN_TARGET'].n == 450, 'Target subset counts changed')
            check(group.metrics['SINGLE_LABEL'].n == 690 and group.metrics['MULTILABEL'].n == 285, 'Normalized parent multilabel counts')
    receipt = {'status': 'PASS', 'scope': 'TRADEOFF' if tradeoff else 'MAIN_FUSION', 'prediction_rows': nrows, 'methods': methodlist,
               'evaluation_conditions': len(groups), 'seed_conditions': len(byseed), 'method_view_summaries': len(averages),
               'independent_metric_checks_against_frozen_evaluator': frozen_checks, 'max_absolute_metric_difference': max_metric_error,
               'independent_stratum_metric_checks_against_frozen_evaluator': frozen_stratum_checks,
               'full216_candidates_preserved': True, 'formal_evaluation_reads_Gold_after_saved_predictions_exist': True,
               'pre_prediction_reference_preflight_disclosure': {
                   'occurrences': 2,
                   'purpose': 'Evaluator helper loaded heldout references during synthetic math/preflight checks; only public975query195step7fold counts were inspected',
                   'new_fusion_performance_computed_during_preflight': False,
                   'labels_sent_to_predictor_or_parameter_fitter': False,
                   'frozen_protocol_or_calibration_parameters_changed_using_outer_labels': False,
                   'scope': 'strict_no_reference_read_before_prediction_timing_not_met; calibration_Gold_isolation_preserved'},
               'prediction_sha256': sha(path), 'evaluator_sha256': sha(Path(__file__)),
               'frozen_evaluator_sha256': sha(BENCH / 'evaluate_techniques.py'),
               'split_sha256': sha(OLD / 'GROUPED_TRAIN_VALIDATION_SPLITS.json'),
               'parameter_registration_sha256': REGISTRATION_SHA256,
               'resource': {'CPU_thread_limit': 2, 'wall_seconds': time.perf_counter() - wall_start,
                            'process_CPU_seconds': time.process_time() - cpu_start,
                            'process_highwater_rss_Mac_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                            'new_training_updates': 0, 'GPU_calls': 0, 'model_calls': 0, 'LLM_calls': 0},
               'counts_per_method_seed_view': {'queries': 975, 'logical_steps': 195, 'scenarios': 7, 'all_seen': 525, 'all_unseen': 305, 'mixed': 145, 'seen_target': 670, 'unseen_target': 450},
               'limitations': ['PUBLIC_EXPOSED_DEVELOPMENT; no independent external test', 'Mixed queries occur in both target strata;670+450 is not an independent sample count',
                              'Gold-target subset P/F1 count true labels outside the target as false positives; use subset MRR/Top10/Recall for interpretation',
                              'Seed SD does not estimate independent attack variability', 'No confirmatory p-value or ordinary IID interval',
                              'Class-wise metrics with no evaluated positive are NA; class F1 remains0 for absent classes in fixed216 macro average',
                              'Equal-scene target means omit only undefined target scenes and disclose their count; query-weighted H and mean scene H are distinct'],
               'score_matrix_sources': list(matrices.values())}
    output = ROOT / 'results' / ('TRADEOFF_EVALUATION_AUDIT.json' if tradeoff else 'EVALUATION_AUDIT.json')
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--tradeoff', action='store_true')
    args = parser.parse_args()
    prediction = ROOT / ('predictions/TRADEOFF_PREDICTIONS.jsonl' if args.tradeoff else 'FUSION_PREDICTIONS.jsonl')
    result = evaluate(prediction, args.tradeoff)
    print(json.dumps({k: result[k] for k in ['status', 'scope', 'prediction_rows', 'evaluation_conditions', 'independent_metric_checks_against_frozen_evaluator', 'max_absolute_metric_difference']}))
