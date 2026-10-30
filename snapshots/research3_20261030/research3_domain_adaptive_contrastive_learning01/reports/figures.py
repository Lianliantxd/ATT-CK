"""Actual publication-style descriptive figures; no fabricated uncertainty."""
import csv,sys
from pathlib import Path
import numpy as np
from reportlab.graphics.shapes import Drawing,Rect,Line,String,PolyLine
from reportlab.graphics import renderPDF,renderSVG
from reportlab.lib.colors import HexColor,white
R=Path(__file__).resolve().parents[1];O=R/'reports/analysis-output/figures';O.mkdir(parents=True,exist_ok=True)
def rows(n):return list(csv.DictReader((R/n).open()))
def draw(name,title,labels,series,legends,cap):
 d=Drawing(900,400);d.add(Rect(0,0,900,400,fillColor=white,strokeColor=None));d.add(String(50,375,title,fontSize=15,fontName='Helvetica-Bold'));colors=['#506F8C','#D1944C','#5E8169','#9F6B80'];x,y,w,h=65,80,805,235
 for k in range(6):
  value=cap*k/5;yy=y+h*k/5;d.add(Line(x,yy,x+w,yy,strokeWidth=.5,strokeColor=HexColor('#DFE5E9')));d.add(String(x-7,yy-3,f'{value:.2f}',fontSize=9,textAnchor='end'))
 step=w/len(labels);bw=min(35,step/(len(series)+1))
 for j,a in enumerate(series):
  for i,value in enumerate(a):
   xx=x+(i+.5)*step+(j-len(series)/2)*bw;d.add(Rect(xx,y,bw-2,h*value/cap,fillColor=HexColor(colors[j]),strokeColor=None));d.add(String(xx+(bw-2)/2,y+h*value/cap+4,f'{value:.3f}',fontSize=7,textAnchor='middle'))
 for i,label in enumerate(labels):d.add(String(x+(i+.5)*step,y-18,label,fontSize=10,textAnchor='middle'))
 for j,legend in enumerate(legends):d.add(Rect(65+j*200,344,10,10,fillColor=HexColor(colors[j]),strokeColor=None));d.add(String(80+j*200,344,legend,fontSize=9))
 d.add(String(65,25,'Grouped exposed development: 7 scenarios, 195 steps, 975 queries. Seed averages are descriptive; no independent-test claim.',fontSize=8));renderPDF.drawToFile(d,str(O/(name+'.pdf')));renderSVG.drawToFile(d,str(O/(name+'.svg')))
def main():
 g=rows('GROUPED_VALIDATION_RESULTS.csv');scenes=[str(i) for i in range(1,8)];configs=[('B0','SHARED'),('B1','SHARED'),('B2','ONE_VIEW_PER_STEP'),('B2','MULTI_VIEW_AUGMENTATION')]
 draw('figure01_scenario_mrr','Grouped development MRR@10: ordinary supervised training is a strong baseline',['Scene '+s for s in scenes],[[np.mean([float(r['mrr']) for r in g if r['method']==m and r['augmentation']==a and r['evaluation_partition']=='HELDOUT' and r['scenario']==s]) for s in scenes] for m,a in configs],['Frozen char','Frozen GTE','TFIDF linear one-view','TFIDF linear multi-view'],.35)
 st=rows('SEEN_UNSEEN_TECHNIQUE_RESULTS.csv');draw('figure02_seen_unseen','Seen versus unseen Gold subsets under the same 216-candidate ranking',['Seen Gold subset','Unseen Gold subset'],[[sum(float(r['mrr'])*int(r['n_records']) for r in st if r['method']==m and r['augmentation']==a and r['stratum']==cat)/sum(int(r['n_records']) for r in st if r['method']==m and r['augmentation']==a and r['stratum']==cat) for cat in ['SEEN_GOLD_SUBSET','UNSEEN_GOLD_SUBSET']] for m,a in configs],['Frozen char','Frozen GTE','TFIDF linear one-view','TFIDF linear multi-view'],.25)
 logs=rows('CONTRASTIVE_TRAINING_LOGS.csv');d=Drawing(900,400);d.add(Rect(0,0,900,400,fillColor=white,strokeColor=None));d.add(String(50,375,'Actual B2 training loss: fixed 120 Adam updates, seed 42',fontName='Helvetica-Bold',fontSize=15));colors=['#506F8C','#D1944C'];x,y,w,h=65,80,805,235
 for k in range(6):
  v=1.5*k/5;yy=y+h*k/5;d.add(Line(x,yy,x+w,yy,strokeColor=HexColor('#DFE5E9'),strokeWidth=.5));d.add(String(x-8,yy-3,f'{v:.1f}',fontSize=9,textAnchor='end'))
 for j,aug in enumerate(['ONE_VIEW_PER_STEP','MULTI_VIEW_AUGMENTATION']):
  points=[]
  for epoch in [1,*range(10,121,10)]:
   vals=[float(r.get('loss_before_update') or r.get('loss')) for r in logs if r['method']=='B2' and r['seed']=='42' and r['augmentation']==aug and int(r['epoch'])==epoch];points.extend([x+w*epoch/120,y+h*np.mean(vals)/1.5])
  d.add(PolyLine(points,strokeColor=HexColor(colors[j]),strokeWidth=2));d.add(String(70+j*300,344,aug,fontSize=10,fillColor=HexColor(colors[j])))
 for epoch in [0,30,60,90,120]:d.add(String(x+w*epoch/120,y-18,str(epoch),fontSize=10,textAnchor='middle'))
 d.add(String(65,25,'Loss is averaged over 7 overlapping training folds; this is an optimization diagnostic, not a generalization statistic.',fontSize=8));renderPDF.drawToFile(d,str(O/'figure03_training_loss.pdf'));renderSVG.drawToFile(d,str(O/'figure03_training_loss.svg'));print(O)
if __name__=='__main__':main()
