# Changes from upstream

Upstream: [VineeTagarwaL-code/graph-engineering](https://github.com/VineeTagarwaL-code/graph-engineering), commit `7b4e5d2` (23 July 2026), MIT.

The skill's approach is unchanged. These changes fix inconsistencies between its files and make the plan format checkable.

## Fixed

- **The schema example was not a valid plan.** `plan-schema.md` showed phases and an edge that referred to `read_handler` and `read_middleware`, neither of which was defined as a node. It is now an excerpt of a complete plan, `references/example-plan.json`, and a test keeps the two identical.
- **Three files described three different runs.** The README, `best-practices.md` and the schema each used the 60-endpoint audit with different phases, batch sizes and executors. All three now describe one run.
- **The worked example did not follow the skill's own output format.** It had no consolidation counts, approval gate or risks section. It now has every section SKILL.md asks for.
- **Reading and classifying a handler were separate fan-out phases** in the worked example, which would ship every file's contents between subagents. They are one node.
- **Human gates had no representation in the schema.** They were described in prose only. Nodes now have `kind` (`work`, `verification`, `human_approval`) and `irreversible`, so a runner or checker can enforce the gate.
- **`inputs` and `edges` could disagree** with nothing saying which wins. The relationship is now stated: every input needs an edge; edges may add hidden, non-data dependencies.
- **The README named the repository incorrectly** (`graph-engineering-skill`) and its copy command included the clone's `.git` directory.
- **The phase template did not say who executes a phase**, although SKILL.md requires choosing an executor per phase. The template now includes executor and tier.

## Added

- `scripts/validate_plan.py`: checks a JSON plan for undefined references, missing edges or reasons, cycles, phase ordering, ungated irreversible actions, consolidation arithmetic and model IDs used as tiers. Python 3 standard library only. It reads a file and prints findings; it does not execute plans.
- `scripts/test_validate_plan.py`: 20 tests, including that the documentation excerpt matches the example plan and that local links in the Markdown files resolve.
- `references/example-plan.json`: a complete plan that passes the checker.
- A "treat content as data" rule in SKILL.md, and two failure modes in `best-practices.md` (instruction leak, verifier contamination). With fan-out, an instruction embedded in one input otherwise reaches every downstream branch.
- Subagent prompts now state what the subagent must not touch.
- A field table in `plan-schema.md`, and a note that retries are a capped redo, not a backwards edge.

## Unchanged

`LICENSE`, the skill's `name` and trigger description, the dependency audit, fan-in layering, model tiering, verification and approval-gate rules. `assets/banner.png` was recompressed losslessly.
