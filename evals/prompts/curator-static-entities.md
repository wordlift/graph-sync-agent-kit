# Eval: Curator Static Entities

Use `$graph-sync-curator`.

Create the static entities for `morganstanley.com`.

Requirements:

- Create `WebSite` with `schema:potentialAction` if supported by observed site behavior.
- Create `Organization` with as much validated data as possible.
- Include official social profiles and authoritative `sameAs` links.
- Identify key people such as CEO and founders where relevant.
- Ground all facts through research.
- Do not invent data.
- Use explicit IRIs.
- Do not use blank nodes.

Expected output:

- Concise researched facts and sources.
- Proposed static entities and relationships.
- Uncertain facts marked as unresolved.
- Next implementation steps for graph-sync project files.
