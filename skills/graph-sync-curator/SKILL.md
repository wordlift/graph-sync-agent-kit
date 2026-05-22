---
name: graph-sync-curator
description: "Semantic curation workflow for WordLift graph-sync projects. Use when starting or iterating a graph-sync project: researching and creating static entities, parsing sitemaps, defining content clusters, prioritizing clusters, sampling pages, choosing schema.org types for Google rich results, connecting pages to static entities, extracting FAQ/video/authorship markup, running real syncs, and auditing/fixing schema.org or Google validation issues."
---

# Graph Sync Curator

## Overview

Use this skill to drive the day-to-day semantic curation workflow for WordLift graph-sync projects. Treat it as the primary practitioner workflow for moving from a target domain to static entities, sitemap clusters, dynamic mappings, real syncs, and validation loops.

Use `graph-sync-project` when curation decisions become concrete project edits. Use `graph-sync-repo-lifecycle` when tested work should be committed or pushed.

If the user asks for a full journey from project creation, repository URL, or existing checkout through curation and publishing, treat this skill as the orchestrator: coordinate with `graph-sync-repo-lifecycle` for repository setup and publishing, use `graph-sync-project` for implementation/runtime edits, and keep semantic decisions in this curator workflow.

## Workflow

### 1. Create static entities

Start with static entities before dynamic content clusters.

- Research the target domain using available web/browser tools.
- Create `WebSite` and add `schema:potentialAction` when observed site behavior supports it.
- Create `Organization` with as much validated data as possible.
- Add official social profiles and authoritative `schema:sameAs` links.
- Identify key people such as CEOs, founders, and prominent leaders when relevant.
- Ground all facts in observed sources; do not invent data.
- Use explicit IRIs and avoid blank nodes.
- Keep URL-valued schema properties as plain literals.
- Connect static entities to dynamic page entities in later mappings.

Read `references/static-entities.md` for the detailed static entity checklist.

### 2. Parse sitemap and define content clusters

Before writing cluster mappings:

- Parse the sitemap and count total URLs.
- Group URLs by path patterns, page templates, and page intent.
- Exclude static assets, documents, images, and URLs already handled by static templates.
- Produce a prioritized content-cluster overview.
- Identify representative sample URLs for the next cluster.

Read `references/sitemap-clustering.md` when planning or reviewing sitemap clusters.

### 3. Work on the next content cluster

For the highest-priority unfinished cluster:

- Sample representative URLs with Playwright or another available browser/tooling path.
- Inspect HTML and XHR/network traffic before finalizing extraction.
- Prefer structured upstream sources over brittle HTML parsing when available.
- Choose the most specific useful schema.org type for page intent and rich-result eligibility.
- Avoid generic `WebPage` when a more specific type is available.
- Do not add Breadcrumbs markup by default.
- Connect dynamic entities to static entities wherever meaningful.
- Add authorship markup whenever possible.
- Extract FAQ content when available and connect `FAQPage` to the main entity.
- Extract videos as `VideoObject` and connect them to the main entity with `schema:about` / `schema:subjectOf`.
- Keep merchant snippets and carousel beta disabled when project policy says they are disabled.
- Do not hardcode constants from sample pages.

Read `references/content-cluster-workflow.md` for the full cluster loop.

### 4. Validate and iterate

Run real syncs and audits for semantic work. Tests alone are not enough for curation changes.

- Audit schema.org issues and Google errors/warnings.
- Fix schema.org issues and Google errors.
- Attempt to fix Google warnings when practical and aligned with the project goal.
- Inspect generated TTL/debug artifacts where useful.
- Repeat until the cluster is clean enough for the agreed acceptance criteria.

Read `references/validation-loop.md` for the validation loop and acceptance checklist.

### 5. Review SEO/GEO quality

Use the SEO/GEO review lens before declaring a cluster complete.

- Check search visibility, rich-result fit, and snippet opportunities.
- Check generative engine optimization: entity clarity, provenance, authorship, relationships, and topical graph structure.
- Confirm recommendations are grounded in actual mappings/templates and observed page behavior.
- Avoid unsupported schema features.

Read `references/seo-geo-review.md` for the review lens.

### 6. Prepare validated changes for publishing

After generated artifacts are tested, validated, and accepted:

- Summarize semantic changes.
- Summarize validation results.
- List remaining warnings or risks.
- Suggest publishing the validated changes.
- If the user confirms, hand off to `graph-sync-repo-lifecycle`.

Do not push without explicit user confirmation.
