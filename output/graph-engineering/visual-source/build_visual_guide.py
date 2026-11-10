#!/usr/bin/env python3
"""Build the standalone visual companion. Run with the workspace PDF Python."""
from pathlib import Path
from math import atan2, cos, sin, pi
import json
import re
import hashlib
from statistics import mean
from reportlab.pdfgen import canvas
from reportlab import rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import pymupdf as fitz

BASE = Path(__file__).resolve().parents[1]
ASSETS = BASE / "visual-assets"
OUT = BASE / "graph-engineering-visual-guide.pdf"
TMP = BASE.parent.parent / "tmp/pdfs/graph-visual"
TMP.mkdir(parents=True, exist_ok=True)
W, H = 960, 600
M = 48
BG = "#F5F1E8"
INK = "#163C3D"
MUTED = "#536665"
LINE = "#D4DBD2"
PALE = "#E5EBE2"
WHITE = "#FFFCF5"
ORANGE = "#C34E2D"
LIGHT = "#B4CBC1"

FONT_ROOT = Path("/usr/share/fonts/truetype/ibm-plex")
DESIGN_FONTS = Path("/mnt/c/Users/apexw/.agents/skills/canvas-design/canvas-fonts")
for name, path in {
    "Body": FONT_ROOT / "IBMPlexSans-Regular.ttf",
    "Medium": FONT_ROOT / "IBMPlexSans-Medium.ttf",
    "Bold": FONT_ROOT / "IBMPlexSans-SemiBold.ttf",
    "Mono": FONT_ROOT / "IBMPlexMono-Regular.ttf",
    "Display": DESIGN_FONTS / "BricolageGrotesque-Regular.ttf",
    "DisplayBold": DESIGN_FONTS / "BricolageGrotesque-Bold.ttf",
    "Serif": DESIGN_FONTS / "CrimsonPro-Italic.ttf",
}.items():
    pdfmetrics.registerFont(TTFont(name, str(path)))

rl_config.useA85 = False
c = canvas.Canvas(str(TMP / "unoptimized.pdf"), pagesize=(W, H), pageCompression=1,
                  initialFontName="Body", initialFontSize=12)
c.setTitle("Graph Engineering | The Visual Guide")
c.setAuthor("")
c.setSubject("A standalone, concise guide to agent loops, execution graphs and practical patterns.")
c.setCreator("Graph Engineering")
c.setKeywords("graph engineering, agents, workflows, state, verification")
PAGES = []
TEXT_BOXES = []
CURRENT = 0
CURRENT_SECTION = ""
CURRENT_DARK = False

def rect(x, y, w, h, fill=BG, stroke=None, radius=0, lw=1):
    c.setLineWidth(lw)
    if fill: c.setFillColor(HexColor(fill))
    if stroke: c.setStrokeColor(HexColor(stroke))
    if radius:
        c.roundRect(x, H-y-h, w, h, radius, stroke=int(bool(stroke)), fill=int(bool(fill)))
    else:
        c.rect(x, H-y-h, w, h, stroke=int(bool(stroke)), fill=int(bool(fill)))

def line(x1, y1, x2, y2, color=LINE, width=1):
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(width)
    c.line(x1, H-y1, x2, H-y2)

def circle(x, y, radius, fill=INK, stroke=None, width=1):
    c.setLineWidth(width)
    c.setFillColor(HexColor(fill))
    if stroke: c.setStrokeColor(HexColor(stroke))
    c.circle(x, H-y, radius, stroke=int(bool(stroke)), fill=1)

def txt(x, y, s, size=20, font="Body", color=INK, align="left"):
    c.setFont(font, size)
    c.setFillColor(HexColor(color))
    width = pdfmetrics.stringWidth(s, font, size)
    bx = x if align == "left" else x-width/2 if align == "center" else x-width
    c.drawString(bx, H-y-size, s)
    TEXT_BOXES.append((CURRENT, bx, y, width, size, s))
    return width

