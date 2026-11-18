const fs = require('fs');
const path = require('path');
const sharp = require('/home/kurogane/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const mj = '/tmp/saccade-guide-math-net/node_modules/mathjax-full/js/';
const { mathjax } = require(mj+'mathjax.js');
const { TeX } = require(mj+'input/tex.js');
const { SVG } = require(mj+'output/svg.js');
const { liteAdaptor } = require(mj+'adaptors/liteAdaptor.js');
const { RegisterHTMLHandler } = require(mj+'handlers/html.js');
const { AllPackages } = require(mj+'input/tex/AllPackages.js');
const adaptor = liteAdaptor(); RegisterHTMLHandler(adaptor);
const doc = mathjax.document('', {InputJax:new TeX({packages:AllPackages}),OutputJax:new SVG({fontCache:'local'})});
const items = JSON.parse(fs.readFileSync(path.join(__dirname,'equations.json'),'utf8'));
const dest = path.join(__dirname,'equations'); fs.mkdirSync(dest,{recursive:true});
(async()=>{
  for (const item of items) {
    const markup=adaptor.outerHTML(doc.convert(item.latex,{display:true}));
    if(markup.includes('data-mjx-error')) throw new Error(item.id+' '+markup);
    let svg=markup.slice(markup.indexOf('<svg'),markup.indexOf('</svg>')+6);
    svg=svg.replace(/(width|height)="([0-9.]+)(ex|em)"/g,(_,a,n)=>`${a}="${Math.ceil(Number(n)*8.5)}px"`).replace(/currentColor/g,'#000000');
    if(!svg.includes('xmlns=')) svg=svg.replace('<svg ','<svg xmlns="http://www.w3.org/2000/svg" ');
    fs.writeFileSync(path.join(dest,item.id+'.svg'),svg);
    await sharp(Buffer.from(svg),{density:300}).png().toFile(path.join(dest,item.id+'.png'));
  }
  console.log('Rendered',items.length,'equations');
})();
