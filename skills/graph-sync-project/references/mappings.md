# Graph Sync Mappings

## Mapping Configuration Contract
- Fallback mapping key:
  - `mapping` (default: `default.yarrrml`)
- Mapping base directory:
  - `mappings_dir` (default: `profiles/<profile_name>/mappings`)
- Route table:
  - `[[profiles.<name>.mappings]]`
  - required keys per route: `pattern`, `mapping`

## Mapping Selection Rules
- Callback mapping selection is profile-driven using `ProfileDefinition.resolve_mapping(url)`.
- Route matching target is URL path only (`urlparse(url).path`), not full URL/query/fragment.
- Route scan is ordered; first match wins.
- Policy constraints for XPath, sample-page hardcoding, and fallback authorization are defined in `references/policy.md`.
- Fallback behavior:
  - if no routes are defined, runtime behaves as implicit `pattern = ".*"` with `mapping`
  - if routes exist without `pattern = ".*"`, runtime appends that fallback
- Prefer no-op fallback mappings for unhandled URLs unless the project explicitly wants generic fallback output.
- Do not let fallback mappings emit generic `WebPage` entities as a substitute for content-cluster modeling.

## Mapping Path And Template Resolution
- Selected mapping path:
  - absolute paths are used as-is
  - relative paths resolve under `mappings_dir`
- Template variant resolution order:
  1. existing `.j2`/`.liquid` path as selected
  2. sibling `<file>.j2`
  3. sibling `<file>.liquid`
  4. plain file

## Required And Optional Extraction
- Classify important fields as required or optional during cluster modeling.
- Use selective sources for fields that may be absent, so missing selectors do not emit empty literals or malformed IRIs.
- Use root/page-level iterators only for triples guaranteed by the page contract, such as the primary entity skeleton.
- Keep optional entity IRIs guarded by the source that proves the entity exists.
- For creative works, treat authorship as expected unless the user accepts otherwise; missing authorship should be caught in validation and resolved with a better selector, another observed source, or an explicitly approved fallback.

## Postprocessor Escalation
- Use YARRRML for stable scalar extraction, simple repeatable fields, and entity skeletons.
- Escalate to a postprocessor when extraction needs rich text cleanup, nested entity construction, API/XHR enrichment, deduplication, validation, or shared logic across pages.
- Do not add a postprocessor just because XPath is possible; use one when the mapping output would otherwise be brittle, flattened, or hard to validate.

## Canonicalizer-Friendly IDs
- Treat dynamic YARRRML subject IRIs as staging IDs; final entity IRIs are normalized by the canonical ID postprocessor.
- Prefer simple staging subjects such as `__URL__`, `__URL__#article`, or `__URL__#<entity>` over canonical-link XPath expressions.
- Ensure each root entity has a useful schema.org type, `schema:url`, and `schema:name`/`schema:headline`, because these feed canonical ID generation.
