---
name: graph-sync-repo-lifecycle
description: "Repository lifecycle workflow for WordLift graph-sync projects. Use when creating a new graph-sync project from the template, initializing git, cloning an existing graph-sync repository, preparing a working checkout (API key, Sheets credentials, environment), orienting in an existing or dashboard-bootstrapped repository, checking its cross-OS baseline, committing successful project changes, or pushing verified changes back to the remote repository."
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
- Inspect the repository shape before editing (see "Orient In An Existing Repository").
- Check API-key readiness before running graph-sync commands, validation, or real syncs:
  - Look for a project-root `.env` without printing its contents; use existence/non-empty checks and quiet key-name checks only.
  - When resuming from a local source directory, check whether that source directory already has a `.env`; if it does, ask before copying it into the working checkout, keep it untracked, and never echo the secret value.
  - If no usable `.env` exists, ask the user to provide the WordLift API key through a local-only path, such as editing `.env`, exporting an environment variable in their shell, or pointing to an existing local secret file. Do not ask them to paste the key into chat.
  - When creating `.env`, prefer copying `.env.example` if present; otherwise create the smallest local placeholder the project expects and tell the user exactly which placeholder must be replaced before syncs.
  - Verify `.env` and `.env.*` are ignored before any commit or push.
  - A Google Sheets source also needs the project's service-account JSON file (`SHEETS_SERVICE_ACCOUNT` in `.env`, usually `.config/sa-key.json`). It is never in the repository, and each project has its own. If it is missing, say so and give the user a message to forward to the WordLift tech team; never switch the source to the sitemap instead (`graph-sync-project` `references/sources-and-profiles.md`).
- Set up the environment with `uv sync` (`graph-sync-project` `references/local-runs.md`).
- Run the project setup/validation command only when needed for the user's task.

## Orient In An Existing Repository

Before changing anything in a repository you didn't create in this session, build a short picture of it and tell the user in plain language:

- **Profiles:** each `[profiles.<name>]` in `worai.toml`, its source (sitemap, sheet tab, URL list), its `url_regex`, its crawler modes, its fallback `mapping` and routes.
- **Accounts:** which variable each profile's `api_key` reads, and which account that is (`graph-sync-project` `scripts/kg_check.py account`).
- **Page types:** the mappings under `profiles/_base/mappings/` and `profiles/<name>/mappings/`, the root type each one emits, and its staging subjects.
- **Static templates and exports:** `profiles/_base/templates/`, `exports.toml.j2`.
- **Postprocessors:** the manifest each profile uses (a profile file replaces `_base`'s) and the classes under `src/`.
- **CI:** the workflow's profile `options` and `all` list against the profiles in `worai.toml`.
- **The template version:** `# Generated by graph-sync-template vX` in `pyproject.toml`.

Repositories created from the WordLift dashboard are bootstrapped by an agent. Expect, and check:

- A hardcoded `urls` list or a sitemap where the client provided a Google Sheet (the bootstrap had no service-account file).
- Routes with slug alternations, or routes to mappings that emit nothing.
- Tests asserting the bootstrap's own modeling choices. When an agreed fix contradicts one, update the test in the same change.
- Generated research files (for example `.bootstrap-artifacts/`) that nothing at runtime reads.

## Baseline Check

These settings make a repository run the same on Windows, macOS, Linux and CI. Older and bootstrapped repositories often miss some. When you work in a repository, check them; for each one missing, explain it to the user in one sentence and fix it only with their approval, as a separate commit from the content work:

| Check | Fix |
| --- | --- |
| `worai` is in the dev dependency group | `uv add --dev "worai>=<version>"` (`graph-sync-project` `references/cli-resolution.md`) |
| Custom postprocessors with `wordlift-sdk` >= 8.5.0 depend on `wordlift-sdk[all]` | `uv add "wordlift-sdk[all]>=<current>,<9.0.0"` |
| The crawler profiles set `ingest_timeout_ms = 600000` | Add or uncomment it in `[profiles._base]` |
| `ingest_loader` is not the retired `web_scrape_api` | Switch to `crawler` (`graph-sync-project` `references/crawler.md`) |
| The committed `postprocessor_runtime` is `persistent` | Restore `persistent` |
| No route sends URLs to a mapping that emits nothing | Remove the URLs from the source instead |
| `.gitignore` covers `.env`, `.env.*` (except `.env.example`), `.config/`, `output/` | Add the missing lines |
| `pyproject.toml` has no `[tool.setuptools] packages = []` | `[tool.setuptools.packages.find]` with `where = ["src"]` |
| Shell scripts keep LF line endings on Windows checkouts | `.gitattributes` with `*.sh text eol=lf` |

Never change `canonical_id_strategy` or a page's root type as part of a baseline fix: both re-mint entity IRIs and leave the old entities in the graph (`graph-sync-project` `references/kg-checks.md`).

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

When a graph-sync CLI command is needed, do not assume `worai` is globally installed. Prefer the project-documented command first. Otherwise follow `graph-sync-project` `references/cli-resolution.md`: a sync runs `uv run worai ...` from the project environment (with `worai` in the dev group), never a `worai` from `PATH`, `pipx` or `uvx`, which lack the project's postprocessor package. Use the GitHub workflow or a user-provided validation path when local execution is not practical.

Ask before installing or fetching packages, and report which runner was used.

## Secret Hygiene

Before any commit or push:

- Inspect changed and staged files before staging broadly.
- Never stage `.env`, `.env.*` except intentional examples such as `.env.example`, `.codex/`, `.claude/settings.local.json`, `.gemini/`, `WORDLIFT.md` (wordlift-cli writes it into the folder it starts in), private keys, service-account JSON files, downloaded credentials, local provider configs, token dumps, or API response dumps.
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
