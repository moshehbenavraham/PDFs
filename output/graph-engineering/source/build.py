#!/usr/bin/env python3
"""Build "Graph Engineering: a field guide for agentic coders".

Generates source/guide.html (all text, layout and inline SVG diagrams) and
prints it to ../graph-engineering-field-guide.pdf with the cached Chromium.

Run:  /home/aiwithapex/.venvs/pdf/bin/python source/build.py
"""
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
HTML = HERE / "guide.html"
PDF = PROJECT / "graph-engineering-field-guide.pdf"
CHROME = "/home/aiwithapex/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"

PARTS = ["Start here", "From loops", "The graph", "Build one", "Reality check", "Your move"]

# ───────────────────────────── SVG helpers ─────────────────────────────

def svg(w, h, inner, cls="", style=""):
    return (f'<svg class="dg {cls}" viewBox="0 0 {w} {h}" width="{w}" height="{h}" text-anchor="middle" '
            f'style="{style}" xmlns="http://www.w3.org/2000/svg">{inner}</svg>')

def node(x, y, w, h, label, k="agent", sub=None, loop=False, fs=13):
    cy = y + h / 2
    o = f'<g class="n {k}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>'
    if sub:
        o += f'<text x="{x+w/2}" y="{cy-2}" font-size="{fs}">{label}</text>'
        o += f'<text class="sub" x="{x+w/2}" y="{cy+13}">{sub}</text>'
    else:
        o += f'<text x="{x+w/2}" y="{cy+fs*0.35}" font-size="{fs}">{label}</text>'
    if loop:
        o += loopglyph(x + w - 13, y + 13)
    return o + "</g>"

def loopglyph(cx, cy, r=5.5, cls="lg"):
    # small circular arrow marking "an agent loop runs in here"
    return (f'<path class="{cls}" d="M{cx+r} {cy} A{r} {r} 0 1 1 {cx+r*0.3:.1f} {cy-r*0.95:.1f}" '
            f'marker-end="url(#ahs)"/>')

def pill(x, y, w, h, label, fs=12.5, k="io"):
    return (f'<g class="n {k}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}"/>'
            f'<text x="{x+w/2}" y="{y+h/2+fs*0.35}" font-size="{fs}">{label}</text></g>')

def diamond(cx, cy, w, h, label, k="code", sub=None, fs=12.5):
    pts = f"{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}"
    o = f'<g class="n {k}"><polygon points="{pts}"/>'
    if sub:
        o += f'<text x="{cx}" y="{cy-1}" font-size="{fs}">{label}</text><text class="sub" x="{cx}" y="{cy+13}">{sub}</text>'
    else:
        o += f'<text x="{cx}" y="{cy+fs*0.35}" font-size="{fs}">{label}</text>'
    return o + "</g>"

def edge(d, cls="", label=None, lx=0, ly=0, anchor="middle"):
    o = f'<path class="e {cls}" d="{d}" marker-end="url(#ah)"/>'
    if label:
        o += f'<text class="el {cls}" x="{lx}" y="{ly}" text-anchor="{anchor}">{label}</text>'
    return o

def ln(x1, y1, x2, y2, cls="", **kw):
    return edge(f"M{x1} {y1} L{x2} {y2}", cls, **kw)

def txt(x, y, s, cls="el", anchor="middle"):
    return f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{s}</text>'

# ───────────────────────────── page helpers ─────────────────────────────

pages = []

def page(part, kicker, title, body, lede=None, cls="", fs=1.12):
    pages.append(dict(part=part, kicker=kicker, title=title, body=body, lede=lede, cls=cls, fs=fs))

def card(title, text, k="", tag=None, extra=""):
    t = f'<div class="tag">{tag}</div>' if tag else ""
    return f'<div class="card {k}">{t}<h3>{title}</h3><p>{text}</p>{extra}</div>'

def chips(items, k=""):
    return '<div class="chips">' + "".join(f'<span class="chip {k}">{i}</span>' for i in items) + "</div>"

LEGEND = ('<div class="legend"><span><i class="sw agent"></i>agent (loop inside)</span>'
          '<span><i class="sw code"></i>plain code</span>'
          '<span><i class="sw verify"></i>verifier</span>'
          '<span><i class="sw human"></i>human gate</span>'
          '<span><i class="sw retry"></i>retry edge</span></div>')

# ═════════════════════════════ PAGE 1 · COVER ═════════════════════════════

def cover_art():
    o = ""
    # faint grid of dots
    for gx in range(0, 600, 40):
        for gy in range(0, 600, 40):
            o += f'<circle cx="{gx+20}" cy="{gy+20}" r="1.1" fill="#2A2F3D"/>'
    E = lambda d, c="#7C83FF", dash="": f'<path d="{d}" fill="none" stroke="{c}" stroke-width="1.8" {dash} marker-end="url(#ah)"/>'
    def box(x, y, w, h, label, c, fill):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{c}" stroke-width="1.8"/>'
                f'<text x="{x+w/2}" y="{y+h/2+4.5}" text-anchor="middle" font-family="IBM Plex Mono" font-size="12.5" '
                f'font-weight="500" style="fill:#E9EAF2" letter-spacing=".04em">{label}</text>')
    # edges
    o += E("M300 62 L300 98")
    o += E("M300 150 L300 186")
    o += E("M262 238 C 200 262, 120 262, 108 300")
    o += E("M300 238 L300 300")
    o += E("M338 238 C 400 262, 480 262, 492 300")
    o += E("M108 352 C 120 392, 200 392, 256 408", "#34D399")
    o += E("M300 352 L300 398", "#34D399")
    o += E("M492 352 C 480 392, 400 392, 344 408", "#34D399")
    o += E("M300 478 L300 506", "#FBBF24")
    # retry edge
    o += E("M236 442 C 60 442, 20 300, 60 230 C 80 196, 150 212, 226 212", "#FF8A4C", 'stroke-dasharray="6 5"')
    o += '<text x="34" y="330" font-family="IBM Plex Mono" font-size="11" style="fill:#FF8A4C" transform="rotate(-90 34 330)" text-anchor="middle" letter-spacing=".08em">RETRY</text>'
    # nodes
    o += '<rect x="250" y="26" width="100" height="36" rx="18" fill="#E9EAF2"/><text x="300" y="49" text-anchor="middle" font-family="IBM Plex Mono" font-size="12.5" font-weight="600" style="fill:#0F1117" letter-spacing=".06em">TASK</text>'
    o += box(232, 100, 136, 50, "PLAN", "#7C83FF", "#1B1E3A")
    o += box(232, 188, 136, 50, "BUILD", "#7C83FF", "#1B1E3A")
    # loop ring on BUILD
    o += '<path d="M368 200 C 420 180, 430 246, 372 228" fill="none" stroke="#FF8A4C" stroke-width="1.8" marker-end="url(#ah)"/>'
    o += box(48, 302, 120, 50, "SECURITY", "#34D399", "#0F2A23")
    o += box(240, 302, 120, 50, "LOGIC", "#34D399", "#0F2A23")
    o += box(432, 302, 120, 50, "STYLE", "#34D399", "#0F2A23")
    o += '<polygon points="300,400 366,440 300,480 234,440" fill="#1A1D27" stroke="#C9CCDA" stroke-width="1.8"/><text x="300" y="444.5" text-anchor="middle" font-family="IBM Plex Mono" font-size="12.5" font-weight="500" style="fill:#E9EAF2" letter-spacing=".04em">GATE</text>'
    o += box(232, 508, 136, 50, "HUMAN OK", "#FBBF24", "#2E2408")
    return f'<svg viewBox="0 0 600 580" width="560" height="541" xmlns="http://www.w3.org/2000/svg">{o}</svg>'

pages.append(dict(raw=f"""
<section class="page cover">
  <div class="cv-l">
    <div class="kicker">A field guide for agentic coders and vibe coders</div>
    <h1>Graph<br>Engineering</h1>
    <p class="cv-sub">What comes after the loop: how to wire agents, checks and people into a system you can actually trust.</p>
    <div class="cv-meta">
      <span>28 pages</span><span>6 patterns</span><span>1 worked example</span><span>Everything you need is on the page</span>
    </div>
  </div>
  <div class="cv-r">{cover_art()}</div>
</section>"""))

# ═════════════════════════════ PAGE 2 · 60 seconds ═════════════════════════════

page(0, "The 60-second version", "If you only read one page, read this one.", f"""
<div class="cols" style="grid-template-columns: 0.92fr 1.08fr; gap:44px; height:100%">
  <div class="stack" style="justify-content:space-between">
    <blockquote class="big">A <b class="c-loop">loop</b> asks: should this one agent keep going?<br><br>A <b class="c-graph">graph</b> asks: who runs next, with what state, under which rules?</blockquote>
    <div class="note"><b>Who this is for.</b> You already build with a coding agent that runs tools in a loop until the tests pass. This guide shows what changes when one loop stops being enough, and how to tell when that has happened.</div>
  </div>
  <ol class="takeaways">
    <li><b>Loops are not dead.</b> A loop is the smallest possible graph, and the nodes of a graph run loops inside them. Same system, different zoom level.</li>
    <li><b>The thing you design changes.</b> Less prompt, more topology: nodes that do work, edges that decide what runs next, shared state, and contracts.</li>
    <li><b>Graphs pay off when you know something about the shape of the work:</b> steps that can run in parallel, checks that must be independent, gates that must never be skipped, progress that must survive a crash.</li>
    <li><b>They are not free.</b> Anthropic's multi-agent research system scored 90.2% higher than its single agent on an internal evaluation, and used about 15 times the tokens of a normal chat.</li>
    <li><b>Start with one good loop.</b> Add graph structure only when your traces show the loop hiding parallel work, self-grading, or fragile state.</li>
  </ol>
</div>
""")

# ═════════════════════════════ PAGE 3 · five layers ═════════════════════════════

rows = [
    ("Prompt", "2023 to 2024", "The wording of one request", "Phrasing changes the answer; hallucination", "l1"),
    ("Context", "2024 to mid 2025", "What goes into the window: retrieved docs, tool schemas, history", "Missing facts, diluted or conflicting context", "l2"),
    ("Harness", "2025 to early 2026", "Tools, sandbox, permissions, storage. <span class='mono'>Agent = Model + Harness</span>", "Wrong tool picked; permissions too broad", "l3"),
    ("Loop", "named June 2026", "One agent that keeps going: observe, decide, act, verify", "Runaway retries, context bloat, self-grading", "l4"),
    ("Graph", "named July to Aug 2026", "Many nodes and the rules that connect them", "Orchestration overhead, token burn, premature complexity", "l5"),
]
tr = "".join(f'<tr class="{c}"><td><span class="lname">{n}</span><span class="lera">{e}</span></td><td>{d}</td><td>{f}</td></tr>' for n, e, d, f, c in rows)
page(1, "Part 1 · From loops to graphs", "Five layers, each one wrapping the last.", f"""
<div class="cols" style="grid-template-columns: 372px 1fr; gap:40px; align-items:center; height:100%">
  <div class="nest n5"><span>Graph</span>
    <div class="nest n4"><span>Loop</span>
      <div class="nest n3"><span>Harness</span>
        <div class="nest n2"><span>Context</span>
          <div class="nest n1"><span>Prompt</span></div>
        </div>
      </div>
    </div>
  </div>
  <div>
    <table class="tbl layers">
      <thead><tr><th style="width:24%">Layer</th><th style="width:40%">What you design</th><th>How it typically fails</th></tr></thead>
      <tbody>{tr}</tbody>
    </table>
    <div class="note" style="margin-top:18px"><b>Nothing gets replaced.</b> Prompts and context shape a single model call. The harness gives the model hands and memory. The loop makes one agent self-correcting. The graph coordinates several loops, plain code and human checkpoints over shared state.</div>
  </div>
</div>
""", lede="The leverage in AI engineering keeps moving outward. Each new layer contains the ones before it.")

# ═════════════════════════════ PAGE 4 · timeline ═════════════════════════════

