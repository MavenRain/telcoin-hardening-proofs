#!/usr/bin/env python3
"""Ensure the incomplete project cannot pass the complete-qualification command."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--jobs", type=int, choices=range(1, 9), default=1,
                    help="independent negative-check workers (default: 1)")
args = parser.parse_args()
# The full suite starts a compiler process for every negative control.
result = subprocess.run([sys.executable, "-I", str(ROOT / "tools/check.py"), "--require-complete",
                         "--jobs", str(args.jobs)],
                        cwd=ROOT, capture_output=True, text=True, timeout=3600)
if result.returncode != 2:
    print(result.stdout + result.stderr, file=sys.stderr)
    raise SystemExit("expected qualification-blocked exit 2")
report = json.loads((ROOT / ".build/report.json").read_text())
if report["model_checked"] is not True or report["implementation_proved"] is not False \
        or report["deployment_qualified"] is not False or not report["blockers"]:
    raise SystemExit("qualification status is inconsistent")
print("Incomplete qualification correctly rejected with exit 2; model checks passed.")
