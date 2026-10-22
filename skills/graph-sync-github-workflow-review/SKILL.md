---
name: graph-sync-github-workflow-review
description: "GitHub Actions review workflow for WordLift graph-sync projects. Use when reviewing or optimizing graph-sync workflow files, reusable workflow inputs, profile dispatch and the orchestrator, secrets, caching, CI runtime, GitHub Actions cost, reliability, or required quality gates."
---

# Graph Sync GitHub Workflow Review

## Overview

Use this skill to review graph-sync GitHub Actions workflows for reliability, speed, cost, and governance while preserving quality gates.

Use `graph-sync-project` when workflow changes affect runtime project contracts or docs/specs.

## How CI Runs A Sync

- The generated `.github/workflows/graph-sync.yml` runs `uv sync --locked --no-dev`, then `wordlift/graph-sync@v6`.
- The action installs its own `worai` (with the latest compatible `wordlift-sdk`) into **system Python** and runs it there. The project's `uv.lock` applies only to the `persistent` postprocessor workers, which run in `./.venv/bin/python`.
- `@v6` tracks the latest `v6.x.y` release. The action selects its compatible `worai`; pin `worai_version` only to debug a regression.
- The graph-sync orchestrator (`graph-sync-orchestrator`, maintained by the WordLift tech team) dispatches each `(repository, profile)` from its `sync-targets.json` through `workflow_dispatch`.

## Review Focus

Check:

- **Profile options.** Every profile in `worai.toml` that should run on CI is in the `profile` input's `options` list and in the `all` matrix. The `options` list gates the orchestrator: GitHub rejects a dispatch whose profile isn't listed (HTTP 422), and the orchestrator job fails with `Failed to dispatch workflow`. The orchestrator finds its run by a job named `… (<profile>)`, which the matrix produces.
- **Secrets.** Every secret the sync or a postprocessor reads is a repository secret **and** a line in the graph-sync step's `env:` block. A secret missing from `env:` is invisible to the job; postprocessors skip silently, so CI stays green while the feature writes nothing. No secret the sync doesn't read.
- **Local-only profiles.** worai resolves every profile's `${VAR}` on every run, so a variable used only by a local test profile needs a placeholder in `env:` (with a comment), or every CI run fails.
- **Sheets.** A `sheets` source needs the `SHEETS_SERVICE_ACCOUNT` secret holding the service-account JSON **content**.
- `PIP_BREAK_SYSTEM_PACKAGES: "1"` in the step's `env:` (Ubuntu 24.04+ runners mark system Python as externally managed).
- The committed `worai.toml` has `postprocessor_runtime = "persistent"`, never `inprocess` (every URL fails on CI with `No module named '<project_package>'`).
- With custom postprocessors and `wordlift-sdk` >= 8.5.0 in the lock, the dependency is `wordlift-sdk[all]` (otherwise every URL fails with `No module named 'regex'`).
- Workflow triggers, `workflow_call` inputs and path filters.
- Dependency setup and cache configuration (`astral-sh/setup-uv` with Python 3.12, cache keyed on `pyproject.toml` and `uv.lock`).
- Job timeouts and concurrency. With one concurrency group per repository, GitHub keeps one pending run: when one profile runs longer than the orchestrator's dispatch gap, the next pending profile is cancelled by the one after it. Report it; sequencing belongs to the orchestrator.
- Artifact upload behavior (debug output when useful) and the KPI step (`graph_kpis_enabled`).
- Least-privilege `permissions`.
- CI signal quality and cost impact.

## Reading A Failing Run

- The step summary carries the run report; failed URLs and their errors are listed there.
- `Successes: 0` with the same error on every URL is a configuration problem (runtime, missing extra, missing secret), not the site.
- A failing run still writes the static templates first, so it can revert template edits that were only synced locally.

## Process

When reviewing:

- Read the workflow file and relevant project docs.
- Identify reliability risks first.
- Identify unnecessary runtime or compute waste.
- Recommend measurable improvements.
- Avoid weakening required checks unless the user explicitly approves it.
- Keep workflow changes observable through logs, summaries, or artifacts.
- Changes to the orchestrator or to repository secrets need the WordLift tech team when the user lacks access: give the user a message to forward.

## Output

For reviews, lead with findings ordered by severity. Include file/line references when possible, then list open questions and a short summary.
