"""Scientific figures from frozen-score diagnosis, never simulated results."""
import csv,os,subprocess,tempfile
from pathlib import Path
from reportlab.graphics.shapes import Drawing,Rect,Line,String
from reportlab.graphics import renderPDF,renderSVG
from reportlab.lib.colors import HexColor,white
R=Path(__file__).resolve().parents[1];O=R/'reports/analysis-output/figures'
def read(n):return list(csv.DictReader((R/n).open()))
def base(title,sub):
 d=Drawing(1080,480);d.add(Rect(0,0,1080,480,fillColor=white,strokeColor=None));d.add(String(40,448,title,fontName='Helvetica-Bold',fontSize=17));d.add(String(40,422,sub,fontSize=10));return d
def export(d,name):
 renderPDF.drawToFile(d,str(O/(name+'.pdf')));renderSVG.drawToFile(d,str(O/(name+'.svg')))
 with tempfile.TemporaryDirectory(prefix='r3-diag-fig-') as td:
  env=os.environ.copy();env['XDG_CACHE_HOME']=td
  subprocess.run(['/Users/tianxd/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm','-png','-singlefile','-r','120',str(O/(name+'.pdf')),str(O/name)],check=True,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
def main():
 r=next(x for x in read('INDEPENDENT_HIT_RECOUNT.csv') if x['seed']=='17' and x['view_id']=='ONE_VIEW_PER_STEP')
 vals=[int(r['retained_hit_queries']),int(r['lost_hit_queries']),int(r['gte_miss_with_unseen_order_rank_le10']),int(r['gte_miss_with_unseen_order_rank_gt10'])]
 d=base('Where the 450 unseen-target queries end up','ONE view, seed17 (all three ONE seeds have the same hit-set counts). Full 216-candidate rankings remain unchanged.')
 colors=['#498775','#BA5A45','#C79542','#4F6F91'];names=['GTE hit retained by C4','GTE hit lost after fusion','GTE miss: seen competition','GTE miss: unseen order >10'];x=55;y=250;w=970
 for v,c,name in zip(vals,colors,names):
  width=w*v/450;d.add(Rect(x,y,width,70,fillColor=HexColor(c),strokeColor=white));d.add(String(x+width/2,y+31,str(v),fillColor=white,textAnchor='middle',fontSize=16,fontName='Helvetica-Bold'));x+=width
 for i,(v,c,name) in enumerate(zip(vals,colors,names)):
  yy=210-i*27;d.add(Rect(55,yy-3,12,12,fillColor=HexColor(c),strokeColor=None));d.add(String(78,yy,f'{name}: {v} / 450 ({v/450:.1%})',fontSize=11))
 d.add(String(55,68,'349/384 original GTE misses have no correct unseen label in the first 10 positions of the unseen internal order.',fontSize=10))
 d.add(String(55,47,'Internal order is a rank-identity diagnostic, not an evaluation with unseen-only candidate filtering.',fontSize=9));export(d,'figure01_unseen_failure_partition')
 d=base('The 32 lost hits are restored by removing the seen supervision component','Diagnostic component removal using the original lambda/gamma and saved scores; these are not formal model results.')
 labels=['Frozen GTE reference','Frozen C4','Remove seen supervision','Remove seen bias'];values=[32,0,32,0];x0=70;y0=115;w=930;h=245
 for v in [0,8,16,24,32]:
  yy=y0+h*v/32;d.add(Line(x0,yy,x0+w,yy,strokeColor=HexColor('#DCE3EA'),strokeWidth=.6));d.add(String(x0-10,yy-3,str(v),textAnchor='end',fontSize=10))
 for i,(name,v) in enumerate(zip(labels,values)):
  xx=x0+70+i*235;hh=h*v/32;d.add(Rect(xx,y0,100,max(hh,.8),fillColor=HexColor(colors[i]),strokeColor=None));d.add(String(xx+50,y0+hh+8,str(v),textAnchor='middle',fontSize=13));d.add(String(xx+50,y0-24,name,textAnchor='middle',fontSize=10))
 d.add(String(65,67,'All 32 ONE losses have gamma=0; none uses the two-step validation fallback. No exact Gold-score ties.',fontSize=10))
 d.add(String(65,45,'This identifies a computational ranking cause, not an attack-semantic or annotation cause.',fontSize=9));export(d,'figure02_component_removal')
 d=base('Misses within the unseen order dominate across exposed scenarios','ONE view, seed17. The four disjoint groups sum to each scenario\'s unseen-target queries; no independence claim.')
 rows=read('results/PRIMARY_DIAGNOSIS_BY_SCENE.csv');x0=65;y0=105;w=950;h=275;cap=175
 for v in [0,50,100,150]:
  yy=y0+h*v/cap;d.add(Line(x0,yy,x0+w,yy,strokeColor=HexColor('#DEE5EA'),strokeWidth=.5));d.add(String(x0-8,yy-3,str(v),textAnchor='end',fontSize=9))
 counts=read('results/HIT_COUNTS_BY_FOLD_SEED_VIEW.csv')
 for i,row in enumerate(rows):
  a=next(x for x in counts if x['fold_id']==row['fold_id'] and x['seed']=='17' and x['view_id']=='ONE_VIEW_PER_STEP')
  vs=[int(a['retained_hit_queries']),int(a['lost_hit_queries']),int(row['cross_group_block_only_candidate']),int(row['within_unseen_order_gt10'])];xx=x0+35+i*135;yy=y0
  for v,c in zip(vs,colors):
   hh=h*v/cap;d.add(Rect(xx,yy,65,hh,fillColor=HexColor(c),strokeColor=white));
   if v>=8:d.add(String(xx+32.5,yy+hh/2-3,str(v),textAnchor='middle',fontSize=9,fillColor=white))
   yy+=hh
  d.add(String(xx+32.5,yy+7,'n='+str(sum(vs)),textAnchor='middle',fontSize=9))
  d.add(String(xx+32.5,y0-19,'Scene '+row['fold_id'].split('_')[-1],textAnchor='middle',fontSize=10))
 for i,(c,name) in enumerate(zip(colors,['Retained','Fusion loss','Seen competition','Unseen order >10'])):d.add(String(65+i*250,65,name,fontSize=10,fillColor=HexColor(c)))
 d.add(String(65,39,'Five replicas per logical step and three reused seeds are dependent. No p-value or confidence interval is shown.',fontSize=9));export(d,'figure03_scene_failure_partition')
 print('THREE_REAL_DIAGNOSTIC_FIGURES_SAVED')
if __name__=='__main__':main()