eras = [
    ("2017 to 2022", "Make the model good", "Transformer, InstructGPT and RLHF", "Plain language becomes a workable control interface."),
    ("Late 2022 to 2023", "Let it act", "ReAct, Toolformer, function calling", "Model output turns from prose into structured actions."),
    ("2023", "Let it retry and search", "Reflexion, Self-Refine, Tree of Thoughts, Graph of Thoughts, LATS", "One pass gives way to critique, branching and backtracking."),
    ("2023 to early 2024", "Give it teammates", "CAMEL, MetaGPT, AutoGen, LangGraph (Jan 2024), GPTSwarm", "Roles, procedures and explicit cyclic state graphs."),
    ("Late 2024 to 2025", "Make it production", "Anthropic workflow patterns, MCP, OpenAI Agents SDK, Google ADK and A2A", "Standard protocols, tracing, checkpoints, orchestrator and workers."),
    ("2026", "Engineer the topology", "Google ADK 2.0 (May), loop engineering (June), graph engineering (July), Feng et al. survey (Aug)", "Whole agents become typed nodes in versioned, recoverable systems."),
]
tl = "".join(f'<div class="era e{i}"><div class="dot"></div><div class="when">{w}</div><h3>{t}</h3><p class="works">{k}</p><p>{b}</p></div>' for i, (w, t, k, b) in enumerate(eras))
page(1, "Part 1 · From loops to graphs", "The name is new. The architecture is not.", f"""
<div class="timeline">{tl}</div>
<div class="cols" style="grid-template-columns:1fr 1fr; gap:16px; margin-top:20px">
  <div class="note"><b>How the name arrived.</b> Around 18 to 19 July 2026, OpenClaw creator Peter Steinberger asked whether the field was still talking about loops or had moved on to graphs. The post drew over three million views. In August, Feng and 36 co-authors published the survey that framed graph engineering as the route from individual intelligence to system intelligence.</div>
  <div class="note"><b>Why it is more than a label.</b> LangGraph launched in January 2024 specifically to build cyclic graphs for agents, so the idea is years old. What changed is that a node can now hold an entire capable agent, not just one function or one model call. Three things lined up: capable nodes, structured interfaces, and a runtime you can observe.</div>
</div>
""", lede="Each era solved the bottleneck that the previous one exposed.")

# ═════════════════════════════ PAGE 5 · loop refresher ═════════════════════════════

loop_svg = svg(470, 290,
    node(40, 30, 130, 52, "Observe", "loopn") + node(300, 30, 130, 52, "Decide", "loopn") +
    node(300, 170, 130, 52, "Act", "loopn", sub="call a tool") + node(40, 170, 130, 52, "Verify", "loopn", sub="tests, checks") +
    ln(170, 56, 298, 56, "lp") + ln(365, 82, 365, 168, "lp") + ln(300, 196, 172, 196, "lp") +
    ln(105, 170, 105, 84, "lp", label="not yet", lx=68, ly=131) +
    edge("M105 222 L105 262 L196 262", "", label="pass", lx=128, ly=254) + pill(198, 246, 74, 32, "done") +
    txt(235, 122, "one agent", "ctr") + txt(235, 140, "one growing transcript", "ctr2"))
page(1, "Part 1 · From loops to graphs", "First, the loop you already know.", f"""
<div class="cols" style="grid-template-columns: 470px 1fr; gap:44px">
  <div>{loop_svg}</div>
  <div class="stack" style="gap:14px">
    <blockquote class="mid">&ldquo;Tools in a loop toward a goal.&rdquo;<cite>Simon Willison's definition of an agent</cite></blockquote>
    <p class="body">The agent looks at the current state, picks an action, sees the result, and repeats until a stop condition is true. It works because it is simple: the model finds its own path, so you do not have to write every path in advance.</p>
    <div><div class="lbl">Stop conditions</div>{chips(["goal_reached", "verification_passed", "budget_exhausted", "human_stop", "unrecoverable_failure"], "mono")}</div>
    <div><div class="lbl">A production coding loop has six parts (Addy Osmani)</div>{chips(["automations", "worktrees", "skills", "MCP connectors", "subagents", "external state"])}</div>
  </div>
</div>
<div class="lbl" style="margin-top:16px">Loop engineering is really four loops, nested (LangChain, June 2026)</div>
<div class="grid g4">
  {card("Agent loop", "The model calls tools again and again until it decides to stop.", "loop", "1 · inner")}
  {card("Verification loop", "Tests or a grader reject bad output and feed the errors back in.", "loop", "2")}
  {card("Event-driven loop", "Schedules, webhooks and alerts keep starting new runs.", "loop", "3")}
  {card("Hill-climbing loop", "Traces and eval results are mined to improve prompts, tools and memory.", "loop", "4 · outer")}
</div>
""")

# ═════════════════════════════ PAGE 6 · three walls ═════════════════════════════

w1 = ""
names = ["Plan", "Code", "Security", "Logic", "Style", "Fix"]
for i, nme in enumerate(names):
    k = "verify" if i in (2, 3, 4) else "loopn"
    w1 += node(1 + i * 56, 34, 48, 30, nme, k, fs=9.2)
    if i < 5:
        w1 += ln(49 + i * 56, 49, 56 + i * 56, 49, "thin")
w1 += '<path class="brace" d="M113 74 L113 82 L273 82 L273 74"/>' + txt(193, 98, "these three could run at once", "el good")
w1 = svg(330, 108, w1)

w2 = svg(330, 108,
    node(105, 34, 120, 44, "Same agent", "loopn") +
    edge("M105 46 C 40 20, 40 92, 103 68", "lp", label="writes", lx=38, ly=24) +
    edge("M225 68 C 290 92, 290 20, 227 46", "lp", label="grades", lx=292, ly=24) +
    txt(165, 100, "same context, same blind spots", "el bad"))

w3 = ""
for i in range(60):
    c = "#E8590C" if i == 47 else ("#D9D3C7" if i < 47 else "#EFEBE3")
    w3 += f'<rect x="{6 + i*5.3:.1f}" y="38" width="3.6" height="{30 if i != 47 else 40}" rx="1.5" fill="{c}" transform="translate(0 {0 if i != 47 else -5})"/>'
w3 += txt(6 + 47 * 5.3 + 2, 24, "bad step 48", "el bad") + txt(6, 86, "step 1", "el", "start") + txt(324, 86, "step 60", "el", "end") + txt(165, 105, "no clean way to roll back just the damage", "el bad")
w3 = svg(330, 108, w3)

page(1, "Part 1 · From loops to graphs", "Where a single loop runs out of road.", f"""
<div class="grid g3">
  <div class="card wall"><div class="tag">Wall 1</div><h3>Everything happens in a line</h3>{w1}<p>Log analysis, bug reproduction and code inspection could run side by side. A single loop does them one after another. Latency multiplies, and an early mistake flows quietly downstream.</p></div>
  <div class="card wall"><div class="tag">Wall 2</div><h3>It grades its own homework</h3>{w2}<p>Giving one loop several personas does not help. Writing and critiquing in the same context window means the agent shares blind spots with itself and mistakes confidence for evidence.</p></div>
  <div class="card wall"><div class="tag">Wall 3</div><h3>A transcript is not a database</h3>{w3}<p>State lives in the chat history. A small error early in a long run cannot be isolated or undone without throwing away the whole run.</p></div>
</div>
<div class="lbl" style="margin-top:18px">Symptoms you have probably seen</div>
<div class="grid g3">
  <div class="sym"><b>The &ldquo;Ralph loop&rdquo;</b>Re-prompt against the goal until it stumbles into a pass or hits the step limit.</div>
  <div class="sym"><b>Context bloat</b>Every call re-reads the full history, including stale errors and failed attempts. Cost and latency climb as the run gets longer.</div>
  <div class="sym"><b>Going in circles</b>In the original ReAct error analysis, 47% of failures were the agent repeating the same thought and action; another 23% came from empty search results it could not recover from.</div>
</div>
""", lede="Feng et al. (August 2026) name three structural walls. More turns and a bigger model do not remove them.")

# ═════════════════════════════ PAGE 7 · three debts ═════════════════════════════

page(1, "Part 1 · From loops to graphs", "Three debts a fast loop quietly runs up.", f"""
<div class="grid g3 tall">
  <div class="card debt"><div class="bignum">1</div><h3>Intent debt</h3>
    <p>Whenever project context is not written down, the loop does not stop and ask. It fills the gap with a confident guess, and guesses differently on the next cycle.</p>
    <div class="tell"><span>The tell</span>The same architectural decision gets re-made, differently, every run.</div>
    <div class="fix"><span>Pay it down</span>Write the conventions, build steps and verification rules into files the agent always reads, such as SKILL.md.</div></div>
  <div class="card debt"><div class="bignum">2</div><h3>Comprehension debt</h3>
    <p>The loop generates and ships code faster than people can read the diffs. The codebase grows while the team's mental model falls behind.</p>
    <div class="tell"><span>The tell</span>Nobody can explain how a merged feature works without asking the agent.</div>
    <div class="fix"><span>Pay it down</span>Keep external state that humans read too: trackers, decision notes, milestones that persist across runs.</div></div>
  <div class="card debt"><div class="bignum">3</div><h3>Cognitive surrender</h3>
    <p>Green test suites lull engineers into approving whatever clears the checks. Independent judgement about quality and architecture stops forming.</p>
    <div class="tell"><span>The tell</span>Reviews take seconds. &ldquo;Tests pass&rdquo; has become the whole review.</div>
    <div class="fix"><span>Pay it down</span>Put a real human gate where a mistake would be expensive, and treat it as a decision, not a rubber stamp.</div></div>
</div>
<div class="note" style="margin-top:16px"><b>Why this belongs in a guide about graphs.</b> Martin Fowler's line between agentic engineering and vibe coding is that the human stays responsible for understanding the system. Graph structure will not pay these debts for you. It does give you named places to pay them: contracts, shared state, and gates.</div>
""", lede="Addy Osmani's warning to anyone running autonomous coding loops at scale.")

# ═════════════════════════════ PAGE 8 · G = (V,E,S,C) ═════════════════════════════

g = (pill(0, 84, 64, 30, "task") + ln(64, 99, 82, 99) +
     node(84, 76, 96, 46, "Planner", "agent", loop=True) +
     edge("M180 90 C 200 70, 204 52, 222 52") + edge("M180 108 C 200 128, 204 146, 222 146") +
     node(224, 30, 100, 44, "Worker A", "agent", loop=True) + node(224, 124, 100, 44, "Worker B", "agent", loop=True) +
     edge("M324 52 C 344 52, 344 86, 362 92") + edge("M324 146 C 344 146, 344 112, 362 106") +
     node(364, 76, 92, 46, "Verifier", "verify") + ln(456, 99, 476, 99) +
     diamond(512, 99, 72, 56, "Gate", "code") +
     edge("M512 127 L512 196 L132 196 L132 124", "retry", label="fail: retry", lx=340, ly=190) +
     # state bar
     '<rect class="statebar" x="0" y="232" width="548" height="44" rx="10"/>' +
     txt(274, 250, "SHARED STATE", "sblbl") + txt(274, 267, "plan · patch · findings · budget · checkpoints", "sbtxt") +
     "".join(f'<path class="dot" d="M{x} {y} L{x} 232"/>' for x, y in [(112, 200), (274, 170), (410, 200)]) +
     edge("M548 99 L560 99", "") )
g = svg(560, 280, g.replace('M548 99 L560 99', 'M548 99 L559 99'))

page(2, "Part 2 · The graph", "A graph has four parts: nodes, edges, state, contracts.", f"""
<div class="cols" style="grid-template-columns: 280px 560px 280px; gap:16px; align-items:stretch">
  <div class="stack" style="gap:14px">
    <div class="card def v"><div class="letter">V</div><h3>Nodes do the work</h3><p>A plain function, one model call, a tool, a human, or a whole agent running its own loop. Each node has one job.</p></div>
    <div class="card def e"><div class="letter">E</div><h3>Edges decide what runs next</h3><p>Fixed handoffs, conditional branches, fan-out and fan-in, retry cycles. This is where you draw the line between code that must be deterministic and judgement you leave to the model.</p></div>
  </div>
  <div class="stack" style="justify-content:center; align-items:center; gap:10px">
    <div class="formula">G = (<b class="cv">V</b>, <b class="ce">E</b>, <b class="cs">S</b>, <b class="cc">C</b>)</div>
    {g}
    {LEGEND}
  </div>
  <div class="stack" style="gap:14px">
    <div class="card def s"><div class="letter">S</div><h3>State is explicit</h3><p>A typed, versioned record that nodes read from and write to. It replaces &ldquo;whatever is in the chat history&rdquo; and can be checkpointed, replayed and rolled back.</p></div>
    <div class="card def c"><div class="letter">C</div><h3>Contracts keep it honest</h3><p>Input and output schemas, tool permissions, token and money budgets, retry limits, and what counts as done.</p></div>
  </div>
</div>
<div class="note" style="margin-top:16px"><b>The practical definition (LangGraph):</b> nodes do work, edges determine what runs next, state moves through the graph. Think of it as a state machine in which some of the states happen to be very capable agents.</div>
""")

# ═════════════════════════════ PAGE 9 · zoom levels ═════════════════════════════

