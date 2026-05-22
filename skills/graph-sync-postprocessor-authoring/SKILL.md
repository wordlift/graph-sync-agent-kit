---
name: graph-sync-postprocessor-authoring
description: "Custom postprocessor authoring workflow for WordLift graph-sync projects. Use when creating, editing, testing, or debugging graph-sync postprocessors, postprocessor manifests, SDK runner invocations, context payload usage, or postprocessor failure artifacts."
---

# Graph Sync Postprocessor Authoring

## Overview

Use this skill to create, modify, test, or debug custom postprocessors for WordLift graph-sync projects.

Read `references/runtime.md` for runtime loading, manifest behavior, context fields, and failure artifacts. Read `references/authoring.md` for the class contract, minimal example, and local runner workflow.

## Authoring Workflow

When creating or editing a postprocessor:

- Prefer mappings and static templates first; use postprocessors only when transformation logic cannot be modeled cleanly there.
- Keep transforms idempotent and deterministic.
- Preserve expected root `WebPage` identity behavior.
- Avoid deleting unrelated triples unless explicitly intended.
- Avoid logging secrets from context payloads.
- Do not rely on constants from sample pages.
- Do not add hardcoded fallbacks unless explicitly authorized.

## Manifest Workflow

When editing manifests:

- Load `_base` and profile manifest behavior from `references/runtime.md`.
- Keep `_base` postprocessors before profile postprocessors.
- Use `class = "package.module:ClassName"`.
- Set `timeout_seconds`, `enabled`, and `keep_temp_on_error` intentionally.
- Confirm the configured Python environment can import the target class.

## Testing Workflow

Use the SDK runner for local validation when possible. Resolve the Python runner before executing it:

- Prefer the project-documented postprocessor test command.
- Prefer `uv run python -m ...` when the project uses `uv`.
- Use `.venv/bin/python -m ...` when the project has a local virtual environment.
- Use active `python -m ...` only after confirming it can import `wordlift_sdk`.
- Ask before installing/fetching Python packages.

```bash
python -m wordlift_sdk.kg_build.postprocessor_runner \
  --class my_project.postprocessors:AddSimpleNameFallback \
  --input-graph ./tmp/input_graph.nq \
  --output-graph ./tmp/output_graph.nq \
  --context ./tmp/context.json
```

Inspect:

- Output graph existence.
- Expected triples.
- Idempotence on repeated runs.
- Failure artifacts under `output/postprocessor_debug/` when `keep_temp_on_error = true`.

## Compatibility

For SDK 5.1.1+:

- Do not use `context.settings`; read config from `context.profile`.
- Do not expect `context.account.key`; use `context.account_key`.
- Keep `context.account` as the clean `/me` account payload.
