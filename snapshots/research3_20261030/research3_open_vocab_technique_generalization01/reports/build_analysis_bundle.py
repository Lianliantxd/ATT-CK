"""Evidence-first analysis bundle from completed offline predictions."""
import csv
import hashlib
import json
import statistics
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'reports/analysis-output'
ONE, MULTI = 'ONE_VIEW_PER_STEP', 'MULTI_VIEW_AUGMENTATION'


def read(name):
    return list(csv.DictReader((R/name).open()))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def n(row,key):
    return float(row[key])


def main():
    O.mkdir(parents=True, exist_ok=True)
    overall = read('FUSION_RESULTS.csv')
    lookup = {(r['method'],r['view_id']):r for r in overall}
    z,s,c0,c3,c4 = [lookup[m,ONE] for m in ['Z0','S0','C0','C3','C4']]
    hypotheses = read('results/PRIMARY_HYPOTHESIS_SUMMARY.csv')
    seeds = read('results/OVERALL_RESULTS_BY_SEED.csv')
    byseed = {(r['method'],r['view_id'],r['seed']):r for r in seeds}
    audit = json.loads((R/'results/EVALUATION_AUDIT.json').read_text())
    tradeaudit = json.loads((R/'results/TRADEOFF_EVALUATION_AUDIT.json').read_text())
    pipeline = json.loads((R/'results/PIPELINE_LINEAGE_AUDIT.json').read_text())
    table = ['| 方法 | 总体MRR | Seen MRR | Unseen MRR | H_MRR | Top10 | Macro-F1@5 |',
             '|---|---:|---:|---:|---:|---:|---:|']
    methods = ['Z0','S0','C0','C1','C2','C3','C4','C5','P2','C6_B4','C6_B5']
    for m in methods:
        row=lookup[m,ONE]
        table.append('| '+m+' | '+' | '.join(f'{n(row,k):.6f}' for k in ['mrr','seen_target_mrr','unseen_target_mrr','H_MRR','top10_accuracy','macro_f1_at_5_all_candidates'])+' |')
    analysis = [
        '# 广义零样本离线融合：严格分析记录',
        '',
        '本分析限定7个已曝光场景的分组开发评价。核心比较为预注册C4相对Z0/S0以及C1相对Z0；不从外层结果重新选择方法或参数。ONE为主，MULTI为补充。没有新增训练、GPU前向、模型下载或LLM调用。',
        '',
        '**当前证据支持“相对结构排除的B3恢复部分Unseen排名”，不支持“已解决Seen—Unseen兼顾”或“新算法优于简单融合”。**',
        '',
        *table,
        '',
        f'C4总体MRR为{n(c4,"mrr"):.6f}，比Z0高{n(c4,"mrr")-n(z,"mrr"):.6f}，比S0低{n(s,"mrr")-n(c4,"mrr"):.6f}。其Seen保留率为{n(c4,"seen_target_mrr")/n(s,"seen_target_mrr"):.2%}，Unseen相对Z0保留率为{n(c4,"unseen_target_mrr")/n(z,"unseen_target_mrr"):.2%}。前者满足工作阈值50%，后者不满足80%，因此H2的预注册联合标准失败。H1仅要求比Z0总体更好且Unseen非零，得到开发性满足；不能把较弱H1解释成平衡问题已经解决。',
        '',
        f'C3总体MRR{n(c3,"mrr"):.6f}和H{n(c3,"H_MRR"):.6f}均略高于C4；C4并未获得独立于标准化分数融合的MRR增益。C0只使用唯一训练步骤频率，总体MRR已达到S0的{n(c0,"mrr")/n(s,"mrr"):.2%}。这个比例是基线成绩比，不是“频率因果解释了多少监督收益”的估计。C0在One-shot的类MRR为0，在More-shot的类MRR为0.424160，说明强频率基线与长尾能力必须分开报告。',
        '',
        '正式C1的Unseen MRR与Z0完全相同，Seen有所下降，H3没有改善。正式C4的H低于Z0；但固定诊断曲线中的gamma=0.4点ONE H=0.053182，高于Z0的0.049493，同时只保留72.46%的Z0 Unseen MRR。该点不是内验证正式选出的C4，不能事后替换主结果；它说明在此次固定范围内仍有其他取舍，不能断言所有简单偏置都无效。',
        '',
        'Mixed覆盖进一步限制总体增益的解释。C4在145条Mixed查询中Seen命中56.55%、Unseen命中3.45%，两类同时命中为0；Z0同时命中4.14%。总体命中提升没有转化为混合标签的完整覆盖。所有候选排名始终保留216类，未根据Gold过滤预测。',
        '',
        '逐样本ONE结果：Z0在450条Unseen-target查询中命中66条；C4命中34条，相对Z0新恢复0条、丢失32条。因此C4的“恢复”只相对B3的结构性Unseen排除成立。D2候选分数竞争32条，D3冻结语义也未命中384条；不能据此认定日志缺少机制证据或某攻击未发生，具体语义原因保持UNRESOLVED。',
        '',
        '## 可保留的论断与证据边界',
        '',
        '- 论断：简单监督残差恢复B3部分Unseen排序。证据：C4 Unseen MRR=0.023053，S0=0；同时Seen损失40.70%。允许措辞为“当前开发集的条件性恢复”；禁止“普遍开放词汇能力改善”。不确定性来自场景曝光、共享训练及有限类别覆盖。决策：保留，并同时报告保留率与Mixed失败。',
        '- 论断：C4未提供超越C3的独立收益。证据：C4/C3 ONE MRR=0.130524/0.131219，Unseen MRR相同。禁止把残差公式作为原创贡献。决策：当前复杂化NO-GO；未来机制必须超过现有简单融合。',
        '- 论断：频率先验是不可忽略的强基线。证据：C0总体MRR=0.161331，但Unseen与One-shot类MRR均0。禁止将成绩比当作因果归因比例。决策：保留类别先验、长尾与Macro-F1并列评价。',
        '- 论断：内验证选择与外层权衡存在差距。证据：正式C4 H低于Z0，固定gamma=0.4诊断点H略高于Z0但仍未满足80%Unseen保留阈值。禁止以该外层点替换正式配置。决策：可形成未来预先验证的校准稳定性问题，当前不扩展网格。',
        '',
        '## 证据质量与已披露流程偏差',
        '',
        f'独立实现对{audit["evaluation_conditions"]}个主条件的{audit["independent_metric_checks_against_frozen_evaluator"]}项总体指标、{audit["independent_stratum_metric_checks_against_frozen_evaluator"]}项分层指标与旧冻结评价器交叉复算，最大差值0。Z0/S0/B4/B5历史指标复现。另有23400行固定曲线预测独立评价。',
        '',
        '两次评估辅助预检在主预测完成之前加载了旧heldout_reference：一次用于合成数学测试初始化，一次用于核对已公开975/195/7计数。未计算新融合外层性能、未向预测器或拟合器传输Gold、未改变冻结协议或校准参数；但严格“会话内任何Gold均在预测后首次读取”的时序要求没有完全满足。正式评价在保存完整排名后运行。此偏差已在两份评价审计和PIPELINE_LINEAGE_AUDIT中保留，不用“零提前读取”表述掩盖。',
        '',
        '拟合器访问日志仅包含7份合法内部验证reference；预测器没有reference读取。462份选择记录、1722个有限网格条件及源文件/预测SHA一致。收据包含耗时而非签名绝对时间，文件mtime只提供阶段顺序的辅助证据，不能冒充独立时间证明。',
        '',
        '不能计算普通IID显著性或跨来源有效性：975查询包含195步骤的5次采样，3种子是计算重复，LOSO训练集合重叠，只有7个已曝光场景。当前分析没有独立外部测试结论。下一步判断应优先基于合法外部数据、校准支持量与Mixed失败，而不是立即启动LoRA或增加复杂模块。',
    ]
    (O/'analysis-report.md').write_text('\n'.join(analysis)+'\n')
    stats = ['# 统计附录', '',
             '比较单位：7个公开且已经曝光的场景；每场景含逻辑步骤，每步有5次相关查询。每方法/视图/种子975查询、195步骤；3个固定继承种子17/42/73。主方法11个×2视图×3种子×7折=462条件。未做新训练。', '',
             'S=Seen-target MRR（670查询），U=Unseen-target MRR（450查询）；Mixed145同时进入两目标子集。主H对分别合并查询后的S/U计算2SU/(S+U)；分母0则0，无目标则NA。H的种子均值不是一般意义上种子均值S/U的调和平均，所有表按实际逐种子计算再汇总。', '',
             '场景等权指标逐场景计算再平均；没有目标的场景为NA并报告有效场景数。Gold子集F1会将另一子集真标签计入FP，解释优先用MRR/Top10/Recall。Macro-F1固定216类，不能删掉缺失或未见类。', '',
             '效应量为配对绝对MRR差及保留率。误差棒为3种子样本标准差ddof=1，仅反映继承头/参数选择变化。Z0、C0、C1、C5的seed行是确定性重复，SD为0不意味着真实攻击间不确定性为0。', '',
             '不计算p值、置信区间或多重检验校正：这些条件不满足独立随机抽样与确认性推断前提。仅预注册3个可执行主要比较；H4只有在外部数据合格时才可执行。删除1场景得到的min/max是敏感范围，不是95%CI。', '',
             '| 假设 | 视图 | ΔMRR | 配对seed SD | 删除1场景ΔMRR范围 | 正/负/平场景 | 预注册条件 |',
             '|---|---|---:|---:|---|---|---|']
    for h in hypotheses:
        deltas = [n(byseed[h['method'],h['view_id'],seed],'mrr')-n(byseed[h['baseline'],h['view_id'],seed],'mrr') for seed in ['17','42','73']]
        stats.append(f'| {h["hypothesis"]}: {h["method"]}−{h["baseline"]} | {"ONE" if h["view_id"]==ONE else "MULTI"} | {n(h,"mrr_delta"):+.6f} | {statistics.stdev(deltas):.6f} | [{n(h,"mrr_query_weighted_delete_one_min"):+.6f}, {n(h,"mrr_query_weighted_delete_one_max"):+.6f}] | {h["mrr_positive_scenes"]}/{h["mrr_negative_scenes"]}/{h["mrr_tied_scenes"]} | {h["passes_registered_development_criterion"]} |')
    stats += ['', 'H1：总体MRR高于Z0且U>0；H2：U高于S0且Seen保留≥50% S0、Unseen保留≥80% Z0；H3：C1的U高于Z0。阈值是本轮预先规定的工作标准，不是普适效用函数。', '',
              '主数据表已保存全部Top1/5/10、Precision/Recall@1/5/10、Micro-F1@5、Macro-F1@5、S/U/H、Mixed覆盖和预测类别偏置。主要表：FUSION_RESULTS.csv；逐种子：results/OVERALL_RESULTS_BY_SEED.csv；逐场景：results/SCENE_RESULTS.csv；全部单/多标签与目标分层：results/STRATA_BY_SCENE.csv。', '',
              '长尾桶按各折唯一训练步骤支持计数：0、1、2—4、≥5。候选fold-technique组合分别1064/173/199/76，合计7×216；存在外层Gold的组合分别58/21/37/17。同一技术可以在不同折进入不同桶，不能把跨折唯一类数当作互斥类总数。', '',
              '排序现象D1—D4非互斥；不能相加作为独立错误总数。D1只表示S0/P2缺乏未见分类器；D2保留“候选”限定；D3也不是日志机制证据判定；D4为Mixed的覆盖竞争。', '',
              f'正式主评价耗时{audit["resource"]["wall_seconds"]:.3f}s（CPU {audit["resource"]["process_CPU_seconds"]:.3f}s），峰值RSS {audit["resource"]["process_highwater_rss_Mac_bytes"]:,}字节；曲线评价耗时{tradeaudit["resource"]["wall_seconds"]:.3f}s。均为本机过程级计数，不包含整个研究任务与其他阶段。']
    (O/'stats-appendix.md').write_text('\n'.join(stats)+'\n')
    catalog = ['# 图目录与解释要求', '', '全部图为实际保存结果，提供PDF、SVG与100dpi PNG。主图ONE、曲线同时ONE/MULTI。颜色仅区分方法/目标，不表示统计显著性。', '']
    descriptions = [
        ('figure01_main_seen_unseen','总体/Seen/Unseen三面板','FUSION_RESULTS.csv',
         '说明总体MRR收益与Unseen恢复是否兼得。','S0总体/Seen最强但U=0；C4恢复部分U，仍损失约40.7%Seen且仅保留约51.8%Z0的U。',
         '需保留S0强基线及S/U绝对指标，不能只比较C4对Z0总体增益。'),
        ('figure02_seen_unseen_tradeoff','固定偏置曲线及正式方法点','SEEN_UNSEEN_TRADEOFF.csv; FUSION_RESULTS.csv',
         '展示Seen/Unseen取舍与内验证选参位置。','正式C4低于Z0 H；gamma=.4诊断点有更高H但仍未满足U80%阈值；C3/C4相近。',
         '不能用诊断点事后替代C4；不能声称整个简单融合族不可能改善H。需要未来独立验证校准稳定性。'),
        ('figure03_mixed_coverage','Mixed Seen/Unseen/双命中覆盖','MIXED_SAMPLE_COVERAGE.csv; FUSION_RESULTS.csv',
         '检验Hit-any是否掩盖混合标签遗漏。','C4双命中0，Z0为4.14%；C4的Seen覆盖提高没有产生两组联合覆盖。',
         '将Mixed双命中作为完整识别的必要诊断，而不是仅汇报总体命中。'),
        ('figure04_long_tail_class_mrr','按训练支持桶的类等权MRR','LONG_TAIL_TECHNIQUE_RESULTS.csv',
         '防止查询加权指标掩盖频率先验与尾部弱点。','C0在More-shot类等权MRR很高，One-shot为0；C3/C4在One/Few改善而Unseen仍低于Z0。',
         '频率是强对照；泛化论断必须报告类等权与全216Macro-F1。')]
    for name,title,source,purpose,notice,decision in descriptions:
        catalog += [f'## {name}', '', f'- 文件：figures/{name}.pdf / .svg / .png', f'- 内容：{title}。数据源：{source}。',
                    f'- 为什么绘制：{purpose}', f'- 应注意：{notice}', f'- 对判断的影响：{decision}',
                    '- 图注必须保留：DEVELOPMENT_ONLY；216完整候选；975查询/195步骤/7场景；3-seed SD不是独立样本置信区间；无新增训练。',
                    '- 核查：刻度/零值/分母/视图与表一致；图2统一gamma诊断与正式fold-specific gamma明确区分；图4类等权不冒充查询加权。', '']
    catalog += ['视觉QA：评估agent逐张检查4张PNG；root另行逐张检查，均清晰无重叠或截断。此项仅证明可读性，不替代数学评价核验。首次Poppler字体缓存警告通过独立临时字体缓存修复，同一数据同一布局重新导出；最终tradeoff图再次检查。']
    (O/'figure-catalog.md').write_text('\n'.join(catalog)+'\n')
    inputs = ['FUSION_RESULTS.csv','MIXED_SAMPLE_COVERAGE.csv','LONG_TAIL_TECHNIQUE_RESULTS.csv','SEEN_UNSEEN_TRADEOFF.csv',
              'results/PRIMARY_HYPOTHESIS_SUMMARY.csv','results/OVERALL_RESULTS_BY_SEED.csv',
              'results/RANK_FAILURE_PHENOMENA_SUMMARY.csv','results/EVALUATION_AUDIT.json','results/TRADEOFF_EVALUATION_AUDIT.json',
              'results/PIPELINE_LINEAGE_AUDIT.json','FUSION_PARAMETER_REGISTRATION.json',
              'reports/figures_open_vocab.py','reports/build_analysis_bundle.py','open_vocab_evaluation/evaluate_saved.py']
    images = sorted((O/'figures').glob('*'))
    provenance = {'status':'REAL_SAVED_RESULT_ANALYSIS_COMPLETE', 'qualification':'DEVELOPMENT_ONLY',
                  'primary_view':ONE, 'supplementary_view':MULTI, 'source_files':[{'path':name,'sha256':sha(R/name)} for name in inputs],
                  'figures':[{'path':str(p.relative_to(R)), 'bytes':p.stat().st_size,'sha256':sha(p)} for p in images],
                  'new_training_updates':0,'new_GPU_calls':0,'new_LLM_calls':0,
                  'uncertainty':'seed_SD_computational_variation_and_delete_one_scene_descriptive_range; no_CI_or_pvalues',
                  'pre_prediction_reference_preflight_disclosure':audit['pre_prediction_reference_preflight_disclosure'],
                  'pipeline_audit_status':pipeline['status'],
                  'visual_QA':{'four_figures_inspected_by_evaluation_agent':True,'four_figures_inspected_by_root':True,
                               'root_qa_note':'Legible; no overlapping or clipped content; no new mathematical validation implied',
                               'fontconfig_warning_resolved_with_temporary_cache':True,'final_tradeoff_png_rechecked':True}}
    (O/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':provenance['status'],'figures':len(images),'bundle':str(O)}))


if __name__=='__main__':
    main()