z = (  # left: single loop
    txt(110, 22, "ZOOM IN: A LOOP", "zlbl") +
    node(50, 96, 120, 56, "Agent", "loopn") +
    edge("M150 96 C 196 30, 24 30, 70 94", "lp") +
    txt(110, 190, "V = 1,  E = 1", "zmath") + txt(110, 210, "the smallest cyclic graph", "el") +
    '<path class="sep" d="M250 10 L250 250"/>' +
    # middle: graph
    txt(520, 22, "ZOOM OUT: A GRAPH", "zlbl") +
    '<path class="proj" d="M480 100 L800 44"/><path class="proj" d="M480 144 L800 232"/>' +
    node(290, 100, 80, 44, "Plan", "agent") + ln(370, 122, 398, 122) +
    node(400, 100, 80, 44, "Build", "agent hl", loop=True) +
    edge("M480 112 C 500 96, 500 80, 518 76") + edge("M480 132 C 500 148, 500 164, 518 168") +
    node(520, 54, 86, 44, "Review A", "verify") + node(520, 146, 86, 44, "Review B", "verify") +
    edge("M606 76 C 626 80, 626 106, 644 114") + edge("M606 168 C 626 164, 626 138, 644 130") +
    diamond(680, 122, 68, 52, "Gate", "code") +
    edge("M680 148 L680 220 L440 220 L440 146", "retry") +
    # right: inside
    '<rect class="inside" x="800" y="44" width="340" height="188" rx="14"/>' +
    txt(970, 22, "INSIDE ONE NODE: A LOOP AGAIN", "zlbl") +
    node(826, 70, 100, 40, "Observe", "loopn", fs=12) + node(1014, 70, 100, 40, "Decide", "loopn", fs=12) +
    node(1014, 164, 100, 40, "Act", "loopn", fs=12) + node(826, 164, 100, 40, "Verify", "loopn", fs=12) +
    ln(926, 90, 1012, 90, "lp") + ln(1064, 110, 1064, 162, "lp") + ln(1014, 184, 928, 184, "lp") + ln(876, 164, 876, 112, "lp") +
    txt(970, 134, "hundreds of tool calls,", "el") + txt(970, 149, "one typed result out", "el"))
z = svg(1152, 256, z)
page(2, "Part 2 · The graph", "Loops and graphs are zoom levels, not rivals.", f"""
{z}
<div class="grid g3" style="margin-top:14px">
  {card("Autonomy inside nodes, rules between them", "In an open while-loop the model improvises its own control flow. In a graph the model is free inside each node, and you define how work moves from node to node.", "graph")}
  {card("Cycles are a feature", "A data pipeline is a DAG: a step running twice is a bug. Agent graphs are cyclic on purpose. Retry, refine, ask, wait for approval. The cycles are just bounded.", "graph")}
  {card("What is actually new", "A node can now be an entire agent that works through hundreds of tool calls and hands back a typed result. LangChain calls this the real reason the new term is justified.", "graph")}
</div>
""", lede="&ldquo;Loops are dead&rdquo; is wrong. Graphs do not eliminate loops. They contain them.")

# ═════════════════════════════ PAGE 10 · not that graph ═════════════════════════════

page(2, "Part 2 · The graph", "Not that kind of graph.", f"""
<div class="cols" style="grid-template-columns:1fr 1fr; gap:18px">
  <div class="card versus a"><div class="tag">This guide</div><h3>Graph as architecture</h3>
    <p class="q">&ldquo;Which worker or check runs next, with what state, under which rules?&rdquo;</p>
    <dl><dt>Node</dt><dd>A unit of work: agent, tool call, router, linter, human gate</dd>
        <dt>Edge</dt><dd>Control flow: a transition, a branch, a parallel fan-out</dd>
        <dt>Tools</dt><dd>LangGraph, LlamaIndex Workflows, Google ADK, Temporal, Prefect</dd>
        <dt>Cost to adopt</dt><dd>Low to moderate. You declare state, nodes and edges.</dd></dl></div>
  <div class="card versus b"><div class="tag">Different thing</div><h3>Graph as data</h3>
    <p class="q">&ldquo;Where do the facts live, and how do I follow relationships between them?&rdquo;</p>
    <dl><dt>Node</dt><dd>An entity: a customer, a module, a statute, an incident</dd>
        <dt>Edge</dt><dd>A typed relation: <span class="mono">depends_on</span>, <span class="mono">supersedes</span>, <span class="mono">caused_by</span></dd>
        <dt>Tools</dt><dd>Neo4j, Microsoft GraphRAG, HippoRAG 2, Zep Graphiti</dd>
        <dt>Cost to adopt</dt><dd>Very high. Around 1,000 times the indexing cost of vectors, plus entity resolution.</dd></dl></div>
</div>
<div class="cols" style="grid-template-columns: 1.15fr 1fr; gap:18px; margin-top:16px; align-items:start">
  <div class="note"><b>Also not:</b> graph neural networks (models that learn over graph data) or Graph of Thoughts (a graph of reasoning steps inside one agent). <b>How the two meet:</b> in a mature system the knowledge graph is simply called from a retrieval node, and agent memory lives in the shared state.</div>
  <div class="kg">
    <div class="lbl">When a knowledge graph earns its cost (GraphRAG-Bench and related audits)</div>
    <div class="kgrow"><span class="up">+10.5 pts</span>multi-hop questions: graph 53.4% vs vector 42.9%</div>
    <div class="kgrow"><span class="up">+36.4 pts</span>how facts change over time: 58.1% vs 21.7%</div>
    <div class="kgrow"><span class="dn">&minus;0.8 pts</span>simple fact lookup: 60.1% vs 60.9% for plain vector search</div>
    <div class="kgrow"><span class="dn">77% / 44%</span>chance a 5-hop chain holds at 95% / 85% accuracy per hop</div>
  </div>
</div>
""", lede="The word means two different things in AI. Mixing them up is the most common mistake in this conversation.")

# ═════════════════════════════ PAGE 11 · loop vs graph ═════════════════════════════

cmp = [
    ("What you design", "One agent's repeated feedback cycle", "The topology: nodes, edges, state, contracts"),
    ("Who steers", "The model picks nearly every step", "You fix the structure; nodes keep local autonomy"),
    ("Parallel work", "Possible, but buried inside a turn", "First-class fan-out and fan-in"),
    ("Verification", "Self-check, or an outer grader", "Independent verifier nodes, voting, policy gates, CI"),
    ("State", "Transcript plus scratch files", "Typed shared state, checkpoints, provenance"),
    ("When it breaks", "Usually the whole run", "One node or one subgraph"),
    ("Recovery", "Re-prompt or restart", "Resume a checkpoint, retry a node, reroute, roll back"),
    ("Human role", "Interrupt, or review at the end", "An explicit approval node on the path"),
    ("Typical failure", "Wandering, self-grading, context pollution", "Coordination bugs, stale shared state, bad routing"),
    ("Cost risk", "Too many turns, ever-growing context", "Fan-out multiplying model calls"),
    ("Best for", "Open-ended exploration where the next step is hard to predict", "Partly structured work with known dependencies, gates or specialist roles"),
]
page(2, "Part 2 · The graph", "Loop and graph, side by side.", f"""
<table class="tbl cmp">
  <thead><tr><th style="width:17%"></th><th style="width:38%"><span class="c-loop">Loop engineering</span> <em>feedback through time</em></th><th><span class="c-graph">Graph engineering</span> <em>relationships through time and structure</em></th></tr></thead>
  <tbody>{''.join(f'<tr><td class="dim">{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in cmp)}</tbody>
</table>
<p class="fine">Typical tendencies, not hard rules. Loops are graphs, and graph nodes can be loops, so the two columns overlap on purpose.</p>
""")

# ═════════════════════════════ PAGE 12 · six patterns ═════════════════════════════

def mini(inner):
    return svg(330, 104, inner, "mini")

p_chain = mini(node(8, 34, 78, 36, "Step 1", "agent", fs=11.5) + ln(86, 52, 116, 52) + node(118, 34, 78, 36, "Check", "code", fs=11.5) +
               ln(196, 52, 226, 52) + node(228, 34, 78, 36, "Step 2", "agent", fs=11.5))
p_router = mini(node(8, 34, 78, 36, "Router", "code", fs=11.5) +
                edge("M86 44 C 130 44, 150 20, 196 20") + ln(86, 52, 196, 52) + edge("M86 60 C 130 60, 150 84, 196 84") +
                node(198, 4, 108, 30, "Bug fix agent", "agent", fs=11) + node(198, 38, 108, 30, "Docs agent", "agent", fs=11) + node(198, 72, 108, 30, "Cheap model", "agent", fs=11))
p_par = mini(pill(4, 38, 44, 28, "in", 11) + edge("M48 46 C 80 46, 84 20, 112 20") + ln(48, 52, 112, 52) + edge("M48 58 C 80 58, 84 84, 112 84") +
             node(114, 4, 96, 30, "Security", "verify", fs=11) + node(114, 38, 96, 30, "Logic", "verify", fs=11) + node(114, 72, 96, 30, "Style", "verify", fs=11) +
             edge("M210 20 C 238 20, 240 46, 262 46") + ln(210, 52, 262, 52) + edge("M210 84 C 238 84, 240 58, 262 58") +
             node(264, 36, 62, 32, "Merge", "code", fs=11))
p_orch = mini(node(4, 34, 96, 36, "Orchestrator", "agent", fs=11, loop=False) +
              edge("M100 44 C 130 44, 136 20, 160 20") + ln(100, 52, 160, 52) + edge("M100 60 C 130 60, 136 84, 160 84") +
              node(162, 4, 76, 30, "Worker", "agent", fs=11) + node(162, 38, 76, 30, "Worker", "agent", fs=11) +
              '<g class="n ghost"><rect x="162" y="72" width="76" height="30" rx="10"/><text x="200" y="91" font-size="11">+ N more</text></g>' +
              edge("M238 20 C 262 20, 262 46, 280 46") + ln(238, 52, 280, 52) + edge("M238 84 C 262 84, 262 58, 280 58") +
              node(282, 36, 46, 32, "Sum", "agent", fs=11))
p_eval = mini(node(22, 34, 104, 36, "Generator", "agent", fs=11.5) + ln(126, 46, 196, 46) +
              node(198, 34, 104, 36, "Evaluator", "verify", fs=11.5) +
              edge("M250 70 C 250 114, 74 114, 74 72", "retry", label="reject, with critique", lx=162, ly=86) +
              edge("M302 52 L326 52", "") + txt(314, 44, "ok", "el"))
p_gate = mini(node(8, 34, 84, 36, "Agent", "agent", fs=11.5) + ln(92, 52, 124, 52, label="proposal", lx=108, ly=30) +
              diamond(160, 52, 68, 54, "Gate", "human", fs=11.5) + ln(194, 52, 226, 52) +
              node(228, 34, 96, 36, "Deploy / pay", "io2", fs=11.5))

def pat(n, name, fig, text, when):
    return f'<div class="card pat"><div class="pathead"><span class="pn">{n}</span><h3>{name}</h3></div>{fig}<p>{text}</p><p class="when"><b>Use when</b> {when}</p></div>'

page(3, "Part 3 · Build one", "Six patterns cover most of what you will build.", f"""
<div class="grid g3 pats">
  {pat(1, "Prompt chain", p_chain, "A fixed sequence. Each step works on the structured output of the last, with a programmatic check in between.", "the steps are known and always the same.")}
  {pat(2, "Router", p_router, "A classifier (code or a small model) inspects the input and sends it to a specialist path or a cheaper model tier.", "inputs fall into distinct kinds.")}
  {pat(3, "Parallelize", p_par, "Fan out, then merge. Either split into independent sections, or run the same check several times and vote.", "subtasks do not need each other's output.")}
  {pat(4, "Orchestrator and workers", p_orch, "A lead agent breaks the task down at runtime, spawns as many workers as it needs, then synthesizes.", "you cannot predict the subtasks in advance.")}
  {pat(5, "Evaluator and optimizer", p_eval, "A generator paired with an independent verifier that has real authority to reject and send work back.", "quality must not be self-certified.")}
  {pat(6, "Gate before side effects", p_gate, "A deterministic check or human approval sits between a model's proposal and anything irreversible.", "a mistake would be costly or hard to undo.")}
</div>
""", lede="Five come from Anthropic's Building Effective Agents. The sixth is the one that keeps you out of trouble.")

# ═════════════════════════════ PAGE 13 · worked example ═════════════════════════════

def badge(x, y, n):
    return f'<g class="badge"><circle cx="{x}" cy="{y}" r="10"/><text x="{x}" y="{y+4}">{n}</text></g>'

ex = (pill(0, 124, 78, 34, "feature") + ln(78, 141, 104, 141) +
      node(106, 114, 112, 54, "Planner", "agent", sub="writes the plan") + ln(218, 141, 252, 141) +
      node(254, 106, 138, 70, "Worker", "agent", sub="loops on code + tests", loop=True) +
      edge("M392 126 C 430 126, 430 44, 468 44") + ln(392, 141, 468, 141) + edge("M392 156 C 430 156, 430 238, 468 238") +
      node(470, 20, 138, 48, "Security review", "verify", sub="fresh context") +
      node(470, 117, 138, 48, "Logic review", "verify", sub="fresh context") +
      node(470, 214, 138, 48, "Style review", "verify", sub="fresh context") +
      edge("M608 44 C 646 44, 646 126, 684 128") + ln(608, 141, 684, 141) + edge("M608 238 C 646 238, 646 156, 684 154") +
      node(686, 114, 118, 54, "Synthesizer", "code", sub="merges findings") + ln(804, 141, 836, 141) +
      diamond(888, 141, 100, 76, "Pass?", "code") +
      ln(938, 141, 972, 141, label="yes", lx=954, ly=133) +
      node(974, 114, 96, 54, "Human", "human", sub="approves") + ln(1070, 141, 1094, 141) +
      pill(1096, 124, 56, 34, "merge") +
      edge("M888 179 L888 300 L323 300 L323 178", "retry", label="no: structured critique goes back to the worker (max 3 retries)", lx=606, ly=316) +
      badge(254, 106, 1) + badge(470, 20, 2) + badge(686, 114, 3) + badge(888, 103, 4) + badge(974, 114, 5))
