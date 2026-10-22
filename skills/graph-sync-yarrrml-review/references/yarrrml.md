# YARRRML For Graph-Sync Mappings

What works, what is safe, and how to think when extracting HTML with YARRRML on the `worph` backend. XPath details: `references/xpath.md`. Identity, routes and staging rules: `graph-sync-project` (`references/mappings.md`).

> YARRRML doesn't select anything. All selection is XPath; YARRRML binds the selected nodes to RDF.

- **Iterator** = where you stand (the context node).
- **Reference** `$(…)` = what you take from there (an XPath expression, relative to the iterator node).

## 1. Sources And Iterators

```yaml
sources:
  page:
    access: __XHTML__
    referenceFormulation: xpath
    iterator: /
```

- `__XHTML__` is the fetched page after the SDK's XHTML conversion; `__URL__` is its final URL. The SDK substitutes both before materialization.
- `iterator` selects the nodes to loop over; every reference in the mapping is evaluated from each of those nodes.
- `iterator: /` stands on the whole document (`worph` uses the `<html>` element). Use it for page-level values: `<head>`, `<meta>`, the `<h1>`, the main entity.
- Use a scoped iterator (`//details[summary]`, `//li[contains(concat(' ', normalize-space(@class), ' '), ' product-tile ')]`) for repeated items whose values live inside each item.
- On `worph` a reference sees **only the iterator node's subtree**. From a scoped iterator, `//head/…` searches that item only and finds nothing; no sibling, parent or position is reachable (§11.7, §11.10).
- Write iterators as `/`, `/html[…]` or `//…`. A bare relative iterator such as `html` or `html/head/meta` matches nothing on `worph` (it is evaluated from the `<html>` element), so every URL fails with `No JSON-LD nodes produced`.

## 2. XPath Inside References

`worph` evaluates references with `elementpath`: **XPath 2.0** functions work (`matches`, `lower-case`, `if … then … else`, `tokenize`; `references/xpath.md` §15). Keep to XPath 1.0 only in a mapping that must also run on the `morph` backend.

Class matching, always the safe form:

```xpath
//div[contains(concat(' ', normalize-space(@class), ' '), ' article ')]
```

`@class='article'` fails when the class attribute is `"article main"`.

## 3. Position And Structure

```xpath
p[1]                                   /* first p child */
li[last()]
//div[p[@class='price']]               /* divs containing a price paragraph */
//span[@class='price']/ancestor::div[1]
//h2/following-sibling::p[1]
```

Positions are a last resort; anchor on ids, classes and attributes (`references/xpath.md` §16).

## 4. Extracting Values

```yaml
- [schema:headline, "$(.)"]                       # the iterator node's text
- [schema:url, "$(@href)"]                        # an attribute
- [schema:author, "$(span[@class='name'])"]       # a child element's text
```

- An element's value is all its descendant text joined.
- Without `$(…)` a value is a constant: `"span[@class='name']/text()"` would be written to the graph as that literal string.

## 5. Meta Tags

Read them from `iterator: /` with a direct path, or iterate the tag itself so the mapping fires only when it exists:

```yaml
- [schema:description, "$(//head/meta[@name='description']/@content)"]
```

```yaml
description_source:
  access: __XHTML__
  referenceFormulation: xpath
  iterator: //meta[@name='description'][string-length(normalize-space(@content)) > 0]
```

## 6. Subjects

In graph-sync a subject is a staging IRI that the SDK rewrites:

