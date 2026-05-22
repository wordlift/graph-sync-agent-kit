---
name: graph-sync-yarrrml-review
description: "YARRRML and RML review workflow for WordLift graph-sync mappings. Use when writing, auditing, or debugging mapping files for selector correctness, route compatibility, Morph-KGC behavior, duplicate mappings, extraction robustness, or schema.org output quality."
---

# Graph Sync YARRRML Review

## Overview

Use this skill to review or improve YARRRML/RML mappings in graph-sync projects. Focus on correctness, maintainability, runtime compatibility, and semantic output quality.

Use `graph-sync-project` for broader project edits and runtime configuration.

## Review Focus

Check mappings for:

- Relative XPath selectors.
- No duplicate mappings.
- Route/fallback compatibility with the active profile.
- Template variant expectations for `.j2`, `.liquid`, or plain mapping files.
- Morph-KGC compatibility.
- Clear, minimal mapping rules.
- Extraction rules that generalize across pages in the configured source.
- Avoidance of hardcoded constants from sample pages.
- Explicit IRIs and no blank nodes in emitted entities.
- URL-valued schema properties as plain literals.
- More specific schema.org types instead of generic `WebPage` when possible.

## Process

When reviewing:

- Inspect the relevant mapping file and profile configuration.
- Identify the source pages or representative samples used by the mapping.
- Confirm selectors are grounded in real source structure.
- Check whether XHR/network data offers a more stable source than HTML parsing.
- Review the generated TTL or debug output when available.
- Lead with concrete findings, ordered by severity.
- Include file/line references when possible.

## Guardrails

- Do not invent unsupported function syntax.
- Do not use JSON-LD or other structured data markup as an extraction source.
- Do not introduce absolute XPath selectors.
- Do not add hardcoded fallbacks unless the user explicitly authorizes them.
- Escalate when a requirement cannot be implemented cleanly with current mapping capabilities.
