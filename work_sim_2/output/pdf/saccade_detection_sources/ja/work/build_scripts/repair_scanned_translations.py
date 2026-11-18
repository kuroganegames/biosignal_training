from pathlib import Path
import json, unicodedata, re, sys
import pymupdf as fitz
B=Path('/media/kurogane/backup/bisignal_training/work_sim_2/output/pdf/saccade_detection_sources');O=B/'ja'
boxes=json.loads((O/'work/scanned_figure_rectangles.json').read_text())
font='/tmp/saccade_babeldoc_cache/fonts/SourceHanSerifJP-Regular.ttf'
bold='/tmp/saccade_babeldoc_cache/fonts/SourceHanSansJP-Bold.ttf'
repairs=[]
mapping={
 '2 プロブレムステートメント':'2 問題設定',
 '3 信号モデリング 眼球運動':'3 信号のモデル化',
 '4.4 アルゴリズム サッケードの原理':'4.4 アルゴリズム',
 '假説':'仮説',
 'アリasing':'エイリアシング',
 'ニステガム分析':'眼振解析',
 'ノイスタグムスの迅速相':'眼振の急速相',
}
for stem,figures in boxes.items():
 selected=[x for x in sys.argv[1:] if not x.startswith('--')]
 if selected and not any(stem.startswith(x) for x in selected):continue
 f=O/(stem+'_ja.pdf'); d=fitz.open(f);src=fitz.open(B/(stem+'.pdf'))
 for entry in figures:
  n=entry['page']-1;r=fitz.Rect(entry['rect'])+(-1.5,-1.5,1.5,1.5);r=r & src[n].rect
  pix=src[n].get_pixmap(matrix=fitz.Matrix(3,3),clip=r,alpha=False)
  p=d[n];p.add_redact_annot(r,fill=(1,1,1));p.apply_redactions(images=0,graphics=0,text=0)
  p.insert_image(r,stream=pix.tobytes('png'),overlay=True)
  repairs.append({'document':stem,'page':n+1,'action':'restore_original_figure','rect':list(r)})
 for n,p in ([] if '--figures-only' in sys.argv else enumerate(d)):
  if n==0:continue
  changes=[]
  for b in p.get_text('dict')['blocks']:
   if 'lines' not in b:continue
   spans=[s for l in b['lines'] for s in l['spans']]
   old=unicodedata.normalize('NFKC',''.join(s['text'] for s in spans));new=old
   for a,z in mapping.items():new=new.replace(a,z)
   if '\\mathbf' in new:new='パラメータのベクトルを β とする。'
   if old!=new:
    changes.append((fitz.Rect(b['bbox']),old,new,min(s['size'] for s in spans),'JPRepairBold' if new[:1].isdigit() else 'JPRepair'))
  if changes:
   for r,old,new,size,name in changes:p.add_redact_annot(r+(-.3,-.3,.3,.3),fill=(1,1,1))
   p.apply_redactions(images=0,graphics=0,text=0)
   p.insert_font(fontname='JPRepair',fontfile=font);p.insert_font(fontname='JPRepairBold',fontfile=bold)
   for r,old,new,size,name in changes:
    size=min(size,10)
    while p.insert_textbox(r+(0,-.8,1,1),new,fontsize=size,fontname=name,lineheight=1.1)<0:
     size-=.3
     if size<5:raise ValueError((stem,n,new))
    repairs.append({'document':stem,'page':n+1,'action':'correct_text','before':old,'after':new,'size':size})
 tmp=f.with_suffix('.repaired.pdf');d.save(tmp,garbage=4,deflate=True);d.close();tmp.replace(f)
 ja=fitz.open(f);dual=fitz.open()
 for i in range(len(src)):
  dual.insert_pdf(src,from_page=i,to_page=i);dual.insert_pdf(ja,from_page=i,to_page=i)
 dual.set_metadata({'title':stem+' | 原文・日本語交互対訳','author':src.metadata.get('author',''),'subject':'機械翻訳、冒頭頁の原文照合、図版の原文保持'})
 dual.save(O/(stem+'_en_ja.pdf'),garbage=4,deflate=True)
(O/'work/scanned_pdf_repairs.json').write_text(json.dumps(repairs,ensure_ascii=False,indent=2))
print('Completed repairs:',len(repairs))
