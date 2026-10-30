"""Serialize the recorded same-context AI judgments; no model/ranking access.

The manual step plans retain separate per-view overrides. Support is intersected
with the exact query text; a missing support citation is a hard error.
"""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((R / name).read_text())


def dump(name, value):
    (R / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def jsonlines(name):
    return [json.loads(s) for s in (R / name).read_text().splitlines() if s.strip()]


def writecsv(name, rows, fields):
    with (R / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(row.get(k), ensure_ascii=False) if isinstance(row.get(k), (list, dict)) else row.get(k) for k in fields})


def source_type(text):
    if '[**]' in text or 'Classification:' in text:
        return 'IDS_ALERT_DERIVED_PATTERN_NOT_NATIVE_PAYLOAD'
    if 'type=' in text and ('audit(' in text or 'msg=audit' in text):
        return 'AUDIT_RECORD_AS_DISPLAYED_NOT_INDEPENDENTLY_CERTIFIED'
    if 'sudo:' in text or 'sudo[' in text or 'COMMAND=' in text:
        return 'SUDO_COMMAND_RECORD_AS_DISPLAYED_NOT_PROOF_OF_COMPLETION'
    if 'AttackMate' in text or 'selenium' in text.lower():
        return 'AUTOMATION_OR_APPLICATION_TRACE_NOT_SERVER_AUTHENTICATION_PROOF'
    return 'APPLICATION_SYSTEM_OR_NETWORK_LOG_AS_DISPLAYED_UNCERTIFIED'


BLOCK = 'NOT_EVALUABLE_WITHOUT_BREAKING_ALLOWED_REVIEW_INPUT_CONTRACT'
KNOWN = ['DIRECT_EVIDENCE_PRESENT', 'PARTIAL_EVIDENCE_PRESENT',
         'BACKGROUND_COMPATIBILITY_ONLY', 'NO_RELEVANT_EVIDENCE_IN_VISIBLE_SCOPE',
         'INSUFFICIENT_VISIBLE_INPUT', 'COMPETING_TECHNIQUE_AMBIGUITY',
         'GOLD_SCOPE_OR_GRANULARITY_UNCERTAIN', 'NOT_EVALUABLE']

# Decompose compound propositions without relaxing their reference meaning.
# A recorded action can be direct evidence while a purpose or returned result
# in the full catalog proposition remains unestablished.
ACTION_ONLY = {
    'T1136': ('创建本地账户', '维持访问的目的和后续使用未建立'),
    'T1072': ('通过集中管理/软件部署系统执行命令', '恶意使用、横向活动和授权边界未建立'),
    'T1010': ('发起当前打开应用窗口的枚举请求', '未显示返回的窗口列表；冻结原文允许attempt，本条直接支持请求而不认证返回内容'),
}