def wrap(s, width, size, font):
    result = []
    for para in s.split("\n"):
        words = para.split()
        row = ""
        for word in words:
            test = (row + " " + word).strip()
            if pdfmetrics.stringWidth(test, font, size) > width and row:
                result.append(row)
                row = word
            else:
                row = test
        result.append(row)
    return result

def para(x, y, s, width, size=21, leading=None, font="Body", color=INK):
    leading = leading or size*1.3
    for row in wrap(s, width, size, font):
        txt(x, y, row, size, font, color)
        y += leading
    return y

def label(x, y, s, color=MUTED, size=10.5):
    return txt(x, y, s.upper(), size, "Mono", color)

def arrow(points, color=INK, width=2, head=7, dash=False):
    c.saveState()
    c.setStrokeColor(HexColor(color))
    c.setFillColor(HexColor(color))
    c.setLineWidth(width)
    c.setLineJoin(1)
    if dash: c.setDash(5, 4)
    p = c.beginPath()
    p.moveTo(points[0][0], H-points[0][1])
    for x, y in points[1:]: p.lineTo(x, H-y)
    c.drawPath(p)
    if dash: c.setDash()
    x, y = points[-1]
    px, py = points[-2]
    a = atan2(y-py, x-px)
    p = c.beginPath()
    p.moveTo(x, H-y)
    p.lineTo(x-head*cos(a-pi/6), H-(y-head*sin(a-pi/6)))
    p.lineTo(x-head*cos(a+pi/6), H-(y-head*sin(a+pi/6)))
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()

def node(x, y, w, title, h=62, kind="agent", size=20, sub=None):
    styles = {
        "agent": (INK, WHITE, None),
        "plain": (PALE, INK, None),
        "outline": (BG, INK, INK),
        "accent": (ORANGE, WHITE, None),
        "light": (WHITE, INK, None),
    }
    fill, color, stroke = styles[kind]
    rect(x, y, w, h, fill, stroke, 13, 1.4)
    ty = y + (h-size)/2-3 if not sub else y+9
    txt(x+w/2, ty, title, size, "Medium", color, "center")
    if sub: txt(x+w/2, y+h-24, sub, 11, "Mono", color, "center")

def picture(name, x, y, w, h=None):
    h = h or w
    c.drawImage(str(ASSETS / (name+".png")), x, H-y-h, w, h, mask="auto")

def foot(n, section, dark=False):
    color = LIGHT if dark else MUTED
    line(M, 550, W-M, 550, "#446061" if dark else LINE)
    label(M, 566, "GRAPH ENGINEERING / VISUAL GUIDE", color, 9)
    label(W/2, 566, section, color, 9)
    txt(W-M, 563, f"{n:02d} / 24", 11, "Mono", color, "right")

def start(n, section, title, sub=None, dark=False, size=42):
    global CURRENT, CURRENT_SECTION, CURRENT_DARK
    CURRENT = n
    CURRENT_SECTION, CURRENT_DARK = section, dark
    PAGES.append({"page": n, "section": section, "title": title.replace("\n", " ")})
    rect(0, 0, W, H, INK if dark else BG)
    color = WHITE if dark else INK
    label(M, 34, section, LIGHT if dark else MUTED)
    txt(W-M, 26, f"{n:02d}", 24, "Display", ORANGE if not dark else LIGHT, "right")
    para(M, 73, title, W-2*M, size, size*1.08, "DisplayBold", color)
    if sub: para(M, 133, sub, 850, 20, 26, color=LIGHT if dark else MUTED)
    c.bookmarkPage(f"page-{n}")
    c.addOutlineEntry(PAGES[-1]["title"], f"page-{n}", level=0)

def end():
    if CURRENT != 1:
        foot(CURRENT, CURRENT_SECTION, CURRENT_DARK)
    c.showPage()

def takeaway(s, dark=False):
    rect(M, 480, W-2*M, 46, "#254A4B" if dark else PALE, radius=10)
    circle(M+20, 503, 3.5, ORANGE if not dark else "#E8AC82")
    txt(M+35, 488, s, 19, "Medium", WHITE if dark else INK)

