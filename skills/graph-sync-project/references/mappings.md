# Graph Sync Mappings

How the runtime picks and renders a page's mapping, and the identity rules every mapping must follow. Writing the YARRRML and XPath itself: `graph-sync-yarrrml-review` (`references/yarrrml.md`, `references/xpath.md`).

## Mapping Configuration Contract

- Fallback mapping: `mapping` (default `default.yarrrml`).
- Routes: `[[profiles.<name>.mappings]]` tables, each with `pattern` and `mapping`.
- Mapping files resolve from `profiles/_base/mappings/` and `profiles/<name>/mappings/` (or `mappings_dir`); an absolute path is used as is.
- Template variant resolution order for a selected file:
  1. the selected `.j2` / `.liquid` file itself
  2. sibling `<file>.j2`
  3. sibling `<file>.liquid`
  4. the plain file
- Templates render with `dataset_uri`, `account` and `exports` (from `exports.toml.j2`).

## Route Matching

- `re.match(pattern, path)`: the pattern is tested against the URL **path** only (no host, query or fragment) and is anchored at the start of the path, not at its end.
- For a URL with an empty path (`https://www.example.com`), the pattern is tested against the **full URL**. Route the homepage with a pattern that accepts both: `^(/|https://www\.example\.com/?)$`.
- Routes are scanned in order; the first match wins. When no route is `.*`, the runtime appends `.*` → `mapping`, so every URL gets a mapping.
- Type pages by route only when the path states the type (`^/blog/`). Never list slugs in a pattern to type pages (`references/sources-and-profiles.md`).
- `url_regex` (which URLs enter the run) uses `re.search` on the full URL; routes (which mapping a URL gets) use `re.match` on the path.

## Every Routed URL Must Produce A Graph

- A mapping that emits nothing **fails the URL** (`No JSON-LD nodes produced`). There is no "no-op" mapping.
- Keep pages you don't map out of the source instead: `url_regex`, the sheet tab, or the sitemap filter. This includes the homepage when static templates own it (`references/static-templates.md`).
- A fallback mapping gated on its page template (its iterator requires a marker of that template) fails loudly on pages it doesn't recognise. That is the intended signal: a new page type appeared.
- The fallback mapping never emits a generic `WebPage` as a substitute for modeling.

## Page Identity

- `__URL__` is the URL the loader finally fetched (after redirects). The SDK substitutes it as text anywhere in the mapping, subjects and values, before materialization.
- The page's root entity uses `__URL__` for its subject and its `schema:url`. Never take page identity from `rel=canonical`, `og:url` or similar tags: sites echo other pages there, and the SDK keys the canonical IRI and the re-sync lookup on `schema:url`.
- Exactly **one** first-level entity per page carries the page URL as `schema:url`. A second one makes the re-sync lookup merge them into `-2` twins. Entities that point at other pages (list items) carry the target URL with a fragment in their value (`<target>#list-item`).
- The root entity has a type, `schema:url` and `schema:name` or `schema:headline`: these feed the canonical IRI, `<container>/<slug of the name>-<hash>`. A changed title therefore mints a new IRI and leaves the old entity behind.
- Type the root as what the page is: the thing it presents (`Product`, `Event`, …) or the most specific page type (`Article`, `CollectionPage`, `FAQPage`, `ItemPage`, `AboutPage`, `ContactPage`, …). Never plain `WebPage` (`references/policy.md`).

## Staging Subjects (`canonical_id_strategy = "dependency_graph"`)

Mapping subjects are staging IRIs; the canonical IDs postprocessor rewrites them. Stage the page root on `__URL__` and every child **under** it:

```yaml
s: "{{ dataset_uri }}/articles/__URL__"                                          # page root
s: "{{ dataset_uri }}/articles/__URL__/item-lists/related"                       # child
s: "{{ dataset_uri }}/articles/__URL__/item-lists/related/list-items/$(@data-id)" # grandchild
```

→ `articles/<slug>-<hash>/item-lists/related/list-items/<key>`.

- Children nest only when staged under the parent's dataset-prefixed IRI. `__URL__#fragment` subjects (`__URL__#faq`) and fixed seeds with fragments do not nest: the SDK re-mints them as root entities keyed by name, so identical texts on different pages merge, and children of a fragment root can share one IRI across all pages.
- Key children by a stable attribute (an id, a `data-*` attribute, an href segment), never by visible text.
- Children of a root typed exactly `schema:WebPage` collapse on re-sync: the reconciler swaps that root to its existing IRI before the canonical step, so the children are re-minted as colliding root entities. Another reason never to map plain `WebPage`.
- `canonical_id_strategy` unset means `legacy`: no nesting; staging subjects stay as written.

## Literals

- Put no `datatype:` other than `xsd:string` on mapping objects. The SDK's JSON-LD normalization turns any value carrying `@type` into an entity, so `datatype: xsd:integer` writes a junk entity instead of a number. Emit plain values; cast them in a postprocessor when a real number, boolean or date type matters.
- URL-valued properties (`schema:url`, `schema:image`, `schema:contentUrl`) are plain string literals, never IRIs.
- Schema.org enumeration members are plain strings too (`"https://schema.org/InStock"`), not IRI objects (`references/policy.md`).

## Required And Optional Extraction

- Classify important fields as required or optional during cluster modeling.
- Use selective sources for fields that may be absent, so missing selectors do not emit empty literals or malformed IRIs.
- Use root/page-level iterators only for triples guaranteed by the page contract, such as the primary entity skeleton.
- Keep optional entity IRIs guarded by the source that proves the entity exists.
- For creative works, treat authorship as expected unless the user accepts otherwise; missing authorship should be caught in validation and resolved with a better selector, another observed source, or an explicitly approved fallback.

## Postprocessor Escalation

- Use YARRRML for everything addressable in the page's HTML: scalar fields, repeated items, entity skeletons, simple value logic (`if … then … else`, string functions; `worph` evaluates XPath 2.0).
- Escalate to a postprocessor for typed literals, list positions from a scoped iterator, data outside the page (a Google Sheet, an external API), deduplication or cross-entity linking.
- The page's own XHR responses and embedded JSON (`__NEXT_DATA__`, JSON-LD) are not a source for either.
- Postprocessors change values and links between existing entities; they never create subjects or rename IRIs (`graph-sync-postprocessor-authoring`).
