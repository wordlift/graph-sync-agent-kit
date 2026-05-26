#!/usr/bin/env python3
"""Update marketplace refs for the graph-sync-agent-kit release."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_PLUGIN_NAME = "graph-sync-agent-kit"
SEMVER_TAG_RE = re.compile(r"^v(?P<version>\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)$")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--marketplace-root",
        required=True,
        type=Path,
        help="Path to the checked-out wordlift/agent-marketplace repository.",
    )
    parser.add_argument(
        "--ref",
        required=True,
        help="Release tag to publish, for example v0.2.0.",
    )
    parser.add_argument(
        "--plugin-name",
        default=DEFAULT_PLUGIN_NAME,
        help=f"Marketplace plugin name. Defaults to {DEFAULT_PLUGIN_NAME}.",
    )
    args = parser.parse_args()

    match = SEMVER_TAG_RE.fullmatch(args.ref)
    if match is None:
        print(
            f"error: --ref must be a semver tag such as v0.2.0: {args.ref}",
            file=sys.stderr,
        )
        return 2

    marketplace_root = args.marketplace_root.resolve()
    version = match.group("version")

    codex_path = marketplace_root / ".agents" / "plugins" / "marketplace.json"
    claude_path = marketplace_root / ".claude-plugin" / "marketplace.json"

    codex = load_json(codex_path)
    claude = load_json(claude_path)

    codex_changed = update_codex(codex, args.plugin_name, args.ref)
    claude_changed = update_claude(claude, args.plugin_name, args.ref, version)

    if codex_changed:
        write_json(codex_path, codex)
    if claude_changed:
        write_json(claude_path, claude)

    if codex_changed or claude_changed:
        print(f"Updated {args.plugin_name} marketplace refs to {args.ref}.")
    else:
        print(f"Marketplace already points {args.plugin_name} at {args.ref}.")
    return 0


def update_codex(catalog: dict[str, Any], plugin_name: str, ref: str) -> bool:
    entry = find_plugin(catalog, plugin_name, "Codex")
    source = require_object(entry.get("source"), "Codex plugin source")

    if source.get("ref") == ref:
        return False

    source["ref"] = ref
    return True


def update_claude(
    catalog: dict[str, Any],
    plugin_name: str,
    ref: str,
    version: str,
) -> bool:
    entry = find_plugin(catalog, plugin_name, "Claude")
    source = require_object(entry.get("source"), "Claude plugin source")

    changed = False
    if source.get("ref") != ref:
        source["ref"] = ref
        changed = True
    if entry.get("version") != version:
        entry["version"] = version
        changed = True
    return changed


def find_plugin(catalog: dict[str, Any], plugin_name: str, label: str) -> dict[str, Any]:
    plugins = catalog.get("plugins")
    if not isinstance(plugins, list):
        raise ValueError(f"{label} marketplace must contain a plugins array")

    matches = [
        entry
        for entry in plugins
        if isinstance(entry, dict) and entry.get("name") == plugin_name
    ]
    if not matches:
        raise ValueError(f"{label} marketplace does not contain {plugin_name}")
    if len(matches) > 1:
        raise ValueError(f"{label} marketplace contains duplicate {plugin_name} entries")
    return matches[0]


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing marketplace file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
