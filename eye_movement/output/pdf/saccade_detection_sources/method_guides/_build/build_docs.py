from pathlib import Path
import json, sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from PIL import Image
from content import METHODS

BUILD=Path(__file__).resolve().parent
ROOT=BUILD.parent
CAT=json.loads((ROOT.parent/'catalog.json').read_text())
REF={r['key']:r for r in CAT['references']}
OUT=ROOT/'docx';OUT.mkdir(exist_ok=True)
FONT='Noto Sans CJK JP'

def set_font(style,name,size,bold=False):
    style.font.name=name;style.font.size=Pt(size);style.font.bold=bold;style.font.color.rgb=RGBColor(0,0,0)
    rp=style.element.get_or_add_rPr()
    fonts=rp.find(qn('w:rFonts'))
    if fonts is None: fonts=OxmlElement('w:rFonts');rp.append(fonts)
    for k in ['ascii','hAnsi','eastAsia','cs']:fonts.set(qn('w:'+k),name)
    lang=OxmlElement('w:lang');lang.set(qn('w:eastAsia'),'ja-JP');rp.append(lang)

def paragraph(doc,text,style=None,bold_lead=None):
    p=doc.add_paragraph(style=style)
    if bold_lead:p.add_run(bold_lead+'　').bold=True
    p.add_run(text)
    return p

def heading(doc,text):
    p=doc.add_paragraph(text,'Heading 1');p.paragraph_format.keep_with_next=True
    return p

def page(doc,title):
    doc.add_page_break();heading(doc,title)

