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
- Extract from the page's own HTML, as the sync fetches it, with YARRRML and XPath. Use the browser's network panel (XHR) only to understand how a page is built, never as a data source.
- Anchor XPath selectors on ids, classes and attributes (`//div[@id='x']//h2`), relative to the iterator for repeated items.
- Unless the user specifies a loader, use `crawler` (the template default) with `ingest_timeout_ms = 600000`. Fall back to `playwright` only when the crawler cannot produce the page; `simple`, `proxy` and `premium_scraper` are rarely needed.
- Start the crawler at `crawler_js_render_mode = "disabled"` and `crawler_proxy_mode = "disabled"`. Escalate (JavaScript rendering, then a proxy) only when `scripts/fetch_page.py` shows missing content or a blocked response; escalate per profile, not for the whole repository.
- The `playwright` loader drives a local browser through the Python `playwright` package; it needs `uv run playwright install chromium` on the machine running the sync.
- For the page's root entity, use the runtime page URL (`__URL__`) as subject and as `schema:url`, never canonical or Open Graph meta values.
- Ensure each page has exactly one first-level entity carrying the page URL, and that entity includes `schema:url`.
- Type each page's root entity as what the page is: the thing it presents (`Product`, `Event`, `Service`, `Place`, …) or the most specific page type (`Article`, `NewsArticle`, `CollectionPage`, `FAQPage`, `ItemPage`, `AboutPage`, `ContactPage`, `ProfilePage`, `SearchResultsPage`, …). If no type fits a page, list the URLs and the closest candidate types and ask the user; never drop such a page silently and never fall back to plain `WebPage`.
- Exception: when the client's own type list names `WebPage` for a page, map it as `WebPage` and keep it childless (links to the static `Organization` / `WebSite` only).
- Connect child entities through an explicit hierarchy such as `mainEntity`, `itemListElement`, `hasPart`, `about` / `subjectOf`, or another grounded Schema.org relationship appropriate to the page.
- Connect every entity to the graph: it references, and is referenced by, other entities. No orphans (a `ListItem` no `itemListElement` points to, a topic no page links with `about`).
- Use static rooted identity entities as the single source of truth for organizations and businesses; page-level mappings and postprocessors link to them as objects instead of re-emitting partial duplicate nodes.
- Stage child subjects under the page root's staging IRI (`{{ dataset_uri }}/<container>/__URL__/<child>/<stable key>`) and key them by a stable attribute, never by visible text.
- For geographic entities, always try to provide `schema:sameAs` links to Wikidata, GeoNames, and DBpedia.
- Always scout for question/answer pairs to create `FAQPage` markup connected to the main entity, unless `FAQPage` is the main entity itself.
- When `FAQPage` is not the page main entity, link it with `schema:about` from FAQ to main entity and `schema:subjectOf` from main entity to FAQ; keep the canonical page `schema:url` on the main entity only.
- Look for ratings and connect them to `Organization` or emit output markup where supported.
- Always try to add authorship markup on creative works (`Article`, blog posts, and related content) with an E-E-A-T mindset.
- Always write URL-valued schema properties as absolute plain literals (not IRIs and not `xsd:anyURI`), including `schema:url`, `schema:contentUrl`, and similar URL fields.
- Emit numeric, boolean and date values as plain literals in mappings; when a real typed literal matters (`schema:position`, `numberOfItems`), cast it in a postprocessor.
- When social sharing links are present, add `schema:potentialAction` using `ShareAction` and connect it to the page entity.
- When linking content already modeled in other clusters, prefer lightweight link structures (for example collection items with URL literals) instead of re-creating full page entities.
- When possible, add collection page markup with list items that link to related URLs.
- Keep `ItemList` entities inside the hierarchy of the owning page or entity.
- Treat `worai.toml` as the authoritative runtime configuration.
- Prefer several named profiles over one complex regex. When the URLs don't state the page type, give each type its own Google Sheet tab and profile, even a type with one URL.
- Store graph exports, production graph snapshots, validation/audit artifacts, KPI reports, and other local investigation artifacts under `output/`.
- Keep docs, indexes, examples, changelogs, and TODOs in sync when behavior contracts change.
- Validate structured data changes before graph sync runs.
- Name the account a sync will write to and get the user's confirmation before every sync.
- For parallel, bounded QA/review delegations, use subagents only when the user or environment explicitly permits delegation.
- Follow an OOP and KISS approach.

## DONTs

- Do not use blank nodes.
- Do not create duplicate mappings.
- Do not create multiple primary entities for the same canonical URL within a profile; one URL must map to one primary entity.
- Do not type anything as plain `schema:WebPage` (exception above). It earns no rich result, and it is the only root type the re-sync reconciler swaps, so its children collapse on re-sync.
- Do not use `__URL__#fragment` subjects or fragment seeds for child entities; they don't nest under `dependency_graph` and collide across pages.
- Do not put a `datatype:` other than `xsd:string` on mapping objects; the SDK turns typed values into junk entities.
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
- Do not hardcode the dataset URI; use provided placeholders or runtime context.
- Do not use `CreativeWork` when a more specific grounded Schema.org type applies.
- Do not invent Schema.org types or properties.
- Do not model schema.org enum values as IRI objects; write them as plain strings (`"https://schema.org/InStock"`), which the SDK's schema.org SHACL grammar accepts.
- Do not add Breadcrumbs markup by default.
- In YARRRML files, do not use positional XPath paths from the document root (`/html/body/div[2]/…`); they break on any layout change.
- Do not use JSON-LD, embedded JSON (`__NEXT_DATA__`, other `<script>` data) or the page's XHR responses as a data source for extraction, in mappings or postprocessors: they may change or disappear.
- You may still use JSON-LD/structured data only to infer the best semantic type when creating configurations.
- Do not hardcode constants from sample pages used during development; extraction/mapping rules must generalize across source pages.
- Do not add hard-coded fallbacks (including static fallback templates/paths) unless explicitly authorized by the user.
- Do not introduce unverified values for policy, pricing, availability, shipping, return, tax, or corporate identifier data.
- Do not widen mapping scope with catch-all rules when a cluster-specific rule is possible.
- Do not type pages with slug lists in route patterns (`^/(about|press|team)/?$`); use per-type sheet tabs.
- Do not route URLs to a mapping that emits nothing: it fails every such URL. Keep pages that are fully defined by static templates (the homepage) and pages you don't map out of the source with `url_regex`, the sheet, or the sitemap filter.
- Do not emit a static-template entity (`Organization`, `WebSite`) from a page graph with only some of its properties; with `graph_write_strategy = "put"` the page write replaces it. Reference it as an object only.
- Do not change mapping or postprocessor semantics without explicit approval.
- Do not implement custom IRI canonicalization in project mappings or postprocessors when `worai` / `wordlift-sdk` canonical ID handling owns canonicalization; postprocessors never create subjects or build IRIs from strings.
- Do not treat ad-hoc local config files as project defaults. Never commit `postprocessor_runtime = "inprocess"` or a local config copy.
- When a Google Sheets source cannot be read (missing service-account file), do not fall back to the sitemap, a URL list or invented pages; stop and ask for the file.
- Never delete from a knowledge graph as part of graph-sync work: no entity deletions, property deletes or account resets, with any tool. When a change leaves old entities behind, list them for the user (`references/kg-checks.md`). Never run `worai graph reset` on a client account.
- Do not delegate final semantic modeling or integration decisions to subagents; keep those in the main agent.
- Do not mark work complete without running applicable validation.
