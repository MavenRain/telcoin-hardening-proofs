#!/usr/bin/env python3
"""Reject witness-audit weakening, stale evidence and unsupported closure credit."""
import copy
import hashlib
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
catalog = runpy.run_path(str(ROOT / "tools/catalog.py"))
auditor = runpy.run_path(str(ROOT / "tools/audit.py"))


class AuditChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = catalog["load"](ROOT / "proof-audit.json")
        cls.source_ledger = catalog["load"](ROOT / "source-ledger.json")
        cls.source_seal = catalog["load"](ROOT / "proof-scope.json")
        cls.inventory = catalog["inventory"]()

    def setUp(self):
        self.data = copy.deepcopy(self.source)
        self.ledger = copy.deepcopy(self.source_ledger)
        self.seal = copy.deepcopy(self.source_seal)

    def row(self, name="M004"):
        return next(row for row in self.data["obligations"] if row["id"] == name)

    def validate(self):
        return auditor["validate"](ROOT, self.ledger, self.seal, self.data)

    def reject(self, message):
        with self.assertRaises(ValueError) as caught:
            self.validate()
        self.assertIn(message, str(caught.exception))

    def test_audited_model_coverage_does_not_close_external_obligations(self):
        result = self.validate()
        self.assertEqual((result["model_obligations"], result["reviewed_obligations"],
                          result["covered_obligations"], result["partial_obligations"],
                          result["unreviewed_obligations"]), (83, 83, 8, 75, 0))
        self.assertEqual(result["unaudited_criteria"], 0)
        self.assertTrue(result["witness_audit_complete"])
        self.assertFalse(result["model_coverage_complete"])
        self.assertFalse(result["external_obligations_closed"])
        self.assertNotIn("model_checked", result)
        self.assertEqual(len(result["remaining"]), 75)
        self.assertEqual(set(result["witness_scope_counts"]),
                         {"arbitrary_trace", "general_transition", "conditional_liveness", "finite_example"})

    def test_census_uses_the_existing_explicit_proof_classifier(self):
        source = "\n".join(path.read_text() for path in sorted((ROOT / "proofs").glob("*.mech")))
        self.assertEqual(self.validate()["proof_declarations"], len(catalog["theorem_names"](source)))

    def test_sealed_inputs_are_pinned(self):
        for field, message in (("proof_scope_sha256", "scope pin"), ("source_ledger_sha256", "ledger pin")):
            with self.subTest(field=field):
                self.data = copy.deepcopy(self.source)
                self.data[field] = "0" * 64
                self.reject(message)

    def test_frozen_requirement_cannot_be_rewritten(self):
        model = next(row for row in self.ledger["obligations"] if row["id"] == "M004")
        model["required_scope"] = "One held slot only."
        self.reject("sealed obligations changed")

    def test_changed_missing_or_added_corpus_module_is_rejected(self):
        name = next(iter(self.data["corpus_sha256"]))
        for operation in ("changed", "missing", "added"):
            with self.subTest(operation=operation):
                self.data = copy.deepcopy(self.source)
                if operation == "changed":
                    self.data["corpus_sha256"][name] = "0" * 64
                elif operation == "missing":
                    self.data["corpus_sha256"].pop(name)
                else:
                    self.data["corpus_sha256"]["proofs/99-unreviewed.mech"] = "0" * 64
                self.reject("proof corpus")

    def test_missing_duplicate_or_external_obligation_is_rejected(self):
        for operation in ("missing", "duplicate", "external"):
            with self.subTest(operation=operation):
                self.data = copy.deepcopy(self.source)
                if operation == "missing":
                    self.data["obligations"].pop()
                elif operation == "duplicate":
                    self.data["obligations"].append(copy.deepcopy(self.data["obligations"][0]))
                else:
                    self.data["obligations"][0]["id"] = "E001"
                self.reject("obligation census")

    def test_proof_gap_keeps_its_sealed_packet(self):
        self.row()["closure_packet"] = "R08"
        self.reject("reassigned closure packet")

    def test_missing_duplicate_reordered_or_boolean_criterion_is_rejected(self):
        for operation in ("missing", "duplicate", "reordered", "boolean"):
            with self.subTest(operation=operation):
                self.data = copy.deepcopy(self.source)
                criteria = self.row()["criteria"]
                if operation == "missing":
                    criteria.pop()
                elif operation == "duplicate":
                    criteria.append(copy.deepcopy(criteria[0]))
                elif operation == "reordered":
                    criteria.reverse()
                else:
                    criteria[0]["index"] = False
                self.reject("criterion census")

    def test_helper_unknown_path_or_duplicate_witness_cannot_receive_proof_credit(self):
        for operation in ("helper", "unknown_path", "duplicate"):
            with self.subTest(operation=operation):
                self.data = copy.deepcopy(self.source)
                witnesses = self.row()["witnesses"]
                if operation == "helper":
                    witnesses[0]["name"] = "tryReserve"
                elif operation == "unknown_path":
                    witnesses[0]["path"] = "../proofs/21-pending-lifecycle.mech"
                else:
                    witnesses.append(copy.deepcopy(witnesses[0]))
                self.reject("proof witness")

    def test_statement_and_premises_are_required(self):
        self.row()["witnesses"][0]["statement"] = "Equal Count zero zero"
        self.reject("changed witness statement")
        self.data = copy.deepcopy(self.source)
        self.row()["witnesses"][0]["premises"] = []
        self.reject("witness premises")

    def test_closed_example_cannot_be_relabeled_general(self):
        self.row("M013")["witnesses"][1]["scope_kind"] = "arbitrary_trace"
        self.reject("closed statement labeled general")

    def test_closed_statement_with_any_head_cannot_be_labeled_general(self):
        real = auditor["corpus"]
        witness = self.row()["witnesses"][0]
        key = f"{witness['path']}#{witness['name']}"

        def corpus(root):
            pins, statements = real(root)
            return pins, {**statements, key: "NotRefunded zero"}

        witness["statement"] = "NotRefunded zero"
        with patch.dict(auditor["validate"].__globals__, {"corpus": corpus}):
            self.reject("closed statement labeled general")

    def test_finite_example_alone_cannot_witness_a_criterion(self):
        row = self.row("M013")
        item = row["criteria"][1]
        finite = row["witnesses"][1]
        item.update(status="witnessed", remaining="", witnesses=[f"{finite['path']}#{finite['name']}"])
        self.reject("finite examples cannot close")

    def test_criterion_cannot_cite_an_unrecorded_witness(self):
        self.row()["criteria"][0]["witnesses"] = ["proofs/21-pending-lifecycle.mech#freeReservationOwnsSlot"]
        self.reject("unknown criterion witness")

    def test_witness_cannot_be_unassigned(self):
        self.row()["criteria"][0].update(status="gap", witnesses=[],
                                           remaining="Missing complete saturation evidence.")
        self.reject("not assigned to a criterion")

    def test_gap_requires_exact_remaining_work(self):
        self.row()["criteria"][0].update(status="gap", remaining="")
        self.reject("remaining criterion work")

    def test_complete_flag_cannot_hide_unresolved_criteria(self):
        self.row("M009")["scope_complete"] = True
        self.reject("unresolved criteria")

    def test_general_local_witnesses_do_not_imply_full_scope_credit(self):
        self.row()["scope_complete"] = False
        covered = self.validate()["covered_obligations"]
        self.row()["criteria"][0].update(status="witnessed", remaining="")
        result = self.validate()
        self.assertEqual(result["covered_obligations"], covered)
        self.assertEqual(next(row["status"] for row in result["remaining"]
                              if row["id"] == "M004"), "partial")

    def test_witnessed_criterion_requires_evidence_and_empty_remaining_work(self):
        for operation in ("missing", "remaining"):
            with self.subTest(operation=operation):
                self.data = copy.deepcopy(self.source)
                item = self.row()["criteria"][1]
                if operation == "missing":
                    item["witnesses"] = []
                else:
                    item["remaining"] = "Still missing the full scope."
                self.reject("witnessed criterion lacks evidence")

    def test_unknown_duplicate_or_changed_control_is_rejected(self):
        for operation in ("unknown", "duplicate", "changed"):
            with self.subTest(operation=operation):
                self.data = copy.deepcopy(self.source)
                control = self.row()["controls"][0]
                if operation == "unknown":
                    control["name"] = "unregistered_control"
                elif operation == "duplicate":
                    self.row()["controls"].append(copy.deepcopy(control))
                else:
                    control["sha256"] = "0" * 64
                self.reject("semantic control")

    def test_full_scope_credit_requires_weakening_controls(self):
        row = self.row()
        row["criteria"][0].update(status="witnessed", remaining="")
        row.update(scope_complete=True, controls=[])
        self.reject("lacks weakening controls")

    def test_unreviewed_record_cannot_receive_credit(self):
        self.row()["reviewed"] = False
        self.reject("unreviewed obligation receives credit")
        self.data = copy.deepcopy(self.source)
        row = self.row()
        row.update(reviewed=False, scope_complete=False, scope_review="", witnesses=[], controls=[])
        for item in row["criteria"]:
            item.update(status="unreviewed", witnesses=[], remaining="Audit this criterion against its sealed scope.")
        row["criteria"][0]["status"] = "gap"
        self.reject("unreviewed criterion receives credit")

    def test_complete_audit_requires_every_criterion_reviewed(self):
        for row in self.data["obligations"]:
            row.update(reviewed=True, scope_review="Required scope still needs audit.")
        self.row("M056")["criteria"][0]["status"] = "unreviewed"
        result = self.validate()
        self.assertEqual(result["unreviewed_obligations"], 0)
        self.assertEqual(result["unaudited_criteria"], 1)
        self.assertFalse(result["witness_audit_complete"])

    def test_unknown_fields_cannot_force_complete_status(self):
        self.data["model_coverage_complete"] = True
        self.reject("audit fields")

    def test_R02_cannot_close_with_unaudited_criteria(self):
        self.row("M056")["criteria"][0]["status"] = "unreviewed"
        inventory = self.inventory | {"witness_audit": self.validate()}
        original_load = catalog["load"]
        plan = original_load(ROOT / "proof-roadmap.json")
        packet = plan["packets"][1]
        packet["status"] = "closed"
        pin = hashlib.sha256((ROOT / "proof-audit.json").read_bytes()).hexdigest()
        packet["evidence"] = [{"criterion": index, "path": "proof-audit.json", "sha256": pin}
                              for index in range(len(packet["exit_criteria"]))]
        def load(path):
            return plan if path.name == "proof-roadmap.json" else original_load(path)
        with patch.dict(catalog["proof_plan"].__globals__, {"load": load}):
            with self.assertRaisesRegex(ValueError, "R02 witness audit is incomplete"):
                catalog["proof_plan"](inventory)

    def test_complete_witness_audit_can_close_R02_with_remaining_model_gaps(self):
        original_load = catalog["load"]
        plan = original_load(ROOT / "proof-roadmap.json")
        packet = plan["packets"][1]
        packet["status"] = "closed"
        pin = hashlib.sha256((ROOT / "proof-audit.json").read_bytes()).hexdigest()
        packet["evidence"] = [{"criterion": index, "path": "proof-audit.json", "sha256": pin}
                              for index in range(len(packet["exit_criteria"]))]
        def load(path):
            return plan if path.name == "proof-roadmap.json" else original_load(path)
        with patch.dict(catalog["proof_plan"].__globals__, {"load": load}):
            self.assertEqual(catalog["proof_plan"](self.inventory)["packets"][1]["status"], "closed")
        self.assertFalse(self.inventory["witness_audit"]["model_coverage_complete"])

    def test_unknown_scope_or_status_value_is_rejected(self):
        self.row()["witnesses"][0]["scope_kind"] = "fully_proved"
        self.reject("invalid witness scope")
        self.data = copy.deepcopy(self.source)
        self.row()["criteria"][0]["status"] = "approved"
        self.reject("invalid criterion status")

    def test_audit_version_or_scope_cannot_change(self):
        for field, value in (("version", 2), ("version", True), ("scope", "other")):
            with self.subTest(field=field, value=value):
                self.data = copy.deepcopy(self.source)
                self.data[field] = value
                self.reject("invalid witness audit version or scope")

    def test_witness_and_criterion_text_is_required(self):
        for target, field in (("witness", "establishes"), ("witness", "limits"), ("criterion", "rationale")):
            with self.subTest(field=field):
                self.data = copy.deepcopy(self.source)
                record = self.row()["witnesses"][0] if target == "witness" else self.row()["criteria"][0]
                record[field] = ""
                self.reject(f"{target} {field}")

    def test_duplicate_criterion_witness_or_non_list_controls_is_rejected(self):
        criterion = self.row()["criteria"][1]
        criterion["witnesses"] = criterion["witnesses"] * 2
        self.reject("invalid criterion witnesses")
        self.data = copy.deepcopy(self.source)
        self.row()["controls"] = {}
        self.reject("invalid semantic controls")


if __name__ == "__main__":
    unittest.main(verbosity=2)
