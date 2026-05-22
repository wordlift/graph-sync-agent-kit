# CLI Resolution

Use this reference before running graph-sync CLI commands from a skill. Do not assume `worai` is globally installed.

## Resolution Order

When a graph-sync CLI command is needed:

1. Prefer the project-documented command from `AGENTS.md`, `README.md`, `docs/`, scripts, or workflow files.
2. If the project pins a `worai_version` in `.github/workflows/graph-sync.yml`, reuse that version for local/ephemeral runs when practical.
3. If `worai` is on `PATH`, run `worai version` or `worai --help` first to confirm it works.
4. If the project explicitly provides `worai` in its local environment, use the project runner, for example `uv run worai ...`.
5. If `worai` is unavailable and an ephemeral runner is acceptable, prefer a pinned command:

```bash
pipx run --spec worai==<version> worai <args>
```

or:

```bash
uvx --from worai==<version> worai <args>
```

6. If no version is known or the command would install/fetch packages, ask the user before proceeding.
7. If local CLI execution is not practical, rely on the GitHub workflow or ask the user for the preferred validation path.

## Smoke Command Intent

The intent of a smoke command is to verify that the project's graph-sync CLI path can load the config/profile and expose the expected command contract. The exact command may differ by installed `worai` version.

Candidate command shapes:

```bash
worai --config worai.toml graph sync run --profile <name> --help
```

```bash
uv run worai --config worai.toml graph sync run --profile <name> --help
```

```bash
pipx run --spec worai==<version> worai --config worai.toml graph sync run --profile <name> --help
```

Use the project-documented equivalent when these shapes do not match the installed CLI.

## Safety

- Do not install or fetch packages without approval when the environment requires it.
- Prefer pinned versions for ephemeral runners.
- Report which runner was used in the final validation summary.
- If only GitHub Actions can run the real sync safely, say that clearly and do not fake local validation.