def small_caption(x, y, title, body, width=250):
    txt(x, y, title, 22, "DisplayBold")
    para(x, y+36, body, width, 18, 24, color=MUTED)

# 01 / COVER
CURRENT = 1
PAGES.append({"page": 1, "section": "START", "title": "Graph Engineering: The Visual Guide"})
rect(0, 0, W, H, BG)
picture("network-sculpture", 360, 0, 600)
rect(0, 0, 360, H, BG)
label(48, 48, "THE VISUAL GUIDE", ORANGE, 12)
txt(46, 118, "Graph", 76, "DisplayBold")
txt(47, 222, "Engineering", 50, "DisplayBold")
para(50, 312, "Build agents that\nwork together.", 300, 31, 37, "Serif")
para(50, 401, "One idea per page.\nSix patterns you can use.", 350, 20, 29, color=MUTED)
line(48, 505, 312, 505)
label(48, 524, "UNDERSTAND 02", MUTED, 10)
label(210, 524, "BUILD 07", MUTED, 10)
label(48, 546, "OPERATE 16", MUTED, 10)
label(210, 546, "START 20", MUTED, 10)
c.bookmarkPage("page-1")
c.addOutlineEntry(PAGES[-1]["title"], "page-1", level=0)
for y, x1, x2, dest in [(524,48,174,2),(524,210,312,7),(546,48,174,16),(546,210,312,20)]:
    c.linkRect("", f"page-{dest}", (x1,H-y-18,x2,H-y+2), relative=0, thickness=0)
end()

# 02 / MENTAL MODEL
start(2, "UNDERSTAND", "A loop lives inside the graph.")
para(48, 148, "An agent repeats actions.\nA graph coordinates the work.", 360, 28, 37, "Serif")
para(48, 284, "An agent is a model that uses tools to pursue a goal. Its loop is the repeated cycle of acting and checking.", 325, 21, 28)
node(432, 243, 108, "Plan", kind="plain")
node(588, 219, 146, "Agent", h=110, sub="loop inside")
node(783, 243, 128, "Check", kind="plain")
arrow([(540,274),(588,274)])
arrow([(734,274),(783,274)])
arrow([(805,313),(805,394),(661,394),(661,329)], ORANGE)
label(696, 406, "retry if needed", ORANGE, 10)
takeaway("The graph decides who runs next, with what information and rules.")
end()

# 03 / LAYERS
start(3, "UNDERSTAND", "Five things you design.")
steps = [
    ("01","Prompt","The request"),
    ("02","Context","The information"),
    ("03","Harness","Tools and limits"),
    ("04","Loop","Act, check, repeat"),
    ("05","Graph","Connect the work"),
]
for i,(num,title,body) in enumerate(steps):
    x=48+i*176
    y=310-i*25
    rect(x,y,160,135,INK if i==4 else PALE,radius=14)
    label(x+16,y+15,num,LIGHT if i==4 else MUTED)
    txt(x+16,y+47,title,25,"DisplayBold",WHITE if i==4 else INK)
    para(x+16,y+86,body,135,16,20,color=LIGHT if i==4 else MUTED)
    if i<4: arrow([(x+160,y+55),(x+172,y+55),(x+172,y+30),(x+176,y+30)],MUTED,1.5,5)
para(48, 151, "Each layer gives the next one something to build on.", 790, 25, 32, "Serif")
takeaway("A better graph still needs good prompts, useful context and capable nodes.")
end()

# 04 / WHY
start(4, "UNDERSTAND", "Add structure where it helps.")
xs=[48,344,640]
for x in xs: rect(x,181,272,263,WHITE,radius=14)
# Three miniature illustrations, drawn as precise vector geometry.
for y in [225,266,307]:
    arrow([(74,266),(104,266),(104,y),(158,y)],MUTED,1.5,5)
    rect(158,y-13,102,26,PALE,radius=6)
    arrow([(260,y),(282,y),(282,266),(297,266)],MUTED,1.5,5)
