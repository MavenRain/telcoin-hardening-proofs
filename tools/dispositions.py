#!/usr/bin/env python3
"""Check pinned source dispositions and obligation links, without proof credit."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy
import sys


def fields(value, expected: set[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"invalid {label} fields")


def text(value, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing {label}")


def references(value, label: str) -> None:
    if (not isinstance(value, list) or any(not isinstance(item, str) for item in value)
            or len(value) != len(set(value))):
        raise ValueError(f"invalid {label} references")


def validate(units: list[dict], ledger: dict, manifest_hash: str,
             atomic_ids: set[str], packets: dict[str, set[str]]) -> dict:
    fields(ledger, {"version", "source_manifest_sha256", "units", "obligations"}, "source ledger")
    if type(ledger["version"]) is not int or ledger["version"] != 1:
        raise ValueError("invalid source ledger version")
    if ledger["source_manifest_sha256"] != manifest_hash:
        raise ValueError("source ledger manifest pin is stale")
    rows, obligations = ledger["units"], ledger["obligations"]
    if not units or not isinstance(rows, list) or len(rows) != len(units):
        raise ValueError("source ledger must cover every indexed unit exactly once")
    if not isinstance(obligations, list):
        raise ValueError("invalid source obligation list")
    by_id = {}
    for row in obligations:
        fields(row, {"id", "kind", "workstream", "closure_packet", "property",
                     "required_scope", "acceptance_criteria", "required_evidence", "candidate_atoms"},
               "source obligation")
        name, kind = row["id"], row["kind"]
        if (not isinstance(kind, str) or kind not in {"model", "external"} or not isinstance(name, str)
                or not re.fullmatch(("M" if kind == "model" else "E") + r"[0-9]{3,}", name)
                or name in by_id):
            raise ValueError("invalid or duplicate source obligation identity")
        packet, stream = row["closure_packet"], row["workstream"]
        if (not isinstance(packet, str) or packet not in {f"R{i:02}" for i in range(3, 9)}
                or not isinstance(stream, str) or stream not in packets.get(packet, set())):
            raise ValueError(f"invalid obligation closure assignment: {name}")
        for key in ("property", "required_scope"):
            text(row[key], f"{name} {key}")
        for key in ("acceptance_criteria", "required_evidence"):
            if not isinstance(row[key], list) or not row[key]:
                raise ValueError(f"missing {name} {key}")
            for item in row[key]:
                text(item, f"{name} {key}")
        candidates = row["candidate_atoms"]
        references(candidates, f"{name} candidate atoms")
        if set(candidates) - atomic_ids or (kind == "external" and candidates):
            raise ValueError(f"invalid candidate proof links: {name}")
        by_id[name] = row
    by_unit, used = {}, set()
    states = Counter()
    pending_sources = Counter()
    for index, (unit, row) in enumerate(zip(units, rows), 1):
        fields(row, {"id", "source", "lines", "sha256", "disposition", "obligations",
                     "rationale", "reconciles"}, "source disposition")
        name = f"U{index:04}"
        if row["id"] != name:
            raise ValueError("source ledger units are missing, duplicated or reordered")
        if (not isinstance(row["lines"], list) or len(row["lines"]) != 2
                or any(type(line) is not int for line in row["lines"])
                or any(row[key] != unit[key] for key in ("source", "lines", "sha256"))):
            raise ValueError(f"source disposition pin is stale: {name}")
        state = row["disposition"]
        if not isinstance(state, str) or state not in {"pending", "context", "obligation", "superseded"}:
            raise ValueError(f"invalid source disposition: {name}")
        links, replacements = row["obligations"], row["reconciles"]
        references(links, f"{name} obligations")
        references(replacements, f"{name} reconciliations")
        if not isinstance(row["rationale"], str):
            raise ValueError(f"invalid source rationale: {name}")
        if state != "pending":
            text(row["rationale"], f"{name} disposition rationale")
        if (state == "obligation") != bool(links) or set(links) - by_id.keys():
            raise ValueError(f"missing or invalid obligation links: {name}")
        if state in {"pending", "context"} and replacements:
            raise ValueError(f"unaudited or context unit has reconciliation links: {name}")
        if state == "superseded" and not replacements:
            raise ValueError(f"superseded unit has no replacement: {name}")
        if state == "obligation" and row["source"].startswith("sources/w1/") and not replacements:
            raise ValueError(f"original requirement has no modified-plan reconciliation: {name}")
        used.update(links)
        states[state] += 1
        if state == "pending":
            pending_sources[row["source"]] += 1
        by_unit[name] = row
    if used != by_id.keys():
        raise ValueError("source ledger contains an unreferenced obligation")
    for name, row in by_unit.items():
        for target in row["reconciles"]:
            replacement = by_unit.get(target)
            if (replacement is None or target == name
                    or replacement["disposition"] not in {"obligation", "superseded"}):
                raise ValueError(f"missing or unaudited reconciliation target: {name}: {target}")
            if not replacement["source"].startswith("sources/w1-modified/"):
                raise ValueError(f"reconciliation target is not a modified-plan unit: {name}: {target}")
    # Walk iteratively so a long valid replacement chain cannot exhaust Python's stack.
    resolved, reconciled_obligations = set(), {}
    for name in by_unit:
        stack, active = [(name, False)], set()
        while stack:
            target, leaving = stack.pop()
            if leaving:
                active.remove(target)
                resolved.add(target)
                reconciled_obligations[target] = set(by_unit[target]["obligations"])
                for child in by_unit[target]["reconciles"]:
                    reconciled_obligations[target].update(reconciled_obligations[child])
            elif target in active:
                raise ValueError(f"cyclic source reconciliation: {target}")
            elif target not in resolved:
                active.add(target)
                stack.append((target, True))
                stack.extend((child, False) for child in by_unit[target]["reconciles"])
    for name, row in by_unit.items():
        if row["disposition"] == "obligation" and row["reconciles"]:
            retained = set().union(*(reconciled_obligations[target] for target in row["reconciles"]))
            if set(row["obligations"]) - retained:
                raise ValueError(f"reconciliation drops retained obligations: {name}")
    return {"complete": states["pending"] == 0,
            "source_units": len(rows), "audited_units": len(rows) - states["pending"],
            "pending_units": states["pending"], "context_units": states["context"],
            "obligation_units": states["obligation"], "superseded_units": states["superseded"],
            "model_obligations": sum(row["kind"] == "model" for row in obligations),
            "external_obligations": sum(row["kind"] == "external" for row in obligations),
            "pending_by_source": dict(sorted(pending_sources.items()))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true",
                        help="reject any source unit whose disposition remains pending")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    catalog = runpy.run_path(str(root / "tools/catalog.py"))
    inventory = catalog["inventory"]()
    catalog["proof_plan"](inventory)
    report = {"version": 1, "scope": "source_disposition_links",
              "note": "Disposition rationales require semantic review; candidate atoms receive no proof credit.",
              "dispositions": inventory["dispositions"],
              "inputs_sha256": {relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
                                for relative in ("source-ledger.json", "sources/manifest.json",
                                                 "claims.json", "atomic-claims.json", "proof-roadmap.json",
                                                 "tools/catalog.py", "tools/dispositions.py")}}
    (root / ".build").mkdir(exist_ok=True)
    (root / ".build/source-disposition-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(inventory["dispositions"]))
    if args.require_complete and not inventory["dispositions"]["complete"]:
        print("Source disposition closure blocked by pending units.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"source disposition validation failed: {error}", file=sys.stderr)
        sys.exit(1)
