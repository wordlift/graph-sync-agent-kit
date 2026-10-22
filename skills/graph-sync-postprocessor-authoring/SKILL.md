---
name: graph-sync-postprocessor-authoring
description: "Custom postprocessor authoring workflow for WordLift graph-sync projects. Use when creating, editing, testing, or debugging graph-sync postprocessors, postprocessor manifests, runtimes (persistent, oneshot, inprocess) on Windows/macOS/Linux and CI, SDK runner invocations, context payload usage, or postprocessor failure artifacts."
---

# Graph Sync Postprocessor Authoring

## Overview

Use this skill to create, modify, test, or debug custom postprocessors for WordLift graph-sync projects.

Read `references/runtime.md` for the chain order, manifest selection, runtimes per platform, context fields, and failure artifacts. Read `references/authoring.md` for the class contract, what a postprocessor may change, data sources, and local testing.

## Authoring Workflow

When creating or editing a postprocessor:

- Prefer mappings and static templates first; use postprocessors only when transformation logic cannot be modeled cleanly there (typed literals, positions from scoped iterators, data outside the page, deduplication, cross-entity linking).
- Change values and links between existing entities; never create subjects or build IRIs from strings. When a node must come from a postprocessor, mint it with `context.ids` and test a second sync of a changed page.
- Never emit static-template entities (`Organization`, `WebSite`) with partial properties.
- Keep transforms idempotent and deterministic.
- Preserve expected root `WebPage` identity behavior.
- Avoid deleting unrelated triples unless explicitly intended.
- Avoid logging secrets from context payloads.
- Read only context fields every runtime provides (`references/runtime.md`).
- Do not rely on constants from sample pages.
- Do not add hardcoded fallbacks unless explicitly authorized.
- Never read embedded JSON or the page's XHR endpoints; external APIs and sheets are fine, with their secrets forwarded in the workflow `env:`.

## Manifest Workflow

When editing manifests:

- A profile's `postprocessors.toml` replaces `_base`'s; the two are never combined (`references/runtime.md`).
- Use `class = "package.module:ClassName"`.
- Set `timeout_seconds`, `enabled`, and `keep_temp_on_error` intentionally.
- Keep the committed `postprocessor_runtime = "persistent"` and the manifest's `python = "./.venv/bin/python"`; local Windows runs switch to `inprocess` in a local config copy instead (`graph-sync-project` `references/local-runs.md`).
- Confirm the project environment can import the target class: `uv run python -c "import <package.module>"`.

## Testing Workflow

Use the SDK's one-shot runner for local validation. Resolve the Python runner before executing it:

- Prefer the project-documented postprocessor test command.
- Prefer `uv run python -m ...` when the project uses `uv`; it works the same on every OS.
- Use the project virtual environment's Python directly only when `uv` is unavailable (`.venv/bin/python` on macOS/Linux, `.venv\Scripts\python.exe` on Windows).
- Use active `python -m ...` only after confirming it can import `wordlift_sdk`.
- Ask before installing/fetching Python packages.

```bash
uv run python -m wordlift_sdk.kg_build.postprocessors.oneshot \
  --class my_project.postprocessors:IntegerPositionsPostprocessor \
  --input-graph ./tmp/input_graph.nq \
  --output-graph ./tmp/output_graph.nq \
  --context ./tmp/context.json
```

Inspect:

- Output graph existence.
- Expected triples.
- Idempotence on repeated runs.
- Failure artifacts under `output/postprocessor_debug/` when `keep_temp_on_error = true`.

Then run a real sync of a few pages, and a second one after a content change when the postprocessor touches entity identity.

## Compatibility

For SDK 5.1.1+:

- Do not use `context.settings`; read config from `context.profile`.
- Do not expect `context.account.key`; use `context.account_key`.
- `context.account` is the full `/me` payload only under `inprocess`; under `persistent` / `oneshot` it carries `dataset_uri`, `country_code` and `language`.
