#!/usr/bin/env python3
"""Build the locked mechanism-lang checker in a disposable repository-local cache."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, cwd: Path = ROOT) -> str:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=600)
    if result.returncode:
        raise RuntimeError(f"{args[0]} failed ({result.returncode}): {result.stdout}{result.stderr}")
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-source", type=Path, help="reuse a local checkout as the clone source")
    args = parser.parse_args()
    lock = json.loads((ROOT / "toolchain.lock.json").read_text())["compiler"]
    cache = ROOT / ".cache" / "mechanism-lang"
    if cache.exists():
        raise ValueError(f"cache already exists: {cache}; inspect it before choosing a new build")
    cache.parent.mkdir(exist_ok=True)
    source = str(args.local_source.resolve()) if args.local_source else lock["repository"]
    run("git", "clone", "--no-hardlinks", "--no-checkout", source, str(cache))
    run("git", "checkout", "--detach", lock["revision"], cwd=cache)
    if args.local_source:
        vendor = args.local_source.resolve() / "vendor" / "veil"
        run("git", "clone", "--no-hardlinks", "--no-checkout", str(vendor), str(cache / "vendor" / "veil"))
        run("git", "checkout", "--detach", lock["vendor_veil_revision"], cwd=cache / "vendor" / "veil")
    else:
        # Veil marks its nested donor submodules as data-only. They are not
        # checker build inputs, and their URLs include a machine-local path.
        run("git", "submodule", "update", "--init", "--", "vendor/veil", cwd=cache)
    revision = run("git", "rev-parse", "HEAD", cwd=cache)
    vendor_revision = run("git", "rev-parse", "HEAD", cwd=cache / "vendor" / "veil")
    if revision != lock["revision"] or vendor_revision != lock["vendor_veil_revision"]:
        raise ValueError("source revision does not match the toolchain lock")
    if run("git", "status", "--porcelain", cwd=cache):
        raise ValueError("compiler checkout is dirty before build")
    build_log = run("dune", "build", "bin/mech.exe", cwd=cache)
    compiler = cache / "_build" / "default" / "bin" / "mech.exe"
    report = {"revision": revision, "vendor_veil_revision": vendor_revision,
              "compiler_sha256": hashlib.sha256(compiler.read_bytes()).hexdigest(),
              "ocaml": run("ocamlc", "-version"), "dune": run("dune", "--version")}
    (ROOT / ".cache" / "compiler-build.json").write_text(json.dumps(report, indent=2) + "\n")
    (ROOT / ".cache" / "compiler-build.log").write_text(build_log + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
