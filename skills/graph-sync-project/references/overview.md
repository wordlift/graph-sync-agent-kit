# Graph Sync Overview

## Purpose
- Provide stable context for coding agents working on `worai graph sync`.
- Prevent configuration and behavior drift from SDK runtime semantics.

## Project Contract
- Primary workflow: run the project-documented graph-sync command for the selected profile. Do not assume `worai` is globally installed; use `references/cli-resolution.md` before running CLI commands.
- Profile config section: `[profiles.<name>]` in `worai.toml`.
- Selected profile must define `api_key`.
- SDK v8 cloud-flow contract requires explicit ingestion config in profile/base settings:
  - `ingest_source` (`urls|sitemap|sheets`)
  - `ingest_loader`
  - optional `ingest_timeout_ms`
- Treat `wordlift-sdk` as the source of truth for supported `worai.toml` profile/config keys. Check `pyproject.toml`, `uv.lock`, or the active environment before assuming config semantics.
- Treat `worai` primarily as the graph-sync command runner; verify its command shape separately through `references/cli-resolution.md`.
- Current template baseline is `wordlift-sdk>=8.2.1,<9.0.0`.
- Generated GitHub Actions workflow keeps `wordlift/graph-sync@v6` and pins the `worai` binary through `worai_version`.

## Callback Processing Order (Per URL)
1. Validate callback payload (`errors`, HTML availability, root ID).
2. Patch static templates once (if not already done in this protocol lifecycle).
3. Resolve page mapping from route/fallback rules.
4. Resolve and render mapping template (`plain` / `.j2` / `.liquid`).
5. Apply mapping to page HTML and produce graph.
6. Reconcile root `WebPage` IRI with callback `response.id`.
7. Apply built-in canonical ID pass.
8. Apply configured custom postprocessors in loaded order.
9. Write debug TTL for page graph when debug is enabled.
10. Patch final graph to WordLift.

## Recommended Repository Layout
```text
worai.toml
profiles/<profile_name>/mappings/
  default.yarrrml
  product.yarrrml
  product.yarrrml.j2
profiles/<profile_name>/templates/
  exports.toml
  static.ttl
profiles/_base/
  postprocessors.toml
profiles/<profile_name>/
  postprocessors.toml
```

## Related Skill References
- `references/policy.md`
- `references/mappings.md`
- `references/static-templates.md`
- `references/postprocessors.md`
- `references/troubleshooting.md`
- `references/ci-checklist.md`
