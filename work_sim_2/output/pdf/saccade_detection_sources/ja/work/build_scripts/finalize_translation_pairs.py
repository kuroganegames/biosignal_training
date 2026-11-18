from pathlib import Path
import ast,json,sys,pymupdf as fitz
B=Path('/media/kurogane/backup/bisignal_training/work_sim_2/output/pdf/saccade_detection_sources');O=B/'ja'
refs=json.loads((B/'catalog.json').read_text())['references']
tree=ast.parse(Path('/tmp/package_saccade_translations.py').read_text())
titles=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='titles' for x in n.targets))
for r,title in zip(refs,titles):
 if sys.argv[1:] and r['id'][:2] not in sys.argv[1:]:continue
 source=B/r['local_pdf'];mono=O/(r['id']+'_ja.pdf');pair=O/(r['id']+'_en_ja.pdf')
 assert mono.exists(),mono
 ja=fitz.open(mono);meta=ja.metadata
 meta.update(title=title,author=r['authors'],subject='日本語訳。機械翻訳と用語調整・抜き取り照合。詳細は translation_manifest.json を参照。',keywords='saccade, eye movement, 日本語訳')
 ja.set_metadata(meta);ja.xref_set_key(ja.pdf_catalog(),'Lang','(ja-JP)');ja.subset_fonts()
 tmp=mono.with_suffix('.final.pdf');ja.save(tmp,garbage=4,deflate=True);ja.close();tmp.replace(mono)
 ja=fitz.open(mono);src=fitz.open(source);dual=fitz.open();toc=[]
 assert len(ja)==len(src),(r['id'],len(ja),len(src))
 for i in range(len(src)):
  dual.insert_pdf(src,from_page=i,to_page=i,final=0);dual.insert_pdf(ja,from_page=i,to_page=i,final=0)
  toc.append([1,f'{i+1}頁：原文・日本語',2*i+1])
 dual.set_toc(toc);dual.set_metadata({'title':title+'（原文対訳版）','author':r['authors'],'subject':'原文ページの直後に、対応する日本語ページを配置。機械翻訳・一部原文照合。'})
 dual.save(pair,garbage=4,deflate=True)
 print(mono.name,len(ja),'Japanese pages;',len(dual),'bilingual pages')
