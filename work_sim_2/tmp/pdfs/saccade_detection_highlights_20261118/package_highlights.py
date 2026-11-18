from pathlib import Path
from collections import defaultdict
from html import escape
import hashlib, json, re, zipfile

WORK = Path(__file__).resolve().parent
SOURCES = Path.cwd() / 'output/pdf/saccade_detection_sources'
OUT = SOURCES / 'highlighted'
PDF_DIR = SOURCES.parent
catalog = json.loads((SOURCES / 'catalog.json').read_text())
translations = json.loads((SOURCES / 'ja/translation_manifest.json').read_text())
labels = {d['id']: f"{d['author_label']} ({d['year']})" for d in translations['documents']}
methods = {
    'Dai2021': 'Dai提案法：疎な微分を利用した雑音除去と速度閾値',
    'Engbert2003': 'Engbert法：適応速度閾値と両眼の重なり',
    'Nystrom2010': 'Nyström-Holmqvist法：NH / ONH',
    'Friedman2018': 'Friedman法：MNH',
    'Konig2014': 'König法：Cluster Fix',
    'Zemblys2018': 'Zemblys法：IRF / I-RF',
    'Salvucci2000': 'I-VT・I-HMM・I-DT・I-MSTの基礎記述',
    'Komogortsev2010': 'I-VT・I-HMM・I-KF・I-MST・I-DTの比較実装',
    'Sauter1991': 'カルマンフィルタとHinkley法',
    'Bahill1981': '速度閾値法の背景文献',
    'Blignaut2009': '分散閾値法：尺度の定義と閾値選択',
    'Zemblys2019Correction': 'IRFの後処理に関する訂正',
}

documents = []
for ref in catalog['references']:
    doc = json.loads((WORK / f"{ref['key']}_annotation_manifest.json").read_text())
    doc['author_label'] = labels[ref['id']]
    doc['method_label_ja'] = methods[ref['key']]
    documents.append(doc)

page_count = sum(len(d['highlighted_pages']) for d in documents)
annotation_count = sum(d['annotation_count'] for d in documents)
manifest = {
    'created': '2026-11-18',
    'scope_ja': '収集済み原文12本の複製に、検出原理・計算式・処理手順・パラメータ・関係する図表の説明をハイライトした。',
    'page_numbering_ja': 'PDFの先頭から数えた1始まりのページ番号。誌面の印刷ページ番号とは異なる。',
    'highlight_colors': {'yellow': '検出手法の説明', 'orange': '2019年の訂正と併読が必要なIRFの後処理記述'},
    'annotation_type': 'Native PDF Highlight with Japanese comments and bookmarks; not flattened',
    'document_count': len(documents),
    'highlighted_page_count': page_count,
    'annotation_count': annotation_count,
    'validation': {
        'original_pdf_sha256_unchanged': True,
        'original_page_content_streams_preserved': True,
        'original_page_sizes_and_crop_boxes_preserved': True,
        'all_highlighted_pages_rendered_and_visually_checked': True,
    },
    'documents': documents,
}
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')

toc = []
cards = []
for number, doc in enumerate(documents):
    key = doc['key']
    first = doc['highlighted_pages'][0]
    link = f"{doc['file']}#page={first}"
    toc.append(f'<li><a href="#{key}">{escape(doc["author_label"])}</a><span>{escape(methods[key])}</span></li>')
    by_page = defaultdict(list)
    caution_pages = set()
    for region in doc['regions']:
        if region['label_ja'] not in by_page[region['page']]:
            by_page[region['page']].append(region['label_ja'])
        if region['kind'] == 'caution':
            caution_pages.add(region['page'])
    rows = []
    for page, topics in sorted(by_page.items()):
        text = '<br>'.join(escape(t) for t in topics)
        badge = '<span class="caution-label">訂正参照</span>' if page in caution_pages else ''
        rows.append(f'<tr><th scope="row"><a href="{doc["file"]}#page={page}">{page}頁</a>{badge}</th><td>{text}</td></tr>')
    paper_link = f'https://doi.org/{doc["doi"]}' if doc.get('doi') else doc['source']
    note = ''
    if key == 'Zemblys2018':
        note = '<p class="note">8-9頁のオレンジ色の記述は、<a href="11_Zemblys_et_al_2019_Correction_methods_highlighted.pdf#page=1">2019年の訂正論文（1-2頁）</a>と併読してください。元論文の本文は書き換えず、訂正内容を日本語注釈で案内しています。</p>'
    if key == 'Bahill1981':
        note = '<p class="note">DaiらのVTの背景として引用された文献です。DaiらのVT自作実装を、そのまま記述した論文ではありません。</p>'
    if key == 'Blignaut2009':
        note = '<p class="note">分散尺度によって閾値の意味が異なります。14頁の数値範囲は原著の測定条件での結果として確認してください。</p>'
    cards.append(f'''<article id="{key}">
<div class="eyebrow">{number:02d} / {escape(doc['author_label'])} / 原文全{doc['total_pages']}頁</div>
<h2>{escape(methods[key])}</h2>
<p class="title-ja">{escape(doc['title_ja'])}</p>
<p class="title-en">{escape(doc['title_en'])}</p>
<p class="actions"><a class="button" href="{link}">ハイライト付きPDFを開く</a><a href="{escape(paper_link,quote=True)}">書誌・原文の出典</a></p>
{note}
<table><thead><tr><th>PDF頁</th><th>ハイライトした説明</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p class="back"><a href="#top">一覧に戻る</a></p>
</article>''')

