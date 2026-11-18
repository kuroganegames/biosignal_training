from pathlib import Path
import json,html
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from pypdf import PdfReader,PdfWriter
b=Path('/media/kurogane/backup/bisignal_training/work_sim_2/output/pdf/saccade_detection_sources');out=b/'ja'
d=json.loads((out/'work/correction_verified_translation.json').read_text())
pdfmetrics.registerFont(TTFont('JP','/tmp/saccade_babeldoc_cache/fonts/SourceHanSerifJP-Regular.ttf'))
pdfmetrics.registerFont(TTFont('JPB','/tmp/saccade_babeldoc_cache/fonts/SourceHanSansJP-Bold.ttf'))
styles={
 'body':ParagraphStyle('body',fontName='JP',fontSize=9.6,leading=14.5,wordWrap='CJK',spaceAfter=7),
 'title':ParagraphStyle('title',fontName='JPB',fontSize=17,leading=24,wordWrap='CJK',spaceAfter=12,textColor=HexColor('#173a4e')),
 'heading':ParagraphStyle('heading',fontName='JPB',fontSize=11.2,leading=16,wordWrap='CJK',spaceBefore=9,spaceAfter=7,textColor=HexColor('#173a4e')),
 'meta':ParagraphStyle('meta',fontName='JP',fontSize=8.2,leading=12,wordWrap='CJK',spaceAfter=6),
 'quote':ParagraphStyle('quote',fontName='JP',fontSize=9.3,leading=14.1,wordWrap='CJK',leftIndent=12,rightIndent=9,spaceAfter=8,borderColor=HexColor('#b6c8cf'),borderWidth=.5,borderPadding=6),
 'reference':ParagraphStyle('reference',fontName='JP',fontSize=7.6,leading=10.7,wordWrap='CJK',spaceAfter=5),
}
def para(t,style):return Paragraph(html.escape(t).replace('\n','<br/>'),styles[style])
story=[para(d['title'],'title'),para(d['authors'],'meta'),para(d['citation'],'meta'),para(d['date'],'meta'),Spacer(1,4)]
for i,blocks in enumerate(d['pages']):
 if i:story.append(PageBreak())
 for block in blocks:
  kind,text=next(iter(block.items()));story.append(para(text,'body' if kind=='text' else kind))
story.append(Spacer(1,5));story.append(para(d['editorial_note'],'meta'))
def footer(c,doc):
 c.setFont('JP',7);c.setFillColor(HexColor('#637480'));c.drawString(45,25,'Zemblys et al. (2019) | 原文照合済み日本語訳 | 2026-11-18');c.drawRightString(550,25,str(doc.page))
f=out/'11_Zemblys_et_al_2019_Correction_ja.pdf'
SimpleDocTemplate(str(f),pagesize=(595.276,841.89),rightMargin=45,leftMargin=45,topMargin=42,bottomMargin=43,title=d['title'],author=d['authors']).build(story,onFirstPage=footer,onLaterPages=footer)
source=PdfReader(b/'11_Zemblys_et_al_2019_Correction.pdf');translated=PdfReader(f);writer=PdfWriter()
for i in range(max(len(source.pages),len(translated.pages))):
 if i<len(source.pages):writer.add_page(source.pages[i])
 if i<len(translated.pages):writer.add_page(translated.pages[i])
writer.add_metadata({'/Title':d['title']+'（原文対訳）','/Author':d['authors']})
with (out/'11_Zemblys_et_al_2019_Correction_en_ja.pdf').open('wb') as file:writer.write(file)
print('Verified correction:',len(translated.pages),'Japanese pages')