circle(408,266,30,INK)
circle(544,266,30,PALE)
arrow([(443,266),(509,266)])
txt(408,251,"A",21,"Medium",WHITE,"center")
txt(544,251,"B",21,"Medium",INK,"center")
for j in range(3):
    rect(692+j*18,220+j*27,126,62,WHITE,INK,8)
circle(799,293,8,ORANGE)
for x,title,body in zip(xs,["Parallel work","Fresh review","Durable state"],[
    "Separate tasks can run together.",
    "A separate check can catch missed errors.",
    "Saved progress survives interruptions.",
]):
    txt(x+22,342,title,25,"DisplayBold")
    para(x+22,383,body,229,18,24,color=MUTED)
takeaway("Start with one useful loop. Add coordination when you can name the benefit.")
end()

# 05 / ANATOMY
start(5, "UNDERSTAND", "Four parts. One system.")
node(173,210,150,"Worker")
node(464,210,150,"Check",kind="plain")
node(755,210,150,"Finish",kind="outline")
arrow([(323,241),(464,241)])
arrow([(614,241),(755,241)])
label(355,212,"edge",ORANGE)
rect(173,313,732,51,PALE,radius=9)
txt(539,324,"SHARED STATE",16,"Mono",INK,"center")
for x in [248,539,830]: line(x,272,x,313,LINE,1.5)
label(48,228,"nodes",ORANGE)
for x,title,body in [
    (48,"Nodes","Agent, code, tool or person."),
    (270,"Edges","Choose what runs next."),
    (492,"State","Remember the facts."),
    (714,"Contracts","Inputs, outputs and limits."),
]:
    txt(x,406,title,25,"DisplayBold")
    para(x,445,body,198,18,23,color=MUTED)
end()

# 06 / WHICH GRAPH
start(6, "UNDERSTAND", "Work graphs and data graphs.")
line(480,179,480,506)
label(48,186,"Execution graph",ORANGE)
para(48,224,"What happens next?",365,31,37,"Serif")
node(48,301,108,"Write",kind="agent")
node(202,301,108,"Review",kind="plain")
node(356,301,76,"Ship",kind="outline",size=18)
arrow([(156,332),(202,332)])
arrow([(310,332),(356,332)])
para(48,414,"Nodes are jobs.\nEdges are handoffs.",370,22,31)
label(528,186,"Knowledge graph",ORANGE)
para(528,224,"How are facts related?",385,31,37,"Serif")
circle(578,333,34,INK)
circle(840,333,34,PALE)
line(613,333,805,333,INK,2)
label(657,307,"owns",MUTED,11)
txt(578,322,"Team",15,"Medium",WHITE,"center")
txt(840,322,"Repo",15,"Medium",INK,"center")
para(528,414,"Nodes are things.\nEdges are relationships.",370,22,31)
end()

# 07 / CONTRACT
start(7, "BUILD", "Give every node a clear job.")
para(48,153,"A contract says what a node may do\nand what it must return.",650,25,33,"Serif")
items=[
    ("01 / JOB","Review one patch."),
    ("02 / INPUT","Patch + requirements."),
    ("03 / OUTPUT","Findings + evidence."),
    ("04 / TOOLS","Read files; run checks."),
    ("05 / LIMITS","Timeout; retry cap; cost cap."),
    ("06 / DONE","Every requirement checked."),
]
for i,(head,body) in enumerate(items):
    col=i%3; row=i//3
    x=48+col*296; y=254+row*123
    line(x,y,x+272,y,LINE)
    label(x,y+16,head,ORANGE)
    para(x,y+46,body,265,21,27)
end()

# 08 / STATE
start(8, "BUILD", "Keep a record the system can read.")
picture("state-layers",48,174,348)
label(444,185,"Typed state = named fields with defined formats",MUTED,10)
rows=[
    ("task","What success means"),
    ("artifact","The current draft or patch"),
    ("findings","Problems + supporting evidence"),
    ("checks","Pass/fail results"),
    ("budget","Time, spend and retries left"),
    ("approval","Pending, approved or denied"),
]
for i,(key,val) in enumerate(rows):
    y=221+i*41
    txt(444,y,key,17,"Mono")
    txt(574,y,val,18,"Body")
    if i<5: line(444,y+34,912,y+34,LINE,.7)
