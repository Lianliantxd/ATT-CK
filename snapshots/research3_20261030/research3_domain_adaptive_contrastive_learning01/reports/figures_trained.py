"""Real fixed-protocol training results; seed SD is computational variation only."""
import csv,sys
from pathlib import Path
import numpy as np
from reportlab.graphics.shapes import Drawing,Rect,Line,String,PolyLine
from reportlab.graphics import renderPDF,renderSVG
from reportlab.lib.colors import HexColor,white
R=Path(__file__).resolve().parents[1];O=R/'reports/analysis-output/figures';O.mkdir(exist_ok=True)
COLORS=['#426F93','#CF8B45','#64806E'];MODES=['ONE_VIEW_PER_STEP','MULTI_VIEW_AUGMENTATION']
def read(n):return list(csv.DictReader((R/n).open()))
def base(title,subtitle):
 d=Drawing(1050,430);d.add(Rect(0,0,1050,430,fillColor=white,strokeColor=None));d.add(String(55,402,title,fontSize=15,fontName='Helvetica-Bold'));d.add(String(55,381,subtitle,fontSize=9));return d

def export(d,name):
 renderPDF.drawToFile(d,str(O/(name+'.pdf')));renderSVG.drawToFile(d,str(O/(name+'.svg')))
def foot(d,text):d.add(String(65,24,text,fontSize=8))
def main():
 rr=read('results/OVERALL_RESULTS.csv');m={(r['method'],r['augmentation']):r for r in rr};methods=['B0','B1','B2','B3','B4','B5','B6','B7','B8','B9','B9_CONST'];d=base('Grouped development MRR@10: ordinary linear supervision remains competitive','B0 char; B1 frozen GTE; B2 TFIDF linear; B3 GTE linear; B4 projection BCE; B5 standard contrastive; B6 random; B7 semantic; B8 confusion; B9 reliability; CONST fixed weight')
 x,y,w,h=65,85,950,260;cap=.25
 for j in range(6):
  yy=y+h*j/5;d.add(Line(x,yy,x+w,yy,strokeColor=HexColor('#DEE5E9'),strokeWidth=.5));d.add(String(x-7,yy-3,f'{cap*j/5:.2f}',textAnchor='end',fontSize=9))
 step=w/len(methods);bw=25
 for i,method in enumerate(methods):
  if method in ['B0','B1']:
   v=float(m[method,'SHARED']['mrr']);xx=x+(i+.5)*step-bw/2;d.add(Rect(xx,y,bw,h*v/cap,fillColor=HexColor(COLORS[2]),strokeColor=None));d.add(String(xx+bw/2,y+h*v/cap+5,f'{v:.3f}',fontSize=8,textAnchor='middle'))
  else:
   for j,mode in enumerate(MODES):
    r=m[method,mode];v=float(r['mrr']);sd=float(r['mrr_seed_SD']);xx=x+(i+.5)*step+(j-1)*bw;d.add(Rect(xx,y,bw-2,h*v/cap,fillColor=HexColor(COLORS[j]),strokeColor=None));cx=xx+(bw-2)/2;lo=y+h*(v-sd)/cap;hi=y+h*(v+sd)/cap;d.add(Line(cx,lo,cx,hi,strokeWidth=.7));d.add(Line(cx-3,hi,cx+3,hi,strokeWidth=.7));d.add(String(cx,hi+4,f'{v:.3f}',fontSize=7,textAnchor='middle'))
  d.add(String(x+(i+.5)*step,y-18,'CONST' if method=='B9_CONST' else method,fontSize=10,textAnchor='middle'))
 for j,legend in enumerate(['ONE view: mean +/- seed SD','MULTI view: mean +/- seed SD','Frozen: no training seed']):d.add(String(65+j*310,358,legend,fontSize=10,fillColor=HexColor(COLORS[j])))
 foot(d,'7 exposed scenarios / 195 logical steps / 975 queries per seed. Error bars are 3-seed SD, not generalization confidence intervals.');export(d,'figure04_all_trained_mrr')
 st=read('SEEN_UNSEEN_TECHNIQUE_RESULTS.csv');selected=['B1','B3','B4','B5','B7','B8','B9'];d=base('Training gains largely concentrate on seen techniques','ONE-view protocol; same full216 ranking, target Gold subset restricted. Mixed-label queries appear in both groups.');cap=.32;x,y,w,h=65,85,950,260;step=w/len(selected)
 for j in range(5):
  yy=y+h*j/4;d.add(Line(x,yy,x+w,yy,strokeColor=HexColor('#DEE5E9'),strokeWidth=.5));d.add(String(x-7,yy-3,f'{cap*j/4:.2f}',textAnchor='end',fontSize=9))
 for i,method in enumerate(selected):
  mode='SHARED' if method=='B1' else MODES[0]
  for j,cat in enumerate(['SEEN_GOLD_SUBSET','UNSEEN_GOLD_SUBSET']):
   rows=[r for r in st if r['method']==method and r['augmentation']==mode and r['stratum']==cat];v=sum(float(r['mrr'])*int(r['n_records']) for r in rows)/sum(int(r['n_records']) for r in rows);xx=x+(i+.5)*step+(j-1)*32;d.add(Rect(xx,y,30,h*v/cap,fillColor=HexColor(COLORS[j]),strokeColor=None));d.add(String(xx+15,y+h*v/cap+5,f'{v:.3f}',fontSize=9,textAnchor='middle'))
  d.add(String(x+(i+.5)*step,y-18,method,fontSize=10,textAnchor='middle'))
 d.add(String(65,358,'Seen Gold target MRR',fontSize=10,fillColor=HexColor(COLORS[0])));d.add(String(390,358,'Unseen Gold target MRR',fontSize=10,fillColor=HexColor(COLORS[1])));foot(d,'Seen target:670 queries; unseen target:450 queries;145mixed queries overlap. No candidate or unseen label removed.');export(d,'figure05_trained_seen_unseen')
 primary=read('results/FOUR_PRIMARY_HYPOTHESES.csv');d=base('Reliability weighting does not provide a consistent same-pool increment','B9 minus B8 MRR@10 by held-out scenario; seeds averaged within each scenario. No inferential error bars.');x,y,w,h=65,85,950,260;low=-.016;high=.016;zero=y+h/2
 for value in [-.016,-.008,0,.008,.016]:
  yy=y+h*(value-low)/(high-low);d.add(Line(x,yy,x+w,yy,strokeColor=HexColor('#B6C2CB') if value==0 else HexColor('#DEE5E9'),strokeWidth=1 if value==0 else .5));d.add(String(x-7,yy-3,f'{value:+.3f}',fontSize=9,textAnchor='end'))
 step=w/7
 for i in range(7):
  for j,mode in enumerate(MODES):
   r=next(r for r in primary if r['hypothesis']=='H4' and r['augmentation']==mode and r['scenario']==str(i+1));v=float(r['mrr_delta_seed_mean']);yy=y+h*(v-low)/(high-low);xx=x+(i+.5)*step+(j-1)*30;d.add(Rect(xx,min(zero,yy),28,abs(yy-zero),fillColor=HexColor(COLORS[j]),strokeColor=None));d.add(String(xx+14,yy+(5 if v>=0 else -10),f'{v:+.4f}',fontSize=8,textAnchor='middle'))
  d.add(String(x+(i+.5)*step,y-18,'Scene '+str(i+1),fontSize=10,textAnchor='middle'))
 d.add(String(65,358,'ONE view',fontSize=10,fillColor=HexColor(COLORS[0])));d.add(String(390,358,'MULTI view',fontSize=10,fillColor=HexColor(COLORS[1])));foot(d,'7 exposed scenarios, shared scripts uncertain. Same32candidates and optimization budget; risk weighting is a proxy, not certified negative evidence.');export(d,'figure06_reliability_scene_deltas')
 logs=read('CONTRASTIVE_TRAINING_LOGS.csv');d=base('Actual CPU projection training curves: seed42, ONE view','Each line averages 7 overlapping training folds. Loss definitions differ; levels do not establish cross-method superiority.');x,y,w,h=65,85,950,260;cap=7.
 for i in range(8):
  yy=y+h*i/7;d.add(Line(x,yy,x+w,yy,strokeColor=HexColor('#DEE5E9'),strokeWidth=.5));d.add(String(x-7,yy-3,str(i),textAnchor='end',fontSize=9))
 for j,method in enumerate(['B5','B7','B9']):
  points=[]
  for epoch in [1,*range(10,121,10)]:
   vals=[float(r['loss']) for r in logs if r['method']==method and r['seed']=='42' and r['augmentation']==MODES[0] and int(r['epoch'])==epoch];points.extend([x+w*epoch/120,y+h*np.mean(vals)/cap])
  d.add(PolyLine(points,strokeColor=HexColor(COLORS[j]),strokeWidth=2));d.add(String(65+j*310,358,method,fontSize=10,fillColor=HexColor(COLORS[j])))
 for epoch in [0,30,60,90,120]:d.add(String(x+w*epoch/120,y-18,str(epoch),fontSize=10,textAnchor='middle'))
 foot(d,'120 fixed Adam updates, no early stopping or heldout selection. Full logs/checkpoints saved; optimization convergence is not independent generalization.');export(d,'figure07_contrastive_training_loss');print(O)
if __name__=='__main__':main()