- The page root: `{{ dataset_uri }}/<container>/__URL__` (container = the type's plural in kebab case: `products`, `articles`, `collection-pages`).
- Its children, **under** it: `{{ dataset_uri }}/<container>/__URL__/<child-container>/<stable key>`.
- Result: `<container>/<slug of the name>-<hash>/<child-container>/<key>`.

Never use `__URL__#fragment` subjects or positional subjects (`ex:item_$(position())`). Key children by a stable attribute (an `id`, a `data-*` attribute, the last segment of an `href`), never by visible text: text changes leave the old child behind, and non-ASCII text produces escaped IRI segments.

## 7. Repeated Content

```yaml
iterator: //*[@id='article-main-content']//p
```

```yaml
- [schema:articleBody, "$(.)"]
```

Filter at the iterator for specific items (`(//*[@id='article-main-content']//p)[1]`).

## 8. Avoid

- `replace()` / `tokenize()` with a pattern that can match an empty string (`/?$`, `,*`): `worph` raises `FORX0003` and silently drops the value (`references/xpath.md` §15 (f)). `matches()` accepts such patterns.
- Relying on visual order without structural anchors.
- `//` everywhere in scoped references: it is slow and catches nested look-alikes.
- Several logical entities in one mapping rule.
- `datatype:` other than `xsd:string` (§11.3).

## 9. Debugging

1. Explore the page in the browser's DevTools (`$x("//your/xpath")`): node count, value.
2. Check against what the sync fetched: `fetch_page.py <url> --xpath "<expr>"` (`graph-sync-project` scripts) fetches the page in the profile's crawler mode, converts it like the SDK and evaluates like `worph`. DevTools differs on `<tbody>`, JavaScript-rendered content and XPath 2.0 (`references/xpath.md` §12).
3. Encode it in YARRRML, run the profile with `--debug`, and read `output/debug_cloud/<profile>/cloud_<sha256(url)>.ttl`.

## 10. Patterns

### 10.1 Page Root From Head And Body

```yaml
prefixes:
  schema: http://schema.org/
  xsd: http://www.w3.org/2001/XMLSchema#

sources:
  page:
    access: __XHTML__
    referenceFormulation: xpath
    iterator: /

mappings:
  product:
    sources: [page]
    s: "{{ dataset_uri }}/products/__URL__"
    po:
      - [a, schema:Product]
      - p: schema:url
        o:
          - value: __URL__
            datatype: xsd:string
      - p: schema:name
        o:
          - value: "$(normalize-space((//h1)[1]))"
            datatype: xsd:string
      - p: schema:description
        o:
          - value: "$(//head/meta[@name='description'][string-length(normalize-space(@content)) > 0]/@content)"
            datatype: xsd:string
      - p: schema:brand
        o:
          - value: "{{ exports.organization_root_iri }}"
            type: iri
```

### 10.2 First Non-Empty Value

A union with `[1]` takes the first match in document order:

```yaml
- p: schema:image
  o:
    - value: "$(normalize-space((//meta[@property='og:image']/@content | //main//img[@itemprop='image']/@src)[1]))"
      datatype: xsd:string
```

Never use this for the page's own subject or `schema:url`: use `__URL__` (`rel=canonical` and `og:url` sometimes name another page).

### 10.3 One Typed Root Per Page, Linked To The Static Entities

```yaml
mappings:
  article:
    sources: [page]
    s: "{{ dataset_uri }}/articles/__URL__"
    po:
      - [a, schema:Article]            # never schema:WebPage
      - p: schema:url
        o:
          - value: __URL__
            datatype: xsd:string
      - p: schema:headline
        o:
          - value: "$(normalize-space((//h1)[1]))"
            datatype: xsd:string
      - p: schema:publisher
        o:
          - value: "{{ exports.organization_root_iri }}"
            type: iri
      - p: schema:isPartOf             # CreativeWork types only
        o:
          - value: "{{ exports.website_root_iri }}"
            type: iri
```

Plain `schema:WebPage` earns no rich result, and it is the only root type the re-sync reconciler swaps, so its children collapse on re-sync. If no type fits a page, list the URLs with the closest candidate types and ask.

Legacy repositories wrap the content entity in a `schema:WebPage` at `__URL__` with `schema:mainEntity` to `__URL__#main-entity`. Don't copy it. When you touch such a repository, collapse it into one typed root; the new type mints new IRIs and the old entities stay in the graph, so agree it with the user first (`graph-sync-project` `references/kg-checks.md`).

### 10.4 Several Sources In One File

```yaml
sources:
  page:
    access: __XHTML__
    referenceFormulation: xpath
    iterator: /
  faq:
    access: __XHTML__
    referenceFormulation: xpath
    iterator: //details[@id][summary][p]
  video:
    access: __XHTML__
    referenceFormulation: xpath
    iterator: //main//iframe[contains(@src, '/embed/')]
```

### 10.5 FAQ: FAQPage, Question, Answer

The FAQ hangs under the page root; questions are keyed by each item's `id`.

```yaml
mappings:
  faq_page:
    sources: [faq]
    s: "{{ dataset_uri }}/articles/__URL__/faq-pages/faq"
    po:
      - [a, schema:FAQPage]
      - p: schema:about
        o:
          - value: "{{ dataset_uri }}/articles/__URL__"
            type: iri
      - p: schema:mainEntity
        o:
          - value: "{{ dataset_uri }}/articles/__URL__/faq-pages/faq/questions/$(@id)"
            type: iri

  page_faq_link:
    sources: [faq]
    s: "{{ dataset_uri }}/articles/__URL__"
    po:
      - p: schema:subjectOf
        o:
          - value: "{{ dataset_uri }}/articles/__URL__/faq-pages/faq"
            type: iri

  faq_question:
    sources: [faq]
    s: "{{ dataset_uri }}/articles/__URL__/faq-pages/faq/questions/$(@id)"
    po:
      - [a, schema:Question]
      - p: schema:name
        o:
          - value: "$(normalize-space(summary))"
            datatype: xsd:string
      - p: schema:acceptedAnswer
        o:
          - value: "{{ dataset_uri }}/articles/__URL__/faq-pages/faq/questions/$(@id)/answers/answer"
            type: iri

  faq_answer:
    sources: [faq]
    s: "{{ dataset_uri }}/articles/__URL__/faq-pages/faq/questions/$(@id)/answers/answer"
    po:
      - [a, schema:Answer]
      - p: schema:text
        o:
          - value: "$(normalize-space(p[1]))"
            datatype: xsd:string
```

- The `FAQPage` has no `schema:url` when it isn't the page's main entity.
- When FAQ items have no stable attribute, key them by position with one source per position (§11.10).

### 10.6 VideoObject From Embeds

```yaml
mappings:
  video:
    sources: [video]
    s: "{{ dataset_uri }}/articles/__URL__/videos/$(substring-before(concat(substring-after(@src, '/embed/'), '?'), '?'))"
    po:
      - [a, schema:VideoObject]
      - p: schema:embedUrl
        o:
          - value: "$(@src)"
            datatype: xsd:string
      - p: schema:name
        o:
          - value: "$(normalize-space(@title))"
            datatype: xsd:string

  page_video:
    sources: [video]
    s: "{{ dataset_uri }}/articles/__URL__"
    po:
      - p: schema:video
        o:
          - value: "{{ dataset_uri }}/articles/__URL__/videos/$(substring-before(concat(substring-after(@src, '/embed/'), '?'), '?'))"
            type: iri
```

Google's video rich result also needs a thumbnail and an upload date, which embeds rarely carry; a postprocessor can add them from the video platform's API.

### 10.7 ItemList And ListItems

The list hangs under the page; items are keyed by the last segment of their link, and each item's `schema:url` is the target with a `#list-item` fragment (§11.5).

```yaml
sources:
  tile:
    access: __XHTML__
    referenceFormulation: xpath
    iterator: //ul[contains(concat(' ', normalize-space(@class), ' '), ' product-grid ')]/li[a/@href]

mappings:
  item_list:
    sources: [tile]       # fires only on pages that have tiles
    s: "{{ dataset_uri }}/collection-pages/__URL__/item-lists/products"
    po:
      - [a, schema:ItemList]

  page_list_link:
    sources: [tile]
    s: "{{ dataset_uri }}/collection-pages/__URL__"
    po:
      - p: schema:mainEntity
        o:
          - value: "{{ dataset_uri }}/collection-pages/__URL__/item-lists/products"
            type: iri

  list_item:
    sources: [tile]
    s: "{{ dataset_uri }}/collection-pages/__URL__/item-lists/products/list-items/$(replace(a/@href, '^.*/([^/]+)/?$', '$1'))"
    po:
      - [a, schema:ListItem]
      - p: schema:name
        o:
          - value: "$(normalize-space(a))"
            datatype: xsd:string
      - p: schema:url
        o:
          - value: "$(concat(if (starts-with(a/@href, 'http')) then a/@href else concat(replace('__URL__', '^(https?://[^/]+).*$', '$1'), a/@href), '#list-item'))"
            datatype: xsd:string

  list_elements:
    sources: [tile]
    s: "{{ dataset_uri }}/collection-pages/__URL__/item-lists/products"
    po:
      - p: schema:itemListElement
        o:
          - value: "{{ dataset_uri }}/collection-pages/__URL__/item-lists/products/list-items/$(replace(a/@href, '^.*/([^/]+)/?$', '$1'))"
            type: iri
```

- The key pattern `^.*/([^/]+)/?$` always consumes characters, so `replace()` is safe (§8).
- The URL expression handles absolute and root-relative links (it takes the origin from `__URL__`). `resolve-uri()` does not resolve root-relative links in `worph`.
- `schema:position` needs the item's position, which a scoped iterator cannot compute (§11.10).
- Carousel SHACL shapes expect `schema:item` on list items; when items link by URL only, exclude `google-carousel` / `google-carousels-beta` for that profile.

### 10.8 Several Values For One Property

Several `o:` entries emit **every** non-empty match:

```yaml
- p: schema:name
  o:
    - value: "$(normalize-space((//h1)[1]))"
      datatype: xsd:string
    - value: "$(normalize-space(//head/title))"
      datatype: xsd:string
```

This writes two names when both exist. Use it only when one of them is expected per page; for "first non-empty", use the union of §10.2. Don't add a hardcoded constant as a last fallback unless the user authorized it.

### Quick Reference

| Syntax | Resolves to | Use |
| --- | --- | --- |
| `__URL__` | The page's final URL | `schema:url` of the root; inside staging subjects |
| `{{ dataset_uri }}/<container>/__URL__` | The page root's staging IRI | Subject of the root and prefix of its children |
| `{{ exports.<key> }}` | A value from `exports.toml.j2` | Static entities (organization, website) and shared constants |
| `type: iri` | The object is an IRI | Links between entities (`publisher`, `mainEntity`, `itemListElement`, `about`) |
| `datatype: xsd:string` | A plain string | Every literal, URLs included |

## 11. `worph` Specifics

### 11.1 The Empty-Literal Trap

`$(normalize-space(//meta[@name='x']/@content))` emits an empty `""` on pages where the node is absent: `normalize-space()` of nothing is `""`. Use a bare, filtered reference, which emits only when a non-empty node exists:

```yaml
- p: schema:text
  o:
    - value: "$(//p[contains(concat(' ', normalize-space(@class), ' '), ' text ')][string-length(normalize-space(.)) > 0])"
      datatype: xsd:string
```

or filter at the iterator so the mapping fires only when the node is present (§5).

### 11.2 IRI Objects

`type: iri` marks an object as an IRI; `~iri` after a value does the same. URL-valued data properties (`schema:url`, `schema:image`, `schema:contentUrl`) stay plain strings; only links between entities are IRIs.

### 11.3 Typed Literals: Emit Plain Values, Cast In A Postprocessor

`worph` emits a correct typed literal, but the SDK's JSON-LD normalization treats any value carrying `@type` as a node and mints an entity for it, before postprocessors run. So put no `datatype:` other than `xsd:string` on objects:

```yaml
- p: schema:position
  o:
    - value: "3"
- p: schema:datePublished
  o:
    - value: "$(normalize-space((//time/@datetime)[1]))"   # an ISO date string is fine for Google
```

Where a real integer matters (`position`, `numberOfItems`, `reviewCount`), cast it in a postprocessor: `Literal(int(v), datatype=XSD.integer)`. Schema.org enumeration values are plain strings too (`"https://schema.org/InStock"`).

### 11.4 Fan-Out: N Objects From One Document Iterator

A multi-valued reference emits one triple per matched node:

```yaml
# iterator: /
- p: schema:itemListElement
  o:
    - value: "{{ dataset_uri }}/collection-pages/__URL__/item-lists/products/list-items/$(//ul[@id='grid']/li/a/replace(@href, '^.*/([^/]+)/?$', '$1'))"
      type: iri
```

Key the `ListItem` subjects with the same expression so the objects line up with them.

### 11.5 The `#fragment` Value Trick

The API link finds entities by `schema:url`. When two entities would legitimately carry the same page URL (a `Product` and a `ListItem` pointing at it from a listing), put a fragment in the second one's **value**:

```yaml
- p: schema:url
  o:
    - value: "$(concat(if (starts-with(a/@href, 'http')) then a/@href else concat(replace('__URL__', '^(https?://[^/]+).*$', '$1'), a/@href), '#list-item'))"
      datatype: xsd:string
```

Fragments are safe in values only; as subjects they don't nest (§6).

### 11.6 Subjects Are Staging IDs

The canonical IDs postprocessor rewrites `s:` as long as the root entity has a type, `schema:url` (= `__URL__`) and `schema:name` or `schema:headline`. A fixed seed (`{{ dataset_uri }}/articles/article-seed`) works for a lone root but gives children nothing page-specific to nest under.

### 11.7 `//head` From A Scoped Iterator

`worph` evaluates each reference with `elementpath.select(<iterator node>, ref)`, and ElementTree nodes have no parent pointer. From a scoped `<li>` iterator, `//head/link[@rel='canonical']` searches the `<li>` subtree and returns nothing. Take head and page-level values from a mapping whose iterator is `/`, and key scoped entities off something inside the node (`a/@href`).

### 11.8 Not On The Page → Postprocessor

A value from a Google Sheet or an external API is a postprocessor's job. A JSON blob in a `<script>` tag (`__NEXT_DATA__`, on-page JSON-LD) and the page's XHR responses are not a source at all. Keep YARRRML for what the HTML shows.

### 11.9 Conditionals And Constants Without A Postprocessor

Simple value logic stays in the mapping:

```yaml
- p: schema:priceCurrency
  o:
    - value: "EUR"                     # a constant: no $(…)
      datatype: xsd:string
- p: schema:inLanguage
  o:
    - value: "$(if (normalize-space(//html/@lang) = 'tr-TR') then 'tr' else normalize-space(//html/@lang))"
      datatype: xsd:string
- p: schema:datePublished
  o:
    - value: "$(if (string-length(normalize-space((//time)[1]/@datetime)) > 0) then (//time)[1]/@datetime else ())"
      datatype: xsd:string
```

- `else ()` (the empty sequence) emits no triple.
- String functions: `upper-case()`, `lower-case()`, `translate()`, `substring-before/after()`, `concat()`. `translate()` is the portable case fold if the mapping must survive a `morph` backend.
- Constants are for facts that hold for every page of the profile (a currency, a fixed category); never copy values from sample pages.

### 11.10 List Positions: A Scoped Iterator Can't Count Its Siblings

From a scoped iterator, `count(preceding-sibling::li) + 1` returns 1 for every item: no sibling is reachable (§11.7). Two ways that work:

- **One source per position, iterating the root.** The iterator is evaluated on the whole document; only references are subtree-bound. `iterator: /html[(//ul[@id='grid']/li)[N]]` fires only when item N exists, while every reference still sees the document: `(//ul[@id='grid']/li)[N]//h2`. The position is the constant `"N"`, and subjects are stable (`…/list-items/N`). Generate the sources and mappings with a Jinja loop (`{% for i in range(1, 25) %}`).
- **A postprocessor** that reads document order from the page HTML with the same selector and sets `schema:position` on the existing `ListItem`s. It must not create or rename IRIs.

### 11.11 Text In Document Order: `descendant::text()`

`X//text()` returns text nodes out of document order (the text after an inline `<strong>` can come first), so `string-join(X//text(), ' ')` scrambles copy. `X/descendant::text()` keeps the order:

```yaml
- value: "$(normalize-space(string-join((//h1)[1]/descendant::text(), ' ')))"
```

A bare `$(X)` keeps the order but glues text across `<br>` ("first line.Second line"), hence the join with `' '`. The SDK's XHTML keeps `<script>` elements: add `[not(ancestor::script)]` when collecting body text.

### 11.12 What The XHTML Conversion Changes

- No `<tbody>` is inserted (browsers add one): write `//table//tr`, not `//table/tbody/tr`.
- `<script>` elements are kept.
- Text that follows an HTML comment inside an element can be dropped (`9<!-- -->:47` becomes `9`); read such values in a postprocessor from the raw HTML.
