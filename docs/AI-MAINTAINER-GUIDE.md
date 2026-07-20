# AI maintainer guide

This file is the operating entry point for an AI coding agent maintaining the public reference
pipeline. It describes how to understand the repository, change it safely, run it, and prove that a
change preserved the project contract.

## Mission

Maintain a small, inspectable example of evidence-constrained job-material preparation. A successful
change should make one contract clearer or stronger without importing personal data or granting the
agent external authority.

## Read order

Before editing:

1. `AGENTS.md`: non-negotiable repository boundaries.
2. `README.md`: product thesis, public/private boundary, and user-facing behavior.
3. `src/agentic_job_hunting/pipeline.py`: end-to-end artifact flow.
4. `src/agentic_job_hunting/review.py`: reviewer input boundaries and release gates.
5. `src/agentic_job_hunting/ledger.py`: fingerprint and state semantics.
6. `tests/test_pipeline.py`: executable behavior contract.
7. The exact example or script affected by the requested change.

Do not infer behavior from this guide when the code or tests say otherwise. Update the guide when a
deliberate contract change makes it stale.

## Invariants

Every change must preserve these properties unless the repository owner explicitly changes the
public contract:

- Inputs remain synthetic. Never add a real name, email, resume, application, employer record,
  credential, inbox token, or absolute workstation path.
- Every employer-facing claim has a non-empty repository-relative `source` and exact `support`.
- The cold reader receives only `company`, `role`, `jd_text`, and final `material`. It must not gain
  access to the profile, strategy, evidence graph, repository, or prior review.
- Duplicate targets are rejected through a deterministic fingerprint.
- A failed review produces `blocked`; code must fail closed rather than silently downgrade a gate.
- The terminal public state is `reviewed_material_pack`.
- `external_submission_authorized` remains `false`.
- The manifest hashes every final review artifact.
- The repository remains dependency-light, locally runnable, and covered by the acceptance suite.

## Where changes belong

- Change evidence validation, ranking, artifact creation, or release state in `pipeline.py`.
- Change target identity or local state transitions in `ledger.py`.
- Change evidence-aware or cold-reader behavior in `review.py`.
- Change command-line arguments or output in `cli.py`.
- Add synthetic scenarios under `examples/` and behavioral coverage under `tests/`.
- Add a new repository-wide privacy token only in `scripts/privacy_check.py`.
- Keep user-facing explanation in `README.md`; keep operational maintenance detail here.

Avoid duplicating a contract in several places. Put the executable rule in code or a test, then link
to it from documentation.

## Start and run

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
bash scripts/verify.sh
```

For a focused demo run:

```bash
.venv/bin/agentic-job-hunting build \
  --profile examples/synthetic-profile.json \
  --jd examples/synthetic-jd.json \
  --output /tmp/agentic-job-demo
```

Use a fresh output directory when testing deduplication-sensitive behavior. Reusing a directory is
expected to trigger the target ledger's duplicate gate.

## Safe change loop

1. Name the contract being changed and the observable result.
2. Inspect the current implementation and its nearest tests.
3. Make the smallest coherent change.
4. Add or update a test that would fail without the change.
5. Run the focused test while iterating.
6. Run `bash scripts/verify.sh` before handoff.
7. Inspect the generated `application-pack.json`, not only the command exit code.
8. Review `git diff` for private data, absolute paths, weakened gates, and unrelated edits.

When a reviewer or test exposes a reusable failure pattern, fix the earliest layer that could have
prevented it. Prefer an input validator or test over a reminder in prose. Keep scenario-specific
wording out of global rules.

## Extension recipes

### Replace template drafting with a model

Keep model invocation behind a narrow function and preserve the existing output contract. Validate
the returned claims against the evidence graph before writing employer-facing material. The model
must not receive credentials or gain network-side submission authority. Add a deterministic test
double so the full suite remains offline and reproducible.

### Add a pipeline stage

Define the stage's input, structured output, failure state, and consumer. Add its artifact before
manifest construction, hash it in the manifest when it affects release, and test both pass and fail
paths. A new stage must not create an alternate route around evidence or review gates.

### Add a reviewer

Give the reviewer the minimum input needed for its independent judgment. Document the input boundary
in its function signature and lock that signature with a test. If its verdict can block release,
bind its final output to the manifest.

### Change evidence selection

Use a synthetic example where the old and new ranking differ. Preserve weak-fit refusal and explain
selection versus omission in `strategy.json`. Do not turn the screen into a claim about hiring
probability.

### Change target identity

Update fingerprint tests first. Normalization must be deterministic and stable across processes.
Document any migration implication for an existing `targets.sqlite` file.

## Acceptance matrix

| Change type | Minimum proof |
|---|---|
| Documentation only | Privacy scan, link/path check, `git diff --check` |
| Pipeline or ledger | Focused regression test plus full `scripts/verify.sh` |
| Review contract | Pass and fail tests, cold-reader input-boundary test, full verification |
| Output schema | Artifact-content assertions, manifest hash assertions, README update |
| Dependency or packaging | Clean environment install, CLI demo, full verification |

## Publishing checklist

- The synthetic demo reaches `reviewed_material_pack`.
- The manifest still says `external_submission_authorized: false`.
- Unsupported evidence, weak fit, and failed review paths remain blocking.
- Lint and tests pass.
- Privacy/secret scanning passes.
- Generated artifacts contain no absolute workstation paths or private tokens.
- README commands match the current CLI.
- `git diff --check` is clean.

Do not publish production credentials, automation prompts, personal evidence, live job records, or
browser-submission code into this repository. Describe the production topology at the capability
level; keep the runnable public implementation synthetic and bounded.
