from pathlib import Path
import sys,json,tempfile,subprocess,pymupdf as fitz
B=Path('/media/kurogane/backup/bisignal_training/work_sim_2/output/pdf/saccade_detection_sources/ja')
patch=Path(sys.argv[1]).resolve();out=Path(tempfile.mkdtemp(prefix='jp_pdf_repairs_'))
subprocess.run(['/home/kurogane/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3','/tmp/render_repair_overlays.py',str(patch),str(out)],check=True)
data=json.loads(patch.read_text());manifest=json.loads((out/'manifest.json').read_text())
for entry in manifest:
 name=entry['document'];file=B/name;d=fitz.open(file);overlay=fitz.open(entry['overlay']);items=[x for x in data if x['document']==name]
 for page_no in sorted(set(x['page'] for x in items)):
  p=d[page_no-1]
  for x in [v for v in items if v['page']==page_no]:p.add_redact_annot(fitz.Rect(x.get('erase_rect',x['rect'])),fill=(1,1,1))
  p.apply_redactions(images=0,graphics=0,text=0)
 for overlay_no,x in enumerate(entry['items']):
  p=d[x['page']-1];r=fitz.Rect(x['rect']);bounds=fitz.Rect()
  for block in overlay[overlay_no].get_text('blocks'):
   if block[6]==0:bounds|=fitz.Rect(block[:4])
  assert not bounds.is_empty,x
  bounds+=(-.2,-.2,.2,.2)
  scale=min(1,r.width/bounds.width,r.height/bounds.height)
  width=bounds.width*scale;height=bounds.height*scale
  left=r.x0+(r.width-width)/2 if x.get('align',0)==1 else r.x0
  target=fitz.Rect(left,r.y0,left+width,r.y0+height)
  p.show_pdf_page(target,overlay,overlay_no,clip=bounds,overlay=True)
 tmp=file.with_suffix('.repaired.pdf');d.save(tmp,garbage=4,deflate=True);d.close();tmp.replace(file)
 print('Applied',len(items),'typeset repairs to',name)
