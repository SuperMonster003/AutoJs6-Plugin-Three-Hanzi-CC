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
the workflow leaves it and any human review fixes untouched. Otherwise it pushes the automation-owned
branch with a lease, explicitly dispatches `build.yml` and `markdown.yml`, and creates a PR containing
the upstream release summary, exact lock differences, source comparison link, and human review
checklist. Explicit dispatch is required because ordinary pushes made with `GITHUB_TOKEN` do not start
new workflow runs.

Before the first real upstream update, a repository administrator must enable **Settings > Actions >
General > Allow GitHub Actions to create and approve pull requests**. The workflow requests no review,
contains no approval command, never enables auto-merge, and never creates a tag or Release. If the
repository setting remains disabled, preparation and mandatory CI dispatch still occur, but PR creation
fails with an actionable error instead of silently weakening the process.

The generated PR is intentionally review-only. Dictionary output changes, license changes, APK size
changes, and localized release documentation remain human decisions. No failing fixture may be updated
in bulk merely to make the PR green.
