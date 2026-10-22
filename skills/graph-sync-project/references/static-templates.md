# Graph Sync Static Templates

Static templates are hand-written RDF (`.ttl.j2`) for entities that don't vary per page: the `Organization`, the `WebSite`, their addresses, contact points and search action. They are written once per run, before any page.

## Static Template Or Mapping

| Situation | Use |
| --- | --- |
| Fixed business facts (name, address, social profiles) | Static template |
| One entity per project (`Organization`, `WebSite`) | Static template |
| Data that varies per page | YARRRML mapping |
| One entity per page of a type | YARRRML mapping |

## Templates Directory

- Static template source directory is `templates_dir`; default `profiles/<profile_name>/templates`, with `profiles/_base/templates` searched as well. Put shared templates in `_base`.
- Runtime scans the directories and reifies files whose RDF format can be inferred: plain RDF (`.ttl`, `.jsonld`) and templated RDF (`.ttl.j2`, `.ttl.liquid`).
- Render context: `account`, `dataset_uri`, `exports`.
- File names start with a two-digit order: `20_` for roots (`20_organization.ttl.j2`, `20_website.ttl.j2`), `30_` for their first-level children (`30_website_search_action.ttl.j2`), `40_` for second-level children (`40_organization_postal_address.ttl.j2`).

## Exports

- Exports load from `profiles/_base/` and `profiles/<profile>/`, in the order `exports.toml`, `exports.toml.j2`, `exports.toml.liquid`. Without one, `exports` is `{}`.
- Declare every template IRI there, built on `{{ dataset_uri }}`, and use them as `{{ exports.<key> }}` in templates and mappings:

```toml
# profiles/_base/exports.toml.j2
organization_root_iri = "{{ dataset_uri }}/organizations/acme"
website_root_iri = "{{ dataset_uri }}/web-sites/acme-com"
organization_postal_address_iri = "{{ dataset_uri }}/organizations/acme/postal-addresses/main"
website_search_action_iri = "{{ dataset_uri }}/web-sites/acme-com/search-actions/search"
```

- Kebab-case slugs; dependent IRIs nested under their parent's slug; never a hardcoded dataset URI.
- Templates render with strict variables: a profile whose `exports` lacks a key the mapping uses fails.

## Example

```turtle
@prefix schema: <http://schema.org/> .

<{{ exports.organization_root_iri }}>
  a schema:Organization ;
  schema:name "Acme" ;
  schema:url "https://www.example.com/" ;
  schema:logo "https://www.example.com/logo.png" ;
  schema:sameAs "https://www.wikidata.org/wiki/Q00000000" ;
  schema:address <{{ exports.organization_postal_address_iri }}> .
```

- A parent company is a second `Organization` in the same file, linked with `schema:parentOrganization`. Sibling brands of one group use the same parent name and URL.
- `WebSite` links its publisher (`schema:publisher <{{ exports.organization_root_iri }}>`) and, when the site has a search box, a `schema:potentialAction` `SearchAction` with an `EntryPoint` target (`schema:urlTemplate "https://www.example.com/search?q={search_term_string}"`).

## Patch Timing

- The static template graph is written once per run, before page mappings, in one bulk write; it is skipped when its import hash is unchanged.
- An edit to a template entity takes effect on the next run (the write replaces each template entity).
- An entity **removed** from the templates is not deleted from the graph; list it for the user as a leftover (`references/kg-checks.md`).
- A failing run still writes the templates first.
- Never emit a template entity from a page mapping or postprocessor with only some of its properties: with `graph_write_strategy = "put"` the page write replaces the template's version. Pages reference template entities as objects only.

## The Homepage

The API link looks a page up by exact `schema:url`, and always requests the homepage **with** a trailing slash (`https://www.example.com/`). The crawler reports the homepage's final URL **without** it (`https://www.example.com`), and that is what `__URL__` becomes. So a homepage entity built by a mapping is never found. In order of preference:

1. **Let the static templates own the homepage**: `Organization` and `WebSite` with a hand-written `schema:url "https://www.example.com/"` (with the slash). Keep the homepage URL out of every profile's source (no sheet row; a `url_regex` that requires a path, such as `^https://www\.example\.com/.+`).
2. **If the homepage needs page-level markup** from its HTML (lists, FAQ), map it with its own route or profile and add the slash: `value: "$(if (ends-with('__URL__', '/')) then '__URL__' else concat('__URL__', '/'))"`. Don't use `replace('__URL__', '/?$', '/')`: the pattern can match an empty string, which `worph` rejects, and the entity silently loses its `schema:url`. The switch mints a new homepage IRI: delete the old bare-URL entity once.

## Debug Output

With `--debug`, the static template graph is written to `output/debug_cloud/<profile>/static_templates.ttl`.

## Exports vs Mapping Variables

- Use `exports.toml` (or templated exports) for reusable profile-level constants and computed values.
- Use mapping template variables (`account`, `dataset_uri`, `exports`) for mapping-local rendering.
- Prefer `exports` when multiple mappings or postprocessors need the same derived values.

## Checklist

- Every entity has an explicit IRI (no blank nodes), declared in `exports.toml.j2`.
- URL-valued properties (`schema:url`, `schema:logo`) are plain string literals.
- `schema:sameAs` points to authoritative sources (Wikidata first, official profiles).
- Facts come from official sources (the site's footer, about, contact and legal pages); unverified facts stay out.
- File prefixes respect the dependency order.
