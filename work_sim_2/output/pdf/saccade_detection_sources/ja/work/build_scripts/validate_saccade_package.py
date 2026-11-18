from pathlib import Path
import json,hashlib,zipfile,re
from urllib.parse import urlparse,unquote
from html.parser import HTMLParser
from pypdf import PdfReader
B=Path('/media/kurogane/backup/bisignal_training/work_sim_2/output/pdf/saccade_detection_sources');O=B/'ja';D=B.parent
m=json.loads((O/'translation_manifest.json').read_text());assert len(m['documents'])==12
results=[]
for x in m['documents']:
 src=B/x['source'];ja=O/x['japanese']['file'];pair=O/x['bilingual']['file']
 assert hashlib.sha256(src.read_bytes()).hexdigest()==x['source_sha256']
 assert hashlib.sha256(ja.read_bytes()).hexdigest()==x['japanese']['sha256']
 assert hashlib.sha256(pair.read_bytes()).hexdigest()==x['bilingual']['sha256']
 counts=[len(PdfReader(p).pages) for p in [src,ja,pair]]
 assert counts[0]==counts[1] and counts[2]==counts[0]*2
 results.append({'document':x['id'],'pages':counts})
merged=PdfReader(D/'saccade_detection_papers_ja.pdf');assert len(merged.pages)==157;assert len(merged.outline)==12;assert len(merged.pages[0]['/Annots'])==12
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,t,a):
  if t=='a':self.links.extend(v for k,v in a if k=='href')
for f in [B/'index.html',O/'index.html']:
 parser=Links();parser.feed(f.read_text())
 for link in parser.links:
  u=urlparse(link)
  if u.scheme or not u.path:continue
  assert (f.parent/unquote(u.path)).exists(),(f,link)
zfile=D/'saccade_detection_sources_with_japanese.zip'
with zipfile.ZipFile(zfile) as z:
 assert z.testzip() is None
 names=set(z.namelist());assert sum(n.endswith('.pdf') for n in names)==37
 assert all('/work/' not in n for n in names)
print(json.dumps({'papers':12,'original_pages':sum(r['pages'][0] for r in results),'japanese_pages':sum(r['pages'][1] for r in results),'bilingual_pages':sum(r['pages'][2] for r in results),'combined_pages':157,'bookmarks':12,'clickable_contents':12,'zip_pdf_files':37,'original_checksums':'unchanged','html_links':'valid','zip_integrity':'passed'},ensure_ascii=False,indent=2))
(O/'work/final_validation.json').write_text(json.dumps({'documents':results,'combined_pages':157,'bookmarks':12,'clickable_contents':12,'zip_pdf_files':37,'original_checksums':'unchanged','html_links':'valid','zip_integrity':'passed'},ensure_ascii=False,indent=2))
