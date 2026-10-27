from pathlib import Path
import math, json, textwrap
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / 'pdf/tomorrow-has-questions.pdf'
ASSETS = ROOT / 'assets'
W, H = 1280, 720
NAVY, CREAM, CORAL, MINT, GOLD = '#102B3D', '#F6F0E4', '#EA7656', '#8CD6C3', '#E8B86D'
INK, MUTED, PALE, BLUE = '#163344', '#536979', '#E5E7DB', '#244A60'
FONTDIR = Path('/usr/share/fonts/truetype/ibm-plex')
for name, file in [('Body','IBMPlexSans-Regular.ttf'), ('Medium','IBMPlexSans-Medium.ttf'),
                   ('Bold','IBMPlexSans-Bold.ttf'), ('Display','IBMPlexSansCondensed-Bold.ttf'),
                   ('Italic','IBMPlexSans-Italic.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONTDIR/file)))

SOURCES = {
 1: ('Moonshots conversation', 'https://www.youtube.com/watch?v=dthaDyttHns'),
 2: ('Robocurve, RoboDojo-RC Tier 1', 'https://robocurve.org/opus-5-5-robodojo-rc-tier-1/'),
 3: ('TheoPhysEval preprint', 'https://arxiv.org/abs/2610.16733'),
 4: ('Ansari XPRIZE', 'https://www.xprize.org/competitions/ansari'),
 5: ('Anousheh Ansari biography', 'https://www.xprize.org/people/anousheh-ansari'),
 6: ('Oil Cleanup XCHALLENGE', 'https://www.xprize.org/competitions/oil-cleanup'),
 7: ('XPRIZE Carbon Removal', 'https://www.xprize.org/competitions/carbonremoval'),
 8: ('XPRIZE Healthspan', 'https://www.xprize.org/competitions/healthspan'),
 9: ('OpenAI, sycophancy report', 'https://openai.com/index/expanding-on-sycophancy/'),
 10: ('Anthropic, reward tampering', 'https://www.anthropic.com/research/reward-tampering'),
 11: ('Tesla Roadster', 'https://www.tesla.com/roadster'),
}

c = canvas.Canvas(str(OUT), pagesize=(W,H), pageCompression=1, initialFontName='Body')
c.setTitle('Tomorrow Has Questions')
c.setSubject('Machines, moonshots, incentives, AI alignment and human purpose')
c.setAuthor('')
c.setCreator('PDF workspace')
c.setViewerPreference('DisplayDocTitle', 'true')
c.setViewerPreference('FitWindow', 'true')
PAGE, RECORDS, BOXES = 0, [], []

def fill(color): c.setFillColor(HexColor(color))
def stroke(color): c.setStrokeColor(HexColor(color))
def rect(x,y,w,h,color,r=0):
    fill(color)
    if r: c.roundRect(x,H-y-h,w,h,r,stroke=0,fill=1)
    else: c.rect(x,H-y-h,w,h,stroke=0,fill=1)
def line(x1,y1,x2,y2,color=INK,width=2):
    stroke(color); c.setLineWidth(width); c.line(x1,H-y1,x2,H-y2)
def circle(x,y,r,color,outline=None,width=2):
    fill(color); stroke(outline or color); c.setLineWidth(width)
    c.circle(x,H-y,r,stroke=int(bool(outline)),fill=1)
def path(points,color,outline=None,width=2,close=True):
    p=c.beginPath(); p.moveTo(points[0][0],H-points[0][1])
    for x,y in points[1:]: p.lineTo(x,H-y)
    if close:p.close()
    fill(color); stroke(outline or color);c.setLineWidth(width)
    c.drawPath(p,fill=int(close),stroke=int(bool(outline) or not close))
def tx(text,x,y,size=30,color=INK,font='Body',width=None,leading=None,align='left'):
    leading=leading or size*1.23
    lines=[]
    for part in str(text).split('\n'):
        if width is None: lines.append(part); continue
        row=''
        for word in part.split():
            candidate=(row+' '+word).strip()
            if row and pdfmetrics.stringWidth(candidate,font,size)>width:
                lines.append(row);row=word
            else:row=candidate
        lines.append(row)
    fill(color);c.setFont(font,size)
    for i,l in enumerate(lines):
        tw=pdfmetrics.stringWidth(l,font,size)
        xx=x-tw/2 if align=='center' else x-tw if align=='right' else x
        yy=y+i*leading
        if xx < -0.5 or xx+tw > W+0.5 or yy < -0.5 or yy+size > H+0.5:
            raise ValueError(f'Text outside page {PAGE}: {l}')
        c.drawString(xx,H-yy-size*.8,l)
        BOXES.append(dict(page=PAGE,text=l,x=xx,y=yy,w=tw,h=size))
    return y+leading*len(lines)
def image(name,x=0,y=0,w=W,h=H):
    src=ASSETS/name
    if not src.exists(): raise FileNotFoundError(src)
    c.drawImage(str(src),x,H-y-h,width=w,height=h,mask='auto')
def shade_left():
    c.saveState()
    fill(NAVY)
    for i in range(100):
        c.setFillAlpha(.82*(1-i/100))
        c.rect(i*8,0,8,H,stroke=0,fill=1)
    for j in range(90):
        c.setFillAlpha(.83*j/90)
        c.rect(0,89-j,W,1,stroke=0,fill=1)
    c.restoreState()
def footer(note='',refs=(),dark=False):
    col = '#C2D4DA' if dark else MUTED
    if note: tx(note,64,664,14,col,width=1075,leading=18)
    xx=64
    for ref in refs:
        label=f'[{ref}] {SOURCES[ref][0]}'
        tw=pdfmetrics.stringWidth(label,'Body',13)
        tx(label,xx,692,13,col)
        c.linkURL(SOURCES[ref][1],(xx,H-707,xx+tw,H-690),relative=0,thickness=0)
        xx+=tw+24
    tx(f'{PAGE:02}',1215,681,15,col,'Medium',align='right')
def new(title,section='',dark=False,bg=None,art=None):
    global PAGE
    if PAGE:c.showPage()
    PAGE+=1
    rect(0,0,W,H,bg or (NAVY if dark else CREAM))
    if art:image(art);shade_left()
    c.bookmarkPage(f'p{PAGE}')
    c.addOutlineEntry(title,f'p{PAGE}',0,False)
    RECORDS.append(dict(page=PAGE,title=title,section=section))
    if section:tx(section.upper(),64,37,15,MINT if dark else MUTED,'Medium')
    return CREAM if dark else INK
def heading(text,dark=False,size=58,width=1150):
    return tx(text,64,92,size,CREAM if dark else INK,'Display',width=width,leading=size*1.04)
def arrow(x1,y,x2,color=INK):
    line(x1,y,x2-12,y,color,3)
    path([(x2,y),(x2-14,y-8),(x2-14,y+8)],color)
def star(x,y,r=12,color=GOLD):
    p=[]
    for i in range(8):
        ang=math.pi/4*i;rr=r if i%2==0 else r*.25
        p.append((x+rr*math.cos(ang),y+rr*math.sin(ang)))
    path(p,color)
def mug(x,y,s=1,color=CORAL):
    c.saveState();c.translate(x,H-y);c.scale(s,s)
    c.setFillColor(HexColor(color));c.roundRect(0,-64,63,64,8,fill=1,stroke=0)
    c.setStrokeColor(HexColor(color));c.setLineWidth(9);c.circle(64,-29,19,stroke=1,fill=0)
    c.setStrokeColor(HexColor(CREAM));c.setLineWidth(3)
    c.bezier(19,10,8,20,28,25,18,37);c.bezier(42,10,31,20,51,25,41,37)
    c.restoreState()
def person(x,y,s=1,color=CORAL):
    circle(x,y,14*s,color)
    rect(x-17*s,y+22*s,34*s,48*s,color,12*s)
    line(x-9*s,y+65*s,x-16*s,y+102*s,color,10*s)
    line(x+9*s,y+65*s,x+16*s,y+102*s,color,10*s)
def compass(x,y,r=92):
    circle(x,y,r,BLUE, MINT,2)
    circle(x,y,r-14,BLUE,'#446878',1)
    for i in range(12):
        a=i*math.pi/6
        line(x+(r-17)*math.cos(a),y+(r-17)*math.sin(a),x+(r-26)*math.cos(a),y+(r-26)*math.sin(a),MINT,2)
    path([(x,y-r*.74),(x-r*.14,y+r*.22),(x,y+r*.09)],CORAL)
    path([(x,y+r*.74),(x+r*.14,y-r*.22),(x,y-r*.09)],CREAM)
    circle(x,y,7,GOLD)

# 01
new('Tomorrow has questions',dark=True,art='01-tomorrow.png')
tx('TOMORROW\nHAS QUESTIONS',64,137,78,CREAM,'Display',leading=84)
tx('Flying cars. Clever machines.\nAnd the wonderfully difficult\nbusiness of being human.',68,353,29,CREAM,leading=38)
line(68,500,170,500,MINT,4)
tx('A field trip through the ideas in Moonshots',68,529,20,CREAM,'Medium')
tx('With Peter Diamandis, Anousheh Ansari,\nSalim Ismail and Emad Mostaque',68,567,17,'#D8E0DC',leading=23)
footer('Based on the supplied conversation. Evidence checked 20 October 2026.',[1],True)

# 02
new('Your robot starts Monday', 'Before we begin', dark=True)
heading('Your robot starts Monday',True,72)
tx('It can take one thing off your hands. What goes first?',64,201,31,CREAM)
for x,n,title,body in [
    (80,'A','The chores','Laundry, dishes,\nendless tiny errands.'),
    (470,'B','The work','Reports, schedules,\nrepetitive decisions.'),
    (860,'C','The hard thinking','Research, calculations,\nproblems that resist you.')]:
    tx(n,x,290,104,MINT if n=='B' else CORAL,'Display')
    tx(title,x,420,33,CREAM,'Bold')
    tx(body,x,477,26,'#D0DEDF',leading=34)
tx('And what would you do with the time?',64,600,33,GOLD,'Medium')
footer('A show-of-hands question. There is no correct answer.',dark=True)

# 03
new('Four questions for the trip','Our route')
heading('Four questions for the trip')
for i,(a,b) in enumerate([
    ('What can machines do?','Cars, robots and scientific work'),
    ('What do we reward?','XPRIZE and the art of useful incentives'),
    ('Who chooses the goal?','Alignment, institutions and shared benefits'),
    ('What will we choose?','Purpose, play and life with other people')]):
    yy=213+i*105
    tx(f'0{i+1}',64,yy,52,CORAL,'Display')
    tx(a,185,yy+2,33,INK,'Bold')
    tx(b,185,yy+47,23,MUTED)
    line(185,yy+88,1200,yy+88,'#D7DBD3',1)
footer('The episode supplies the questions. The diagrams and audience exercises develop them.',[1])

# 04
new('A flying car is a wonderful question','01 / Machines',dark=True,art='03-car.png')
tx('A FLYING CAR\nIS A WONDERFUL\nQUESTION',64,118,67,CREAM,'Display',leading=69)
tx('The next question:\nwho insures the landing?',68,393,32,CREAM,'Medium',width=490,leading=40)
footer('Roadster discussion, 07:07-16:54. Conceptual illustration. See the evidence notes for qualifications.',[1,11],True)

# 05
new('A demo still has to pass everyday life','01 / Machines')
heading('A demo still has to\npass everyday life',size=62)
for i,(name,desc) in enumerate([
 ('Capability','Can it do the task?'),
 ('Reliability','Can it repeat it safely?'),
 ('Economics','Does the whole system pay?'),
 ('Institutions','Who permits it and answers for it?')]):
    xx=64+i*304
    yy=340-i*23
    rect(xx,yy,264,205+i*23,PALE)
    tx(str(i+1),xx+20,yy+20,54,CORAL,'Display')
    tx(name,xx+20,yy+86,29,INK,'Bold')
    tx(desc,xx+20,yy+133,23,INK,width=230,leading=29)
tx('The spectacular moment is only one part of deployment.',64,600,28,INK,'Medium')
footer('Discussion framework inspired by the episode, 12:50-15:56 and 24:37-27:00.',[1])

# 06
new('Cheaper thinking changes the economics','01 / Machines')
heading('Cheaper thinking changes the economics',size=55)
tx('A published robotics comparison, with matched caching assumptions',64,171,23,MUTED)
for i,(name,cost,progress,col) in enumerate([
 ('GPT-6 Astra',1.14,'36.7% mean progress. 5/120 fully completed.',BLUE),
 ('Opus 5.5',.90,'36.0% mean progress. 1/120 fully completed.',CORAL)]):
    yy=264+i*141
    tx(name,64,yy,28,INK,'Medium')
    rect(291,yy,420*cost/1.14,56,col)
    tx(f'${cost:.2f}',735,yy+4,42,INK,'Display')
    tx(progress,291,yy+72,20,MUTED)
tx('21%',952,268,105,CORAL,'Display')
tx('lower estimated\nmodel cost per trial',953,393,27,INK,'Medium',leading=34)
tx('Cheaper attempts still need better completion.',64,574,33,INK,'Bold')
footer('Six selected real-world tasks. Progress is partial task progress, not success rate. Model cost excludes the robot and operations.',[2])

# 07
new('The final task is harder than one step','01 / Machines',dark=True)
heading('A great step can still make\na lousy morning',True,63)
tx('Suppose each step succeeds 99% of the time.',64,250,29,CREAM)
for x,n,v,col in [(64,'1 step','99%',MINT),(476,'20 steps','82%',GOLD),(888,'100 steps','37%',CORAL)]:
    tx(v,x,338,100,col,'Display')
    tx(n,x,468,29,CREAM,'Medium')
    line(x,521,x+302,521,col,5)
tx('Long routines need recovery, checking and safe ways to stop.',64,584,29,CREAM,'Medium')
footer('Illustrative mathematics, not a robot benchmark. All steps must succeed, with independent failures: 0.99 raised to the number of steps.',dark=True)

# 08
new('Your home is the final boss','01 / Machines',dark=True,art='02-laundry.png')
tx('YOUR HOME\nIS THE\nFINAL BOSS',64,113,72,CREAM,'Display',leading=75)
tx('A sock. A spill.\nA very convincing teddy bear.',67,399,29,CREAM,width=445,leading=39)
tx('Useful robots need judgment\nwhen the script runs out.',67,520,25,MINT,leading=33)
footer('A household full of exceptions. Episode, 24:37-26:28. Conceptual illustration.',[1],True)

# 09
new('The right body depends on the job','01 / Machines')
heading('The right body depends on the job')
# humanoid
circle(240,291,42,BLUE);rect(190,344,100,103,BLUE,16)
line(203,449,193,521,BLUE,21);line(277,449,287,521,BLUE,21)
line(184,364,152,431,BLUE,18);line(296,364,328,431,BLUE,18)
circle(225,289,5,MINT);circle(255,289,5,MINT)
# wheeled arm
rect(568,469,144,25,CORAL,8);circle(589,514,21,INK);circle(690,514,21,INK)
line(633,466,590,385,CORAL,22);circle(590,385,20,INK)
line(590,385,677,322,CORAL,22);circle(677,322,16,INK)
line(677,322,727,348,CORAL,14);line(727,348,746,331,INK,7);line(727,348,742,369,INK,7)
# pipe inspector
rect(908,310,270,150,PALE,70);circle(1123,385,73,CREAM,INK,3)
for xx,cc in [(957,MINT),(1007,GOLD),(1057,MINT)]:
    rect(xx,365,43,46,cc,10)
    if xx<1057:line(xx+44,388,xx+49,388,INK,8)
circle(1100,389,22,BLUE)
circle(1107,388,9,GOLD)
for xx in (976,1020,1064):line(xx,405,xx-12,442,INK,5)
for x,title,body in [
 (64,'Human-shaped','Works with tools and spaces\nbuilt around people.'),
 (474,'Task-shaped','Trades generality for a simpler,\nmore efficient job.'),
 (884,'Modular','Changes tools or parts as\nthe job changes.')]:
    tx(title,x,554,30,INK,'Bold');tx(body,x,600,22,MUTED,leading=28)
footer('These are design choices, not a forecast that one form factor will win. Episode, 21:51-28:18.',[1])

# 10
new('Physics gets a very fast collaborator','01 / Machines',dark=True)
heading('Physics gets a very fast collaborator',True,57)
for row in range(5):
    for col in range(10):
        idx=row*10+col
        circle(90+col*48,270+row*48,15,MINT if idx<49 else NAVY, MINT if idx==49 else None)
tx('49 / 50',650,240,105,CREAM,'Display')
tx('unpublished theoretical physics problems',656,367,27,MINT,width=530)
tx('Under $3 per problem on average',656,447,30,CREAM,'Bold',width=520)
tx('With literature search and computational tools',656,499,23,'#C2D4DA',width=520)
tx('Choosing an important new question remains a different challenge.',64,588,28,CREAM,'Medium')
footer('TheoPhysEval authors report this result for GPT-6 Astra in Codex. This preprint measures concrete calculations, not all of scientific discovery.',[3],True)

# 11
new('A prize is a question with a finish line','02 / Incentives',dark=True,art='04-prize.png')
tx('A PRIZE IS\nA QUESTION\nWITH A\nFINISH LINE',64,121,73,CREAM,'Display',leading=73)
tx('People you never expected\nmay bring the answer.',67,485,30,CREAM,leading=40)
footer('XPRIZE opens a problem to competing approaches and defines how success will be judged.',[1,4],True)

# 12
new('Ten million dollars made a question concrete','02 / Incentives')
heading('A dream gets a measurable target',size=62)
tx('$10M',64,244,124,CORAL,'Display')
tx('Ansari XPRIZE',70,390,28,INK,'Bold')
tx('Anousheh Ansari and her family\nhelped make the prize possible.\nShe later flew to the International\nSpace Station in 2006.',70,445,24,MUTED,width=440,leading=32)
line(560,240,560,586,'#C9D1CD',2)
for yy,big,small in [(238,'100 km','Reach space with a privately funded crewed vehicle.'),
                     (355,'Twice in two weeks','Prove the spacecraft can be reused.'),
                     (480,'4 October 2004','SpaceShipOne completes the winning flight.')]:
    tx(big,620,yy,39,INK,'Display')
    tx(small,620,yy+54,25,MUTED,width=570,leading=31)
footer('Launched in 1996. This is a short summary of the target, not the full competition rulebook.',[4,5])

new('What makes us move?','02 / Incentives',dark=True)
heading('What makes us move?',True,72)
tx('The conversation proposes four powerful motives.',64,197,29,'#C2D4DA')
for x,y,title,body,col in [
 (64,298,'Fear','Something must be prevented.',CORAL),
 (690,298,'Gain','There is a reward to pursue.',GOLD),
 (64,475,'Curiosity','There is something to discover.',MINT),
 (690,475,'Love','Someone or something matters.',CORAL)]:
    circle(x+28,y+27,27,col)
    tx(title,x+83,y-2,42,CREAM,'Display')
    tx(body,x+83,y+63,26,'#D0DEDF')
footer('The speakers use the word greed for personal gain. These motives are a discussion lens, not a scientific ranking of human behavior.',[1],True)

# 13
new('Congratulations. You optimized the wrong thing.','02 / Incentives',dark=True)
heading('Congratulations.\nYou optimized the wrong thing.',True,63)
tx('Imagine a cafe pays a bonus for every cup served.',64,258,30,CREAM)
mug(118,363,1.8,CORAL)
for row in range(2):
    for col in range(5):mug(663+col*90,350+row*109,.72,MINT)
arrow(377,426,550,GOLD)
tx('One satisfying coffee',64,549,30,CREAM,'Bold')
tx('Ten tiny, infuriating coffees',650,549,30,CREAM,'Bold')
footer('Invented example. Audience challenge: what should the cafe measure, and how could that measure be gamed?',dark=True)

# 14
new('The rules are part of the invention','02 / Incentives')
heading('The rules are part of the invention')
for x,y,n,title,body in [
 (64,245,'1','An outcome','What changes for the person or place you care about?'),
 (680,245,'2','A measurable finish','What result, by when, under which conditions?'),
 (64,443,'3','Boundaries','What harms, shortcuts or exclusions disqualify a team?'),
 (680,443,'4','Independent proof','Who checks the result, repeats the test and handles disputes?')]:
    tx(n,x,y,64,CORAL,'Display')
    tx(title,x+95,y+3,34,INK,'Bold')
    tx(body,x+95,y+64,26,MUTED,width=450,leading=34)
footer('A design checklist developed from the episode discussion of measurable targets and perverse incentives.',[1])

# 15
new('The moonshot menu','02 / Incentives',dark=True)
heading('The moonshot menu',True,68)
tx('Four frontiers discussed in the episode',64,182,25,'#C2D4DA')
for x,y,n,title,body,col in [
 (64,269,'01','Habitable worlds','Use telescope data to search\nfor places that could support life.',MINT),
 (680,269,'02','Animal communication','Find meaningful patterns\nacross the species barrier.',GOLD),
 (64,459,'03','Learning at scale','Help more children learn,\ninside and outside school.',CORAL),
 (680,459,'04','Organ preservation','Give matching and transport\nmore time to save a life.',MINT)]:
    tx(n,x,y,49,col,'Display')
    tx(title,x+90,y+2,33,CREAM,'Bold')
    tx(body,x+90,y+60,25,'#D0DEDF',leading=33)
footer('Episode, 49:31-54:31. These are discussed ambitions and prize concepts; this slide does not assert current launch status or clinical readiness.',[1],True)

# 16
new('Prizes already reach beyond space','02 / Incentives')
heading('Prizes already reach beyond space')
for x,n,title,body,tag in [
 (64,'01','Cleaner oceans','The oil-cleanup challenge\nrewarded better recovery\ntechnology.','Awarded in 2011'),
 (480,'02','Carbon removal','A $100 million competition\nrewarded solutions for\nremoving atmospheric carbon.','Awarded in 2025'),
 (896,'03','Healthspan','A competition targets\nimproved function as\npeople age.','A goal under pursuit')]:
    circle(x+110,280,65,CORAL if n=='02' else MINT)
    tx(n,x+110,243,76,INK,'Display',align='center')
    tx(title,x,392,32,INK,'Bold')
    tx(body,x,448,25,MUTED,leading=34)
    tx(tag,x,579,20,INK,'Medium')
footer('Competitions demonstrate a way to organize effort. An award alone does not prove universal access or solve an entire field.',[6,7,8])

# 17
new('You have a fictional ten million dollars','Your turn',bg=CORAL)
heading('You have a fictional $10 million',size=68)
tx('60 seconds. One partner. One useful prize.',64,204,31,INK,'Medium')
for yy,num,body in [
 (291,'1','Name a problem that matters to someone.'),
 (382,'2','Describe a result a stranger could verify.'),
 (473,'3','Close the most obvious loophole.')]:
    tx(num,64,yy,52,INK,'Display')
    tx(body,150,yy+7,32,INK,width=1000)
line(64,569,1215,569,INK,2)
tx('The judge asks: could a clever team win while making life worse?',64,600,29,INK,'Bold',width=1120)
footer('Discussion exercise. The budget is fictional.')

# 18
new('Whose values are in the machine?','03 / Alignment',dark=True)
tx('WHOSE VALUES\nARE IN THE\nMACHINE?',64,148,81,CREAM,'Display',leading=85)
tx('Humanity does not arrive\nwith one agreed instruction manual.',68,466,29,'#D0DEDF',leading=39)
for x,y,r in [(935,265,123),(1084,487,80),(795,505,67)]:
    compass(x,y,r)
tx('Useful to whom?',935,80,23,MINT,'Medium',align='center')
tx('Under whose rules?',1010,615,23,GOLD,'Medium',align='center')
footer('The episode raises value disagreement, shared goals and whose interests AI should serve, 1:05:26-1:24:18.',[1],True)

# 19
new('Alignment has three layers','03 / Alignment')
heading('Alignment has three layers')
for yy,n,title,body,col in [
 (241,'01','The model','What behavior does training reward?',MINT),
 (368,'02','The organization','What do growth, competition and liability reward?',GOLD),
 (495,'03','The society','Who benefits, who bears the risk, and who has a voice?',CORAL)]:
    rect(64,yy,80,80,col)
    tx(n,104,yy+17,46,INK,'Display',align='center')
    tx(title,190,yy+2,34,INK,'Bold')
    tx(body,190,yy+55,27,MUTED,width=980)
footer('A discussion framework. Progress at one layer cannot establish alignment across the whole system.',[1])

# 20
new('The score can look great while the outcome gets worse','03 / Alignment',dark=True)
heading('The score can look great\nwhile the outcome gets worse',True,60)
for x,n,title,body in [
 (64,'A','Flattery','The assistant agrees\nbecause agreement\nwins approval.'),
 (478,'B','Shortcut','The agent exploits\na scoring loophole\ninstead of doing the task.'),
 (892,'C','Narrow success','A system meets its metric\nwhile shifting the cost\nto someone else.')]:
    tx(n,x,298,77,CORAL if n=='B' else MINT,'Display')
    tx(title,x,409,33,CREAM,'Bold')
    tx(body,x,466,27,'#D0DEDF',leading=36)
footer('Illustrative mechanisms. OpenAI reported a sycophancy rollback in 2025; Anthropic studied specification gaming in controlled experiments.',[9,10],True)

# 21
new('Trust needs several kinds of evidence','03 / Alignment')
heading('Trust needs several kinds of evidence')
for x,y,n,title,body in [
 (64,237,'1','Values and training','State the desired behavior.\nReward honesty and useful uncertainty.'),
 (680,237,'2','Tests that can surprise it','Use unfamiliar cases and adversarial tests.\nCheck whether the result helps people.'),
 (64,435,'3','Limits on action','Match access to the task.\nRequire review for consequential actions.'),
 (680,435,'4','Accountability after release','Record failures, invite complaints,\nand make correction possible.')]:
    tx(n,x,y,60,CORAL,'Display')
    tx(title,x+80,y+2,31,INK,'Bold',width=465)
    tx(body,x+80,y+67,24,MUTED,width=465,leading=33)
footer('Practical discussion proposals, not a proven recipe for aligning superintelligence. Better training alone is not a safety guarantee.',[1,9,10])

# 22
new('Technology and institutions keep different clocks','03 / Alignment',dark=True)
heading('Technology and institutions\nkeep different clocks',True,62)
for x,title,items,col in [
 (64,'The product clock','Model releases\nNew capabilities\nLower costs',MINT),
 (706,'The public clock','Rules and insurance\nInfrastructure\nTrust and responsibility',GOLD)]:
    tx(title,x,275,36,CREAM,'Bold')
    tx(items,x,347,31,col,leading=49)
line(621,254,621,551,'#3A5A6A',2)
tx('A useful moonshot: make responsible adoption faster.',64,591,32,CREAM,'Medium')
footer('Conceptual comparison inspired by the episode. No measured rates or forecast timeline are implied.',[1],True)

# 23
new('Abundance has a distribution problem','03 / Alignment')
heading('Abundance has a distribution problem',size=57)
tx('More capability can create value. Access determines who feels it.',64,186,28,MUTED)
for i,(title,body) in enumerate([
 ('Affordability','Can people pay for\nhousing, care and learning?'),
 ('Access','Can they actually use\nthe systems and services?'),
 ('Participation','Do they have a voice\nand a share in the gains?')]):
    x=64+i*414
    circle(x+110,329,73,[MINT,GOLD,CORAL][i])
    person(x+110,293,.66,INK)
    tx(title,x,451,34,INK,'Bold')
    tx(body,x,510,27,MUTED,leading=36)
footer('The episode proposes cheaper essentials and broader participation. These are ambitions, not guaranteed outcomes.',[1])

# 24
new('Would you still play?','04 / Purpose',dark=True,art='05-chess.png')
tx('WOULD YOU\nSTILL PLAY?',64,120,85,CREAM,'Display',leading=88)
tx('Suppose a machine could\nbeat everyone at this table.',68,344,30,CREAM,leading=39)
tx('Would that make the evening\nwith your friend worthless?',68,464,30,MINT,leading=39)
footer('Episode, 1:30:30-1:31:25. A thought experiment about the value of play. Conceptual illustration.',[1],True)

# 25
new('Meaning can survive being outperformed','04 / Purpose')
heading('Meaning can survive\nbeing outperformed',size=65)
for x,n,title,body in [
 (64,'01','The experience','The pleasure of making,\nlearning and trying.'),
 (480,'02','The people','Time shared with friends,\nfamily and community.'),
 (896,'03','The contribution','A difference that matters\nto someone you care about.')]:
    tx(n,x,303,76,CORAL,'Display')
    tx(title,x,417,32,INK,'Bold')
    tx(body,x,477,27,MUTED,leading=36)
tx('A world record has never been the only reason to do something.',64,595,29,INK,'Medium')
footer('Philosophical synthesis of the conversation, not a prediction that automation makes every transition easy.',[1])

# 26
new('A purpose worth trying this week','04 / Purpose',dark=True)
heading('A purpose worth trying this week',True,64)
tx('I care about',64,249,32,'#C2D4DA')
line(331,286,1195,286,MINT,2)
tx('I want to help',64,356,32,'#C2D4DA')
line(331,393,1195,393,MINT,2)
tx('This week I will',64,463,32,'#C2D4DA')
line(331,500,1195,500,MINT,2)
tx('Example: help my neighbor learn a new skill, together, for one hour.',64,581,27,GOLD,width=1120)
footer('60-second reflection. A purpose can begin small, and it can change as you learn.',dark=True)

# 27
new('The best future has other people in it','04 / Purpose',dark=True,art='06-community.png')
tx('THE BEST FUTURE\nHAS OTHER\nPEOPLE IN IT',64,103,70,CREAM,'Display',leading=73)
tx('More time to make things.\nMore room to care.\nMore reasons to gather.',68,410,31,CREAM,leading=44)
footer('The conversation returns to shared purpose, collective creativity and human connection.',[1],True)

# 28
new('What is your moonshot?','The question to take home',dark=True)
star(1138,149,35,GOLD);star(1059,221,13,MINT);star(1183,277,17,CORAL)
tx('WHAT IS YOUR\nMOONSHOT?',64,135,105,CREAM,'Display',leading=105)
tx('A problem worth solving.\nA result worth proving.\nSomeone worth doing it with.',68,409,36,MINT,leading=52)
tx('Tomorrow will need better tools. It will also need our choices.',68,605,27,CREAM,'Medium')
footer('Discussion ends here. Evidence notes and clickable sources follow.',dark=True)

# 29
new('Three headlines, read carefully','Evidence notes')
heading('Three headlines, read carefully',size=60)
for yy,label,body in [
 (219,'The flying Roadster','The episode describes a demo and gives performance and street-legality claims. This deck uses it as a discussion prompt, without certifying those details.'),
 (351,'The 84% robotics drop','The transcript quotes $2.36 to $0.38 from July to September. That pair was not verified in the primary page checked. Slide 6 uses its published $1.14 vs $0.90 comparison instead.'),
 (500,'The physics score','The primary preprint reports 98%, or 49 out of 50. It does not establish a perfect score, autonomous discovery, or a date when physics will be solved.')]:
    tx(label,64,yy,29,INK,'Bold')
    tx(body,441,yy,23,MUTED,width=746,leading=31)
footer('Evidence checked 20 October 2026. Source detail matters more than the size of a headline.',[1,2,3,11])

# 30
new('How to read this presentation','Evidence notes')
heading('How to read this presentation',size=61)
for yy,title,body in [
 (215,'Reported results','Benchmark numbers and historical prize results link to the relevant primary source. A benchmark is evidence within its test conditions.'),
 (345,'Ideas from the conversation','New prize concepts, abundant essentials and future human purpose appear as proposals or discussion themes. They are not forecasts presented as facts.'),
 (475,'Illustrations and exercises','Artwork is conceptual. The cafe example, reliability calculation, alignment checklist and audience challenges are explanatory additions.')]:
    tx(title,64,yy,30,INK,'Bold')
    tx(body,520,yy,24,MUTED,width=675,leading=33)
footer('The deck omits sponsor segments and does not rely on the organ-memory anecdote, sweeping historical claims, or speculative timelines.',[1])

# 31
new('Sources for machines and moonshots','Reading room')
heading('Sources for machines and moonshots',size=55)
def source_row(num,y,subtitle):
    title,url=SOURCES[num]
    tx(f'[{num}]',64,y,25,CORAL,'Bold')
    tx(title,130,y,26,INK,'Bold')
    tx(subtitle,130,y+36,20,MUTED,width=1050)
    c.linkURL(url,(64,H-y-65,1205,H-y+3),relative=0,thickness=0)
for n,y,sub in [
 (1,199,'Supplied transcript. Main themes: 07:07, 17:33, 29:31, 36:16, 1:05:26 and 1:24:24.'),
 (2,283,'23 September 2026. Six-task comparison, estimated inference cost and partial progress.'),
 (3,367,'9 October 2026. TheoPhysEval preprint, arXiv:2610.16733.'),
 (4,451,'Official competition history, winning target and 2004 result.'),
 (5,535,'Official biography of Anousheh Ansari.'),
 (11,619,'Official product page. Consult current specifications and conditions.')]:
    source_row(n,y,sub)
footer()

# 32
new('Sources for incentives and alignment','Reading room')
heading('Sources for incentives and alignment',size=55)
for n,y,sub in [
 (6,199,'Official Wendy Schmidt Oil Cleanup XCHALLENGE competition page.'),
 (7,283,'Official Carbon Removal competition page and 2025 award history.'),
 (8,367,'Official Healthspan competition page. A target is distinct from a completed outcome.'),
 (9,451,'2 May 2025. OpenAI explains its GPT-4o sycophancy failure and response.'),
 (10,535,'17 June 2024. Anthropic investigates specification gaming and reward tampering.')]:
    source_row(n,y,sub)
tx('Click a source title to open the original. Return to any section with the PDF bookmarks.',64,623,21,MUTED)
footer('All web sources checked 20 October 2026.')

c.save()
(ROOT/'qa/slide-manifest.json').write_text(json.dumps(RECORDS,indent=2))
(ROOT/'qa/text-boxes.json').write_text(json.dumps(BOXES,indent=2))
(ROOT/'source/sources.json').write_text(json.dumps(SOURCES,indent=2))
print(json.dumps({'pdf':str(OUT),'pages':PAGE,'text_lines':len(BOXES)},indent=2))
