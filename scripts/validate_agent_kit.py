#!/usr/bin/env python3
"""Validate graph-sync-agent-kit packaging contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?"
    r"(?:\+[0-9A-Za-z.-]+)?$"
)

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

CODEX_MANIFEST_FIELDS = {
    "id",
    "name",
    "version",
    "description",
    "skills",
    "apps",
    "mcpServers",
    "interface",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
}

CODEX_INTERFACE_FIELDS = {
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "websiteURL",
    "privacyPolicyURL",
    "termsOfServiceURL",
    "brandColor",
    "composerIcon",
    "logo",
    "screenshots",
    "defaultPrompt",
    "default_prompt",
}

CLAUDE_MANIFEST_FIELDS = {
    "$schema",
    "name",
    "displayName",
    "description",
    "version",
    "author",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []

    validate_codex_plugin(root, errors)
    validate_claude_plugin(root, errors)
    validate_skills(root, errors)
    validate_eval_prompts(root, errors)

    if errors:
        print("Agent kit validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Agent kit validation passed: {root}")
    return 0


def validate_codex_plugin(root: Path, errors: list[str]) -> None:
    manifest = load_json(root / ".codex-plugin" / "plugin.json", errors)
    if manifest is None:
        return

    reject_todos(manifest, ".codex-plugin/plugin.json", errors)
    reject_unknown_fields(manifest, CODEX_MANIFEST_FIELDS, ".codex-plugin/plugin.json", errors)
    require_string(manifest, "name", ".codex-plugin/plugin.json", errors)
    validate_semver(manifest, ".codex-plugin/plugin.json", errors)
    require_string(manifest, "description", ".codex-plugin/plugin.json", errors)
    validate_author(manifest, ".codex-plugin/plugin.json", errors)

    skills_path = manifest.get("skills")
    if skills_path not in ("skills", "./skills", "skills/", "./skills/"):
        errors.append(".codex-plugin/plugin.json field `skills` must point to `./skills/`")

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append(".codex-plugin/plugin.json field `interface` must be an object")
        return

    reject_unknown_fields(
        interface,
        CODEX_INTERFACE_FIELDS,
        ".codex-plugin/plugin.json interface",
        errors,
    )
    for key in (
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
    ):
        require_string(interface, key, ".codex-plugin/plugin.json interface", errors)

    if "defaultPrompt" not in interface and "default_prompt" not in interface:
        errors.append(".codex-plugin/plugin.json interface must define `defaultPrompt`")

    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not all(is_non_empty_string(v) for v in capabilities):
        errors.append(".codex-plugin/plugin.json interface `capabilities` must be strings")

    brand_color = interface.get("brandColor")
    if brand_color is not None and (
        not isinstance(brand_color, str) or HEX_COLOR_RE.fullmatch(brand_color) is None
    ):
        errors.append(".codex-plugin/plugin.json interface `brandColor` must use `#RRGGBB`")


def validate_claude_plugin(root: Path, errors: list[str]) -> None:
    manifest = load_json(root / ".claude-plugin" / "plugin.json", errors)
    if manifest is None:
        return

    reject_todos(manifest, ".claude-plugin/plugin.json", errors)
    reject_unknown_fields(manifest, CLAUDE_MANIFEST_FIELDS, ".claude-plugin/plugin.json", errors)
    for key in ("name", "displayName", "description"):
        require_string(manifest, key, ".claude-plugin/plugin.json", errors)
    validate_semver(manifest, ".claude-plugin/plugin.json", errors)
    validate_author(manifest, ".claude-plugin/plugin.json", errors)


def validate_skills(root: Path, errors: list[str]) -> None:
    skills_root = root / "skills"
    if not skills_root.is_dir():
        errors.append("missing `skills/` directory")
        return

    skill_roots = [
        path
        for path in sorted(skills_root.iterdir(), key=lambda p: p.name)
        if path.is_dir() and not path.name.startswith(".")
    ]
    if not skill_roots:
        errors.append("`skills/` must contain at least one skill directory")
        return

    for skill_root in skill_roots:
        validate_skill(skill_root, errors)


def validate_skill(skill_root: Path, errors: list[str]) -> None:
    skill_md = skill_root / "SKILL.md"
    if not skill_md.is_file():
        errors.append(f"{skill_root.name}: missing SKILL.md")
        return

    try:
        contents = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{skill_root.name}: cannot read SKILL.md: {exc}")
        return

    if "[TODO:" in contents:
        errors.append(f"{skill_root.name}: SKILL.md still contains a TODO placeholder")

    frontmatter = parse_frontmatter(contents, f"{skill_root.name}/SKILL.md", errors)
    if frontmatter is None:
        return

    if frontmatter.get("name") != skill_root.name:
        errors.append(f"{skill_root.name}: frontmatter `name` must match directory name")
    if not is_non_empty_string(frontmatter.get("description")):
        errors.append(f"{skill_root.name}: frontmatter `description` must be non-empty")

    agent_manifest = skill_root / "agents" / "openai.yaml"
    if agent_manifest.is_file():
        validate_agent_manifest(agent_manifest, skill_root.name, errors)


def validate_agent_manifest(path: Path, skill_name: str, errors: list[str]) -> None:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"{skill_name}: agents/openai.yaml is invalid: {exc}")
        return

    if not isinstance(payload, dict):
        errors.append(f"{skill_name}: agents/openai.yaml must contain an object")
        return

    interface = payload.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{skill_name}: agents/openai.yaml must define `interface`")
        return

    for key in ("display_name", "short_description"):
        if not is_non_empty_string(interface.get(key)):
            errors.append(f"{skill_name}: agent interface `{key}` must be non-empty")


def validate_eval_prompts(root: Path, errors: list[str]) -> None:
    prompts_root = root / "evals" / "prompts"
    if not prompts_root.is_dir():
        errors.append("missing `evals/prompts/` directory")
        return
    if not any(prompts_root.glob("*.md")):
        errors.append("`evals/prompts/` must contain markdown prompt fixtures")


def load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        errors.append(f"missing `{path}`")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"`{path}` must be valid JSON: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"`{path}` must contain a JSON object")
        return None
    return payload


def parse_frontmatter(contents: str, label: str, errors: list[str]) -> dict[str, Any] | None:
    if not contents.startswith("---\n"):
        errors.append(f"{label}: missing YAML frontmatter")
        return None
    end = contents.find("\n---", 4)
    if end == -1:
        errors.append(f"{label}: unclosed YAML frontmatter")
        return None
    try:
        payload = yaml.safe_load(contents[4:end])
    except yaml.YAMLError as exc:
        errors.append(f"{label}: invalid YAML frontmatter: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"{label}: YAML frontmatter must contain an object")
        return None
    return payload


def validate_author(payload: dict[str, Any], label: str, errors: list[str]) -> None:
    author = payload.get("author")
    if not isinstance(author, dict):
        errors.append(f"{label} field `author` must be an object")
        return
    require_string(author, "name", f"{label} author", errors)


def validate_semver(payload: dict[str, Any], label: str, errors: list[str]) -> None:
    version = payload.get("version")
    if not isinstance(version, str) or SEMVER_RE.fullmatch(version) is None:
        errors.append(f"{label} field `version` must be strict semver")


def reject_unknown_fields(
    payload: dict[str, Any],
    allowed: set[str],
    label: str,
    errors: list[str],
) -> None:
    for key in sorted(set(payload) - allowed):
        errors.append(f"{label} field `{key}` is not allowed")


def require_string(payload: dict[str, Any], key: str, label: str, errors: list[str]) -> None:
    if not is_non_empty_string(payload.get(key)):
        errors.append(f"{label} field `{key}` must be a non-empty string")


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def reject_todos(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, str):
        if "[TODO:" in value:
            errors.append(f"{label} contains a TODO placeholder")
        return
    if isinstance(value, list):
        for item in value:
            reject_todos(item, label, errors)
        return
    if isinstance(value, dict):
        for item in value.values():
            reject_todos(item, label, errors)


if __name__ == "__main__":
    sys.exit(main())
