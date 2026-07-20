#!/bin/bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT/.venv/bin/python}"
DEMO_DIR="$(mktemp -d /tmp/agentic-job-hunting-verify.XXXXXX)"

cleanup() {
  rm -rf "$DEMO_DIR"
}
trap cleanup EXIT

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Python environment not found at $PYTHON_BIN" >&2
  echo "Run: python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'" >&2
  exit 2
fi

cd "$ROOT"

echo "[1/5] lint"
"$PYTHON_BIN" -m ruff check .

echo "[2/5] tests"
"$PYTHON_BIN" -m pytest -q

echo "[3/5] synthetic demo"
"$PYTHON_BIN" -m agentic_job_hunting build \
  --profile examples/synthetic-profile.json \
  --jd examples/synthetic-jd.json \
  --output "$DEMO_DIR"

echo "[4/5] privacy and secret scan"
"$PYTHON_BIN" scripts/privacy_check.py

echo "[5/5] output and documentation contracts"
"$PYTHON_BIN" - "$DEMO_DIR/application-pack.json" "$ROOT" <<'PY'
import json
import re
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert manifest["state"] == "reviewed_material_pack"
assert manifest["external_submission_authorized"] is False
assert len(manifest["artifacts"]) == 5
assert all(len(value) == 64 for value in manifest["artifacts"].values())

root = Path(sys.argv[2]).resolve()
for markdown in (root / "README.md", root / "docs/AI-MAINTAINER-GUIDE.md"):
    text = markdown.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "#")):
            continue
        local = (markdown.parent / target.split("#", 1)[0]).resolve()
        assert local.is_relative_to(root), f"link escapes repository: {markdown}: {target}"
        assert local.exists(), f"broken local link: {markdown}: {target}"

print("output and documentation contracts passed")
PY

git diff --check
echo "verification passed"
