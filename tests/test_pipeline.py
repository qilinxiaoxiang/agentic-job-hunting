import inspect
import json

import pytest

from agentic_job_hunting import EvidenceError, build_pack
from agentic_job_hunting.ledger import TargetLedger
from agentic_job_hunting.review import cold_reader_review


def _examples():
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    return root / "examples" / "synthetic-profile.json", root / "examples" / "synthetic-jd.json"


def test_demo_builds_reviewed_pack_and_stops_before_submission(tmp_path):
    profile, jd = _examples()
    manifest = build_pack(profile, jd, tmp_path / "pack")
    assert manifest["state"] == "reviewed_material_pack"
    assert manifest["external_submission_authorized"] is False
    assert len(manifest["artifacts"]) == 5
    cold = json.loads((tmp_path / "pack" / "cold-reader.json").read_text())
    assert cold["verdict"] == "PASS"
    assert cold["unexplained_terms"] == []


def test_unsupported_evidence_blocks_build(tmp_path):
    profile_path, jd = _examples()
    profile = json.loads(profile_path.read_text())
    del profile["evidence"][0]["support"]
    broken = tmp_path / "profile.json"
    broken.write_text(json.dumps(profile))
    with pytest.raises(EvidenceError, match="source, and support"):
        build_pack(broken, jd, tmp_path / "pack")


def test_cold_reader_signature_cannot_receive_private_authoring_context():
    parameters = set(inspect.signature(cold_reader_review).parameters)
    assert parameters == {"company", "role", "jd_text", "material"}


def test_ledger_rejects_duplicate_target(tmp_path):
    ledger = TargetLedger(tmp_path / "targets.sqlite")
    target = {
        "company": "Northstar",
        "role": "Engineer",
        "source_url": "https://example.com/job/1",
    }
    assert ledger.add(**target) is True
    assert ledger.add(**target) is False
