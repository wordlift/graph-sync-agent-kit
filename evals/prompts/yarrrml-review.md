# Eval: YARRRML Review

Use `$graph-sync-yarrrml-review`.

Review a graph-sync YARRRML mapping for correctness and maintainability.

Requirements:

- Check selector robustness.
- Confirm relative XPath use.
- Check route/fallback compatibility.
- Look for duplicate mappings.
- Check that emitted schema.org output uses explicit IRIs and URL literals.
- Identify brittle assumptions based on sample pages.

Expected output:

- Findings ordered by severity.
- File/line references where possible.
- Suggested fixes.
- Residual risks.
