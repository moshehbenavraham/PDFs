#!/usr/bin/env python3
"""Tests for validate_plan.py.  Run:  python3 scripts/test_validate_plan.py"""
import copy
import json
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from validate_plan import validate  # noqa: E402

EXAMPLE = json.loads((HERE.parent / "references" / "example-plan.json").read_text(encoding="utf-8"))


def node(plan, nid):
    return next(n for n in plan["nodes"] if n["id"] == nid)


class ValidatePlan(unittest.TestCase):
    def setUp(self):
        self.plan = copy.deepcopy(EXAMPLE)

    def assertError(self, fragment):
        errors, _ = validate(self.plan)
        self.assertTrue(any(fragment in e for e in errors), f"expected an error containing {fragment!r}, got {errors}")

    def test_example_plan_is_clean(self):
        self.assertEqual(validate(self.plan), ([], []))

    def test_undefined_input_node(self):
        node(self.plan, "prioritize")["inputs"] = ["nowhere.clusters"]
        self.assertError("undefined node")

    def test_input_field_must_be_an_output(self):
        node(self.plan, "prioritize")["inputs"] = ["cluster_findings.themes"]
        self.assertError("not among the outputs")

    def test_input_without_edge(self):
        self.plan["edges"] = [e for e in self.plan["edges"] if (e["from"], e["to"]) != ("prioritize", "draft_email")]
        self.assertError("no edge prioritize -> draft_email")

    def test_edge_needs_reason(self):
        self.plan["edges"][0]["reason"] = " "
        self.assertError("reason is required")

    def test_edge_to_undefined_node(self):
        self.plan["edges"].append({"from": "read_handler", "to": "audit_endpoint", "reason": "x"})
        self.assertError("both ends must be defined nodes")

    def test_cycle(self):
        self.plan["edges"].append({"from": "prioritize", "to": "cluster_findings", "reason": "retry"})
        self.assertError("dependency cycle")

    def test_irreversible_needs_direct_gate(self):
        self.plan["edges"] = [e for e in self.plan["edges"] if e["from"] != "approve_send"]
        node(self.plan, "send_email")["inputs"] = ["draft_email"]
        self.assertError("must depend directly on a human_approval node")

    def test_irreversible_never_in_subagent(self):
        node(self.plan, "send_email")["executor"] = "subagent"
        self.assertError("never in a subagent")

    def test_ungated_and_unverified_send_warns(self):
        self.plan["nodes"] = [n for n in self.plan["nodes"] if n["id"] != "verify_critical"]
        self.plan["edges"] = [e for e in self.plan["edges"] if "verify_critical" not in (e["from"], e["to"])]
        self.plan["phases"] = [p for p in self.plan["phases"] if p["nodes"] != ["verify_critical"]]
        node(self.plan, "draft_email")["inputs"] = ["prioritize.remediation_plan"]
        errors, warnings = validate(self.plan)
        self.assertEqual(errors, [])
        self.assertTrue(any("no verification node upstream" in w for w in warnings))

    def test_tier_is_not_a_model_id(self):
        node(self.plan, "audit_endpoint")["tier"] = "some-model-id"
        self.assertError("never a model id")

    def test_node_missing_from_phases(self):
        self.plan["phases"].pop()
        self.assertError("not assigned to any phase")

    def test_phase_order_follows_edges(self):
        self.plan["phases"][7]["nodes"], self.plan["phases"][8]["nodes"] = ["send_email"], ["approve_send"]
        self.assertError("must run in a later phase")

    def test_same_phase_dependency(self):
        self.plan["phases"][3]["nodes"] = ["cluster_findings", "prioritize"]
        self.plan["phases"].pop(4)
        self.assertError("must run in a later phase")

    def test_consolidation_arithmetic(self):
        self.plan["consolidation"]["layers"][0]["outputs"] = 4
        self.assertError("gives 3 outputs, not 4")

    def test_consolidation_must_end_in_one(self):
        self.plan["consolidation"]["layers"].pop()
        self.assertError("must produce 1 output")

    def test_oversized_layer_warns(self):
        self.plan["consolidation"]["layers"] = [{"inputs": 60, "batch_size": 60, "outputs": 1}]
        errors, warnings = validate(self.plan)
        self.assertEqual(errors, [])
        self.assertTrue(any("above 30" in w for w in warnings))

    def test_schema_doc_excerpt_matches_example(self):
        """The JSON shown in plan-schema.md must stay identical to the real example plan."""
        doc = (HERE.parent / "references" / "plan-schema.md").read_text(encoding="utf-8")
        excerpt = json.loads(doc.split("```json", 1)[1].split("```", 1)[0])
        for n in excerpt["nodes"]:
            self.assertEqual(n, node(EXAMPLE, n["id"]))
        for key in ("edges", "phases"):
            for item in excerpt[key]:
                self.assertIn(item, EXAMPLE[key])
        for key in ("consolidation", "verification"):
            self.assertEqual(excerpt[key], EXAMPLE[key])

    def test_markdown_links_resolve(self):
        import re
        root = HERE.parent
        for md in [root / "SKILL.md", root / "README.md", root / "CHANGES.md", *sorted((root / "references").glob("*.md"))]:
            text = md.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)#\s]+)", text):
                if "://" not in target:
                    self.assertTrue((md.parent / target).exists(), f"{md.name}: broken link {target}")
            if md.name == "SKILL.md":
                for target in re.findall(r"`((?:references|scripts)/[\w./-]+)`", text):
                    self.assertTrue((root / target).exists(), f"SKILL.md: missing {target}")

    def test_not_an_object(self):
        self.assertEqual(validate([])[0], ["plan must be a JSON object"])


if __name__ == "__main__":
    unittest.main()
