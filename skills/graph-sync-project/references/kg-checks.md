# Knowledge Graph Checks Around A Sync

The checks a sync needs, with the account's API key only: before a run (which account), after a run (did the pages land, any twins), and what a sync leaves behind. `scripts/kg_check.py` runs each one from the repository root (`uv run python <graph-sync-project skill>/scripts/kg_check.py <command>`). Never print the API key.

For anything else about a WordLift Knowledge Graph (why the API link of a page is empty, response shapes, GraphQL, patching or exporting entities), use the `wordlift-kg` skill when it is installed.

## Before A Sync: Which Account

`kg_check.py account [--profile <profile>]` shows the account the profile's key opens: account id, **Website URL**, dataset URI and entity count. A sync writes into that account's graph at once, with no dry run, so show these to the user and wait for a yes.

**The crawler fetches only the Website URL's host**, compared exactly (`www.example.com` ≠ `example.com`). The script warns when the profile's source hosts differ:

- No Website URL: every fresh fetch fails with HTTP 412 (`Account website URL not configured.`).
- Another host: HTTP 403 (`Access to host '…' is not allowed`).
- Pages still in the crawler cache succeed, so a broken setup can look partially working.

The Website URL is set in the WordLift management console; the API key cannot change it. `/accounts/me` is cached: clear the cache to re-check after a change.

Several accounts can have the same Website URL: a temporary account, an old account kept after a move, or one account per language on a multilingual site. The crawler accepts each of them, but the site's API link answers from only one: the account its cloud site points to (on multilingual sites, by `__wl_lang`). A sync to another account succeeds and changes nothing on the site. After a sync, `kg_check.py page` warns when another account answered the API link. When the user isn't sure which account the site uses, they can search the management console for the site.

## After A Sync: Did The Pages Land

`kg_check.py page <url> [<url> ...]` shows, per URL, the entities whose `schema:url` equals the URL (GraphQL, live) and how many nodes the API link serves (cached), with the account's include/exclude decision for that URL when it sends one (`excluded` = dropped, `bypassed` = served).

- Run `kg_check.py clear-cache` after every sync before reading the API link; it changes no data.
- Entities without a `schema:url` (an `FAQPage` under its page, list items) don't match a URL; check them in the page's debug graph (`output/debug_cloud/<profile>/`).
- The homepage is looked up with a trailing slash (`references/static-templates.md`).
- If the graph has the entities but the API link serves nothing after a cache clear, the cause is a setting outside the repository that the API key can't read. Ask the user to check two things in the WordLift management console: that the site has a **cloud site** (the API link finds the account by the page's host through it; without one, every page answers empty), and the page in the account's **include/exclude list**. The `wordlift-kg` skill has the other checks.

## After A Sync: Twins

`kg_check.py twins` lists real duplicates: two or more entities with the same `schema:url` **and** the same full type set. Different types on one URL are normal (`Organization` and `WebSite` on the homepage); `web-pages/<40 hex>` and `collection-pages/<40 hex>` entities carry internal-link data and share their page's URL by design.

Twins from a sync come from:

- **A changed page title or name.** Entity IRIs are minted from `schema:name` / `schema:headline`, so a new title mints a new IRI and the old entity stays.
- **A changed root type**, or a mapping moved to another container.
- **Two first-level entities with the same `schema:url` on one page**: the re-sync lookup merges them into `-2` twins (`references/mappings.md`).
- **Children staged with `__URL__#fragment` subjects**, or minted by a postprocessor: they become shared root entities and collide across pages.

## A Sync Never Deletes

A page removed from the source, a changed title, a changed type or a template entity dropped from `templates/` leaves its old entities in the graph; a page write doesn't remove them.

Graph-sync work never deletes them (`references/policy.md`), not even when the user asks for a cleanup during the session:

- Before a change that re-mints IRIs, tell the user in plain words that the old entities will stay in the graph next to the new ones.
- After the sync, list the old top-level IRIs (`kg_check.py twins`, `kg_check.py page <url>`) and save them to `output/leftover-entities.txt`, one entity per line: the IRI first, then a space and the page URL it belongs to.
- Tell the user how many there are and where the list is. Removing them is a separate decision outside graph-sync work.

Never run `worai graph reset` on a client account: it also clears the Website URL, so every crawler fetch fails afterwards.

## Temporary Accounts

To experiment without touching the client's live graph, create a temporary account in the WordLift management console, set its **Website URL to the host the profile crawls**, and put its API key in `.env` (keep the client's key aside). Keep its own dataset URI: two accounts sharing one dataset URI break the entity pages of both. Before syncing the client's account again, put its key back and confirm with `kg_check.py account`.

The API link finds the account by the page's host (its cloud site), not by the key, so it never shows a temporary account's graph: it shows the client's live graph, or nothing. Check a temporary account through the graph lines of `kg_check.py page` (it warns when another account answered the API link), and create no cloud site for it.
