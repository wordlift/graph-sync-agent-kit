# Building Custom Postprocessors

## Class Contract
- Class must expose:
  - `process_graph(self, graph, context)`
- Return semantics:
  - return a `Graph` to replace the current graph
  - return `None` to keep input graph unchanged

## Class Path
- Manifest entry must use:
  - `class = "package.module:ClassName"`

## Minimal Example
```python
from rdflib import Graph, Literal, Namespace

SCHEMA = Namespace("http://schema.org/")


class AddSimpleNameFallback:
    def process_graph(self, graph: Graph, context):
        for subject in list(graph.subjects()):
            if (subject, SCHEMA.name, None) in graph:
                continue
            graph.add((subject, SCHEMA.name, Literal("Untitled")))
        return graph
```

## Suggested Layout
```text
my_project/
  __init__.py
  postprocessors.py
profiles/_base/postprocessors.toml
```

Manifest entry:

```toml
[[postprocessors]]
class = "my_project.postprocessors:AddSimpleNameFallback"
```

## Local Validation Workflow
- Prepare:
  - `./tmp/input_graph.nq`
  - `./tmp/context.json`
- Resolve the Python runner:
  - prefer the project-documented postprocessor test command
  - prefer `uv run python -m ...` when the project uses `uv`
  - use `.venv/bin/python -m ...` when the project has a local virtual environment
  - use active `python -m ...` only after confirming it can import `wordlift_sdk`
  - ask before installing/fetching Python packages
- Run with the resolved Python:

```bash
python -m wordlift_sdk.kg_build.postprocessor_runner \
  --class my_project.postprocessors:AddSimpleNameFallback \
  --input-graph ./tmp/input_graph.nq \
  --output-graph ./tmp/output_graph.nq \
  --context ./tmp/context.json
```

- Inspect output:
  - `./tmp/output_graph.nq`
- For manifest-run failures with temp retention enabled:
  - `output/postprocessor_debug/<class_path_sanitized>/`

## Safety Guidelines
- Prefer idempotent transforms.
- Keep output deterministic.
- Avoid deleting unrelated triples unless explicitly intended.
- Preserve expected root `WebPage` identity behavior.
- Avoid logging secrets from context payloads.
- Do not rely on constants extracted from sample pages used for mapping/postprocessor testing; implement selectors/rules/normalization that work across pages in the configured source.
- Do not add hard-coded fallbacks unless the user explicitly authorizes that behavior.

## Compatibility
- Pin `wordlift-sdk` to a tested range.
- Revalidate after SDK upgrades:
  - context payload fields
  - manifest parsing/defaults
  - runner module path and flags

## SDK 5.1.1+ Context Migration
- `context.settings` was removed.
  - Before: `context.settings["api_url"]`
  - After: `context.profile["settings"]["api_url"]`
- `context.account.key` is no longer injected.
  - Before: `context.account["key"]` or `context.account.key`
  - After: `context.account_key`
- `context.account` remains the clean `/me` account object.
