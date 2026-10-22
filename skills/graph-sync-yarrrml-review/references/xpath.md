# XPath For HTML Extraction

The XPath subset used to extract data from HTML in graph-sync mappings, and how the `worph` backend evaluates it. XPath here is a read-only path language for navigating a tree: no state, no mutation, no joins. If an expression feels confusing, picture the tree.

## 1. Mental Model

An HTML page is a tree. An XPath expression says where you are in the tree, which nodes you want, and under what conditions.

## 2. Absolute And Relative Paths

```xpath
/html/body/div     /* from the document root: breaks on any layout change */
//div              /* every div in the document */
.                  /* the current node: the iterator node in a mapping */
```

Positional paths from the root are rarely right in real HTML. Anchor on ids, classes and attributes instead (§16).

## 3. The Two Slashes

```xpath
div/p              /* p must be a direct child of div */
div//p             /* p anywhere inside div */
```

Use `/` where the structure is stable, `//` where it is noisy.

## 4. Selecting By Attributes

```xpath
//div[@id='main']
//meta[@name='description']
//img[@src]                                                      /* attribute exists */
//div[contains(concat(' ', normalize-space(@class), ' '), ' card ')]   /* safe class match */
```

Never `//div[@class='card']`: HTML classes are space-separated lists, so it fails on `class="card featured"`. A plain `contains(@class, 'card')` also matches `card-header` and `discard`.

## 5. Attributes

```xpath
a/@href
img/@src
meta/@content
```

In references: `"$(@href)"`, `"$(@content)"`. `worph` needs the standard form `country/@name`, not the shorthand `country@name`.

## 6. Text

```xpath
.                  /* the node's string value: all descendant text */
h1                 /* a child element's text */
span[@class='author']
```

`text()` is not the same thing. It returns only the node's **own** text children, one value per run of text. On `<p>Hello <b>world</b> tail</p>`, `text()` gives `"Hello "` and `" tail"`: two values (two triples), and "world" is lost. Use it only to skip child elements' text on purpose.

## 7. Position And Order

```xpath
p[1]                  /* 1-based */
p[position() = 1]
li[last()]
li[position() <= 5]
```

## 8. Predicates

```xpath
//a[@href]
//a[contains(@href, '/product/')]
//div[p]              /* divs that contain a p */
```

## 9. Axes

```xpath
ancestor::div[1]                  /* closest ancestor div */
h2/following-sibling::p[1]        /* first paragraph after a heading */
p/preceding-sibling::h2[1]        /* closest heading before a paragraph */
```

From a scoped iterator these axes cannot leave the iterator node's subtree (§15 (b), (c)).

## 10. Common Patterns

```xpath
//h1                                                    /* headline */
//*[@id='article-main-content']/p[1]                    /* first body paragraph */
//*[@id='article-main-content']//p                      /* all body paragraphs */
//div[contains(concat(' ', normalize-space(@class), ' '), ' card ')]   /* repeated blocks */
//meta[@property='og:url']/@content                     /* meta value */
```

## 11. Anti-Patterns

- `//` everywhere.
- `@class='x'` for classes.
- Deep positional paths from the root.
- Text matching without anchors.
- XPath 2.0 functions (`matches()`, `lower-case()`) in a mapping that must survive a switch to the `morph` backend. On the default `worph` backend they work (§15).

## 12. Debugging

1. Explore the page in the browser's DevTools: `$x("//div[@id='main']")`, then check node count, node type, text and attributes.
2. **Confirm against what the sync sees.** DevTools is not a faithful test: a selector can work there and match nothing in the mapping, or the reverse.
   - The browser shows the DOM after its own JavaScript ran. The sync gets what the crawler fetched in the profile's JavaScript mode.
   - Browsers insert `<tbody>` into every table; the SDK's conversion does not. `//table/tbody/tr` works in DevTools and matches nothing in the mapping: write `//table//tr`.
   - Browsers evaluate XPath 1.0 only, so an XPath 2.0 expression (`matches()`, `if … then … else`) errors in DevTools but works in the mapping.
   - The SDK's conversion keeps `<script>` elements and can drop text that follows an HTML comment.
3. For an exact check, run `fetch_page.py <url> --xpath "<expr>"` (`graph-sync-project` scripts): it fetches the page as the sync does, converts it with the SDK's `HtmlConverter` and evaluates with `elementpath` from the document root, as `worph` does for `iterator: /`.

## 13. Golden Rules

1. XPath selects nodes, not meaning.
2. Iterator scope beats clever expressions.
3. Relative paths prevent data bleed.
4. Stable anchors beat clever traversal.
5. If it's hard to read, it's probably wrong.

## 14. Out Of Scope

XPath 3.1 functions, namespaces, XSLT. XPath 2.0 functions do work on `worph` (§15).

## 15. How `worph` Evaluates XPath

`worph` evaluates `$(…)` references with `elementpath` over `xml.etree.ElementTree` (not lxml). Consequences, all verified:

### (a) Rich Functions Work, Including XPath 2.0

```xpath
normalize-space(//h1)                            /* collapse whitespace */
concat('https://x.com', ./a/@href)               /* compose a URL */
substring-before(concat(//title, '|'), '|')      /* substring, never empty */
translate(@rel, 'CANONICAL', 'canonical')        /* case fold, portable */
string-length(normalize-space(.)) > 0            /* presence test */
(//link[@rel='canonical']/@href | //meta[@property='og:url']/@content)[1]   /* first non-empty */
matches('abc', 'a.c')   lower-case('ABC')   tokenize('a,b', ',')   if (…) then … else …   /* XPath 2.0 */
```

"Keep to XPath 1.0" is a portability convention for mappings that might move to the `morph` (morph-kgc) backend, not a `worph` limitation. For such mappings prefer `translate()` over `lower-case()` and skip `matches()`.

