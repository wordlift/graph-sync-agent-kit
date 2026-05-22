# Eval: Curator Sitemap Clusters

Use `$graph-sync-curator`.

Parse the sitemap for a graph-sync project and define content clusters.

Requirements:

- Count total URLs.
- Exclude assets and URLs already handled statically.
- Group URLs by path pattern, page template, and content intent.
- Prioritize clusters by semantic value, rich-result opportunity, and coverage.

Expected output:

- Total URL count.
- Exclusion summary.
- Cluster overview with sample URLs.
- Recommended next cluster and rationale.
