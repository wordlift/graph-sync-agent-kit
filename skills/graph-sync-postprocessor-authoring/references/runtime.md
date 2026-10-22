# Graph Sync Postprocessors Runtime

## Place In The Chain

Per page, after the mapping is materialized:

1. `root_id_reconciler` (built-in): on a re-sync, swaps the page root's staging IRI for its existing canonical IRI (`context.existing_web_page_id`). Only a root typed exactly `schema:WebPage` is swapped.
2. Custom postprocessors, in manifest order.
3. `canonical_ids` (built-in): rewrites staging IRIs into canonical ones, nesting children under their parents.
4. `import_annotation` (built-in): stamps import metadata (`seovoc:importHash` and others).

Then SHACL validation, the import-hash check and the write.

## Manifest Location

- The runtime reads **one** manifest per profile: `profiles/<profile_name>/postprocessors.toml` when it exists, otherwise `profiles/_base/postprocessors.toml`. A profile manifest replaces `_base`'s; entries are never combined, so a profile that needs the shared postprocessors lists them again.
- Enabled entries run in file order. A disabled entry is not loaded.

## Runtimes

`postprocessor_runtime` in `worai.toml` (the SDK default without any setting is `oneshot`; generated projects set `persistent`):

| Runtime | How it runs | Where it works |
| --- | --- | --- |
| `persistent` | One long-lived worker subprocess per postprocessor: `<python> -m wordlift_sdk.kg_build.postprocessors.persistent` | CI and macOS/Linux. **Commit this.** |
| `oneshot` | A new subprocess per page: `<python> -m wordlift_sdk.kg_build.postprocessors.oneshot` | Slow; same platforms as `persistent`. |
| `inprocess` | Inside the `worai` process, no subprocess | Local Windows runs only, from a local config copy; never commit. |

- Subprocess runtimes pass the graph as N-Quads and read the result back as N-Quads. A non-zero exit, a timeout or a missing output graph fails that page.
- On Windows the subprocess runtimes fail with `[WinError 2]` (no `./.venv/bin/python`) or `[WinError 10038]` (the SDK reads the worker pipe with `select()`, which Windows supports only on sockets). Use `inprocess` there (`graph-sync-project` `references/local-runs.md`).
- `inprocess` is accepted only in `[profiles._base]`; worai rejects it in a named profile. It imports the project package into the `worai` process, so `worai` must run from the project environment. On CI, `worai` runs from system Python, where that import fails for every page.
- `postprocessor_runtime` can be set per profile (`persistent` or `oneshot`).

## Manifest Contract

- Global defaults in the manifest:
  - `python` default: `"./.venv/bin/python"` (the Linux/macOS path; it doesn't exist on Windows)
  - `timeout_seconds` default: `120`
  - `enabled` default: `true`
  - `keep_temp_on_error` default: `false`
- Per-entry required:
  - `class = "package.module:ClassName"`
- Per-entry optional overrides:
  - `python`
  - `timeout_seconds`
  - `enabled`
  - `keep_temp_on_error`
- `python` must keep the `./` prefix and is resolved from the directory `worai` is launched in: run from the repository root.

## Context Passed To Postprocessors

| Field | Content |
| --- | --- |
| `profile_name` | Active profile |
| `profile` | Resolved, interpolated profile; settings under `profile["settings"]` (`api_url` defaults to `https://api.wordlift.io`) |
| `url` | Page URL |
| `account` | Under `persistent` / `oneshot`: only `dataset_uri`, `country_code`, `language`. Under `inprocess`: the full `/me` account object |
| `account_key` | The account's API key |
| `exports` | Values from `exports.toml.j2` |
| `response` | `id`, `web_page.url`, `web_page.html` (the fetched HTML) |
| `existing_web_page_id` | The page root's existing IRI on a re-sync, else `None` |
| `existing_import_hash`, `import_hash_mode` | Real values only under `inprocess`; the subprocess runtimes always see `None` / `"on"` |
| `ids` | `IdAllocator` for deterministic child IRIs, when the dataset URI is known |

Read only the fields every runtime provides. Code that reads other `account` attributes (`url`, `features`, …) works in a local Windows run (`inprocess`) and fails every page on CI (`persistent`) with an `AttributeError`. Under `inprocess` the account object also carries the API key (`account.key`): never log it.

## SDK 5.1.1+ Compatibility Note

- `context.settings` is removed; read config from `context.profile`.
- `context.account.key` is not injected; use `context.account_key`.

## Manifest Example

```toml
# profiles/_base/postprocessors.toml
python = "./.venv/bin/python"
timeout_seconds = 120
enabled = true
keep_temp_on_error = false

[[postprocessors]]
class = "graph_sync_example_com.postprocessors.positions:ListPositionsPostprocessor"

[[postprocessors]]
class = "graph_sync_example_com.postprocessors.faq_from_sheet:FaqFromSheetPostprocessor"
enabled = true
timeout_seconds = 60
keep_temp_on_error = true
```

## Failure Artifacts

- If `keep_temp_on_error = true`, a failing subprocess run copies its temp files (input graph, context with the key redacted) to:
  - `output/postprocessor_debug/<class_path_sanitized>/`
