from pathlib import Path
import html, json
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from pypdf import PdfReader, PdfWriter

B = Path('/media/kurogane/backup/bisignal_training/work_sim_2/output/pdf/saccade_detection_sources')
O = B / 'ja'
pdfmetrics.registerFont(TTFont('JP', '/tmp/saccade_babeldoc_cache/fonts/SourceHanSerifJP-Regular.ttf'))
pdfmetrics.registerFont(TTFont('JPB', '/tmp/saccade_babeldoc_cache/fonts/SourceHanSansJP-Bold.ttf'))
W, H = 598, 842
C = Canvas('/tmp/sauter_verified_first_page.pdf', pagesize=(W, H))
styles = {
    'title': ParagraphStyle('title', fontName='JPB', fontSize=17, leading=24, wordWrap='CJK', textColor=HexColor('#173a4e')),
    'head': ParagraphStyle('head', fontName='JPB', fontSize=10, leading=15, wordWrap='CJK', textColor=HexColor('#173a4e')),
    'body': ParagraphStyle('body', fontName='JP', fontSize=9, leading=13.7, wordWrap='CJK'),
    'small': ParagraphStyle('small', fontName='JP', fontSize=7.3, leading=10.5, wordWrap='CJK'),
    'abstract': ParagraphStyle('abstract', fontName='JP', fontSize=9.1, leading=14, wordWrap='CJK'),
}
def draw(text, x, top, width, style='body', gap=7):
    p = Paragraph(html.escape(text), styles[style]); _, height = p.wrap(width, H)
    p.drawOn(C, x, H-top-height)
    return top+height+gap

