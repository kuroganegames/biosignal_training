from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import json
import pdfplumber

ROOT=Path.cwd()/'output/pdf/saccade_detection_sources'
OUT=Path(__file__).resolve().parent
SELECT={
 'Dai2021':[4,5,6,7,8,9], 'Engbert2003':[2,3],
 'Nystrom2010':[4,5,6,7,8,9,10], 'Friedman2018':[4,5,6,7,8,9,10,11],
 'Konig2014':[2,3,4,5], 'Zemblys2018':[4,5,6,7,8,9],
 'Salvucci2000':[3,4,5], 'Komogortsev2010':[3,4],
 'Sauter1991':[2,3,4,5,6], 'Bahill1981':[3,4],
 'Blignaut2009':[2,3,4,5,6,7,13,14], 'Zemblys2019Correction':[1,2]
}

def run(ref):
    key=ref['key']; pages=[]
    with pdfplumber.open(ROOT/ref['local_pdf']) as doc:
        for number in SELECT[key]:
            p=doc.pages[number-1]; w,h=p.width,p.height
            lines=[]
            bx0,bt,bx1,bb=p.bbox; mid=(bx0+bx1)/2
            for col,(x0,x1) in [('L',(bx0,mid)),('R',(mid,bx1))]:
                crop=p.crop((x0,bt,x1,bb))
                ll=crop.extract_text_lines(x_tolerance=2,y_tolerance=2.5,return_chars=True)
                for i,line in enumerate(ll):
                    rect=[round(line[k],2) for k in ['x0','top','x1','bottom']]
                    # Retain individual character bounds for selective, tightly aligned highlighting.
                    chars=[[round(c[k],2) for k in ['x0','top','x1','bottom']] for c in line['chars'] if c.get('text','').strip()]
                    lines.append({'id':f'{number:02d}-{col}-{i:03d}','col':col,'rect':rect,'text':line['text'],'chars':chars})
            pages.append({'page':number,'width':w,'height':h,'lines':lines})
    (OUT/(key+'_layout.json')).write_text(json.dumps(pages,ensure_ascii=False))
    text=[]
    for p in pages:
        text.append(f"\n### {key} PDF {p['page']} ({p['width']} x {p['height']}) ###")
        for line in p['lines']:
            text.append(f"{line['id']} y={line['rect'][1]:.1f}-{line['rect'][3]:.1f} {line['text']}")
    (OUT/(key+'_layout.txt')).write_text('\n'.join(text)+'\n')
    return key,len(pages)

if __name__=='__main__':
    refs=[r for r in json.loads((ROOT/'catalog.json').read_text())['references'] if r['key'] in ['Konig2014','Nystrom2010']]
    with ProcessPoolExecutor(max_workers=3) as ex:
        for result in ex.map(run,refs):print(result,flush=True)
