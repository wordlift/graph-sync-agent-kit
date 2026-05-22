# Content Cluster Workflow

Use this workflow for each prioritized dynamic content cluster.

## Sample

- Select representative URLs from the cluster.
- Include edge cases when obvious, such as missing media, missing author, pagination, or sparse content.
- Use Playwright or available browser tooling when page behavior requires rendering.
- Inspect XHR/network traffic before finalizing extraction.
- Prefer stable upstream data over brittle HTML selectors when available.

## Model

- Choose the most specific useful schema.org type.
- Avoid generic `WebPage` when a more specific entity type is available.
- Do not add Breadcrumbs markup by default.
- Connect the main entity to static entities such as `WebSite`, `Organization`, `Person`, `Brand`, or `Place`.
- Add authorship markup for creative works whenever possible.
- Add `FAQPage` when question/answer content exists.
- Connect FAQ entities to the main entity with `schema:about` and `schema:subjectOf` where appropriate.
- Add videos as `VideoObject` and connect them to the main entity.
- Add ratings, collections, and sharing actions when observed and supported.

## Implement

- Prefer static templates for stable static entities.
- Prefer YARRRML mappings for repeatable extraction.
- Use postprocessors only when mapping/static-template approaches cannot express the needed behavior cleanly.
- Keep mappings generalized across the configured source pages.
- Avoid sample-page constants and hardcoded fallbacks.

## Review

- Inspect generated graph output.
- Check for duplicate entities.
- Check URL literals.
- Check explicit IRIs.
- Check that entity type matches page intent.
- Check connections to static entities.
- Check FAQ/video/authorship completeness.
