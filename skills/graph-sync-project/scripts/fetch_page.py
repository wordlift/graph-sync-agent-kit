#!/usr/bin/env python3
"""Fetch pages through the WordLift crawler the way a graph-sync run does.

Run from the graph-sync repo root, with the project environment:

    uv run python <this-skill>/scripts/fetch_page.py URL [URL ...] [--profile NAME]
    uv run python <this-skill>/scripts/fetch_page.py URL --probe
    uv run python <this-skill>/scripts/fetch_page.py URL --xpath "//h1" --xpath "//title"

By default each URL is fetched in the profile's crawler modes (`crawler_js_render_mode`,
`crawler_proxy_mode` from worai.toml) with the profile's API key: the same request the sync's
`crawler` loader sends. The result is what a sync receives: the HTML, the status code and the
final URL (which becomes `__URL__` and `schema:url`).

`--probe` fetches in every mode from cheapest to most expensive, then fetches once more in the
profile's mode. The crawler caches by URL alone, whatever the mode, for about 24 h: the last fetch
is what the next sync gets.

Cost order: js=disabled+proxy=disabled < JS rendering < proxy (simple < standard < premium).
Pick the cheapest mode that returns the content the mappings need.

Files go to output/fetch/: the raw HTML, the SDK's XHTML conversion (what XPath runs on) when the
project environment has wordlift-sdk, and the crawler's metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
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

PROBE_LADDER = [
    ("disabled", "disabled"),
    ("enabled", "disabled"),
    ("disabled", "simple"),
    ("disabled", "standard"),
    ("enabled", "standard"),
]
OUTPUT_DIR = Path("output") / "fetch"


class PageSummary(HTMLParser):
    """Title, <h1> count and visible text size: enough to compare modes at a glance."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.h1_count = 0
        self.text_chars = 0
        self._skip_depth = 0
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "template"):
            self._skip_depth += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1_count += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "template") and self._skip_depth:
            self._skip_depth -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self._skip_depth:
            self.text_chars += len(data.strip())


def file_stem(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    readable = re.sub(r"[^A-Za-z0-9]+", "-", f"{parsed.netloc}{parsed.path}").strip("-")[:80]
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]
    return f"{readable}-{digest}"


def fetch(url: str, js: str, proxy: str, api_key: str, force: bool) -> dict:
    params = {"url": url, "js_render_mode": js, "proxy_mode": proxy}
    if force:
        params["force"] = "true"
    _, body = request("GET", f"{API_BASE}/crawler/fetch", api_key, params=params, timeout=600)
    return json.loads(body)


def explain_api_error(exc: ApiError) -> str:
    if exc.status == 401:
        return "the API key was rejected: check WORDLIFT_API_KEY in .env"
    if exc.status == 412:
        return "the account has no Website URL: set it in the dashboard (it must be this site's host)"
    if exc.status == 403:
        return (
            "the crawler refused the request: the account's Website URL must be this site's host "
            "(check with kg_check.py account)"
        )
    return "crawler API error"


def element_values(value) -> list[str]:
    """Render an elementpath result the way worph does: element text = all descendant text."""
    items = value if isinstance(value, list) else [value]
    out = []
    for item in items:
        if item is None:
            continue
        if isinstance(item, ET.Element):
            out.append("".join(item.itertext()))
        else:
            out.append(str(item))
    return out


def convert_and_select(html: str, expressions: list[str]):
    """Convert like the SDK, evaluate like worph from `iterator: /`. None when unavailable."""
    try:
        from wordlift_sdk.utils.html_converter import HtmlConverter
    except ImportError:
        return None, "wordlift-sdk is not importable: run with `uv run python` from the repo root"
    try:
        xhtml = HtmlConverter().convert(html)
    except Exception as exc:  # the sync fails this URL the same way
        return None, f"XHTML conversion failed (the sync fails this page too): {exc}"
    results = []
    if expressions:
        try:
            import elementpath
        except ImportError:
            return xhtml, "elementpath is missing: add worai to the dev group (see local-runs.md)"
        root = ET.fromstring(xhtml)
        for expr in expressions:
            try:
                results.append((expr, element_values(elementpath.select(root, expr)), None))
            except Exception as exc:
                results.append((expr, [], str(exc)))
    return xhtml, results


