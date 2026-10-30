"""Two descriptive scientific figures; measured inputs only, no neural forward."""
import csv
import os
import subprocess
from pathlib import Path
from reportlab.graphics.shapes import Drawing,String,Line,Rect
from reportlab.graphics import renderPDF,renderSVG
from reportlab.lib import colors
ROOT=Path(__file__).resolve().parents[1];FIG=ROOT/'analysis/figures';FIG.mkdir(exist_ok=True)
blue=colors.HexColor('#245B78');orange=colors.HexColor('#C8833B');gray=colors.HexColor('#DDE3E8')
def text(d,x,y,s,size=10,bold=False):
    d.add(String(x,y,s,fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,fillColor=colors.HexColor('#263443')))
def axes(d,x,y,w,h,maximum):
    for j in range(5):
        py=y+j*h/4;d.add(Line(x,py,x+w,py,strokeColor=gray,strokeWidth=.6));text(d,x-28,py-3,f'{maximum*j/4:g}',9)
def save(d,name):
    renderPDF.drawToFile(d,str(FIG/(name+'.pdf')));renderSVG.drawToFile(d,str(FIG/(name+'.svg')))
    cache=FIG/'.font-cache';cache.mkdir(exist_ok=True)
    fc=FIG/'fontconfig.xml';fc.write_text(f'<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd"><fontconfig><dir>/System/Library/Fonts</dir><dir>/Library/Fonts</dir><cachedir>{cache}</cachedir></fontconfig>')
    with (FIG/(name+'.render.log')).open('w') as log:
        p=subprocess.run(['pdftoppm','-png','-singlefile','-scale-to','1600',str(FIG/(name+'.pdf')),str(FIG/name)],
            env={**os.environ,'FONTCONFIG_FILE':str(fc)},stdout=log,stderr=log,timeout=45)
        assert p.returncode==0

rows=[r for r in csv.DictReader((ROOT/'results/NEURAL_CANDIDATE_DIAGNOSTICS.csv').open()) if r['pool']=='embedding']
d=Drawing(900,460)
text(d,35,425,'Larger candidate pools: better recall, worse reranking',19,True)
text(d,35,400,'Saved GTE Cross-Encoder scores; E1 native-prefix candidate source. No new model calls.',10)
x,y,w,h=80,120,740,235;axes(d,x,y,w,h,100)
for i,r in enumerate(rows):
    center=x+w*(i+.5)/3
    for j,(key,col) in enumerate([('candidate_hit',blue),('top10_accuracy',orange)]):
        value=float(r[key])*100;bx=center-48+j*50
        d.add(Rect(bx,y,40,h*value/100,fillColor=col,strokeColor=None));text(d,bx,y+h*value/100+9,f'{value:.2f}%',11)
    text(d,center-14,y-22,'K='+r['K'],11)
for i,(label,col) in enumerate([('Candidate Hit@K',blue),('Final Top-10',orange)]):
    bx=85+i*230;d.add(Rect(bx,64,12,12,fillColor=col,strokeColor=None));text(d,bx+18,65,label,11)
text(d,40,28,'975 exposed queries / 195 steps / 7 dependent scenarios; descriptive proportions, no population error bars.',10)
save(d,'figure01_candidate_competition')

metrics=list(csv.DictReader((ROOT/'MECHANISM_BASELINE_RESULTS.csv').open()))
views=['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL'];names=['RAW','LITERAL','+RELATIONS','RAW+LITERAL']
d=Drawing(1000,640)
text(d,35,605,'Mechanism representation: sensitivity to input budget',19,True)
text(d,35,582,'Top-10 (%) with fixed K2 knowledge, 216 candidates; same native observation within each budget protocol.',10)
for ix,(protocol,alg) in enumerate([('BYTE','char'),('BYTE','bm25'),('FEATURE','char'),('FEATURE','bm25')]):
    col=ix%2;row=ix//2;x=65+col*490;y=355-row*235;w=405;h=150
    title=('UTF8 byte caps' if protocol=='BYTE' else 'Actual CPU feature caps')+' / '+alg.upper()
    text(d,x,y+h+18,title,12,True);axes(d,x,y,w,h,20)
    for j,v in enumerate(views):
        r=next(r for r in metrics if r['protocol']==protocol and r['algorithm']==alg and r['input_view']==v and r['knowledge']=='K2_DESCRIPTION_16_1')
        value=float(r['top10_accuracy'])*100;bx=x+j*w/4+25
        d.add(Rect(bx,y,48,h*value/20,fillColor=blue if j==0 else orange,strokeColor=None));text(d,bx,y+h*value/20+6,f'{value:.2f}',10)
        text(d,bx-9,y-18,names[j],8)
text(d,35,58,'Feature units: character 3/4/5-gram occurrences and BM25 word tokens; these are NOT GTE tokens.',10)
text(d,35,38,'Relation markers have no BM25 knowledge postings. A zero delta does not test semantic relation reasoning.',10)
text(d,35,18,'Deterministic CPU runs; exposed development data only. No new neural representation scores are plotted.',10)
save(d,'figure02_budget_sensitivity')
print('Rendered two PDF/SVG/PNG figures')