ex = svg(1152, 322, ex)
page(3, "Part 3 · Build one", "A graph you could build this week: ship a feature.", f"""
{ex}
<div class="grid g5 steps" style="margin-top:6px">
  <div class="step"><span class="bn">1</span><b>Autonomy stays inside.</b> The worker loops on code and tests for as long as its budget allows. Nobody scripts its steps.</div>
  <div class="step"><span class="bn">2</span><b>Reviewers are independent.</b> Each gets a fresh context and only the diff. None of them sees the worker's reasoning.</div>
  <div class="step"><span class="bn">3</span><b>Fan-in is plain code.</b> Wait for all three, merge into one structured list of findings.</div>
  <div class="step"><span class="bn">4</span><b>The gate is not a vibe.</b> Tests green and no blocking findings, or it goes back with the critique attached.</div>
  <div class="step"><span class="bn">5</span><b>A person owns the irreversible step.</b> The run pauses, saves its state, and resumes on approval.</div>
</div>
<div class="cols" style="grid-template-columns: 1fr auto; gap:18px; margin-top:12px; align-items:center">
  <div class="note slim"><b>In coding-agent terms:</b> reviewers are subagents with their own context, the worker's sandbox is a git worktree, project conventions live in SKILL.md, and the gate is your test suite and CI.</div>
  {LEGEND}
</div>
""", lede="Planner, worker, parallel reviewers, synthesizer, pass/fail gate. Five stages is the recommended ceiling for a first graph.")

# ═════════════════════════════ PAGE 14 · node contract ═════════════════════════════

six = [
    ("One responsibility", "A single job you can say in a sentence."),
    ("What it may read", "The minimum state keys it needs. Nothing more."),
    ("What it must write", "A structured output schema, not free prose."),
    ("Tools and permissions", "Only what this role requires."),
    ("Timeout, retries, budget", "Hard ceilings on time, attempts and spend."),
    ("Evidence of success", "The objective proof that lets it say done."),
]
sixh = "".join(f'<li><span class="k">{i+1}</span><div><b>{a}</b>{b}</div></li>' for i, (a, b) in enumerate(six))
page(3, "Part 3 · Build one", "A diagram is not an architecture. Every node signs a contract.", f"""
<div class="cols" style="grid-template-columns: 1fr 520px; gap:40px; align-items:start">
  <div>
    <ul class="six">{sixh}</ul>
    <div class="note" style="margin-top:14px"><b>Think in typed handoffs.</b> Interfaces such as <span class="mono">ResearchRequest → EvidenceBundle</span> or <span class="mono">PatchCandidate → VerifiedPatch</span> replace every component scribbling in one shared conversation.</div>
  </div>
  <div class="spec">
    <div class="spechead"><span>node</span> security_reviewer<i>contract</i></div>
    <div class="specrow"><span>does</span><div>Find security defects in one diff. Nothing else.</div></div>
    <div class="specrow"><span>reads</span><div><code>patch.diff</code> <code>plan.summary</code></div></div>
    <div class="specrow"><span>writes</span><div><code>findings: Finding[]</code><em>severity · file · line · why · suggested fix</em></div></div>
    <div class="specrow"><span>tools</span><div><code>read_file</code> <code>grep</code> <code>run_scanner</code><em>no write access, no network</em></div></div>
    <div class="specrow"><span>limits</span><div><code>timeout 5 min</code> <code>retries 1</code> <code>budget 60k tokens</code></div></div>
    <div class="specrow"><span>done when</span><div>Every changed file is covered and each finding cites a line.</div></div>
    <div class="specfoot">Illustrative values. The six fields are the point.</div>
  </div>
</div>
""", lede="Six things to write down for each node before you write any orchestration code.")

# ═════════════════════════════ PAGE 15 · state ═════════════════════════════

chat = ""
ws = [150, 190, 120, 200, 170, 90, 196, 140, 180, 110, 200, 160]
for i, w in enumerate(ws):
    c = "#F3C7AE" if i in (5, 8) else "#DDD7CB"
    chat += f'<rect x="{10 if i % 2 == 0 else 220 - w}" y="{8 + i*17}" width="{w}" height="11" rx="5.5" fill="{c}"/>'
chat = svg(230, 216, chat)

ck = ('<path class="e" d="M16 30 L300 30" style="marker-end:none"/>' +
      "".join(f'<circle class="ckp" cx="{16+i*71}" cy="30" r="7"/>' + txt(16 + i * 71, 54, f"step {i+1}", "el") for i in range(5)) +
      '<path class="e retry" d="M158 30 C 180 2, 220 4, 244 4" marker-end="url(#ah)"/>' + txt(292, 8, "fork and retry", "el retry"))
ck = svg(340, 62, ck)

page(3, "Part 3 · Build one", "Stop using the chat log as your database.", f"""
<div class="cols" style="grid-template-columns: 270px 1fr 372px; gap:22px; align-items:stretch">
  <div class="card plain"><div class="tag bad">Loop habit</div><h3>State is the transcript</h3>{chat}<p>Plans, drafts, errors and decisions all pile into one history that every call re-reads.</p></div>
  <div class="card plain"><div class="tag good">Graph habit</div><h3>State is a typed record</h3>
<pre class="code"><span class="cm"># each key has an owner and a merge rule</span>
<b>State</b>
  task        <i>str</i>
  plan        <i>Plan</i>              <span class="cm">planner writes</span>
  patch       <i>PatchCandidate</i>    <span class="cm">worker writes</span>
  findings    <i>list[Finding]</i>     <span class="cm">reducer: append</span>
  tests       <i>TestReport</i>
  budget      <i>tokens, retries</i>   <span class="cm">first-class</span>
  approval    <i>pending | granted</i></pre>
    <p>Nodes read what they need and write structured updates. Parallel writers merge through a reducer instead of overwriting each other.</p></div>
  <div class="card plain"><div class="tag">Under the hood</div><h3>Steps with a barrier</h3>
    <ol class="super"><li><b>Plan.</b> Pick the nodes whose inputs changed.</li><li><b>Execute.</b> Run them in parallel, each reading the same frozen snapshot.</li><li><b>Update.</b> Commit all writes together, then checkpoint.</li></ol>
    {ck}
    <p>This is how LangGraph's Pregel runtime avoids agents corrupting shared memory mid-step.</p></div>
</div>
<div class="lbl" style="margin-top:14px">What a checkpoint after every step buys you</div>
<div class="grid g4">
  {card("Crash and resume", "A shutdown stops the graph cleanly at a step boundary. A fresh instance picks up from the saved state.", "graph")}
  {card("Pause for a human", "The run saves itself and releases compute. A person inspects, edits state if needed, and resumes.", "graph")}
  {card("Time travel", "Open any earlier checkpoint, change a parameter or prompt, and fork a new branch without re-running upstream.", "graph")}
  {card("Retry only what broke", "Keep validated upstream work. Roll back or re-execute just the corrupted part.", "graph")}
</div>
""")

# ═════════════════════════════ PAGE 16 · evidence ═════════════════════════════

page(4, "Part 4 · Reality check", "What the evidence says, and what it costs.", f"""
<div class="grid g3 stats">
  <div class="stat good"><div class="num">+90.2%</div><h3>better on breadth-first research</h3><p>Anthropic's multi-agent research system against its own single-agent setup, on an internal evaluation.</p></div>
  <div class="stat good"><div class="num">up to 90%</div><h3>less wall-clock time</h3><p>For complex queries in the same system, after moving from sequential searching to parallel subagents and parallel tool calls.</p></div>
  <div class="stat bad"><div class="num">~15&times;</div><h3>the tokens of a normal chat</h3><p>Every parallel worker and reviewer starts its own context window and system prompt. Speed and breadth are bought with compute.</p></div>
</div>
<div class="cols" style="grid-template-columns: 1.1fr 1fr; gap:18px; margin-top:16px">
  <div class="note warn"><b>Read these numbers carefully.</b> They are vendor-reported measurements of one system, not independent benchmarks. Anthropic's own analysis found that token use alone explained much of the performance difference in a browsing evaluation. Some of what looks like &ldquo;multi-agent intelligence&rdquo; is simply more compute. The same report says tightly coupled tasks are a poor fit.</div>
  <div class="stack" style="gap:12px">
    <div class="sig"><b>Google ADK 2.0 (May 2026)</b>rebuilt its runtime from a hierarchical agent executor into a graph engine. Agents, tools and functions are all nodes.</div>
    <div class="sig"><b>LangGraph</b>passed 65 million monthly downloads by mid-2026, with production use reported at Klarna, Replit and Elastic.</div>
    <div class="sig"><b>Sparse beats chatty.</b> Research on communication topologies finds that all-to-all agent chat hurts accuracy. Pruning low-value edges does better for fewer tokens.</div>
  </div>
</div>
""", lede="The best-documented case is Anthropic's Research system: a lead agent, parallel workers, a separate citation checker.")

# ═════════════════════════════ PAGE 17 · sixteen agents ═════════════════════════════

def agents_panel(conv):
    o = ""
    for i in range(8):
        ax = 30 + i * 62
        o += f'<g class="n agent"><circle cx="{ax}" cy="36" r="15"/></g>' + loopglyph(ax, 36, 5.5)
        if conv:
            o += f'<path class="e bad" d="M{ax} 52 L{252 + (i-3.5)*8:.0f} 128" marker-end="url(#ah)"/>'
        else:
            o += f'<path class="e good" d="M{ax} 52 L{ax} 126" marker-end="url(#ah)"/>'
            o += f'<g class="n verify"><rect x="{ax-22}" y="128" width="44" height="30" rx="8"/><text x="{ax}" y="147" font-size="10.5">bug {i+1}</text></g>'
    if conv:
        o += '<g class="n badn"><rect x="152" y="130" width="200" height="38" rx="10"/><text x="252" y="153" font-size="12.5">Linux kernel build fails</text></g>'
    return svg(500, 176, o, style="width:100%")

page(4, "Part 4 · Reality check", "Sixteen agents, one bottleneck.", f"""
<div class="cols" style="grid-template-columns:1fr 1fr; gap:18px">
  <div class="card plain center"><div class="tag good">Parallelism works</div><h3>Many independent failing tests</h3>{agents_panel(False)}<p>Each agent takes a different bug. Work divides cleanly, and progress scales with the number of agents.</p></div>
  <div class="card plain center"><div class="tag bad">Parallelism stalls</div><h3>Everyone hits the same wall</h3>{agents_panel(True)}<p>All sixteen agents collide on one problem, repeat each other's work, and overwrite each other's fixes.</p></div>
</div>
<div class="cols" style="grid-template-columns: 1fr 1.25fr; gap:28px; margin-top:16px; align-items:center">
  <p class="body"><b>The experiment.</b> In February 2026, Nicholas Carlini ran sixteen parallel Claude instances through almost 2,000 sessions to build a C compiler. Parallelism helped until the remaining work stopped being separable. The fix was not more agents. It was restructuring the test setup so the work split into independent pieces again.</p>
  <blockquote class="big tight">A good graph does not just add nodes. It creates useful <b class="c-graph">independence</b> between them.<cite>Agent count is not the resource. Decomposable work is.</cite></blockquote>
</div>
""", lede="The most useful lesson about multi-agent systems comes from a stress test that hit a limit.")

# ═════════════════════════════ PAGE 18 · fan-out math ═════════════════════════════

def bars(vals):
    o = ""
    for i, (lab, v, mx, c, t) in enumerate(vals):
        o += (f'<div class="bar"><span class="bl">{lab}</span><span class="bt"><i style="width:{v/mx*100:.0f}%;background:{c}"></i></span><span class="bv">{t}</span></div>')
    return o

