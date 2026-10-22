# Graph Sync Troubleshooting

Start from `output/graph_sync_failures.csv` (`--output-dir output`, `references/local-runs.md`): it lists each failed URL with its error. To tell a fetch problem from a mapping problem, fetch one failing URL with `scripts/fetch_page.py` and evaluate the mapping's selectors with `--xpath`.

## Run Fails Before Any Page

| Error | Cause and fix |
| --- | --- |
| `ProfileConfigError: Missing environment variable 'VAR' for profile '<other>'` | Every profile's `${VAR}` is resolved on every run. Set the variable (a placeholder is enough when that profile isn't run). |
| `Exactly one source is required` | The profile inherits a source key from `_base` and sets another. Keep source keys out of `_base` when profiles use different sources. |
| `INGEST_SOURCE` / `INGEST_LOADER` errors | Set `ingest_source` (`urls`, `sitemap`, `sheets`) and `ingest_loader` explicitly; don't rely on the legacy `web_page_import_mode` / `web_page_import_timeout`. |
| `'dict object' has no attribute '…'` | The profile has no `exports.toml.j2` with that key; put shared exports in `profiles/_base/`. |
| A key in `worai.toml` has no effect | It is written after a `[[profiles.<name>.mappings]]` table, so it belongs to that route. Move it above the routes. |
| `ValueError` about `postprocessor_runtime` | `inprocess` is only accepted in `[profiles._base]`. |
| A Sheets source returns 401/403 or "file not found" | The service-account file is missing or the sheet isn't shared with its `client_email`. Ask the WordLift tech team; never switch the source (`references/sources-and-profiles.md`). |

## Every URL Fails

| Error | Cause and fix |
| --- | --- |
| `No module named '<project_package>'` locally | `worai` doesn't run from the project environment; add it to the dev group (`references/local-runs.md`). |
| `No module named '<project_package>'` on CI | `postprocessor_runtime = "inprocess"` was committed. Commit `persistent`. |
| `No module named 'regex'` on CI | SDK >= 8.5.0 without the `all` extra and custom postprocessors. Depend on `wordlift-sdk[all]`. |
| `[WinError 2]` or `[WinError 10038]` | `persistent` postprocessors on Windows. Use `inprocess` in a local config copy. |
| `UnicodeEncodeError: 'charmap'` / `UnicodeDecodeError: 'utf-8'` | Windows default encoding; set `PYTHONUTF8=1`. |
| `BrokenProcessPool` | `mapping_pool_size` too high on Windows; use 6 or lower. |
| `Crawler API error 412` / `403 … Access to host` | The account's Website URL is missing or another host (`references/kg-checks.md`). |
| `INGEST_LOAD_NETWORK_ERROR` | `ingest_timeout_ms` unset; set `600000` (`references/crawler.md`). |

## Some URLs Fail

| Error | Cause and fix |
| --- | --- |
| `No JSON-LD nodes produced` | The URL's mapping emitted nothing: wrong route, the page's template differs, or the fetched page lacks the content (wrong crawler mode). Fetch it with `fetch_page.py` and test the iterator. If the page should not be mapped, remove it from the source. |
| `INGEST_LOAD_NETWORK_ERROR`, 403/429 from the site | Timeout or blocking: see `references/crawler.md`. |
| Failed to convert HTML to XHTML | The page's HTML is broken beyond the SDK's repair; check it with `fetch_page.py` (it reports the same conversion error). |
| Postprocessor timeout | Increase `timeout_seconds` in the manifest, or make the postprocessor cheaper. |
| `Postprocessor did not produce output graph` | The postprocessor crashed; set `keep_temp_on_error = true` and read `output/postprocessor_debug/<class>/`. |

## The Run Is Green But The Data Is Wrong

| Symptom | Cause |
| --- | --- |
| A property is missing on some pages | Its selector doesn't match those pages, the wrong crawler mode is cached for them, or a `replace()` / `tokenize()` pattern can match an empty string (`worph` drops the value without failing). |
| An empty `""` value | `normalize-space()` of a missing node; filter on presence (`graph-sync-yarrrml-review`). |
| A number written as a strange entity | A `datatype:` other than `xsd:string` in the mapping (`references/mappings.md`). |
| Twins (two entities, same URL and type) | A title change, a type change, two first-level entities on one URL, or fragment subjects (`references/kg-checks.md`). |
| Children re-minted as generic root entities after a re-sync | The page root is plain `WebPage`, children use fragment subjects, or a postprocessor minted IRIs. |
| A template entity reverted to a stub | A page graph emits it with partial properties (`references/static-templates.md`). |
| A postprocessor's output is missing on CI only | Its secret is not in the workflow `env:`. |
| The API link still shows old data | The account cache: run `kg_check.py clear-cache`. |
| Homepage entity not served | The trailing-slash mismatch (`references/static-templates.md`). |
| A page not in the graph at all | It isn't in the source, `url_regex` skipped it (anchored patterns skip URL variants silently), or the sitemap omits it. |

## Mapping Routes

- Routes match the URL path with `re.match`, first match wins; an unmatched URL gets the fallback mapping (`references/mappings.md`).
- Relative mapping paths resolve under `profiles/_base/mappings/` and `profiles/<name>/mappings/`.
- `.j2` / `.liquid` render errors: check the variable names (`dataset_uri`, `account`, `exports`).

## Postprocessor Context (SDK 5.1.1+)

- `context.settings` was removed: use `context.profile`.
- `context.account.key` is not injected: use `context.account_key`.

## Debug Artifacts

- Static templates: `output/debug_cloud/<profile>/static_templates.ttl`
- Per page: `output/debug_cloud/<profile>/cloud_<sha256(url)>.ttl`
- Postprocessor failures with `keep_temp_on_error = true`: `output/postprocessor_debug/<class_path_sanitized>/`
- Fetched pages: `output/fetch/` (`scripts/fetch_page.py`)
