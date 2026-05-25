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
- Fallback output policy: catch-all/default mappings should not emit generic `WebPage` entities unless explicitly intended.
- Template variant expectations for `.j2`, `.liquid`, or plain mapping files.
- Morph-KGC compatibility.
- Clear, minimal mapping rules.
- Extraction rules that generalize across pages in the configured source.
- Required vs optional field handling: selective sources should prevent empty triples, while validation should flag missing required fields.
- Canonicalizer-friendly IDs: dynamic subject IRIs should be simple staging IDs, and root entities should expose type, `schema:url`, and `schema:name`/`schema:headline`.
- Postprocessor escalation: keep stable scalar fields in YARRRML, but flag rich text cleanup, nested FAQ/video nodes, API/XHR enrichment, deduplication, validation, or shared logic as postprocessor candidates.
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
- Do not use a root/page iterator to emit optional or conditionally present values that may become empty literals or malformed IRIs.
- Do not silently downgrade expected authorship or other required creative-work properties; missing required data is a validation issue.
- Do not add hardcoded fallbacks unless the user explicitly authorizes them.
- Escalate when a requirement cannot be implemented cleanly with current mapping capabilities.