page(4, "Part 4 · Reality check", "The math of fan-out: the 50% rule.", f"""
<div class="cols" style="grid-template-columns:1fr 1fr; gap:18px">
  <div class="card plain"><div class="tag good">Pass rate 50% per cycle</div><h3>Parallel wins: same calls, less waiting</h3>
    <div class="lbl sm">Agent calls to finish</div>
    {bars([("Loop", 6, 6, "var(--loop)", "2 &times; 3 in sequence = 6"), ("Graph", 6, 6, "var(--graph)", "2 &times; 3 in parallel = 6")])}
    <div class="lbl sm" style="margin-top:10px">Wall-clock time</div>
    {bars([("Loop", 3, 3, "var(--loop)", "baseline"), ("Graph", 2, 3, "var(--graph)", "about two-thirds")])}
    <p>Both need about two cycles. The graph spends the same number of calls and finishes sooner.</p></div>
  <div class="card plain"><div class="tag bad">Pass rate 30% per cycle</div><h3>Parallel loses: you pay for every failure three times</h3>
    <div class="lbl sm">Cycles to finish</div>
    {bars([("Loop", 3.3, 3.3, "var(--loop)", "about 3.3"), ("Graph", 3.3, 3.3, "var(--graph)", "about 3.3")])}
    <div class="lbl sm" style="margin-top:10px">Tokens burned per failed cycle</div>
    {bars([("Loop", 1, 3, "var(--loop)", "stops at the first failed check"), ("Graph", 3, 3, "var(--graph)", "3&times;: all reviewers fire every time")])}
    <p>The loop fails fast and retries cheaply. The graph launches every branch on every doomed attempt.</p></div>
</div>
<div class="cols" style="grid-template-columns: 1.1fr 1fr; gap:18px; margin-top:16px">
  <div class="rule"><div class="lbl">The rule</div>Keep low-pass-rate work inside a sequential loop until the worker is reliable. Fan out once the per-cycle pass rate is above roughly 50%.
    <div class="ineq">value of <b>independence + parallelism</b> &nbsp;&gt;&nbsp; cost of <b>coordination + tokens + latency</b></div></div>
  <div class="note"><b>Make budgets part of the state.</b> A graph that can spawn workers needs hard limits it can read and enforce:
    {chips(["max agents", "tool calls", "wall-clock", "tokens", "retries", "money"], "mono")}</div>
</div>
""", lede="A worked model with three verification checks (Flowtivity). Whether a graph saves money depends on how often the work passes.")

# ═════════════════════════════ PAGE 19 · how graphs fail ═════════════════════════════

fails = [
    ("Poisoned upstream", "One hallucinating or compromised node feeds bad input to every branch below it."),
    ("Shared-state races", "Two branches update the same key. Lost updates, stale reads, duplicate side effects."),
    ("Wrong routing", "A faulty router sends work to the wrong specialist, or the wrong permission level, every time."),
    ("Fan-out bills", "Parallel branches multiply model calls. A harmful action also runs faster in parallel."),
    ("Bigger attack surface", "More agents with more tools means more places for prompt injection to land."),
    ("An org chart of weak employees", "Drawing a big graph before one capable agent has solved the task just multiplies surfaces and cost."),
]
defs = [
    ("Gate before anything irreversible", "Schema checks, policy, spending limits, or a human between proposal and action."),
    ("Least privilege per node", "Each role gets only its own tools. Keep trusted and untrusted state apart."),
    ("Budgets and retry ceilings", "Enforced by the runtime, not requested in a prompt."),
    ("Checkpoints", "Contain a failure to one node. Resume instead of restarting."),
    ("Verifiers that are actually different", "Five copies of the same model voting can be weaker than one deterministic check, one differently prompted critic and one external test."),
    ("Sparse wiring", "Connect only the nodes that need to talk. Start with 3 to 5 nodes."),
]
page(4, "Part 4 · Reality check", "Graphs fail in their own ways.", f"""
<div class="cols" style="grid-template-columns:1fr 1fr; gap:22px">
  <div><div class="colhead bad">New ways to fail</div><ul class="list bad">{''.join(f'<li><b>{a}</b>{b}</li>' for a, b in fails)}</ul></div>
  <div><div class="colhead good">What to build in</div><ul class="list good">{''.join(f'<li><b>{a}</b>{b}</li>' for a, b in defs)}</ul></div>
</div>
<blockquote class="mid center" style="margin-top:22px">Graphs are not safer by default. They give you more places to put safety, and more places to audit it.</blockquote>
""", lede="A graph is a control surface, not a safety proof. It can contain a failure, and it can also amplify one.")

# ═════════════════════════════ PAGE 20 · governing loops ═════════════════════════════

page(4, "Part 4 · Reality check", "When loops multiply, someone has to govern them.", f"""
<div class="cols" style="grid-template-columns: 0.92fr 1.08fr; gap:26px">
  <div><div class="colhead bad">Four ways uncoordinated loops go wrong</div>
    <ul class="list bad">
      <li><b>Goodhart's collapse</b>A loop sees only its one metric and learns to game it. More downloads through clickbait titles that burn audience trust.</li>
      <li><b>Upward blindness</b>A feedback loop cannot step back and ask whether its target is still the right target.</li>
      <li><b>Loops fighting loops</b>One optimizes speed, its sibling optimizes thoroughness. A heater and an air conditioner in the same room, both dashboards green.</li>
      <li><b>Nobody watching the watcher</b>The eval suite drifts away from real traffic while its scores keep climbing.</li>
    </ul></div>
  <div><div class="colhead good">Four rules to wire into the graph</div>
    <ul class="list good num">
      <li><span class="k">1</span><div><b>Metrics never travel alone.</b>Pair every speed or volume metric with a quality or safety metric tied to something the model cannot game: real retention, real revenue, the compiler.</div></li>
      <li><span class="k">2</span><div><b>Every target has an owner.</b>A human or higher-level loop sits upstream with the authority to audit, veto or roll back.</div></li>
      <li><span class="k">3</span><div><b>Separate the speeds.</b>Real-time execution, daily prompt tuning, weekly operations, quarterly strategy. Fast loops escalate to slow ones. They do not override them.</div></li>
      <li><span class="k">4</span><div><b>Freeze the guardrails.</b>Certain verification gates and approval rules are fixed, so a self-improving loop cannot optimize them away.</div></li>
    </ul></div>
</div>
<div class="note" style="margin-top:14px"><b>Two graphs, really.</b> The <i>work graph</i> produces artifacts: code, reports, fixes. The <i>improvement graph</i> is the network of feedback loops that watch traces and adjust prompts, policies and other loops. The second one needs engineering too.</div>
""", lede="Ideas from control theory, via Carlos E. Perez and Eigent. Useful the moment you run more than one automated loop.")

# ═════════════════════════════ PAGE 21 · testing & tracing ═════════════════════════════

ladder = [
    ("Node tests", "Does each function, tool adapter and agent honour its contract?"),
    ("Edge and routing tests", "Given this state, which transitions are possible?"),
    ("Invariant tests", "Can a forbidden state or action ever be reached?"),
    ("Subgraph tests", "Does a whole capability, such as code review, hold up?"),
    ("End-state tests", "What actually changed in the outside world?"),
    ("Trajectory evals", "Efficiency, tool choice, policy adherence, odd behaviour."),
    ("Repeated trials", "Same input, many runs. Paths differ, so run it more than once."),
]
lad = "".join(f'<div class="rung" style="margin-left:{i*18}px"><b>{a}</b><span>{b}</span></div>' for i, (a, b) in enumerate(ladder))
page(4, "Part 4 · Reality check", "Test the wiring, not just the answer.", f"""
<div class="cols" style="grid-template-columns: 1.12fr 1fr; gap:30px">
  <div><div class="lbl">A testing ladder for graphs</div><div class="ladder">{lad}</div>
    <p class="fine" style="margin-top:10px">Many different paths can reach the same good outcome. Judge the final state and the safety constraints. Use traces to diagnose, not to demand one canonical path.</p></div>
  <div class="stack" style="gap:14px">
    <div class="card plain"><div class="tag">Review questions that prompts never raised</div>
      <ul class="qs"><li>Can an unverified value reach the payment node?</li><li>What happens if worker C times out?</li><li>Can these two branches write the same state?</li><li>Which graph version produced this side effect?</li></ul></div>
    <div><div class="lbl">Every trace should carry</div>{chips(["node id", "graph version", "parent and child", "edge decision", "state delta", "model and tool versions", "latency", "cost", "side-effect id"], "mono")}</div>
    <div class="note slim"><b>What you deploy is no longer &ldquo;prompt + model name&rdquo;.</b> It is graph version, node versions, state schema, tool versions, checkpoints and traces. Long runs may be mid-flight when you ship, so roll out gradually.</div>
  </div>
</div>
""", lede="For coding agents this is unusually tractable: patches can be compiled, type-checked, linted, scanned and run against tests.")

# ═════════════════════════════ PAGE 22 · decision table ═════════════════════════════

dec = [
    ("Ownership", "One agent with one prompt and toolset can own the task end to end.", "The work needs different specialties, model tiers or separate permissions."),
    ("Verification", "Fewer than three checks. One test or rubric validates the result.", "Three or more independent checks, plus conditional routing."),
    ("Concurrency", "Steps are strictly sequential and share the same tight context.", "Subtasks can run at the same time and be merged."),
    ("Pass rate", "Below 50% per cycle. Fail fast, retry cheaply.", "At or above 50%. Fan-out cuts waiting by a third to 90%."),
    ("Recovery", "Short runs that are cheap to replay from scratch.", "Long runs that need checkpoints, partial rollback, pause and resume."),
    ("Human oversight", "A person reviews the output afterwards, or chats along.", "High-stakes actions need approval before they execute."),
]
page(5, "Part 5 · Your move", "Loop or graph? Decide row by row.", f"""
<table class="tbl decide">
  <thead><tr><th style="width:15%"></th><th style="width:42.5%"><span class="hd loop">Stay with a loop when&hellip;</span></th><th><span class="hd graph">Move to a graph when&hellip;</span></th></tr></thead>
  <tbody>{''.join(f'<tr><td class="dim">{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in dec)}</tbody>
</table>
<div class="cols" style="grid-template-columns:1fr 1fr; gap:18px; margin-top:16px">
  <div class="note"><b>Graphs are not the default.</b> Choosing a single well-scoped loop early on is a deliberate advantage, not a shortcut. Anthropic's advice still stands: start with the simplest thing that works, and add complexity only when it earns its cost.</div>
  <div class="note"><b>And it can go the other way.</b> LangChain's own deep-research system moved <i>away</i> from a predefined graph and back toward an agentic core loop, because the best order of discovery could not be predicted ahead of time.</div>
</div>
""", lede="Mostly left column: keep your loop. Several rows on the right: you have outgrown it.")

# ═════════════════════════════ PAGE 23 · run by hand ═════════════════════════════

hand = [
    ("Name the output", "Write the final deliverable in one concrete sentence. &ldquo;A verified pull request.&rdquo; &ldquo;A one-page recommendation on whether this idea is worth testing.&rdquo;"),
    ("List the jobs", "Write down the five to seven distinct jobs a competent human specialist would do to produce it."),
    ("Map real dependencies", "Which jobs truly need another job's output? Ignore the order you happened to write them in."),
    ("Mark the gates", "Wherever an error would have a large blast radius, insert a mandatory human checkpoint."),
    ("Play every node yourself", "Open a fresh chat for each node. Pass only the output artifact from one chat into the next. No shared history."),
]
page(5, "Part 5 · Your move", "Before you automate anything, run the graph by hand.", f"""
<div class="grid g5 hand">
  {''.join(f'<div class="hstep"><div class="hn">{i+1}</div><h3>{a}</h3><p>{b}</p></div>' for i, (a, b) in enumerate(hand))}
</div>
<div class="cols" style="grid-template-columns: 1.2fr 1fr; gap:18px; margin-top:18px; align-items:stretch">
  <div class="rule"><div class="lbl">The test</div>Automate the topology only if the isolated, node-by-node version clearly produces better output than one continuous chat session. If it does not, you have just learned that cheaply.</div>
  <div class="note"><b>Why this works.</b> Separate chats give each role its own context, exactly as separate nodes would. You experience the handoffs, discover which artifacts each step really needs, and find the gates, all before writing a line of orchestration code.</div>
</div>
""", lede="A thirty-minute experiment with nothing but chat windows. It tells you whether a graph would help at all.")

# ═════════════════════════════ PAGE 24 · five stages ═════════════════════════════

stages = [
    ("Audit", "Map every loop you run. Record steps per run, where retries cluster, wall-clock time, and token cost per successful task."),
    ("Identify", "In those traces, find actions that do not depend on each other, and every place where the agent reviews its own work."),
    ("Design", "Sketch the topology with a hard ceiling of 3 to 5 nodes. Write the six contracts for each one."),
    ("Implement", "Use a framework or plain async primitives. Keep measuring time saved against tokens spent, and watch the 50% pass-rate line."),
    ("Type and govern", "Give edges explicit meaning, make human approvals resumable steps, and anchor feedback loops to metrics that cannot be gamed."),
]
exs = [
    "Start from data you already have: traces.",
    "Security, logic and style checks. Docs, code and tickets. Unit, integration and end-to-end tests.",
    "Planner → Worker → Parallel reviewers → Synthesizer → Pass/fail gate",
    "<span class='mono'>asyncio.gather()</span> is a perfectly good first runtime.",
    "<span class='mono'>depends_on</span> · <span class='mono'>supersedes</span> · <span class='mono'>decided_by</span> · <span class='mono'>caused</span>",
]
page(5, "Part 5 · Your move", "Five stages from a loop to a graph.", f"""
<div class="stages">
  {''.join(f'<div class="stage"><div class="sn">Stage {i+1}</div><h3>{a}</h3><p>{b}</p><div class="sx">{exs[i]}</div></div>' for i, (a, b) in enumerate(stages))}
</div>
<div class="note" style="margin-top:18px"><b>Go in this order.</b> The first two stages are observation only. Most of the value comes from stage 2: discovering which parts of your existing loop were secretly parallel, and where generation and verification were tangled together. Sometimes the answer is two changes to your loop, not a new architecture.</div>
""", lede="For when hand-testing and production traces agree that one loop is hiding structure.")