para(444,477,"Give each field one writer or a rule for combining updates.",450,20,26,"Medium")
end()

# Pattern helper.
def pattern(n, number, title, lead, use, caution=None):
    start(n, f"PATTERN {number} / 06", title)
    para(48,169,lead,272,24,31,"Serif")
    label(48,323,"USE WHEN",ORANGE)
    para(48,352,use,266,20,27)
    if caution: takeaway(caution)

# 09 / CHAIN
pattern(9,"01","Chain: work in order.",
        "One result becomes\nthe next step's input.",
        "The sequence is known.")
for x,title,kind in [(364,"Outline","plain"),(563,"Draft","agent"),(762,"Check","plain")]:
    node(x,266,150,title,kind=kind)
arrow([(514,297),(563,297)])
arrow([(713,297),(762,297)])
label(388,353,"step 1")
label(590,353,"step 2")
label(788,353,"step 3")
takeaway("Check each handoff before the next step uses it.")
end()

# 10 / ROUTER
pattern(10,"02","Route: choose the right path.",
        "Classify the request.\nSend it to one path.",
        "Different inputs need different handling.",
        "Give uncertain inputs a fallback path.")
node(368,279,143,"Router",kind="accent")
for y,title in [(181,"Code"),(279,"Docs"),(377,"Fallback")]:
    node(686,y,210,title,kind="plain" if title!="Fallback" else "outline")
    arrow([(511,310),(596,310),(596,y+31),(686,y+31)])
end()

# 11 / PARALLEL
start(11,"PATTERN 03 / 06","Parallelize: split, then join.",dark=True)
picture("parallel-paths",48,166,356)
para(454,168,"Independent tasks can run together.",415,29,37,"Serif",WHITE)
for y,title in [(270,"Check A"),(344,"Check B")]:
    node(518,y,148,title,kind="light",h=51,size=19)
    arrow([(461,320),(484,320),(484,y+25.5),(518,y+25.5)],LIGHT,1.8)
    arrow([(666,y+25.5),(715,y+25.5),(715,320),(758,320)],LIGHT,1.8)
node(758,294,142,"Combine",kind="light",h=52,size=19)
para(454,427,"Define what the join does when a branch fails.",431,21,28,color=LIGHT)
end()

# 12 / ORCHESTRATOR
pattern(12,"04","Delegate: let the task shape the team.",
        "A lead agent creates jobs, then combines the results.",
        "Subtasks emerge as the work unfolds.",
        "Give workers separate jobs and a shared spending limit.")
node(365,277,140,"Lead")
for y,title in [(187,"Worker A"),(277,"Worker B"),(367,"Worker C")]:
    node(578,y,142,title,h=57,kind="plain",size=18)
    arrow([(505,308),(541,308),(541,y+28.5),(578,y+28.5)])
    arrow([(720,y+28.5),(755,y+28.5),(755,308),(790,308)])
node(790,277,122,"Combine",kind="outline",size=18)
end()

# 13 / EVALUATOR
pattern(13,"05","Review: improve with evidence.",
        "A reviewer checks the result and returns specific failures.",
        "Quality has a clear test or scoring rule.",
        "Fresh context helps. Tests and different methods add stronger evidence.")
node(368,258,150,"Create")
node(580,258,150,"Review",kind="plain")
node(794,258,118,"Done",kind="outline")
arrow([(518,289),(580,289)])
arrow([(730,289),(794,289)])
label(746,260,"pass",MUTED,9)
arrow([(654,320),(654,394),(443,394),(443,320)],ORANGE)
label(447,408,"fail + evidence; bounded retries",ORANGE,10)
end()