`resolve-uri()` leaves root-relative links (`/products/x`) unresolved; build absolute URLs from the origin of `__URL__` (`references/yarrrml.md` §10.7).

### (b) A Reference Only Sees The Iterator Node's Subtree

`worph` evaluates each reference with `elementpath.select(<iterator node>, ref)`, and ElementTree elements carry no parent or root pointer. So `//head/link/@href` from a scoped `<li>` iterator searches the `<li>` subtree and returns nothing; from the `/` iterator it returns the href. Take head, canonical and `<meta>` values from a mapping whose iterator is `/`, and key scoped entities off something inside the node (`./a/@href`).

### (c) No Axis Leaves The Subtree, Not Even `preceding-sibling`

From a scoped iterator, `count(preceding-sibling::div) + 1` returns 1 for every node, `count(../div)` and `count(/html)` return 0, and `//h1` returns nothing. A scoped item cannot compute its own position; the sibling idiom works only from an `iterator: /` mapping. Per-item positions: `references/yarrrml.md` §11.10.

### (d) Iterators Are Evaluated From The `<html>` Element

`iterator: /` is special-cased to the root element. Any other iterator is evaluated with the `<html>` element as context: `/html[…]`, `//…` and child paths such as `body/…` work, but a bare `html` or `html/head/meta` matches nothing, so the mapping produces no nodes and every URL fails.

### (e) `//text()` Is Out Of Document Order: Use `descendant::text()`

`X//text()` returns text nodes out of document order (tails before child texts), so `string-join(X//text(), ' ')` scrambles mixed content with inline `<strong>`/`<br>`. `X/descendant::text()` keeps document order. The same applies to `string(.)` on a mixed-content iterator node.

### (f) `replace()` And `tokenize()` Reject Patterns That Can Match An Empty String

XPath 2.0 raises `FORX0003` when a `replace()` or `tokenize()` pattern can match the empty string (`/?$`, `,*`, `^`), even if the input contains a non-empty match. `worph` then drops the value without failing the URL: the triple is simply missing. `matches()` accepts such patterns. Make the pattern consume at least one character, or use a conditional:

```xpath
replace(U, '/?$', '/')                              /* ✗ FORX0003: '/?$' matches "" */
if (ends-with(U, '/')) then U else concat(U, '/')   /* ✓ add a trailing slash once */
replace(U, '([^/])$', '$1/')                        /* ✓ the match is never empty */
```

### Everyday Idioms

**`normalize-space()` of a missing node is `""`.** It can't test presence and yields empty (junk) triples. Filter with a predicate:

```xpath
//p[@class='intro'][string-length(normalize-space(.)) > 0]
//meta[@name='description'][string-length(normalize-space(@content)) > 0]
```

**1-based position from siblings**, only from an `iterator: /` mapping. Emit it without `datatype: xsd:integer` and cast it in a postprocessor (`references/yarrrml.md` §11.3):

```xpath
count(preceding-sibling::li[.//a/h3]) + 1
```

**Case-insensitive match**, portable form:

```xpath
//link[translate(@rel, 'CANONICAL', 'canonical') = 'canonical']/@href
```

**First non-empty fallback** (union + `[1]`):

```xpath
(//link[@rel='canonical']/@href | //meta[@property='og:url']/@content | //meta[@name='twitter:url']/@content)[1]
```

For a page's own subject and `schema:url`, use `__URL__` instead of these tags.

## 16. Recipe Book: Anchor-Based Selectors

Write selectors as document-wide `//…` searches anchored on ids, classes and attributes, never positional paths from the root (§2), and evaluate them from a mapping whose iterator is `/` (§15 (b)). Anchors survive reordered lists, missing tabs and markup churn.

An element's text is all its descendant text joined, so `$(…/label)` gives the label's full text. A selector matching N nodes emits N values, so N triples.

1. A `label` nested in `div › table › span`, each hop anchored:

   ```xpath
   //div[@id='wrapper']//table[contains(concat(' ', normalize-space(@class), ' '), ' data ')]//span//label
   ```

2. The 3rd `label` inside a div, overall: `(//div[@id='fields']//label)[3]`
3. All label texts inside a div (one triple each): `//div[@id='fields']//label`
4. All `h1` texts inside a span with an id: `//span[@id='hero']//h1`
5. All item texts inside a div: `//div[@id='menu']//li`
6. A `label` of a given class inside a div:

   ```xpath
   //div[@id='fields']//label[contains(concat(' ', normalize-space(@class), ' '), ' required ')]
   ```

   or only the first match: `(//div[@id='fields']//label[contains(concat(' ', normalize-space(@class), ' '), ' required ')])[1]`
7. Any `<meta>` in `<head>`:

   ```xpath
   //head/meta[@property='og:title']/@content
   //head/meta[@name='description']/@content
   //head/meta[starts-with(@property, 'og:')]/@content     /* every og:* value */
   ```

### `(…)[n]` vs `…//el[n]`

- `(//div[@id='x']//label)[3]` is the 3rd label in the whole div (flattened, document order).
- `//div[@id='x']//label[3]` is every label that is the 3rd among its own siblings: zero or several matches when labels live under different parents.

For "the Nth thing overall", parenthesize first.

### Robustness

- **A missing anchor gives an empty result, never a crash.** `//div[@id='not-here']//label` returns nothing and the property is not emitted.
- **Anchors beat positions.** A label found by class survives reordering; `(//label)[3]` breaks when someone reorders the list. Use positions only when nothing stable exists.
- **Present-only values:** append `[string-length(normalize-space(.)) > 0]` to skip empty nodes.
- **Class match** is always `contains(concat(' ', normalize-space(@class), ' '), ' x ')`.
