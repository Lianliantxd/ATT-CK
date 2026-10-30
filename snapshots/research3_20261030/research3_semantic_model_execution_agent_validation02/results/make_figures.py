"""Descriptive vector scientific plots from completed result CSVs."""
import csv,sys
from pathlib import Path
from reportlab.graphics.shapes import Drawing,Rect,String,Line
from reportlab.graphics import renderPDF,renderSVG
from reportlab.lib.colors import HexColor,white
R=Path(__file__).resolve().parents[1];O=R/'reports/analysis-output/figures';O.mkdir(parents=True,exist_ok=True)
COLORS=['#426B92','#D6873B','#53795B']
def read(name):return list(csv.DictReader((R/name).open()))
def chart(name,title,labels,series,legend,cap=100):
 d=Drawing(850,410);d.add(Rect(0,0,850,410,fillColor=white,strokeColor=None));d.add(String(48,382,title,fontName='Helvetica-Bold',fontSize=16,fillColor=HexColor('#172B3A')))
 x,y,w,h=60,95,755,240
 for value in range(0,cap+1,10):
  yy=y+h*value/cap;d.add(Line(x,yy,x+w,yy,strokeColor=HexColor('#DFE4E8'),strokeWidth=.5));d.add(String(x-8,yy-3,str(value),textAnchor='end',fontSize=9))
 step=w/len(labels);bw=min(22,step/(len(series)+1.8))
 for j,values in enumerate(series):
  for i,value in enumerate(values):
   xx=x+(i+.5)*step+(j-len(series)/2)*bw;hh=h*value/cap
   d.add(Rect(xx,y,bw-2,hh,fillColor=HexColor(COLORS[j]),strokeColor=None));d.add(String(xx+(bw-2)/2,y+hh+4,f'{value:.1f}',textAnchor='middle',fontSize=7))
 for i,label in enumerate(labels):
  for j,line in enumerate(label.split('\n')):d.add(String(x+(i+.5)*step,y-17-j*12,line,textAnchor='middle',fontSize=8))
 for j,label in enumerate(legend):
  xx=65+j*245;d.add(Rect(xx,354,10,10,fillColor=HexColor(COLORS[j]),strokeColor=None));d.add(String(xx+15,354,label,fontSize=10))
 d.add(String(60,27,'P0 EXPOSED_DEV: 975 queries / 195 logical steps; one fixed model seed. Descriptive bars; no independent test.',fontSize=9))
 renderPDF.drawToFile(d,str(O/(name+'.pdf')));renderSVG.drawToFile(d,str(O/(name+'.svg')))
def main():
 e={x['method']:x for x in read('EMBEDDING_REAL_RESULTS.csv')};r={x['method']:x for x in read('RERANKER_REAL_RESULTS.csv')};e.update(r)
 names=['M0_MATCHED_E1_NATIVE_PREFIX','E1_NATIVE_PREFIX','E2_NATIVE_FIELDS_PREFIX','M0_MATCHED_E3_NATIVE_WINDOW_DIRECT','E3_NATIVE_WINDOW_DIRECT','E4_NATIVE_WINDOW_CHUNK_MAX','E5_NATIVE_WINDOW_CHUNK_MEAN','GTE_RERANKER_EMBEDDING_TOP20']
 chart('figure-01-main','Pretrained models: Top-10 coverage and early ranking differ',['TF-IDF\nprefix','GTE\nprefix','GTE fields\nprefix','TF-IDF\nwindow','GTE\nwindow','GTE chunk\nmax','GTE chunk\nmean','GTE CE\nEmbed20'],[[float(e[n][metric])*100 for n in names] for metric in ['top1_accuracy','top10_accuracy','mrr']],['Top-1 (%)','Top-10 (%)','MRR@10 x 100'],cap=40)
 u=read('RERANKER_CANDIDATE_UPPER_BOUNDS.csv')
 chart('figure-02-candidates','Candidate inclusion improves with K; reranking conversion declines',[x['pool'].title()+'\nK='+x['K'] for x in u],[[float(x['Top10_candidate_upper_bound'])*100 for x in u],[float(e['M0_MATCHED_E1_NATIVE_PREFIX' if x['pool']=='LEXICAL' else 'E1_NATIVE_PREFIX']['top10_accuracy'])*100 for x in u],[float(x['actual_Top10'])*100 for x in u]],['Candidate hit upper bound (%)','Original Top-10 (%)','Reranked Top-10 (%)'],cap=100)
 print(O)
if __name__=='__main__':main()