# 14 / GATE
start(14,"PATTERN 06 / 06","Gate: pause before the action.")
picture("approval-gate",530,165,382)
para(48,169,"A proposal becomes an action only after the required checks.",413,32,39,"Serif")
para(48,308,"Use code for fixed rules.\nUse a person when judgment or authorization is required.",395,23,31)
node(48,445,118,"Propose",h=56,size=18)
node(222,445,104,"Gate",h=56,size=18,kind="accent")
node(382,445,98,"Act",h=56,size=18,kind="outline")
arrow([(166,473),(222,473)])
arrow([(326,473),(382,473)])
end()

# 15 / WORKED EXAMPLE
start(15,"BUILD / WORKED EXAMPLE","One feature. A small, useful graph.",
      "Each reviewer checks the same patch in a separate context.")
node(48,269,100,"Plan",size=19)
node(192,269,110,"Build",size=19)
for y,title in [(194,"Logic"),(278,"Tests"),(362,"Style")]:
    node(374,y,130,title,h=51,kind="plain",size=19)
    arrow([(302,300),(339,300),(339,y+25.5),(374,y+25.5)])
    arrow([(504,y+25.5),(543,y+25.5),(543,300),(582,300)])
node(582,269,112,"Check",kind="accent",size=19)
node(738,269,174,"Approve + act",kind="outline",size=18)
arrow([(148,300),(192,300)])
arrow([(694,300),(738,300)])
label(702,274,"pass",MUTED,9)
arrow([(638,331),(638,443),(247,443),(247,331)],ORANGE)
label(312,454,"fail: return findings to the builder",ORANGE,10)
para(48,504,"Pass = required tests succeed and blocking findings are resolved.",850,20,26,"Medium")
end()

# 16 / RECOVERY
start(16,"OPERATE","Save progress. Resume deliberately.")
para(48,149,"A checkpoint is a saved snapshot of the run.",825,27,34,"Serif")
for x,num,title in [(48,"01","Plan saved"),(270,"02","Draft saved"),(492,"03","Check fails"),(714,"04","Resume")]:
    rect(x,241,198,135,WHITE,radius=12)
    circle(x+30,270,8,ORANGE if num=="03" else INK)
    label(x+52,260,num,MUTED,13)
    txt(x+20,312,title,24,"DisplayBold")
    if num!="04": arrow([(x+198,308),(x+222,308)],MUTED,1.6,6)
arrow([(591,376),(591,420),(369,420),(369,376)],ORANGE)
label(401,432,"retry from saved state",ORANGE)
takeaway("Restoring state does not undo a sent message, payment or deployment.")
end()

# 17 / FAILURE
start(17,"OPERATE","Make the failure path explicit.")
rows=[
    ("A retry loop never ends.","Enforce time and retry limits."),
    ("Two nodes overwrite a field.","Assign one writer, or combine writes."),
    ("An external action repeats.","Use a stable action ID and deduplicate."),
    ("A route is uncertain.","Send it to a defined fallback."),
]
label(48,173,"WHEN THIS HAPPENS",MUTED)
label(512,173,"BUILD THIS IN",ORANGE)
for i,(problem,fix) in enumerate(rows):
    y=216+i*75
    line(48,y-13,912,y-13,LINE)
    txt(48,y,problem,22,"Medium")
    arrow([(463,y+16),(486,y+16)],ORANGE,1.5,5)
    para(512,y,fix,400,22,28)
end()

# 18 / COST
start(18,"OPERATE","Less waiting can mean more spending.")
para(48,145,"Illustration: three independent jobs, two minutes each.",850,23,30,"Serif")
label(48,220,"SEQUENTIAL",MUTED)
for x,tag in [(246,"A"),(414,"B"),(582,"C")]:
    rect(x,208,152,45,PALE,radius=8)
    txt(x+76,215,tag,20,"Medium",INK,"center")
txt(774,216,"6 min",24,"DisplayBold")
label(48,319,"PARALLEL",MUTED)
for y,tag in [(281,"A"),(331,"B"),(381,"C")]:
    rect(246,y,152,41,INK,radius=8)
    txt(322,y+5,tag,20,"Medium",WHITE,"center")