# ═════════════════════════════ PAGE 25 · tooling map ═════════════════════════════

tools = [
    ("LangGraph", "Agent state machine", "Typed state channels with reducers, cyclic retries, checkpoints after every step, time travel, human-in-the-loop pauses.", "graph"),
    ("LlamaIndex Workflows", "Event-driven steps", "Decorate functions as steps that react to typed events. No global barrier, so fast branches do not wait for slow ones.", "graph"),
    ("Google ADK 2.0", "Graph-native runtime", "Agents, tools and functions are all nodes. Graph, dynamic and collaborative workflows are core primitives.", "graph"),
    ("OpenAI Agents SDK", "Orchestration and tracing", "Single and multi-agent orchestration with built-in tools and integrated tracing.", "graph"),
    ("Temporal", "Durable execution", "Wraps node runs as activities: event-sourced history, timeouts, automatic retries across infrastructure crashes.", "code"),
    ("Prefect / Dagster", "Data and lineage", "Orchestrates the surrounding data assets so that agent runs stay reproducible and comparable.", "code"),
]
page(5, "Part 5 · Your move", "The tooling map, briefly.", f"""
<div class="grid g3 tools">
  {''.join(f'<div class="card tool {k}"><div class="tag">{b}</div><h3>{a}</h3><p>{c}</p></div>' for a, b, c, k in tools)}
</div>
<div class="cols" style="grid-template-columns: 1fr 1fr 1fr; gap:14px; margin-top:16px">
  <div class="note"><b>Protocols are edges too.</b> MCP connects an agent to tools and data. A2A connects one agent to another, including graphs owned by other teams.</div>
  <div class="note"><b>A common production stack:</b> LangGraph for the agent state machine, Temporal around each node for durability, Kafka for events between services.</div>
  <div class="note"><b>You may not need any of it yet.</b> Subagents, worktrees, a test gate and a tracker file already form a small graph. Structure first, framework second.</div>
</div>
""", lede="Two schools: a central state machine with synchronized steps, or loosely coupled steps reacting to events.")

# ═════════════════════════════ PAGE 26 · open questions ═════════════════════════════

oq = [
    ("Is it the topology, or just more tokens?", "A ten-agent graph that beats one agent also used ten times the compute. Researchers are calling for equal-compute comparisons."),
    ("How much of the graph should be fixed?", "Too rigid and capable models cannot find better strategies. The likely answer: fixed safety boundaries around model-chosen paths."),
    ("Who designs the graph?", "Today, mostly you. Systems that compile a goal, policies and budget into a graph, then tune it from traces, are an open research area."),
    ("What does &ldquo;verified&rdquo; mean?", "A schema can say a node returns evidence. It cannot say what counts as enough, or whether two agents agree on the word."),
    ("Are your verifiers independent?", "Agents built on the same model and prompts share failure modes. Nobody yet knows how to measure that well."),
    ("Will the name last?", "It may dissolve into older terms: workflows, state machines, distributed systems. The underlying need for explicit control will not."),
]
page(5, "Part 5 · Your move", "Still unsettled, and worth saying out loud.", f"""
<div class="grid g3 oqs">
  {''.join(f'<div class="card oq"><div class="qm">?</div><h3>{a}</h3><p>{b}</p></div>' for a, b in oq)}
</div>
<div class="note" style="margin-top:16px"><b>The honest summary.</b> Feng et al. present graph engineering as an emerging paradigm, not a settled discipline, and say the evidence does not yet show it improves performance everywhere. LangChain calls the term a buzzword for a real, long-standing engineering problem. Both can be true.</div>
""", lede="A field guide should also mark where the map runs out.")

# ═════════════════════════════ PAGE 27 · cheat sheet ═════════════════════════════

rules = [
    "Start with one good loop. Graduate only when traces say so.",
    "Draw the graph before you code it. Run it by hand before you automate it.",
    "Keep autonomy inside nodes and rules between them.",
    "Never let a model grade its own work. Verify in a separate context.",
    "First graph: 3 to 5 nodes. Six contracts per node.",
    "Put state in a typed record with checkpoints, not in the transcript.",
    "Fan out only when work is truly independent and passes more than half the time.",
    "Make budgets part of the state: agents, calls, tokens, retries, money.",
    "Put a deterministic or human gate before anything irreversible.",
    "Add independence, not nodes.",
]
pages.append(dict(raw=f"""
<section class="page dark">
  <header><div class="kicker">The one-page cheat sheet</div><h1>Ten rules to keep next to your terminal.</h1></header>
  <div class="body"><ol class="rules">{''.join(f'<li><span>{i+1:02d}</span>{r}</li>' for i, r in enumerate(rules))}</ol>
  <div class="closing">The graph decides where autonomy helps, where plain code should take over, where work can fan out, where evidence must come back together, where state must persist, and where a person must say yes. <b>Agentic nodes inside engineered topology.</b></div></div>
  __FOOT__
</section>"""))

# ═════════════════════════════ PAGE 28 · sources ═════════════════════════════

src = [
    ("The term and the survey", [
        "Feng, Xiang, Zhang et al., <i>Graph Engineering in the Era of LLM Agents: From Individual Intelligence to System Intelligence</i>, arXiv:2608.21156, Aug 2026",
        "LangChain, <i>The Art of Loop Engineering</i>, June 2026",
        "LangChain, <i>3 Years of Graph Engineering with LangGraph</i>, July 2026",
        "Addy Osmani on loop engineering, June 2026, as summarized by AI Builder Club",
    ]),
    ("Production evidence", [
        "Anthropic, <i>Building Effective Agents</i>, Dec 2024",
        "Anthropic, <i>How We Built Our Multi-Agent Research System</i>, June 2025",
        "Nicholas Carlini, <i>Building a C Compiler with a Team of Parallel Claudes</i>, Feb 2026",
        "Anthropic, <i>Demystifying Evals for AI Agents</i>, Jan 2026",
        "Google ADK 2.0 release notes, May 2026; OpenAI, <i>New Tools for Building Agents</i>, Mar 2025",
    ]),
    ("Practice, economics and runtime", [
        "Flowtivity, <i>From Loops to Graphs: The Next Paradigm in AI Agent Engineering</i> (50% rule, five stages)",
        "AI Builder Club, <i>Graph Engineering Guide (2026)</i>; V12 Labs, <i>Graph Engineering for AI Agents: Beyond Loops</i>",
        "Eigent, <i>Graph Engineering for AI Agents: Beyond Single Feedback Loops</i> (governance rules)",
        "LangChain documentation, <i>LangGraph runtime (Pregel)</i>; Temporal documentation, <i>LangGraph integration</i>",
    ]),
    ("Foundations and benchmarks", [
        "Yao et al., <i>ReAct</i>, 2022; Shinn et al., <i>Reflexion</i>, 2023; Madaan et al., <i>Self-Refine</i>, 2023",
        "Besta et al., <i>Graph of Thoughts</i>, 2023; Zhuge et al., <i>Language Agents as Optimizable Graphs</i> (GPTSwarm), 2024",
        "CAMEL, MetaGPT and AutoGen, 2023; LangGraph launch post, Jan 2024",
        "<i>GraphRAG-Bench</i>, arXiv:2506.05690, and evaluation audit arXiv:2506.06331; Zep Graphiti, arXiv:2501.13956",
    ]),
]
page(5, "Sources and scope", "Where this comes from.", f"""
<div class="grid g2 srcs">
  {''.join(f'<div class="srcg"><div class="lbl">{t}</div><ul>{"".join(f"<li>{s}</li>" for s in items)}</ul></div>' for t, items in src)}
</div>
<div class="note" style="margin-top:14px"><b>Scope and limits.</b> This guide condenses three research briefs on graph engineering compiled in October and November 2026. Figures are quoted as the original sources report them. Several are vendor-reported measurements of a single system, and the worked example and node contract are illustrations, not benchmarks. Where sources disagreed, the more conservative reading was used.</div>
""")

# ───────────────────────────── CSS ─────────────────────────────

