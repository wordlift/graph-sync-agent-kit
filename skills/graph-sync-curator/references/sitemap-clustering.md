# Sitemap Clustering

Use sitemap clustering to plan dynamic graph-sync work by page intent and template pattern.

## Parse

- Fetch or inspect the source the project uses: the sitemap, the client's Google Sheet tabs, or the URL list. A sheet or list provided by the client wins over the sitemap; a sheet that can't be read is a blocker for the tech team, not a reason to use the sitemap.
- Count total URLs.
- Exclude image, static asset, document, and media URLs (`url_regex`).
- Exclude URLs already handled by static templates, the homepage included.
- Note sitemap partitions if multiple sitemap files exist.
- Note page types the sitemap misses: they need another source (a sheet tab).

## Cluster

Group URLs by:

- Path pattern.
- Page template.
- Page intent.
- Content type.
- Business priority.
- Rich-result opportunity.
- Relationship to existing static entities.

Examples:

- Product pages.
- Category or collection pages.
- Article or blog pages.
- Location pages.
- Event pages.
- FAQ/help pages.
- Video pages.
- People/profile pages.

When the paths don't reveal the type (no `/blog/`-like segment or id pattern per type), group the pages by a template marker in their HTML (the `<body>` class, the main container), spot-check a few per group, and plan one sheet tab and one profile per type. Don't type pages with lists of slugs in route patterns (`graph-sync-project` `references/sources-and-profiles.md`).

## Prioritize

Prefer clusters that offer:

- Strong semantic value.
- Clear schema.org type.
- Large URL coverage.
- Rich-result eligibility.
- Strong links to static entities.
- Clean and repeatable extraction patterns.

## Output

Provide:

- Total URL count.
- Excluded URL count and reasons.
- Cluster table with sample URLs, the proposed schema.org type, and how the cluster is selected (route pattern or sheet tab).
- Recommended next cluster.
- Unknowns or sampling needs.
