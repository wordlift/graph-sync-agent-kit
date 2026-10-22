# Graph Sync Postprocessors

Runtime details, the class contract and local testing live in `graph-sync-postprocessor-authoring` (`references/runtime.md`, `references/authoring.md`). The rules a project change must respect:

## Where They Run In The Chain

Per page: built-in root ID reconciler → custom postprocessors (manifest order) → built-in canonical IDs → built-in import annotation. A custom postprocessor sees staging IRIs on a first import and the existing canonical root on a re-sync.

## Manifest

- `profiles/<profile>/postprocessors.toml` **replaces** `profiles/_base/postprocessors.toml` for that profile; the two are never combined. A profile that needs the shared postprocessors plus its own lists all of them.
- `class = "package.module:ClassName"`, with the package under `src/`.

## Runtime Per Environment

- Commit `postprocessor_runtime = "persistent"` (CI). It runs workers in the manifest's `python` (default `./.venv/bin/python`).
- Local Windows runs use `inprocess` in a local config copy (`references/local-runs.md`); never commit it.

## When To Use One

- Prefer mappings and static templates; YARRRML on `worph` handles conditionals and string functions.
- Use a postprocessor for typed literals, list positions from scoped iterators, data outside the page (a Google Sheet, an external API), deduplication and cross-entity linking.
- Never as a way to read the page's own XHR responses or embedded JSON.
- Postprocessors change values and links between existing entities. They never create subjects or rename IRIs, and never emit static-template entities with partial properties.

## CI Secrets

A postprocessor that reads `os.environ` needs that variable as a repository secret **and** in the workflow step's `env:`. Postprocessors are written to skip silently on errors, so a missing secret leaves CI green while the feature writes nothing.
