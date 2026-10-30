"""Build a reference-first gate and a conditional design, never a method run."""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

R = Path(__file__).resolve().parents[1]
B = R.parent


def read(n):
    return json.loads((R / n).read_text())


def dump(n, x):
    (R / n).write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')


def write(n, s):
    (R / n).write_text(s.strip() + '\n')


def main():
    audit = read('audit/ASSET_AUDIT_SUMMARY.json')
    c = audit['case_counts']
    parity = audit['input_parity']
    history = read('audit/HISTORICAL_RESULT_SOURCE_AUDIT.json')
    decision = 'GO_AFTER_REFERENCE_QUALIFICATION'
    status = 'COMPLETED_METHOD_GATE'
    hypothesis = {
        'hypothesis_id': 'H1_CONDITIONAL_BOUND_EVIDENCE_RANKING',
        'hypothesis_statement': '仅在独立参考已确认同一冻结输入含目标技术及相近候选的区分性证据后，候选必要条件与同主体/对象/时间事实绑定的校验残差，能否在全216候选、相同输入和公开知识预算下，相对冻结GTE、最强全候选词法及C4提高Unseen排序，同时满足Seen损失上限？',
        'admission_status': 'NOT_ADMITTED_CONDITIONAL_DESIGN_ONLY',
        'mechanism': {
            'input': 'all216 candidate public definitions and identical frozen query;no authorGold,human answers,AI review labels,scenario IDs or predicted test labels',
            'verifier': 'not implemented;future deterministic frozen checker on source-bound literal facts;at most8 public-definition conditions/candidate;cannot infer missing actions or purpose',
            'binding': 'a support/contradiction must bind same subject,object,time and action/result role;no association from filename or co-occurrence alone',
            'condition_value': {'SUPPORTED': 1.0, 'PARTIALLY_SUPPORTED': 0.5, 'CONTRADICTED': -1.0, 'NOT_ESTABLISHED': 0.0, 'NOT_EVALUABLE': 0.0},
            'candidate_residual': 'arithmetic mean across fixed necessary conditions;unknown contributes0,not counterevidence;empty condition list=>residual0',
            'score': 'saved/future matched-protocol C4 score +0.1*candidate_residual;lambda0.1fixed;no fitting or grid',
            'tie': 'descending score then technique ID ascending',
            'coverage': 'score all216;not merely rerank originalTop10;new condition text may not add information beyond shared public knowledge'},
        'expected_effect': 'conditional testable improvement from evidence binding,not from expanded pool,more tokens,Gold routing or restoring old GTE ranks',
        'expected_failure_modes': ['no independently confirmed discriminating evidence', 'deterministic checker cannot reliably bind facts or cover definition predicates',
            'necessary condition semantics outside model-visible knowledge scope', 'same gain reproduced by lexical baseline or unbound ablation',
            'Unseen benefit paired with Seen loss', 'gain only on exposed development data'],
        'strongest_baselines': ['Z0 frozen GTE','full216 BM25','full216 CharacterNgramTFIDF','matched word TFIDF',
            'B3/S0 closed-set supervised baseline with true missing Unseen','C4','C3','C0 training-only prior'],
        'required_reference': ['independent two-reviewer plus arbitration visible-evidence reference',
            'verified target definition/parent-child scope', 'candidate-distinction adjudication without rankings',
            'pre-outcome cohort and eligibility freeze', 'qualified independent execution/script/source test lineage'],
        'required_inputs': ['same frozen query bytes and public candidate documents for all methods',
            'train-only Seen/support mask', 'frozen GTE/B3/C4 versions and train normalization',
            'registered deterministic verifier version and traceable conditions;currentlyNOT_SELECTED_NOT_IMPLEMENTED'],
        'primary_metric': ['Unseen-target MRR@10','Unseen-target Top-10 Hit Rate'],
        'secondary_metrics': ['overall MRR@10','overall Top10','Top1','Top5','Precision@5','Recall@5','Recall@10',
            'Seen MRR@10','Seen Top10','Mixed Seen/Unseen/both hit','eligibility and UNKNOWN coverage','latency and compute'],
        'success_criterion': {'Unseen_MRR10_absolute_gain_vs_each_required_strong_baseline_at_least': 0.01,
            'Unseen_Top10_absolute_gain_vs_each_required_strong_baseline_at_least': 0.02,
            'Seen_MRR10_absolute_loss_vs_each_required_strong_baseline_at_most': 0.005,
            'Seen_Top10_absolute_loss_vs_each_required_strong_baseline_at_most': 0.01,
            'interpretation': 'joint operational margins proposed before any new test outcome;not universal scientific constants;no posthoc relaxation'},
        'falsification_criterion': ['after qualified evaluation,any primary gain/Seen retention margin fails',
            'simple matched baseline or no-binding ablation reproduces all gains',
            'gain disappears with equalized candidates,input bytes,knowledge and budget',
            'effect occurs only on previously exposed384/P0',
            'only wording or UNKNOWN rate changes without additional independently verifiable correct rankings'],
        'not_testable_conditions_not_to_be_misreported_as_empirical_falsification': ['independent reference unavailable',
            'independent test unavailable','verifier version/sample-size justification/fair baseline parity not frozen'],
        'current_evidence': {'historical_source': str(R / 'audit/HISTORICAL_RESULT_SOURCE_AUDIT.json'),
            'historical_order_failure': '349 frozen within-Unseen order misses;cause unresolved',
            'AI_related_clues_queries': c['AI_flag_related_direct_or_partial_queries'],
            'AI_any_direct_clues_queries': c['AI_flag_any_direct_queries'],
            'independently_confirmed_discriminating_cases': 'NOT_AVAILABLE',
            'evidence_grade': 'historical numeric/source audit plus nonindependent AI clues;not independent semantic confirmation'},
        'missing_evidence': ['independent semantic reference and candidate distinction', 'legitimate unseen independent test',
            'matched raw/knowledge budgets and baseline outputs on qualified evaluation',
            'validated frozen checker,public-condition coverage and independent sample-size/precision justification'],
        'comparison_to_prior_methods': {'GTE': 'adds explicit condition-to-fact binding residual rather than another text similarity view',
            'B3_C4': 'keeps their original supervised/fusion scores;no new head or recalibration;residual must show increment over C4 andC3',
            'contrastive_hard_negatives': 'no encoder training,hard-negative mining or new geometry adaptation in the conditional design',
            'EvidenceLineFusion': 'requires same-entity/event binding and condition states,not line lexical overlap/concentration weighting',
            'mechanism_cards': 'must verify condition predicates and scope against independent reference;rendering a new card alone is not sufficient',
            'Agent': 'no adaptive query,new logs,roles,reflection or model-agent calls',
            'novelty': 'difference is an unimplemented candidate mechanism,not established novelty or contribution;current local audit cannot establish literature novelty'},
        'go_no_go_status': decision,
        'experiment_permission': False}
    register = {'task': 'R3_METHOD_HYPOTHESIS_GATE01', 'registered_utc': datetime.now(timezone.utc).isoformat(),
        'primary_hypothesis_count': 1, 'primary_hypothesis': hypothesis,
        'alternative_directions': [
            {'direction': 'retain Unseen order in fusion', 'status': 'NOT_PRIMARY_ALREADY_DIAGNOSED',
             'reason': '32 historical losses restored by removing seen-supervision correction;restoringGTE is not novel gain and cannot repair349 internal-order misses'},
            {'direction': 'label/input/taxonomy alignment', 'status': 'REFERENCE_QUALIFICATION_WORK_NOT_SECOND_ALGORITHM',
             'reason': '34 AI scope clues and strong input/document parity differences justify audit,not confirmed label errors or a new method'},
            {'direction': 'do not develop algorithm', 'status': 'FALLBACK_IF_REFERENCE_OR_TEST_GATE_FAILS',
             'reason': 'if discriminating failures cannot be independently established,retireH1;do not add complexity'}],
        'final_decision': decision, 'execution_status': status,
        'method_experiment_admitted': False, 'new_method_implemented': False, 'experiment_executed': False,
        'stage8_reference_stop_rule': 'same single decisionGO_AFTER_REFERENCE_QUALIFICATION;not permission to obtain new data or contact reviewers'}
    dump('METHOD_HYPOTHESIS_REGISTER.json', register)

    write('REFERENCE_REQUIREMENTS.md', f'''
# 独立语义参考最低合同 v1（仅设计，未招募、未标注）

当前状态：**INDEPENDENT_SEMANTIC_REFERENCE_NOT_AVAILABLE**；**INDEPENDENT_TEST_NOT_AVAILABLE**。本轮核验的旧30例人审表30项均PENDING，384预审均为非独立AI结果。正式参考不能由H1校验器或重复运行同一AI审查器生成。

## 四类信息必须分开保存

1. 作者标签：原始sample_id、原标签、父化规则、来源版本/hash；仅表示作者的步骤/执行标注。
2. 可见行为：冻结输入逐字文本/hash、原生日志ID（未提供则null）、本轮派生定位符及其性质、主体/对象/时间/动作/结果的实际文字；不从标签补事实。
3. 人工语义充分性：两位独立审查者针对每个技术/条件的状态、引用、范围和理由；不与作者标签等同。
4. 完整攻击目标/意图真值：需要独立执行记录或其他合格参考；当前NOT_AVAILABLE，不由前三类替代。本合同默认只认证当前视图的行为证据，不认证完整意图。

## 预测隔离与审查流程

包制作人员可做来源整理，但不能充当唯一独立语义裁定者。方法开发者、H1校验器输出和当前AI标签不得成为参考来源。

第一遍只给中性查询ID、当前合法日志和来源/覆盖信息，先记录事实与事件绑定，不给任何模型分数、TopK、历史错误解释或AI判断。第二遍给不可改写的冻结技术定义和父子范围合同；作者目标标签仅作为待审主张单列。公开216候选词表及定义全部可访问，候选以预先固定的中性顺序呈现，不标注哪项来自哪个模型或排第几。相近技术按公开分类关系预先确定；不得仅由被评价方法挑选容易的竞争者。

Top10对比的原先合同冲突在未来参考中采用“模型来源/分数/顺序不展示”的对照包解决；若完整候选适用性仍未检查，则记录仅检查的范围，不声称排除了全部竞争技术。任何预测来源候选的纳入方式须由独立包制作者预先封存并披露选择依赖，不能被称为严格模型无关参考。

每位审查者单独工作，先锁定意见再看分歧；至少两位具备日志/ATT&CK解释能力的真人，以真实匿名ID和资质声明登记。分歧由未参与首轮的第三位仲裁者处理，保留两份原意见、分歧点、仲裁依据和未决状态。记录审查者是否接触模型排名、作者标签、旧AI结果、何时接触；已有曝光不能通过换ID恢复盲审资格。必要时改由未曝光者重审；无此人则保留有限资格。

## 每个条件的必填合同

case_id、原query与hash、技术ID/名称/原文与hash、定义适用层级；核心动作、对象、必要前提、主体/资产、必需状态变化/结果、相近技术的区分条件；条件是必要、可选、举例还是当前无法定义；审查者ID/时间/曝光；状态、支持引用、反证引用、缺失信息、范围、理由；分歧与仲裁记录；最终参考资格与适用范围。

状态固定：SUPPORTED、PARTIALLY_SUPPORTED、CONTRADICTED、NOT_ESTABLISHED、NOT_EVALUABLE。没有显示必要字段时另记NOT_OBSERVABLE_IN_CURRENT_VIEW的覆盖原因，并保持非反证。CONTRADICTED必须引用同主体、对象、时间及命题的真实相反事实；没有证据、UNKNOWN、单一syscall失败均不能代替。

引用必须能在同一查询的合法输入找到原文、行/事件位置和hash。派生Fact ID只能定位显示行；原生事件身份未知就保持未知。日志的工具名、文件名、root账号、IDS派生签名和时间戳不能单独填成完整机制或意图。不得为匹配Gold重写必要条件。

## 资格与指标边界

冻结父技术标题与正文子类型不一致时，先核查已有知识生成/映射链及作者标注范围。原标签和原描述保持不变；如未来独立审计需要新参考版本，必须在新预测之前另行冻结版本，保留原合同并报告双版本敏感性，不能反向把失败改为成功。

QUALIFIED_FOR_VISIBLE_BEHAVIOR_RANKING_ONLY要求：可追溯日志与定义、适用范围明确、必要动作/对象绑定有人工依据、Gold与预先登记竞争解释有可核验区分、分歧完成仲裁、全部引用合法且曝光影响可接受。是否穷尽216候选、是否存在尚未裁定的正标签必须单列。

部分正类Bag、只审目标Gold或未穷尽竞争者的参考，不自动具备完整多标签Precision/Recall资格。只可在明示的声明正类范围报告排序诊断；不得将所有其他候选作为负例。主实验的完整多标签指标需先满足其参考覆盖合同；否则该指标NOT_AVAILABLE或停止该实验，不填0。当前384均未获得上述资格，AI线索可决定人工工作顺序，不能决定方法正确性。

## 最小补齐材料及停止

- 现有384查询的来源、冻结定义/父子范围和独立人工逐条件意见、分歧/仲裁；先核验31个直接线索及34个范围线索，但最终资格须覆盖预登记队列，不能用抽样替代声称全量裁定。
- 独立确认至少存在“可见且可区分但冻结排序失败”的开发案例；若无法确认，H1不进入方法实验。
- 同时包括Seen、Unseen、Mixed及正确/失败控制的参考。384是按GTE漏召回选择的子集，不能单独衡量Seen代价或总体收益。
- 另行冻结未参与前期开发的执行/脚本/来源测试清单、依赖hash、曝光日志、参考封存与访问控制。对既有384重新人审只改善语义参考，不产生独立测试。单来源单正类服务器Bag不构成216类泛化测试，本轮不访问它。
- 对照方法的同查询字节、同公开知识、候选/标签合同及计算预算的版本对齐记录。当前只有30/975查询文本、41/216知识文档逐字一致，尚不具备跨旧协议直接比较资格。

如必要字段不在当前冻结视图，先记录不可评价及最小字段需求；本轮不读未授权原日志、不扩大数据集、不上传Gold、不联系审查者。没有独立参考就保持AI_PRE_REVIEW_NOT_GOLD，并停在**{decision}**。本合同不是下一轮数据/模型操作授权。
''')

    write('MINIMAL_EXPERIMENT_PROTOCOL.md', '''
# 最小可证伪实验设计 v1：尚未准入、不得执行

唯一候选H1_CONDITIONAL_BOUND_EVIDENCE_RANKING。状态DESIGN_ONLY_NOT_EXECUTABLE。当前没有独立确认的可区分失败案例、独立测试、合格参考、可复现校验器版本及样本量依据。本文件不是已准入研究问题或新算法成果。

## 先决门控

按REFERENCE_REQUIREMENTS完成参考；确认至少有“同一合法视图含必要且区分性证据，但冻结GTE排序仍失败”的开发案例。否则撤回H1，不能仅因31条AI直接线索或349条内部排序失败而采用它。新测试须与既有P0、7场景、脚本/执行模板、384诊断及所有方法开发隔离。资格、排除和目标范围在模型结果之前冻结，不按任何方法是否命中挑测试集。

当前384是GTE漏召回条件化子集，不能单独作共同测试或用它宣布Seen/Unseen兼顾。未来测试必须含Seen、Unseen、Mixed、成功和失败类型；独立执行/脚本分组和参考穷尽性须已认证。现有975可继续作为已曝光开发控制，不能换名成TEST。

## 输入、候选与实现合同

全216父候选不变，输出完整排序与来源引用；所有方法共享同一份query字节及同一公开知识文本/hash。建议日志上限2000UTF8字节且实际token≤2048，知识每技术实际token≤1024；同一条选择/截断规则用于全部方法，并保留是否删除了必要语义的资格审计。必要定义超预算或父子范围未认证时不能静默裁剪后当作完整参考；先停在合同核验。

原作者Gold、人审状态、当前AI条件答案、场景/步骤标签和测试Seen/Unseen真值不得进入方法输入。Seen掩码仅来自对应模型合法训练集合，不能按测试Gold路由。公开定义的原子条件最多8个/候选，必须在测试曝光前由公开知识独立固定；新方法不能读取比基线更多的定义内容。

H1条件设计：冻结的确定性校验器对同主体/对象/时间的字面事实标记支持/部分/反证/未知；值1/.5/−1/0，未知不扣分，平均形成候选残差，C4原分数+0.1残差。无条件或全部未知时残差0，保留C4排序。全部216都要检查，不能只重排原Top10以假装修复内部349案例。不得复制旧排序到新方法名下。

**校验器尚未选择、实现、验证或定版**。其版本、支持的日志类型、条件覆盖和错误容忍合同必须先在合格开发参考上完成；此项未冻结前实验仍不可执行。公式本身不是创新证明，也不表示当前已有可执行算法。

## 不可弱化的对照及消融

必需：冻结GTE、全216 BM25、全216字符n-gram TF-IDF、matched word TF-IDF、B3/S0、C4、C3和训练先验C0。保留已存在的来源融合、描述头/对比学习及真实CE历史记录作为既有工作对照；候选20/50/100的CE属于不同候选预算，不得与全216混作同条件结果。

历史词法100个P0条件全部登记；203共同覆盖只可作诊断，不能替代216主对照。历史最优条件是开发集选择，不能声称独立胜者。未来共同视图的条件和词法超参数必须在合法开发参考上选定/冻结；不能只挑旧names-only弱条件。若要沿用engine固定BM25，k1=1.5、b=.75，字符3/4/5-gram，混合.5/.5；这是既有设置，非本轮新方法。

现存GTE/B3/C4分数仅在query/知识hash、划分和模型版本完全一致时复用；任何输入改变都须在另行授权后为所有受影响方法生成真实匹配预测。新方法的基分数、参数选择与B3缺失类规则同C4，Unseen监督分数仍为缺失，不改成有效负常数。

消融预登记：残差置0（C4恒等控制，不作为新增方法实绩）；移除主体/对象/时间绑定但保持其余输入和计算；固定seed17打乱候选—条件配对但保留信息量；共享视图的简单词法残差对照。需要实际运行后才能给数字；本轮不生成合成增益或反事实预测作为结果。

## 冻结指标与评价单位

共同主指标为Unseen-target MRR@10和Top10 Hit，两者必须同时改善；排名始终全216。次指标：总体MRR/Top10、Top1/5、Precision@5、Recall@5/10、Seen MRR/Top10、Mixed任一/Seen/Unseen/双目标命中、完整参考覆盖率、UNKNOWN比例、失败率、延时和资源。

MRR@10取第一个合格正类的截断倒数排名；TopK是至少一个合格目标命中；Precision@5和Recall只在参考覆盖满足合同的集合计算。没有目标或参考不合格填NOT_AVAILABLE，不填0。Seen/Unseen相对每一冻结训练集合；Mixed查询可进入两个目标子集，不相加当独立样本。

保留既有ONE主协议及17/42/73种子，不根据测试选择头。若使用既有7折模型，按每一模型训练掩码计算Seen/Unseen，先在同一测试单位聚合模型条件，再在独立执行/脚本组汇总；7折×3种子不是21个独立测试重复。报告模型条件数和各目标分母。测试没有可靠分组或某目标无足够支持时，停止确认性比较。

五个采样归同逻辑步骤；脚本/执行/来源依赖更高时以最高已认证独立组为分析单位。主表同时报告查询加权与组等权，不把975采样或3种子当IID。若将来满足独立组及样本量要求，可预登记seed1729、5000次独立组配对重采样的不确定区间；当前不计算p值或CI。

## 事前成功、失败和停止线

以下是尚未见新测试结果前提出的工作性边界，不是自然常数：相对每个必需强基线，Unseen MRR@10绝对提升≥.01，Top10绝对提升≥.02；Seen MRR绝对下降≤.005，Seen Top10下降≤.01。B3必须保留在Seen强对照中，不能只相对低Seen的GTE宣布兼顾。联合条件任何一项失败，都不支持本候选的联合收益主张；不能用总体MRR补救。

在资格齐备的实际评价中，与强基线相同、简单对照/去绑定消融复现全部收益、增益仅来自候选覆盖或更多输入、只在曝光开发样本有效、UNKNOWN措辞变化无可验证新增正确排名、Unseen增益伴随超限Seen代价，均视为未支持H1。保留全部失败，不事后改阈值、增权重或扩大候选。

参考不充分、独立测试未准备、定义范围不清或实现未冻结，属于“不可检验/不得执行”，不是已经实验性证伪。此时不报告性能，不通过合成控制填空。需要先有独立参考才可估计差异方差和规划样本量；当前测试查询数、独立组数、功效/精度依据均NOT_AVAILABLE。未补齐前不得把本设计标为可运行的最终预注册。

## 计算上限（未来提案，不是授权）

本轮预算固定0模型调用、0训练、0GPU、0网络、0服务器。未来最小验证提案上限1000个已合格查询、216候选、每候选≤8条件，共≤1728000次确定性条件检查；校验结果跨旧头/种子共享，不重复采集证据。CPU≤2线程，整体wall≤2小时，新增盘≤1GB；不下载、不训练、不新增LLM/Agent。若未来需对新合格测试生成GTE特征，限现有固定权重和一次query/知识编码缓存，GPU0显存≤15%，仍受2小时总上限；这需要新的明确运行授权，不能从本文件推定已经取得。

任何上限先到即停并保存不完整状态，不扩大额度。新参考、测试清单、输入知识hash、最终N/组数与精度依据、所有对照版本及校验器版本缺一，本设计不执行。本轮在设计交付后停止。
''')

    write('GO_NO_GO_DECISION.md', f'''
# 唯一科研决策

**{decision}**。

门控工作已完成，方法实验未准入。H1仅为一个带先决条件的可证伪候选，不能从349条内部排序失败或31条AI直接线索跳到“已证实算法失败”。选择这个流程决策，是因为可以明确规定待检验的增量及其反证，但当前缺少独立参考来判断前提是否成立；它不承诺补参考后必然GO。

已核验{audit['assets_checked']}个资产，路径缺失{len(audit['missing_assets'])}，历史哈希差异{len(audit['hash_mismatches'])}（已知旧报告漂移，未修复）；登记{audit['baseline_audit_rows']}个基线/条件行。全部384条缺少本轮可验证的独立语义参考与独立测试资格；当前主指标合格数为0（行政准入结果），真实可区分案例数仍NOT_AVAILABLE。

次级阻断：152条当前AI视图不足线索、34条范围线索、其他198条以参考缺失为主要阻断；这些主要阻断互斥，全部384仍有共同参考缺失。旧词法与GTE仅30/975查询、41/216知识文档逐字相同，尚不能直接跨协议比较因果效果。测试、强基线预算对齐及实现资格也须补齐。

不是GO_METHOD_EXPERIMENT：独立参考/测试、公平输入与可复现校验器均未就绪。不是把输入或标签错误当作既成主因：AI范围疑问和字节差异并未独立证实错误根因。也不把方向A当作已准入算法问题；只能在参考确认存在可区分失败后再次过门。

若独立审查不能确认同一合法输入里有区分性证据，或者公平简单基线已解决全部候选增量，应撤回H1并停止方法开发。若参考/测试仍不合格，继续保持未准入，不增加Agent、规则复杂度或模型来填未知。

证据等级：历史数值和版本核验为可复查事实；384分类为非独立AI线索；条件残差可能有效是研究假设；当前主要因果根因、真实可评价案例规模及独立泛化均未确认。本轮没有方法实验成功结论。
''')

    write('reports/research-question-card.md', f'''
# Research Question Card — H1_CONDITIONAL_BOUND_EVIDENCE_RANKING

What：在独立确认有区分性证据时，显式条件—事实绑定残差是否对全216排序有独立增量？
Why：349个内部排序失败不能靠只移动Seen候选修复，但具体语义机制未确认；126个AI相关线索可用于参考资格工作。
Who：未来独立日志/ATT&CK审查者提供参考，方法开发者不替代裁定；本轮未联系任何人。
Where/When：现有公开曝光开发资产用于门控；任何正式方法评价须在未来独立、封存且获授权的测试上进行。
How：同输入/知识/候选预算，对比GTE、BM25、字符检索、B3、C4及去绑定消融；固定联合Unseen收益和Seen代价阈值。

Evidence：{R}/audit/HISTORICAL_RESULT_SOURCE_AUDIT.json；{R}/audit/CASE_QUALIFICATION_COUNTS.json。
Missing：独立语义参考、候选区分、测试、预算对齐、校验器版本和样本量依据。
Falsification：达到资格后联合标准失败、简单基线/无绑定消融复现全部增益，或增益只由更多信息解释。
Current decision：{decision}；NOT_ADMITTED_CONDITIONAL_DESIGN_ONLY。
Next minimal action：只补参考资格合同所列材料；本轮不执行采集、人审、训练或模型调用。不生成文献综述/创新提案：没有本轮授权的外部文献核验，不能声称已证明新颖性。
''')

    htable = '\n'.join(f'| {x["method"]} | {float(x["mrr"]):.4f} | {float(x["seen_target_mrr"]):.4f} | {float(x["unseen_target_mrr"]):.4f} |' for x in history['fusion_ONE_three_seed_results'] if x['method'] in {'Z0', 'S0', 'C3', 'C4'})
    miss = audit['hash_mismatches'][0] if audit['hash_mismatches'] else None
    mismatch_text = f'{miss["path"]}；旧期望{miss["expected_sha256"]}，当前{miss["sha256"]}。这是此前已披露的差异，本轮未修复。' if miss else '本轮未发现已登记版本差异。'
    main_report = f'''
---
type: results-report
date: 2026-10-28
experiment_line: open-vocab-method-gate
round: 1
purpose: hypothesis-admission
status: completed_gate_reference_not_qualified
source_artifacts:
  - {R}/audit/ASSET_AUDIT_SUMMARY.json
  - {R}/audit/CASE_QUALIFICATION_COUNTS.json
  - {R}/audit/HISTORICAL_RESULT_SOURCE_AUDIT.json
linked_experiments:
  - {B}/research3_open_vocab_technique_generalization01
linked_results:
  - {R}/CASE_QUALIFICATION_MATRIX.csv
---

# 方法假设准入与最小实验设计

## 执行结论

状态**{status}**，含义是已完成收到范围内的门控审计与条件设计，**没有准入或执行方法实验**。唯一科研决策**{decision}**。当前能定义一个精确可反驳的条件候选，但尚不能将其作为证据充分、可立即实施的新算法问题。

本轮检查现有预测与报告仅为版本/合同/既有结果核验，不重跑模型、不重做384语义预审或历史参数网格。附件止于§7.1，消息从§8接续，中间未提供的部分不补造规则。旧报告哈希漂移按实际记录，其他合法工作继续完成。

## 1. 现有强基线是否已充分登记和核验？

实际清点{audit['assets_checked']}个资产，指定/关联路径缺失{len(audit['missing_assets'])}，历史哈希差异{len(audit['hash_mismatches'])}。主来源为开放词汇、失败诊断和384预审；补充已有强词法、领域对比学习、机制判别、早期LLM/Agent及后续真实语义模型验证。42个216列分数文件哈希已核对，126个所引用B3/B4/B5源Checkpoint仅做hash，未加载或执行；不把此前报告“378已核验”冒充本轮重新核验378个模型。

三类保存导出逐行核对字段、216列/候选集合与B3缺失：GTE2909行、B317454行、融合64350行。没有重新计算模型分数或全套指标。基线审计共{audit['baseline_audit_rows']}行：11个开放词汇方法、100个历史P0词法/来源条件、3个既有方向摘要、14个后续真实Embedding/CE及matched检索条件。既有26项强基线登记另存。两项主要全候选BM25/char原生回执和975条预测逐行核对；其他条件保留历史结果及范围，不声称全部原生预测都在本轮逐项重做复算。

已有全216 BM25 native K2的开发MRR .1055108、Top10 .2369231；字符n-gram native K2为.1293724/.2779487。它们是历史开发条件，不是公平同视图胜者。C0、C3、B3、来源融合、对比/困难负例、真实CE和静态/Agent控制均保留，不用names-only弱条件替代最强现有对照。203共同覆盖不替代216主评价。

后续validation02已真实运行Embedding/Reranker且有3个工程闭环Episode，不能沿用更早任务的“尚无模型运行”状态；旧强基线登记中监督分类未执行的状态也已被后续B3真实训练记录补充。该轮同预算E1 matched word TF-IDF保存MRR .1401302，高于同协议E1 GTE的.1066732；这项词法强对照必须保留，但不能再跨预算与本轮Z0/C4作因果比较。Agent有效配对只有0/1/2例，不能包装为12例完整配对或增益。机制卡片、来源融合、投影/对比、困难负例与校准均已尝试，不能重命名为本轮创新。

因此：主要对照已登记，关键版本和若干原生回执已核验；**公平独立比较资格仍不足**，不是所有基线都已完成新的共同协议评价。

## 2. 历史数字是否同口径？

以下直接来自保存FUSION_RESULTS.csv的ONE、三种子均值，不是新实验：

| 方法 | 总体MRR@10 | Seen-target MRR | Unseen-target MRR |
|---|---:|---:|---:|
{htable}

主协议每条件975查询、195步骤、7场景、216候选；Seen-target670与Unseen-target450重叠145个Mixed。历史ONE重计表三种子都保留34、丢失32、GTEmiss384，miss中内部Unseen排名>10为349、≤10为35。不能把MULTI的35保留/31丢失混成ONE。

32丢失已被旧反事实表定位到Seen监督修正：移除该项恢复32、移除偏置恢复0、恢复GTE恢复32；这是旧诊断，不是本轮新发现或新方法预测。349说明仅移动Seen不能修复冻结内部顺序，不证明语义主干是原因。B3 Unseen缺失是闭集结构，不称为主干遗忘。

分母核对：seed17 ONE的全部450个Unseen目标查询有605个Gold分配；全部missed Gold539中，384个查询全未命中的子集对应520个，另19个missed Gold来自至少命中另一个Gold的查询。384、520、539、605不能互换。

## 3. 384条AI预审能否作为正式语义Gold？

不能。它们是同上下文AI线索，已有预测暴露，Top10比较未执行，原生事件身份/省略记录数未认证；独立人审未提供，30例旧人审表也全PENDING。AI_PRE_REVIEW_NOT_GOLD必须保留。31个直接相关线索不是31个正确预测，34个范围线索不是34个错标，197个任一目标无相关线索不是197个不可识别攻击。

原始单位：384唯一查询、80逻辑步骤、145文本hash、520查询—目标分配、2618条件；不可相互替代或作IID攻击次数。仅用继承字段构建资格表，没有新增语义判断。

## 4. 是否有足够资格案例？

| 项目 | 本轮可报告数量/状态 |
|---|---|
| 原始查询 | 384 |
| AI标记任一直接/部分相关行为 | 126（31直接、95部分；仅线索） |
| 独立确认相关行为 | NOT_AVAILABLE |
| 有合格候选区分依据 | NOT_AVAILABLE |
| 需人工裁定 | 384 |
| 当前不可进入确认性主指标 | 384（行政准入，不是行为不存在） |
| 核验资产中已登记合格独立参考/测试记录 | 各0 |
| 真实具有独立参考/测试资格的查询规模 | NOT_AVAILABLE；未核验不能假定全世界不存在 |

互斥主要阻断：OBSERVATION_INSUFFICIENT152、LABEL_SCOPE_UNRESOLVED34、REFERENCE_MISSING198。前两类是继承AI线索，用于复核优先级；152由顶层“当前视图无相关148+输入不足4”形成，不能当成已证实的数据缺陷。所有384同时有REFERENCE_MISSING、CANDIDATE_FOR_HUMAN_ADJUDICATION和NOT_ELIGIBLE_FOR_CURRENT_HYPOTHESIS，故多标签不能相加。

## 5. 哪个假设最具体、与旧方法有何区别？

唯一条件候选H1_CONDITIONAL_BOUND_EVIDENCE_RANKING：**先由独立参考确认有必要且可区分的证据，再检验同事件绑定的必要条件校验残差是否有超出GTE/强词法/C4的排序增量，并守住Seen代价。** 固定残差分值、.1系数、全216候选、未知不作反证，详见JSON登记。

它尚未准入：当前没有满足前提的独立确认案例，也没有实现/验证/冻结校验器。不能直接采用方向A作为已经成立的算法问题。与旧方法的候选差别是显式同主体/对象/时间条件校验，不是又一次文本render、分数融合、难负例训练或增加查询。此差别是否有独立增量还未知，现有局部资料也不能证明文献新颖性。没有新增算法代码、模型或预测。

只恢复GTE的方向不作主假设；32例已解释且349例不受Seen移动修复。输入/标签/父子映射列为资格工作，不并列开发第二算法。不能确认区分性失败则撤回H1，而不是加模块。

## 6. 需要哪些参考和测试材料？

预测隔离的真人双审、分歧和第三人仲裁；冻结字面输入及原生/派生引用身份；目标定义与父子适用范围；必要/区分条件及明确支持/部分/反证/未建立/不可评价状态；审查者曝光与资质；参考穷尽范围及用途。四类真值——作者标签、日志实际行为、人审充分性、完整攻击意图——分开保存。

重新人工审384只改善参考，不使它们成为独立测试。现有975和P1/P2均已曝光/关联开发；服务器单正类Bag未构成多技术独立测试，本轮不访问。必须另行确认未参与开发的执行/脚本/来源、分组、封存及参考；本轮仅制定要求，不采集或联系审查者。

## 7. 当前是否公平可比？

同名P0和216不足以证明同协议：查询ID及父化标签975/975相同，查询字面只{parity['identical_query_texts']}/975相同，知识文档只{parity['identical_knowledge_documents']}/216相同。GTE冻结查询共{parity['GTE_query_total_UTF8_bytes']}字节、最大{parity['GTE_query_max_UTF8_bytes']}；native词法共{parity['lexical_query_total_UTF8_bytes']}、最大{parity['lexical_query_max_UTF8_bytes']}。GTE知识共{parity['GTE_knowledge_total_UTF8_bytes']}字节，词法{parity['lexical_knowledge_total_UTF8_bytes']}。这些是实际字符串审计，不是预处理致错的因果证明。

后续2048实际Token模型协议有matched词法对照，但也不是本轮Z0的同一2000字节特征协议。未来必须固定共同视图和公开知识，若hash变了就不能沿用旧预测冒充匹配结果；所有受影响对照需在新授权后生成真实预测。当前**尚不具备确认性公平方法比较条件**。

## 8. 唯一决策、证据等级与可证伪标准

**{decision}**：先补参考资格并重新过门，不授予方法运行资格。此选择承认可以写出一个精确的条件检验，不声称前提已经成立或参考补齐必然让方法有效。参考若证明没有区分性失败，或简单基线解释全部可验证增量，则退回停止新方法开发。

历史哈希/字段/保存结果和预算差异是可复查事实；384分类是非独立AI线索；条件残差有效性是待检假设；真实主要失败机制、独立测试规模及算法新颖性暂不可确认。

独立参考/测试及公平实现齐备后，Unseen MRR至少+.01、Top10至少+.02，且Seen MRR损失≤.005、Seen Top10损失≤.01，需同时相对必需强基线满足。任何一项不满足、简单词法或去绑定消融复现全部收益、收益只由更多候选/信息解释、仅在曝光开发有效，均不支持H1。参考不足属于未检验，不能报告为实验性证伪。阈值为事前工作性约束，不是已验证自然标准，不能看新结果后放宽。

## 9. 最小实验与统计设计

这里只生成MINIMAL_EXPERIMENT_PROTOCOL.md：同字节/知识、全216、八项强对照及四项消融，已有ONE/三种子条件保留，组依赖/目标重叠明确，预测与评价分离。相同输入/候选/资源并不意味各方法实际调用数相同；实际开销必须单列，不隐藏额外信息或语义监督。

当前没有实验样本量/独立组数量与精度依据，校验器版本未冻结，协议明确不可执行；不把详细公式或阈值当成已完成准入。没有重算新MRR、准确率、显著性或合成收益。没有科学推断图，行政计数表已完整给出。

## 10. 下一轮启动前必须补齐及停止

先完成独立参考合同及预测隔离方案、明确当前视图/父子范围和真正可区分失败；再取得独立测试资格、同协议强基线/预算、校验器版本和样本量依据。参考限定读现有合法输入；缺字段只列最小需求，不能自动扩大读取、上传Gold、联系别人或再调用模型。

本轮写出门控资产与完整资格矩阵、唯一条件候选、参考合同及最小设计后停止。没有自动训练、调参、校准、GPU或Agent实验。

## 完整性和复现

哈希差异：{mismatch_text}

这是基于旧报告记录的预先存在版本例外，不修改旧文本；运行末对本轮核验资产逐一复核初始hash，报告实际修改数。输入清单及每条字段/来源见ASSET_INVENTORY.csv；脚本只负责文件hash、保存记录schema/计数、继承AI资格映射和报告生成，不实现H1。

完整交付位于{R}。必需10文件以及audit子目录有实际内容；RUN_MANIFEST.json记录输入/输出/代码哈希与实际命令，FINAL_VALIDATION.json独立检查文件、单位、资格、决策一致性。机械门控核验通过不代表方法已有效或正式参考合格。
'''
    write('METHOD_HYPOTHESIS_GATE_REPORT.md', main_report)
    write('reports/analysis-report.md', f'''
# 门控分析记录

唯一门控问题：已有开发排序失败是否具备独立语义参考、公平基线和独立测试，从而允许检验一个必要条件绑定残差假设？

事实依据：{audit['assets_checked']}项实际资产、{audit['baseline_audit_rows']}行历史基线登记、384条资格记录。相关AI线索126，但独立区分数量NOT_AVAILABLE。预算审计确认绝大多数输入和知识文本不同，不能把旧分数差当方法因果增益。

Claim candidate1：当前不具备方法实验准入。来源CASE_QUALIFICATION_MATRIX及来源/预算审计；允许说参考/测试/公平实现缺失，禁止说“所有错误是标签问题”。决定keep。
Claim candidate2：显式条件绑定残差可能改善排序。来源仅历史排序现象和AI线索；允许条件性研究问题，禁止已有效或已有独立确认；下一检查为真人资格合同；决定weaken至NOT_ADMITTED。
Claim candidate3：词法强于GTE或新方法必然需要。不同预算及无独立参考；不能作公平因果比较；决定discard该强表述。

最终{decision}。新方法、训练、统计检验与模型推理均未执行。
''')
    write('reports/stats-appendix.md', '''
# 统计与分母

仅记录既有结果/行政计数。384查询、80逻辑步、145文本、520目标分配、2618AI条件；126是至少一个直接/部分AI线索的查询并集，不是126正确技术或独立攻击。

主要阻断152+34+198=384互斥，多资格标签可重叠。合格主指标准入0由门控规则产生；独立确认行为/可区分案例的实际规模NOT_AVAILABLE，不能将未知填0。既有人审30PENDING是该表中的事实，不能证明其他未核验位置绝无人工参考。

历史ONE三种子MRR只是已保存开发结果，本轮未复算评价；Top10/Seen/Unseen分母保持原协议。未计算新的效应量、置信区间、显著性或假设支持率。实验样本量/独立组数/功效与精度依据尚未具备，不能声称检验有足够统计功效。
''')
    write('reports/figure-catalog.md', '''
# 图件状态

NOT_CREATED：本轮为方法准入和实验设计，没有新实验结果；完整行政计数用表格与CSV。没有声称生成的图件或算法收益图。
''')
    # A real manifest exists before independent validation; it is deliberately
    # unsealed until validation has actually run.
    manifest = {'task_id': 'R3_METHOD_HYPOTHESIS_GATE01', 'run_version': 'v1_reference_first_gate',
        'execution_status': status, 'manifest_phase': 'ANALYSIS_COMPLETE_PENDING_INDEPENDENT_VALIDATION',
        'final_decision': decision, 'experiment_executed': False, 'new_method_implemented': False,
        'new_model_calls': 0, 'new_agent_calls': 0, 'new_training_runs': 0, 'downloads': 0,
        'GPU_tasks': 0, 'server_access': False, 'external_network_access': False,
        'scope': read('protocol/RECEIVED_SCOPE.json'), 'assets_checked': audit['assets_checked'],
        'baseline_conditions_registered': audit['baseline_audit_rows'],
        'reference_status': 'INDEPENDENT_SEMANTIC_REFERENCE_NOT_AVAILABLE',
        'independent_test_status': 'INDEPENDENT_TEST_NOT_AVAILABLE',
        'hypothesis_registered': hypothesis['hypothesis_id'],
        'hypothesis_admission_status': hypothesis['admission_status'],
        'source_snapshot': str(R / 'audit/INPUT_HASH_SNAPSHOT.json'),
        'input_hashes': read('audit/INPUT_HASH_SNAPSHOT.json')['files'],
        'output_hashes': 'PENDING_FINAL_SEAL_NOT_YET_CLAIMED', 'code_hashes': 'PENDING_FINAL_SEAL',
        'actual_commands': [{'command': 'python3 -B research3_method_hypothesis_gate01/code/audit_assets.py', 'status': 'EXECUTED_SUCCESS',
            'note': 'repeated after extending audit to later real-model validation02,not model inference'},
            {'command': 'python3 -B research3_method_hypothesis_gate01/code/build_gate.py', 'status': 'EXECUTING_REPORT_BUILD'}],
        'lookup_failures': ['initial alias research3_technique_strong_baselines_and_generalization02 not present;resolved actual project research3_technique_strong_baselines_generalization02',
            'OPEN_VOCAB_PROTOCOL.json absent;actual frozen contracts GENERALIZED_ZERO_SHOT_PROTOCOL.md and FUSION_PARAMETER_REGISTRATION.json inspected',
            'method/run.py,method/run_baselines.py,METHOD_REGISTRATION.json guesses absent;actual baselines/engine.py and run_matrix.py inspected'],
        'lookup_failure_interpretation': 'failed guessed lookup is not a missing user-required asset;no source recreated',
        'historical_hash_mismatches': audit['hash_mismatches'],
        'stop_after_delivery': True}
    dump('RUN_MANIFEST.json', manifest)
    print(json.dumps({'execution_status': status, 'final_decision': decision,
                      'hypotheses_registered': 1, 'method_experiment_admitted': False,
                      'experiment_executed': False, 'case_rows': c['original_queries']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
