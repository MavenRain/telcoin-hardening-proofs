#!/usr/bin/env python3
"""Reject scope weakening and distinguish source closure from proof coverage."""
import copy
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
catalog = runpy.run_path(str(ROOT / "tools/catalog.py"))
scope = runpy.run_path(str(ROOT / "tools/scope.py"))


class ScopeChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = catalog["inventory"]()
        cls.source_ledger = catalog["load"](ROOT / "source-ledger.json")
        cls.source_seal = catalog["load"](ROOT / "proof-scope.json")

    def setUp(self):
        self.data = copy.deepcopy(self.inventory)
        self.ledger = copy.deepcopy(self.source_ledger)
        self.seal = copy.deepcopy(self.source_seal)

    def reject(self, message):
        with self.assertRaises(ValueError) as caught:
            scope["validate"](ROOT, self.data, self.ledger, self.seal)
        self.assertIn(message, str(caught.exception))

    def test_seal_does_not_credit_proofs_or_external_results(self):
        result = scope["validate"](ROOT, self.data, self.ledger, self.seal)
        self.assertTrue(result["source_scope_sealed"])
        self.assertFalse(result["proof_witnesses_audited"])
        self.assertFalse(result["external_obligations_closed"])
        self.assertNotIn("model_checked", result)
        self.assertEqual((result["original_tracking_ids"], result["decisions"]), (102, 12))

    def test_pending_dispositions_block_the_seal(self):
        self.data["semantically_complete"] = False
        self.reject("pending dispositions")

    def test_pending_count_cannot_hide_behind_complete_flags(self):
        self.data["dispositions"]["pending_units"] = 1
        self.reject("pending dispositions")

    def test_missing_workstream_is_rejected(self):
        self.seal["workstreams"].pop()
        self.reject("workstream")

    def test_stale_manifest_is_rejected(self):
        self.seal["source_manifest_sha256"] = "0" * 64
        self.reject("manifest pin")

    def test_stale_ledger_is_rejected(self):
        self.seal["source_ledger_sha256"] = "0" * 64
        self.reject("ledger pin")

    def test_property_scope_kind_and_packet_changes_require_new_baseline(self):
        baseline = copy.deepcopy(self.ledger)
        for field, value in (("property", "Only a closed example."),
                             ("required_scope", "One source, one swarm."),
                             ("kind", "external"), ("closure_packet", "R08")):
            with self.subTest(field=field):
                self.ledger = copy.deepcopy(baseline)
                model = next(row for row in self.ledger["obligations"] if row["kind"] == "model")
                model[field] = value
                self.reject("obligations changed")

    def test_removed_obligation_is_rejected(self):
        self.ledger["obligations"].pop()
        self.reject("obligations changed")

    def test_census_cannot_omit_an_obligation(self):
        self.seal["obligation_ids"].pop()
        self.reject("obligation census")

    def test_duplicate_census_entry_is_rejected(self):
        self.seal["obligation_ids"].append(self.seal["obligation_ids"][0])
        self.reject("obligation census")

    def test_tracking_requirement_cannot_become_context(self):
        unit = self.seal["tracking"][0]["unit"]
        next(row for row in self.ledger["units"] if row["id"] == unit)["disposition"] = "context"
        self.reject("normative scope row")

    def test_missing_tracking_or_decision_link_is_rejected(self):
        baseline = copy.deepcopy(self.seal)
        for key in ("tracking", "decisions"):
            with self.subTest(key=key):
                self.seal = copy.deepcopy(baseline)
                self.seal[key].pop()
                self.reject("tracking or decision links")

    def test_reassigned_tracking_unit_is_rejected(self):
        self.seal["tracking"][0]["unit"] = self.seal["tracking"][1]["unit"]
        self.reject("tracking or decision links")

    def test_missing_boundary_is_rejected(self):
        self.seal["boundary"] = " "
        self.reject("proof boundary")

    def test_closed_r01_accepts_audited_source_scope_with_proof_coverage_open(self):
        with tempfile.TemporaryDirectory(prefix="telcoin-r01-gate-") as directory:
            root = Path(directory).resolve()
            files = ("claims.json", "atomic-claims.json", "source-ledger.json", "proof-scope.json",
                     "sources/manifest.json", "tools/scope.py",
                     "sources/w1-modified/03-RATIONALE-AND-CROSSWALK.md",
                     "sources/w1-modified/04-DECISIONS-AND-ACCEPTANCE.md")
            for relative in files:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)
            plan = catalog["load"](ROOT / "proof-roadmap.json")
            first = plan["packets"][0]
            first["status"] = "closed"
            first["evidence"] = [{"criterion": index, "path": relative,
                                  "sha256": hashlib.sha256((root / relative).read_bytes()).hexdigest()}
                                 for index, relative in enumerate(("source-ledger.json", "proof-scope.json", "tools/scope.py"))]
            (root / "proof-roadmap.json").write_text(json.dumps(plan))
            probe = runpy.run_path(str(ROOT / "tools/catalog.py"))["proof_plan"]
            probe.__globals__["ROOT"] = root
            result = probe(self.data)
            self.assertGreaterEqual(result["closed_packets"], 1)
            self.assertFalse(catalog["load"](ROOT / "atomic-claims.json")["coverage_complete"])
            self.data["semantically_complete"] = False
            with self.assertRaisesRegex(ValueError, "pending dispositions"):
                probe(self.data)
            self.data["semantically_complete"] = True
            (root / "proof-scope.json").write_text(json.dumps(self.seal | {"source_ledger_sha256": "0" * 64}))
            first["evidence"][1]["sha256"] = hashlib.sha256((root / "proof-scope.json").read_bytes()).hexdigest()
            (root / "proof-roadmap.json").write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, "ledger pin"):
                probe(self.data)


if __name__ == "__main__":
    unittest.main()
