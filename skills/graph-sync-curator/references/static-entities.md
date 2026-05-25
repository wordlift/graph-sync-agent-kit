# Static Entities

Use static entities to establish stable graph anchors before dynamic page mappings.

## Research Requirements

- Use available web/browser tools to research the target domain.
- Prefer official sources first: website footer, about pages, contact pages, press pages, investor pages, social profiles, and authoritative registries.
- Cross-check important facts such as legal name, headquarters, founder, CEO, and social profile URLs.
- Mark uncertain facts as unresolved instead of inventing values.

## Entity Checklist

Create or review:

- `WebSite`
  - Explicit IRI.
  - `schema:url` as a plain URL literal.
  - `schema:name`.
  - `schema:publisher` or equivalent link to the organization.
  - `schema:potentialAction` when observed search/action behavior supports it.
- `Organization`
  - Explicit IRI.
  - `schema:name`, `schema:url`, logo/image when validated.
  - `schema:sameAs` links to official social and authority profiles.
  - Address/contact details when validated.
  - Links to founders, CEO, parent/subsidiary, or brand entities when useful.
- `Brand`
  - Create only when the public brand identity is meaningfully distinct from the legal or operating organization.
  - Use an explicit IRI, validated `schema:name`, and connect the organization with `schema:brand`.
- `Person`
  - Explicit IRI.
  - Role/title and organization relationship.
  - Official sameAs links only when validated.

## Modeling Rules

- Do not use blank nodes.
- Keep URL-valued properties as plain literals, not IRIs or `xsd:anyURI`.
- Use `http://schema.org` as the default vocabulary base URI unless explicitly required otherwise.
- Prefer stable, readable exported IRIs for static roots.
- Avoid duplicating entities already modeled elsewhere in the project.
