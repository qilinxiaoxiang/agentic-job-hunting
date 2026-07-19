# Agentic Job Hunting

A synthetic, evidence-constrained reference pipeline for turning a live job description into a
reviewed application material pack.

The pipeline discovers or imports a role, fingerprints it for deduplication, screens fit, selects
only source-backed candidate evidence, builds a role-specific narrative, and runs two independent
reviews. The ordinary reviewer can inspect the evidence graph. The cold reader receives only the
job description and final material, so familiarity with private context cannot hide unclear prose.

The public pipeline deliberately stops at `reviewed_material_pack`. It contains no account
creation, inbox codes, browser automation, form submission, real applications, or personal data.

This is one application of the operating model in
[Software Is Switching Operators](https://shawnxiang.com/articles/agentic-life-os/): a person sets
the goal and legal boundaries, agents prepare bounded work, deterministic checks enforce evidence,
and reviewers decide whether the material is ready.

## Reproducible demo

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/agentic-job-hunting build \
  --profile examples/synthetic-profile.json \
  --jd examples/synthetic-jd.json \
  --output /tmp/agentic-job-demo
.venv/bin/pytest
.venv/bin/python scripts/privacy_check.py
```

The output contains:

- `strategy.json` — role outcomes, fit, selected/omitted evidence, and interview reason.
- `material.txt` — the employer-facing synthetic material.
- `claim-sources.json` — every visible claim and its source/support.
- `review.json` — evidence-aware review.
- `cold-reader.json` — blind comprehension review.
- `application-pack.json` — hashes and the terminal public state.

If any visible claim lacks support, either review fails, an unexplained term remains, or the role is
weakly matched, the builder refuses to mark the pack ready.

## Design boundaries

- The ledger identifies duplicates by normalized company, role, and source URL.
- Fit scoring is transparent and intentionally small; it is a screen, not a prediction of hiring.
- Content generation is template-based in this public demo. A model can replace the drafting step
  only if the same claim-source and review contracts remain enforced.
- The cold-reader function has no profile or evidence parameter by design.
- The final pack is not an authorization to contact anyone or mutate an external system.

## License

MIT
