from pathlib import Path
import json
import re
import hashlib
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'how-anthropic-builds-with-ai.pdf'
BUILD = ROOT / '.build'
BUILD.mkdir(exist_ok=True)
W, H = 960, 540
INK = '#2D2530'
PAPER = '#F6F1E8'
RUST = '#AF482F'
PALE = '#E3CBB6'
MUTED = '#6C6268'
LINE = '#D9CFC4'
GREEN = '#40695B'

FONT_DIR = Path('/usr/share/fonts/truetype/ibm-plex')
for name, filename in [('Plex','IBMPlexSans-Regular.ttf'),('PlexBold','IBMPlexSans-Bold.ttf'),('PlexMedium','IBMPlexSans-Medium.ttf'),('PlexMono','IBMPlexMono-Regular.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
pdfmetrics.registerFontFamily('Plex', normal='Plex', bold='PlexBold', italic='Plex', boldItalic='PlexBold')

SOURCES = {
 '1': {'title':'How the Claude Code team does code review','date':'15 October 2026','url':'https://claude.dev/blog/solving-code-review-at-anthropic/'},
 '2': {'title':'Redesigning source control at Anthropic','date':'13 October 2026, updated 15 October','url':'https://www.anthropic.com/research/redesigning-source-control'},
 '3': {'title':'How Anthropic teams use Claude Code','date':'24 July 2025','url':'https://claude.com/resources/articles/how-anthropic-teams-use-claude-code'},
 '4': {'title':'Making Claude Code more secure and autonomous','date':'20 October 2025','url':'https://www.anthropic.com/research/claude-code-sandboxing'},
 '5': {'title':'An update on recent Claude Code quality reports','date':'23 April 2026','url':'https://www.anthropic.com/research/april-23-postmortem'},
 '6': {'title':'Introducing Claude Tag','date':'23 June 2026','url':'https://www.anthropic.com/news/introducing-claude-tag'},
}

SLIDES = [
 {'title':'How Anthropic builds with AI','seconds':40,'sources':[]},
 {'title':'What changed inside Claude Code','seconds':55,'sources':['1']},
 {'title':'The engineering loop','seconds':60,'sources':['1','2','6']},
 {'title':'Tasks worth delegating','seconds':60,'sources':['3']},
 {'title':'A brief an agent can execute','seconds':85,'sources':['1','3']},
 {'title':'Proof of completion','seconds':70,'sources':['1','3']},
 {'title':'Context that survives the session','seconds':65,'sources':['1']},
 {'title':'Parallel work with one owner','seconds':65,'sources':['6','1']},
 {'title':'Review that converges','seconds':75,'sources':['1']},
 {'title':'Human approval follows risk','seconds':80,'sources':['1']},
 {'title':'Autonomy needs enforced limits','seconds':65,'sources':['4','6']},
 {'title':'A release path built for recovery','seconds':70,'sources':['1']},
 {'title':'Prompts and reviewers need regression tests','seconds':75,'sources':['1','5']},
 {'title':'Humans own system-level judgment','seconds':65,'sources':['2','1']},
 {'title':'Bottlenecks move beyond coding','seconds':65,'sources':['2']},
 {'title':'A scorecard for useful throughput','seconds':70,'sources':['1']},
 {'title':'A two-week pilot','seconds':85,'sources':['1','3']},
 {'title':'The next task is the starting point','seconds':50,'sources':['1','2','3']},
 {'title':'Sources for the playbook','seconds':0,'sources':[]},
 {'title':'Sources and evidence limits','seconds':0,'sources':[]},
]

c = canvas.Canvas(str(OUT), pagesize=(W,H), pageCompression=1, initialFontName='Plex', initialFontSize=12)
c.setTitle('How Anthropic builds with AI: The practical engineering playbook')
c.setAuthor('')
c.setSubject('18 self-contained presentation slides for 20 minutes, with 2 reference slides. Research dated 27 October 2026.')
c.setCreator('')
c.setViewerPreference('DisplayDocTitle', 'true')
c.showOutline()
boxes = []
current = 0
dark = False

def para(text, x, top, width, size=21, font='Plex', color=None, leading=None, maxh=None):
    text = text.replace('\n', '<br/>')
    color = color or (PAPER if dark else INK)
    style = ParagraphStyle('p',fontName=font,fontSize=size,leading=leading or size*1.22,
                           textColor=HexColor(color),alignment=TA_LEFT,spaceBefore=0,spaceAfter=0)
    p = Paragraph(text,style)
    pw, ph = p.wrap(width, H)
    if maxh is not None and ph > maxh + .1:
        raise ValueError(f'Slide {current}: text height {ph:.1f} exceeds {maxh}: {text}')
    if top + ph > H-40 and size > 12:
        raise ValueError(f'Slide {current}: text enters footer: {text}')
    p.drawOn(c,x,H-top-ph)
    boxes.append({'slide':current,'text':re.sub('<[^>]+>','',text),'x':x,'top':top,'w':width,'h':ph,'size':size})
    return ph

def rule(top, x=48, width=864, color=None, thickness=.7):
    c.setStrokeColor(HexColor(color or ('#63515E' if dark else LINE)))
    c.setLineWidth(thickness)
    c.line(x,H-top,x+width,H-top)

def number(text,x,top,width=230,size=92,color=None):
    return para(text,x,top,width,size,'PlexMedium',color,leading=size*1.02)

def begin(n, title=None, bg=PAPER, image=None):
    global current,dark
    current=n
    dark=bg==INK
    c.setFillColor(HexColor(bg)); c.rect(0,0,W,H,fill=1,stroke=0)
    if image:
        c.drawImage(str(ROOT/'assets'/image),0,0,W,H,mask='auto')
    c.bookmarkPage(f'slide-{n}')
    c.addOutlineEntry(SLIDES[n-1]['title'],f'slide-{n}',level=0)
    if title:
        para(title,48,42,858,38,'PlexMedium',maxh=96)

def end(note=None):
    s=SLIDES[current-1]
    label = note or ('Sources '+', '.join('['+x+']' for x in s['sources']) if s['sources'] else '')
    footer_color = '#D8C7CA' if dark else '#716770'
    if label:
        para(label,48,511,808,10.4,color=footer_color,leading=12)
        if s['sources']:
            c.linkRect('', 'slide-19' if all(int(x)<=3 for x in s['sources']) else 'slide-20', (48,14,780,32),relative=0,thickness=0)
    para(f'{current:02d}',882,509,30,12,'PlexMono',footer_color,leading=14)
    c.showPage()

# 01. Image-led cover, keeping all typography selectable.
begin(1,image='workshop.png')
para('THE PRACTICAL ENGINEERING PLAYBOOK',48,51,480,12,'PlexMedium',RUST)
para('How Anthropic<br/>builds with AI',46,137,500,60,'PlexMedium',leading=62,maxh=190)
para('Briefs, verification, review<br/>and the human decisions that matter.',49,338,390,23,leading=29)
para('20 minutes',49,449,200,15,'PlexMedium')
end('Based on research dated 27 October 2026')

# 02. Precisely scoped evidence, no company-wide conflation.
begin(2,'What changed inside Claude Code',bg=INK)
number('~90%',47,140,470,116,PALE)
para('of Claude Code\'s own code<br/>comes from Claude',53,270,410,25,maxh=70)
number('>2x',542,155,280,64,PALE)
para('merged pull requests',548,226,340,23)
number('>40%',542,302,300,64,PALE)
para('reduction in the share reverted',548,373,340,23,maxh=60)
para('Higher output changes the engineering process.\nHuman attention shifts toward judgment and verification.',52,434,840,20,leading=25,maxh=54)
end('Claude Code team self-report [1]. PR and revert comparisons: June to September 2026. Not a controlled study.')

# 03. Editorial sequence; the arrangement is a synthesis, not an internal architecture claim.
begin(3,'The engineering loop')
steps=[('01','Specify','A person defines the outcome, constraints and success evidence.'),
       ('02','Delegate','Claude Code or Slack agents implement, test and iterate.'),
       ('03','Verify','Runnable checks and a fresh reviewer test the result.'),
       ('04','Approve','Automated gates and risk determine required human review.'),
       ('05','Release','Flags, staged exposure and monitoring limit the impact.'),
       ('06','Learn','Incidents and recurring findings improve tests and instructions.')]
for i,(n,t,b) in enumerate(steps):
    col=i//3; row=i%3; x=48+col*450; y=146+row*105
    para(n,x,y,60,29,'PlexMono',RUST)
    para(t,x+72,y,335,23,'PlexBold')
    para(b,x+72,y+32,335,18.5,leading=23,maxh=52)
rule(474)
end('Synthesis of documented practices [1, 2, 6]. Teams use different tools and approval policies.')

# 04. Selection criteria grounded in practical examples.
begin(4,'Tasks worth delegating')
para('Strong first candidates',48,135,410,27,'PlexMedium',RUST)
para('Bug fixes with a reproducible failure<br/><br/>Tests for known behavior<br/><br/>Refactors with stable interfaces<br/><br/>Small features with visible acceptance criteria',48,187,390,22,leading=27,maxh=250)
para('Human framing comes first',511,135,405,27,'PlexMedium',GREEN)
para('Ambiguous product decisions<br/><br/>Changes spanning undocumented systems<br/><br/>Migrations with unclear invariants<br/><br/>Work without a reliable correctness check',511,187,395,22,leading=27,maxh=250)
rule(458)
para('A good delegation target has a bounded scope and an observable finish line.',48,472,855,18,'PlexMedium')
end('Practical selection guide derived from Anthropic team workflows [3].')

# 05. Fully usable brief, clearly an illustrative adaptation.
begin(5,'A brief an agent can execute')
para('Example task: fix duplicate submissions during a slow save',48,111,850,23,'PlexMedium',RUST)
brief=[('OUTCOME','A repeated click cannot create a second pending save request.'),
       ('CONTEXT','Inspect the form, save handler and existing integration tests.'),
       ('CONSTRAINTS','Preserve validation and keyboard access. Keep the API unchanged.'),
       ('PROOF','Reproduce the bug. Add a failing test, fix it, then rerun the checks.'),
       ('HANDOFF','Return the diff, test output, remaining risks and rollback steps.'),
       ('STOP RULE','Ask before changing shared contracts or expanding the scope.')]
for i,(label,body) in enumerate(brief):
    y=167+i*51
    rule(y-10)
    para(label,48,y,164,13.5,'PlexMono',MUTED)
    para(body,224,y-3,680,19.5,leading=23.5,maxh=47)
end('Illustrative brief based on verification and task-framing practices [1, 3].')

# 06. The second original illustration adds meaning to the verification lesson.
begin(6,image='verification.png')
para('Proof of<br/>completion',48,45,495,43,'PlexMedium',leading=46)
proof=[('Behavior','Show the expected result on the actual user journey.'),
       ('Checks','Attach relevant test, build or browser output.'),
       ('Regression','Show that the check catches the original failure.'),
       ('Limits','State what you did not verify and why.')]
for i,(t,b) in enumerate(proof):
    y=164+i*84
    para(t,48,y,400,21,'PlexBold')
    para(b,48,y+28,399,19,leading=23,maxh=49)
end('Adapted from the Claude Code team\'s executable verification practice [1, 3].')

# 07. Three distinct jobs for durable context.
begin(7,'Context that survives the session')
rows=[('CLAUDE.md','Project knowledge','Stack, commands, conventions and non-goals. Keep it short and link to deeper documentation.'),
      ('REVIEW.md','Review priorities','Describe real failure modes, sensitive areas and evidence required for a finding.'),
      ('Skills + checks','Repeatable work','Encode useful procedures. Turn recurring feedback into a skill, lint rule or test.')]
for i,(name,head,body) in enumerate(rows):
    y=153+i*108
    para(name,48,y,295,26,'PlexMono',RUST)
    para(head,364,y,542,23,'PlexBold')
    para(body,364,y+34,542,21,maxh=57)
    if i<2:rule(y+91)
para('Repeated corrections are evidence that the working context needs an update.',48,478,860,18,'PlexMedium')
end('Claude Code team practice [1]. File names and conventions can be adapted to another agent harness.')

# 08. Parallelism described without implying one universal Anthropic topology.
begin(8,'Parallel work with one owner')
para('Anthropic delegates work to multiple Claudes through Slack.\nParallel work still needs clear interfaces and a person accountable for the result.',48,117,860,23,leading=29,maxh=88)
rule(221)
para('Independent work',48,247,402,28,'PlexMedium',RUST)
para('One agent implements the change.<br/><br/>A fresh reviewer examines the diff.<br/><br/>Other agents validate findings.',48,295,395,21,leading=27,maxh=170)
para('Integration responsibility',520,247,394,28,'PlexMedium',GREEN)
para('A person owns shared assumptions and the final change.<br/><br/>Suggested start: one implementer and one reviewer. Expand when coordination works.',520,295,385,21,leading=27,maxh=170)
end('Slack delegation and fresh-context review [6, 1]. Starting configuration is a suggested adaptation.')

# 09. Large numerals make the failure and remedy memorable.
begin(9,'Review that converges',bg=INK)
number('50+',47,141,420,112,PALE)
para('review / fix rounds<br/>on one PR overnight',53,266,360,25,leading=30)
para('A documented failure of agents\nkeeping one another busy.',53,359,370,21,leading=27)
number('3',540,146,300,105,PALE)
para('rounds before the author<br/>must reconsider the approach',546,264,357,24,leading=30)
para('Later passes focus on changed code.<br/>Reviewers avoid repeating findings.<br/>They identify the whole bug class.',546,360,363,20,leading=27,maxh=100)
end('Claude Code team example and revised review policy [1]. The three-round cap triggers reassessment.')

# 10. Exact scope of approvals and the trusted-author exception retained.
begin(10,'Human approval follows risk')
tiers=[('0','LOW RISK','Docs, copy, internal features or additive changes behind a flag.'),
       ('1','MEDIUM RISK','Ordinary product changes and sensitive behavior such as caching or system prompts.'),
       ('2','HIGH RISK','The highest-risk changes and paths with an explicit two-person requirement.')]
for i,(n,t,b) in enumerate(tiers):
    x=48+i*298
    number(n,x,130,230,86,RUST)
    para(t,x,228,265,15,'PlexMono',MUTED)
    para(b,x,263,258,21,leading=26,maxh=110)
rule(392)
para('Required human approvals after automated review, security checks and CI pass. Lighter paths apply only to trusted authors. Sensitive paths retain human requirements.',48,408,864,19.5,leading=25,maxh=55)
para('The directing human owns the change. An agent cannot fill a required human slot.',48,468,864,18.5,'PlexMedium',maxh=24)
end('Claude Code team policy [1]. The directing author can count toward the required human total.')

# 11. Third original image: a visual metaphor, not an implementation diagram.
begin(11,bg=INK,image='boundaries.png')
para('Autonomy needs<br/>enforced limits',48,45,465,42,'PlexMedium',leading=46)
controls=[('Workspace','Limit which files the agent can read and change.'),
          ('Network','Allow only the destinations the task needs.'),
          ('Identity','Scope credentials, tools, data and spending.'),
          ('Oversight','Keep action logs and clear escalation boundaries.')]
for i,(t,b) in enumerate(controls):
    y=164+i*84
    para(t,48,y,399,21,'PlexBold',PALE)
    para(b,48,y+28,390,19,leading=23,maxh=48)
end('Filesystem and network isolation [4]. Scoped access, spend controls and audit logs [6].')

# 12. Sequential release steps, with concrete ownership.
begin(12,'A release path built for recovery')
release=[('01','Merge queue','Run checks against main with the change applied.'),
         ('02','Feature flag','Keep new behavior easy to disable.'),
         ('03','Staged exposure','Exercise changes internally before wider release.'),
         ('04','Detection','Watch user behavior, failures and incident signals.'),
         ('05','Recovery','A named owner can disable, revert or fix quickly.')]
for i,(n,t,b) in enumerate(release):
    y=143+i*59
    para(n,48,y,62,23,'PlexMono',RUST)
    para(t,131,y,246,22,'PlexBold')
    para(b,387,y,518,21,leading=26,maxh=54)
    if i<4:rule(y+46)
para('Before merging: how will we notice a failure, and how will we undo the change?',48,472,860,19,'PlexMedium')
end('Release and rollback practices reported by the Claude Code team [1].')

# 13. Include the less obvious practical lesson: prompt/harness changes need evaluation.
begin(13,'Prompts and reviewers need\nregression tests')
para('Past incidents test review',48,161,409,25,'PlexMedium',RUST)
para('Save the offending PR and its fix or revert.<br/><br/>Confirm the bug with an engineer.<br/><br/>Test whether the reviewer catches it.<br/><br/>Include clean PRs to measure false alarms.',48,209,391,21,leading=26,maxh=260)
para('Configuration needs tests',515,161,397,25,'PlexMedium',GREEN)
para('Anthropic traced quality losses to reasoning settings, context caching and a brevity prompt.<br/><br/>Its response included broader model-specific evaluations, the public build in internal testing, and gradual rollout.',515,209,389,21,leading=27,maxh=260)
end('Incident-driven reviewer evaluations [1]. April 2026 quality postmortem [5].')

# 14. Human review retains concrete responsibilities.
begin(14,'Humans own system-level judgment')
para('A locally plausible change can still violate the architecture.',48,112,870,25,'PlexMedium',RUST)
para('Scion\'s source-control team',48,179,390,24,'PlexBold')
para('Agents sometimes scanned commit history when the code-review service already owned the answer.<br/><br/>Adversarial review sometimes added excessive validation for hypothetical concerns.',48,225,393,22,leading=28,maxh=220)
para('What the human decides',522,179,390,24,'PlexBold')
para('Which system owns this fact?<br/><br/>Which invariants must stay true?<br/><br/>Is the added complexity justified?<br/><br/>Are we solving the right problem?',522,225,382,22,leading=28,maxh=220)
end('Scion team examples [2]. Accountability remains with the person directing the agent [1].')

# 15. One scale case, framed as a lesson rather than a prescribed tool migration.
begin(15,'Bottlenecks move beyond coding',bg='#EBD4BF')
para('Anthropic monorepo: merged changes per day',48,115,857,23,'PlexMedium')
number('~2,500',45,168,420,86,RUST)
para('May 2026',51,270,400,21,'PlexMedium')
number('>30,000',493,168,430,86,RUST)
para('September 2026',501,270,400,21,'PlexMedium')
rule(323,color='#C7AA91')
para('Seven engineers built Scion source control, Antique code review and related systems, then migrated the monorepo in five months.',48,346,415,23,leading=29,maxh=120)
para('Transferable lesson',520,346,385,23,'PlexBold')
para('Measure review queues, checkouts and CI. Improve the limiting stage before adding more agent capacity.',520,386,385,22,leading=27,maxh=90)
end('Anthropic self-report [2]. Scion is internal and tailored to an unusual workload, not a general Git replacement.')

# 16. A compact native scorecard; no invented performance targets.
begin(16,'A scorecard for useful throughput')
score=[('Delivery','Time from accepted task to verified change'),
       ('Human effort','Review time, waiting and repair work'),
       ('Quality','Escaped defects, reverts and incidents'),
       ('Review efficiency','False alarms and rounds to pass'),
       ('Economics','Total cost per accepted change')]
for i,(label,metric) in enumerate(score):
    y=145+i*55
    para(label,48,y,265,22,'PlexBold',RUST)
    para(metric,328,y,580,22,maxh=54)
    rule(y+40)
para('Expand autonomy when delivery improves and quality holds.',48,452,855,23,'PlexMedium',leading=28,maxh=56)
end('Suggested scorecard. Review time, reverts, incidents, noise and convergence reflect reported practice [1].')

# 17. Complete proposed pilot, self-contained and actionable.
begin(17,'A two-week pilot')
para('One repository. One owner. A small set of comparable tasks.',48,112,860,24,'PlexMedium',RUST)
pilot=[('DAYS 1-2','Establish the baseline','Choose bounded tasks, record current delivery and review effort, and define quality limits.'),
       ('DAYS 3-5','Run the complete loop','Use the brief, runnable proof and fresh review. Keep required human approvals.'),
       ('DAYS 6-10','Improve one bottleneck','Turn repeated feedback into context or checks. Compare results and total effort with baseline.')]
for i,(label,title,body) in enumerate(pilot):
    y=176+i*96
    para(label,48,y,176,16,'PlexMono',MUTED)
    para(title,235,y-4,670,23,'PlexBold')
    para(body,235,y+28,670,21,leading=26,maxh=57)
    if i<2:rule(y+80)
para('Decision: expand one task type, refine the process, or pause if quality worsens.',48,474,860,18.5,'PlexMedium')
end('Proposed adoption plan derived from the research [1, 3]. It is not Anthropic\'s published rollout schedule.')

# 18. A concise closing slide that also works as a take-away.
begin(18,bg=INK)
para('The next task is<br/>the starting point',48,49,857,51,'PlexMedium',leading=55)
closing=[('01','Write the outcome and constraints.'),
         ('02','Define the proof before implementation.'),
         ('03','Name the owner, review rule and rollback.')]
for i,(n,t) in enumerate(closing):
    y=229+i*66
    para(n,48,y,73,27,'PlexMono',PALE)
    para(t,138,y-1,766,28,'PlexMedium',leading=34,maxh=45)
rule(441)
para('Engineering judgment and verification make delegation useful.',48,461,864,24,'PlexMedium',PALE)
end('Practical synthesis of Anthropic\'s reported workflows [1, 2, 3].')

# 19-20. Clickable reference slides are outside the 20-minute running order.
def source_entry(key, top, description):
    s=SOURCES[key]
    para('['+key+']',48,top,62,23,'PlexMono',RUST)
    title='<link href="'+s['url']+'" color="'+INK+'">'+s['title']+'</link>'
    para(title,124,top,780,23,'PlexBold',leading=27,maxh=59)
    para(s['date'],124,top+58,777,13.5,'PlexMono',MUTED)
    para(description,124,top+82,775,18,leading=23,maxh=50)

begin(19,'Sources for the playbook')
source_entry('1',125,'Verification, review, approvals, release controls, convergence and the Claude Code metrics.')
source_entry('2',245,'Scion\'s scale, delivery timeline, architectural tradeoffs and human oversight.')
source_entry('3',365,'Team workflows for testing, debugging, code navigation and bounded implementation.')
end('Reference slide. Titles are clickable links to the primary sources. Research cutoff: 27 October 2026.')

begin(20,'Sources and evidence limits')
for idx,key in enumerate(['4','5','6']):
    y=126+idx*76
    s=SOURCES[key]
    para('['+key+']',48,y,61,22,'PlexMono',RUST)
    para('<link href="'+s['url']+'" color="'+INK+'">'+s['title']+'</link>',124,y,777,21,'PlexBold',leading=24,maxh=50)
    para(s['date'],124,y+48,777,13,'PlexMono',MUTED)
rule(362)
para('How to read the evidence',48,380,861,23,'PlexBold')
para('Metrics are Anthropic self-reports, with different teams and measurement periods. They do not establish causal productivity gains. The example brief, scorecard and pilot are proposed adaptations. Public disclosures do not establish one universal internal setup.',48,419,863,18,leading=23,maxh=73)
end('Based on the supplied research and linked primary sources. Reference slides are outside the 20-minute pacing.')

c.save()

# Keep editable source, timing and verification metadata alongside the deliverable.
elapsed=0
for s in SLIDES:
    s['start_seconds']=elapsed
    elapsed+=s['seconds']
assert elapsed==1200
(ROOT/'source'/'slide-plan.json').write_text(json.dumps({'duration_seconds':elapsed,'size_points':[W,H],'slides':SLIDES,'sources':SOURCES},indent=2),encoding='utf-8')
(BUILD/'text-geometry.json').write_text(json.dumps(boxes,indent=2),encoding='utf-8')

import pymupdf
doc=pymupdf.open(OUT)
assert len(doc)==20
for page in doc:
    assert abs(page.rect.width-W)<.01 and abs(page.rect.height-H)<.01
    assert page.get_text().strip()
    page.get_pixmap(matrix=pymupdf.Matrix(4/3,4/3),alpha=False).save(BUILD/f'slide-{page.number+1:02d}.png')
text='\n\n'.join('SLIDE '+str(p.number+1)+'\n'+p.get_text() for p in doc)
(BUILD/'extracted-text.txt').write_text(text,encoding='utf-8')
report={'pages':len(doc),'size_points':[W,H],'timed_slides':18,'reference_slides':2,'duration_seconds':elapsed,'links':sum(len(p.get_links()) for p in doc),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()}
(BUILD/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
