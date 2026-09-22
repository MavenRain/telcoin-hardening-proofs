#!/usr/bin/env python3
"""Check the ordered mechanism-lang proof sources and their axiom disclosure."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


MUTATIONS = [
    ("retry_bypass", "| unvalidated => retry", "| unvalidated => accept"),
    ("poll_over_budget", "| event outcome rest => next (pollWork remaining rest)",
     "| event outcome rest => next (next (pollWork remaining rest))"),
    ("release_reoccupies_slot", "| slot state rest => slot off rest)", "| slot state rest => slot on rest)"),
    ("authentication_bypass", "both authenticated (memberAllowed (effectiveProfile validPolicy requested) member)",
     "memberAllowed (effectiveProfile validPolicy requested) member"),
    ("trusted_violation_exempt", "| protocolViolation => on", "| protocolViolation => off"),
    ("batch_admitted", "| on => batchRefused", "| on => forwarded"),
    ("overload_demotes", "| http429 => failures", "| http429 => next failures"),
    ("early_endpoint_retirement", "both converged newPathPassed", "newPathPassed"),
    ("firewall_omits_current", "either current future", "future"),
    ("model_claims_implementation", "checkItem implementationLinked (checkItem numericEnvelopeSpecified",
     "checkItem on (checkItem numericEnvelopeSpecified"),
    ("stale_generation_releases", "releaseDecision generation (sameCount token generation)",
     "releaseDecision generation on"),
    ("generation_not_advanced", "| on => freeLease (next generation)", "| on => freeLease generation"),
    ("unowned_completion_refunds", "| noOwnedLease => lease", "| noOwnedLease => freeLease zero"),
    ("terminal_cleanup_skipped", "| ownedGeneration generation => releaseOwned generation lease",
     "| ownedGeneration generation => lease"),
    ("pending_pool_grows", "| reserveAt index => updateLease index reserveLease pool",
     "| reserveAt index => leaseCell (heldLease zero) (updateLease index reserveLease pool)"),
    ("handshake_credit_not_debited", "| validated => predecessor available", "| validated => available"),
    ("refill_exceeds_capacity", "| trustedClockCredit credits => boundedWork capacity (add available credits)",
     "| trustedClockCredit credits => add available credits"),
    ("eviction_mints_credit", "| sourceEvicted identity => available", "| sourceEvicted identity => capacity"),
    ("forged_clock_mints_credit", "| claimedClockCredit credits => available",
     "| claimedClockCredit credits => add available credits"),
    ("fallback_mints_credit", "| admissionPolicyChanged valid => available",
     "| admissionPolicyChanged valid => capacity"),
    ("clock_overissues_credit", "| timeTick rest => rateEvent (trustedClockCredit rate) (timedEvents rest rate)",
     "| timeTick rest => rateEvent (trustedClockCredit (next rate)) (timedEvents rest rate)"),
    ("poll_discards_backlog", "| zero => events\n    | next remaining =>",
     "| zero => noEvents\n    | next remaining =>"),
    ("poll_loses_wakeup", "| event outcome rest => on", "| event outcome rest => off"),
    ("critical_service_skipped", "| completedServiceRound => criticalTurn state",
     "| completedServiceRound => state"),
    ("pending_cost_omitted", "add (multiply queued queueCost)\n      (add (multiply pending pendingCost) (multiply established establishedCost))",
     "add (multiply queued queueCost) (multiply established establishedCost)"),
    ("record_epoch_bypassed", "recordDecision (both verified (sameCount recordEpoch currentEpoch)) index records",
     "recordDecision verified index records"),
    ("record_authentication_bypassed", "recordDecision (both verified (sameCount recordEpoch currentEpoch)) index records",
     "recordDecision (sameCount recordEpoch currentEpoch) index records"),
    ("old_epoch_resolution_retained", "| slot present rest => slot off (clearCommitteeRecords rest)",
     "| slot present rest => slot present (clearCommitteeRecords rest)"),
    ("duplicate_record_adds_member", "| slot present rest => slot on rest)",
     "| slot present rest => slot on (slot present rest))"),
]


def invoke(compiler: Path, command: str, bundle: Path):
    return subprocess.run([str(compiler), command, str(bundle)], capture_output=True, text=True, timeout=120)


def negative_checks(compiler: Path, source: str, build: Path) -> list[str]:
    cases = [(name, source.replace(before, after)) for name, before, after in MUTATIONS]
    if any(source.count(before) != 1 for _, before, _ in MUTATIONS):
        raise ValueError("a mutation target is absent or ambiguous")
    cases.extend([
        ("false_equality", source + "\ndef impossible : Equal Flag off on := same\n"),
        ("false_bound", source + "\ndef impossible : AtMost (next zero) zero := least zero\n"),
        ("nonterminating_proof", source + "\ndef rec loop : Count -> Count := fun (n : Count) => loop n\n"),
    ])
    rejected = []
    negative_dir = build / "negative"
    negative_dir.mkdir(exist_ok=True)
    for name, candidate in cases:
        path = negative_dir / f"{name}.mech"
        path.write_text(candidate)
        result = invoke(compiler, "check", path)
        diagnostic = result.stdout + result.stderr
        (negative_dir / f"{name}.log").write_text(diagnostic)
        # Parser failures, crashes, timeouts and tool usage errors are not proof rejection.
        expected = "termination:" if name == "nonterminating_proof" else "mismatch:"
        if result.returncode != 1 or not diagnostic.strip().startswith(expected):
            raise ValueError(f"negative check {name} did not produce a type/termination rejection: {diagnostic}")
        rejected.append(name)
    return rejected


def validate_compiler(compiler: Path, catalog: dict) -> dict:
    lock = catalog["load"](ROOT / "toolchain.lock.json")["compiler"]
    receipt = catalog["load"](ROOT / ".cache" / "compiler-build.json")
    for field in ("revision", "vendor_veil_revision"):
        if receipt[field] != lock[field]:
            raise ValueError("compiler provenance differs from toolchain lock")
    if receipt["compiler_sha256"] != hashlib.sha256(compiler.read_bytes()).hexdigest():
        raise ValueError("checker binary does not match the pinned build receipt")
    return receipt


def implementation_links(path: Path | None, catalog: dict) -> dict:
    mapping = catalog["load"](ROOT / "implementation-map.json")
    lock = catalog["load"](ROOT / "toolchain.lock.json")["implementation"]
    if mapping["revision"] != lock["revision"]:
        raise ValueError("implementation mapping has a different target revision")
    if path is None:
        return {"status": "not_checked_this_run", "refinement_proved": False}
    revision = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    if revision != lock["revision"]:
        raise ValueError("implementation checkout is not at the pinned revision")
    for entry in mapping["entries"]:
        file = path / entry["path"]
        if not file.resolve().is_relative_to(path.resolve()) or file.is_symlink():
            raise ValueError("unsafe implementation path")
        if hashlib.sha256(file.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"implementation source changed: {entry['path']}")
    return {"status": "source_links_checked", "revision": revision,
            "entries": len(mapping["entries"]), "refinement_proved": False}


def input_hashes() -> dict[str, str]:
    paths = ["claims.json", "atomic-claims.json", "source-inventory.json",
             "sources/manifest.json", "implementation-map.json", "toolchain.lock.json",
             "README.md", "docs/COVERAGE.md", "docs/MODELS.md", "docs/TRUST.md",
             "docs/ROADMAP.md", "Makefile", ".github/workflows/model-checks.yml"]
    paths.extend(str(path.relative_to(ROOT)) for path in (ROOT / "proofs").glob("*.mech"))
    paths.extend(str(path.relative_to(ROOT)) for path in (ROOT / "tools").glob("*.py"))
    return {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in sorted(paths)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mech", default=os.environ.get("MECH", str(ROOT / ".cache/mechanism-lang/_build/default/bin/mech.exe")))
    parser.add_argument("--implementation", type=Path)
    parser.add_argument("--require-complete", action="store_true",
                        help="also require every implementation and deployment claim to be proved")
    args = parser.parse_args()
    build = ROOT / ".build"
    build.mkdir(exist_ok=True)
    (build / "report.json").unlink(missing_ok=True)
    checked_inputs = input_hashes()
    compiler = Path(args.mech).resolve(strict=True)
    catalog = runpy.run_path(str(ROOT / "tools" / "catalog.py"))
    provenance = validate_compiler(compiler, catalog)
    inventory = catalog["inventory"]()
    if inventory != catalog["load"](ROOT / "source-inventory.json"):
        raise ValueError("source inventory is stale; run tools/catalog.py and review the change")
    if catalog["coverage_markdown"](inventory) != (ROOT / "docs" / "COVERAGE.md").read_text():
        raise ValueError("coverage document is stale")
    linked = implementation_links(args.implementation, catalog)
    files = sorted((ROOT / "proofs").glob("*.mech"))
    if not files:
        raise ValueError("no proof sources")
    source = "\n".join(path.read_text() for path in files)
    if re.search(r"\b(axiom|sorry|admit|unsafe|primitive)\b", re.sub(r"--[^\n]*", "", source)):
        raise ValueError("proof source contains a prohibited escape hatch")
    bundle = build / "all.mech"
    bundle.write_text(source)
    for command in ("check", "axioms"):
        result = invoke(compiler, command, bundle)
        (build / f"{command}.log").write_text(result.stdout + result.stderr)
        if result.returncode != 0:
            print(result.stdout + result.stderr, file=sys.stderr)
            return 1
        if command == "axioms" and (result.stdout.strip() or result.stderr.strip()):
            print("nonempty axiom disclosure", file=sys.stderr)
            return 1
    rejected = negative_checks(compiler, source, build)
    claims = catalog["load"](ROOT / "claims.json")["claims"]
    atoms = catalog["atomic_claims"](catalog["theorem_names"](source), {row["id"] for row in claims})
    if checked_inputs != input_hashes():
        raise ValueError("proof inputs or validation tooling changed during this run")
    report = {"model_checked": True, "axioms": [], "modules": len(files),
              "inputs_sha256": checked_inputs,
              "checked_proof_declarations": len(catalog["theorem_names"](source)),
              "negative_checks_rejected": rejected,
              "claim_groups": len(claims), "source_units": len(inventory["units"]),
              "atomic_model_obligations": len(atoms),
              "claim_decomposition_complete": False,
              "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
              "compiler": provenance, "implementation_links": linked,
              "implementation_proved": False, "deployment_qualified": False,
              "blockers": ["Complete atomic claim decomposition and model coverage",
                           "Machine-checked refinement from pinned Rust and transport dependencies",
                           "Resolve D01-D12 and record the accepted numerical envelope",
                           "Supply required M1-M6, topology, storage and operator evidence"]}
    (build / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ("model_checked", "checked_proof_declarations",
          "claim_groups", "atomic_model_obligations", "source_units", "implementation_proved", "deployment_qualified")} |
          {"negative_checks_rejected": len(rejected), "report": ".build/report.json"}))
    if args.require_complete:
        print("Full qualification blocked: " + "; ".join(report["blockers"]), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        sys.exit(1)
