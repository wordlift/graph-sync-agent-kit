# Building Custom Postprocessors

## Class Contract
- Class must expose:
  - `process_graph(self, graph, context)`
- Return semantics:
  - return a `Graph` to replace the current graph
  - return `None` to keep input graph unchanged
- The class is instantiated without arguments.

## Class Path
- Manifest entry must use:
  - `class = "package.module:ClassName"`
- The package lives under `src/` and is installed into `.venv` by `uv sync` (`[tool.uv] package = true`). Generated projects name it after the project (`graph-sync-example-com` → `graph_sync_example_com`); older ones after the domain. Check `src/` before writing class paths.
- Old repositories with `[tool.setuptools] packages = []` keep the package out of the environment (`No module named '<package>'`); replace it with `[tool.setuptools.packages.find]` / `where = ["src"]` and run `uv sync --reinstall-package <project-name>`.

## Minimal Example

Cast `ListItem` positions, emitted as plain strings by the mapping, to integers:

```python
from rdflib import Graph, Literal, Namespace, XSD

SCHEMA = Namespace("http://schema.org/")


class IntegerPositionsPostprocessor:
    def process_graph(self, graph: Graph, context):
        for subject, value in list(graph.subject_objects(SCHEMA.position)):
            text = str(value).strip()
            if text.isdigit():
                graph.set((subject, SCHEMA.position, Literal(int(text), datatype=XSD.integer)))
        return graph
```

## Suggested Layout
```text
src/graph_sync_example_com/
  __init__.py
  postprocessors/
    __init__.py
    positions.py
profiles/_base/postprocessors.toml
```

Manifest entry:

```toml
[[postprocessors]]
class = "graph_sync_example_com.postprocessors.positions:IntegerPositionsPostprocessor"
```

## What A Postprocessor May Change

A postprocessor changes **values and links between entities that already exist**: set positions, cast literals, normalise URLs, link two existing entities, drop a node. It must not add new subjects, and must not rewrite IRIs by building strings. The IRI logic lives in the SDK steps around it:

- **First import:** the page root is still a staging IRI, so a node added under it is re-based by the canonical step and nests correctly. Everything looks fine.
- **Re-sync of a page whose content changed:** the reconciler has already swapped a `WebPage` root to its existing canonical IRI, so the canonical step has nothing to re-base. Added children are re-minted as root entities with generic slugs (`image-objects/imageobject`, `-2`, `-3`) that collide across pages. Pages skipped by the import hash keep their old children, which hides the problem until content changes.

What to do instead:

1. Create the node in the YARRRML mapping, staged under the page root. The SDK handles it on every run.
2. If it must come from a postprocessor, use types the SDK nests by policy (`Question`/`Answer` via `mainEntity`/`acceptedAnswer`, `VideoObject` via `video`, `ImageObject` via `image`), mint the IRI with the allocator (`context.ids.new_child(graph, parent=page_iri, type_name="VideoObject", index=n, force_index=True, url_value=...)`), and test a **second** sync of a changed page.
3. A pattern that held across re-syncs: a **first** custom postprocessor that, when `context.existing_web_page_id` is set, re-bases every `<staging root>/…` subject and object onto `<existing_web_page_id>/…`.

Never emit a static-template entity (`Organization`, `WebSite`) from a page graph with only some of its properties: with `graph_write_strategy = "put"` the page write replaces the template's version. Reference it as an object only.

Older repositories often mint their own IRIs in postprocessors (`graph.add((URIRef(f"{page}/…"), …))`). They work on a fresh graph and drift on every re-sync. When you touch one, move the node into the mapping or apply pattern 3; strays already written stay until deleted.

## Values

- URL-valued properties (`schema:url`, `schema:image`, `schema:contentUrl`, `schema:embedUrl`, `schema:thumbnailUrl`) are plain string literals, never `URIRef`.
- Typed literals are safe here (unlike in mappings): `Literal(3, datatype=XSD.integer)`, `Literal(date, datatype=XSD.date)`.
- Never write empty values, `"None"`, or placeholders.

