#!/usr/bin/env python3
"""Read-only checks on the WordLift account a graph-sync profile writes to.

Run from the graph-sync repo root (the API key comes from the profile, `.env` or the environment):

    uv run python <this-skill>/scripts/kg_check.py account [--profile NAME]
    uv run python <this-skill>/scripts/kg_check.py page URL [URL ...]
    uv run python <this-skill>/scripts/kg_check.py types
    uv run python <this-skill>/scripts/kg_check.py twins
    uv run python <this-skill>/scripts/kg_check.py clear-cache

account      which account the key belongs to, its Website URL, dataset URI and entity count;
             warns when the profile's source hosts differ from the Website URL host
page         what the KG holds for page URLs (GraphQL, live) and what the API link serves (cached)
types        entity counts per schema.org type
twins        entities sharing one schema:url AND the same type set (real duplicates)
clear-cache  clear the account's response cache (API link, data endpoint, /accounts/me);
             touches no graph data

Nothing here deletes or changes entities.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    API_BASE,
    ApiError,
    add_config_arguments,
    configure_stdout,
    load_settings,
    request,
)

ACCOUNT_ACCEPT = "application/vnd.wordlift.account-info.v2+json"
PRIVATE = {"X-include-Private": "true"}
PAGE_QUERY = """
query ($urls: [String]!) {
  entities(query: { urlConstraint: { in: $urls } }) {
    iri
    url: string(name: "schema:url")
    name: string(name: "schema:name")
    headline: string(name: "schema:headline")
    types: refs(name: "rdf:type")
  }
}
"""
ALL_QUERY = """
query ($page: Int, $rows: Int) {
  entities(query: {}, page: $page, rows: $rows) {
    iri
    url: string(name: "schema:url")
    types: refs(name: "rdf:type")
  }
}
"""


def short_type(iri: str) -> str:
    return iri.rstrip("/").rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def graphql(api_key: str, query: str, variables: dict) -> list[dict]:
    _, body = request(
        "POST",
        f"{API_BASE}/graphql",
        api_key,
        payload={"query": query, "variables": variables},
        headers=PRIVATE,
    )
    doc = json.loads(body)
    if doc.get("errors"):
        raise SystemExit(f"GraphQL error: {doc['errors']}")
    return (doc.get("data") or {}).get("entities") or []


def all_entities(api_key: str, rows: int = 2000) -> list[dict]:
    out: list[dict] = []
    page = 0
    while True:
        batch = graphql(api_key, ALL_QUERY, {"page": page, "rows": rows})
        out.extend(batch)
        if len(batch) < rows:
            return out
        page += 1


def source_hosts(settings) -> set[str]:
    hosts = set()
    sitemap = settings.get("sitemap_url")
    if isinstance(sitemap, str) and sitemap.startswith("http"):
        hosts.add(urllib.parse.urlsplit(sitemap).hostname or "")
    urls = settings.get("urls")
    if isinstance(urls, list):
        hosts.update(urllib.parse.urlsplit(u).hostname or "" for u in urls if isinstance(u, str))
    return {h.lower() for h in hosts if h}


def cmd_account(args, settings, api_key: str) -> int:
    _, body = request("GET", f"{API_BASE}/accounts/me", api_key, accept=ACCOUNT_ACCEPT)
    me = json.loads(body)
    try:
        _, stats_body = request("GET", f"{API_BASE}/accounts/me/stats", api_key, accept="*/*")
        entities = json.loads(stats_body).get("entities")
    except ApiError:
        entities = "?"
    website = me.get("url") or ""
    print(f"account id    {me.get('accountId')}")
    print(f"website URL   {website or '(not set)'}")
    print(f"dataset URI   {me.get('datasetUri')}")
    print(f"language      {me.get('language')}")
    print(f"API link via  {me.get('dataApiRoute')}")
    print(f"entities      {entities}")
    if settings.profile:
        print(f"profile       {settings.profile} (source: {settings.get('ingest_source', '?')})")

    website_host = (urllib.parse.urlsplit(website).hostname or "").lower()
    if not website_host:
        print("WARNING: no Website URL: every crawler fetch fails with 412. Set it in the dashboard.")
        return 1
    hosts = source_hosts(settings)
    others = sorted(h for h in hosts if h != website_host)
    if others:
        print(
            f"WARNING: the crawler only fetches {website_host} for this key; "
            f"source URLs on {', '.join(others)} fail with 403."
        )
        return 1
    print("(/accounts/me is cached: after changing the account, run clear-cache and re-check)")
    return 0


def api_link(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    path = f"{parts.scheme}/{parts.netloc}{parts.path}"
    link = f"{API_BASE}/data/{urllib.parse.quote(path, safe='/%:@!$&()*+,;=~-._')}"
    return f"{link}?{parts.query}" if parts.query else link


def count_nodes(body: str) -> int:
    if not body.strip():
        return 0
    doc = json.loads(body)
    if isinstance(doc, list):
        return len(doc)
    if isinstance(doc, dict):
        graph = doc.get("@graph")
        return len(graph) if isinstance(graph, list) else 1
    return 0


def cmd_page(args, settings, api_key: str) -> int:
    _, me_body = request("GET", f"{API_BASE}/accounts/me", api_key, accept=ACCOUNT_ACCEPT)
    account_id = str(json.loads(me_body).get("accountId") or "")
    found = graphql(api_key, PAGE_QUERY, {"urls": args.urls})
    by_url: dict[str, list[dict]] = defaultdict(list)
    for entity in found:
        by_url[entity.get("url") or ""].append(entity)
    for url in args.urls:
        print(url)
        entities = by_url.get(url, [])
        if not entities:
            print("  KG: no entity has this exact schema:url")
        for entity in entities:
            types = ", ".join(sorted(short_type(t) for t in entity.get("types") or []))
            label = entity.get("name") or entity.get("headline") or ""
            print(f"  KG: {types} {entity['iri']} {label[:60]!r}")
        link = api_link(url)
        try:
            headers: dict[str, str] = {}
            _, body = request("GET", link, None, accept="application/ld+json", response_headers=headers)
            decision = headers.get("x-wordlift-include-exclude-status")
            note = f", include/exclude: {decision}" if decision else ""
            nodes = count_nodes(body)
            print(f"  API link: {nodes} node(s){note} (cached; clear-cache after a sync) {link}")
            served_by = headers.get("x-wordlift-account-id")
            if served_by and account_id and served_by != account_id:
                print(f"  -> answered by account {served_by}, not this key's account {account_id}: the API link"
                      " finds the account by the page's host (its cloud site), so it doesn't show this graph")
            if decision == "excluded":
                print("  -> dropped by the account's include/exclude list, which the API key can't read:"
                      " ask the user to check this page in it in the WordLift management console")
            elif nodes == 0 and entities:
                print("  -> the graph has this page but the API link is empty: after a cache clear, ask the user to"
                      " check in the WordLift management console that the site has a cloud site, and the"
                      " include/exclude list")
        except ApiError as exc:
            print(f"  API link: HTTP {exc.status} {link}")
    return 0


def cmd_types(args, settings, api_key: str) -> int:
    counts: Counter[str] = Counter()
    entities = all_entities(api_key)
    for entity in entities:
        types = entity.get("types") or []
        counts[" + ".join(sorted(short_type(t) for t in types)) or "(untyped)"] += 1
    print(f"{len(entities)} entities")
    for type_set, count in counts.most_common():
        print(f"{count:8d}  {type_set}")
    return 0


def cmd_twins(args, settings, api_key: str) -> int:
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for entity in all_entities(api_key):
        url = entity.get("url")
        if not url:
            continue
        type_set = " + ".join(sorted(short_type(t) for t in entity.get("types") or [])) or "(untyped)"
        groups[(url, type_set)].append(entity["iri"])
    twins = {key: sorted(iris) for key, iris in groups.items() if len(iris) > 1}
    if not twins:
        print("no twins: every (schema:url, type set) has one entity")
        return 0
    print(f"{len(twins)} URL(s) with twins (same schema:url and same types):")
    for (url, type_set), iris in sorted(twins.items()):
        print(f"{url}  [{type_set}]")
        for iri in iris:
            print(f"  {iri}")
    return 1


def cmd_clear_cache(args, settings, api_key: str) -> int:
    status, _ = request("DELETE", f"{API_BASE}/accounts/me/cache", api_key, accept="*/*")
    print(f"cache cleared (HTTP {status})")
    return 0


def main() -> int:
    configure_stdout()
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    common = argparse.ArgumentParser(add_help=False)
    add_config_arguments(common)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("account", parents=[common])
    page = sub.add_parser("page", parents=[common])
    page.add_argument("urls", nargs="+")
    sub.add_parser("types", parents=[common])
    sub.add_parser("twins", parents=[common])
    sub.add_parser("clear-cache", parents=[common])
    args = parser.parse_args()

    settings = load_settings(
        Path(args.config), args.profile, Path(args.env_file), require_profile=False
    )
    api_key = settings.api_key(args.key_env)
    handler = {
        "account": cmd_account,
        "page": cmd_page,
        "types": cmd_types,
        "twins": cmd_twins,
        "clear-cache": cmd_clear_cache,
    }[args.command]
    try:
        return handler(args, settings, api_key)
    except ApiError as exc:
        hint = " (the API key was rejected: check .env)" if exc.status == 401 else ""
        print(f"FAILED: {exc}{hint}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
