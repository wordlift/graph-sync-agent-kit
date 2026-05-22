# Graph Sync Postprocessors Runtime

## Manifest Locations And Load Order
- Runtime loads postprocessors from:
  1. `profiles/_base/postprocessors.toml`
  2. `profiles/<profile_name>/postprocessors.toml`
- Enabled entries from `_base` run first, then enabled profile entries.

## Execution Model
- Each postprocessor runs in a subprocess:
  - `<python> -m wordlift_sdk.kg_build.postprocessor_runner`
- Graph handoff format:
  - input graph serialized as N-Quads
  - output graph read from N-Quads
- Non-zero exit code or missing output graph fails callback processing.

## Manifest Contract
- Global defaults in manifest:
  - `python` default: `"./.venv/bin/python"`
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

## Context Passed To Postprocessors
- `profile_name`
- `url`
- `dataset_uri`
- `country_code`
- `exports`
- `profile` (resolved/interpolated profile object)
- `account_key` (runtime auth key)
- `account` (`/me` account payload without injected `key`)
- callback response payload (`id`, `web_page.url`, `web_page.html`)
- `ids` allocator when dataset URI is available

## SDK 5.1.1+ Compatibility Note
- `context.settings` is removed; read config from `context.profile`.
- `context.account.key` is not injected; use `context.account_key`.

## Template Example Dependency Note
- The bundled YouTube example postprocessor (`src/wl1506345_graph_sync/postprocessors/youtube.py`) uses `lxml` for HTML iframe parsing.

## Manifest Example
```toml
# profiles/_base/postprocessors.toml
python = "./.venv/bin/python"
timeout_seconds = 120
enabled = true
keep_temp_on_error = false

[[postprocessors]]
class = "my_project.postprocessors:NormalizeProductIds"

[[postprocessors]]
class = "my_project.postprocessors:DropInvalidOffers"
enabled = true
timeout_seconds = 60
keep_temp_on_error = true
```

## Failure Artifacts
- If `keep_temp_on_error = true`, runtime copies temp artifacts to:
  - `output/postprocessor_debug/<class_path_sanitized>/`
