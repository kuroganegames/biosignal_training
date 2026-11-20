from pathlib import Path
from collections import defaultdict
import hashlib, json, re, sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DictionaryObject, FloatObject, NameObject,
                          NumberObject, TextStringObject, DecodedStreamObject, Fit)
from selections import SELECTIONS

WORK=Path(__file__).resolve().parent
SOURCES=Path.cwd()/'output/pdf/saccade_detection_sources'
OUT=SOURCES/'highlighted'
CAT=json.loads((SOURCES/'catalog.json').read_text())['references']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
arr=lambda values:ArrayObject([FloatObject(v) for v in values])
COLORS={'method':(1.0,0.90,0.12),'caution':(1.0,0.57,0.12)}

def merge_rows(rects):
    # Merge subscript/superscript fragments with their base line, avoiding darker overlaps.
    merged=[]
    for rect in sorted(rects,key=lambda r:(r[1],r[0])):
        r=list(rect)
        if merged and r[1]<merged[-1][3]-.2:
            old=merged[-1]
            old[:]=[min(old[0],r[0]),min(old[1],r[1]),max(old[2],r[2]),max(old[3],r[3])]
        else: merged.append(r)
    return merged

def highlight(writer,page_index,rects,label,kind,uid,page_height):
    # pdfplumber uses top-down coordinates; PDF annotations use bottom-up coordinates.
    boxes=[[x0-.3,page_height-bottom-.15,x1+.3,page_height-top+.15] for x0,top,x1,bottom in rects]
    bounds=[min(r[0] for r in boxes),min(r[1] for r in boxes),max(r[2] for r in boxes),max(r[3] for r in boxes)]
    quads=[]
    for l,b,r,t in boxes:quads += [l,t,r,t,l,b,r,b]
    color=COLORS[kind]
    appearance=DecodedStreamObject()
    instructions=['q','/GS0 gs',f'{color[0]} {color[1]} {color[2]} rg']
    for l,b,r,t in boxes:
        instructions.append(f'{l-bounds[0]:.3f} {b-bounds[1]:.3f} {r-l:.3f} {t-b:.3f} re')
    instructions += ['f','Q']
    appearance.set_data(('\n'.join(instructions)+'\n').encode('ascii'))
    gs=DictionaryObject({NameObject('/Type'):NameObject('/ExtGState'),NameObject('/ca'):FloatObject(.34),
                         NameObject('/CA'):FloatObject(.34),NameObject('/BM'):NameObject('/Multiply')})
    appearance.update({NameObject('/Type'):NameObject('/XObject'),NameObject('/Subtype'):NameObject('/Form'),
        NameObject('/FormType'):NumberObject(1),NameObject('/BBox'):arr([0,0,bounds[2]-bounds[0],bounds[3]-bounds[1]]),
        NameObject('/Resources'):DictionaryObject({NameObject('/ExtGState'):DictionaryObject({NameObject('/GS0'):gs})})})
    annot=DictionaryObject({NameObject('/Type'):NameObject('/Annot'),NameObject('/Subtype'):NameObject('/Highlight'),
        NameObject('/Rect'):arr(bounds),NameObject('/QuadPoints'):arr(quads),NameObject('/C'):arr(color),
        NameObject('/CA'):FloatObject(.34),NameObject('/F'):NumberObject(4),
        NameObject('/T'):TextStringObject('検出手法の読解ガイド'),NameObject('/Subj'):TextStringObject(label),
        NameObject('/Contents'):TextStringObject(f'{label}\n原文PDF {page_index+1}頁。検出手法を読み直すための注釈です。'),
        NameObject('/NM'):TextStringObject(uid),
        NameObject('/AP'):DictionaryObject({NameObject('/N'):writer._add_object(appearance)})})
    writer.add_annotation(page_index,annot)
    return boxes

