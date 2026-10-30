"""Scientific figures from actual frozen saved metrics; no selection or training."""
import csv
import os
import subprocess
import tempfile
from pathlib import Path

from reportlab.graphics import renderPDF, renderSVG
from reportlab.graphics.shapes import Circle, Drawing, Line, PolyLine, Rect, String
from reportlab.lib.colors import HexColor, white

R = Path(__file__).resolve().parents[1]
O = R / 'reports/analysis-output/figures'
O.mkdir(parents=True, exist_ok=True)
ONE, MULTI = 'ONE_VIEW_PER_STEP', 'MULTI_VIEW_AUGMENTATION'
COL = {'Z0': '#417c6c', 'S0': '#315d8a', 'C0': '#848484', 'C1': '#9a7b46', 'C2': '#9a6fa5',
       'C3': '#d19735', 'C4': '#c64d3d', 'C5': '#4e8a9a', 'P2': '#6a7399', 'C6_B4': '#777099', 'C6_B5': '#6d8894'}
_font_tmp = tempfile.TemporaryDirectory(prefix='r3-open-vocab-fonts-')
_font_config = Path(_font_tmp.name) / 'fonts.conf'
_font_config.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig>'
                        '<dir>/System/Library/Fonts</dir><dir>/Library/Fonts</dir>'
                        '<cachedir>' + _font_tmp.name + '/cache</cachedir></fontconfig>')


def read(name):
    with (R / name).open() as handle:
        return list(csv.DictReader(handle))


def num(row, key):
    return float(row[key])


def text(d, x, y, value, size=10, color='#263544', anchor='start', bold=False):
    d.add(String(x, y, value, fontSize=size, fillColor=HexColor(color), textAnchor=anchor,
                 fontName='Helvetica-Bold' if bold else 'Helvetica'))


def base(title, subtitle, width=1260, height=600):
    d = Drawing(width, height)
    d.add(Rect(0, 0, width, height, fillColor=white, strokeColor=None))
    text(d, 42, height - 35, title, 18, bold=True)
    text(d, 42, height - 58, subtitle, 10)
    return d


