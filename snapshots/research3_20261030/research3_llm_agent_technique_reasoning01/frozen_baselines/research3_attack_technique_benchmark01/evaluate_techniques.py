"""Independent ranking evaluator. No external dependencies or model calls."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

ID = re.compile(r'T\d{4}(?:\.\d{3})?\Z')

def normalize_technique_id(value: object):
    text = str(value).strip().upper()
    return text.split('.')[0] if ID.fullmatch(text) else None

def normalize_ranked(values: list, universe=None) -> list:
    out, seen = [], set()
    for value in values:
        key = normalize_technique_id(value)
        if key is None or (universe is not None and key not in universe):
            out.append('__INVALID__')  # invalid predictions occupy their original rank
        elif key not in seen:
            seen.add(key)
            out.append(key)
    return out

def summarize(records: list, universe=None, official_compat: bool = False) -> dict:
    if not records:
        raise ValueError('No scoreable records')
    totals = Counter()
    tp, fp, fn = Counter(), Counter(), Counter()
    gold_all = set()
    for record in records:
        gold = {normalize_technique_id(x) for x in record['ground_truth']}
        if not gold or None in gold:
            raise ValueError('Missing or invalid gold labels: fail closed')
        if official_compat:
            pred = list(dict.fromkeys(str(x).strip().upper().split('.')[0] for x in record['predictions'] if x is not None and str(x).strip()))
        else:
            pred = normalize_ranked(record['predictions'], universe)
        gold_all |= gold
        ranks = [i+1 for i,x in enumerate(pred[:10]) if x in gold]
        totals['mrr'] += 1/min(ranks) if ranks else 0
        for k in (1,5,10):
            hits = len(set(pred[:k]) & gold)
            totals[f'top{k}_accuracy'] += int(hits > 0)
            totals[f'precision_at_{k}'] += hits/k
            totals[f'recall_at_{k}'] += hits/len(gold)
        selected = set(pred[:5])
        tp.update(gold & selected);fp.update(selected-gold);fn.update(gold-selected)
    n = len(records)
    result = {'n_records':n, **{k:v/n for k,v in totals.items()}}
    def f1(label):
        a,b,c=tp[label],fp[label],fn[label]
        return 2*a/(2*a+b+c) if 2*a+b+c else 0
    classes = set(universe) if universe else gold_all
    result['micro_f1_at_5'] = 2*sum(tp.values())/(2*sum(tp.values())+sum(fp.values())+sum(fn.values()))
    result['macro_f1_at_5_all_candidates'] = sum(map(f1,classes))/len(classes)
    result['macro_f1_at_5_gold_present'] = sum(map(f1,gold_all))/len(gold_all)
    return result

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('records');parser.add_argument('--output',required=True)
    args=parser.parse_args()
    records=[json.loads(x) for x in Path(args.records).read_text().splitlines()]
    Path(args.output).write_text(json.dumps(summarize(records),indent=2))
