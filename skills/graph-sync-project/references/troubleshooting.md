# Graph Sync Troubleshooting

## Ingestion Source/Loader Resolution Errors
- Symptom:
  - runtime fails fast during ingestion setup (`INGEST_SOURCE` / `INGEST_LOADER` related errors).
- Check:
  - `ingest_source` is explicitly set to one of `urls|sitemap|sheets`.
  - `ingest_loader` is explicitly set (for example `crawler`, the template default).
  - do not rely on legacy fallback keys `web_page_import_mode` / `web_page_import_timeout`.

## Mapping Routes Do Not Match
- Symptom:
  - URL-specific mapping is never selected.
- Check:
  - patterns match URL path, not full URL.
  - route order is correct (first match wins).

## Unexpected Fallback Mapping
- Symptom:
  - unmatched URLs still resolve to a mapping.
- Cause:
  - runtime ensures fallback `.* -> mapping`.
- Check:
  - intended fallback `mapping` file and location.

## Mapping File Not Found
- Symptom:
  - mapping read/render failure.
- Check:
  - relative paths are resolved under `mappings_dir`.
  - absolute path usage is intentional and valid.

## Template Variable Errors
- Symptom:
  - `.j2` or `.liquid` rendering fails.
- Check:
  - required context keys exist (`dataset_uri`, `account`, `exports`, `profile` when needed).
  - template references valid variable names.

## Postprocessor Context Key Errors (SDK 5.1.1+)
- Symptom:
  - custom postprocessor crashes on missing `context.settings` or `context.account.key`.
- Check:
  - replace `context.settings` with `context.profile`.
  - replace `context.account.key` with `context.account_key`.
  - keep using `context.account` only for `/me` account fields.

## Postprocessor Class Import Failure
- Symptom:
  - subprocess exits with import/class error.
- Check:
  - `class` uses `package.module:ClassName`.
  - `python` points to env where your package is installed/importable.

## Postprocessor Timeout
- Symptom:
  - callback fails after timeout.
- Check:
  - increase `timeout_seconds` in manifest.
  - optimize expensive graph operations.

## Missing Postprocessor Output Graph
- Symptom:
  - runtime reports no output graph produced.
- Check:
  - processor does not crash.
  - runner writes output and processor returns `Graph` or `None`.

## Debug Artifacts
- Static template debug:
  - `output/debug_cloud/<profile>/static_templates.ttl`
- Per-page callback debug:
  - `output/debug_cloud/<profile>/cloud_<sha256(url)>.ttl`
- Postprocessor temp artifacts on failure:
  - `output/postprocessor_debug/<class_path_sanitized>/`
