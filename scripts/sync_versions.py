#!/usr/bin/env python3
"""Sync plugin manifest versions from pyproject.toml."""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any


MANIFEST_PATHS = (
    Path(".codex-plugin/plugin.json"),
    Path(".claude-plugin/plugin.json"),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if plugin manifests are not already synced.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    version = read_project_version(root / "pyproject.toml")
    changed: list[Path] = []

    for relative_path in MANIFEST_PATHS:
        path = root / relative_path
        payload = read_json(path)
        current = payload.get("version")
        if current == version:
            continue

        if args.check:
            print(
                f"{relative_path}: version {current!r} does not match "
                f"pyproject.toml version {version!r}",
                file=sys.stderr,
            )
            changed.append(relative_path)
            continue

        payload["version"] = version
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        changed.append(relative_path)

    if args.check and changed:
        print("Run `python scripts/sync_versions.py` to update plugin manifests.", file=sys.stderr)
        return 1

    if changed:
        names = ", ".join(str(path) for path in changed)
        print(f"Synced plugin manifest versions to {version}: {names}")
    else:
        print(f"Plugin manifest versions already synced to {version}")
    return 0


def read_project_version(path: Path) -> str:
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Cannot read {path}: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise SystemExit(f"{path} is invalid TOML: {exc}") from exc

    version = payload.get("project", {}).get("version")
    if not isinstance(version, str) or not version.strip():
        raise SystemExit(f"{path} must define [project] version")
    return version


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path} is invalid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise SystemExit(f"{path} must contain a JSON object")
    return payload


if __name__ == "__main__":
    sys.exit(main())
