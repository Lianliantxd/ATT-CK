"""Scientific descriptive vector figures, all values from saved actual results."""
import csv
from pathlib import Path
from reportlab.graphics.shapes import Drawing,Rect,Line,String
from reportlab.graphics import renderPDF,renderSVG
from reportlab.lib.colors import HexColor,white
R=Path(__file__).resolve().parents[1];O=R/'reports/analysis-output/figures';O.mkdir(parents=True,exist_ok=True)
def chart(name,title,labels,data,legends,cap):
 colors=['#426B92','#D18A46','#597B60'];d=Drawing(850,390);d.add(Rect(0,0,850,390,fillColor=white,strokeColor=None));d.add(String(45,365,title,fontName='Helvetica-Bold',fontSize=15));x,y,w,h=60,90,760,225
 for value in range(0,cap+1,10 if cap>40 else 5):
  yy=y+h*value/cap;d.add(Line(x,yy,x+w,yy,strokeWidth=.5,strokeColor=HexColor('#E0E5EA')));d.add(String(x-7,yy-3,str(value),fontSize=9,textAnchor='end'))
 step=w/len(labels);bw=min(25,step/(len(data)+1.5))
 for j,values in enumerate(data):
  for i,v in enumerate(values):
   xx=x+(i+.5)*step+(j-len(data)/2)*bw;d.add(Rect(xx,y,bw-2,h*v/cap,fillColor=HexColor(colors[j]),strokeColor=None));d.add(String(xx+(bw-2)/2,y+h*v/cap+4,f'{v:.1f}',fontSize=8,textAnchor='middle'))
 for i,lab in enumerate(labels):
  for j,line in enumerate(lab.split('\n')):d.add(String(x+(i+.5)*step,y-17-j*12,line,fontSize=9,textAnchor='middle'))
 for j,lab in enumerate(legends):
  d.add(Rect(60+j*245,335,10,10,fillColor=HexColor(colors[j]),strokeColor=None));d.add(String(75+j*245,335,lab,fontSize=10))
 d.add(String(60,25,'P0 EXPOSED_DEV: 975 queries / 195 logical steps. One fixed protocol; bars are descriptive, not independent-test estimates.',fontSize=8))
 renderPDF.drawToFile(d,str(O/(name+'.pdf')));renderSVG.drawToFile(d,str(O/(name+'.svg')))
def main():
 rows=list(csv.DictReader((R/'MECHANISM_BASELINE_RESULTS.csv').open()));m={x['method']:x for x in rows};views=['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL'];labels=[model+'\n'+v for model in ['CHAR','BM25'] for v in ['Raw','Literal','Literal+R','Raw+Literal']]
 chart('figure-01-mechanism','Mechanism representations do not consistently improve retrieval',labels,[[float(m[f'{model}__{v}__{k}']['top10_accuracy'])*100 for model in ['CHAR','BM25'] for v in views] for k in ['K2_DESCRIPTION_16_1','MECHANISM_CARD']],['Original description Top-10 (%)','Mechanism card Top-10 (%)'],25)
 labels=[model+'\n'+v for model in ['CHAR','BM25'] for v in ['Raw','Literal']]
 chart('figure-02-knowledge-control','Knowledge-card gains are confounded by lexical content and ordering',labels,[[float(m[f'{model}__{v}__{k}']['top10_accuracy'])*100 for model in ['CHAR','BM25'] for v in ['RAW','LITERAL']] for k in ['MECHANISM_CARD','CARD_PREFIX_ONLY','CARD_WORD_ORDER_CONTROL']],['Full-source card (%)','Visible-prefix-only card (%)','Same-word order control (%)'],25)
 if (R/'results/NEURAL_BASELINE_RESULTS.csv').exists():
  labels=[model+'\n'+v for model in ['Embed','CE Top20'] for v in ['Raw','Literal','Literal+R','Raw+Literal']]
  chart('figure-03-neural','Fixed GTE models: mechanism views on the exposed development set',labels,[[float(m[f'{model}__{v}__{k}']['top10_accuracy'])*100 for model in ['GTE_EMBEDDING','GTE_CE'] for v in views] for k in ['K2_DESCRIPTION_16_1','MECHANISM_CARD']],['Original description Top-10 (%)','Mechanism card Top-10 (%)'],50)
 print(O)
if __name__=='__main__':main()