def table(doc,rows,headers=None):
    t=doc.add_table(rows=1,cols=3)
    t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    widths=[1.05,1.55,4.46]
    for c,w in zip(t.columns,widths):c.width=Inches(w)
    for c,s in zip(t.rows[0].cells,headers or ['パラメータ','役割または設定例','定義と確認事項']):c.text=s
    for row in rows:
        for c,s in zip(t.add_row().cells,row):c.text=s
    borders=OxmlElement('w:tblBorders')
    for name in ['top','left','bottom','right','insideH','insideV']:
        el=OxmlElement('w:'+name);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
    t._tbl.tblPr.append(borders)
    for ri,row in enumerate(t.rows):
        trpr=row._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
        if ri==0:trpr.append(OxmlElement('w:tblHeader'))
        for ci,cell in enumerate(row.cells):
            cell.width=Inches(widths[ci]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            pr=cell._tc.get_or_add_tcPr();m=OxmlElement('w:tcMar')
            for side in ['top','left','bottom','right']:
                x=OxmlElement('w:'+side);x.set(qn('w:w'),'85');x.set(qn('w:type'),'dxa');m.append(x)
            pr.append(m)
            if ri==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E8EEF1');pr.append(sh)
            for p in cell.paragraphs:
                p.style='Table Text';p.paragraph_format.keep_with_next=False
                for r in p.runs:r.bold=(ri==0)
    return t

def hyperlink(p,text,url):
    from docx.opc.constants import RELATIONSHIP_TYPE as RT
    rid=p.part.relate_to(url,RT.HYPERLINK,is_external=True)
    h=OxmlElement('w:hyperlink');h.set(qn('r:id'),rid)
    r=OxmlElement('w:r');rp=OxmlElement('w:rPr')
    col=OxmlElement('w:color');col.set(qn('w:val'),'176375');rp.append(col)
    r.append(rp);tx=OxmlElement('w:t');tx.text=text;r.append(tx);h.append(r);p._p.append(h)

for m in METHODS:
    if len(sys.argv)>1 and m['id'] not in sys.argv[1:]:continue
    d=Document();sec=d.sections[0]
    sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.left_margin=sec.right_margin=Inches(.72)
    sec.top_margin=Inches(.6);sec.bottom_margin=Inches(.6)
    sec.header_distance=Inches(.2);sec.footer_distance=Inches(.25)
    set_font(d.styles['Normal'],FONT,11)
    d.styles['Normal'].paragraph_format.line_spacing=1.14
    d.styles['Normal'].paragraph_format.space_after=Pt(6)
    d.styles['Normal'].paragraph_format.widow_control=True
    for name,size in [('Title',21),('Heading 1',14),('Heading 2',12)]:
        set_font(d.styles[name],FONT,size,True)
        d.styles[name].paragraph_format.space_before=Pt(10 if name!='Title' else 0)
        d.styles[name].paragraph_format.space_after=Pt(8)
    for name,size in [('Small',9.2),('Table Text',9.7),('Code',9.1)]:
        if name not in d.styles:d.styles.add_style(name,1)
        set_font(d.styles[name], 'DejaVu Sans Mono' if name=='Code' else FONT,size)
        d.styles[name].paragraph_format.space_after=Pt(3)
        d.styles[name].paragraph_format.line_spacing=1.10
    for border in list(d.styles.element.iter(qn('w:pBdr'))):
        border.getparent().remove(border)
    d.styles['Code'].paragraph_format.left_indent=Inches(.15)
    # Navigation is useful across the separately distributed guides.
    footer=sec.footer.paragraphs[0];footer.style='Small';footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    footer.add_run(m['short']+'　｜　')
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
    d.core_properties.title=m['title']+' 手法解説'
    d.core_properties.subject='サッケード検出の原理と実装手順'
    d.core_properties.author=''
    d.core_properties.keywords='saccade, Japanese, method guide'
    paragraph(d,m['title'],'Title')
    paragraph(d,'サッケード検出の原理と実装手順','Small')
    paragraph(d,m['overview'])
    paragraph(d,m['scope'],'Small')
    heading(d,'入力と出力')
    paragraph(d,m['input'],bold_lead='入力')
    paragraph(d,m['output'],bold_lead='出力')
    heading(d,'検出の原理と計算式')
    paragraph(d,m['principle'])
    for i,(formula,explanation) in enumerate(m['equations']):
        f=BUILD/'equations'/f'{m["id"]}_{i}.png'
        with Image.open(f) as img: w,h=img.size
        p=d.add_paragraph();p.paragraph_format.space_before=Pt(5);p.paragraph_format.space_after=Pt(4);p.paragraph_format.keep_with_next=True
        p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        shape=p.add_run().add_picture(str(f),width=Inches(min(w/300,6.95)))
        shape._inline.docPr.set('descr',explanation)
        paragraph(d,explanation,'Small')
    if m.get('extra'):paragraph(d,m['extra'],'Small')
    if m.get('feature_rows'):
        page(d,'初期モデルの特徴量')
        paragraph(d,'原著の完全モデルに用いた14特徴。窓の端点処理、軸の統合方法、欠測の扱いも学習済みモデルと一致させる。窓内点数が少ない場合は、原著は最低3点を確保する。')
        table(d,m['feature_rows'],['特徴','単位と窓','計算する内容'])
        paragraph(d,'rmsは隣接変位の二乗平均平方根、stdは標準偏差、bceaは二変量等確率楕円面積を表す。diffの3特徴では前後窓の差の符号規約を含めて学習時の実装に合わせる。','Small')
        paragraph(d,'特徴選択によって一部の特徴が除かれたモデルもある。推論時に14個を無条件に渡すのではなく、モデルが要求する特徴名と順序を読む。','Small')
    page(d,'処理手順とパラメータ')
    for i,(title,body) in enumerate(m['steps'],1):paragraph(d,body,bold_lead=f'{i} {title}')
    heading(d,'必要な設定')
    paragraph(d,'数値は原著の設定例であり、装置や課題を問わず使える推奨値ではない。自動推定される値も、その推定規則を保存する。','Small')
    table(d,m['params'])
    page(d,'擬似コードと計算例')
    paragraph(d,m['code_note'],'Small')
    for line in m['code'].splitlines():
        p=paragraph(d,line,'Code');p.paragraph_format.keep_with_next=True
    d.paragraphs[-1].paragraph_format.keep_with_next=False
    heading(d,'数値例')
    for text in m['example']:paragraph(d,text)
    paragraph(d,'数値例は原理を確認するために作成した例であり、論文の実測データや性能試験の結果ではない。','Small')
    page(d,'実装上の注意と検証')
    for title,body in m['caveats']:paragraph(d,body,bold_lead=title)
    heading(d,'確認すべき挙動')
    for i,text in enumerate(m['checks'],1):paragraph(d,f'{i}　{text}')
    heading(d,'原典と確認箇所')
    paragraph(d,m['locations'],'Small')
    for key in m['refs']:
        r=REF[key]
        label=f"{r['authors']} ({r['year']}). {r['title']}. {r.get('journal',r.get('booktitle',''))}."
        p=paragraph(d,label,'Small');p.paragraph_format.keep_with_next=True
        p=d.add_paragraph(style='Small')
        if r.get('doi'):hyperlink(p,'DOI '+r['doi'],'https://doi.org/'+r['doi'])
        else:hyperlink(p,'原典の公開ページ',r['source'])
    paragraph(d,'再現時の記録項目　データセットと注釈の版、取得周波数、座標単位、前処理、検出器とモデルの版、パラメータ、後処理、評価時のイベント対応規則。','Small')
    paragraph(d,'作成日 2026年11月18日　原典の方法を整理した技術解説。擬似コードは説明用で、性能を検証済みの実装ではない。','Small')
    d.save(OUT/(m['id']+'_ja.docx'))
print('Created',len(METHODS),'DOCX guides')
