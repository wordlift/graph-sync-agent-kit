---
name: graph-sync-curator
description: "Semantic curation workflow for WordLift graph-sync projects. Use when starting, continuing or fixing a graph-sync project, including for non-technical users: researching and creating static entities, parsing sitemaps or sheet sources, defining content clusters, prioritizing clusters, sampling pages, choosing schema.org types for Google rich results, connecting pages to static entities, extracting FAQ/video/authorship markup, running real syncs on Windows/macOS/Linux, checking the knowledge graph, and auditing/fixing schema.org or Google validation issues."
---

# Graph Sync Curator

## Overview

Use this skill to drive the day-to-day semantic curation workflow for WordLift graph-sync projects. Treat it as the primary practitioner workflow for moving from a target domain to static entities, sitemap clusters, dynamic mappings, real syncs, and validation loops.

Use `graph-sync-project` when curation decisions become concrete project edits. Use `graph-sync-repo-lifecycle` when a project must be created, cloned, prepared, committed, or pushed.

If the user asks for a full journey from project creation, repository URL, or existing checkout through curation and publishing, treat this skill as the orchestrator: coordinate with `graph-sync-repo-lifecycle` for repository setup and publishing, use `graph-sync-project` for implementation/runtime edits, and keep semantic decisions in this curator workflow.

## Working With The User

The user may not be technical: WordLift's customer success team works in these repositories without a developer background. Work so that any user gets a correct result.

- **Speak plainly.** Explain what you will do and what happened in terms of pages, page types and what search engines and AI assistants will see. Leave file names, commands and error text out unless the user asks.
- **Never ask technical questions** (XPath, runtimes, Python, SDK options, IRIs, crawler modes). Decide them from the repository, these skills and the code. Ask only what the user knows: which pages or page types matter, what the pages should say about the client, which account to use, whether a result looks right.
- **Run every command yourself**, including environment setup on the user's operating system (`graph-sync-project` `references/local-runs.md`).
- **Confirm the account before every sync.** A sync has no dry run: it writes immediately into the knowledge graph of the account whose API key the profile uses, usually the client's live graph. Before each run, show the account (id and Website URL from `graph-sync-project` `scripts/kg_check.py account`), the profile and the number of pages, and wait for a yes. Once per session, mention that a temporary account with the same Website URL avoids touching the live graph (`graph-sync-project` `references/kg-checks.md`).
- **Hand over what only the WordLift tech team can do.** A missing Google service-account file, repository secrets, the orchestrator schedule, access rights, or an error inside `worai` or the SDK: stop and write a short message the user can forward, with the repository, the profile, what is needed and the exact error line.
- **Unattended runs.** When nobody can answer (a non-interactive run whose task prompt tells you to run syncs, such as the WordLift dashboard bootstrap), the task prompt is the approval: don't wait for confirmations or forwardable messages. Name the account and every sync, and anything the tech team must do, in the final report instead.
- **Never delete from the knowledge graph.** When a change leaves old entities behind, list them for the user (`graph-sync-project` `references/kg-checks.md`).
- **Never fall back silently.** No sitemap instead of an unreadable sheet, no plain `WebPage` instead of asking about a page type, no skipped pages or changed sources without saying so first.

## Workflow

### 0. Establish project context

Before researching static entities or creating project files, determine whether the current workspace is ready for graph-sync work.

- Inspect the current directory for graph-sync project markers such as `worai.toml`, `profiles/`, mapping files, static template directories, `pyproject.toml`, `AGENTS.md`, or an initialized `.git/` repository.
- If the user says "start the graph-sync workflow" for a domain and the current directory is empty or does not contain graph-sync project markers, first coordinate with `graph-sync-repo-lifecycle` to create a new project from the WordLift graph-sync template.
- Infer a conservative project name from the domain when the user did not provide one, for example `graph-sync-example-org` for `www.example.org`.
- Ask only for details that cannot be inferred safely, such as whether to trust the Copier template or whether to initialize git and create the first commit.
- Do not start writing static entities, mappings, templates, or curation notes into an uninitialized directory.
- In an existing repository, including one bootstrapped from the WordLift dashboard, orient first and run the baseline check through `graph-sync-repo-lifecycle` ("Orient In An Existing Repository", "Baseline Check"). Summarize for the user what the project covers today (profiles, page types, sources, accounts) before proposing changes.
- After the repository exists, the checkout has been inspected, and local API-key readiness has been checked through `graph-sync-repo-lifecycle`, continue with static entities in this curator workflow.

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
- Let the static templates own the homepage (`schema:url` with the trailing slash) and keep the homepage out of every profile's source.
- Connect static entities to dynamic page entities in later mappings.

Read `references/static-entities.md` for the detailed static entity checklist.

### 2. Parse the source and define content clusters

Before writing cluster mappings:

- Read the project's source: the sitemap, the client's Google Sheet, or the URL list the client provided. A sheet provided by the client wins over the sitemap.
- Count total URLs.
- Group URLs by path patterns, page templates, and page intent.
- Exclude static assets, documents, images, and URLs already handled by static templates.
- Produce a prioritized content-cluster overview.
- Identify representative sample URLs for the next cluster.
- When the URLs don't reveal the page type, plan one Google Sheet tab and one profile per type instead of URL patterns (`graph-sync-project` `references/sources-and-profiles.md`).

Read `references/sitemap-clustering.md` when planning or reviewing clusters.

### 3. Work on the next content cluster

For the highest-priority unfinished cluster:

- Stay scoped to the selected cluster until it is validated; capture unrelated URL patterns as next-cluster notes.
- Fetch representative URLs as the sync does with `graph-sync-project` `scripts/fetch_page.py`; use `--probe` to find the cheapest crawler mode that returns the content.
- Extract from the fetched page HTML only. Use the browser's network panel only to understand how a page is built, never as a data source.
- Choose the most specific useful schema.org type for page intent and rich-result eligibility. Never type a page as plain `WebPage`; when no type fits, list the URLs and candidate types and ask the user.
- Do not add Breadcrumbs markup by default.
- Connect dynamic entities to static entities wherever meaningful.
- Add authorship markup whenever possible.
- Extract FAQ content when available and connect `FAQPage` to the main entity.
- Extract videos as `VideoObject` and connect them to the main entity with `schema:video` (the SDK nests `VideoObject` children through it).
- Keep merchant snippets and carousel beta disabled when project policy says they are disabled.
- Do not hardcode constants from sample pages.

Read `references/content-cluster-workflow.md` for the full cluster loop.

### 4. Validate and iterate

Run real syncs and audits for semantic work. Tests alone are not enough for curation changes.

- Confirm the account with the user, then run the profile with `--debug --output-dir output` (`graph-sync-project` `references/local-runs.md`).
- Read the failures report and fix failing pages.
- Check sample pages and twins in the knowledge graph, then clear the cache (`graph-sync-project` `scripts/kg_check.py`).
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

- Inspect `git status` before the final response.
- Summarize semantic changes.
- Summarize validation results.
- List remaining warnings or risks.
- Name what still needs the WordLift tech team (a new profile in the orchestrator, a repository secret), with a message to forward.
- If project changes exist, explicitly ask whether to prepare a commit handoff through `graph-sync-repo-lifecycle`.
- If the user confirms, hand off to `graph-sync-repo-lifecycle`.

This commit-handoff prompt is required after a successful curation session even when the user did not mention commit or publish. Do not commit or push without explicit user confirmation.
