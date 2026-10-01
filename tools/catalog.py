#!/usr/bin/env python3
"""Inventory every nonblank source block without claiming semantic completeness."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def checked_path(relative: str) -> Path:
    path = ROOT / relative
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
        raise ValueError(f"unsafe path: {relative}")
    return path


def snapshot_files() -> list[dict]:
    manifest = load(ROOT / "sources" / "manifest.json")
    rows = manifest["files"]
    paths = [row["path"] for row in rows]
    if len(set(paths)) != len(paths):
        raise ValueError("duplicate snapshot path")
    expected = set(paths)
    actual = {str(p.relative_to(ROOT)) for folder in ("w1", "w1-modified")
              for p in (ROOT / "sources" / folder).iterdir() if p.is_file()}
    if actual != expected:
        raise ValueError("snapshot inventory differs from manifest")
    for row in rows:
        data = checked_path(row["path"]).read_bytes()
        if digest(data) != row["sha256"] or len(data) != row["bytes"]:
            raise ValueError(f"snapshot changed: {row['path']}")
    return rows


def source_units(rows: list[dict], claims: dict) -> list[dict]:
    units = []
    for row in rows:
        if not row["path"].endswith(".md"):
            continue
        lines = checked_path(row["path"]).read_text().splitlines()
        start = None

        def flush(stop):
            nonlocal start
            if start is None:
                return
            text = "\n".join(lines[start:stop])
            groups = [claim["id"] for claim in claims["claims"]
                      if row["path"] == claims["target_document"]
                      and start + 1 <= claim["lines"][1] and stop >= claim["lines"][0]]
            units.append({"source": row["path"], "lines": [start + 1, stop],
                          "sha256": digest(text.encode()), "claim_groups": groups})
            start = None

        for index, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                flush(index)
            elif (stripped.startswith("|") or re.match(r"^(#{1,6}\s|[-*+]\s|\d+[.)]\s)", stripped)):
                flush(index)
                start = index
                if stripped.startswith("|") or stripped.startswith("#"):
                    flush(index + 1)
            elif start is None:
                start = index
        flush(len(lines))
        covered = {n for unit in units if unit["source"] == row["path"]
                   for n in range(unit["lines"][0], unit["lines"][1] + 1)}
        if any(line.strip() and index + 1 not in covered for index, line in enumerate(lines)):
            raise ValueError(f"source inventory dropped a line: {row['path']}")
    return units


def theorem_names(source: str) -> set[str]:
    definitions = re.findall(r"^def(?: rec)?\s+(\w+)\s*:\s*(.*?)\s*:=", source, re.M | re.S)
    result = set()
    for name, statement in definitions:
        depth, last_arrow = 0, 0
        for index, char in enumerate(statement):
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            elif depth == 0 and statement[index:index + 2] == "->":
                last_arrow = index + 2
        # Proof-consuming functions returning Count or a generic family are
        # checked too, but are not counted as explicit proof declarations.
        if re.match(r"\s*(Equal|AtMost)\b", statement[last_arrow:]):
            result.add(name)
    return result


def atomic_claims(theorems: set[str], groups: set[str]) -> list[dict]:
    data = load(ROOT / "atomic-claims.json")
    if data["coverage_complete"] is not False:
        raise ValueError("complete atomic coverage has not been established")
    assumptions = set(data["shared_assumptions"])
    rows = data["claims"]
    ids = [row["id"] for row in rows]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("empty or duplicate atomic claims")
    manifest_paths = {row["path"] for row in load(ROOT / "sources/manifest.json")["files"]}
    for row in rows:
        if row["parent"] not in groups or not row["theorems"] or set(row["theorems"]) - theorems:
            raise ValueError(f"invalid atomic proof links: {row['id']}")
        if set(row["assumptions"]) - assumptions or not row["open_implementation_obligations"]:
            raise ValueError(f"missing atomic boundary: {row['id']}")
        ref = row["source"]
        if ref["path"] not in manifest_paths:
            raise ValueError(f"unlocked atomic source: {row['id']}")
        lines = checked_path(ref["path"]).read_text().splitlines()
        start, stop = ref["lines"]
        if not (1 <= start <= stop <= len(lines)):
            raise ValueError(f"invalid atomic source range: {row['id']}")
    return rows


def validate_claims(claims: dict, theorems: set[str]) -> None:
    ids = [claim["id"] for claim in claims["claims"]]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("empty or duplicate claim identifiers")
    lines = checked_path(claims["target_document"]).read_text().splitlines()
    for claim in claims["claims"]:
        start, stop = claim["lines"]
        if not (1 <= start <= stop <= len(lines)):
            raise ValueError(f"invalid source range: {claim['id']}")
        if set(claim["theorems"]) - theorems:
            raise ValueError(f"unknown theorem in {claim['id']}")
        if not claim["model_scope"] or not claim["required_evidence"]:
            raise ValueError(f"missing boundary or evidence in {claim['id']}")
    if {claim["workstream"] for claim in claims["claims"]} != {f"W{i}" for i in range(10)}:
        raise ValueError("a workstream is absent from the ledger")


def inventory() -> dict:
    rows = snapshot_files()
    claims = load(ROOT / "claims.json")
    source = "\n".join(path.read_text() for path in sorted((ROOT / "proofs").glob("*.mech")))
    validate_claims(claims, theorem_names(source))
    atomic_claims(theorem_names(source), {row["id"] for row in claims["claims"]})
    units = source_units(rows, claims)
    validator = runpy.run_path(str(ROOT / "tools/dispositions.py"))["validate"]
    plan = load(ROOT / "proof-roadmap.json")
    ledger = load(ROOT / "source-ledger.json")
    summary = validator(units, ledger,
                        digest((ROOT / "sources/manifest.json").read_bytes()),
                        {row["id"] for row in load(ROOT / "atomic-claims.json")["claims"]},
                        {row["id"]: set(row["workstreams"]) for row in plan["packets"]})
    auditor = runpy.run_path(str(ROOT / "tools/audit.py"))["validate"]
    witness_audit = auditor(ROOT, ledger, load(ROOT / "proof-scope.json"), load(ROOT / "proof-audit.json"))
    return {"version": 1, "semantically_complete": summary["complete"],
            "note": "Disposition links are checked; semantic rationales and theorem scope require review.",
            "dispositions": summary,
            "witness_audit": {key: value for key, value in witness_audit.items() if key != "remaining"},
            "units": units}


def proof_plan(data: dict) -> dict:
    plan = load(checked_path("proof-roadmap.json"))
    if plan["version"] != 1 or plan["scope"] != "proof_repository":
        raise ValueError("invalid proof-roadmap scope or version")
    budget, reserve = plan["turn_budget"], plan["reserve_turns"]
    if type(budget) is not int or not 1 <= budget <= 50 or type(reserve) is not int or reserve < 0:
        raise ValueError("invalid proof-roadmap turn budget")
    packets = plan["packets"]
    if [row["id"] for row in packets] != [f"R{i:02}" for i in range(1, 11)]:
        raise ValueError("proof-roadmap must retain the ten ordered closure packets")
    statuses = {row["id"]: row["status"] for row in packets}
    workstreams = {row["workstream"] for row in load(ROOT / "claims.json")["claims"]}
    assigned, earlier = set(), set()
    for row in packets:
        name = row["id"]
        if not isinstance(row["title"], str) or not row["title"].strip() or re.search(r"[\n\r|]", row["title"]):
            raise ValueError(f"invalid proof packet title: {name}")
        if row["status"] not in {"pending", "active", "closed"}:
            raise ValueError(f"invalid proof packet status: {name}")
        if (type(row["planned_turns"]) is not int or row["planned_turns"] < 1
                or type(row["turns_spent"]) is not int or row["turns_spent"] < 0):
            raise ValueError(f"invalid proof packet turn count: {name}")
        dependencies = row["depends_on"]
        if not isinstance(dependencies, list) or len(set(dependencies)) != len(dependencies) or set(dependencies) - earlier:
            raise ValueError(f"invalid proof packet dependencies: {name}")
        if row["status"] in {"active", "closed"} and any(statuses[dep] != "closed" for dep in dependencies):
            raise ValueError(f"proof packet prerequisites are open: {name}")
        scopes = row["workstreams"]
        if not isinstance(scopes, list) or not scopes or len(set(scopes)) != len(scopes) or set(scopes) - workstreams:
            raise ValueError(f"invalid proof packet workstreams: {name}")
        assigned.update(scopes)
        criteria = row["exit_criteria"]
        if not isinstance(criteria, list) or not criteria or any(not isinstance(item, str) or not item.strip() for item in criteria):
            raise ValueError(f"missing proof packet exit criteria: {name}")
        evidence = row["evidence"]
        if not isinstance(evidence, list):
            raise ValueError(f"invalid proof packet evidence: {name}")
        witnessed = set()
        for receipt in evidence:
            index = receipt["criterion"]
            if type(index) is not int or not 0 <= index < len(criteria):
                raise ValueError(f"invalid proof packet evidence criterion: {name}")
            relative, expected = receipt["path"], receipt["sha256"]
            if (not isinstance(relative, str) or not relative or Path(relative).is_absolute()
                    or not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected)):
                raise ValueError(f"invalid proof packet evidence reference: {name}")
            path = checked_path(relative)
            if not path.is_file() or digest(path.read_bytes()) != expected:
                raise ValueError(f"stale or missing proof packet evidence: {name}: {relative}")
            witnessed.add(index)
        if row["status"] == "closed" and witnessed != set(range(len(criteria))):
            raise ValueError(f"proof packet lacks evidence for every exit criterion: {name}")
        earlier.add(name)
    if assigned != workstreams:
        raise ValueError("proof-roadmap omits a workstream")
    planned = sum(row["planned_turns"] for row in packets)
    if planned + reserve != budget:
        raise ValueError("proof-roadmap allocations and reserve differ from the turn budget")
    if packets[0]["status"] == "closed":
        scope = runpy.run_path(str(ROOT / "tools/scope.py"))["validate"]
        scope(ROOT, data, load(ROOT / "source-ledger.json"), load(ROOT / "proof-scope.json"))
    if packets[1]["status"] == "closed" and not data["witness_audit"]["witness_audit_complete"]:
        raise ValueError("R02 witness audit is incomplete")
    return plan | {"planned_turns": planned,
                   "turns_used": sum(row["turns_spent"] for row in packets),
                   "closed_packets": sum(row["status"] == "closed" for row in packets)}


def coverage_markdown(data: dict) -> str:
    claims = load(ROOT / "claims.json")
    plan = proof_plan(data)
    closed, total = plan["closed_packets"], len(plan["packets"])
    budget_status = ("target exceeded" if plan["turns_used"] > plan["turn_budget"] else
                     "exhausted before closure" if plan["turns_used"] == plan["turn_budget"] and closed < total else
                     "within budget")
    rows = ["# Claim coverage", "", "Generated by `python3 -I tools/catalog.py`.", "",
            f"{len(data['units'])} source units are indexed, including headings, context and code. "
            "Every nonblank Markdown line is covered. "
            + ("All source dispositions are recorded." if data["semantically_complete"] else
               "Semantic decomposition is incomplete."), "",
            "## Source disposition audit", "",
            f"{data['dispositions']['audited_units']}/{len(data['units'])} source units have audited dispositions; "
            f"{data['dispositions']['pending_units']} remain pending. "
            f"{data['dispositions']['model_obligations']} model and "
            f"{data['dispositions']['external_obligations']} external obligations are assigned.", "",
            "The pinned [source ledger](../source-ledger.json) retains every unit, its rationale, "
            "obligation links and original/modified reconciliations. Candidate atoms receive no theorem "
            "credit from this check. See [the ledger format](SOURCE-LEDGER.md).", "",
            "## Proof repository closure", "",
            "The fixed proof-only checklist is in [proof-roadmap.json](../proof-roadmap.json); "
            "its scope and execution rules are in the [roadmap](ROADMAP.md). "
            "Existing theorem work is credited through the packet audits.", "",
            f"**Closure checklist: {closed}/{total} packets ({100 * closed / total:.0f}%).** "
            "This measures audited packet closure, not total effort or deployment qualification.", "",
            f"Execution turns used: {plan['turns_used']}/{plan['turn_budget']}. "
            f"Allocation: {plan['planned_turns']} planned + {plan['reserve_turns']} reserve. "
            f"Budget status: {budget_status}.", "",
            "| Packet | Closure task | Planned turns | Actual turns | Status |",
            "|---|---|---:|---:|---|"]
    for row in plan["packets"]:
        rows.append(f"| {row['id']} | {row['title']} | {row['planned_turns']} | "
                    f"{row['turns_spent']} | {row['status']} |")
    audit = data["witness_audit"]
    rows.extend(["", "Evidence hashes check freshness. Each exit criterion still requires an audit "
                 "of its evidence, and semantic completeness requires the checked source disposition ledger.", "",
            "## Frozen model witness audit", "",
            f"{audit['reviewed_obligations']}/{audit['model_obligations']} model obligations have a first witness review: "
            f"{audit['covered_obligations']} covered, {audit['partial_obligations']} partial, "
            f"{audit['unreviewed_obligations']} unreviewed. "
            f"{audit['unaudited_criteria']} acceptance criteria still need audit.", "",
            f"The pinned corpus contains {audit['proof_declarations']} explicit proof declarations in "
            f"{audit['modules']} modules. [proof-audit.json](../proof-audit.json) records exact statements, "
            "premises, scope limits and outstanding criterion work. "
            "See [the R02 audit](R02-AUDIT.md). Statement and hash checks do not establish semantic entailment. "
            "Finite examples receive no general coverage credit; external obligations remain open.", "",
            "## Full implementation and deployment claims", "",
            "Every group below remains open against the Telcoin implementation and deployment. "
            "Theorem links cover only the explicitly stated model scope in `claims.json`.", "",
            "| Group | Workstream | Requirement | Model theorem links |", "|---|---|---|---|"])
    for claim in claims["claims"]:
        link = f"../{claims['target_document']}#L{claim['lines'][0]}"
        rows.append(f"| [{claim['id']}]({link}) | {claim['workstream']} | {claim['claim']} | "
                    + (", ".join(f"`{name}`" for name in claim["theorems"]) or "Open") + " |")
    rows.extend(["", "Use `claims.json` for each theorem's limited scope and required evidence. "
                 "Use `source-inventory.json` for all original and modified document ranges. "
                 "Text not assigned to a group is retained for manual triage; it is never treated as proved.", ""])
    atoms = load(ROOT / "atomic-claims.json")["claims"]
    rows.extend(["## Atomic model obligations", "", f"{len(atoms)} obligations have explicit model theorem links. "
                 "All retain implementation obligations and stated assumptions in `atomic-claims.json`.", "",
                 "| ID | Parent | Property | Theorems |", "|---|---|---|---|"])
    for row in atoms:
        rows.append(f"| {row['id']} | {row['parent']} | {row['property']} | "
                    + ", ".join(f"`{name}`" for name in row["theorems"]) + " |")
    rows.append("")
    return "\n".join(rows)


if __name__ == "__main__":
    data = inventory()
    (ROOT / "source-inventory.json").write_text(json.dumps(data, indent=2) + "\n")
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "COVERAGE.md").write_text(coverage_markdown(data))
    print(json.dumps({"source_units": len(data["units"]),
                      "units_with_group_links": sum(bool(row["claim_groups"]) for row in data["units"]),
                      "semantically_complete": data["semantically_complete"],
                      "audited_source_units": data["dispositions"]["audited_units"]}))
