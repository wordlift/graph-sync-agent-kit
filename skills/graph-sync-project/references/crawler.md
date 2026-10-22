# Fetching Pages: The Crawler

How a sync fetches pages, how to pick the cheapest working mode, and the fetch problems that look like mapping problems.

## Loaders

`ingest_loader` decides how pages are fetched:

- `crawler` (template default): WordLift's managed crawler, called with the profile's API key. It handles JavaScript rendering, proxies, retries and caching on the server; nothing is installed locally.
- `playwright`: a headless browser on the machine running the sync, through the Python `playwright` package. It needs `uv run playwright install chromium` once per machine (the CI action installs it). Use it only when the crawler can't produce the page.
- `simple` (plain HTTP), `proxy`, `premium_scraper`: rarely needed.
- `web_scrape_api` and its `web_page_import_*` keys are the retired loader. When you touch such a repository, switch it to `crawler` with `crawler_js_render_mode`, `crawler_proxy_mode` and `ingest_timeout_ms`.

## Crawler Settings

```toml
[profiles._base]
ingest_loader = "crawler"
crawler_js_render_mode = "disabled"   # disabled | enabled | auto
crawler_proxy_mode = "disabled"       # disabled | simple | standard | premium | auto
ingest_timeout_ms = 600000
```

- **Always set `ingest_timeout_ms = 600000`.** Without it, `worai graph sync` gives each crawler request 30 seconds. The crawler queues fetches, and a queued fetch can wait longer, so those pages fail with `INGEST_LOAD_NETWORK_ERROR` (no status code, no details) and the run looks like a flaky crawler. The template ships the line commented out.
- **Cost order:** `disabled` + `disabled` is the cheapest; JavaScript rendering costs a little more; proxies cost the most (`simple` < `standard` < `premium`). Use the cheapest combination that returns the content the mappings need.
- Prefer explicit modes over `auto`: `auto` lets the crawler escalate on its own, at a higher cost.
- Each key can be set per profile. A named profile overrides `_base`, so most pages can stay cheap while one profile pays for rendering or a proxy (`references/sources-and-profiles.md`).
- The account's Website URL must be the host being crawled, or every fetch fails with 412 or 403 (`references/kg-checks.md`).

## Choosing The Mode: `scripts/fetch_page.py`

`fetch_page.py` sends the same request as the sync's crawler loader (`GET https://api.wordlift.io/crawler/fetch` with the URL, both modes and the profile's key) and saves what comes back under `output/fetch/`: the raw HTML, the SDK's XHTML conversion (what XPath runs on), and the crawler's status code and final URL.

```bash
uv run python <graph-sync-project skill>/scripts/fetch_page.py <url> --profile <profile>          # the profile's mode
uv run python <graph-sync-project skill>/scripts/fetch_page.py <url> --profile <profile> --probe  # every mode, cheapest first
uv run python <graph-sync-project skill>/scripts/fetch_page.py <url> --xpath "//h1"                # evaluate like the mapping
```

Read the probe from the cheapest mode up:

- The cheapest mode returns the content (title, main text, the elements the mappings use) → use it.
- The content is missing or the page is a shell → JavaScript rendering (`crawler_js_render_mode = "enabled"`).
- The site answers 403/429, a captcha or a challenge page → a proxy, `simple` first, then `standard`. Add `--include-premium` only when every other mode fails.

Use the script before writing mappings, and whenever a page fails or maps wrong, to tell a fetch problem from a mapping problem. Its final URL is what the mapping sees as `__URL__`.

## The Crawler Cache

The crawler caches each fetch by **URL alone**, whatever modes the next request asks for. A cached copy lives for the site's `Cache-Control` max-age, else a per-domain interval, else 24 hours. A sync never forces a refetch; `fetch_page.py` does by default (`force=true`) and overwrites the cached copy.

- After probing, the **last** mode fetched is what the next sync receives. `--probe` therefore fetches once more in the profile's mode at the end. After changing a profile's mode, fetch its sample URLs once in the new mode, or wait a day.
- Two profiles fetching the same URL in different modes serve each other's cached HTML. Give every URL exactly one profile.
- A re-run inside the cache window doesn't touch the site, so it is fast. A failing fresh fetch can hide behind cached successes, which makes a broken setup look partially working.
- When a page renders differently by mode, gate the mapping on a marker of the expected render (an attribute only the rendered page has). A wrong-mode cached copy then fails that URL loudly and keeps the last good graph, instead of writing a degraded one.

## Limits Of JavaScript Rendering

The crawler's browser waits for the page but never scrolls or clicks, so infinite scroll and "load more" listings render only the first batch. Ask the server for a bigger page instead (for example a `?sz=N` page-size parameter on product listings), and strip that query back off `schema:url` in the mapping.

## Fetch Problems In A Run

| Symptom | Cause |
| --- | --- |
| `INGEST_LOAD_NETWORK_ERROR`, no status | `ingest_timeout_ms` unset (30 s) |
| `Crawler API error 412 … Account website URL not configured` | the account has no Website URL |
| `Crawler API error 403 … Access to host '…' is not allowed` | the Website URL's host differs from the crawled host |
| Status 403/429 from the site, captcha HTML | the site blocks the crawler: escalate the proxy mode |
| Mapped values missing on some pages only | the page needs rendering, or another profile's mode is in the cache |
| `schema:url` of the homepage lacks the trailing slash | the crawler's final URL drops it (`references/static-templates.md`) |
