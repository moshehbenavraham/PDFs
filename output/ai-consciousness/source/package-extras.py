from pathlib import Path
import base64, json, html, subprocess, textwrap, shutil
from weasyprint import HTML
import pymupdf as fitz

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
data=json.loads((ROOT/'source/deck-data.json').read_text())
def esc(x): return html.escape(str(x),quote=True)
def uri(p,mime): return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
fonts=''.join('@font-face{font-family:Inter;font-weight:'+str(weight)+';src:url('+uri(ROOT/'assets/fonts'/name,'font/otf')+')}\n' for name,weight in [('Inter-Regular.otf',400),('Inter-Bold.otf',700)])
images={k:uri(ROOT/'assets'/f'{k}.png','image/png') for k in {s['image'] for s in data['slides'] if s['image']}}
reveals={2:{1:1},7:{1:1,2:2},14:{1:1,2:1,4:1},18:{2:1},23:{1:1}}
sections=[]
for n,s in enumerate(data['slides'],1):
    cells=[]
    for j,t in enumerate(s['items']):
        style=f"left:{t['x']}px;top:{t['y']}px;width:{t['w']}px;height:{t['h']}px;font-size:{t['size']}px;color:{t['color']};font-weight:{700 if t['bold'] else 400};text-align:{t.get('align','left')}"
        tag='a' if t.get('link') else 'div'
        extra=f' href="{esc(t["link"])}" target="_blank" rel="noopener"' if t.get('link') else ''
        step=reveals.get(n,{}).get(j,0)
        cells.append(f'<{tag} class="text" data-step="{step}" style="{style}"{extra}>{esc(t["text"])}</{tag}>')
    bg=f'<img class="art" src="{images[s["image"]]}" alt="Conceptual artwork: {esc(s["title"])}">' if s['image'] else ''
    sections.append(f'<section class="slide" id="slide-{n}" aria-label="Slide {n}: {esc(s["title"])}" style="background:{s["bg"]}">{bg}{"".join(cells)}</section>')
