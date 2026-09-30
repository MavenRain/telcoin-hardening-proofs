#!/usr/bin/env python3
"""Adversarial regression checks for the source-disposition gate."""
import copy
from pathlib import Path
import runpy
import unittest

validate = runpy.run_path(str(Path(__file__).with_name("dispositions.py")))["validate"]
PIN = "a" * 64


class DispositionChecks(unittest.TestCase):
    def setUp(self):
        self.units = [
            {"source": "sources/w1/example.md", "lines": [1, 1], "sha256": "b" * 64},
            {"source": "sources/w1/example.md", "lines": [2, 2], "sha256": "c" * 64},
            {"source": "sources/w1-modified/example.md", "lines": [1, 1], "sha256": "d" * 64},
            {"source": "sources/w1/example.md", "lines": [3, 3], "sha256": "e" * 64},
        ]
        self.ledger = {"version": 1, "source_manifest_sha256": PIN, "units": [], "obligations": []}
        for index, unit in enumerate(self.units, 1):
            self.ledger["units"].append(unit | {"id": f"U{index:04}", "disposition": "context",
                                               "obligations": [], "reconciles": [],
                                               "rationale": "A source section label."})
        for name, kind in (("M001", "model"), ("E001", "external")):
            self.ledger["obligations"].append({
                "id": name, "kind": kind, "workstream": "W1", "closure_packet": "R08",
                "property": "Preserve the stated boundary.", "required_scope": "All relevant traces.",
                "acceptance_criteria": ["Audited evidence satisfies the source clause."],
                "required_evidence": ["The exact witness and scope."],
                "candidate_atoms": ["A1"] if kind == "model" else [],
            })
        self.ledger["units"][1].update(disposition="obligation", obligations=["M001"],
                                        reconciles=["U0003"], rationale="The modified plan retains this clause.")
        self.ledger["units"][2].update(disposition="obligation", obligations=["M001", "E001"],
                                        rationale="Separate the symbolic rule from runtime qualification.")
        self.ledger["units"][3].update(disposition="superseded", reconciles=["U0003"],
                                        rationale="The revised acceptance replaces the earlier clause.")

    def check(self):
        return validate(self.units, self.ledger, PIN, {"A1"}, {"R08": {"W1"}})

    def reject(self, message):
        with self.assertRaises(ValueError) as caught:
            self.check()
        self.assertIn(message, str(caught.exception))

    def test_recorded_dispositions_do_not_credit_candidates_as_proofs(self):
        report = self.check()
        self.assertTrue(report["complete"])
        self.assertEqual((report["model_obligations"], report["external_obligations"]), (1, 1))
        self.assertNotIn("model_checked", report)

    def test_pending_unit_blocks_closure(self):
        self.ledger["units"][0].update(disposition="pending", rationale="")
        report = self.check()
        self.assertFalse(report["complete"])
        self.assertEqual(report["pending_units"], 1)

    def test_removed_unit_is_rejected(self):
        self.ledger["units"].pop()
        self.reject("exactly once")

    def test_duplicate_unit_is_rejected(self):
        self.ledger["units"][3] = copy.deepcopy(self.ledger["units"][0])
        self.reject("missing, duplicated or reordered")

    def test_reordered_units_are_rejected(self):
        self.ledger["units"][0], self.ledger["units"][1] = self.ledger["units"][1], self.ledger["units"][0]
        self.reject("missing, duplicated or reordered")

    def test_changed_unit_text_is_rejected(self):
        self.ledger["units"][0]["sha256"] = "f" * 64
        self.reject("source disposition pin is stale")

    def test_changed_source_range_is_rejected(self):
        self.ledger["units"][0]["lines"] = [1, 2]
        self.reject("source disposition pin is stale")

    def test_boolean_line_number_cannot_alias_one(self):
        self.ledger["units"][0]["lines"] = [True, 1]
        self.reject("source disposition pin is stale")

    def test_changed_manifest_is_rejected(self):
        self.ledger["source_manifest_sha256"] = "f" * 64
        self.reject("manifest pin is stale")

    def test_missing_review_rationale_is_rejected(self):
        self.ledger["units"][0]["rationale"] = " "
        self.reject("disposition rationale")

    def test_unknown_disposition_is_rejected(self):
        self.ledger["units"][0]["disposition"] = "approved"
        self.reject("invalid source disposition")

    def test_unknown_obligation_is_rejected(self):
        self.ledger["units"][2]["obligations"].append("M999")
        self.reject("missing or invalid obligation links")

    def test_unreferenced_obligation_is_rejected(self):
        self.ledger["obligations"].append(self.ledger["obligations"][0] | {"id": "M002"})
        self.reject("unreferenced obligation")

    def test_duplicate_obligation_is_rejected(self):
        self.ledger["obligations"].append(copy.deepcopy(self.ledger["obligations"][0]))
        self.reject("invalid or duplicate source obligation identity")

    def test_duplicate_obligation_link_is_rejected(self):
        self.ledger["units"][2]["obligations"] = ["M001", "E001", "M001"]
        self.reject("invalid U0003 obligations references")

    def test_duplicate_reconciliation_link_is_rejected(self):
        self.ledger["units"][1]["reconciles"] = ["U0003", "U0003"]
        self.reject("invalid U0002 reconciliations references")

    def test_duplicate_candidate_atom_is_rejected(self):
        self.ledger["obligations"][0]["candidate_atoms"] = ["A1", "A1"]
        self.reject("invalid M001 candidate atoms references")

    def test_context_cannot_consume_an_obligation(self):
        self.ledger["units"][0]["obligations"] = ["M001"]
        self.reject("missing or invalid obligation links")

    def test_pending_cannot_consume_an_obligation(self):
        self.ledger["units"][1].update(disposition="pending", rationale="", reconciles=[])
        self.reject("missing or invalid obligation links")

    def test_pending_unit_cannot_carry_reconciliation_links(self):
        # U0003 is an audited modified-plan target, so only the pending guard rejects this link.
        self.ledger["units"][0].update(disposition="pending", rationale="", reconciles=["U0003"])
        self.reject("unaudited or context unit has reconciliation links")

    def test_context_unit_cannot_carry_reconciliation_links(self):
        self.ledger["units"][0]["reconciles"] = ["U0003"]
        self.reject("unaudited or context unit has reconciliation links")

    def test_original_requirement_needs_reconciliation(self):
        self.ledger["units"][1]["reconciles"] = []
        self.reject("has no modified-plan reconciliation")

    def test_original_requirement_cannot_reconcile_to_itself(self):
        self.ledger["units"][1]["reconciles"] = ["U0002"]
        self.reject("missing or unaudited reconciliation target")

    def test_original_requirement_cannot_reconcile_to_an_original_clause(self):
        self.ledger["units"][1]["reconciles"] = ["U0004"]
        self.reject("reconciliation target is not a modified-plan unit")

    def test_modified_clause_cannot_reconcile_to_an_original_clause(self):
        self.units.append({"source": "sources/w1-modified/example.md", "lines": [2, 2], "sha256": "f" * 64})
        self.ledger["units"].append(self.units[-1] | {"id": "U0005", "disposition": "superseded",
                                                      "obligations": [], "reconciles": ["U0002"],
                                                      "rationale": "The original clause replaces this revision."})
        self.reject("reconciliation target is not a modified-plan unit")

    def test_modified_requirement_cannot_retain_an_original_clause(self):
        self.units.append({"source": "sources/w1-modified/example.md", "lines": [2, 2], "sha256": "f" * 64})
        self.ledger["units"].append(self.units[-1] | {"id": "U0005", "disposition": "obligation",
                                                      "obligations": ["E001"], "reconciles": ["U0002"],
                                                      "rationale": "The revision cites the original clause."})
        self.reject("reconciliation target is not a modified-plan unit")

    def test_superseded_clause_needs_a_replacement(self):
        self.ledger["units"][3]["reconciles"] = []
        self.reject("has no replacement")

    def test_superseded_clause_cannot_point_to_context(self):
        self.ledger["units"][3]["reconciles"] = ["U0001"]
        self.reject("missing or unaudited reconciliation target")

    def test_replacement_cannot_be_unaudited(self):
        self.ledger["obligations"] = [row for row in self.ledger["obligations"] if row["id"] != "E001"]
        self.ledger["units"][2].update(disposition="pending", obligations=[], rationale="")
        self.reject("missing or unaudited reconciliation target")

    def test_unknown_replacement_is_rejected(self):
        self.ledger["units"][3]["reconciles"] = ["U9999"]
        self.reject("missing or unaudited reconciliation target")

    def test_reconciliation_cannot_drop_a_retained_model_obligation(self):
        self.ledger["units"][2]["obligations"] = ["E001"]
        self.reject("drops retained obligations")

    def test_malformed_obligation_kind_is_rejected(self):
        self.ledger["obligations"][0]["kind"] = []
        self.reject("invalid or duplicate source obligation identity")

    def test_cyclic_reconciliation_is_rejected(self):
        # Two modified clauses keep this cycle independent of the modified-plan target guard.
        self.units[3]["source"] = "sources/w1-modified/example.md"
        self.ledger["units"][3]["source"] = self.units[3]["source"]
        self.ledger["units"][2]["reconciles"] = ["U0004"]
        self.reject("cyclic source reconciliation")

    def test_missing_acceptance_evidence_is_rejected(self):
        self.ledger["obligations"][0]["required_evidence"] = []
        self.reject("required_evidence")

    def test_unknown_candidate_atom_is_rejected(self):
        self.ledger["obligations"][0]["candidate_atoms"] = ["unknown"]
        self.reject("invalid candidate proof links")

    def test_external_requirement_cannot_claim_model_candidates(self):
        self.ledger["obligations"][1]["candidate_atoms"] = ["A1"]
        self.reject("invalid candidate proof links")

    def test_unknown_closure_packet_is_rejected(self):
        self.ledger["obligations"][0]["closure_packet"] = "R99"
        self.reject("invalid obligation closure assignment")

    def test_unassigned_workstream_is_rejected(self):
        self.ledger["obligations"][0]["workstream"] = "W0"
        self.reject("invalid obligation closure assignment")

    def test_user_supplied_complete_flag_is_rejected(self):
        self.ledger["complete"] = True
        self.reject("invalid source ledger fields")

    def test_empty_inventory_cannot_claim_complete(self):
        self.units = []
        self.ledger["units"] = []
        self.ledger["obligations"] = []
        self.reject("exactly once")


if __name__ == "__main__":
    unittest.main()
