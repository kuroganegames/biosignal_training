from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFont

WORK = Path(__file__).resolve().parent
entries = json.loads((WORK / 'render_manifest.json').read_text())
keys = sorted(set(x['key'] for x in entries))
out = WORK / 'contacts'
out.mkdir(exist_ok=True)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
for key in keys:
    pages = sorted((x for x in entries if x['key'] == key), key=lambda x:x['page'])
    for start in range(0, len(pages), 4):
        items = pages[start:start+4]
        width = 650
        thumbs = []
        for x in items:
            im = Image.open(x['png']).convert('RGB')
            im = im.resize((width, round(im.height*width/im.width)), Image.Resampling.LANCZOS)
            thumbs.append(im)
        height = max(im.height for im in thumbs) + 40
        sheet = Image.new('RGB', ((width+18)*min(2,len(items))+18, height*math.ceil(len(items)/2)+18), '#d6dde4')
        draw = ImageDraw.Draw(sheet)
        for i, (x, im) in enumerate(zip(items,thumbs)):
            xx, yy = 18+(width+18)*(i%2), 18+height*(i//2)
            draw.text((xx,yy), f'{key} / PDF p. {x["page"]}', fill='black', font=font)
            sheet.paste(im,(xx,yy+28))
        sheet.save(out / f'{key}_{start//4+1}.png')
print('\n'.join(p.name for p in sorted(out.glob('*.png'))))
