#!/usr/bin/env python3
"""Check a machine-readable plan against references/plan-schema.md.

Usage:  python3 scripts/validate_plan.py plan.json
        python3 scripts/validate_plan.py -        (read the plan from stdin)

Standard library only. It reads one JSON file and prints findings; it never
executes a plan, calls a network, or writes anything.

Exit status: 0 = no errors (warnings may be printed), 1 = errors, 2 = unreadable input.
"""
import json
import math
import sys

EXECUTORS = {"inline", "subagent"}
TIERS = {"fast", "standard", "strongest"}
KINDS = {"work", "verification", "human_approval"}
MODES = {"parallel", "sequential"}
MAX_LAYER = 30  # SKILL.md: consolidate in layers of 20 to 30 items


def validate(plan):
    """Return (errors, warnings) for a parsed plan."""
    errors, warnings = [], []
    if not isinstance(plan, dict):
        return ["plan must be a JSON object"], warnings

    if not isinstance(plan.get("goal"), str) or not plan["goal"].strip():
        errors.append("goal: required, one sentence saying what done looks like")

    # ---- nodes -------------------------------------------------------------
    nodes = {}
    raw_nodes = plan.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        return errors + ["nodes: required, a non-empty list"], warnings
    for i, n in enumerate(raw_nodes):
        if not isinstance(n, dict) or not isinstance(n.get("id"), str) or not n["id"]:
            errors.append(f"nodes[{i}]: every node needs a string id")
            continue
        nid = n["id"]
        if "." in nid:
            errors.append(f"node {nid}: ids may not contain '.', it separates node from field in inputs")
        if nid in nodes:
            errors.append(f"node {nid}: duplicate id")
            continue
        nodes[nid] = n

    def kind(nid):
        return nodes[nid].get("kind", "work")

    for nid, n in nodes.items():
        if not isinstance(n.get("description"), str) or not n["description"].strip():
            errors.append(f"node {nid}: description is required")
        outs = n.get("outputs")
        if not isinstance(outs, list) or not outs or not all(isinstance(o, str) and o for o in outs):
            errors.append(f"node {nid}: outputs must name the fields it returns")
        if not isinstance(n.get("inputs", []), list):
            errors.append(f"node {nid}: inputs must be a list")
        card = n.get("cardinality", 1)
        if not isinstance(card, int) or isinstance(card, bool) or card < 1:
            errors.append(f"node {nid}: cardinality must be a positive integer")
        if n.get("executor") not in EXECUTORS:
            errors.append(f"node {nid}: executor must be one of {sorted(EXECUTORS)}")
        if "tier" in n and n["tier"] not in TIERS:
            errors.append(f"node {nid}: tier must be one of {sorted(TIERS)}, never a model id")
        if n.get("executor") == "subagent" and "tier" not in n:
            warnings.append(f"node {nid}: subagent node has no tier")
        if kind(nid) not in KINDS:
            errors.append(f"node {nid}: kind must be one of {sorted(KINDS)}")
        if "irreversible" in n and not isinstance(n["irreversible"], bool):
            errors.append(f"node {nid}: irreversible must be true or false")
        if n.get("irreversible") is True and n.get("executor") == "subagent":
            errors.append(f"node {nid}: irreversible actions run inline, never in a subagent")
        if kind(nid) == "human_approval" and n.get("executor") == "subagent":
            errors.append(f"node {nid}: a human approval gate runs inline")
        if kind(nid) == "human_approval" and n.get("irreversible") is True:
            errors.append(f"node {nid}: the approval gate and the irreversible action must be separate nodes")

    # ---- edges -------------------------------------------------------------
    edge_set = set()
    raw_edges = plan.get("edges", [])
    if not isinstance(raw_edges, list):
        errors.append("edges: must be a list")
        raw_edges = []
    for i, e in enumerate(raw_edges):
        if not isinstance(e, dict):
            errors.append(f"edges[{i}]: must be an object")
            continue
        a, b = e.get("from"), e.get("to")
        label = f"edge {a} -> {b}"
        if a not in nodes or b not in nodes:
            errors.append(f"{label}: both ends must be defined nodes")
            continue
        if a == b:
            errors.append(f"{label}: a node cannot depend on itself")
        if not isinstance(e.get("reason"), str) or not e["reason"].strip():
            errors.append(f"{label}: reason is required; if nothing flows across it, there is no edge")
        if (a, b) in edge_set:
            warnings.append(f"{label}: listed more than once")
        edge_set.add((a, b))

    # every input reference must name a defined node and field, and have an edge
    for nid, n in nodes.items():
        for ref in n.get("inputs", []) if isinstance(n.get("inputs", []), list) else []:
            if not isinstance(ref, str) or not ref:
                errors.append(f"node {nid}: inputs must be strings like 'node_id' or 'node_id.field'")
                continue
            src, _, field = ref.partition(".")
            if src not in nodes:
                errors.append(f"node {nid}: input '{ref}' refers to an undefined node")
                continue
            if field and field not in (nodes[src].get("outputs") or []):
                errors.append(f"node {nid}: input '{ref}' is not among the outputs of {src}")
            if (src, nid) not in edge_set and src != nid:
                errors.append(f"node {nid}: reads {src} but there is no edge {src} -> {nid}")

    # ---- cycles ------------------------------------------------------------
    preds = {nid: set() for nid in nodes}
    for a, b in edge_set:
        if a != b:
            preds[b].add(a)
    remaining = {nid: set(p) for nid, p in preds.items()}
    while True:
        ready = [nid for nid, p in remaining.items() if not p]
        if not ready:
            break
        for nid in ready:
            del remaining[nid]
        for p in remaining.values():
            p.difference_update(ready)
    if remaining:
        errors.append("edges: dependency cycle among " + ", ".join(sorted(remaining))
                      + "; model retries as a capped redo of the affected nodes, not as an edge")

    def ancestors(nid):
        seen, stack = set(), list(preds[nid])
        while stack:
            cur = stack.pop()
            if cur not in seen:
                seen.add(cur)
                stack.extend(preds[cur])
        return seen

    # ---- gates -------------------------------------------------------------
    for nid, n in nodes.items():
        if n.get("irreversible") is True:
            gates = [p for p in preds[nid] if kind(p) == "human_approval"]
            if not gates:
                errors.append(f"node {nid}: irreversible, so it must depend directly on a human_approval node")
            if not remaining and not any(kind(a) == "verification" for a in ancestors(nid)):
                warnings.append(f"node {nid}: irreversible with no verification node upstream")
        if kind(nid) == "human_approval" and not any(nodes[b].get("irreversible") is True
                                                    for a, b in edge_set if a == nid):
            warnings.append(f"node {nid}: approval gate does not guard any irreversible node")

    # ---- phases ------------------------------------------------------------
    phase_of = {}
    raw_phases = plan.get("phases")
    if not isinstance(raw_phases, list) or not raw_phases:
        errors.append("phases: required, a non-empty list")
        raw_phases = []
    seen_numbers = set()
    for i, ph in enumerate(raw_phases):
        if not isinstance(ph, dict):
            errors.append(f"phases[{i}]: must be an object")
            continue
        num = ph.get("phase")
        if not isinstance(num, int) or isinstance(num, bool):
            errors.append(f"phases[{i}]: phase must be an integer")
            continue
        if num in seen_numbers:
            errors.append(f"phase {num}: listed more than once")
        seen_numbers.add(num)
        if ph.get("mode") not in MODES:
            errors.append(f"phase {num}: mode must be one of {sorted(MODES)}")
        if "batch_size" in ph and (not isinstance(ph["batch_size"], int) or isinstance(ph["batch_size"], bool)
                                   or ph["batch_size"] < 1):
            errors.append(f"phase {num}: batch_size must be a positive integer")
        members = ph.get("nodes")
        if not isinstance(members, list) or not members:
            errors.append(f"phase {num}: nodes must be a non-empty list")
            continue
        for nid in members:
            if nid not in nodes:
                errors.append(f"phase {num}: '{nid}' is not a defined node")
            elif nid in phase_of:
                errors.append(f"node {nid}: appears in more than one phase")
            else:
                phase_of[nid] = num
    if raw_phases:
        for nid in nodes:
            if nid not in phase_of:
                errors.append(f"node {nid}: not assigned to any phase")
        for a, b in sorted(edge_set):
            if a in phase_of and b in phase_of and phase_of[a] >= phase_of[b]:
                errors.append(f"edge {a} -> {b}: {b} (phase {phase_of[b]}) must run in a later phase "
                              f"than {a} (phase {phase_of[a]})")

    # ---- consolidation -----------------------------------------------------
    cons = plan.get("consolidation")
    if cons is not None:
        layers = cons.get("layers") if isinstance(cons, dict) else None
        if not isinstance(layers, list) or not layers:
            errors.append("consolidation.layers: must be a non-empty list")
        else:
            prev = None
            for i, layer in enumerate(layers):
                vals = [layer.get(k) if isinstance(layer, dict) else None for k in ("inputs", "batch_size", "outputs")]
                if not all(isinstance(v, int) and not isinstance(v, bool) and v >= 1 for v in vals):
                    errors.append(f"consolidation.layers[{i}]: inputs, batch_size and outputs must be positive integers")
                    prev = None
                    continue
                inputs, batch, outputs = vals
                if outputs != math.ceil(inputs / batch):
                    errors.append(f"consolidation.layers[{i}]: {inputs} inputs in batches of {batch} "
                                  f"gives {math.ceil(inputs / batch)} outputs, not {outputs}")
                if prev is not None and inputs != prev:
                    errors.append(f"consolidation.layers[{i}]: takes {inputs} inputs but the previous layer produced {prev}")
                if batch > MAX_LAYER:
                    warnings.append(f"consolidation.layers[{i}]: batch_size {batch} is above {MAX_LAYER}; "
                                    "detail thins out in large fan-ins")
                prev = outputs
            if prev is not None and prev != 1:
                errors.append(f"consolidation: the last layer must produce 1 output, not {prev}")
        if isinstance(cons, dict) and not cons.get("completeness_check"):
            errors.append("consolidation.completeness_check: required; count received against expected")
    elif any(isinstance(n.get("cardinality"), int) and n.get("cardinality", 1) > MAX_LAYER for n in nodes.values()):
        warnings.append(f"a node fans out to more than {MAX_LAYER} items but the plan has no consolidation section")

    ver = plan.get("verification")
    if ver is not None and (not isinstance(ver, dict) or not ver.get("method") or not ver.get("scope")):
        errors.append("verification: needs both method and scope")

    return errors, warnings


def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        return 0 if len(argv) == 2 else 2
    try:
        text = sys.stdin.read() if argv[1] == "-" else open(argv[1], encoding="utf-8").read()
        plan = json.loads(text)
    except (OSError, ValueError) as exc:
        print(f"cannot read plan: {exc}", file=sys.stderr)
        return 2
    errors, warnings = validate(plan)
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    if errors:
        print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    count = len(plan["nodes"])
    print(f"ok: {count} nodes, {len(plan.get('edges', []))} edges, {len(plan['phases'])} phases, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
