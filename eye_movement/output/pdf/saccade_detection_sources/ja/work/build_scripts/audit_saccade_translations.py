from pathlib import Path
import pymupdf,json,re,unicodedata,sys
BASE=Path('/media/kurogane/backup/bisignal_training/work_sim_2/output/pdf/saccade_detection_sources');OUT=BASE/'ja';QA=OUT/'work/qa';QA.mkdir(exist_ok=True)
records=json.loads((QA/'page_audit.json').read_text()) if sys.argv[1:] and (QA/'page_audit.json').exists() else []
if sys.argv[1:]:records=[r for r in records if r['source'][:2] not in sys.argv[1:]]
for target in sorted(OUT.glob('*_ja.pdf')):
 if target.stem.endswith('_en_ja'):continue
 if sys.argv[1:] and target.name[:2] not in sys.argv[1:]:continue
 source=BASE/(target.stem.removesuffix('_ja')+'.pdf')
 if not source.exists():continue
 a=pymupdf.open(source);b=pymupdf.open(target);pages=[]
 for i,p in enumerate(b):
  pymupdf.TOOLS.mupdf_warnings(reset=True)
  text=unicodedata.normalize('NFKC',p.get_text());jp=len(re.findall(r'[\u3040-\u30ff\u3400-\u9fff]',text));en=len(re.findall(r'[A-Za-z]+',text))
  page={'page':i+1,'japanese_chars':jp,'english_words':en,'replacement_chars':text.count('\ufffd'),'source_chars':len(a[i].get_text()) if i<len(a) else None}
  # Capturing a small thumbnail of every page helps locate layout anomalies.
  p.get_pixmap(matrix=pymupdf.Matrix(.55,.55)).save(str(QA/(target.stem+'_p'+str(i+1).zfill(2)+'.png')))
  page['render_warnings']=pymupdf.TOOLS.mupdf_warnings(reset=True)
  pages.append(page)
 text='\n\n'.join(unicodedata.normalize('NFKC',p.get_text()) for p in b)
 (QA/(target.stem+'.txt')).write_text(text)
 record={'source':source.name,'translation':target.name,'source_pages':len(a),'translation_pages':len(b),'pages':pages,'low_japanese_pages':[p['page'] for p in pages if p['japanese_chars']<50 and (p['source_chars'] or 0)>500]}
 records.append(record)
 print(target.name,'pages',len(a),'->',len(b),'low Japanese:',record['low_japanese_pages'])
(QA/'page_audit.json').write_text(json.dumps(sorted(records,key=lambda x:x['source']),ensure_ascii=False,indent=2))
