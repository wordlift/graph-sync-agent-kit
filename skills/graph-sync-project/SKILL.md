---
name: graph-sync-project
description: "Technical implementation workflow for WordLift graph-sync projects. Use when editing or reviewing graph-sync project files, worai.toml profiles, sources and profiles, crawler modes, mappings, static templates, postprocessor manifests, runtime behavior, running syncs locally on Windows/macOS/Linux, checking results in the knowledge graph, troubleshooting, tests, docs/spec synchronization, or CI smoke contracts."
---

# Graph Sync Project

## Overview

Use this skill for technical implementation work in WordLift graph-sync repositories. It covers runtime configuration, mappings, static templates, postprocessor behavior, troubleshooting, verification, and docs/spec synchronization.

For semantic prioritization and cluster curation, use `graph-sync-curator`. For repo creation, commit, and push workflows, use `graph-sync-repo-lifecycle`.

## Start Protocol

Before editing:

- Read only the focused references needed for the task.
- Ground decisions in observed repository behavior and source evidence.
- Do not change runtime semantics without explicit approval.
- Keep docs/specs aligned when user-facing or contract behavior changes.

Always load `references/policy.md` for policy-sensitive graph modeling or mapping work.

## Task Routing

- General runtime contract: read `references/overview.md`.
- `worai.toml` keys and starting values: read `references/config.md`.
- Sources, profiles, Google Sheets tabs and credentials, registering a profile: read `references/sources-and-profiles.md`.
- Loaders, crawler modes, cost and cache: read `references/crawler.md`.
- Running a sync on a laptop (any OS), reports, what CI does differently: read `references/local-runs.md`.
- Knowledge graph checks around a sync (which account, did the pages land, twins, leftover entities, temporary accounts): read `references/kg-checks.md`. Other knowledge graph work (an empty API link, GraphQL, patching, exports): the `wordlift-kg` skill when installed.
- Graph-sync CLI commands or smoke checks: read `references/cli-resolution.md`.
- Mapping selection/config behavior, page identity, staging subjects: read `references/mappings.md`.
- Static template/export behavior and the homepage: read `references/static-templates.md`.
- Postprocessor runtime behavior: read `references/postprocessors.md`.
- Runtime failures and regressions: read `references/troubleshooting.md`.
- CI/smoke contract changes: read `references/ci-checklist.md` and consider `graph-sync-github-workflow-review`.
- Custom postprocessor authoring: use `graph-sync-postprocessor-authoring`.
- YARRRML/RML mapping review: use `graph-sync-yarrrml-review`.

## Scripts

Standard-library Python scripts in this skill's `scripts/` folder. Run them from the graph-sync repository root with the project environment (`uv run python <this skill>/scripts/<script> ...`); they read the API key from the profile, `.env` or the environment and never print it.

- `scripts/fetch_page.py`: fetch pages exactly as a sync does (crawler, the profile's modes and key), probe the cheapest working mode, save the HTML and its XHTML conversion under `output/fetch/`, evaluate XPath like a mapping (`references/crawler.md`).
- `scripts/kg_check.py`: `account`, `page`, `types`, `twins`, `clear-cache` (`references/kg-checks.md`). Read-only apart from the cache clear.

## Change Protocol

When editing project files:

- Confirm current behavior from relevant references and local source.
- Propose or perform the smallest change set that satisfies the request.
- Update code and tests together when behavior changes.
- Update impacted docs/specs in the same change.
- Keep unrelated refactors out of the change.
- Do not mark work complete without validation.

## Verification

Use tiered validation. Prefer the project-documented validation command first.

Default checks when the project uses `uv`:

```bash
uv run pytest
```

When applicable, also run:

```bash
uv run ruff check .
```

Do not assume `uv`, `pytest`, or `ruff` are globally installed. If the default commands fail because the runner is unavailable, use the project-documented validation command, the active virtual environment, or ask before installing/fetching tooling.

If tests are absent or not meaningful, use a graph-sync CLI smoke check and the project-specific sync/audit path agreed with the user. Resolve the CLI through `references/cli-resolution.md`; do not assume bare `worai` is installed globally.

Before a real sync, check the mapping on fetched pages (`scripts/fetch_page.py --xpath`), confirm the target account with the user (`scripts/kg_check.py account`), then run with `--debug --output-dir output` and follow `references/local-runs.md` for the operating system in use.

For graph-sync runtime changes, verify the affected behavior:

- Mapping route resolution and fallback.
- Relative and absolute mapping path resolution.
- Mapping template variant resolution.
- Static template patching once per run.
- Postprocessor load order and execution.
- Debug artifact paths.
- CLI contract for graph-sync run/create flows.

## Handoff

Summarize:

- What changed.
- Why it changed.
- What validation ran.
- Remaining risks or warnings.

If work is tested and accepted, inspect `git status`. When project changes exist, explicitly ask whether to prepare a commit handoff through `graph-sync-repo-lifecycle`; if no project changes exist, say there is nothing to commit. Require explicit user confirmation before commits or remote pushes.
