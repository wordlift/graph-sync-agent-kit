# Sources And Profiles

Where a profile's URLs come from, and when to split pages into several profiles.

## What A Profile Can Set

A named profile inherits `[profiles._base]` and overrides every key it sets. Scalars, lists (`urls`, `shacl_exclude_builtin_shapes`) and route tables (`mappings`) are replaced, never appended.

| Per profile | Keys |
| --- | --- |
| Source | `ingest_source` with `sitemap_url`, `sheets_url` + `sheets_name`, or `urls` |
| URL filter | `url_regex` |
| Mappings | `mapping` (fallback) and `[[profiles.<name>.mappings]]` routes |
| Fetching | `ingest_loader`, `crawler_js_render_mode`, `crawler_proxy_mode`, `ingest_timeout_ms`, `concurrency` |
| Validation | `shacl_exclude_builtin_shapes` |
| Postprocessors | `profiles/<name>/postprocessors.toml` (replaces `_base`'s), `postprocessor_runtime` (`persistent` or `oneshot` only) |
| Account | `api_key`: the account the profile writes to |

A profile does **not** inherit from sibling profiles, only from `_base`. Files resolve from `profiles/_base/` and `profiles/<name>/`: put shared mappings, templates and `exports.toml.j2` in `profiles/_base/`. A mapping that uses `{{ exports.* }}` in a profile without its own or `_base`'s `exports.toml.j2` fails (`'dict object' has no attribute …`).

When profiles read **different** sources, keep the source keys out of `_base`: a profile that inherits `sitemap_url` and sets `sheets_url` fails with `Exactly one source is required`. When every profile reads the same sheet, `sheets_url` can live in `_base` and each profile sets its `sheets_name`.

## Profiles Or Routes

- **Different sources** (sitemap, sheet, URL list) → separate profiles.
- **Different crawler settings** (rendering, proxy) → separate profiles. Fetch settings apply to a whole profile, and each URL must belong to exactly one profile (the crawler cache is keyed by URL).
- **Different page types whose URL path states the type** (`/blog/…`, `…/p<id>.html`) → one profile, one route per type. Routes match the URL path (`references/mappings.md`).
- **Page types the URLs don't reveal** → one Google Sheet tab per type, one profile per tab. Never type pages with slug lists in a route (`pattern = "^/(about-us|press|team)/?$"`): the list keeps growing, and a mistake is silent (an unmatched URL falls through to the fallback mapping, a wrong match gets the wrong type). This holds even for a type with a single URL.

Every profile costs one CI run per schedule, one entry in the workflow's `options` and `all` lists, and one orchestrator entry. Add one only when a setting must differ.

## One Sheet Tab Per Page Type

```toml
[profiles._base]
ingest_source = "sheets"
sheets_url = "https://docs.google.com/spreadsheets/d/<sheet-id>/edit"
sheets_service_account = "${SHEETS_SERVICE_ACCOUNT}"

[profiles.products]
api_key = "${WORDLIFT_API_KEY}"
sheets_name = "products"
mapping = "product.yarrrml"

[profiles.articles]
api_key = "${WORDLIFT_API_KEY}"
sheets_name = "articles"
mapping = "article.yarrrml"
```

- Name the tab and the profile after the type (`products`, `articles`, `about_pages`).
- When the client provides the types, sort the URLs into tabs from them. When the client provides only URLs or a sitemap, classify the pages: fetch them and group them by a template marker in the HTML (the `<body>` class, the main container), then spot-check a few pages per group.
- A sitemap is one source option, not a requirement: when filtering it by type needs a long or fragile regex, export its URLs once into per-type tabs.
- Trade-off: a tab is a curated list, so new pages appear only when someone adds them; a sitemap picks them up by itself. Say which one the project uses in its README.
- The sheet has one column named `url` with full page URLs, one per row. The service account only reads it; people edit the sheet, so tell the user which rows to add, move or remove.

## Google Sheets Credentials

A sheet source reads the sheet through a Google service account. Each project has its own service-account JSON file, which is not in the repository.

- Locally: the file at `.config/sa-key.json` (git-ignored) and `SHEETS_SERVICE_ACCOUNT=.config/sa-key.json` in `.env`.
- On CI: the file's full JSON **content** in the repository secret `SHEETS_SERVICE_ACCOUNT`, forwarded in the workflow `env:`. worai detects JSON content. A postprocessor that reads a sheet itself gets that raw content on CI, not a path: it must accept both (JSON content starts with `{`).
- The sheet must be shared (Viewer) with the service account's `client_email`.

**When the file is missing, stop.** Tell the user the project needs its Google service-account file and that the WordLift tech team provides it (Google shows a key only once, so they may have to create a new key). Give them a message to forward naming the repository and the `client_email` if known. Never work around it: don't switch the profile to the sitemap or to a URL list, and don't invent the page list. Those pages and their types come from the sheet.

## Sitemap Gaps

Some page types are missing from the public sitemap. A sitemap-only profile then skips them silently: no error, no entities. Cover them with another profile and source (a sheet tab).

## Registering A New Profile

A profile runs on CI only when it is listed in two places:

1. The repository workflow `.github/workflows/graph-sync.yml`: the `options` list of the `profile` input and the `all` matrix. Mandatory: the orchestrator dispatches by profile name, and GitHub rejects a name missing from `options` (HTTP 422).
2. The orchestrator's `sync-targets.json` in `graph-sync-orchestrator`, one entry per profile: `{ "repo": "graph-sync-<project>", "profile": "<profile>" }`.

The orchestrator repository is maintained by the WordLift tech team. If the user can't edit it, give them a message to forward with the repository and profile names. A new profile that reads a new secret also needs that secret in the repository settings and in the workflow `env:` (`graph-sync-github-workflow-review`).
