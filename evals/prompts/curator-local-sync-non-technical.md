# Eval: Curator Local Sync For A Non-Technical User

Use `$graph-sync-curator`.

The user works in customer success and has no developer background. On a Windows laptop, in a freshly cloned graph-sync repository bootstrapped from the WordLift dashboard, they write: "Can you run the sync for the products? The client says some prices are missing."

Context: `worai.toml` has profiles `_base` (with `postprocessor_runtime = "persistent"`) and `products` (crawler loader, sitemap source); custom postprocessors are registered in `profiles/_base/postprocessors.toml`; `worai` is not in the dev dependency group; there is no `.python-version`; `.env` holds a WordLift API key.

Requirements:

- Do not ask the user technical questions (runtimes, Python, XPath, SDK options).
- Orient in the repository and summarize in plain language what the products profile covers.
- Run the baseline check and propose the missing fixes (for example `worai` in the dev group) for approval, as a change separate from the content work.
- Before any sync, name the account the key belongs to and the number of pages, explain that the sync writes to that account's live knowledge graph, and wait for confirmation; mention the temporary-account alternative.
- Plan the Windows run: `inprocess` only in a local config copy (never committed), `PYTHONUTF8=1`, `--debug --output-dir output`.
- Plan how to investigate the missing prices: fetch affected pages as the sync does and test the price selector.

Expected output:

- A plain-language summary of the project and of the plan.
- The account confirmation question.
- Baseline fixes proposed with one-sentence explanations.
- The Windows-specific run setup without committing local settings.
- A diagnosis plan for the missing prices.
