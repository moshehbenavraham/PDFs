import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const req=createRequire('C:/Users/apexw/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/package.json');
const {Canvas,FontLibrary}=req('skia-canvas');
FontLibrary.use('Inter',['Inter-Regular.otf','Inter-Bold.otf'].map(f=>path.join(root,'assets/fonts',f)));
const ctx=new Canvas(1600,900).getContext('2d');
const data=JSON.parse(await fs.readFile(path.join(root,'source/deck-data.json')));
let flags=[];
for(const [i,s] of data.slides.entries())for(const t of s.items){ctx.font=`${t.bold?700:400} ${t.size}px Inter`;const w=Math.max(...t.text.split('\n').map(line=>ctx.measureText(line).width));if(w>t.w+2)flags.push({slide:i+1,text:t.text,width:w,box:t.w});}
console.log(JSON.stringify(flags,null,2));