payload=json.dumps({'slides':[{'title':s['title'],'notes':s['notes'],'time':s['time'],'sources':[data['sources'][k] for k in s['sources']]} for s in data['slides']]},ensure_ascii=False).replace('</','<\\/')
page='''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Is Anyone Home? — AI Consciousness &amp; Sentience</title><style>'''+fonts+'''
*{box-sizing:border-box}html,body{margin:0;background:#050505;color:#f3eedd;width:100%;height:100%;overflow:hidden;font-family:Inter,Arial,sans-serif}#stage{position:absolute;width:1600px;height:900px;left:50%;top:50%;transform-origin:center center}.slide{position:absolute;inset:0;display:none;overflow:hidden}.slide.active{display:block}.art{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.text{position:absolute;white-space:pre;line-height:1.2;text-decoration:none;transition:opacity .4s,transform .4s}.text[data-hidden=true]{opacity:0;transform:translateY(12px);pointer-events:none}a.text{text-decoration:underline;text-underline-offset:5px}#toolbar{position:fixed;bottom:12px;left:50%;transform:translateX(-50%);display:flex;gap:8px;align-items:center;padding:9px 12px;background:#181918eb;border:1px solid #454740;border-radius:8px;opacity:0;transition:opacity .2s;z-index:5}body.controls #toolbar,#toolbar:focus-within{opacity:1}button{font:500 13px Inter;color:#f3eedd;background:transparent;border:1px solid #52534d;border-radius:4px;padding:8px 12px;cursor:pointer}button:hover{background:#34342f}button:focus-visible,a:focus-visible{outline:3px solid #ee634f;outline-offset:3px}#counter{font-size:12px;min-width:54px;text-align:center}#veil{display:none;position:fixed;inset:0;background:black;z-index:20}body.blackout #veil{display:block}dialog{max-width:740px;max-height:86vh;overflow:auto;border:1px solid #60584c;border-radius:8px;background:#f3eedd;color:#222423;padding:32px;font-size:17px;line-height:1.55}dialog::backdrop{background:#000b}dialog button{color:#222423;border-color:#888}dialog h2{line-height:1.2}dialog a{color:#a44035}#live{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}@media(prefers-reduced-motion:reduce){.text,#toolbar{transition:none}}@media print{html,body{overflow:visible;background:white}#stage{position:static;transform:none!important;width:1600px;height:auto}.slide{position:relative;display:block;break-after:page;width:1600px;height:900px}.text[data-hidden=true]{opacity:1;transform:none}#toolbar,dialog,#veil{display:none!important}@page{size:1600px 900px;margin:0}}
</style></head><body class="controls"><main id="stage" aria-label="Presentation">'''+''.join(sections)+'''</main><nav id="toolbar" aria-label="Presentation controls"><button id="prev" title="Left arrow">Previous</button><span id="counter"></span><button id="next" title="Right arrow or Space">Next / reveal</button><button id="fullscreen">Full screen</button><button id="notes">Notes</button><button id="help">Help</button></nav><div id="veil" aria-label="Screen blanked. Press B to resume."></div><div id="live" aria-live="polite"></div><dialog id="dialog"></dialog><script>
const data='''+payload+''';
const slides=[...document.querySelectorAll('.slide')],dialog=document.getElementById('dialog');let index=0,phase=0,hideTimer;
const maxPhase=i=>Math.max(0,...[...slides[i].querySelectorAll('[data-step]')].map(x=>Number(x.dataset.step)));
function render(){slides.forEach((s,i)=>{s.classList.toggle('active',i===index);s.setAttribute('aria-hidden',String(i!==index));s.inert=i!==index});slides[index].querySelectorAll('[data-step]').forEach(el=>{const hidden=Number(el.dataset.step)>phase;el.dataset.hidden=String(hidden);el.setAttribute('aria-hidden',String(hidden))});document.getElementById('counter').textContent=(index+1)+' / '+slides.length;document.getElementById('live').textContent='Slide '+(index+1)+': '+data.slides[index].title;history.replaceState(null,'','#'+(index+1));}
function next(){if(phase<maxPhase(index))phase++;else if(index<slides.length-1){index++;phase=0}render()}
function prev(){if(phase>0)phase--;else if(index>0){index--;phase=maxPhase(index)}render()}
function fit(){document.getElementById('stage').style.transform='translate(-50%,-50%) scale('+Math.min(innerWidth/1600,innerHeight/900)+')'}
async function fullscreen(){try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen()}catch(e){show('Full screen','<p>Your browser blocked automatic full screen. Use its full-screen command or F11.</p>')}}
function show(title,body){dialog.replaceChildren();const h=document.createElement('h2');h.textContent=title;const content=document.createElement('div');content.innerHTML=body;const b=document.createElement('button');b.textContent='Close';b.onclick=()=>dialog.close();dialog.append(h,content,b);dialog.showModal()}
const escape=x=>x.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function notes(){const s=data.slides[index];show((index+1)+'. '+s.title,'<p><strong>'+ (s.time?s.time+' seconds':'Optional appendix')+'</strong></p><p>'+escape(s.notes)+'</p>'+s.sources.map(x=>'<p><a target="_blank" rel="noopener" href="'+escape(x.url)+'">'+escape(x.label)+'</a></p>').join(''))}
function help(){show('The controls','<p><strong>Right / Space:</strong> reveal or advance<br><strong>Left:</strong> go back<br><strong>Home / End:</strong> first / last slide<br><strong>F:</strong> full screen<br><strong>B:</strong> blank / restore screen<br><strong>N:</strong> notes on this screen<br><strong>H:</strong> help<br><strong>Escape:</strong> close a dialog or restore the screen</p><p>Slides 24–26 are optional references. The PDF and PowerPoint show all content without browser reveals. This file works offline.</p>')}
document.getElementById('prev').onclick=prev;document.getElementById('next').onclick=next;document.getElementById('fullscreen').onclick=fullscreen;document.getElementById('notes').onclick=notes;document.getElementById('help').onclick=help;
document.addEventListener('keydown',e=>{if(dialog.open)return;const key=e.key.toLowerCase();if(['arrowright',' ','pagedown'].includes(key)){e.preventDefault();next()}else if(['arrowleft','pageup'].includes(key)){e.preventDefault();prev()}else if(key==='home'){index=0;phase=0;render()}else if(key==='end'){index=slides.length-1;phase=maxPhase(index);render()}else if(key==='f')fullscreen();else if(key==='b')document.body.classList.toggle('blackout');else if(key==='n')notes();else if(key==='h'||key==='?')help();else if(key==='escape')document.body.classList.remove('blackout')});
function controls(){document.body.classList.add('controls');clearTimeout(hideTimer);hideTimer=setTimeout(()=>document.body.classList.remove('controls'),2600)}document.addEventListener('mousemove',controls);document.addEventListener('focusin',controls);let touchStart=null;document.addEventListener('touchstart',e=>{touchStart=e.touches[0].clientX},{passive:true});document.addEventListener('touchend',e=>{if(touchStart===null||dialog.open)return;const dx=e.changedTouches[0].clientX-touchStart;if(Math.abs(dx)>70){if(dx<0)next();else prev()}touchStart=null},{passive:true});
window.addEventListener('resize',fit);window.addEventListener('hashchange',()=>{const n=Number(location.hash.slice(1));if(n>=1&&n<=slides.length){index=n-1;phase=0;render()}});const hash=Number(location.hash.slice(1));if(hash>=1&&hash<=slides.length)index=hash-1;render();fit();controls();
</script></body></html>'''
(OUT/'Is Anyone Home.html').write_text(page,encoding='utf-8')

