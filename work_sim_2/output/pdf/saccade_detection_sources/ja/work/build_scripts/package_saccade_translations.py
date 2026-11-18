from pathlib import Path
import json, html, hashlib, zipfile, re
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

B=Path('/media/kurogane/backup/bisignal_training/work_sim_2/output/pdf/saccade_detection_sources')
O=B/'ja'; D=B.parent
catalog=json.loads((B/'catalog.json').read_text());refs=catalog['references']
titles=[
'陰的な区分多項式近似を用いた正常サッケードおよび低速サッケードの検出',
'マイクロサッケードが明らかにする潜在的注意の方向',
'アイトラッキングデータから固視・サッケード・グリセードを検出する適応的アルゴリズム',
'読書中の眼球運動分類に関する、関連する2手法と独立した2手法の新たな評価',
'クラスタ分析による固視とサッケードのノンパラメトリック検出法：恣意的な閾値を不要にする',
'機械学習によるアイトラッキングデータのイベント検出',
'アイトラッキング記録における固視とサッケードの識別',
'固視およびサッケード行動の自動解析の標準化',
'カルマンフィルタが生成するイノベーションを用いた追跡眼球運動の解析',
'サッケード眼球運動の正常基準データベース：ばらつきとその構築',
'固視の識別：分散度アルゴリズムにおける最適な閾値',
'訂正：「機械学習によるアイトラッキングデータのイベント検出」',
]
authors=['Dai et al.','Engbert & Kliegl','Nyström & Holmqvist','Friedman et al.','König & Buffalo','Zemblys et al.','Salvucci & Goldberg','Komogortsev et al.','Sauter et al.','Bahill et al.','Blignaut','Zemblys et al.']
note='本文・要旨・図表キャプションを日本語化した読解用の訳である。図中文字、数式、文献情報の一部は原文を保持した。機械翻訳に用語調整と抜き取り照合を行っており、全文の手動校正は行っていない。'
manifest={'created':'2026-11-18','language':'ja','engine':'BabelDOC 0.7.1 + local Ollama','model':'Qwen3-30B-A3B-Instruct-2507 Q5_K_XL','processing':'Local translation; document text was not sent to an external translation service.','scope':note,'manual_review':'All 12 abstracts checked against source. Selected titles, author lines, numerical values and cross-references checked. Engbert 2003: core detector description on page 2 and rate-modulation paragraph on page 4 checked. Nystrom 2010: threshold definitions and values on page 7 checked; table equations restored from source. Salvucci 2000: all five pseudocode tables and I-DT description checked; malformed inline image repaired and original HMM figure restored. Zemblys 2019 Correction: full text checked and retypeset. Sauter 1991 and Bahill 1981: first pages checked and retypeset; figures restored from originals and selected OCR/terminology errors corrected. This is not a full manual proofreading of every page.','documents':[]}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for i,r in enumerate(refs):
 src=B/r['local_pdf'];mono=O/(r['id']+'_ja.pdf');dual=O/(r['id']+'_en_ja.pdf')
 assert mono.exists() and dual.exists(),r['id']
 assert sha(src)==r['sha256'],'Original checksum mismatch: '+r['id']
 n=len(PdfReader(src).pages);m=len(PdfReader(mono).pages);z=len(PdfReader(dual).pages)
 assert n==m and z==2*n,(src.name,n,m,z)
 manifest['documents'].append({'id':r['id'],'title_ja':titles[i],'title_en':r['title'],'author_label':authors[i],'year':r['year'],'source':src.name,'source_sha256':sha(src),'source_pages':n,'japanese':{'file':mono.name,'pages':m,'sha256':sha(mono)},'bilingual':{'file':dual.name,'pages':z,'sha256':sha(dual)},'review':'full_text_checked' if i==11 else ('first_page_checked_and_figure_restoration' if i in [8,9] else 'machine_translation_with_spot_checks')})
