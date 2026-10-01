#!/usr/bin/env python3
"""Validate the sealed source scope without assigning proof or external credit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import runpy
import sys


def obligation_digest(obligations: list[dict]) -> str:
    return hashlib.sha256(json.dumps(obligations, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def references(root: Path, ledger: dict, source: str, pattern: str) -> list[dict]:
    lines = (root / source).read_text().splitlines()
    rows = []
    for unit in ledger["units"]:
        if unit["source"] != source:
            continue
        match = re.match(pattern, lines[unit["lines"][0] - 1])
        if match:
            if unit["disposition"] != "obligation" or not unit["obligations"]:
                raise ValueError(f"normative scope row lacks fixed obligations: {unit['id']}")
            rows.append({"id": match[1], "unit": unit["id"],
                         "obligations": unit["obligations"]})
    return rows


def scope_references(root: Path, ledger: dict) -> tuple[list[dict], list[dict]]:
    tracking = references(root, ledger, "sources/w1-modified/03-RATIONALE-AND-CROSSWALK.md",
                          r"\| (N\d+|T\d+|A\d+|S\d+|G\d+|D\d+|R\d+|O\d+|P\d+|M\d+|X\d+) \|")
    decisions = references(root, ledger, "sources/w1-modified/04-DECISIONS-AND-ACCEPTANCE.md",
                           r"\| (D\d{2}) \|")
    expected = {f"{prefix}{index}" for prefix, count in
                (("N", 2), ("T", 12), ("A", 27), ("S", 9), ("G", 7), ("D", 4),
                 ("R", 13), ("O", 9), ("P", 6), ("M", 5), ("X", 8))
                for index in range(1, count + 1)}
    if len(tracking) != 102 or {row["id"] for row in tracking} != expected:
        raise ValueError("source scope must retain all 102 original tracking IDs exactly once")
    if len(decisions) != 12 or {row["id"] for row in decisions} != {f"D{i:02}" for i in range(1, 13)}:
        raise ValueError("source scope must retain all D01-D12 decisions exactly once")
    return tracking, decisions


def validate(root: Path, inventory: dict, ledger: dict, seal: dict) -> dict:
    fields = {"version", "scope", "boundary", "workstreams", "source_manifest_sha256",
              "source_ledger_sha256", "obligations_sha256", "obligation_ids", "tracking", "decisions"}
    if not isinstance(seal, dict) or set(seal) != fields:
        raise ValueError("invalid source scope seal fields")
    if type(seal["version"]) is not int or seal["version"] != 1 or seal["scope"] != "proof_repository":
        raise ValueError("invalid source scope seal version or boundary")
    if not isinstance(seal["boundary"], str) or not seal["boundary"].strip():
        raise ValueError("missing explicit proof boundary")
    if seal["workstreams"] != [f"W{i}" for i in range(10)]:
        raise ValueError("source scope omits or reorders a workstream")
    if inventory["semantically_complete"] is not True or inventory["dispositions"]["complete"] is not True:
        raise ValueError("source scope cannot seal pending dispositions")
    if inventory["dispositions"]["pending_units"] != 0:
        raise ValueError("source scope cannot seal pending dispositions")
    manifest = hashlib.sha256((root / "sources/manifest.json").read_bytes()).hexdigest()
    if seal["source_manifest_sha256"] != manifest or ledger["source_manifest_sha256"] != manifest:
        raise ValueError("source scope manifest pin is stale")
    if seal["source_ledger_sha256"] != hashlib.sha256((root / "source-ledger.json").read_bytes()).hexdigest():
        raise ValueError("source scope ledger pin is stale; an explicit new scope baseline is required")
    obligations = ledger["obligations"]
    if seal["obligations_sha256"] != obligation_digest(obligations):
        raise ValueError("source scope obligations changed; an explicit new scope baseline is required")
    names = [row["id"] for row in obligations]
    if seal["obligation_ids"] != names or len(names) != len(set(names)):
        raise ValueError("source scope obligation census differs from the fixed ledger")
    tracking, decisions = scope_references(root, ledger)
    if seal["tracking"] != tracking or seal["decisions"] != decisions:
        raise ValueError("source scope tracking or decision links changed")
    return {"source_scope_sealed": True, "source_units": len(ledger["units"]),
            "model_obligations": sum(row["kind"] == "model" for row in obligations),
            "external_obligations": sum(row["kind"] == "external" for row in obligations),
            "original_tracking_ids": len(tracking), "decisions": len(decisions),
            "proof_witnesses_audited": False, "external_obligations_closed": False}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    catalog = runpy.run_path(str(root / "tools/catalog.py"))
    inventory = catalog["inventory"]()
    result = validate(root, inventory, catalog["load"](root / "source-ledger.json"),
                      catalog["load"](root / "proof-scope.json"))
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"source scope validation failed: {error}", file=sys.stderr)
        sys.exit(1)
