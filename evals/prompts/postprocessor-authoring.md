# Eval: Postprocessor Authoring

Use `$graph-sync-postprocessor-authoring`.

Create a custom graph-sync postprocessor that adds a fallback `schema:name` only when an entity has no name.

Requirements:

- Implement `process_graph(self, graph, context)`.
- Keep the transform idempotent.
- Do not delete unrelated triples.
- Add a manifest entry.
- Show how to run the SDK postprocessor runner locally.

Expected output:

- Code changes or patch plan.
- Manifest entry.
- Local validation command.
- Notes about context fields and compatibility.
