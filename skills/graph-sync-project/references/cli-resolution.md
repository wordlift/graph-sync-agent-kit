# CLI Resolution

Use this reference before running graph-sync CLI commands from a skill. Do not assume `worai` is globally installed.

This reference covers CLI runner resolution and command shape. For `worai.toml` config semantics, check the project `wordlift-sdk` version as described in `references/overview.md`. For running a sync on a laptop, see `references/local-runs.md`.

## Inside A Graph-Sync Repository

A sync must run `worai` from the **project environment**: postprocessors import the project's `src/` package, which only the project `.venv` has.

1. Prefer the project-documented command from `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/`, scripts, or workflow files.
2. Check that `worai` is a project dependency:

   ```bash
   uv run python -c "import shutil; print(shutil.which('worai'))"
   ```

   A path inside `<repo>/.venv` means `uv run worai ...` is the runner. Anything else means `uv run worai` would silently run another `worai` from `PATH`.
3. If it isn't, add it to the dev group (`uv add --dev "worai>=<version>"`, which updates `uv.lock`), with the user's approval since it changes the repository. For a one-off run without changing the repository: `uv run --with worai==<version> worai ...`.
4. Use the `worai` version CI installs when known (the `worai==` line of the graph-sync action log, or a `worai_version` input in `.github/workflows/graph-sync.yml`); otherwise the latest release.

Do not run syncs with a bare `worai` from `PATH`, `pipx run` or `uvx`: they lack the project package. Those runners are fine for commands that don't load the project (`--help`, account or graph queries).

## Outside A Repository

If `worai` is unavailable and an ephemeral runner is acceptable, prefer a pinned command:

```bash
pipx run --spec worai==<version> worai <args>
```

or:

```bash
uvx --from worai==<version> worai <args>
```

If no version is known or the command would install/fetch packages, ask the user before proceeding. If local CLI execution is not practical, rely on the GitHub workflow or ask the user for the preferred validation path.

## Smoke Command Intent

The intent of a smoke command is to verify that the project's graph-sync CLI path can load the config/profile and expose the expected command contract. The exact command may differ by installed `worai` version.

```bash
uv run worai --config worai.toml --profile <name> graph sync run --help
```

`graph sync run` takes only `--debug` and `--output-dir`; `--config` and `--profile` are top-level `worai` options and come before `graph`. Prefer checking `--help` for the exact runner before assuming a command signature.

## Safety

- Do not install or fetch packages without approval when the environment requires it.
- Prefer pinned versions for ephemeral runners.
- Report which runner was used in the final validation summary.
- A sync writes to the account's live graph: confirm the account with the user first (`references/local-runs.md`).
- If only GitHub Actions can run the real sync safely, say that clearly and do not fake local validation.
