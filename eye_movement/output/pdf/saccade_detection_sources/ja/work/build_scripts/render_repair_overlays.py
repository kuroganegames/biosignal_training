from pathlib import Path
import json,sys,html
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader
B=Path('/media/kurogane/backup/bisignal_training/work_sim_2/output/pdf/saccade_detection_sources/ja')
data=json.loads(Path(sys.argv[1]).read_text());out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('JP','/tmp/saccade_babeldoc_cache/fonts/SourceHanSerifJP-Regular.ttf'))
pdfmetrics.registerFont(TTFont('JPB','/tmp/saccade_babeldoc_cache/fonts/SourceHanSansJP-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'))
manifest=[]
for name in sorted(set(x['document'] for x in data)):
 reader=PdfReader(B/name);items=[x for x in data if x['document']==name];file=out/name;c=Canvas(str(file))
 for x in items:
  page=reader.pages[x['page']-1];width=float(page.mediabox.width);height=float(page.mediabox.height);c.setPageSize((width,height))
  if True:
   x0,y0,x1,y1=x['rect'];size=x.get('size',9.3);font=x.get('font','JP');content=x.get('markup',html.escape(x['text']).replace('\n','<br/>'))
   while True:
    style=ParagraphStyle('repair',fontName=font,fontSize=size,leading=size*x.get('lineheight',1.2),wordWrap='CJK',alignment=x.get('align',0),spaceBefore=0,spaceAfter=0)
    para=Paragraph(content,style);pw,ph=para.wrap(x1-x0,y1-y0)
    if ph<=y1-y0-1:break
    size-=.1
    if size<5:raise ValueError(x)
   para.drawOn(c,x0,height-y0-ph-.3);x['actual_font_size']=round(size,3);x['rendered_height']=ph
  c.showPage()
 c.save();manifest.append({'document':name,'overlay':str(file),'items':items})
Path(sys.argv[1]).write_text(json.dumps(data,ensure_ascii=False,indent=2));(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