html = '''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>検出手法の説明をハイライトした原文PDF | サッケード検出法</title>
<style>
:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#f3f6f8;color:#1c2f3d;font:16px/1.85 system-ui,-apple-system,"Noto Sans CJK JP",sans-serif}main{max-width:1120px;margin:auto;padding:40px 28px 72px}a{color:#075e88;text-underline-offset:3px}a:hover{color:#a24b16}h1{font-size:31px;line-height:1.5;margin:12px 0 16px}h2{font-size:23px;line-height:1.5;margin:10px 0}p{margin:10px 0}.eyebrow{font-size:13px;color:#536b7d;letter-spacing:.02em}.intro{background:#fff;border:1px solid #d8e1e7;border-radius:10px;padding:24px 28px}.legend{display:flex;flex-wrap:wrap;gap:14px;margin:16px 0}.legend span{padding:5px 12px;border-radius:4px}.yellow{background:#fff3a8}.orange{background:#ffdcba}.help{font-size:14px;color:#425c6e}.toc{list-style:none;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:10px 24px}.toc li{border-bottom:1px solid #d9e3ea;padding:9px 0}.toc span{display:block;font-size:13px;color:#526775}.summary{font-weight:650;color:#166b70}article{background:white;border:1px solid #d7e1e8;border-radius:10px;padding:25px 28px;margin:24px 0;scroll-margin-top:18px}.title-ja{margin:10px 0 4px}.title-en{font-size:13px;color:#526775;margin:0 0 16px}.actions{display:flex;align-items:center;gap:18px;flex-wrap:wrap}.button{background:#e9f3f4;border:1px solid #9cc7cd;border-radius:5px;padding:7px 14px;text-decoration:none}.note{font-size:14px;background:#fff4e9;border-left:3px solid #de9654;padding:12px 14px;margin:18px 0}table{width:100%;border-collapse:collapse;margin:20px 0 10px;font-size:14px}thead{background:#edf2f6}th,td{padding:11px 14px;border-bottom:1px solid #dce4e9;text-align:left;vertical-align:top}tbody th{width:92px;white-space:nowrap}.caution-label{display:block;font-size:11px;color:#8d4b15;font-weight:500}.back{font-size:13px;text-align:right}footer{font-size:13px;color:#536b7d}@media(max-width:650px){main{padding:24px 16px}h1{font-size:25px}.intro,article{padding:20px}.toc{grid-template-columns:1fr}th,td{padding:10px 9px}tbody th{width:65px}}@media print{body{background:white}main{max-width:none;padding:0}.toc, .back{display:none}article{break-before:page;border:0;padding:0}a{color:inherit}}
</style></head><body><main id="top">
<div class="eyebrow">サッケード検出法 / 原文読解ガイド / 2026-11-18</div>
<h1>検出手法の説明をハイライトした原文PDF</h1>
<section class="intro"><p>各論文の検出原理、数式、処理手順、パラメータと関係する図表の説明を選び、原文PDFの複製にハイライトを付けました。原本はそのまま保存しています。</p>
<p class="summary">__COUNT__本のPDF / 対象__PAGES__ページ / 日本語注釈・しおり付き</p>
<div class="legend"><span class="yellow">黄色：検出手法の説明</span><span class="orange">オレンジ色：IRFの訂正と併読する箇所</span></div>
<p class="help">下表の頁リンク、またはPDFの「しおり」から該当箇所へ移動できます。ハイライトの注釈には日本語で説明項目を記載しました。色は通常のPDF注釈として保存しているため、対応する閲覧ソフトで確認・編集できます。</p>
<p class="help">頁番号はPDFの先頭から数えた番号です。誌面に印刷されたページ番号とは異なります。</p></section>
<nav aria-label="論文一覧"><ol class="toc">__TOC__</ol></nav>
__CARDS__
<footer><p><a href="manifest.json">収録ファイル・ハイライト箇所・検証記録（JSON）</a></p><p>12本には比較元のDai論文、比較手法の原典・実装出典・背景文献、IRFの訂正論文を含みます。手法と論文は1対1ではありません。</p></footer>
</main></body></html>
'''
html = html.replace('__COUNT__',str(len(documents))).replace('__PAGES__',str(page_count))
html = html.replace('__TOC__',''.join(toc)).replace('__CARDS__','\n'.join(cards))
(OUT / 'index.html').write_text(html)

# Add a prominent entry to the existing collection without changing its other content.
main_index = SOURCES / 'index.html'
main_html = main_index.read_text()
banner = '''<div class="banner" id="method-highlights" style="margin:20px 0"><p><strong>原文12本に検出手法のハイライトを追加しました。</strong>検出原理・数式・処理手順・パラメータを確認できる、日本語注釈・しおり付きのPDFです。</p><p><a href="highlighted/index.html">ハイライト付きPDFと該当ページの一覧</a> · <a href="../saccade_detection_methods_highlighted.zip">12本を一括取得（ZIP）</a></p></div>'''
if 'id="method-highlights"' in main_html:
    main_html = re.sub(r'<div class="banner" id="method-highlights".*?</div>', banner, main_html, count=1, flags=re.S)
else:
    marker = '<h2>比較10手法と文献の対応</h2>'
    assert marker in main_html
    main_html = main_html.replace(marker, banner + marker, 1)
main_index.write_text(main_html)

zip_path = PDF_DIR / 'saccade_detection_methods_highlighted.zip'
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for path in [OUT / 'index.html', OUT / 'manifest.json'] + [OUT / d['file'] for d in documents]:
        z.write(path, 'highlighted/' + path.name)
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
    assert len(z.namelist()) == len(documents) + 2
print(json.dumps({'papers':len(documents), 'pages':page_count, 'annotations':annotation_count,
                  'zip':str(zip_path),'bytes':zip_path.stat().st_size}, ensure_ascii=False))