def main():
    rows = jsonlines('inputs/REVIEW_INPUTS.jsonl')
    facts = jsonlines('inputs/VISIBLE_FACT_REGISTRY.jsonl')
    factmap = {f['fact_id']: f for f in facts}
    aids = {a['logical_step_id']: a for a in read('inputs/STEP_READING_AID.json')}
    plans = read('review/step_judgments.json')
    catalog = read('review/GOLD_CONDITION_CATALOG.json')
    assert set(plans) == set(aids)
    out, progress = [], []

    for row in rows:
        rid, step = row['review_id'], row['logical_step_id']
        plan, aid = plans[step], aids[step]
        own = [factmap[f] for f in row['visible_fact_ids']]

        def local_refs(union_ids):
            texts = {aid['all_visible_line_texts'][i - 1]['text'] for i in union_ids}
            return [f['fact_id'] for f in own if f['text'] in texts]

        def resolve_override(key, seen=()):
            assert key not in seen
            ov = plan.get('overrides', {}).get(key, {})
            return resolve_override(ov['same_as'], seen + (key,)) if 'same_as' in ov else ov

        ov = resolve_override(rid)
        base = {'assessment': plan['default'],
                'support_union_lines': plan.get('support_union_lines', []),
                'reason': plan['note']}
        base.update(ov)
        conditions, gold_reviews = [], []

        for tech in row['gold_technique_ids']:
            c = catalog[tech]
            j = dict(base)
            j.update(plan.get('per_gold', {}).get(tech, {}))
            # Per-target judgments with no explicit support must not inherit a
            # different target's selected lines.
            if tech in plan.get('per_gold', {}) and 'support_union_lines' not in plan['per_gold'][tech]:
                j['support_union_lines'] = []
            assessment = j['assessment']
            refs = local_refs(j.get('support_union_lines', []))
            if assessment in ('DIRECT_EVIDENCE_PRESENT', 'PARTIAL_EVIDENCE_PRESENT'):
                assert refs, (rid, tech, 'positive manual judgment lacks current-view support')
            status = {'DIRECT_EVIDENCE_PRESENT': 'DIRECTLY_SUPPORTED',
                      'PARTIAL_EVIDENCE_PRESENT': 'PARTIALLY_SUPPORTED',
                      'INSUFFICIENT_VISIBLE_INPUT': 'NOT_OBSERVABLE_IN_CURRENT_VIEW',
                      'GOLD_SCOPE_OR_GRANULARITY_UNCERTAIN': 'NOT_EVALUABLE',
                      'NOT_EVALUABLE': 'NOT_EVALUABLE'}.get(assessment, 'NOT_ESTABLISHED')
            positive = status in ('DIRECTLY_SUPPORTED', 'PARTIALLY_SUPPORTED')
            missing = j.get('missing', plan.get('missing', ''))
            specific_gap = missing or j['reason']
            scope = row['coverage_limitations'] + [c['reference_scope_qualification'],
                '直接证据仅指行为核心相关，不等于完整技术、恶意归属或唯一正确标签得到确认。']

            def cond(suffix, text, kind, ev, cite, gap, reasoning, required=True):
                item = {'condition_id': f'{rid}_{tech}_{suffix}', 'technique_id': tech,
                        'condition_text': text, 'condition_type': kind,
                        'required_or_distinguishing': required,
                        'applies_to_visible_variant_only': c['required_conditions_apply_only_to_visible_variant_when_scope_partial'],
                        'evidence_status': ev,
                        'supporting_fact_ids': cite if ev in ('DIRECTLY_SUPPORTED', 'PARTIALLY_SUPPORTED') else [],
                        'contradicting_fact_ids': [],
                        'context_fact_ids': cite if ev not in ('DIRECTLY_SUPPORTED', 'PARTIALLY_SUPPORTED') else [],
                        'supporting_source_type': sorted({source_type(factmap[f]['text']) for f in cite}) if ev in ('DIRECTLY_SUPPORTED', 'PARTIALLY_SUPPORTED') else [],
                        'missing_information': [] if ev == 'DIRECTLY_SUPPORTED' else [gap],
                        'scope_limitations': scope, 'reasoning': reasoning}
                conditions.append(item)
                return item['condition_id']

            ids = []
            core_status = status
            core_reason = j['reason']
            if tech in ACTION_ONLY and assessment == 'DIRECT_EVIDENCE_PRESENT':
                core_status = 'PARTIALLY_SUPPORTED'
                core_reason += '；复合命题分解：' + ACTION_ONLY[tech][1] + '。直接相关动作另列，不把它当作完整复合命题成立。'
                ids.append(cond('OBSERVED_ACTION', ACTION_ONLY[tech][0], 'OBSERVABLE_ACTION_COMPONENT',
                                'DIRECTLY_SUPPORTED', refs, '', j['reason']))
            ids.append(cond('CORE', c['core_condition'], 'CORE_BEHAVIOR', core_status, refs,
                            '未建立完整核心条件：' + specific_gap, core_reason))
            ids.append(cond('OBJECT', c['object_condition'], 'ACTION_OBJECT_AND_BINDING', status, refs,
                            '需要对象与核心动作的可核验绑定；' + specific_gap,
                            '按当前视图的已记录对象解释，不把文件名、域名或工具名自动认证为技术对象。' + j['reason']))
            ids.append(cond('ACTOR', '执行主体及该动作的对抗性用途/授权边界', 'ATTRIBUTION_AND_CONTEXT',
                            'NOT_ESTABLISHED', [],
                            '日志中可能出现进程、账号或IP；没有独立主体身份/授权/目的裁定，不能从root、工具名或Gold反推攻击者。',
                            '该条件保留完整技术归属所需的上下文；不作为否定已观测动作的理由。'))
            if c['result_required_in_visible_definition']:
                result_status = 'DIRECTLY_SUPPORTED' if assessment == 'DIRECT_EVIDENCE_PRESENT' else (
                    'NOT_EVALUABLE' if status == 'NOT_EVALUABLE' else 'NOT_ESTABLISHED')
                result_text = '本地新账户状态及属性已经出现；目的另列' if tech == 'T1136' else '核心动作要求的状态变化/结果：' + c['core_condition']
                ids.append(cond('RESULT', result_text,
                                'STATE_CHANGE_OR_REQUIRED_RESULT', result_status, refs if result_status == 'DIRECTLY_SUPPORTED' else [],
                                '未认证相应结果；请求、进程启动、文件改名或单次返回值不足以补齐。' + specific_gap,
                                j['reason']))
            ids.append(cond('DISTINGUISH', c['distinguishing_information_needed'], 'DISCRIMINATING_RELATION_TO_RANKED_CANDIDATES',
                            'NOT_EVALUABLE', [],
                            '本轮允许的审查输入不含Top10竞争候选，无法确定需要逐对检验的竞争命题；不把未比较写成已排除。',
                            BLOCK))
            if c['variant_specific_requirements_not_necessary_for_every_parent_subtype']:
                ids.append(cond('PARENT_SCOPE', '父技术ID与当前冻结正文变体的完整适用范围', 'TAXONOMY_SCOPE',
                                'NOT_EVALUABLE', [],
                                c['reference_scope_qualification'] + '；未提供完整父类及全部子类合同，不能由某变体不满足推导整个父技术错误。',
                                '保持冻结描述原文；子类型细节只用于可见变体，不能回填或改写父类定义。'))
            gold_reviews.append({'technique_id': tech, 'frozen_name': c['frozen_name'],
                                 'frozen_description_sha256': c['frozen_description_sha256'],
                                 'frozen_description': c['frozen_description'],
                                 'evidence_assessment': assessment, 'supporting_fact_ids': refs if positive else [],
                                 'context_fact_ids': refs if not positive else [],
                                 'reasoning': j['reason'], 'condition_ids': ids,
                                 'reference_scope_qualification': c['reference_scope_qualification'],
                                 'prerequisite_condition_ids': [i for i in ids if i.endswith(('_CORE', '_OBJECT'))],
                                 'prerequisite_scope': '定义中的目标、有效材料/访问及核心动作关系在CORE/OBJECT中检验；不把示例实现或某一变体的前提扩展为全部父类必要条件。未提供完整父类时不能穷尽其前提。',
                                 'possible_actor_asset_scope': '只保留当前visible_facts字面中的账号、进程、主机和对象；CORE/OBJECT/ACTOR分别检查动作绑定和归属，不由simulation_id反推主体。',
                                 'optional_definition_behaviors': c['optional_behaviors'],
                                 'definition_examples_are_not_observation_facts': True})

        overall = base['assessment']
        assert overall in KNOWN
        labels = []
        label_map = {'DIRECT_EVIDENCE_PRESENT': 'OBSERVABLE_EVIDENCE_PRESENT',
                     'PARTIAL_EVIDENCE_PRESENT': 'PARTIAL_EVIDENCE_PRESENT',
                     'BACKGROUND_COMPATIBILITY_ONLY': 'BACKGROUND_COMPATIBILITY_ONLY',
                     'NO_RELEVANT_EVIDENCE_IN_VISIBLE_SCOPE': 'NO_RELEVANT_EVIDENCE_IN_VISIBLE_SCOPE',
                     'INSUFFICIENT_VISIBLE_INPUT': 'INSUFFICIENT_VISIBLE_INPUT',
                     'GOLD_SCOPE_OR_GRANULARITY_UNCERTAIN': 'GOLD_LOG_GRANULARITY_MISMATCH'}
        for g in gold_reviews:
            label = label_map.get(g['evidence_assessment'])
            if label and label not in [x['label'] for x in labels]:
                labels.append({'label': label, 'reason': g['reasoning'],
                               'interpretation': 'potential alignment/scope issue, not proven incorrect Gold' if label == 'GOLD_LOG_GRANULARITY_MISMATCH' else 'same-context AI pre-review'})
        labels.append({'label': 'SEMANTIC_CAUSE_UNRESOLVED', 'reason': 'Top10逐对比较未执行、缺少独立人工裁定且当前上下文已接触历史结果。'})
        failures = [{'label': 'OBSERVATION_COVERAGE_LIMITATION',
                     'reason': '当前冻结视图边界已知，完整源日志及省略记录数未知；这是裁定限制，不是已确定的漏召回根因。'},
                    {'label': 'UNRESOLVED', 'reason': '未得到独立语义参考和合法候选比较，不能将漏召回归因于表示排序。'}]
        if any(g['evidence_assessment'] == 'GOLD_SCOPE_OR_GRANULARITY_UNCERTAIN' for g in gold_reviews):
            failures.append({'label': 'GOLD_SCOPE_OR_GRANULARITY_UNCERTAIN', 'reason': plan['note']})
        positive_ids = list(dict.fromkeys(f for g in gold_reviews for f in g['supporting_fact_ids']))
        record = {k: row[k] for k in ['review_id', 'sample_id', 'logical_step_id', 'scenario_id',
                  'execution_id', 'execution_id_mapping', 'fold_id', 'view_id', 'input_view',
                  'input_view_hash', 'gold_technique_ids']}
        record.update({
            'review_status': 'AI_BLIND_PRE_REVIEW_NOT_GOLD',
            'blinding_status': 'PREDICTION_BLINDING_NOT_ENFORCED',
            'review_method': 'same-context AI read all step-union texts with per-query occurrence mapping; serialized manual plans; not independent per-case adjudication',
            'visible_scope': {k: row[k] for k in ['visible_fact_ids', 'visible_record_count',
                'visible_record_count_unit', 'omitted_record_count', 'native_fact_ids_provided', 'coverage_limitations']},
            'evidence_source': {'path': read('inputs/FROZEN_REVIEW_MANIFEST.json')['case_source_path'],
                'sample_id': row['sample_id'], 'input_hash': row['input_view_hash'],
                'fact_id_kind': 'DERIVED_SOURCE_LOCATOR_NOT_ORIGINAL_EVENT_ID'},
            'visible_facts': [{'fact_id': f['fact_id'], 'literal_text': f['text'],
                               'source_type': source_type(f['text']), 'text_sha256': f['text_sha256']} for f in own],
            'gold_reviews': gold_reviews, 'gold_semantic_conditions': conditions,
            'current_view_reasoning': base['reason'],
            'cross_query_evidence_borrowing': False,
            'competing_technique_analysis': {
                'status': BLOCK, 'competing_techniques_reviewed': [],
                'shared_observable_conditions': [],
                'distinguishing_conditions': [c['condition_id'] for c in conditions if c['condition_type'] == 'DISCRIMINATING_RELATION_TO_RANKED_CANDIDATES'],
                'unresolved_competing_explanations': ['未读取预测候选，不能确认共享条件、排除竞争技术或断言Gold必须排名更高。'],
                'Gold_is_unique_supported_explanation': False},
            'overall_evidence_assessment': overall,
            'overall_assessment_rule': 'manual conservative query-level judgment; multi-Gold can contain direct and unresolved targets, see separate gold_reviews',
            'diagnostic_labels': labels, 'failure_diagnoses': failures,
            'alternative_explanations': ['可见活动可能属于正常管理/后台维护或其他尚未建立的行为链；当前材料未裁定恶意目的。', base['reason']],
            'unresolved_questions': ['完整源日志是否含未显示的区分字段？省略数量及上游选择/截断原因未知。',
                                     '当前目标Gold与实际动作的主体、对象、时间和范围是否由独立证据绑定？',
                                     'Top10竞争技术逐对比较及独立人工裁定尚未完成。'],
            'confidence': 'MEDIUM' if positive_ids and overall == 'DIRECT_EVIDENCE_PRESENT' else 'LOW',
            'confidence_basis': '明确记录的行为核心可提高局部判断确定性；' + base['reason'] + '；冻结视图、定义范围及历史信息暴露限制完整归属判断。置信度不是校准概率。',
            'human_review_required': True,
            'human_review_reasons': ['历史预测暴露，非独立盲审', '尚无人工Gold或独立语义裁定', 'Top10区分性比较未执行']})
        out.append(record)
        if len(out) % 32 == 0 or len(out) == len(rows):
            current = out
            ids = [x['sample_id'] for x in current]
            for x in current:
                for c in x['gold_semantic_conditions']:
                    for f in c['supporting_fact_ids'] + c['contradicting_fact_ids'] + c['context_fact_ids']:
                        assert factmap[f]['review_id'] == x['review_id']
            progress.append({'completed_queries': len(current), 'completed_logical_steps': len({x['logical_step_id'] for x in current}),
                             'remaining_queries': len(rows) - len(current), 'duplicate_ids': len(ids) - len(set(ids)),
                             'missing_from_processed_prefix': [], 'JSON_serialization_roundtrip': json.loads(json.dumps(current)) == current,
                             'citation_scope_check': 'PASS', 'historical_scores_inspected': False})

    with (R / 'review/QUERY_EVIDENCE_REVIEWS.jsonl').open('w') as f:
        for x in out:
            f.write(json.dumps(x, ensure_ascii=False, separators=(',', ':')) + '\n')
    dump('results/BATCH_COMPLETENESS_CHECKS.json', progress)
    flat = []
    for x in out:
        for c in x['gold_semantic_conditions']:
            flat.append({'review_id': x['review_id'], 'sample_id': x['sample_id'], **c})
    writecsv('review/CONDITION_EVIDENCE_MATRIX.csv', flat, ['review_id', 'sample_id', 'technique_id',
             'condition_id', 'condition_type', 'condition_text', 'applies_to_visible_variant_only',
             'evidence_status', 'supporting_fact_ids', 'contradicting_fact_ids', 'context_fact_ids',
             'supporting_source_type', 'missing_information', 'scope_limitations', 'reasoning'])
    summaries = [{'review_id': x['review_id'], 'sample_id': x['sample_id'], 'logical_step_id': x['logical_step_id'],
                  'gold_technique_ids': x['gold_technique_ids'], 'overall_evidence_assessment': x['overall_evidence_assessment'],
                  'any_gold_direct': any(g['evidence_assessment'] == 'DIRECT_EVIDENCE_PRESENT' for g in x['gold_reviews']),
                  'any_gold_partial': any(g['evidence_assessment'] == 'PARTIAL_EVIDENCE_PRESENT' for g in x['gold_reviews']),
                  'diagnostic_labels': [d['label'] for d in x['diagnostic_labels']],
                  'visible_lines': x['visible_scope']['visible_record_count'],
                  'confidence': x['confidence'], 'human_review_required': True,
                  'reasoning': x['current_view_reasoning']} for x in out]
    writecsv('results/QUERY_REVIEW_SUMMARY.csv', summaries, list(summaries[0]))
    queue = [{**s, 'human_review_reasons': x['human_review_reasons'],
              'priority_basis': 'verify directly cited core evidence and multi-target/scope ambiguity first; no calibrated severity ranking',
              'frozen_order_preserved': True} for s, x in zip(summaries, out)]
    writecsv('review/HUMAN_REVIEW_QUEUE.csv', queue, list(queue[0]))
    counts = {
        'unit': 'frozen query records; not independent attacks or Gold truths',
        'query_count': len(out), 'logical_steps': len(plans),
        'unique_target_techniques': len(catalog),
        'query_gold_assignments': sum(len(x['gold_reviews']) for x in out),
        'multi_gold_queries': sum(len(x['gold_reviews']) > 1 for x in out),
        'unique_visible_text_hashes': len({x['input_view_hash'] for x in out}),
        'any_direct_logical_steps': len({x['logical_step_id'] for x in out if any(g['evidence_assessment'] == 'DIRECT_EVIDENCE_PRESENT' for g in x['gold_reviews'])}),
        'top_partial_or_background_queries': sum(x['overall_evidence_assessment'] in {'PARTIAL_EVIDENCE_PRESENT', 'BACKGROUND_COMPATIBILITY_ONLY'} for x in out),
        'top_partial_or_background_without_any_direct_target': sum(x['overall_evidence_assessment'] in {'PARTIAL_EVIDENCE_PRESENT', 'BACKGROUND_COMPATIBILITY_ONLY'} and not any(g['evidence_assessment'] == 'DIRECT_EVIDENCE_PRESENT' for g in x['gold_reviews']) for x in out),
        'displayed_line_instances': len(facts),
        'exclusive_overall_assessments': {k: sum(x['overall_evidence_assessment'] == k for x in out) for k in KNOWN},
        'nonexclusive_any_gold_assessments': {k: sum(any(g['evidence_assessment'] == k for g in x['gold_reviews']) for x in out) for k in KNOWN},
        'gold_assignment_assessments': dict(Counter(g['evidence_assessment'] for x in out for g in x['gold_reviews'])),
        'diagnostic_label_query_counts_nonexclusive': dict(Counter(d['label'] for x in out for d in x['diagnostic_labels'])),
        'failure_diagnosis_query_counts_nonexclusive': dict(Counter(d['label'] for x in out for d in x['failure_diagnoses'])),
        'condition_status_counts': dict(Counter(c['evidence_status'] for c in flat)),
        'condition_rows': len(flat), 'independently_blinded_queries': 0,
        'ranked_competitor_comparisons_completed': 0, 'ranked_competitor_comparisons_blocked': len(out),
        'confirmed_distinguishable_from_ranked_competitors': None,
        'confirmed_distinguishable_count_interpretation': 'not evaluated, not zero evidence',
        'human_review_required_queries': len(out), 'human_adjudications_completed': 0,
        'confirmed_preprocessing_or_truncation_causal_failures': 0,
        'confirmed_representation_ranking_failures': 0,
        'formal_performance_metrics_computed': False}
    dump('results/REVIEW_COUNTS.json', counts)
    pair = []
    labels = sorted(counts['diagnostic_label_query_counts_nonexclusive'])
    for a in labels:
        for b in labels:
            pair.append({'label_a': a, 'label_b': b, 'query_count': sum({a, b} <= {d['label'] for d in x['diagnostic_labels']} for x in out)})
    writecsv('results/DIAGNOSTIC_LABEL_OVERLAP.csv', pair, ['label_a', 'label_b', 'query_count'])
    print(json.dumps(counts, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
