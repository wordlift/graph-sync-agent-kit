# Local Runs (Windows, macOS, Linux)

How to run a graph-sync profile on a laptop, and what differs from CI. Commands are the same on every OS unless a section says otherwise; run them from the repository root.

## Machine Prerequisites

- `git` and `uv`. Nothing else needs a global install: `uv` provides Python and the project tools.
- Graph-sync projects run on **Python 3.12**, and CI sets it in the workflow. Don't add a `.python-version` file to the repository.

## Prepare A Checkout

```bash
uv sync
```

- `.env` at the repository root holds the secrets: `WORDLIFT_API_KEY=...`, plus `SHEETS_SERVICE_ACCOUNT=.config/sa-key.json` for a Google Sheets source. `worai` loads `.env` itself; no `source .env` is needed. Check that `.env` is git-ignored.
- `worai` must run from the project environment. Check:

  ```bash
  uv run python -c "import shutil; print(shutil.which('worai'))"
  ```

  The path must be inside `<repo>/.venv`. When `worai` is not a project dependency, `uv run worai` silently runs another `worai` found on `PATH` (a pipx install, another folder's virtual environment). That interpreter lacks the project's `src/` package, so every URL is fetched (and paid for) and then fails with `No module named '<project_package>'`. Fix the repository once:

  ```bash
  uv add --dev "worai>=<version>"
  ```

  Use the version CI installs (the `worai==` line of the graph-sync action log) or the latest release. Use `uv add`, not a hand edit, so `uv.lock` changes in the same step; CI's `uv sync --locked` fails on a `pyproject.toml` that disagrees with the lock. The lock diff is large: `worai` raises the project's `wordlift-sdk` with it.
- One-off without touching the repository: `uv run --with worai==<version> worai ...`.
- A virtual environment activated from another folder puts its own `worai` first on `PATH`, which is the one `uv run worai` falls through to. The tell is ``VIRTUAL_ENV=… does not match the project environment path `.venv` and will be ignored`` at the top of the run; deactivate it (or unset `VIRTUAL_ENV`) first.

## Confirm The Account Before Every Sync

A sync has no dry run: it writes straight into the knowledge graph of the account whose API key the profile uses, which is usually the client's live graph. Before every run, show the user which account it is and wait for a yes:

```bash
uv run python <graph-sync-project skill>/scripts/kg_check.py account --profile <profile>
```

It prints the account id, Website URL, dataset URI and entity count, and warns when the profile's source hosts don't match the account's Website URL (the crawler then refuses every page). In an unattended run (no user to answer, such as the dashboard bootstrap), the task prompt is the approval: report the account in the final summary instead of waiting (`graph-sync-curator` "Working With The User"). To work without touching the live graph, use a temporary account (`references/kg-checks.md`).

## Run A Profile

```bash
uv run worai --config worai.toml --profile <profile> graph sync run --debug --output-dir output
```

- `--output-dir output` (worai >= 6.19.0) writes `output/graph_sync_report.md` and, when any URL failed, `output/graph_sync_failures.csv` (`timestamp,url,error`). Without it, worai prints only `Total URLs: N, Successes: N, Failures: N`.
- `--debug` writes each page's graph to `output/debug_cloud/<profile>/cloud_<sha256(url)>.ttl` and the static templates to `output/debug_cloud/<profile>/static_templates.ttl`. The graphs are written to the knowledge graph as well.
- A run processes every URL of the profile's source. There is no single-URL option; for a few pages use a local config copy (below) whose profile reads `ingest_source = "urls"` with those URLs. It still writes to the same account.
- After a run, check the result (`references/kg-checks.md`): what the graph holds for sample pages, twins, and a cache clear so the API link serves the new data.

## Local Config Copy

Settings that only apply to one machine go in a copy, never in the committed `worai.toml`:

1. Copy `worai.toml` to `worai.local.toml` **in the same folder** (relative paths resolve from there).
2. Keep it out of git without touching `.gitignore`: add `worai.local.toml` to `.git/info/exclude`.
3. Edit the copy (Windows settings below, a `urls` test source, lower pools).
4. Run with `--config worai.local.toml`.

Every `${VAR}` of **every** profile is interpolated on each run, whichever profile runs. An unset variable used only by another profile fails the run with `ProfileConfigError: Missing environment variable 'VAR' for profile '<other>'`. Give it any value in `.env` locally; on CI it needs a placeholder in the workflow `env:`.

## Windows

Make these changes in `worai.local.toml`:

- **Postprocessors: `postprocessor_runtime = "inprocess"` in `[profiles._base]`.** The committed `persistent` runtime starts worker subprocesses, which fail on Windows with `[WinError 2]` (the manifest's default `./.venv/bin/python` doesn't exist there) or `[WinError 10038]` (the SDK reads the worker's pipe with `select()`, which Windows supports only on sockets). Changing the manifest's `python =` fixes only the first. `inprocess` runs postprocessors inside the `worai` process instead.
  - It must be in `[profiles._base]`: worai rejects `inprocess` in a named profile with a `ValueError`. The `POSTPROCESSOR_RUNTIME` variable doesn't help, because the SDK reads the profile, then `_base`, then the variable, and `_base` already sets `persistent`.
  - It needs `worai` in the project environment (above); otherwise every URL fails with `No module named '<project_package>'`.
  - **Never commit `inprocess`.** CI runs `worai` from system Python, which cannot import the project's package, so every URL fails there.
- **`mapping_pool_size` at 6 or lower.** At 12 the materialization pool broke (`BrokenProcessPool`) and every in-flight URL failed.
- **UTF-8 mode for non-ASCII sites.** The SDK writes an intermediate mapping file with the platform's default encoding (cp1252 on Windows) and reads it back as UTF-8, so Turkish letters or typographic dashes crash the run with `UnicodeEncodeError: 'charmap' codec can't encode ...` or `UnicodeDecodeError: 'utf-8' codec can't decode ...`. Set `PYTHONUTF8=1` for the run: `$env:PYTHONUTF8 = "1"` in PowerShell for the current terminal, or `setx PYTHONUTF8 1` once (applies to new terminals). Nothing changes in the repository.

## macOS And Linux

The committed configuration works as is: `persistent` postprocessors run in `./.venv/bin/python`, and the default encoding is UTF-8.

## Why A Green Local Run Doesn't Prove CI

The CI workflow runs `uv sync --locked --no-dev`, then the `wordlift/graph-sync@v6` action installs its own `worai` (and the latest compatible `wordlift-sdk`) into system Python and runs it there, ignoring the lock. Only the `persistent` postprocessor workers use the project `.venv`. So CI can fail where a local run passed:

- `inprocess` committed: every URL fails with `No module named '<project_package>'`.
- Custom postprocessors on `wordlift-sdk` >= 8.5.0 without the `all` extra: every URL fails with `No module named 'regex'` (the dev group's `worai` hides this locally). Depend on `wordlift-sdk[all]`.
- A secret read by a postprocessor but missing from the workflow `env:` block: the run stays green and the postprocessor silently does nothing (`graph-sync-github-workflow-review`).
- A failing run still writes the static templates first, so it can revert template edits that were only synced locally.
