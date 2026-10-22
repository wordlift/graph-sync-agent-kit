# Content Cluster Workflow

Use this workflow for each prioritized dynamic content cluster.

## Scope

- Work on one selected cluster at a time.
- Exclude URLs already handled by static templates or completed cluster routes.
- Do not broaden mappings, routes, or postprocessors to unrelated URL patterns unless validation proves they share the same template and intent, or the user explicitly asks.
- Record useful out-of-scope findings as backlog or next-cluster notes instead of implementing them immediately.

## Sample

- Select representative URLs from the cluster.
- Include edge cases when obvious, such as missing media, missing author, pagination, or sparse content.
- Fetch them as the sync does: `graph-sync-project` `scripts/fetch_page.py <url> --profile <profile>`. When content is missing or the site blocks the fetch, `--probe` shows the cheapest crawler mode that works (`graph-sync-project` `references/crawler.md`).
- Work from the fetched HTML (`output/fetch/*.xhtml` is what XPath runs on). The browser's DevTools and network panel help to understand a page, but they show the page after its own JavaScript ran, and XHR responses are never a data source.

## Model

- Choose the most specific useful schema.org type: the thing the page presents (`Product`, `Event`) or the most specific page type (`Article`, `CollectionPage`, `ItemPage`, `AboutPage`).
- Never plain `WebPage`. When no type fits, list the URLs and candidate types and ask the user. Exception: the client's own type list names `WebPage` for the page.
- Do not add Breadcrumbs markup by default.
- Connect the main entity to static entities such as `WebSite`, `Organization`, `Person`, `Brand`, or `Place`.
- Add authorship markup for creative works whenever possible.
- Add `FAQPage` when question/answer content exists.
- Connect FAQ entities to the main entity with `schema:about` and `schema:subjectOf` where appropriate.
- Add videos as `VideoObject` and connect them to the main entity with `schema:video`.
- Add ratings, collections, and sharing actions when observed and supported.
- Every child entity hangs under the page root (staging subjects under `{{ dataset_uri }}/<container>/__URL__`), keyed by a stable attribute.

## Implement

- Prefer static templates for stable static entities.
- Prefer YARRRML mappings for repeatable extraction (`graph-sync-yarrrml-review`).
- Use postprocessors only when mapping/static-template approaches cannot express the needed behavior cleanly.
- Keep mappings generalized across the configured source pages.
- Avoid sample-page constants and hardcoded fallbacks.
- Every URL routed to a mapping must produce entities; pages the cluster doesn't cover stay out of the profile's source.
- Check selectors on the fetched samples (`fetch_page.py --xpath`) before a sync.

## Review

- Inspect generated graph output (`output/debug_cloud/<profile>/`).
- Check for duplicate entities and twins (`kg_check.py twins`).
- Check URL literals.
- Check explicit IRIs.
- Check that entity type matches page intent.
- Check connections to static entities.
- Check FAQ/video/authorship completeness.
- Check what the API link serves for a few sample pages after clearing the cache (`kg_check.py page`).