def run_one(url: str, js: str, proxy: str, args, api_key: str, label: str) -> dict | None:
    print(f"  mode js={js} proxy={proxy}{label}")
    try:
        data = fetch(url, js, proxy, api_key, force=not args.no_force)
    except ApiError as exc:
        print(f"    FAILED {exc.status}: {explain_api_error(exc)}")
        return None
    except OSError as exc:
        print(f"    FAILED: {exc}")
        return None

    html = data.get("html") or ""
    summary = PageSummary()
    summary.feed(html)
    status = data.get("status_code")
    title = " ".join(summary.title.split())[:80]
    print(
        f"    status {status} | from_cache {data.get('from_cache')} | final {data.get('url_final')}"
        f" | html {len(html):,} chars | text {summary.text_chars:,} chars | h1 {summary.h1_count}"
        f" | title {title!r}"
    )
    if data.get("error_code") or data.get("error_message"):
        print(f"    crawler error: {data.get('error_code')} {data.get('error_message')}")
    if isinstance(status, int) and status in (401, 403, 429, 503):
        print("    the site refused the crawler: a proxy mode may be needed")

    stem = f"{file_stem(url)}__js-{js}_proxy-{proxy}"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    meta = {k: v for k, v in data.items() if k != "html"}
    (OUTPUT_DIR / f"{stem}.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    saved = [f"{stem}.html"]
    (OUTPUT_DIR / f"{stem}.html").write_text(html, encoding="utf-8")

    if html:
        xhtml, results = convert_and_select(html, args.xpath)
        if xhtml is not None:
            (OUTPUT_DIR / f"{stem}.xhtml").write_text(xhtml, encoding="utf-8")
            saved.append(f"{stem}.xhtml")
        if isinstance(results, str):
            print(f"    note: {results}")
        else:
            for expr, values, error in results:
                if error:
                    print(f"    xpath {expr} -> ERROR {error}")
                    continue
                print(f"    xpath {expr} -> {len(values)} value(s)")
                for value in values[: args.max_values]:
                    print(f"      {' '.join(value.split())[:200]!r}")
    print(f"    saved {OUTPUT_DIR.as_posix()}/{' + '.join(saved)}")
    return data


def parse_mode(text: str) -> tuple[str, str]:
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 2 or not all(parts):
        raise argparse.ArgumentTypeError("use JS,PROXY, e.g. enabled,disabled")
    return parts[0], parts[1]


def main() -> int:
    configure_stdout()
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("urls", nargs="+", help="page URLs, exactly as the source lists them")
    add_config_arguments(parser)
    parser.add_argument(
        "--mode",
        type=parse_mode,
        action="append",
        help="fetch in this JS,PROXY mode instead of the profile's (repeatable)",
    )
    parser.add_argument(
        "--probe", action="store_true", help="try every mode, cheapest first, then the profile's"
    )
    parser.add_argument(
        "--include-premium", action="store_true", help="add the premium proxy to --probe (costly)"
    )
    parser.add_argument(
        "--no-force",
        action="store_true",
        help="accept the crawler's cached copy (what a sync would get right now)",
    )
    parser.add_argument(
        "--xpath", action="append", default=[], help="evaluate on the converted page (repeatable)"
    )
    parser.add_argument("--max-values", type=int, default=5, help="values printed per --xpath")
    args = parser.parse_args()

    settings = load_settings(Path(args.config), args.profile, Path(args.env_file))
    api_key = settings.api_key(args.key_env)
    profile_mode = (
        settings.get("crawler_js_render_mode", "disabled") or "disabled",
        settings.get("crawler_proxy_mode", "disabled") or "disabled",
    )
    loader = settings.get("ingest_loader", "crawler")
    if settings.profile:
        print(f"profile {settings.profile}: loader {loader}, js={profile_mode[0]} proxy={profile_mode[1]}")
    if loader != "crawler":
        print(f"note: this profile fetches with '{loader}', not the crawler")

    for url in args.urls:
        print(url)
        if args.probe:
            ladder = list(PROBE_LADDER)
            if args.include_premium:
                ladder.append(("disabled", "premium"))
            for js, proxy in ladder:
                run_one(url, js, proxy, args, api_key, "")
            if loader == "crawler":
                print("  restoring the cache to the profile's mode (the next sync reuses this fetch)")
                run_one(url, *profile_mode, args, api_key, " (profile)")
        elif args.mode:
            for js, proxy in args.mode:
                run_one(url, js, proxy, args, api_key, "")
            if loader == "crawler" and not args.no_force and args.mode[-1] != profile_mode:
                print(
                    "  note: the crawler now caches this mode for this URL; the next sync gets it."
                    " Re-run without --mode to restore the profile's mode."
                )
        else:
            run_one(url, *profile_mode, args, api_key, " (profile)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