assert (OUT/'Is Anyone Home.pptx').is_file()
subprocess.run(['libreoffice',f'-env:UserInstallation={(ROOT/".build/lo-profile").as_uri()}','--headless','--convert-to','pdf','--outdir',str(OUT),str(OUT/'Is Anyone Home.pptx')],check=True)
# LibreOffice forces its hyperlink theme color even over explicit run colors.
# Restore the authored palette in PDF drawing streams while retaining text and links.
pdf_path=OUT/'Is Anyone Home.pdf'
shutil.copy2(pdf_path,ROOT/'.build/libreoffice-original.pdf')
doc=fitz.open(pdf_path)
old=b'0.2745098039 0.4705882352 0.525490196'
for i,p in enumerate(doc):
    rgb=(182,75,61) if data['slides'][i]['bg']=='#F3EEDD' else (238,99,79)
    new=' '.join(f'{c/255:.10f}' for c in rgb).encode()
    for xref in p.get_contents():
        contents=doc.xref_stream(xref)
        fixed=contents.replace(old+b' rg',new+b' rg').replace(old+b' RG',new+b' RG')
        if fixed!=contents:doc.update_stream(xref,fixed)
tmp=OUT/'slides-color-corrected.pdf'
doc.save(tmp,garbage=4,deflate=True);doc.close();tmp.replace(pdf_path)

guide_css='''@font-face{font-family:Inter;src:url('../assets/fonts/Inter-Regular.otf')}@font-face{font-family:Inter;src:url('../assets/fonts/Inter-Bold.otf');font-weight:bold}@page{size:A4;margin:17mm 19mm 18mm;@bottom-right{content:counter(page);font:9pt Inter;color:#626660} @bottom-left{content:'IS ANYONE HOME?  /  PRESENTER GUIDE';font:8pt Inter;color:#626660}}body{font:11pt/1.55 Inter;color:#222423}h1{font-size:33pt;line-height:1.12;margin:0 0 8mm}h2{font-size:23pt;line-height:1.15;margin:0 0 6mm}p{margin:0 0 4mm}a{color:#a44035;overflow-wrap:anywhere}.page{break-after:page}.page:last-child{break-after:auto}.kicker{font-size:10pt;font-weight:bold;color:#b64b3d;letter-spacing:1pt;margin:0 0 5mm}.slide-image{display:block;width:100%;margin:0 0 6mm}.source{font-size:8.6pt;line-height:1.35;margin-bottom:3mm}.cue{font-size:11pt;line-height:1.7}hr{border:0;border-top:1px solid #d8cebe;margin:7mm 0}li{margin-bottom:3mm}.cover-image{width:100%;margin:10mm 0}'''
intro='''<section class="page"><p class="kicker">PRESENTER GUIDE</p><h1>Is Anyone Home?</h1><p>AI consciousness &amp; sentience</p><img class="cover-image" src="renders/slide-01.png"><p><strong>23 main slides. Approximately 24 minutes.</strong><br>Three optional appendix slides support discussion and further reading.</p><hr><p>The room votes at slides 3 and 22. Mary’s room, the Chinese Room and neuron replacement invite short responses. Slides 18–19 turn the uncertainty into a decision.</p><p>Use the main deck full screen. The PowerPoint includes these notes. The offline browser edition uses Right or Space to reveal and advance, Left to go back, F for full screen, B to blank the screen and N for notes on the current display.</p><p>Keep fictional scenarios separate from research findings. Treat thought experiments as prompts for reasoning, and company research as reported evidence with stated limits.</p></section>'''
pages=[intro]; elapsed=0
for n,s in enumerate(data['slides'],1):
    mins,secs=divmod(elapsed,60); end=elapsed+s['time']; em,es=divmod(end,60)
    pace=f'{mins:02}:{secs:02}–{em:02}:{es:02}  /  {s["time"]} seconds' if s['time'] else 'Optional appendix'
    sources=''.join(f'<p class="source">{esc(data["sources"][k]["label"])}<br><a href="{esc(data["sources"][k]["url"])}">{esc(data["sources"][k]["url"])}</a></p>' for k in s['sources'])
    pages.append(f'<section class="page"><p class="kicker">SLIDE {n:02}  /  {pace}</p><h2>{esc(s["title"])}</h2><img class="slide-image" src="renders/slide-{n:02}.png"><p class="cue">{esc(s["notes"])}</p>{"<hr>"+sources if sources else ""}</section>')
    elapsed=end
guide='<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Is Anyone Home? Presenter Guide</title><style>'+guide_css+'</style></head><body>'+''.join(pages)+'</body></html>'
(ROOT/'.build/presenter-guide.html').write_text(guide,encoding='utf-8')
HTML(filename=str(ROOT/'.build/presenter-guide.html')).write_pdf(str(OUT/'Presenter Guide.pdf'))
print(json.dumps({'html_bytes':(OUT/'Is Anyone Home.html').stat().st_size,'talk_seconds':elapsed,'outputs':[p.name for p in OUT.iterdir() if p.is_file() and not p.name.startswith('.')]}))
