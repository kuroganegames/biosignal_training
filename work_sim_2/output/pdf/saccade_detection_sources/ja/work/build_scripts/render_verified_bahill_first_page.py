from pathlib import Path
import html, json, re
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from pypdf import PdfReader, PdfWriter

B=Path('/media/kurogane/backup/bisignal_training/work_sim_2/output/pdf/saccade_detection_sources'); O=B/'ja'
pdfmetrics.registerFont(TTFont('JP','/tmp/saccade_babeldoc_cache/fonts/SourceHanSerifJP-Regular.ttf'))
pdfmetrics.registerFont(TTFont('JPB','/tmp/saccade_babeldoc_cache/fonts/SourceHanSansJP-Bold.ttf'))
W,H=612,792
C=Canvas('/tmp/bahill_verified_first_page.pdf',pagesize=(W,H))
styles={
 'title':ParagraphStyle('title',fontName='JPB',fontSize=17,leading=24,wordWrap='CJK',textColor=HexColor('#173a4e')),
 'head':ParagraphStyle('head',fontName='JPB',fontSize=10,leading=15,wordWrap='CJK',textColor=HexColor('#173a4e')),
 'body':ParagraphStyle('body',fontName='JP',fontSize=9.3,leading=14.1,wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName='JP',fontSize=7.5,leading=11,wordWrap='CJK'),
}
def draw(text,x,top,width,style='body',gap=8):
 text=re.sub(r'[¹²³⁴⁵⁶⁷⁸⁹⁰˒⁻]+',lambda m:'['+m.group().translate(str.maketrans('¹²³⁴⁵⁶⁷⁸⁹⁰˒⁻','1234567890,-'))+']',text)
 p=Paragraph(html.escape(text),styles[style]);_,height=p.wrap(width,H);p.drawOn(C,x,H-top-height);return top+height+gap
title='サッケード眼球運動の正常基準データベース：ばらつきとその構築'
top=draw('Investigative Ophthalmology & Visual Science (1981), 21(1), 116–125',40,30,532,'small',12)
top=draw(title,40,top,532,'title',12)
top=draw('A. Terry Bahill, Allan Brockenbrough, and B. Todd Troost',40,top,532,'body',14)
top=draw('要旨',40,top,532,'head',4)
abstract='正常被験者13名のサッケード眼球運動について、持続時間、ピーク速度、加速度をサッケード振幅の関数として図示した。サッケード眼球運動の見かけのピーク速度は、速度の算出に用いるアルゴリズムの影響を受けやすい。速度チャネルのフィルタは、ノイズを制限しながら信号情報をすべて通過させるため、位相ずれがゼロで、遮断周波数が60～100 Hzであるべきである。一部の被験者は急速に疲労し、そのパラメータは正常値の範囲外となる。'
top=draw(abstract,40,top,532,'body',8)
top=draw('キーワード：サッケード眼球運動、メインシーケンス、持続時間、速度、加速度、フィルタ処理、微分、パワースペクトル、疲労、帯域幅、線形性',40,top,532,'small',16)
left=[
'メインシーケンス・パラメータと呼ばれるサッケードのピーク速度・振幅・持続時間のパラメータ¹˒²は、サッケードの定義に用いられてきた。これらのパラメータが正常基準データと一致する眼球運動を、サッケードと呼んだ。この手法は、通常のサッケード³⁻⁶、時間的に近接したサッケード⁷、重なり合うサッケード⁸、Heringの法則に従わないサッケード⁹、眼振の急速相¹⁰⁻¹²、随意性眼振¹³、動的オーバーシュート¹⁴、核間性眼筋麻痺における分割されたサッケード¹⁵に用いられてきた。これらの研究の多くは、異なる正常基準データベースを使用している。本論文では、これらのデータベースにばらつきが生じる理由として考えられるものを説明する。',
]
right=[
'これらのピーク速度・振幅・持続時間のパラメータは有用性が高いため、疲労、被験者間および被験者内の変動、計測機器のノイズ、データのローパスフィルタ処理、パラメータ値を計算するアルゴリズムによって、どの程度影響を受けるのかという疑問が生じた。我々は、正常データベースの定量的側面を定めるなかで、これらの疑問に答えた。',
'同一研究室内の比較に使用できる、妥当で一貫した正常サッケード眼球運動データを整えることは困難であった。第1に、均一な年齢層に属する多数の正常被験者を記録する必要があった。第2に、疲労した被験者の眼球運動を除外する必要があった。そのためには、個々のサッケードの速度プロファイルを目視で調べなければならなかった。第3に、ピーク速度と持続時間を、標的の移動量ではなく、サッケード振幅の関数として図示する必要があった。第4に、各サッケードの開始点と終了点の決定には、位置波形ではなく速度波形を用いる必要があった。第5に、速度の計算には位相ずれのないデジタルフィルタとアルゴリズムを用いる必要があった。第6に、特に速度チャネルについて、フィルタのボード線図を測定して作図する必要があった。第7に、［次頁へ続く］',
]
ys=[]
for x,paras in [(40,left),(314,right)]:
 y=top
 for p in paras:y=draw(p,x,y,258,'body',8)
 ys.append(y)
y=ys[0]+10
metadata=[
'所属：カーネギーメロン大学電気工学科、およびピッツバーグ大学医学部神経内科学教室（米国ペンシルベニア州ピッツバーグ）。',
'研究費：米国国立衛生研究所（R23EY02382）、米国国立科学財団（ENG 7722418）、米国海軍航空システム司令部からの助成により一部支援を受けた。',
'投稿：1980年7月24日。',
'別刷請求先：A. Terry Bahill, Biomedical Engineering Program, Department of Electrical Engineering, Carnegie-Mellon University, Pittsburgh, Pa. 15213.',
]
for p in metadata:y=draw(p,40,y,258,'small',7)
assert max(y,*ys)<733,(y,ys)
C.setFont('JP',6.5);C.setFillColor(HexColor('#637480'))
C.drawString(40,44,'0146-0404/81/070116+10$01.00/0 © 1981 Assoc. for Res. in Vis. and Ophthal., Inc.')
C.drawString(40,32,'原文取得：iovs.arvojournals.org, 2026-11-17。第1頁は原文照合のうえ再組版。')
C.drawRightString(572,20,'116 / 日本語版 1');C.save()
f=O/'09_Bahill_et_al_1981_ja.pdf';old=PdfReader(f);first=PdfReader('/tmp/bahill_verified_first_page.pdf');writer=PdfWriter();writer.add_page(first.pages[0])
for p in old.pages[1:]:writer.add_page(p)
writer.add_metadata({'/Title':title,'/Author':'A. Terry Bahill, Allan Brockenbrough, B. Todd Troost'})
tmp=f.with_suffix('.new.pdf')
with tmp.open('wb') as stream:writer.write(stream)
tmp.replace(f)
(O/'work/bahill_first_page_verified_translation.json').write_text(json.dumps({'title':title,'abstract':abstract,'intro_left':left,'intro_right':right,'metadata':metadata,'note':'Source page 1 manually checked and retypeset; remaining pages machine translated.'},ensure_ascii=False,indent=2))
print('Bahill first page rebuilt',ys,y)