txt(450,303,"~2 min + coordination",28,"DisplayBold")
para(450,351,"Still three jobs. The work did not disappear.",403,21,27,color=MUTED)
takeaway("Set limits for total spend, workers and retries. Measure real runs.")
end()

# 19 / EVALUATION
start(19,"OPERATE","Measure the whole result.")
for x,num,title,body in [
    (48,"01","Quality","Did the output meet the requirements?"),
    (344,"02","Time","How long until a usable result arrived?"),
    (640,"03","Cost","What did each successful task cost?"),
]:
    txt(x,185,num,65,"Display",ORANGE)
    txt(x,279,title,34,"DisplayBold")
    para(x,335,body,252,23,30)
para(48,431,"A trace records the steps a run took.",850,19,24,color=MUTED)
takeaway("Compare with a simple baseline. Repeat trials; inspect failures and traces.")
end()

# 20 / CHOICE
start(20,"START SMALL","Choose the shape of the work.")
rect(48,181,414,282,PALE,radius=15)
rect(498,181,414,282,INK,radius=15)
label(74,207,"KEEP ONE LOOP",MUTED)
txt(74,243,"One owner.",34,"DisplayBold")
para(74,308,"The path is uncertain.\nSteps depend closely on each other.\nA short run is cheap to repeat.",350,21,33)
label(524,207,"ADD GRAPH STRUCTURE",LIGHT)
txt(524,243,"Clear handoffs.",34,"DisplayBold",WHITE)
para(524,308,"Independent jobs can run together.\nRequired checks must happen.\nLong runs need pause and resume.",350,21,33,color=WHITE)
para(48,493,"Use the simplest structure that reliably completes the task.",850,23,29,"Medium")
end()

# 21 / MANUAL PROTOTYPE
start(21,"START SMALL","Try the graph before you automate it.")
steps=[
    ("Name the output.","Write one sentence that defines success."),
    ("List the jobs.","Separate work that needs different inputs or checks."),
    ("Draw the handoffs.","Pass a clear artifact from one job to the next."),
    ("Run it by hand.","Use a fresh chat or separate context for each role."),
    ("Compare results.","Keep the structure only if it earns its overhead."),
]
for i,(title,body) in enumerate(steps):
    y=171+i*68
    circle(68,y+22,20,INK)
    txt(68,y+8,str(i+1),18,"Mono",WHITE,"center")
    txt(109,y+6,title,22,"DisplayBold")
    txt(373,y+8,body,20,"Body",MUTED)
end()

# 22 / FIRST IMPLEMENTATION
start(22,"START SMALL","Build the smallest useful version.",dark=True)
para(48,158,"One worker. One independent check.\nA bounded path back.",720,31,39,"Serif",WHITE)
node(144,300,180,"Worker",kind="light",h=70,size=25)
node(428,300,180,"Check",kind="light",h=70,size=25)
node(712,300,140,"Done",kind="light",h=70,size=25)
arrow([(324,335),(428,335)],LIGHT)
arrow([(608,335),(712,335)],LIGHT)
label(631,306,"pass",LIGHT,10)
arrow([(518,370),(518,428),(234,428),(234,370)],"#E8AC82")
label(275,441,"fail + evidence",LIGHT)
para(48,486,"Plain functions can be enough. Add a workflow engine when pause/resume or coordination needs it.",850,20,27,color=LIGHT)
end()

# 23 / CHEAT SHEET
start(23,"KEEP HANDY","Six rules worth remembering.")
rules=[
    ("Start simple.","Prove one loop can do useful work."),
    ("Name the handoffs.","Define inputs, outputs and who owns them."),
    ("Separate the checks.","Judge evidence, not the agent's confidence."),
    ("Save useful state.","Plan for crashes, pauses and retries."),
    ("Bound the work.","Limit time, spend, workers and attempts."),
    ("Gate the action.","Enforce required checks before acting."),
]
for i,(title,body) in enumerate(rules):
    col=i%2; row=i//2
    x=48+col*448; y=177+row*110
    label(x,y,f"0{i+1}",ORANGE,15)
    txt(x+49,y-3,title,26,"DisplayBold")
    para(x+49,y+39,body,343,20,26,color=MUTED)
