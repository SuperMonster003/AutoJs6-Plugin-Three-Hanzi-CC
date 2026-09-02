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

The current deployment policy is `pr-only`. No failing fixture may be updated in bulk merely to make an
upgrade green. Dictionary output changes, license changes, APK size changes, and localized release
documentation remain explicit gates while the project converts each one from repeated human inspection
to deterministic checks.

## Staged merge and release policy

`master` is intentionally not protected, so GitHub's native auto-merge is not used as a substitute for
required checks. A future merge controller will run only trusted code from the default branch and must
not check out PR-controlled content with a write token. It will accept only the expected Actions-authored
same-repository PR, exact `automation/opencc-<version>` branch and head SHA, exact source/lock/resource
file inventory, and successful explicitly dispatched Build and Markdown runs for that same SHA. A stale
success, a mergeable button, or an approval from the PR's own bot identity is not evidence.

The policy progresses independently through `paused`, `pr-only`, `merge`, and `release`. Any mismatch or
service failure leaves the PR open and returns to `pr-only`. Automated release is a separate controller:
it must pin the merged commit, obtain signing material only from encrypted secrets, verify the existing
certificate digest and five signed APKs, create the tag and Release idempotently, read every uploaded
asset back, and update the plugin index only after the Release is consistent. See `ROADMAP.md` M4-D-3
and M4-D-4 for the complete promotion and rollback gates.
