# SEO/GEO Review Lens

Use this lens to review semantic quality for search visibility and generative engine optimization.

## SEO Focus

- Prefer specific schema.org types over generic `WebPage`.
- Check rich-result and snippet opportunities.
- Confirm page intent, entity type, and structured data output are consistent.
- Check that required and recommended properties are present where practical.
- Check that markup reflects visible or otherwise supported page content.
- Avoid unsupported schema features.

## GEO Focus

GEO means generative engine optimization: improving entity clarity and factual grounding for AI answer and retrieval systems.

Review:

- Explicit IRIs.
- Strong entity disambiguation.
- `schema:sameAs` links to authoritative sources.
- Clear `schema:about`, `schema:mentions`, `schema:subjectOf`, `schema:author`, and `schema:publisher` relationships.
- Factual provenance and no invented data.
- Consistent modeling across content clusters.
- Topical graph structure, not just valid isolated markup.

## Guardrails

- Ground recommendations in actual project mappings, templates, and observed pages.
- Do not invent unsupported schema features.
- Do not optimize for warnings by adding unverified facts.
- Keep merchant snippets and carousel beta disabled when project policy says they are disabled.
