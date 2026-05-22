# Graph Sync Static Templates

## Templates Directory
- Static template source directory is `templates_dir`.
- Default `templates_dir`: `profiles/<profile_name>/templates`.

## Exports Loading
- Runtime loads profile exports from profile directory in this order:
  1. `exports.toml`
  2. `exports.toml.j2`
  3. `exports.toml.liquid`
- If no exports manifest exists, `exports` is `{}`.

## Static RDF Reification
- Runtime scans files in `templates_dir` and reifies files whose RDF format can be inferred.
- Supported forms include:
  - plain RDF files (for example `.ttl`, `.jsonld`)
  - templated RDF files (for example `.ttl.j2`, `.ttl.liquid`)
- Render/reify context includes:
  - `account`
  - `dataset_uri`
  - `exports`

## Patch Timing
- Static template graph is patched once per protocol lifecycle, before page mappings.
- First callback triggers static template patching.
- Subsequent callbacks in the same run skip static template patching.

## Debug Output
- In `--debug`, static templates graph is written to:
  - `output/debug_cloud/<profile>/static_templates.ttl`

## Exports vs Mapping Variables
- Use `exports.toml` (or templated exports) for reusable profile-level constants and computed values.
- Use mapping template variables (`account`, `dataset_uri`, `exports`) for mapping-local rendering.
- Prefer `exports` when multiple mappings or postprocessors need the same derived values.