def run(ref):
    key=ref['key']; source=SOURCES/ref['local_pdf']; output=OUT/(source.stem+'_methods_highlighted.pdf')
    reader=PdfReader(source); writer=PdfWriter(); writer.clone_document_from_reader(reader)
    writer.pdf_header=b'%PDF-1.7'
    layouts={p['page']:p for p in json.loads((WORK/(key+'_layout.json')).read_text())}
    regions=[]; count=0; used=set(); root=None
    for si,spec in enumerate(SELECTIONS[key]):
        label,ranges=spec[:2];kind=spec[2] if len(spec)>2 else 'method'
        first=True
        for range_code in ranges.split():
            match=re.fullmatch(r'(\d{2})([LR])(\d{3})-(\d{3})',range_code)
            assert match,range_code
            ps,col,lo,hi=match.groups();number=int(ps);p=layouts[number]
            ids=[f'{ps}-{col}-{i:03d}' for i in range(int(lo),int(hi)+1)]
            lookup={line['id']:line for line in p['lines']}
            assert all(i in lookup for i in ids),(key,range_code)
            assert not (set(ids)&used),(key,range_code,'duplicate selection')
            used.update(ids)
            lines=[lookup[i] for i in ids]
            rects=merge_rows([line['rect'] for line in lines])
            assert rects
            if root is None:
                root=writer.add_outline_item('検出手法の説明（ハイライト）',number-1,fit=Fit.fit_horizontally(p['height']-rects[0][1]+12))
            if first:
                writer.add_outline_item(label,number-1,parent=root,fit=Fit.fit_horizontally(p['height']-rects[0][1]+12))
                first=False
            # Short multi-line annotations are easier to select and inspect in a PDF reader.
            for chunk_index,start in enumerate(range(0,len(rects),12)):
                chunk=rects[start:start+12]
                uid=f'method-{key}-{si:02d}-{range_code}-{chunk_index:02d}'
                highlight(writer,number-1,chunk,label,kind,uid,p['height']);count+=1
            regions.append({'label_ja':label,'page':number,'line_range':range_code,'kind':kind,
                            'rectangles_top_down':rects})
    writer.write(output)
    reread=PdfReader(output);assert len(reread.pages)==len(reader.pages)
    annotations=[]
    for i,(old,new) in enumerate(zip(reader.pages,reread.pages)):
        assert old.get_contents().get_data()==new.get_contents().get_data(),(key,i,'page content changed')
        assert old.mediabox==new.mediabox and old.cropbox==new.cropbox and old.rotation==new.rotation
        for a in new.get('/Annots',[]):
            a=a.get_object()
            if not str(a.get('/NM','')).startswith('method-'):continue
            assert a['/Subtype']=='/Highlight' and len(a['/QuadPoints'])%8==0
            assert a['/AP']['/N'].get_object().get_data()
            assert str(a['/Contents']) and str(a['/Subj'])
            for n in range(0,len(a['/QuadPoints']),2):
                x,y=a['/QuadPoints'][n:n+2]
                assert new.cropbox.left-1<=x<=new.cropbox.right+1,(key,i,x)
                assert new.cropbox.bottom-1<=y<=new.cropbox.top+1,(key,i,y)
            annotations.append(a)
    assert len(annotations)==count
    assert sha(source)==ref['sha256'],key
    result={'key':key,'title_ja':ref.get('title_ja',ref['title']),'title_en':ref['title'],
            'source_pdf':ref['local_pdf'],'source_sha256':sha(source),'file':output.name,
            'sha256':sha(output),'total_pages':len(reader.pages),'highlighted_pages':sorted(set(r['page'] for r in regions)),
            'annotation_count':count,'topics':[s[0] for s in SELECTIONS[key]],'regions':regions,
            'source_content_preserved':True,'source':ref['source'],'doi':ref.get('doi')}
    (WORK/(key+'_annotation_manifest.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return {'key':key,'pages':result['highlighted_pages'],'annotations':count}

if __name__=='__main__':
    for ref in CAT:
        if len(sys.argv)>1 and ref['key'] not in sys.argv[1:]:continue
        print(json.dumps(run(ref),ensure_ascii=False),flush=True)