(O/'translation_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
for i,r in enumerate(refs):
 r.update(title_ja=titles[i],japanese_pdf='ja/'+r['id']+'_ja.pdf',bilingual_pdf='ja/'+r['id']+'_en_ja.pdf',translated='2026-11-18')
catalog['translated']='2026-11-18'
(B/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))

# Cover and navigable contents for the combined Japanese volume.
pdfmetrics.registerFont(TTFont('JP','/tmp/saccade_babeldoc_cache/fonts/SourceHanSerifJP-Regular.ttf'))
pdfmetrics.registerFont(TTFont('JPB','/tmp/saccade_babeldoc_cache/fonts/SourceHanSansJP-Bold.ttf'))
styles={'title':ParagraphStyle('title',fontName='JPB',fontSize=22,leading=29,wordWrap='CJK',textColor=HexColor('#173a4e')),'body':ParagraphStyle('body',fontName='JP',fontSize=8.5,leading=13,wordWrap='CJK'),'item':ParagraphStyle('item',fontName='JPB',fontSize=9.4,leading=13.5,wordWrap='CJK',textColor=HexColor('#173a4e')),'meta':ParagraphStyle('meta',fontName='JP',fontSize=7.4,leading=10.5,wordWrap='CJK')}
c=Canvas('/tmp/saccade_ja_cover.pdf',pagesize=(595.276,841.89));y=37
def draw(t,x,top,width,kind):
 p=Paragraph(html.escape(t),styles[kind]);_,h=p.wrap(width,800);p.drawOn(c,x,841.89-top-h);return top+h
y=draw('サッケード検出法の原典集',42,y,511,'title')+3
y=draw('全12本・日本語版  |  作成日 2026-11-18',42,y,511,'meta')+12
y=draw(note,42,y,511,'body')+5
y=draw('訂正論文（11）は本文全体を照合。Sauter（08）・Bahill（09）は第1頁を照合して再組版した。各論文の原文との対照には、別添の対訳PDFを利用できる。',42,y,511,'body')+15
starts=[];contents_links=[];current=2
for i,(r,t,a) in enumerate(zip(refs,titles,authors)):
 starts.append(current);top=y
 c.setStrokeColor(HexColor('#d5e0e4'));c.setLineWidth(.4);c.line(42,841.89-y+3,553,841.89-y+3)
 c.setFont('JPB',10);c.setFillColor(HexColor('#176c71'));c.drawString(43,841.89-y-14,f'{i:02}')
 y=draw(t,72,y+3,433,'item')+2
 y=draw(f'{a} ({r["year"]})  /  {r["role"]}  /  {r["pdf_pages"]}ページ',72,y,433,'meta')+8
 c.setFont('JP',9);c.setFillColor(HexColor('#173a4e'));c.drawRightString(551,841.89-top-15,str(current))
 contents_links.append((42,841.89-y,553,841.89-top+3))
 current+=r['pdf_pages']
assert y<800,y
c.setFont('JP',7);c.setFillColor(HexColor('#637480'));c.drawString(42,22,'右端は本PDF内の開始ページ。各論文の書誌情報・原文・用語表は同梱の一覧を参照。');c.save()
writer=PdfWriter();writer.append('/tmp/saccade_ja_cover.pdf')
for i,r in enumerate(refs):writer.append(str(O/(r['id']+'_ja.pdf')),outline_item=f'{i:02} {authors[i]} ({r["year"]}) — {titles[i]}',import_outline=False)
for rect,start in zip(contents_links,starts):writer.add_annotation(0,Link(rect=rect,target_page_index=start-1,border=[0,0,0]))
writer.add_metadata({'/Title':'サッケード検出法の原典集・全12本日本語版','/Author':'各論文の著者（翻訳編集：Codex）','/Subject':note})
merged=D/'saccade_detection_papers_ja.pdf'
with merged.open('wb') as stream:writer.write(stream)

