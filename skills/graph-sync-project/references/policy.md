# Graph Sync DOs and DONTs

Operational rules for this project.

## Policy Authority

- This file is the canonical policy source for graph-sync implementation and review guardrails.
- Other graph-sync skill references should reference this file for policy instead of duplicating policy text.

## DOs

- Always assign an explicit IRI to entities.
- Start with static entities for `WebSite`, `Organization`, and other vertical entities; then prefer YARRRML mappings; use postprocessors only after that.
- Ground all implementation decisions in observed repository behavior and source evidence; do not invent assumptions.
- Use `http://schema.org` as the default vocabulary base URI (use `https://schema.org` only if explicitly required).
- In YARRRML files, use relative XPath selectors.
- Unless the user specifies a loader, prefer `crawler` (the template default); fallback priority: `simple`, `playwright`, `proxy`, `web_scrape_api`, `premium_scraper`.
- For `crawler`, set `crawler_js_render_mode` to `auto` or `enabled` when the target page requires JavaScript rendering; leave as `disabled` otherwise.
- For `crawler`, set `crawler_proxy_mode` to `simple`, `standard`, or `premium` when the target site blocks direct crawling; use `auto` to let the crawler decide (higher cost); leave as `disabled` for unrestricted sites.
- Before attempting the `playwright` loader, confirm Playwright MCP integration is installed and available.
- Inspect XHR/network traffic before finalizing extraction; if a structured upstream source exists, prefer it over HTML parsing.
- For geographic entities, always try to provide `schema:sameAs` links to Wikidata, GeoNames, and DBpedia.
- Always scout for question/answer pairs to create `FAQPage` markup connected to the main entity, unless `FAQPage` is the main entity itself.
- Look for ratings and connect them to `Organization` or emit output markup where supported.
- Always try to add authorship markup on creative works (`Article`, blog posts, and related content) with an E-E-A-T mindset.
- Always write URL-valued schema properties as plain literals (not IRIs and not `xsd:anyURI`), including `schema:url`, `schema:contentUrl`, and similar URL fields.
- When social sharing links are present, add `schema:potentialAction` using `ShareAction` and connect it to the page entity.
- When linking content already modeled in other clusters, prefer lightweight link structures (for example collection items with URL literals) instead of re-creating full page entities.
- When possible, add collection page markup with list items that link to related URLs.
- For parallel, bounded QA/review delegations, use subagents only when the user or environment explicitly permits delegation.
- Follow an OOP and KISS approach.

## DONTs

- Do not use blank nodes.
- Do not create duplicate mappings.
- Do not write schema URL properties as IRIs; use plain literals.
- Do not type URL-valued schema properties as `xsd:anyURI`; keep them as plain literals.
- Do not emit image URLs as IRIs (for example `schema:image` / `schema:contentUrl` when URL-valued); keep them as plain literals.
- Do not ingest image or static asset URLs as source pages (for example `/wp-content/uploads/*`, `.webp`, `.png`, `.jpg`, `.pdf`) even if they appear in sitemaps.
- Do not create duplicate `WebPage` entities in collection/related-link sections when those pages are already defined elsewhere; link them by URL literals in item nodes.
- Do not relate entities to the web page canonical URL.
- DO NOT hardcode the dataset URI; use provided placeholders or runtime context.
- Do not use `WebPage` markup when a more specific entity type is available.
- In YARRRML files, do not use absolute XPath selectors.
- Do not use JSON-LD or any other structured data markup as a data source for extraction, because it may be removed in the future.
- You may still use JSON-LD/structured data only to infer the best semantic type when creating configurations.
- Do not hardcode constants from sample pages used during development; extraction/mapping rules must generalize across source pages.
- Do not add hard-coded fallbacks (including static fallback templates/paths) unless explicitly authorized by the user.
- Do not delegate final semantic modeling or integration decisions to subagents; keep those in the main agent.
- Do not mark work complete without running applicable validation.
