---
name: graph-sync-repo-lifecycle
description: "Repository lifecycle workflow for WordLift graph-sync projects. Use when creating a new graph-sync project from the template, initializing git, cloning an existing graph-sync repository, preparing a working checkout, committing successful project changes, or pushing verified changes back to the remote repository."
---

# Graph Sync Repo Lifecycle

## Overview

Use this skill for repository lifecycle work around graph-sync projects: create, clone, initialize git, prepare a checkout, commit verified changes, and push to a remote.

This skill owns git safety. Semantic curation belongs in `graph-sync-curator`; project implementation belongs in `graph-sync-project`.

## New Project Initialization

Ask for or infer:

- Project name.
- Destination directory.
- Whether to trust the Copier template.
- Whether to initialize git and create the first commit.

Default command shape:

```bash
pipx run copier copy gh:wordlift/graph-sync-template <project-name> --trust
cd <project-name>
git init .
git status
git add .
git commit -m "initial commit"
```

Resolve project-generation tools in this order:

- Project-documented generation command.
- Installed `copier` when available.
- `pipx run --spec copier==<version> copier copy ...` when `pipx` is available.
- `uvx --from copier==<version> copier copy ...` when `uvx` is available.
- Ask the user before installing/fetching packages or using an unpinned template tool.

Before the first commit:

- Verify `.env` is ignored.
- Run the secret hygiene checklist.
- Inspect `git status`.
- Avoid staging unrelated local files.

## Existing Project Checkout

Ask for or infer:

- Repository URL.
- Destination directory.
- Branch, if not the default branch.

Default command shape:

```bash
git clone <repo-url>
cd <repo-name>
git status
```

For git operations:

- Confirm `git --version` works when git availability is uncertain.
- For SSH repository URLs, expect remote authentication or SSH keys to be configured.
- If clone, fetch, or push fails due to auth, report the failure and ask for the preferred credential path.

After cloning:

- Read the project `AGENTS.md` or equivalent instructions.
- Inspect the repository shape before editing.
- Run the project setup/validation command only when needed for the user's task.

## Session Closeout

When the user asks to publish, sync back, wrap up, commit, or push successful changes:

- Inspect `git status`.
- Run the secret hygiene checklist.
- Review changed files and avoid unwanted generated artifacts.
- Run the project validation command if it has not already passed.
- Summarize changed files and validation results.
- Propose a clear commit message.
- Ask for explicit confirmation before pushing.

Default closeout command shape:

```bash
git status
git diff --check
uv run pytest
git add <changed-files>
git commit -m "<summary>"
git push
```

Use tiered validation when `uv run pytest` is absent or not meaningful:

- Project-documented validation command.
- Tests when present, using the project runner if documented.
- Lint when configured, using the project runner if documented.
- Graph-sync CLI smoke check for generated projects.
- Real sync/audit validation for curation changes.

Do not assume `uv`, `pytest`, or `ruff` are installed globally. Prefer project-documented commands first; otherwise use the active project environment, `uv run ...` when `uv` is available and configured, or ask before installing/fetching tooling.

When a graph-sync CLI command is needed, do not assume `worai` is globally installed. Prefer the project-documented command first. Otherwise resolve the runner in this order:

- `worai` on `PATH`, after confirming `worai version` or `worai --help` works.
- Project-provided runner such as `uv run worai ...` when the project explicitly provides it.
- Pinned ephemeral runner such as `pipx run --spec worai==<version> worai ...` or `uvx --from worai==<version> worai ...`.
- GitHub workflow or user-provided validation path when local execution is not practical.

Ask before installing or fetching packages, and report which runner was used.

## Secret Hygiene

Before any commit or push:

- Inspect changed and staged files before staging broadly.
- Never stage `.env`, `.env.*` except intentional examples such as `.env.example`, `.codex/`, private keys, service-account JSON files, downloaded credentials, local provider configs, token dumps, or API response dumps.
- Review diffs and config files for inline secrets or sensitive headers, including `api_key`, `token`, `secret`, `password`, `Authorization`, `X-API-Key`, `http_headers`, and service-account blocks.
- If a secret appears in a tracked or staged file, stop and ask how to proceed; do not quote the secret value back to the user.
- Use a project-documented secret scanner when one exists; otherwise keep the check manual and focused on changed files.

## Guardrails

- Do not push without explicit user confirmation.
- Do not force push unless the user explicitly requests it.
- Do not commit `.env`, credentials, private keys, `.codex/`, or local secret files.
- Prefer explicit file staging over blind `git add .` after editing sessions.
- Report validation failures before committing.
- If the worktree contains unrelated user changes, leave them alone and stage only the intended files.
