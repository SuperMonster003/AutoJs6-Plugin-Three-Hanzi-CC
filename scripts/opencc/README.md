# OpenCC upstream automation

The repository separates upstream discovery from mutation:

- `check_upstream.py` is read-only. It queries the latest published, non-prerelease `ver.*` OpenCC
  release and verifies the tag commit, GitHub asset size/digest, downloaded ZIP, resource manifest,
  per-entry SHA-256 values, stored-entry requirement, and configuration inventory before comparing it
  with `opencc-upstream.properties`.
- `update_upstream.py` runs only in a clean checkout after discovery reports a newer validated release.
  It updates exactly the OpenCC submodule pointer, the lock file, and the versioned resource ZIP. It
  verifies the generated state and exact changed-file inventory, and rolls local changes back if any
  generated verification fails.
- `merge_upstream.py` is the trusted, fail-closed M4-D-3 controller. It reads pull-request and workflow
  evidence through the GitHub API without executing the proposed tree. In `merge` mode its separate
  write-side job repeats every gate and binds the squash merge to the expected head SHA.
- `controlled_acceptance.py` supplies one pinned, non-release fixture for remote D2/D3 acceptance while
  no newer formal OpenCC release exists. It is deliberately isolated from the official update path.
- `verify_upstream.py` is the offline build gate. Normal Gradle builds do not contact GitHub.

Run the current-release replay locally:

```sh
python scripts/opencc/check_upstream.py --root .
```

Run all offline automation tests:

```sh
python -m unittest discover -s scripts/opencc/tests -p "test_*.py" -v
```

`update_upstream.py` should normally be run only by `.github/workflows/opencc-upstream.yml`. If the
latest release equals the lock, it exits successfully without changing files. For a newer release it
requires a clean checkout with the OpenCC submodule and tags available:

```sh
python scripts/opencc/update_upstream.py \
  --root . \
  --pr-body-file /tmp/opencc-upgrade-pr.md
```

## Pull request security model

The scheduled workflow starts with a read-only job. A second job receives `contents: write`,
`pull-requests: write`, and `actions: write` only when the read-only job has validated a newer release.
Before committing, it independently downloads and validates the release again and rejects any
time-of-check/time-of-use change in the version, tag, commit, or resource digest.

The update branch is named `automation/opencc-<version>`. If an open PR for that branch already exists,
the workflow leaves it and any follow-up fixes untouched. Otherwise it pushes the automation-owned
branch with a lease, explicitly dispatches `build.yml` and `markdown.yml`, and creates a PR containing
the upstream release summary, exact lock differences, source comparison link, and merge-gate checklist.
Explicit dispatch is required because ordinary pushes made with `GITHUB_TOKEN` do not start new workflow
runs.

The repository enabled **Settings > Actions > General > Allow GitHub Actions to create and approve pull
requests** on 2026-09-02 while retaining read-only default workflow permissions. GitHub exposes creation
and approval as one repository switch, but the current preparation workflow contains no approval, merge,
tag, or Release command. If the setting is disabled later, preparation and mandatory CI dispatch still
occur, but PR creation fails with an actionable error instead of silently weakening the process.

The repository variable `OPENCC_AUTOMATION_MODE` is currently set to `pr-only`. No failing fixture may be
updated in bulk merely to make an upgrade green. Dictionary output changes, license changes, APK size
changes, and localized release documentation remain explicit gates while the project converts each one
from repeated human inspection to deterministic checks.

## Staged merge and release policy

`master` is intentionally not protected, so GitHub's native auto-merge is not used as a substitute for
required checks. `.github/workflows/opencc-auto-merge.yml` runs its evaluator from an explicit checkout of
the default branch with read-only permissions; it never checks out or executes pull-request-controlled
content. The evaluator accepts only one same-repository PR authored by `github-actions[bot]`, base
`master`, an exact `automation/opencc-<version>` branch and head SHA, one direct bot commit, and exactly
the lock, submodule pointer, removed old resource, and added new resource paths. It independently
revalidates the latest official release, proposed ZIP bytes, selected third-party license evidence, and
the resource growth limits (at most 512 KiB and 25%).

For that exact head SHA, the latest explicitly dispatched `build.yml` and `markdown.yml` runs must expose
the exact audited job inventory and every job must be `completed/success`. Older runs, a same-named branch,
the PR page's mergeable button, or an approval from the PR's own bot identity are not evidence. A stale
base/parent, conflict, changed-file drift, changed license evidence, excessive resource growth, latest
`CHANGES_REQUESTED` review, or `do-not-merge` / `automation-pause[d]` label rejects the candidate.

The policy progresses independently through `paused`, `pr-only`, `merge`, and `release`. In the current
`pr-only` deployment, an eligible candidate produces an auditable dry-run summary but no write job. Under
`merge`, a separate least-privilege job downloads trusted controller code from `master`, repeats every
API/upstream gate, rechecks the base SHA immediately before a SHA-bound squash merge, and deletes only an
unchanged automation branch. Any mismatch leaves the PR open; service failures make the controller run
fail visibly. `release` is recognized but intentionally fails closed until the isolated M4-D-4 signing
and publication controller exists.

## Controlled online acceptance

The manual `controlled_acceptance` input of `opencc-upstream.yml` may be used only while the repository
policy is `pr-only`. It revalidates the real latest formal release first, then creates a draft from the
pinned first direct child of the 1.4.2 source commit. Its reserved `999.4.2` version, deliberately
non-official `controlled-ver.999.4.2` tag, distinct test commit title, explicit ZIP manifest marker, and
Draft state are independent production-controller rejection barriers. The fixture changes the same four
paths as an upgrade and dispatches the same Build/Markdown workflows, but the Build workflow requires an
explicit manual boolean and records a uniquely named successful verification step.

The generated fixture normalizes every text dictionary from LF to CRLF and updates the manifest's exact
sizes and SHA-256 values. OpenCC's in-memory parser explicitly removes a trailing CR before parsing each
line, so this is a deterministic semantic no-op; it also prevents GitHub's binary similarity heuristic
from collapsing the old-resource deletion and new-resource addition into a rename. The production
controller's exact four-path add/delete contract therefore remains unchanged.

For the read-only D3 replay, manually dispatch `opencc-auto-merge.yml` with the exact draft branch/SHA and
`controlled_acceptance=true`. That path revalidates the formal base release, fixture commit parent,
resource bytes, licenses, PR shape, and exact workflow runs. It can report eligible only in `pr-only`;
the controller rejects the fixture in `merge` or `release`, rejects `--execute`, and the write job also
requires `candidate_kind == 'official'`. The ordinary `workflow_run` trigger can never select controlled
evaluation. After recording successful, failing, and existing-PR replays, close the draft and delete the
test branch. This acceptance lane is not evidence for a real automatic merge.

Automated release must pin the merged commit, obtain signing material only from encrypted secrets, verify
the existing certificate digest and five signed APKs, create the tag and Release idempotently, read every
uploaded asset back, and update the plugin index only after the Release is consistent. See `ROADMAP.md`
M4-D-3 and M4-D-4 for the complete promotion and rollback gates.
