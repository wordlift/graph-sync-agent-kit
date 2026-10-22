---
name: graph-sync-yarrrml-review
description: "YARRRML and XPath workflow for WordLift graph-sync mappings. Use when writing, auditing, or debugging mapping files for selector correctness, iterator scope, route compatibility, worph behavior, staging subjects, duplicate mappings, extraction robustness, or schema.org output quality."
---

# Graph Sync YARRRML Review

## Overview

Use this skill to write, review or improve YARRRML/RML mappings in graph-sync projects. Focus on correctness, maintainability, runtime compatibility, and semantic output quality.

- `references/yarrrml.md`: iterators, references, subjects, patterns (page root, FAQ, video, item lists), and the `worph` specifics that silently drop or corrupt values.
- `references/xpath.md`: the XPath subset, how `worph` evaluates it, and anchor-based selector recipes.

Use `graph-sync-project` for broader project edits, runtime configuration, identity rules (`references/mappings.md`) and policy (`references/policy.md`).

## Review Focus

Check mappings for:

- Iterators: `/` for page-level values; scoped iterators only for repeated items; no bare relative iterators (`html`), which match nothing on `worph`.
- References that leave a scoped iterator's subtree (`//head` from an `<li>`, sibling counts): they return nothing on `worph`.
- XPath anchored on ids, classes and attributes, with the safe class match; no positional paths from the document root.
- Selectors that hold on the HTML the sync actually fetches (the profile's crawler mode, the SDK's XHTML: no `<tbody>`).
- No duplicate mappings.
- Route/fallback compatibility with the active profile: every URL routed to a mapping must produce nodes; unmapped pages stay out of the source.
- Template variant expectations for `.j2`, `.liquid`, or plain mapping files.
- Clear, minimal mapping rules.
- Extraction rules that generalize across pages in the configured source.
- Required vs optional field handling: selective sources should prevent empty triples (`normalize-space()` of a missing node emits `""`), while validation should flag missing required fields.
- Page identity: the root uses `__URL__` for its subject and `schema:url`, never `rel=canonical` or `og:url`; one first-level entity per page carries the page URL.
- Staging subjects: the root at `{{ dataset_uri }}/<container>/__URL__`, children staged under it and keyed by a stable attribute; no `__URL__#fragment` subjects.
- The root type: the most specific type that fits, never plain `WebPage`.
- Root entities expose a type, `schema:url`, and `schema:name`/`schema:headline`.
- No `datatype:` other than `xsd:string`; URL-valued properties as plain literals; links between entities as `type: iri`.
- `replace()` / `tokenize()` patterns that can match an empty string (the value is silently dropped).
- Text joins in document order (`descendant::text()`, not `//text()`).
- Postprocessor escalation: keep everything addressable in the HTML in YARRRML (`worph` runs XPath 2.0 conditionals and string functions); flag typed literals, positions from scoped iterators, data outside the page, deduplication or cross-entity linking as postprocessor candidates.
- Avoidance of hardcoded constants from sample pages.
- Explicit IRIs and no blank nodes in emitted entities.

## Process

When reviewing:

- Inspect the relevant mapping file and profile configuration.
- Identify the source pages or representative samples used by the mapping.
- Confirm selectors are grounded in real source structure: fetch samples with `graph-sync-project`'s `scripts/fetch_page.py` and evaluate the mapping's expressions with `--xpath`.
- Review the generated TTL or debug output when available (`output/debug_cloud/<profile>/`).
- Lead with concrete findings, ordered by severity.
- Include file/line references when possible.

## Guardrails

- Do not invent unsupported function syntax.
- Do not use JSON-LD, embedded `<script>` JSON or the page's XHR responses as an extraction source.
- Do not introduce positional XPath paths from the document root.
- Do not use a root/page iterator to emit optional or conditionally present values that may become empty literals or malformed IRIs.
- Do not silently downgrade expected authorship or other required creative-work properties; missing required data is a validation issue.
- Do not add hardcoded fallbacks unless the user explicitly authorizes them.
- Escalate when a requirement cannot be implemented cleanly with current mapping capabilities.