def export(d, name):
    pdf = O / (name + '.pdf')
    renderPDF.drawToFile(d, str(pdf))
    renderSVG.drawToFile(d, str(O / (name + '.svg')))
    run = subprocess.run(['pdftoppm', '-r', '100', '-png', '-singlefile', str(pdf), str(O / name)],
                         env={**os.environ, 'FONTCONFIG_FILE': str(_font_config)},
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if run.returncode:
        raise RuntimeError(run.stderr.decode(errors='replace')[-2000:])


def herror(d, x, y, mean, sd, width, cap, color='#243443'):
    left, right = x + width * max(0, mean - sd) / cap, x + width * (mean + sd) / cap
    d.add(Line(left, y, right, y, strokeColor=HexColor(color), strokeWidth=.7))
    for xx in [left, right]:
        d.add(Line(xx, y - 3, xx, y + 3, strokeColor=HexColor(color), strokeWidth=.7))


def main():
    rows = read('FUSION_RESULTS.csv')
    result = {(r['method'], r['view_id']): r for r in rows}
    methods = ['Z0', 'S0', 'C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'P2', 'C6_B4', 'C6_B5']
    labels = {'Z0': 'Z0  Frozen GTE', 'S0': 'S0  B3 classifier', 'C0': 'C0  Frequency only',
              'C1': 'C1  Seen bias', 'C2': 'C2  RRF', 'C3': 'C3  Score fusion',
              'C4': 'C4  Residual + bias', 'C5': 'C5  GTE + prior', 'P2': 'P2  B3 prior correction',
              'C6_B4': 'C6  B4 description head', 'C6_B5': 'C6  B5 contrastive head'}
    d = base('Supervised accuracy and unseen ranking remain in tension',
             'ONE view; actual query-weighted metrics from saved 216-candidate predictions; bars are 3-seed means with seed SD.', height=620)
    panel = [(200, 'mrr', 'Overall MRR@10', .23, '#3b8090'),
             (550, 'seen_target_mrr', 'Seen-target MRR@10', .32, '#315d8a'),
             (900, 'unseen_target_mrr', 'Unseen-target MRR@10', .05, '#c7823c')]
    y0, step, width = 498, 32, 260
    for x, metric, title, cap, color in panel:
        text(d, x, 530, title, 12, bold=True)
        for j in range(5):
            xx = x + width * j / 4
            d.add(Line(xx, 160, xx, 512, strokeColor=HexColor('#e3e8eb'), strokeWidth=.5))
            text(d, xx, 146, f'{cap*j/4:.3f}', 8, anchor='middle')
        for i, method in enumerate(methods):
            row = result[method, ONE]
            y = y0 - i * step
            value, sd = num(row, metric), num(row, metric + '_seed_SD')
            if method == 'C4':
                d.add(Rect(x, y - 11, width + 70, 24, fillColor=HexColor('#fcf1ee'), strokeColor=None))
            d.add(Rect(x, y - 7, width * value / cap, 14, fillColor=HexColor(color), strokeColor=None))
            herror(d, x, y, value, sd, width, cap)
            text(d, x + width * (value + sd) / cap + 5, y - 3, f'{value:.4f}', 9, bold=method == 'C4')
    for i, method in enumerate(methods):
        text(d, 42, y0 - i * step - 4, labels[method], 10, bold=method in ['C4', 'S0', 'Z0'])
    text(d, 42, 105, 'C4 restores unseen MRR above S0, retaining 59.3% of S0 seen MRR and 51.8% of Z0 unseen MRR.', 12, bold=True)
    text(d, 42, 79, 'Z0/C0/C1/C5 are deterministic repetitions for pairing; seed SD is not an independent-attack confidence interval.', 9)
    text(d, 42, 59, '7 exposed scenarios / 195 logical steps / 975 queries per condition. Seen targets: 670; unseen targets: 450, including 145 mixed queries.', 9)
    text(d, 42, 39, 'Candidate rankings are never filtered by Gold. No new model training, GPU forward, or LLM call.', 9)
    export(d, 'figure01_main_seen_unseen')

    tradeoff = read('SEEN_UNSEEN_TRADEOFF.csv')
    d = base('C4 bias sweeps expose a tradeoff that validation selection does not fully recover',
             'Each sweep holds the internally selected lambda for each fold/seed/view and changes only the preregistered gamma.', height=650)
    for column, view in enumerate([ONE, MULTI]):
        x, y, w, h = 85 + column * 610, 170, 500, 355
        text(d, x, 544, 'ONE (primary)' if view == ONE else 'MULTI (supplementary)', 13, bold=True)
        for j in range(7):
            xx = x + w * j / 6
            d.add(Line(xx, y, xx, y + h, strokeColor=HexColor('#e2e7ec'), strokeWidth=.5))
            text(d, xx, y - 18, f'{.33*j/6:.3f}', 8, anchor='middle')
        for j in range(6):
            yy = y + h * j / 5
            d.add(Line(x, yy, x + w, yy, strokeColor=HexColor('#e2e7ec'), strokeWidth=.5))
            text(d, x - 8, yy - 3, f'{.05*j/5:.3f}', 8, anchor='end')
        text(d, x + w / 2, y - 40, 'Seen-target MRR@10', 11, anchor='middle')
        text(d, x, y + h + 4, 'Unseen-target MRR@10', 9)
        sweep = sorted([r for r in tradeoff if r['view_id'] == view], key=lambda r: num(r, 'gamma'))
        points = []
        for row in sweep:
            points.extend([x + w * num(row, 'seen_target_mrr') / .33, y + h * num(row, 'unseen_target_mrr') / .05])
        d.add(PolyLine(points, strokeColor=HexColor('#805c9a'), strokeWidth=1.5, strokeDashArray=[4, 3]))
        for j, row in enumerate(sweep):
            xx, yy = points[2*j:2*j+2]
            d.add(Circle(xx, yy, 3.5, fillColor=white, strokeColor=HexColor('#805c9a'), strokeWidth=1.4))
            sx = w * num(row, 'seen_target_mrr_seed_SD') / .33
            sy = h * num(row, 'unseen_target_mrr_seed_SD') / .05
            d.add(Line(xx-sx, yy, xx+sx, yy, strokeColor=HexColor('#805c9a'), strokeWidth=.6))
            d.add(Line(xx, yy-sy, xx, yy+sy, strokeColor=HexColor('#805c9a'), strokeWidth=.6))
            offset = [(14, 8), (12, 15), (-41, 7), (-45, 7)][j]
            text(d, xx + offset[0], yy + offset[1], f'g={num(row,"gamma"):g}', 9, '#805c9a')
        offsets = {'Z0': (9, 7), 'S0': (-28, 12), 'C2': (9, -14), 'C3': (15, -23), 'C4': (-51, -16)}
        for method in ['Z0', 'S0', 'C2', 'C3', 'C4']:
            row = result[method, view]
            xx, yy = x + w * num(row, 'seen_target_mrr') / .33, y + h * num(row, 'unseen_target_mrr') / .05
            size = 5 if method == 'C4' else 4
            d.add(Rect(xx-size, yy-size, 2*size, 2*size, fillColor=HexColor(COL[method]), strokeColor=white, strokeWidth=.6))
            dx, dy = offsets[method]
            d.add(Line(xx, yy, xx + dx, yy + dy + 3, strokeColor=HexColor(COL[method]), strokeWidth=.5))
            text(d, xx + dx, yy + dy, method, 10, COL[method], bold=method == 'C4')
    text(d, 42, 91, 'Square markers: registered selected methods. Hollow circles: fixed-gamma outer diagnostic; NOT used to replace selected C4.', 10, bold=True)
    text(d, 42, 66, 'ONE gamma=0.4 gives H=0.0532 (Z0: 0.0495), but retains only 72.5% of Z0 unseen MRR; the registered 80% criterion is still unmet.', 10)
    text(d, 42, 44, 'Formal C4 uses fold-specific internally chosen gamma. Sweep bars show 3-seed SD; no post-hoc selection or AUC; all results are development only.', 9)
    export(d, 'figure02_seen_unseen_tradeoff')

    d = base('Mixed-label coverage: recovering any unseen query does not recover both label groups',
             'ONE view; 145 mixed queries (29 logical steps). Hit rates use the same unfiltered 216-class ranking and Top10.', height=560)
    selected = ['Z0', 'S0', 'C0', 'C2', 'C3', 'C4', 'C5']
    x, y, w, h, cap = 85, 140, 1080, 300, .75
    measures = [('mixed_seen_hit10', 'Seen Gold hit', '#315d8a'), ('mixed_unseen_hit10', 'Unseen Gold hit', '#c7823c'),
                ('mixed_both_hit10', 'Both groups hit', '#417c6c')]
    for j in range(6):
        yy = y + h*j/5
        d.add(Line(x, yy, x+w, yy, strokeColor=HexColor('#e2e7ec'), strokeWidth=.5))
        text(d, x-10, yy-3, f'{100*cap*j/5:.0f}%', 9, anchor='end')
    for j, (_, label, color) in enumerate(measures):
        text(d, 85+j*340, 467, label, 11, color, bold=True)
    step, bw = w/len(selected), 34
    for i, method in enumerate(selected):
        row = result[method, ONE]
        cx = x + (i+.5)*step
        for j, (metric, _, color) in enumerate(measures):
            value, sd = num(row, metric), num(row, metric+'_seed_SD')
            xx = cx+(j-1.5)*bw
            d.add(Rect(xx, y, bw-3, max(.6,h*value/cap), fillColor=HexColor(color), strokeColor=None))
            ey = y+h*(value+sd)/cap
            d.add(Line(xx+15, y+h*max(0,value-sd)/cap, xx+15, ey, strokeWidth=.7))
            text(d, xx+15, ey+7, f'{value*100:.1f}%', 8, anchor='middle')
        text(d, cx, y-24, method, 12, anchor='middle', bold=method=='C4')
    text(d, 42, 89, 'C4: Seen hit 56.6%, Unseen hit 3.45%, simultaneous hit 0%. Z0 simultaneous hit: 4.14%. Zero bars are shown explicitly.', 11, bold=True)
    text(d, 42, 61, 'Groups refer to target Gold coverage, not filtered candidate lists. Hit-any can rise while one target group remains missing.', 10)
    text(d, 42, 39, 'Three-seed SD shown where nonzero. Query replicates and seeds are dependent; no significance claim.', 9)
    export(d, 'figure03_mixed_coverage')

    tail = {(r['method'],r['view_id'],r['stratum']):r for r in read('LONG_TAIL_TECHNIQUE_RESULTS.csv')}
    d = base('Training-frequency gains concentrate on well-supported classes',
             'ONE view; class-macro MRR over observed (fold, technique) pairs, giving each pair equal weight.', height=560)
    selected = ['Z0','S0','C0','C3','C4']
    buckets = [('SUPPORT_0','Unseen: 0',58),('SUPPORT_1','One-shot: 1',21),('SUPPORT_2_4','Few-shot: 2-4',37),('SUPPORT_GE5','More-shot: >=5',17)]
    x,y,w,h,cap = 85,140,1080,300,.5
    for j in range(6):
        yy=y+h*j/5
        d.add(Line(x,yy,x+w,yy,strokeColor=HexColor('#e2e7ec'),strokeWidth=.5))
        text(d,x-10,yy-3,f'{cap*j/5:.1f}',9,anchor='end')
    for j,method in enumerate(selected):
        text(d,85+j*210,467,method,11,COL[method],bold=True)
    step,bw=w/4,37
    for i,(b,label,npairs) in enumerate(buckets):
        cx=x+(i+.5)*step
        for j,method in enumerate(selected):
            row=tail[method,ONE,b]
            value,sd=num(row,'class_macro_mrr'),num(row,'class_macro_mrr_seed_SD')
            xx=cx+(j-2.5)*bw
            d.add(Rect(xx,y,bw-3,max(.6,h*value/cap),fillColor=HexColor(COL[method]),strokeColor=None))
            ey=y+h*(value+sd)/cap
            d.add(Line(xx+17,y+h*max(0,value-sd)/cap,xx+17,ey,strokeWidth=.6))
            text(d,xx+17,ey+6,f'{value:.3f}',8,anchor='middle')
        text(d,cx,y-22,label,11,anchor='middle')
        text(d,cx,y-38,f'{npairs} observed fold-technique pairs',8,anchor='middle')
    text(d,42,75,'C0 frequency-only MRR is strong overall, but its one-shot class MRR is 0; high support drives its ranking gains.',11,bold=True)
    text(d,42,53,'Support counts unique training logical steps; five sampled queries never count as five supports. Buckets may differ across folds.',9)
    text(d,42,33,'Bars: 3-seed means with seed SD. Classes without heldout positives have NA class MRR; all216 remain in Macro-F1 evaluation.',9)
    export(d,'figure04_long_tail_class_mrr')
    print(O)


if __name__=='__main__':
    main()
