from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .ledger import TargetLedger
from .review import cold_reader_review, evidence_review


class EvidenceError(ValueError):
    pass


def _words(value: str) -> set[str]:
    return {word.casefold() for word in re.findall(r"[A-Za-z][A-Za-z-]+", value) if len(word) > 3}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_pack(profile_path: str | Path, jd_path: str | Path, output: str | Path) -> dict:
    profile_path, jd_path = Path(profile_path), Path(jd_path)
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    jd = json.loads(jd_path.read_text(encoding="utf-8"))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)

    ledger = TargetLedger(output / "targets.sqlite")
    if not ledger.add(company=jd["company"], role=jd["role"], source_url=jd["source_url"]):
        raise EvidenceError("duplicate target in this ledger")

    jd_words = _words(" ".join(jd["outcomes"] + jd.get("keywords", [])))
    evidence = profile.get("evidence", [])
    for item in evidence:
        if not all(str(item.get(key, "")).strip() for key in ("id", "claim", "source", "support")):
            raise EvidenceError("every evidence item needs id, claim, source, and support")
        if Path(item["source"]).is_absolute():
            raise EvidenceError("public evidence sources must be repository-relative")
    ranked = sorted(
        evidence,
        key=lambda item: len(_words(item["claim"]) & jd_words),
        reverse=True,
    )
    selected = [item for item in ranked if _words(item["claim"]) & jd_words][:3]
    if len(selected) < 2:
        raise EvidenceError("weak fit: fewer than two evidence-backed outcomes")

    material_lines = [f"{profile['display_name']} — {jd['role']}", ""]
    material_lines.append(
        "Interview this candidate because the evidence below combines "
        + ", ".join(item["signal"] for item in selected)
        + "."
    )
    material_lines.extend(["", "Selected evidence"])
    material_lines.extend(f"- {item['claim']}" for item in selected)
    material = "\n".join(material_lines) + "\n"
    claim_sources = [
        {"claim": item["claim"], "source": item["source"], "support": item["support"]}
        for item in selected
    ]
    strategy = {
        "company": jd["company"],
        "role": jd["role"],
        "outcomes": jd["outcomes"],
        "selected": [item["id"] for item in selected],
        "omitted": [item["id"] for item in evidence if item not in selected],
        "terminal_boundary": "reviewed_material_pack",
    }

    artifacts = {
        "strategy.json": strategy,
        "material.txt": material,
        "claim-sources.json": claim_sources,
    }
    for name, value in artifacts.items():
        path = output / name
        path.write_text(
            value if isinstance(value, str) else json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    review = evidence_review(material, claim_sources, jd)
    cold = cold_reader_review(
        company=jd["company"],
        role=jd["role"],
        jd_text="\n".join(jd["outcomes"] + jd.get("keywords", [])),
        material=material,
    )
    (output / "review.json").write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    (output / "cold-reader.json").write_text(json.dumps(cold, indent=2) + "\n", encoding="utf-8")
    ready = review["verdict"] == "PASS" and cold["verdict"] == "PASS"
    manifest = {
        "state": "reviewed_material_pack" if ready else "blocked",
        "external_submission_authorized": False,
        "artifacts": {
            name: _sha(output / name)
            for name in (
                "strategy.json",
                "material.txt",
                "claim-sources.json",
                "review.json",
                "cold-reader.json",
            )
        },
    }
    (output / "application-pack.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    ledger.set_state(
        company=jd["company"],
        role=jd["role"],
        source_url=jd["source_url"],
        state=manifest["state"],
    )
    if not ready:
        raise EvidenceError("independent review blocked the material pack")
    return manifest
