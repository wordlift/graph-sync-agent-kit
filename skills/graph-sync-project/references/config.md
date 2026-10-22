# `worai.toml` Reference

`worai.toml` is the runtime configuration. `[profiles._base]` holds shared settings; each `[profiles.<name>]` inherits `_base` and overrides what it sets (`references/sources-and-profiles.md`). `wordlift-sdk` is the source of truth for supported keys: check the version in `uv.lock` before relying on a key.

## Starting Point

```toml
[profiles._base]
overwrite = true
graph_write_strategy = "put"
canonical_id_strategy = "dependency_graph"
materialization_backend = "worph"
postprocessor_runtime = "persistent"
ingest_loader = "crawler"
crawler_js_render_mode = "disabled"
crawler_proxy_mode = "disabled"
ingest_timeout_ms = 600000
concurrency = 10
mapping_pool_size = 6
shacl_pool_size = 7

[profiles.default]
api_key = "${WORDLIFT_API_KEY}"
ingest_source = "sitemap"
sitemap_url = "https://www.example.com/sitemap.xml"
url_regex = "^https://www\\.example\\.com/(?!.*\\.(?:avif|webp|png|jpe?g|gif|svg|ico|pdf|zip|css|js|xml)(?:\\?.*)?$).+"
mapping = "page.yarrrml"
```

These are the recommended values. The template generates lower pools (`concurrency = 4`, pools of 1) and leaves `ingest_timeout_ms` commented out, so many repositories have those. Leave `concurrency` as it is: it may be a deliberate limit for that site (rate limits, bot challenges). Raising the mapping and SHACL pools is generally safe.

## Sources

| Key | Meaning |
| --- | --- |
| `ingest_source` | `sitemap`, `sheets` or `urls`. Exactly one source per profile. |
| `sitemap_url` | Root sitemap, read recursively. A `file://` URL reads a sitemap committed to the repository. |
| `sitemap_url_pattern` | Regex on each sitemap URL (`re.search`). |
| `url_regex` | Regex on every source URL, any source (`re.search` on the URL exactly as listed). Filters assets and splits pages between profiles. |
| `urls` | A list in the file. Fine for a local test; a poor production source (every change is a commit). |
| `sheets_url`, `sheets_name`, `sheets_service_account` | Google Sheet, tab, service-account file (`references/sources-and-profiles.md`). |

`url_regex` sees the URL **as listed**, before any redirect, with no normalisation:

- An anchored pattern silently skips listed variants (`http://`, no `www`, a trailing slash, `?utm_…`, a fragment, an upper-case extension). They are only counted as skipped; nothing fails.
- A retired page that redirects to another page type still runs through this profile's mapping, on the redirect target's HTML.

Sitemaps include images, documents and assets: exclude them with `url_regex` before they cost a fetch and fail.

## Fetching

`ingest_loader`, `crawler_js_render_mode`, `crawler_proxy_mode`, `ingest_timeout_ms`: see `references/crawler.md`.

## Writing

| Key | Default | Meaning |
| --- | --- | --- |
| `graph_write_strategy` | `patch` | `put` writes each page's graph in one bulk request; `patch` writes entity by entity. |
| `overwrite` | `false` | `true` replaces entities; `false` adds new values to the old ones. |
| `import_hash_mode` | `on` | `on` skips pages whose graph didn't change since the last import; `write` always writes; `off` disables the hash. |

Keep `overwrite = true` with `graph_write_strategy = "put"` (the template default): each run replaces each page's graph. With `overwrite = false`, removed values accumulate forever. Even with `put`, entities that a page no longer emits are not deleted (`references/kg-checks.md`).

## Identity

| Key | Meaning |
| --- | --- |
| `canonical_id_strategy` | `dependency_graph` (template default): readable IRIs with children nested under their parents. Unset means `legacy`: no nesting, staging subjects kept as they are. |

Switching an existing repository's strategy re-mints every IRI and leaves every old entity in the graph: agree the switch with the user first (`references/kg-checks.md`).

## Pools And Runtime

| Key | Default | Meaning |
| --- | --- | --- |
| `concurrency` | 4 | Pages fetched in parallel. |
| `mapping_pool_size` | CPU count | Materialization workers. Keep it at 6 or lower on Windows. |
| `shacl_pool_size` | `concurrency / 2` | SHACL validation workers. |
| `postprocessor_pool_size` | `concurrency * 3/4` | Postprocessor workers. |
| `postprocessor_runtime` | `persistent` | Commit `persistent`. `inprocess` is for local Windows runs only (`references/local-runs.md`). |
| `materialization_backend` | `worph` | `worph` (default; XPath 2.0) or `morph` (morph-kgc fallback, XPath 1.0). |

## Validation

| Key | Meaning |
| --- | --- |
| `shacl_validate_mode` | `warn` (default) logs violations; `fail` fails the page; `off` skips. |
| `shacl_exclude_builtin_shapes` | Built-in shapes to skip, by name without `.ttl`. |
| `shacl_extra_shapes` | Extra shape files. |

A profile's `shacl_exclude_builtin_shapes` **replaces** the `_base` list, so repeat the `_base` entries. Typical exclusions: `google-carousel` / `google-carousels-beta` when list items link by URL without an `item`, `google-merchant-listing` when the site shows no price, `google-factcheck` when product reviews exist (it targets every `Review`).

## Mappings And Files

| Key | Default | Meaning |
| --- | --- | --- |
| `mapping` | `default.yarrrml` | The fallback mapping. |
| `[[profiles.<name>.mappings]]` | — | Routes: `pattern` + `mapping` (`references/mappings.md`). |
| `mappings_dir` | `profiles/<name>/mappings` | Mapping files; `profiles/_base/mappings` is searched as well. |
| `templates_dir` | `profiles/<name>/templates` | Static templates; `profiles/_base/templates` is searched as well. |

## TOML And Interpolation Traps

- `[[profiles.<name>.mappings]]` tables must come **after** every scalar key of that profile. A key written after them silently belongs to the last route table, and the SDK never sees it.
- Values support `${VAR}` from the environment and `.env`. Every profile's variables are resolved on every run, so an unset variable used by any profile fails all runs (`references/local-runs.md`).
- Named profiles replace lists and route tables from `_base`; they don't append to them.