end()

# 24 / OPTIONAL END SOURCES (no sources or cross-references on teaching pages)
start(24,"OPTIONAL / FURTHER READING","Go deeper when you need to.")
sources=[
    ("Patterns","Building effective agents","Anthropic",
     "https://www.anthropic.com/research/building-effective-agents"),
    ("Graph structure","Graph API overview","LangChain documentation",
     "https://docs.langchain.com/oss/python/langgraph/graph-api"),
    ("Saved state","Persistence","LangChain documentation",
     "https://docs.langchain.com/oss/python/langgraph/persistence"),
    ("Production lessons","How we built our multi-agent research system","Anthropic",
     "https://www.anthropic.com/research/multi-agent-research-system"),
]
for i,(topic,title,publisher,url) in enumerate(sources):
    y=167+i*79
    label(48,y+3,topic,ORANGE,10)
    txt(251,y,title,22,"DisplayBold")
    txt(251,y+34,publisher,16,"Body",MUTED)
    line(48,y+68,912,y+68,LINE)
    c.linkURL(url,(251,H-y-60,912,H-y+3),relative=0,thickness=0)
para(48,501,"Everything needed to use this guide is on the preceding pages.",840,21,27,"Serif",MUTED)
end()
c.save()

# Preserve vectors and searchable text; remove default author metadata.
doc=fitz.open(TMP / "unoptimized.pdf")
doc.set_metadata({
    "title":"Graph Engineering | The Visual Guide",
    "author":"",
    "subject":"A standalone guide to agent loops, graphs and practical patterns.",
    "creator":"Graph Engineering",
    "producer":"ReportLab / PyMuPDF",
    "keywords":"agents, graph engineering, workflows",
})
doc.save(OUT,garbage=4,deflate=True)
doc.close()

# Record useful validation, without claiming PDF/UA or tagged reading order.
doc=fitz.open(OUT)
orig=fitz.open(BASE / "graph-engineering-field-guide.pdf")
def words(s): return len(re.findall(r"\b[\w'-]+\b",s))
counts=[words(page.get_text()) for page in doc]
old_counts=[words(page.get_text()) for page in orig]
issues=[]
for pn,x,y,w,h,s in TEXT_BOXES:
    if x < -0.1 or x+w > W+.1 or y<0 or y+h>H:
        issues.append({"page":pn,"text":s,"bounds":[x,y,w,h]})
assert not issues, issues
assert len(doc)==24
assert all(p.rect.width==W and p.rect.height==H for p in doc)
assert all(count>15 for count in counts)
assert all(len(p.get_links())==0 for p in list(doc)[1:23]), "Teaching pages must not contain references."
report={
    "file":str(OUT),
    "pages":len(doc),
    "page_size_points":[W,H],
    "words_per_page":counts,
    "average_words_per_page":round(mean(counts),1),
    "original_average_words_per_page":round(mean(old_counts),1),
    "reduction_in_words_per_page_percent":round((1-mean(counts)/mean(old_counts))*100,1),
    "original_sha256":hashlib.sha256((BASE / "graph-engineering-field-guide.pdf").read_bytes()).hexdigest(),
    "images":sorted(p.name for p in ASSETS.glob("*.png")),
    "text_bounds_issues":issues,
    "external_links_only_on_final_page":True,
    "outline_entries":len(doc.get_toc()),
    "scope":"Structural and visual checks; not a PDF/UA or PDF/A certification.",
}
(BASE/"visual-source/validation.json").write_text(json.dumps(report,indent=2)+"\n")
(BASE/"visual-source/page-map.json").write_text(json.dumps(PAGES,indent=2)+"\n")
(TMP/"extracted-text.txt").write_text("\n\n".join(p.get_text() for p in doc))
print(json.dumps(report,indent=2))
