# Machine-Readable Plan Format

Emit this **only** when the plan is being handed to an external runner: a scheduler, a CI job, another agent. For a human reader it's noise; use the markdown phase plan in SKILL.md instead.

Important: nothing in this schema executes on its own. Fields like `batch_size` are instructions *to a runner you have written*. If no such runner exists, omit them rather than emitting values that imply a scheduler is enforcing them.

## A complete example

[`example-plan.json`](example-plan.json) is a full plan for "audit all 60 endpoint handlers for auth issues and email the verified critical findings". It is the same run shown in the README and in `best-practices.md`, and it passes the validator below. Start from it rather than from a blank file.

## Check a plan before handing it off

```bash
python3 scripts/validate_plan.py plan.json
```

Run from the skill directory. Python 3 standard library only. The script reads one JSON file and prints findings; it never executes a plan. Exit status 0 means no errors. Fix every error before handing the plan to a runner, and read the warnings.

It checks what is easy to get wrong by hand:

- every `inputs` reference names a defined node, and a field that node actually outputs
- every data dependency has an edge, and every edge has a reason
- no dependency cycles, and every node sits in exactly one phase that comes after everything it depends on
- every irreversible node is inline and depends directly on a `human_approval` node
- consolidation arithmetic: each layer's outputs match its inputs and batch size, layers chain, the last one produces 1
- tiers are tier names, not model IDs

## Shape

```json
{
  "goal": "One-sentence statement of what done looks like",
  "nodes": [
    {
      "id": "audit_endpoint",
      "description": "Read one endpoint handler and classify its auth posture against the rubric",
      "inputs": ["read_middleware.auth_defaults", "read_middleware.rubric"],
      "outputs": ["endpoint_id", "auth_mode", "severity", "evidence"],
      "cardinality": 60,
      "executor": "subagent",
      "tier": "standard"
    },
    {
      "id": "approve_send",
      "kind": "human_approval",
      "description": "Show the human the exact email, its one recipient and that it cannot be recalled",
      "inputs": ["draft_email"],
      "outputs": ["decision", "reason"],
      "executor": "inline"
    },
    {
      "id": "send_email",
      "description": "Send the approved email",
      "irreversible": true,
      "inputs": ["approve_send.decision", "draft_email"],
      "outputs": ["message_id"],
      "executor": "inline"
    }
  ],
  "edges": [
    { "from": "read_middleware", "to": "audit_endpoint", "reason": "Each handler is classified relative to the middleware defaults and the rubric" }
  ],
  "phases": [
    { "phase": 2, "mode": "parallel", "nodes": ["audit_endpoint"], "batch_size": 10 }
  ],
  "consolidation": {
    "layers": [
      { "inputs": 60, "batch_size": 20, "outputs": 3 },
      { "inputs": 3, "batch_size": 3, "outputs": 1 }
    ],
    "completeness_check": "received == expected at every layer, list any missing by endpoint_id"
  },
  "verification": {
    "method": "re-derive from source in a fresh context",
    "scope": "every finding marked critical"
  }
}
```

This excerpt shows one node of each kind. It is not a complete plan on its own; the full version is in `example-plan.json`.

## Field notes

| Field | Required | Meaning |
|---|---|---|
| `goal` | yes | One sentence saying what done looks like. |
| `nodes[].id` | yes | Unique. No `.` in the id. |
| `nodes[].description` | yes | The node's single job. |
| `nodes[].inputs` | no | List of `node_id` or `node_id.field`. |
| `nodes[].outputs` | yes | The named fields the node returns. |
| `nodes[].cardinality` | no, default 1 | How many instances run. |
| `nodes[].executor` | yes | `"inline"` or `"subagent"`. |
| `nodes[].tier` | for subagents | `"fast"`, `"standard"` or `"strongest"`. |
| `nodes[].kind` | no, default `"work"` | `"work"`, `"verification"` or `"human_approval"`. |
| `nodes[].irreversible` | no, default false | `true` for sends, deploys, deletes, production writes. |
| `edges[]` | when anything depends on anything | `from`, `to`, `reason`. |
| `phases[]` | yes | `phase` (integer), `mode` (`"parallel"` or `"sequential"`), `nodes`, optional `batch_size`. |
| `consolidation` | when a fan-out exceeds 30 items | `layers` and `completeness_check`. |
| `verification` | for high-stakes output | `method` and `scope`. |

**`inputs` and `edges` say the same thing twice, on purpose.** Every node an `inputs` entry reads from must also appear as an edge with a reason. Edges may additionally carry *hidden* dependencies that move no data: a shared file write, an interface change that must land first. Those have an edge and a reason but no matching input.

**`outputs`**: name the fields each node returns, not just "a summary." Uniform output shape across a cardinality group is what makes fan-in cheap.

**`cardinality`**: how many instances of this node run. Lets a runner size batches without inspecting inputs.

**`edges.reason`**: required, and not bureaucratic. Writing the reason is what catches phantom edges. If you can't articulate what flows across it, there's probably no edge.

**`batch_size`**: cap it at whatever the binding constraint is (API rate limit, context budget), not at an aspirational number.

**`executor`**: irreversible nodes, human approval gates and final synthesis are always `"inline"`; high-cardinality independent nodes are usually `"subagent"`.

**`tier`**: a tier name, never a model ID, since model IDs rot. Let the runner resolve the tier. Strongest is reserved for fresh-context verification of high-stakes output.

**Human gates**: an irreversible action and its approval are two separate nodes. The gate has `"kind": "human_approval"`. The action has `"irreversible": true` and lists the gate among its `inputs`, so there is a direct edge from gate to action. A runner that can't pause for approval must not be handed a plan containing one.

**Retries are not edges.** The graph is acyclic. A failed verification leads to a capped redo of the affected nodes (see "Verification" in SKILL.md); it is not drawn as an edge pointing backwards.

**Omit rather than fabricate.** No `timeout_seconds` unless something enforces timeouts. No `retry` unless something retries. A spec that describes infrastructure you don't have is worse than a shorter honest one. It invites everyone downstream, including the model reading it, to assume guarantees that aren't there.
