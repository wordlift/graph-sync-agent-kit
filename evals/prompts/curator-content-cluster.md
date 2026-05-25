# Eval: Curator Content Cluster

Use `$graph-sync-curator`.

Work on the **Blog / English** content cluster for `wordlift.io`.

Cluster URL pattern: `https://wordlift.io/blog/en/**`

Static entities (`WebSite`, `Organization`) have already been created.
Sample at least these URLs live before proposing anything:

- https://wordlift.io/blog/en/
- https://wordlift.io/blog/en/entity/knowledge-graph/
- https://wordlift.io/blog/en/seo/semantic-seo/

Requirements:

- Fetch and inspect each sample URL — do not assume page structure.
- Analyze page structure and identify the data source (HTML, JSON-LD, XHR).
- Choose the best schema.org type; avoid `schema:WebPage` and `schema:BreadcrumbList`.
- Derive XPath or JSONPath selectors from live page inspection, not assumptions.
- Connect authorship to a static `schema:Person` entity where an author is present.
- Extract FAQ and video markup only if the structure is actually present on the page.
- Propose a `worai graph sync run` validation command using placeholder credentials (`--config worai.toml --profile <profile-name>`); do not attempt to execute it.

Expected output:

- Sampling notes with HTTP status and observed page structure for each URL.
- At least one selector derived from live inspection (not assumed), with source quoted.
- Proposed schema.org type with justification (must not be `schema:WebPage`).
- Authorship strategy referencing a named `schema:Person` entity or explaining its absence.
- Mapping/static-template/postprocessor plan.
- Validation plan with a correctly-structured `worai graph sync run` command (placeholder credentials are acceptable).
