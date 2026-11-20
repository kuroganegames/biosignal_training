from pathlib import Path
from html import escape
from html.parser import HTMLParser
import hashlib
import json
import math
import shutil
import zipfile

from lxml import etree
from pypdf import PdfReader, PdfWriter
from content import METHODS

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT.parent
PDF = ROOT / 'pdf'
PDF.mkdir(exist_ok=True)
catalog = json.loads((SOURCES / 'catalog.json').read_text())
refs = {r['key']: r for r in catalog['references']}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
documents = []
writer = PdfWriter()
page_offset = 0

for m in METHODS:
    name = m['id'] + '_ja'
    pdf = PDF / (name + '.pdf')
    docx = ROOT / 'docx' / (name + '.docx')
    shutil.copy2(ROOT / '_build' / 'render' / m['id'] / pdf.name, pdf)
    reader = PdfReader(pdf)
    expected = 5 if m['id'] == '07_Zemblys_IRF' else 4
    assert len(reader.pages) == expected, m['id']
    for i, page in enumerate(reader.pages):
        txt = page.extract_text()
        assert len(txt) > 100 and '\ufffd' not in txt, (m['id'], i)
    with zipfile.ZipFile(docx) as z:
        assert z.testzip() is None
        style = etree.fromstring(z.read('word/styles.xml'))
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        assert not style.findall('.//w:pBdr', ns)
        images = [n for n in z.namelist() if n.startswith('word/media/')]
        assert len(images) == len(m['equations']), (m['id'], images)
    for page in reader.pages:
        writer.add_page(page)
    writer.add_outline_item(m['title'], page_offset)
    item = {
        'id': m['id'], 'title_ja': m['title'], 'pages': len(reader.pages),
        'combined_start_page': page_offset + 1,
        'pdf': {'file': str(pdf.relative_to(ROOT)), 'sha256': sha(pdf)},
        'docx': {'file': str(docx.relative_to(ROOT)), 'sha256': sha(docx)},
        'equation_images': len(m['equations']),
        'references': [{k: refs[key].get(k) for k in
                        ['key', 'title', 'authors', 'year', 'doi', 'source', 'sha256']}
                       for key in m['refs']],
        'source_locations': m['locations'],
    }
    documents.append(item)
    page_offset += len(reader.pages)

combined = ROOT / 'saccade_method_guides_ja.pdf'
writer.add_metadata({'/Title': 'サッケード検出法 技術解説 全11手法',
                     '/Subject': '原理・数式・処理手順・パラメータ・擬似コード・計算例・原典',
                     '/Author': 'Codex'})
writer.write(combined)
assert len(PdfReader(combined).pages) == 45
assert len(PdfReader(combined).outline) == 11

rows = []
for m, d in zip(METHODS, documents):
    rows.append(f'''<tr><th scope="row">{escape(m['title'])}</th>
<td>{escape(m['overview'])}</td><td class="pages">{d['pages']}頁</td>
<td class="files"><a href="{d['pdf']['file']}">PDF</a>
<a href="{d['docx']['file']}">Word</a></td></tr>''')

html = '''<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>サッケード検出法：手法別技術解説</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f5f7f8;color:#202d36;font:16px/1.8 system-ui,"Noto Sans CJK JP",sans-serif}
main{max-width:1120px;margin:auto;padding:40px 28px 72px}h1{font-size:30px;line-height:1.5;margin:8px 0 18px}h2{font-size:22px;margin:30px 0 12px}
p{margin:12px 0}a{color:#0b627d;text-underline-offset:3px}.meta{font-size:13px;color:#516570}.summary{padding:16px 22px;background:#eaf1f3;border-left:4px solid #347987}
.tablewrap{overflow:auto}table{width:100%;border-collapse:collapse;background:#fff;font-size:14px}th,td{border-bottom:1px solid #d9e1e6;padding:15px 16px;text-align:left;vertical-align:top}thead{background:#e7eef1}tbody th{width:26%;min-width:190px}td.pages{white-space:nowrap}td.files{min-width:90px}td.files a{display:block;padding:3px 0}.download{display:inline-block;padding:8px 16px;margin:8px 0;background:#fff;border:1px solid #a7c3cd;border-radius:5px;text-decoration:none}
@media(max-width:650px){main{padding:24px 16px}h1{font-size:25px}table{min-width:780px}}@media print{body{background:#fff}main{padding:0}tr{break-inside:avoid}a{color:inherit}}
</style></head><body><main>
<p class="meta">サッケード検出法の技術解説 · 作成日 2026年11月18日</p>
<h1>各手法の原理と実装手順</h1>
<p><a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC8212426/">Daiら（2021）</a>の比較対象10手法と、Daiら自身の提案法を、手法別の日本語ドキュメントにまとめました。各4～5ページ、合計45ページです。</p>
<div class="summary"><p>各冊の内容：入力と出力、原理と数式、具体的な処理手順、必要なパラメータ、擬似コード、数値例、長所と制約、検証項目、原典と確認箇所。</p>
<p>原論文の方法を整理した技術解説です。パラメータは原著の設定例、数値例は説明用に作成した例として区別しています。擬似コードは処理を理解するためのもので、性能を検証済みの実装ではありません。</p></div>
<p><a class="download" href="saccade_method_guides_ja.pdf">全11手法の合本PDFを開く（45ページ・しおり付き）</a></p>
<h2>手法別ドキュメント</h2>
<div class="tablewrap"><table><thead><tr><th>手法</th><th>解説の中心</th><th>頁数</th><th>ファイル</th></tr></thead><tbody>
''' + '\n'.join(rows) + '''
</tbody></table></div>
<h2>読み方と収録範囲</h2>
<p>PDF版とWord版の本文は同じです。Word版では本文と表を編集できます。数式は表示を安定させるため画像として挿入しています。合本PDFのページ欄には各冊のページ番号が表示され、しおりから手法を選択できます。</p>
<p>VT・DTの代表的原理、HMM・MST・KFの比較実装と原典の違い、MNHで変更された境界処理、IRFの2019年訂正を明記しています。IRFには14種類の初期特徴量と計算窓の説明を追加しました。論文12本と検出手法の数は一致しません。背景文献・訂正論文は対応する手法の参考資料に含めています。</p>
<p>引用文献のDOIと、収集した原文PDF内の確認箇所を各冊の末尾に記載しました。<a href="manifest.json">ファイル一覧・文献情報・SHA-256</a></p>
</main></body></html>'''
(ROOT / 'index.html').write_text(html)

