#!/usr/bin/env python3
"""Inventory every nonblank source block without claiming semantic completeness."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

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
    return {"version": 1, "semantically_complete": False,
            "note": "Exhaustive textual indexing is not an exhaustive atomic-claim decomposition.",
            "units": source_units(rows, claims)}


def coverage_markdown(data: dict) -> str:
    claims = load(ROOT / "claims.json")
    rows = ["# Claim coverage", "", "Generated by `python3 -I tools/catalog.py`.", "",
            f"{len(data['units'])} source units are indexed, including headings, context and code. "
            "Every nonblank Markdown line is covered. Semantic decomposition is incomplete.", "",
            "Every group below remains open against the Telcoin implementation and deployment. "
            "Theorem links cover only the explicitly stated model scope in `claims.json`.", "",
            "| Group | Workstream | Requirement | Model theorem links |", "|---|---|---|---|"]
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
                      "semantically_complete": False}))
