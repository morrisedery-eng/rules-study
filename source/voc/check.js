// Validate vocalized files: removing niqqud must give back the original line exactly.
const fs=require("fs");
const MARKS=/[֑-ׇֽֿׁׂׅׄ]/g;
const parse=f=>{const m={};if(!fs.existsSync(f))return m;fs.readFileSync(f,"utf8").split("\n").forEach(l=>{const i=l.indexOf("| ");if(i>0&&!l.startsWith("#"))m[l.slice(0,i)]=l.slice(i+2)});return m};
let bad=0,ok=0,missing=0;
for(let d=1;d<=15;d++){const n=String(d).padStart(2,"0"),src=parse(`${__dirname}/src${n}.txt`),voc=parse(`${__dirname}/v${n}.txt`);
  if(!Object.keys(voc).length)continue;
  for(const k in src){if(!/[א-ת]/.test(src[k]))continue;
    if(!(k in voc)){missing++;console.log(`MISSING d${d} ${k}`);continue}
    const back=voc[k].replace(MARKS,"");
    if(back!==src[k]){bad++;let i=0;while(i<back.length&&back[i]===src[k][i])i++;
      console.log(`DIFF d${d} ${k} at ${i}: src[${src[k].slice(Math.max(0,i-8),i+8)}] voc[${back.slice(Math.max(0,i-8),i+8)}]`)}else ok++}
  for(const k in voc)if(!(k in src))console.log(`EXTRA d${d} ${k}`);
}
console.log(`ok ${ok}, diff ${bad}, missing ${missing}`);