manifest = {
    'created': '2026-11-18', 'language': 'ja',
    'scope': 'Dai 2021の比較対象10手法とDai提案法。原文論文に基づく手法別の技術解説。',
    'document_count': 11, 'total_pages': 45,
    'formats': ['PDF', 'DOCX'], 'docx_equations': 'PNG images; body text and tables are editable.',
    'pseudocode_status': 'Explanatory pseudocode; not a benchmarked detector implementation.',
    'visual_review': 'All 45 pages rendered and visually inspected; revised pages rechecked.',
    'combined_pdf': {'file': combined.name, 'pages': 45, 'bookmarks': 11, 'sha256': sha(combined)},
    'documents': documents,
}
(ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')

# Add discoverable links to the existing literature collection without replacing it.
index = SOURCES / 'index.html'
current = index.read_text()
marker = '<div class="banner" id="method-guides"'
banner = '''<div class="banner" id="method-guides" style="margin:20px 0"><p><strong>手法別の技術解説を追加しました。</strong>比較対象10手法＋Dai提案法について、原理・数式・処理手順・パラメータ・擬似コード・計算例を各4～5ページにまとめています。</p><p><a href="method_guides/index.html">全11手法のPDF・Word一覧</a> · <a href="method_guides/saccade_method_guides_ja.pdf">技術解説の合本PDF（45ページ）</a> · <a href="../saccade_method_guides_ja.zip">技術解説を一括取得（ZIP）</a></p></div>'''
if marker not in current:
    current = current.replace('<h2>比較10手法と文献の対応</h2>', banner + '<h2>比較10手法と文献の対応</h2>')
    index.write_text(current)

archive = SOURCES.parent / 'saccade_method_guides_ja.zip'
release_files = [ROOT / 'index.html', ROOT / 'manifest.json', combined]
release_files += sorted(PDF.glob('*.pdf')) + sorted((ROOT / 'docx').glob('*.docx'))
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in release_files:
        z.write(p, 'method_guides/' + str(p.relative_to(ROOT)))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist()) == 25

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.hrefs = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.hrefs.extend(v for k, v in attrs if k == 'href')

for index_file in [ROOT / 'index.html', SOURCES / 'index.html']:
    parser = Links(); parser.feed(index_file.read_text())
    for href in parser.hrefs:
        if href.startswith(('http:', 'https:', '#')): continue
        assert (index_file.parent / href.split('#')[0]).exists(), (index_file, href)

# Preserve the collected source PDFs, Japanese translations and bilingual PDFs.
old = json.loads((SOURCES / 'ja' / 'translation_manifest.json').read_text())
preserved = 0
for item in old['documents']:
    assert sha(SOURCES / item['source']) == item['source_sha256']
    preserved += 1
    for key in ['japanese', 'bilingual']:
        assert sha(SOURCES / 'ja' / item[key]['file']) == item[key]['sha256']
        preserved += 1

# Check the hand-worked examples; these are arithmetic checks, not detector tests.
assert math.isclose((9/12)**2 + (15/18)**2, 1.2569444444444446)
assert math.isclose(.7*17 + .3*(4 + 3*3), 15.8)
assert math.isclose(10*(.05/.95)**2, .02770083102493075)
assert math.isclose(.5**2 + (-.5)**2 + 3**2, 9.5)
assert round(4*math.sqrt(4)*math.exp(5*.04)*.2, 2) == 1.95
assert round(4*math.sqrt(4)*math.exp(5*.12)*.2, 2) == 2.92

validation = {'documents': 11, 'pdf_pages': 45, 'equation_images': sum(d['equation_images'] for d in documents),
              'visually_reviewed_pages': 45, 'combined_bookmarks': 11,
              'archive_files': 25, 'archive_crc': 'pass', 'local_links': 'pass',
              'existing_pdf_hashes_unchanged': preserved, 'worked_example_arithmetic': 'pass',
              'archive_bytes': archive.stat().st_size, 'archive_sha256': sha(archive)}
(ROOT / '_build' / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n')
print(json.dumps(validation, indent=2))