title='カルマンフィルタが生成するイノベーションを用いた追跡眼球運動の解析'
top=draw('生理学的計測 | Medical & Biological Engineering & Computing (1991), 29, 63–69',38,30,522,'small',10)
top=draw(title,38,top,522,'title',12)
top=draw('D. Sauter¹, B. J. Martin², N. Di Renzo², C. Vomscheid¹',38,top,522,'body',5)
top=draw('¹ Centre de Recherche en Automatique de Nancy, UA CNRS 821, LARA, Université de Nancy 1, Vandoeuvre, France',38,top,522,'small',3)
top=draw('² Service Physiologie Environnementale, Institut National de Recherche et de Sécurité, Vandoeuvre, France',38,top,522,'small',12)
top=draw('要旨',38,top,522,'head',4)
abstract='追跡眼球運動をコンピュータで解析するため、単純ながら効率的なアルゴリズムを開発した。このプログラムは滑動性追従眼球運動とサッケードを分離する。両成分の分離は、2段階のサッケード検出処理によって行う。まず、滑らかな成分の速度の自己回帰（AR）モデルを同定し、それを用いてカルマンフィルタを定める。次に、このフィルタが生成するイノベーション（予測残差）の系列によってサッケードを検出する。各サッケードの正確な開始点と終了点は、Hinkleyアルゴリズムで求める。ランダムに動く標的を眼で追跡する場合について、解析手順の例を示す。この方法は高い信頼性を示し、眼振などの他の眼球運動にも容易に拡張できると考えられる。'
top=draw(abstract,38,top,522,'abstract',8)
top=draw('キーワード：追跡眼球運動、Hinkley検定、イノベーション、カルマンフィルタ、サッケード、時系列',38,top,522,'small',14)
top=draw('1　はじめに',38,top,522,'head',7)
left=[
'眼球運動の解析、とりわけ、それぞれサッケードと滑らかな運動と呼ばれる急速相と緩徐相の分離は、臨床研究と基礎研究の双方において極めて重要である。これら2種類の眼球運動は、2つの眼球運動制御サブシステムによって生成され、その出力が組み合わされて外眼筋を駆動する。',
'過去10年間に、両成分を自動的に分離する多数の複雑なコンピュータアルゴリズムが開発されてきた（Allum et al., 1975; Baloh et al., 1980; Barnes, 1982; Matsuoka and Harato, 1983; Baland et al., 1987）。提案されたアルゴリズムの大部分は、基本的にサッケードの動特性（振幅、速度、加速度、持続時間）を識別基準に用いる。これらの処理は時間を要し、しばしばオフライン解析を必要とするうえ、ノイズの影響を受けやすく、強いフィルタ処理が必要になる。',
'一般に、これらは急速相を除外して緩徐相を認識することを目的としており、ほぼ眼振解析に特化している。眼振は、適切な視覚刺激または前庭刺激によって誘発される、逆方向の緩徐な運動と急速な運動の交替からなる。正弦波状の前庭刺激の場合、課題は眼球運動の正弦波成分を再構成することになる。このため、その方法自体が適用範囲を眼振解析に限定している。',
]
right=[
'一方、追跡眼球運動も、眼球運動制御系（Stark et al., 1962; Bahill et al., 1980）や眼と手の協調（Gauthier and Hofferer, 1976; Gauthier et al., 1988）を調べるうえで重要である。視覚標的の移動に対して生じるこれらの運動は、長い滑動性追従区間が修正サッケードによって中断される形をとる。',
'追跡眼球運動の解析では、特に予測不可能な標的波形を追跡する場合、両成分の速度範囲が大きく重なるため、その分離に細心の注意を要する。Matsuoka and Harato（1983）が提案した方法は非常に効率的とみられるが、広帯域信号には適用できない。そこで新しい手法を開発する動機は、第1に高周波成分を変化させずに広帯域信号を解析すること、第2にノイズの多い信号でも動作する高速で信頼性の高い比較的単純なアルゴリズムを得ること、第3に完全自動の信号処理を実現することにあった。',
'本論文の主な目的は、眼位信号を高い周波数（1000 Hz）で標本化した場合に、サッケードとその正確な開始点・終了点を検出できる新しいオンラインアルゴリズムを提案することである。さらに、この方法ではサッケードの検出確率を定量化できる。眼と手による追跡課題の眼球運動解析に適用し、良好な結果を得た。ただし、実験結果の詳細な記述は本論文の範囲外である。',
]
bottoms=[]
for x,paras in [(38,left),(308,right)]:
    y=top
    for p in paras:y=draw(p,x,y,252,'body',7)
    bottoms.append(y)
assert max(bottoms)<770, bottoms
y=max(bottoms)+5
y=draw('連絡先：D. Sauter, CRAN-LARA, Univ. Nancy 1, B.P. 239, 54506 Vandoeuvre Cedex, France',38,y,522,'small',3)
y=draw('初稿受理：1989年10月19日／改稿受理：1990年2月26日　© IFMBE 1991',38,y,522,'small',3)
assert y<807, y
C.setFont('JP',7);C.setFillColor(HexColor('#637480'))
C.drawString(38,20,'第1頁は原文照合のうえ再組版。図・式を含む以後の頁は原文に対応。')
C.drawRightString(560,20,'63 / 日本語版 1')
C.save()
f=O/'08_Sauter_et_al_1991_ja.pdf';old=PdfReader(f);first=PdfReader('/tmp/sauter_verified_first_page.pdf');writer=PdfWriter()
writer.add_page(first.pages[0])
for p in old.pages[1:]:writer.add_page(p)
writer.add_metadata({'/Title':title,'/Author':'D. Sauter, B. J. Martin, N. Di Renzo, C. Vomscheid'})
tmp=f.with_suffix('.new.pdf')
with tmp.open('wb') as stream:writer.write(stream)
tmp.replace(f)
(O/'work/sauter_first_page_verified_translation.json').write_text(json.dumps({'title':title,'abstract':abstract,'intro_left':left,'intro_right':right,'note':'Source page 1 manually checked and retypeset; remaining pages machine translated.'},ensure_ascii=False,indent=2))
print('Sauter first page rebuilt, body bottom:',bottoms)
