# Graph Sync DOs and DONTs

Operational rules for this project.

## Policy Authority

- This file is the canonical policy source for graph-sync implementation and review guardrails.
- Other graph-sync skill references should reference this file for policy instead of duplicating policy text.

## DOs

- Always assign explicit, stable, deterministic IRIs to entities.
- Start with static entities for `WebSite`, `Organization`, and other vertical entities; then prefer YARRRML mappings; use postprocessors only after that.
- Ground all implementation decisions in observed repository behavior and source evidence; do not invent assumptions.
- Use `http://schema.org` as the default vocabulary base URI (use `https://schema.org` only if explicitly required).
- In YARRRML files, use relative XPath selectors.
- Unless the user specifies a loader, prefer `crawler` (the template default); fallback priority: `simple`, `playwright`, `proxy`, `web_scrape_api`, `premium_scraper`.
- For `crawler`, set `crawler_js_render_mode` to `auto` or `enabled` when the target page requires JavaScript rendering; leave as `disabled` otherwise.
- For `crawler`, set `crawler_proxy_mode` to `simple`, `standard`, or `premium` when the target site blocks direct crawling; use `auto` to let the crawler decide (higher cost); leave as `disabled` for unrestricted sites.
- Before attempting the `playwright` loader, confirm Playwright MCP integration is installed and available.
- Inspect XHR/network traffic before finalizing extraction; if a structured upstream source exists, prefer it over HTML parsing.
- For page-level `schema:url`, use the runtime current-page URL value (for example `__URL__` in mappings) instead of canonical or Open Graph meta values.
- Ensure each page has exactly one clear main page-like entity IRI and that entity includes `schema:url`.
- Prefer the most specific grounded Schema.org type for each page or entity, such as `Article`, `NewsArticle`, `AboutPage`, `ProfilePage`, `CollectionPage`, `SearchResultsPage`, `FAQPage`, `Service`, `Organization`, `ContactPoint`, `ItemList`, `Place`, `Event`, or `DigitalDocument`.
- Use specific `WebPage` subtypes such as `AboutPage`, `ProfilePage`, `CollectionPage`, or `SearchResultsPage` when they are the best grounded semantic fit; only generic `WebPage` is discouraged.
- Connect child entities through an explicit hierarchy such as `mainEntity`, `itemListElement`, `hasPart`, `about` / `subjectOf`, or another grounded Schema.org relationship appropriate to the page.
- Use static rooted identity entities as the single source of truth for organizations and businesses; page-level mappings and postprocessors should link to them instead of re-emitting partial duplicate nodes.
- For geographic entities, always try to provide `schema:sameAs` links to Wikidata, GeoNames, and DBpedia.
- Always scout for question/answer pairs to create `FAQPage` markup connected to the main entity, unless `FAQPage` is the main entity itself.
- When `FAQPage` is not the page main entity, link it with `schema:about` from FAQ to main entity and `schema:subjectOf` from main entity to FAQ; keep the canonical page `schema:url` on the main entity only.
- Look for ratings and connect them to `Organization` or emit output markup where supported.
- Always try to add authorship markup on creative works (`Article`, blog posts, and related content) with an E-E-A-T mindset.
- Always write URL-valued schema properties as absolute plain literals (not IRIs and not `xsd:anyURI`), including `schema:url`, `schema:contentUrl`, and similar URL fields.
- For numeric properties such as `schema:position`, emit plain numeric literals from source values when possible.
- When social sharing links are present, add `schema:potentialAction` using `ShareAction` and connect it to the page entity.
- When linking content already modeled in other clusters, prefer lightweight link structures (for example collection items with URL literals) instead of re-creating full page entities.
- When possible, add collection page markup with list items that link to related URLs.
- Keep `ItemList` entities inside the hierarchy of the owning page or entity.
- Treat `worai.toml` as the authoritative runtime configuration.
- Store graph exports, production graph snapshots, validation/audit artifacts, KPI reports, and other local investigation artifacts under `.private/`.
- Keep docs, indexes, examples, changelogs, and TODOs in sync when behavior contracts change.
- Validate structured data changes before graph sync runs.
- For parallel, bounded QA/review delegations, use subagents only when the user or environment explicitly permits delegation.
- Follow an OOP and KISS approach.

## DONTs

- Do not use blank nodes.
- Do not create duplicate mappings.
- Do not create multiple primary entities for the same canonical URL within a profile; one URL must map to one primary entity.
- Do not write schema URL properties as IRIs; use plain literals.
- Do not type URL-valued schema properties as `xsd:anyURI`; keep them as plain literals.
- Do not emit image URLs as IRIs (for example `schema:image` / `schema:contentUrl` when URL-valued); keep them as plain literals.
- Do not emit relative IRIs or relative URL literals where absolute IRIs or URLs are required.
- Do not ingest image or static asset URLs as source pages (for example `/wp-content/uploads/*`, `.webp`, `.png`, `.jpg`, `.pdf`) even if they appear in sitemaps.
- Do not create duplicate `WebPage` entities in collection/related-link sections when those pages are already defined elsewhere; link them by URL literals in item nodes.
- Do not assign `schema:url` to `FAQPage` entities that are not the web page main entity.
- Do not attach `Question` nodes directly to `WebPage`; model `FAQPage` + `Question` + `Answer` and connect FAQ pages to main entities through `about` / `subjectOf`.
- Do not publish `Question` or `Answer` nodes when content is empty or equals `None`.
- Do not derive page-level `schema:url` from canonical tags or Open Graph meta tags when a runtime URL value is available.
- Do not relate entities to the web page canonical URL.
- DO NOT hardcode the dataset URI; use provided placeholders or runtime context.
- Do not use generic `WebPage` markup when a more specific grounded type is available.
- Do not use `CreativeWork` when a more specific grounded Schema.org type applies.
- Do not invent Schema.org types or properties.
- Do not model schema.org enum values as IRI objects.
- In YARRRML files, do not use absolute XPath selectors.
- Do not use JSON-LD or any other structured data markup as a data source for extraction, because it may be removed in the future.
- You may still use JSON-LD/structured data only to infer the best semantic type when creating configurations.
- Do not hardcode constants from sample pages used during development; extraction/mapping rules must generalize across source pages.
- Do not add hard-coded fallbacks (including static fallback templates/paths) unless explicitly authorized by the user.
- Do not introduce unverified values for policy, pricing, availability, shipping, return, tax, or corporate identifier data.
- Do not widen mapping scope with catch-all rules when a cluster-specific rule is possible.
- Do not process pages that are already fully defined by static templates; send them to a null mapping that emits no graph.
- Do not change mapping or postprocessor semantics without explicit approval.
- Do not implement custom IRI canonicalization in project mappings or postprocessors when `worai` / `wordlift-sdk` canonical ID handling owns canonicalization.
- Do not treat ad-hoc local config files as project defaults.
- Do not run bulk graph property deletes or account-level resets without explicit user approval and scoped confirmation.
- Do not delegate final semantic modeling or integration decisions to subagents; keep those in the main agent.
- Do not mark work complete without running applicable validation.