CSS = r"""
@page { size: 1280px 720px; margin: 0; }
:root{
  --paper:#F7F4EE; --ink:#15171C; --mut:#5A6070; --rule:#DDD7CB; --card:#FFFFFF;
  --loop:#E8590C; --loop-bg:#FDEBDD; --graph:#4338CA; --graph-bg:#ECEBFF;
  --ok:#0F8A5F; --ok-bg:#E3F5EC; --hum:#B7791F; --hum-bg:#FFF1D6; --code:#475569; --code-bg:#EEF1F4;
  --bad:#C2255C; --bad-bg:#FCE8EF; --fs:1.12;
}
*{box-sizing:border-box; margin:0; padding:0}
html,body{background:#222; -webkit-print-color-adjust:exact; print-color-adjust:exact}
body{font-family:"Inter",sans-serif; color:var(--ink); font-size:14.5px; line-height:1.45; font-feature-settings:"ss01","cv11"}
.page{width:1280px; height:720px; background:var(--paper); padding:40px 64px 0; display:flex; flex-direction:column;
  page-break-after:always; break-after:page; overflow:hidden; position:relative}
header{flex:none; margin-bottom:18px}
.kicker{font-family:"IBM Plex Mono",monospace; font-size:11.5px; letter-spacing:.12em; text-transform:uppercase; color:var(--graph); font-weight:500; margin-bottom:9px}
h1{font-family:"Inter Display","Inter",sans-serif; font-size:37px; line-height:1.1; letter-spacing:-.025em; font-weight:700}
.lede{font-size:16.5px; color:var(--mut); margin-top:8px}
.body{flex:1; min-height:0}
footer{flex:none; height:42px; display:flex; align-items:center; justify-content:space-between;
  font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:#8A8F9C}
.prog{display:flex; gap:5px; align-items:center}
.prog i{width:22px; height:3px; border-radius:2px; background:var(--rule)}
.prog i.on{background:var(--graph)} .prog span{margin-left:8px}
h3{font-size:15.5px; line-height:1.25; font-weight:650; letter-spacing:-.01em}
p{font-size:13.6px; line-height:1.48; color:#30343D}
p.body, .body > p.body{font-size:15px; line-height:1.55}
.mono, code{font-family:"IBM Plex Mono",monospace; font-size:.92em}
.c-loop{color:var(--loop)} .c-graph{color:var(--graph)}
.cols{display:grid} .stack{display:flex; flex-direction:column}
.grid{display:grid; gap:14px} .g2{grid-template-columns:1fr 1fr} .g3{grid-template-columns:repeat(3,1fr)}
.g4{grid-template-columns:repeat(4,1fr)} .g5{grid-template-columns:repeat(5,1fr)}
.card{background:var(--card); border:1px solid var(--rule); border-radius:14px; padding:16px 18px; position:relative}
.card h3{margin-bottom:6px}
.card.loop{border-top:3px solid var(--loop)} .card.graph{border-top:3px solid var(--graph)}
.tag{font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.1em; text-transform:uppercase; color:var(--mut); margin-bottom:7px; font-weight:500}
.tag.good{color:var(--ok)} .tag.bad{color:var(--bad)}
.card.loop .tag{color:var(--loop)}
.lbl{font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.1em; text-transform:uppercase; color:var(--mut); margin-bottom:8px; font-weight:500}
.lbl.sm{margin-bottom:5px}
.chips{display:flex; flex-wrap:wrap; gap:6px}
.chip{background:#fff; border:1px solid var(--rule); border-radius:999px; padding:4px 11px; font-size:12.5px; font-weight:500}
.chip.mono{font-family:"IBM Plex Mono",monospace; font-size:11.5px; border-radius:7px; background:#F0EDE6}
.note{background:#EFEBE3; border-radius:12px; padding:13px 16px; font-size:13.4px; line-height:1.5; color:#30343D}
.note b{color:var(--ink)} .note.slim{padding:10px 14px; font-size:12.8px}
.note.warn{background:var(--hum-bg)} .note .chips{margin-top:9px}
.fine{font-size:12px; color:var(--mut); margin-top:10px}
blockquote{font-family:"IBM Plex Serif",serif; color:var(--ink)}
blockquote.big{font-size:29px; line-height:1.28; letter-spacing:-.01em}
blockquote.big.tight{font-size:25px; border-left:3px solid var(--graph); padding-left:22px}
blockquote.mid{font-size:20px; line-height:1.35}
blockquote.center{text-align:center}
blockquote cite{display:block; font-family:"Inter"; font-style:normal; font-size:12.5px; color:var(--mut); margin-top:8px; letter-spacing:0}
blockquote b{font-weight:600}

/* legend + svg */
.legend{display:flex; gap:14px; flex-wrap:wrap; font-size:11.5px; color:var(--mut); justify-content:center}
.legend span{display:flex; align-items:center; gap:5px; white-space:nowrap}
.sw{width:13px; height:13px; border-radius:4px; border:1.5px solid; display:inline-block}
.sw.agent{background:var(--graph-bg); border-color:var(--graph)} .sw.code{background:var(--code-bg); border-color:var(--code)}
.sw.verify{background:var(--ok-bg); border-color:var(--ok)} .sw.human{background:var(--hum-bg); border-color:var(--hum)}
.sw.retry{height:0; width:18px; border:0; border-top:2px dashed var(--loop); border-radius:0}
svg.dg{display:block; max-width:100%; height:auto; overflow:visible}
svg text{font-family:"Inter",sans-serif; fill:var(--ink); font-weight:600}
.n rect,.n polygon,.n circle{stroke-width:1.6}
.n.agent rect,.n.agent circle{fill:var(--graph-bg); stroke:var(--graph)}
.n.agent.hl rect{fill:#D9D6FF; stroke-width:2.4}
.n.code rect,.n.code polygon{fill:var(--code-bg); stroke:var(--code)}
.n.verify rect{fill:var(--ok-bg); stroke:var(--ok)}
.n.human rect,.n.human polygon{fill:var(--hum-bg); stroke:var(--hum)}
.n.loopn rect{fill:var(--loop-bg); stroke:var(--loop)}
.n.io rect{fill:var(--ink); stroke:var(--ink)} .n.io text{fill:#fff}
.n.io2 rect{fill:var(--ink); stroke:var(--ink)} .n.io2 text{fill:#fff}
.n.ghost rect{fill:none; stroke:var(--graph); stroke-dasharray:4 3} .n.ghost text{fill:var(--graph); font-weight:500}
.n.badn rect{fill:var(--bad-bg); stroke:var(--bad)}
.n text.sub{font-family:"IBM Plex Mono",monospace; font-size:9.6px; font-weight:400; fill:var(--mut)}
.e{fill:none; stroke:var(--ink); stroke-width:1.5}
.e.thin{stroke-width:1.2} .e.lp{stroke:var(--loop); stroke-width:1.8}
.e.retry{stroke:var(--loop); stroke-dasharray:6 4; stroke-width:1.7}
.e.good{stroke:var(--ok)} .e.bad{stroke:var(--bad)}
.lg{fill:none; stroke:var(--loop); stroke-width:1.5}
text.el{font-family:"IBM Plex Mono",monospace; font-size:10.3px; font-weight:400; fill:var(--mut)}
text.el.retry,text.el.lp{fill:var(--loop)} text.el.good{fill:var(--ok)} text.el.bad{fill:var(--bad)}
text.ctr{font-size:13px; font-weight:650; fill:var(--loop)} text.ctr2{font-family:"IBM Plex Mono"; font-size:10.5px; font-weight:400; fill:var(--mut)}
.brace{fill:none; stroke:var(--ok); stroke-width:1.3}
.statebar{fill:#fff; stroke:var(--ink); stroke-width:1.4}
text.sblbl{font-family:"IBM Plex Mono"; font-size:9.5px; letter-spacing:.14em; fill:var(--mut); font-weight:500}
text.sbtxt{font-family:"IBM Plex Mono"; font-size:11.5px; font-weight:500}
path.dot{stroke:#9AA0AE; stroke-width:1.2; stroke-dasharray:2 4; fill:none}
text.zlbl{font-family:"IBM Plex Mono"; font-size:10.5px; letter-spacing:.12em; fill:var(--mut); font-weight:500}
text.zmath{font-family:"IBM Plex Serif"; font-size:19px; font-style:italic; font-weight:500}
.sep{stroke:var(--rule); stroke-width:1.2} .proj{stroke:var(--graph); stroke-width:1; stroke-dasharray:3 4; fill:none}
.inside{fill:#fff; stroke:var(--graph); stroke-width:1.6}
.badge circle{fill:var(--ink)} .badge text{fill:#fff; font-size:11px; font-weight:700}
.ckp{fill:#fff; stroke:var(--graph); stroke-width:2}

/* cover */
.page.cover{background:#0F1117; color:#E9EAF2; padding:0 0 0 72px; flex-direction:row; align-items:center}
.cover .cv-l{flex:1; padding-right:20px}
.cover .kicker{color:#9BA1FF; margin-bottom:26px}
.cover h1{font-size:104px; line-height:.94; letter-spacing:-.045em; font-weight:800; color:#fff}
.cv-sub{font-family:"IBM Plex Serif",serif; font-size:23px; line-height:1.38; color:#C4C7D6; margin-top:30px; max-width:520px}
.cv-meta{display:flex; flex-wrap:wrap; gap:8px; margin-top:38px}
.cv-meta span{font-family:"IBM Plex Mono"; font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:#A9AEC2; border:1px solid #30364A; border-radius:999px; padding:6px 12px}
.cover .cv-r{width:620px; height:720px; background:#141722; display:flex; align-items:center; justify-content:center; border-left:1px solid #232838}

/* p2 */
.takeaways{list-style:none; counter-reset:t; display:flex; flex-direction:column; gap:13px}
.takeaways li{counter-increment:t; position:relative; padding:0 0 13px 50px; border-bottom:1px solid var(--rule); font-size:14.6px; line-height:1.48; color:#30343D}
.takeaways li:last-child{border:0; padding-bottom:0}
.takeaways li::before{content:counter(t); position:absolute; left:0; top:-2px; width:34px; height:34px; border-radius:50%; background:var(--graph); color:#fff;
  font-weight:700; font-size:15px; display:flex; align-items:center; justify-content:center}
.takeaways b{color:var(--ink)}

/* p3 */
.nest{border:1.6px solid; border-radius:16px; padding:34px 14px 14px; position:relative}
.nest > span{position:absolute; top:9px; left:15px; font-family:"IBM Plex Mono"; font-size:11px; letter-spacing:.1em; text-transform:uppercase; font-weight:600}
.nest.n5{border-color:var(--graph); background:var(--graph-bg)} .n5 > span{color:var(--graph)}
.nest.n4{border-color:var(--loop); background:var(--loop-bg)} .n4 > span{color:var(--loop)}
.nest.n3{border-color:var(--code); background:var(--code-bg)} .n3 > span{color:var(--code)}
.nest.n2{border-color:#8A8F9C; background:#F7F4EE} .n2 > span{color:#6B7080}
.nest.n1{border-color:var(--ink); background:#fff; padding:30px 14px 22px} .n1 > span{color:var(--ink)}
.tbl{width:100%; border-collapse:collapse}
.tbl th{font-family:"IBM Plex Mono"; font-size:10.5px; letter-spacing:.1em; text-transform:uppercase; color:var(--mut); font-weight:500; text-align:left; padding:0 14px 9px 0; border-bottom:1.5px solid var(--ink)}
.tbl td{padding:10px 14px 10px 0; border-bottom:1px solid var(--rule); font-size:13.6px; vertical-align:top; color:#30343D; line-height:1.4}
.lname{display:block; font-weight:700; font-size:15.5px; color:var(--ink)} .lera{font-family:"IBM Plex Mono"; font-size:10.5px; color:var(--mut)}
tr.l5 .lname{color:var(--graph)} tr.l4 .lname{color:var(--loop)}
tr.l5 td{background:linear-gradient(90deg, rgba(67,56,202,.07), transparent)}
.layers td:first-child{padding-left:10px}

/* timeline */
.timeline{display:grid; grid-template-columns:repeat(6,1fr); gap:0; position:relative; padding-top:6px}
.timeline::before{content:""; position:absolute; top:12px; left:0; right:0; height:2px; background:var(--rule)}
.era{padding:0 14px 0 0; position:relative}
.era .dot{width:14px; height:14px; border-radius:50%; background:var(--paper); border:2.5px solid var(--ink); margin-bottom:12px; position:relative}
.era.e5 .dot{background:var(--graph); border-color:var(--graph)} .era.e5 h3{color:var(--graph)}
.era .when{font-family:"IBM Plex Mono"; font-size:10.5px; letter-spacing:.06em; text-transform:uppercase; color:var(--mut); margin-bottom:4px}
.era h3{font-size:16.5px; margin-bottom:8px}
.era p{font-size:12.6px} .era .works{font-family:"IBM Plex Mono"; font-size:10.8px; line-height:1.5; color:var(--mut); margin-bottom:8px; min-height:calc(64px * var(--fs))}

/* walls */
.card.wall svg{margin:4px 0 8px} .sym{font-size:12.9px; line-height:1.48; color:#30343D; border-left:3px solid var(--loop); padding-left:12px}
.sym b{display:block; color:var(--ink); font-size:13.6px}
/* debts */
.card.debt{padding:20px 22px} .bignum{font-family:"Inter Display"; font-size:46px; font-weight:800; color:var(--loop); line-height:1; margin-bottom:8px; letter-spacing:-.03em}
.card.debt h3{font-size:19px; margin-bottom:8px} .card.debt p{font-size:13.8px}
.tell,.fix{font-size:12.8px; line-height:1.45; margin-top:12px; padding-top:10px; border-top:1px solid var(--rule); color:#30343D}
.tell span,.fix span{display:block; font-family:"IBM Plex Mono"; font-size:10px; letter-spacing:.1em; text-transform:uppercase; margin-bottom:2px}
.tell span{color:var(--bad)} .fix span{color:var(--ok)}
/* defs */
.card.def{padding:14px 16px 14px; flex:1} .card.def p{font-size:13px}
.letter{font-family:"IBM Plex Serif"; font-style:italic; font-size:30px; font-weight:600; line-height:1; margin-bottom:6px}
.def.v .letter,.cv{color:var(--graph)} .def.e .letter,.ce{color:var(--ink)} .def.s .letter,.cs{color:var(--ok)} .def.c .letter,.cc{color:var(--hum)}
.formula{font-family:"IBM Plex Serif"; font-style:italic; font-size:30px; letter-spacing:.01em} .formula b{font-weight:600}
/* versus */
.card.versus{padding:18px 22px} .card.versus h3{font-size:21px} .versus.a{border-top:3px solid var(--graph)} .versus.b{border-top:3px solid #8A8F9C}
.versus.a .tag{color:var(--graph)}
.versus .q{font-family:"IBM Plex Serif"; font-style:italic; font-size:15px; margin:4px 0 10px; color:var(--ink)}
dl{display:grid; grid-template-columns:calc(116px * var(--fs)) 1fr; row-gap:6px; font-size:13.2px}
dt{font-family:"IBM Plex Mono"; font-size:10.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--mut); padding-top:2px} dd{color:#30343D}
.kg{background:#fff; border:1px solid var(--rule); border-radius:12px; padding:12px 16px}
.kgrow{font-size:12.8px; display:flex; gap:10px; align-items:baseline; padding:3px 0; color:#30343D}
.kgrow span{font-family:"IBM Plex Mono"; font-weight:600; font-size:12px; width:86px; flex:none}
.up{color:var(--ok)} .dn{color:var(--bad)}
/* cmp */
.cmp td{padding:7.5px 14px 7.5px 0; font-size:13.4px} .cmp th{font-family:"Inter"; font-size:15px; letter-spacing:0; text-transform:none; font-weight:700; padding-bottom:10px}
.cmp th em{font-family:"IBM Plex Mono"; font-style:normal; font-weight:400; font-size:10.5px; color:var(--mut); margin-left:8px; letter-spacing:.04em}
td.dim{font-family:"IBM Plex Mono"; font-size:10.8px; letter-spacing:.07em; text-transform:uppercase; color:var(--mut); padding-top:10px}
.cmp tr:last-child td{background:#EFEBE3; font-weight:600; color:var(--ink); border-bottom:0} .cmp tr:last-child td:first-child{padding-left:10px; border-radius:8px 0 0 8px}
.cmp tr:last-child td:last-child{border-radius:0 8px 8px 0}
/* patterns */
.pats{gap:12px} .card.pat{padding:12px 16px 12px} .pathead{display:flex; align-items:center; gap:9px; margin-bottom:4px}
.pn{width:22px; height:22px; border-radius:50%; background:var(--ink); color:#fff; font-size:12px; font-weight:700; display:flex; align-items:center; justify-content:center; flex:none}
.card.pat h3{margin:0} .card.pat svg{margin:2px auto 6px} .card.pat p{font-size:12.6px; line-height:1.42}
.pat .when{margin-top:4px; color:var(--graph)} .pat .when b{font-family:"IBM Plex Mono"; font-size:10px; letter-spacing:.08em; text-transform:uppercase; font-weight:500; margin-right:3px}
/* example */
.steps{gap:12px} .step{font-size:12.5px; line-height:1.45; color:#30343D; padding-left:30px; position:relative}
.step b{display:block; color:var(--ink); font-size:13px}
.bn{position:absolute; left:0; top:0; width:21px; height:21px; border-radius:50%; background:var(--ink); color:#fff; font-size:11px; font-weight:700; display:flex; align-items:center; justify-content:center}
/* contract */
.six{list-style:none; display:grid; grid-template-columns:1fr 1fr; gap:10px 22px}
.six li{display:flex; gap:12px; padding:11px 0; border-top:1px solid var(--rule); font-size:13.4px; line-height:1.42; color:#30343D}
.six b{display:block; color:var(--ink); font-size:14.8px; margin-bottom:1px}
.k{width:26px; height:26px; border-radius:8px; background:var(--graph); color:#fff; font-weight:700; font-size:13px; display:flex; align-items:center; justify-content:center; flex:none}
.spec{background:#12141B; color:#DADDEA; border-radius:16px; padding:6px 0 10px; font-family:"IBM Plex Mono"; font-size:12px; box-shadow:0 14px 40px rgba(20,22,30,.18)}
.spechead{padding:12px 20px; border-bottom:1px solid #2A2F3F; color:#fff; font-size:14px; font-weight:600}
.spechead span{color:#9BA1FF; font-weight:400; margin-right:6px} .spechead i{float:right; font-style:normal; font-size:10px; letter-spacing:.12em; text-transform:uppercase; color:#7D8399; font-weight:400; padding-top:3px}
.specrow{display:grid; grid-template-columns:92px 1fr; padding:9px 20px; border-bottom:1px solid #20242F; line-height:1.5}
.specrow > span{color:#FF9D66; font-size:11px; letter-spacing:.04em}
.specrow code{background:#222738; border-radius:5px; padding:1px 6px; color:#C9CCFF; font-size:11.5px; margin-right:3px; white-space:nowrap}
.specrow em{display:block; font-style:normal; color:#8D93A8; font-size:10.8px; margin-top:3px}
.specfoot{padding:9px 20px 2px; color:#6F7589; font-size:10.5px}
/* state */
.card.plain{padding:14px 16px} .card.plain p{font-size:12.6px; margin-top:6px}
.card.center{text-align:center} .card.center svg{margin:6px auto}
pre.code{font-family:"IBM Plex Mono"; font-size:11.4px; line-height:1.55; background:#12141B; color:#DADDEA; border-radius:10px; padding:10px 14px; white-space:pre; overflow:hidden}
pre.code b{color:#fff} pre.code i{font-style:normal; color:#A5ABFF} pre.code .cm{color:#7D8399}
.super{padding-left:18px; font-size:12.6px; line-height:1.45; color:#30343D; margin-bottom:8px} .super li{margin-bottom:4px} .super b{color:var(--ink)}
/* stats */
.stat{background:#fff; border:1px solid var(--rule); border-radius:14px; padding:18px 22px}
.stat .num{font-family:"Inter Display"; font-size:62px; font-weight:800; letter-spacing:-.04em; line-height:1}
.stat.good .num{color:var(--ok)} .stat.bad .num{color:var(--bad)} .stat h3{margin:8px 0 6px; font-size:16.5px}
.sig{font-size:13px; line-height:1.45; color:#30343D; border-left:3px solid var(--graph); padding-left:12px} .sig b{color:var(--ink); margin-right:4px}
/* bars */
.bar{display:grid; grid-template-columns:48px 150px 1fr; align-items:center; gap:10px; margin:5px 0; font-size:12.6px}
.bl{font-family:"IBM Plex Mono"; font-size:11px; color:var(--mut)} .bt{height:12px; background:#F0EDE6; border-radius:6px; overflow:hidden; display:block}
.bt i{display:block; height:100%; border-radius:6px} .bv{color:#30343D}
.rule{background:var(--graph); color:#fff; border-radius:12px; padding:14px 18px; font-size:15.5px; line-height:1.45; font-weight:500}
.rule .lbl{color:#C9CCFF; margin-bottom:5px}
.ineq{font-family:"IBM Plex Mono"; font-size:11.8px; font-weight:400; margin-top:10px; padding-top:9px; border-top:1px solid rgba(255,255,255,.25); color:#E3E4FF} .ineq b{color:#fff}
/* lists */
.colhead{font-family:"IBM Plex Mono"; font-size:11px; letter-spacing:.1em; text-transform:uppercase; font-weight:600; padding-bottom:8px; border-bottom:2px solid}
.colhead.bad{color:var(--bad); border-color:var(--bad)} .colhead.good{color:var(--ok); border-color:var(--ok)}
.list{list-style:none} .list li{padding:8px 0 8px 0; border-bottom:1px solid var(--rule); font-size:13.1px; line-height:1.44; color:#30343D}
.list li b{display:block; color:var(--ink); font-size:14px}
.list.num li{display:flex; gap:12px} .list.num .k{background:var(--ok)} .list.num b{display:block}
/* ladder */
.ladder{display:flex; flex-direction:column; gap:6px}
.rung{background:#fff; border:1px solid var(--rule); border-left:4px solid var(--graph); border-radius:9px; padding:7px 14px; font-size:12.8px; display:flex; gap:12px; align-items:baseline}
.rung b{font-size:13.6px; white-space:nowrap} .rung span{color:#454A57}
.qs{list-style:none; font-family:"IBM Plex Serif"; font-style:italic; font-size:14.6px; line-height:1.4} .qs li{padding:4px 0; border-bottom:1px dashed var(--rule)} .qs li:last-child{border:0}
/* decide */
.decide td{padding:9.5px 18px 9.5px 0; font-size:14px} .decide th{padding-bottom:10px}
.hd{font-family:"Inter"; text-transform:none; letter-spacing:0; font-size:15.5px; font-weight:700; padding:4px 12px; border-radius:8px; color:#fff; display:inline-block}
.hd.loop{background:var(--loop)} .hd.graph{background:var(--graph)}
/* hand */
.hstep{background:#fff; border:1px solid var(--rule); border-radius:14px; padding:16px 16px 18px}
.hn{font-family:"Inter Display"; font-size:40px; font-weight:800; color:var(--graph); line-height:1; margin-bottom:10px; letter-spacing:-.03em}
.hstep h3{margin-bottom:6px; font-size:16px} .hstep p{font-size:13px}
/* stages */
.stages{display:grid; grid-template-columns:repeat(5,1fr); gap:0}
.stage{padding:0 18px 0 0; position:relative; border-top:3px solid var(--graph); padding-top:16px; margin-right:6px}
.stage::after{content:""; position:absolute; top:-9px; right:-8px; border-left:10px solid var(--graph); border-top:7.5px solid transparent; border-bottom:7.5px solid transparent}
.sn{font-family:"IBM Plex Mono"; font-size:10.5px; letter-spacing:.1em; text-transform:uppercase; color:var(--graph); font-weight:500}
.stage h3{font-size:21px; margin:4px 0 8px; letter-spacing:-.02em} .stage p{font-size:13.2px; min-height:calc(132px * var(--fs))}
.sx{font-size:12px; line-height:1.45; color:#454A57; background:#fff; border:1px solid var(--rule); border-radius:10px; padding:9px 11px; margin-top:10px; min-height:calc(98px * var(--fs))}
/* tools */
.card.tool h3{font-size:18px} .card.tool.graph .tag{color:var(--graph)} .card.tool.code{border-top:3px solid var(--code)}
/* oq */
.card.oq{padding:16px 18px 16px 56px} .qm{position:absolute; left:16px; top:12px; font-family:"IBM Plex Serif"; font-size:34px; font-weight:600; color:var(--hum); line-height:1}
/* dark */
.page.dark{background:#0F1117; color:#E9EAF2} .dark .kicker{color:#9BA1FF} .dark h1{color:#fff}
.dark footer{color:#6F7589} .dark .prog i{background:#2A2F3F} .dark .prog i.on{background:#9BA1FF}
.rules{list-style:none; display:grid; grid-template-columns:1fr 1fr; grid-template-rows:repeat(5,auto); grid-auto-flow:column; column-gap:44px}
.rules li{display:flex; gap:16px; align-items:baseline; padding:13px 0; border-bottom:1px solid #262B3A; font-size:16.5px; line-height:1.38; color:#E9EAF2; font-weight:500}
.rules span{font-family:"IBM Plex Mono"; font-size:12px; color:#FF9D66; flex:none}
.closing{font-family:"IBM Plex Serif"; font-size:16.5px; line-height:1.5; color:#B9BDCF; margin-top:22px; max-width:1040px} .closing b{color:#fff; font-weight:600}
/* sources */
.srcs{gap:8px 40px} .srcg ul{list-style:none} .srcg li{font-size:12.3px; line-height:1.42; color:#30343D; padding:4.5px 0; border-bottom:1px solid var(--rule)}
.srcg .lbl{color:var(--graph); margin-bottom:4px; margin-top:6px}
.tall .card{height:100%}
"""

