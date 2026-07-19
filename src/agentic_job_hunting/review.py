from __future__ import annotations

import re


def evidence_review(material: str, claim_sources: list[dict], jd: dict) -> dict:
    mapped = {item["claim"] for item in claim_sources if item.get("source") and item.get("support")}
    visible = [line[2:].strip() for line in material.splitlines() if line.startswith("- ")]
    missing = [claim for claim in visible if claim not in mapped]
    outcomes = [str(item).casefold() for item in jd["outcomes"]]
    coverage = sum(any(token in material.casefold() for token in outcome.split()) for outcome in outcomes)
    score = round(coverage / len(outcomes) * 100) if outcomes else 0
    verdict = "PASS" if not missing and score >= 67 else "FAIL"
    return {
        "verdict": verdict,
        "unsupported_claims": missing,
        "outcome_coverage": score,
        "hard_gates": {"evidence": "PASS" if not missing else "FAIL"},
    }


def cold_reader_review(*, company: str, role: str, jd_text: str, material: str) -> dict:
    """Blind review: intentionally has no profile, evidence, strategy, or repository input."""
    jargon = {
        "mcp",
        "rag",
        "hil",
        "p95",
        "control plane",
        "agentic",
    }
    lower = material.casefold()
    jd_lower = jd_text.casefold()
    unexplained = sorted(term for term in jargon if term in lower and term not in jd_lower)
    bullets = [line[2:].strip() for line in material.splitlines() if line.startswith("- ")]
    incomplete = [line for line in bullets if len(re.findall(r"\b\w+\b", line)) < 8]
    reason = bullets[0] if bullets else ""
    verdict = "PASS" if bullets and not unexplained and not incomplete else "FAIL"
    return {
        "company": company,
        "role": role,
        "verdict": verdict,
        "unexplained_terms": unexplained,
        "incomplete_readbacks": incomplete,
        "must_interview_reason": reason,
        "readbacks": [
            {
                "visible_claim": bullet,
                "plain_language": bullet,
                "employer_value": "This is relevant to the stated role outcome.",
            }
            for bullet in bullets
        ],
    }
