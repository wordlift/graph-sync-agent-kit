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
- Source type (`sitemap`, `urls`, or `google_sheets`) and the matching source value.
- WordLift API key handling: always scaffold with `CHANGE_ME` and API-key validation disabled, then tell the user to replace it immediately after Copier finishes.
- For the chosen source type, every required Copier field. Do not pass `source_type` without its matching required data.

Default command shape:

```bash
pipx run copier copy --trust --defaults \
  --data source_type=sitemap \
  --data sitemap_url=https://www.example.org/sitemap.xml \
  --data api_key=CHANGE_ME \
  --data validate_api_key=false \
  gh:wordlift/graph-sync-template <project-name>
cd <project-name>
git init .
git status
git add .
git commit -m "initial commit"
```

Prefer non-interactive Copier execution. Codex shell commands may not provide an interactive TTY for Copier prompts, and template prompting can fail with stdin errors. Use `--defaults` together with explicit `--data` values; `--data` by itself does not suppress prompts. Put Copier switches before the template source and destination for clarity. Do not run bare `copier copy ...` for a new graph-sync project unless an interactive terminal is known to be available.

For non-interactive template data:

- Always provide the required fields for the selected source type in the same Copier command. If a required value is unknown but the user wants a scaffold, use an obvious placeholder and warn that it must be replaced before real syncs.
- For `sitemap`, provide `sitemap_url`. When the domain is known and no sitemap was supplied, use the conventional placeholder `https://<domain>/sitemap.xml`.
- For `urls`, provide `urls` as a non-empty YAML/JSON list. When no URLs were supplied but the domain is known, seed it with the homepage, for example `--data source_type=urls --data 'urls=["https://www.example.org/"]'`.
- For `google_sheets`, provide `sheets_url`, `sheets_name`, and `sheets_service_account`. Use real values only when the user provided them through a safe local path or environment variable. For scaffold-only generation, use obvious placeholders such as `sheets_url=https://docs.google.com/spreadsheets/d/CHANGE_ME/edit`, `sheets_name=Sheet1`, and `sheets_service_account=.secrets/google-service-account.json`, then warn that the project cannot run until those values are replaced.
- Always use `--data api_key=CHANGE_ME --data validate_api_key=false` during Copier generation. Immediately after Copier finishes, tell the user where the placeholder was written and ask them to replace `CHANGE_ME` with a real WordLift API key before any sync, validation, or first commit.
- Do not ask the user to paste secrets into chat, do not echo secret values back, and avoid putting real secrets in command examples, git diffs, shell history, or committed files.
- Avoid adding real API keys, service-account JSON, or generated `.env` files to the first commit.

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
- Source directory, when resuming from an existing local folder rather than cloning.

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

- Read the project `AGENTS.md`, `CLAUDE.md`, or equivalent instructions.
- Inspect the repository shape before editing.
- Check API-key readiness before running graph-sync commands, validation, or real syncs:
  - Look for a project-root `.env` without printing its contents; use existence/non-empty checks and quiet key-name checks only.
  - When resuming from a local source directory, check whether that source directory already has a `.env`; if it does, ask before copying it into the working checkout, keep it untracked, and never echo the secret value.
  - If no usable `.env` exists, ask the user to provide the WordLift API key through a local-only path, such as editing `.env`, exporting an environment variable in their shell, or pointing to an existing local secret file. Do not ask them to paste the key into chat.
  - When creating `.env`, prefer copying `.env.example` if present; otherwise create the smallest local placeholder the project expects and tell the user exactly which placeholder must be replaced before syncs.
  - Verify `.env` and `.env.*` are ignored before any commit or push.
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
- Never stage `.env`, `.env.*` except intentional examples such as `.env.example`, `.codex/`, `.claude/settings.local.json`, private keys, service-account JSON files, downloaded credentials, local provider configs, token dumps, or API response dumps.
- Review diffs and config files for inline secrets or sensitive headers, including `api_key`, `token`, `secret`, `password`, `Authorization`, `X-API-Key`, `http_headers`, and service-account blocks.
- If a secret appears in a tracked or staged file, stop and ask how to proceed; do not quote the secret value back to the user.
- Use a project-documented secret scanner when one exists; otherwise keep the check manual and focused on changed files.

## Guardrails

- Do not push without explicit user confirmation.
- Do not force push unless the user explicitly requests it.
- Do not commit `.env`, credentials, private keys, `.codex/`, `.claude/settings.local.json`, or local secret files.
- Prefer explicit file staging over blind `git add .` after editing sessions.
- Report validation failures before committing.
- If the worktree contains unrelated user changes, leave them alone and stage only the intended files.