DEFS = ('<svg width="0" height="0" style="position:absolute"><defs>'
        '<marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">'
        '<path d="M0 0.8L10 5L0 9.2z" fill="context-stroke"/></marker>'
        '<marker id="ahs" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse">'
        '<path d="M0 0L10 5L0 10z" fill="context-stroke"/></marker></defs></svg>')

def scale_css(css):
    """Make HTML text sizes scale with the per-page --fs variable; SVG label sizes stay fixed."""
    skip = ("text.", ".n text", "svg text", ".badge", ".cover", ".cv-", "h1{", ".page.cover", "footer", ".prog", ".kicker")
    out = []
    for line in css.splitlines():
        if not line.strip().startswith(skip):
            line = re.sub(r"font-size:([\d.]+)px", r"font-size:calc(\1px * var(--fs))", line)
        out.append(line)
    return "\n".join(out)

# Per-page text scale, tuned so each page fills its frame without overflowing.
FS = {4: 1.16, 7: 1.1, 10: 1.1, 12: 1.04, 13: 1.02, 14: 1.22, 15: 1.06, 16: 1.15, 18: 1.1, 19: 1.06,
      20: 1.18, 22: 1.1, 23: 1.22, 24: 1.2, 26: 1.2, 27: 1.22, 28: 1.1}

def foot(i, total, part):
    segs = "".join(f'<i class="{"on" if j == part else ""}"></i>' for j in range(len(PARTS)))
    return (f'<footer><span>Graph Engineering · A field guide</span>'
            f'<span class="prog">{segs}<span>{PARTS[part]}</span></span><span>{i:02d} / {total:02d}</span></footer>')

def render():
    total = len(pages)
    out = []
    for i, p in enumerate(pages, 1):
        fs = FS.get(i, 1.12)
        if "raw" in p:
            raw = p["raw"].replace('<section class="page', f'<section style="--fs:{fs}" class="page', 1)
            out.append(raw.replace("__FOOT__", foot(i, total, 5)))
            continue
        p["fs"] = fs
        lede = f'<p class="lede">{p["lede"]}</p>' if p["lede"] else ""
        out.append(f'<section class="page {p["cls"]}" style="--fs:{p["fs"]}"><header><div class="kicker">{p["kicker"]}</div>'
                   f'<h1>{p["title"]}</h1>{lede}</header><div class="body">{p["body"]}</div>{foot(i, total, p["part"])}</section>')
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<title>Graph Engineering: A Field Guide for Agentic Coders</title>'
            f'<style>{scale_css(CSS)}</style></head><body>{DEFS}{"".join(out)}</body></html>')

def main():
    HTML.write_text(render(), encoding="utf-8")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, executable_path=CHROME)
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        pg.goto(HTML.as_uri())
        pg.evaluate("document.fonts.ready")
        over = pg.evaluate("""() => [...document.querySelectorAll('.page')].map((p,i)=>{
            const b=p.querySelector('.body'); if(!b) return null;
            const kids=[...b.children]; const last=kids[kids.length-1];
            const bottom=Math.max(...kids.map(k=>k.getBoundingClientRect().bottom))-p.getBoundingClientRect().top;
            const limit=b.getBoundingClientRect().bottom-p.getBoundingClientRect().top;
            const wide=[...p.querySelectorAll('*')].some(e=>e.getBoundingClientRect().right-p.getBoundingClientRect().left>1218);
            return {page:i+1, slack:Math.round(limit-bottom), wide};
        }).filter(Boolean)""")
        for o in over:
            flag = "  <-- OVERFLOW" if o["slack"] < 0 else ("  (wide)" if o["wide"] else "")
            print(f'page {o["page"]:02d} slack {int(o["slack"]):4d}px{flag}')
        pg.pdf(path=str(PDF), width="1280px", height="720px", print_background=True, prefer_css_page_size=True)
        b.close()
    print("wrote", PDF)

if __name__ == "__main__":
    sys.exit(main())