## Data Sources

- Read the page from `context.response.web_page.html` (the raw fetched HTML) when the mapping can't express something, for example list positions in document order.
- Never read embedded JSON (`__NEXT_DATA__`, JSON-LD) or the page's own XHR endpoints.
- External APIs and Google Sheets are allowed:
  - Send a `User-Agent` header with `urllib`/`requests` calls; Cloudflare rejects urllib's default one (error 1010).
  - Read secrets from `os.environ`. Each one also needs a repository secret **and** a line in the workflow's `env:` block, or CI silently skips the postprocessor.
  - A Google service-account value is a file path locally and the JSON **content** on CI. Accept both: if the value starts with `{`, use `Credentials.from_service_account_info(json.loads(value), scopes=[...])`, otherwise `from_service_account_file`. Use read-only scopes (`spreadsheets.readonly`).

## Failure Behavior

- An exception fails the page (the URL is reported as failed; other pages continue).
- Postprocessors that depend on optional external data usually catch their own errors and skip. Log a warning when they do: a silent skip hides missing secrets and broken APIs.

## Context Fields

Read only fields every runtime provides (`references/runtime.md`): `url`, `profile`, `profile_name`, `exports`, `account_key`, `response`, `existing_web_page_id`, `ids`, and on `account` only `dataset_uri`, `country_code`, `language`. Other `account` attributes exist only under `inprocess`, so code that reads them passes locally on Windows and fails on CI.

## Local Validation Workflow
- Prepare:
  - `./tmp/input_graph.nq`: a page graph as N-Quads (convert one from `output/debug_cloud/<profile>/cloud_<sha256(url)>.ttl`, or build a small one)
  - `./tmp/context.json`: `{"profile_name": …, "profile": {…}, "url": …, "dataset_uri": …, "language": …, "account_key": …, "exports": {…}, "existing_web_page_id": null, "response": {"id": null, "web_page": {"url": …, "html": …}}}`
- Resolve the Python runner:
  - prefer the project-documented postprocessor test command
  - prefer `uv run python -m ...` when the project uses `uv` (works on every OS)
  - use the project virtual environment's Python directly only when `uv` is unavailable (`.venv/bin/python` on macOS/Linux, `.venv\Scripts\python.exe` on Windows)
  - ask before installing/fetching Python packages
- Run the SDK's one-shot runner (the module the `oneshot` runtime calls):

```bash
uv run python -m wordlift_sdk.kg_build.postprocessors.oneshot \
  --class my_project.postprocessors:IntegerPositionsPostprocessor \
  --input-graph ./tmp/input_graph.nq \
  --output-graph ./tmp/output_graph.nq \
  --context ./tmp/context.json
```

- Inspect output:
  - `./tmp/output_graph.nq`
  - run it again on its own output to check idempotence
- For manifest-run failures with temp retention enabled:
  - `output/postprocessor_debug/<class_path_sanitized>/`
- Then a real sync, and a second sync of a page whose content changed, when the postprocessor touches IRIs.

## Safety Guidelines
- Prefer idempotent transforms.
- Keep output deterministic.
- Avoid deleting unrelated triples unless explicitly intended.
- Preserve expected root `WebPage` identity behavior.
- Avoid logging secrets from context payloads.
- Do not rely on constants extracted from sample pages used for mapping/postprocessor testing; implement selectors/rules/normalization that work across pages in the configured source.
- Do not add hard-coded fallbacks unless the user explicitly authorizes that behavior.

## Compatibility
- Pin `wordlift-sdk` to a tested range, with the `all` extra (`wordlift-sdk[all]`): from 8.5.0 the plain package lacks modules the postprocessor workers import on CI.
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
- `context.account` remains the clean `/me` account object under `inprocess`; under the subprocess runtimes it carries only `dataset_uri`, `country_code` and `language`.