# Add translated titles and links to the existing bibliographic catalogue.
backup=O/'work/index_before_translation.html'
if not backup.exists():backup.write_text((B/'index.html').read_text())
s=backup.read_text()
s=s.replace('<title>サッケード検出法の元論文集 | PMC8212426</title>','<title>サッケード検出法の元論文・日本語訳 | 全12本</title>')
s=s.replace('全保存PDFは元のバイト列のまま保存し','原文PDFはすべて元のバイト列のまま保存し')
s=s.replace('<h1>サッケード検出法の元論文集</h1>','<h1>サッケード検出法の元論文・日本語訳</h1>')
s=s.replace('<b>0</b>未取得PDF','<b>12</b>日本語訳・対訳')
banner='<div class="banner" style="margin:20px 0"><p><strong>全12本の日本語版を追加しました。</strong>日本語のみのPDFと、原文・訳文を1ページずつ交互に並べた対訳PDFがあります。</p><p>'+html.escape(note)+'</p><p>訂正論文は本文全体を照合。Sauter・Bahill論文は第1頁を照合して再組版し、図版を原画像から復元しました。</p><p><a href="../saccade_detection_papers_ja.pdf">全12本の日本語合本</a> · <a href="../saccade_detection_sources_with_japanese.zip">原文・日本語版・対訳版を一括取得</a> · <a href="ja/glossary.csv">対訳用語表</a> · <a href="ja/translation_manifest.json">翻訳・検証記録</a></p></div>'
s=s.replace('<h2>比較10手法と文献の対応</h2>',banner+'<h2>比較10手法と文献の対応</h2>')
for i,r in enumerate(refs):
 s=s.replace('<h3>'+html.escape(r['title'])+'</h3>','<h3>'+html.escape(titles[i])+'</h3><p class="meta">'+html.escape(r['title'])+'</p>')
 pat='<a class="download" href="'+r['local_pdf']+'">保存PDFを開く · '+str(r['pdf_pages'])+'ページ</a>'
 replacement='<a class="download" href="ja/'+r['id']+'_ja.pdf">日本語版 · '+str(r['pdf_pages'])+'ページ</a> <a class="download" href="ja/'+r['id']+'_en_ja.pdf">原文対訳版</a> <a class="download" href="'+r['local_pdf']+'">原文PDF</a>'
 assert pat in s,r['id'];s=s.replace(pat,replacement)
(B/'index.html').write_text(s)

# A small landing page remains useful when the translation folder is opened alone.
rows=[]
for i,r in enumerate(refs):
 rows.append('<tr><td>'+f'{i:02}'+'</td><td>'+html.escape(titles[i])+'<br><small>'+html.escape(authors[i])+f' ({r["year"]})</small></td><td><a href="'+r['id']+'_ja.pdf">日本語</a> · <a href="'+r['id']+'_en_ja.pdf">対訳</a></td></tr>')
(O/'index.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>日本語訳12本</title><style>body{max-width:1000px;margin:40px auto;padding:0 20px;font:16px/1.8 system-ui;color:#203441}table{width:100%;border-collapse:collapse}td{padding:14px;border-bottom:1px solid #ccd8df}td:last-child{white-space:nowrap}a{color:#006685}small{color:#61717e}</style><h1>サッケード検出法の原典集：日本語訳</h1><p>'+html.escape(note)+'</p><p><a href="../index.html">書誌情報と手法の対応表</a> · <a href="glossary.csv">対訳用語表</a></p><table>'+''.join(rows)+'</table></html>')

archive=D/'saccade_detection_sources_with_japanese.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 z.write(merged,merged.name)
 for p in sorted(B.rglob('*')):
  if p.is_file() and 'work' not in p.relative_to(B).parts and p.suffix in ['.pdf','.html','.json','.bib','.csv']:
   if p==B/'index.html':
    archived_index=re.sub(r' · <a href="../saccade_detection_sources_with_japanese.zip">.*?</a>','',p.read_text())
    z.writestr(str(Path(B.name)/p.relative_to(B)),archived_index)
   else:z.write(p,Path(B.name)/p.relative_to(B))
print('Complete:',len(refs),'papers;',len(PdfReader(merged).pages),'combined pages')
print(merged,merged.stat().st_size)
print(archive,archive.stat().st_size)
