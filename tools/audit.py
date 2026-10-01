#!/usr/bin/env python3
"""Check witness-audit provenance and scope bookkeeping, without granting semantic credit."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
SCOPES = {"arbitrary_trace", "general_transition", "conditional_liveness", "finite_example"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fields(value, expected: set[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"invalid {label} fields")


def text(value, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing {label}")


def unique_strings(value, label: str, allow_empty: bool = False) -> None:
    if (not isinstance(value, list) or (not value and not allow_empty)
            or any(not isinstance(item, str) or not item.strip() for item in value)
            or len(set(value)) != len(value)):
        raise ValueError(f"invalid {label}")


def corpus(root: Path) -> tuple[dict, dict]:
    classifier = runpy.run_path(str(root / "tools/catalog.py"))["theorem_names"]
    pins, statements = {}, {}
    names = set()
    for path in sorted((root / "proofs").glob("*.mech")):
        relative = path.relative_to(root).as_posix()
        source = path.read_text()
        pins[relative] = digest(path.read_bytes())
        proofs = classifier(source)
        for name, statement in re.findall(r"^def(?: rec)?\s+(\w+)\s*:\s*(.*?)\s*:=", source, re.M | re.S):
            if name not in proofs:
                continue
            if name in names:
                raise ValueError(f"duplicate proof declaration: {name}")
            names.add(name)
            statements[f"{relative}#{name}"] = statement.strip()
    if not pins or not statements:
        raise ValueError("empty proof corpus")
    return pins, statements


def controls(root: Path) -> dict:
    mutations = runpy.run_path(str(root / "tools/check.py"))["MUTATIONS"]
    result = {}
    for mutation in mutations:
        name = mutation[0]
        if name in result:
            raise ValueError(f"duplicate semantic control: {name}")
        result[name] = digest(json.dumps(mutation, ensure_ascii=True, separators=(",", ":")).encode())
    return result


def validate(root: Path, ledger: dict, seal: dict, audit: dict) -> dict:
    fields(audit, {"version", "scope", "proof_scope_sha256", "source_ledger_sha256",
                   "corpus_sha256", "obligations"}, "audit")
    if type(audit["version"]) is not int or audit["version"] != 1 or audit["scope"] != "proof_repository":
        raise ValueError("invalid witness audit version or scope")
    if audit["proof_scope_sha256"] != digest((root / "proof-scope.json").read_bytes()):
        raise ValueError("stale proof scope pin")
    if audit["source_ledger_sha256"] != seal["source_ledger_sha256"] \
            or audit["source_ledger_sha256"] != digest((root / "source-ledger.json").read_bytes()):
        raise ValueError("stale source ledger pin")
    canonical = runpy.run_path(str(root / "tools/scope.py"))["obligation_digest"]
    if canonical(ledger["obligations"]) != seal["obligations_sha256"]:
        raise ValueError("sealed obligations changed")
    pins, statements = corpus(root)
    if audit["corpus_sha256"] != pins:
        raise ValueError("stale or incomplete proof corpus")
    model = {row["id"]: row for row in ledger["obligations"] if row["kind"] == "model"}
    rows = audit["obligations"]
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("invalid obligation census")
    ids = [row.get("id") for row in rows]
    if any(not isinstance(name, str) for name in ids) or len(set(ids)) != len(ids) or set(ids) != set(model):
        raise ValueError("incomplete or duplicate model obligation census")
    known_controls = controls(root)
    statuses, kinds, gaps = Counter(), Counter(), []
    unaudited_criteria = 0
    for row in rows:
        fields(row, {"id", "closure_packet", "reviewed", "scope_complete", "scope_review",
                     "witnesses", "criteria", "controls"}, "obligation audit")
        name, obligation = row["id"], model[row["id"]]
        if row["closure_packet"] != obligation["closure_packet"]:
            raise ValueError(f"reassigned closure packet: {name}")
        if type(row["reviewed"]) is not bool or type(row["scope_complete"]) is not bool:
            raise ValueError(f"invalid scope review flags: {name}")
        if row["reviewed"]:
            text(row["scope_review"], f"scope review: {name}")
        elif row["scope_complete"] or row["scope_review"] != "" or row["witnesses"] or row["controls"]:
            raise ValueError(f"unreviewed obligation receives credit: {name}")
        if not isinstance(row["witnesses"], list):
            raise ValueError(f"invalid witnesses: {name}")
        witnesses = {}
        for witness in row["witnesses"]:
            fields(witness, {"path", "name", "statement", "scope_kind", "establishes",
                             "premises", "limits"}, "witness")
            if not isinstance(witness["path"], str) or not isinstance(witness["name"], str):
                raise ValueError(f"invalid witness reference: {name}")
            key = f"{witness['path']}#{witness['name']}"
            if key not in statements or key in witnesses:
                raise ValueError(f"unknown or duplicate proof witness: {name}: {key}")
            if witness["statement"] != statements[key]:
                raise ValueError(f"changed witness statement: {name}: {key}")
            if witness["scope_kind"] not in SCOPES:
                raise ValueError(f"invalid witness scope: {name}: {key}")
            if witness["scope_kind"] != "finite_example" and not re.match(r"^\(\s*(?:0\s+)?\w+\s*:", witness["statement"]):
                raise ValueError(f"closed statement labeled general: {name}: {key}")
            for field in ("establishes", "limits"):
                text(witness[field], f"witness {field}: {key}")
            unique_strings(witness["premises"], f"witness premises: {key}")
            witnesses[key] = witness
            kinds[witness["scope_kind"]] += 1
        criteria = row["criteria"]
        if (not isinstance(criteria, list) or any(not isinstance(item, dict) for item in criteria)
                or [item.get("index") for item in criteria] != list(range(len(obligation["acceptance_criteria"])))
                or any(type(item.get("index")) is not int for item in criteria)):
            raise ValueError(f"incomplete criterion census: {name}")
        used = set()
        for item in criteria:
            fields(item, {"index", "status", "witnesses", "rationale", "remaining"}, "criterion")
            if item["status"] not in {"witnessed", "gap", "unreviewed"}:
                raise ValueError(f"invalid criterion status: {name}")
            unaudited_criteria += item["status"] == "unreviewed"
            unique_strings(item["witnesses"], f"criterion witnesses: {name}", allow_empty=True)
            if set(item["witnesses"]) - set(witnesses):
                raise ValueError(f"unknown criterion witness: {name}")
            used.update(item["witnesses"])
            text(item["rationale"], f"criterion rationale: {name}")
            if item["status"] == "witnessed":
                if item["remaining"] != "" or not item["witnesses"]:
                    raise ValueError(f"witnessed criterion lacks evidence: {name}")
                if all(witnesses[key]["scope_kind"] == "finite_example" for key in item["witnesses"]):
                    raise ValueError(f"finite examples cannot close a criterion: {name}")
            else:
                text(item["remaining"], f"remaining criterion work: {name}")
            if not row["reviewed"] and (item["status"] != "unreviewed" or item["witnesses"]):
                raise ValueError(f"unreviewed criterion receives credit: {name}")
        if used != set(witnesses):
            raise ValueError(f"witness is not assigned to a criterion: {name}")
        if not isinstance(row["controls"], list):
            raise ValueError(f"invalid semantic controls: {name}")
        seen = set()
        for control in row["controls"]:
            fields(control, {"name", "sha256"}, "semantic control")
            control_name = control["name"]
            if not isinstance(control_name, str) or control_name in seen \
                    or control_name not in known_controls or control["sha256"] != known_controls[control_name]:
                raise ValueError(f"unknown, duplicate or changed semantic control: {name}")
            seen.add(control_name)
        complete = all(item["status"] == "witnessed" for item in criteria)
        if row["scope_complete"] and not complete:
            raise ValueError(f"complete scope has unresolved criteria: {name}")
        if complete and row["scope_complete"] and not seen:
            raise ValueError(f"complete scope lacks weakening controls: {name}")
        status = "covered" if complete and row["scope_complete"] else "partial" if row["reviewed"] else "unreviewed"
        statuses[status] += 1
        if status != "covered":
            gaps.append({"id": name, "closure_packet": row["closure_packet"], "status": status,
                         "scope_review": row["scope_review"],
                         "criteria": [{"index": item["index"], "status": item["status"],
                                       "remaining": item["remaining"]}
                                      for item in criteria if item["status"] != "witnessed"]})
    return {"audit_valid": True, "proof_scope_sha256": audit["proof_scope_sha256"],
            "audit_sha256": digest((root / "proof-audit.json").read_bytes()),
            "modules": len(pins), "proof_declarations": len(statements),
            "model_obligations": len(model), "reviewed_obligations": len(rows) - statuses["unreviewed"],
            "covered_obligations": statuses["covered"], "partial_obligations": statuses["partial"],
            "unreviewed_obligations": statuses["unreviewed"], "witness_scope_counts": dict(sorted(kinds.items())),
            "unaudited_criteria": unaudited_criteria,
            "witness_audit_complete": statuses["unreviewed"] == 0 and unaudited_criteria == 0,
            "model_coverage_complete": statuses["covered"] == len(model),
            "external_obligations_closed": False, "remaining": gaps,
            "note": "Pins and audit structure are checked. Semantic entailment, scope classifications and premises require review; compiler checks are separate."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true",
                        help="require every model obligation to have a complete witness audit")
    args = parser.parse_args()
    catalog = runpy.run_path(str(ROOT / "tools/catalog.py"))
    inventory = catalog["inventory"]()
    ledger, seal = catalog["load"](ROOT / "source-ledger.json"), catalog["load"](ROOT / "proof-scope.json")
    runpy.run_path(str(ROOT / "tools/scope.py"))["validate"](ROOT, inventory, ledger, seal)
    result = validate(ROOT, ledger, seal, catalog["load"](ROOT / "proof-audit.json"))
    build = ROOT / ".build"
    build.mkdir(exist_ok=True)
    (build / "audit-report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "remaining"}, indent=2))
    return 2 if args.require_complete and not result["model_coverage_complete"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"witness audit failed: {error}", file=sys.stderr)
        raise SystemExit(1)
