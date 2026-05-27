# Graph Sync Agent Kit

Installable agent skills and maintainer eval prompts for WordLift graph-sync projects.

This repository contains reusable agent workflows that were extracted from graph-sync project specs and day-to-day implementation practice. The same `skills/` directory can be packaged for Claude Code, packaged for Codex, or installed directly as Codex skills.

## Skill Inventory

- `graph-sync-curator` — day-to-day semantic curation; orchestrates the other skills end-to-end.
- `graph-sync-project` — technical project edits: mappings, templates, postprocessors, CLI, and validation.
- `graph-sync-repo-lifecycle` — repository setup, commit, and publish.
- `graph-sync-yarrrml-review` — focused YARRRML/RML mapping review.
- `graph-sync-postprocessor-authoring` — postprocessor authoring and debugging.
- `graph-sync-github-workflow-review` — GitHub Actions workflow review.

Each skill's `SKILL.md` is the authoritative reference for its capabilities.

## Repository Layout

```text
.codex-plugin/
  plugin.json

.claude-plugin/
  plugin.json

scripts/
  sync_versions.py
  validate_agent_kit.py

skills/
  graph-sync-curator/
  graph-sync-project/
  graph-sync-repo-lifecycle/
  graph-sync-yarrrml-review/
  graph-sync-postprocessor-authoring/
  graph-sync-github-workflow-review/

evals/
  prompts/

pyproject.toml
```

The `skills/` folders are the installable runtime units. The `evals/prompts/` files are maintainer fixtures for forward-testing skills and should not be installed as skills.

## Installation

Use the repository from:

```text
git@github.com:wordlift/graph-sync-agent-kit.git
```

### Claude Code Plugin

Install through the WordLift agent marketplace:

```bash
claude plugin marketplace add wordlift/agent-marketplace
claude plugin install graph-sync-agent-kit@wordlift
```

Update an installed plugin after a new marketplace release:

```bash
claude plugin update graph-sync-agent-kit@wordlift
```

For local development, clone the repository and load it directly:

```bash
git clone git@github.com:wordlift/graph-sync-agent-kit.git
claude --plugin-dir ./graph-sync-agent-kit
```

When installed as a Claude Code plugin, invoke skills with the plugin namespace:

```text
/graph-sync-agent-kit:graph-sync-curator start the graph-sync workflow for www.example.org
```

### Codex Plugin

Install through the WordLift agent marketplace:

```bash
codex plugin marketplace add wordlift/agent-marketplace --ref main
codex plugin add graph-sync-agent-kit@wordlift
```

Update an installed plugin after a new marketplace release:

```bash
codex plugin marketplace upgrade wordlift
codex plugin add graph-sync-agent-kit@wordlift
```

The marketplace points Codex at this repository as the Git-backed plugin source. Start a new Codex thread after installing or updating the plugin so the skills are loaded.

### Codex Skill Install

Ask Codex to install every skill in this repository:

```text
Use $skill-installer to install all skills under skills/ from wordlift/graph-sync-agent-kit.
```

Install all skills in this kit. They are designed to work together: `graph-sync-curator` orchestrates the workflow, while the other skills provide project, lifecycle, mapping, postprocessor, and GitHub workflow support.

Restart Codex after installing skills.

### Manual Codex Install

Clone the repository and copy all skill folders into Codex's skills directory:

```bash
git clone git@github.com:wordlift/graph-sync-agent-kit.git
cd graph-sync-agent-kit
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/graph-sync-* "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Restart Codex after copying skills.

## Usage

The prompts below are intentionally concrete. Replace `example.org`, repository URLs, profiles, and cluster names with the project you are working on. Claude Code plugin skills use `/graph-sync-agent-kit:<skill>`. Codex skills use `$<skill>`.

| Scenario | Claude Code plugin | Codex |
| --- | --- | --- |
| Start new project | `/graph-sync-agent-kit:graph-sync-curator start the graph-sync workflow for www.example.org` | `Use $graph-sync-curator to start the graph-sync workflow for www.example.org.` |
| Continue current checkout | `/graph-sync-agent-kit:graph-sync-curator continue the graph-sync workflow for this existing project` | `Use $graph-sync-curator to continue the graph-sync workflow for this existing project.` |
| Continue remote repository | `/graph-sync-agent-kit:graph-sync-curator continue the graph-sync workflow for git@github.com:wordlift/graph-sync-example-org.git` | `Use $graph-sync-curator to continue the graph-sync workflow for git@github.com:wordlift/graph-sync-example-org.git.` |
| Create project repository | `/graph-sync-agent-kit:graph-sync-repo-lifecycle create a new graph-sync project for example.org from the WordLift graph-sync template. Use the project name graph-sync-example-org and prepare it for the first working session.` | `Use $graph-sync-repo-lifecycle to create a new graph-sync project for example.org from the WordLift graph-sync template. Use the project name graph-sync-example-org and prepare it for the first working session.` |
| Clone and prepare an existing project | `/graph-sync-agent-kit:graph-sync-repo-lifecycle clone git@github.com:wordlift/graph-sync-example-org.git and prepare the checkout for work` | `Use $graph-sync-repo-lifecycle to clone git@github.com:wordlift/graph-sync-example-org.git and prepare the checkout for work.` |
| Create static entities | `/graph-sync-agent-kit:graph-sync-curator create the static entities for example.org and propose the graph-sync project files that should represent them` | `Use $graph-sync-curator to create the static entities for example.org and propose the graph-sync project files that should represent them.` |
| Parse sitemap and prioritize clusters | `/graph-sync-agent-kit:graph-sync-curator parse the sitemap for example.org and recommend the next content cluster to implement` | `Use $graph-sync-curator to parse the sitemap for example.org and recommend the next content cluster to implement.` |
| Work on a content cluster | `/graph-sync-agent-kit:graph-sync-curator work on the product pages cluster for example.org and propose the graph-sync changes needed for that cluster` | `Use $graph-sync-curator to work on the product pages cluster for example.org and propose the graph-sync changes needed for that cluster.` |
| Update project files safely | `/graph-sync-agent-kit:graph-sync-project implement the agreed product page mapping changes` | `Use $graph-sync-project to implement the agreed product page mapping changes.` |
| Review a YARRRML mapping | `/graph-sync-agent-kit:graph-sync-yarrrml-review review the mapping for Product pages` | `Use $graph-sync-yarrrml-review to review the mapping for Product pages.` |
| Author a postprocessor | `/graph-sync-agent-kit:graph-sync-postprocessor-authoring add a postprocessor that normalizes VideoObject relationships for example.org pages` | `Use $graph-sync-postprocessor-authoring to add a postprocessor that normalizes VideoObject relationships for example.org pages.` |
| Review the GitHub workflow | `/graph-sync-agent-kit:graph-sync-github-workflow-review review the graph-sync GitHub Actions workflow` | `Use $graph-sync-github-workflow-review to review the graph-sync GitHub Actions workflow.` |
| Close out a successful session | `/graph-sync-agent-kit:graph-sync-repo-lifecycle close out this graph-sync project session. The curation changes have been validated. Prepare a safe commit and ask before pushing.` | `Use $graph-sync-repo-lifecycle to close out this graph-sync project session. The curation changes have been validated. Prepare a safe commit and ask before pushing.` |

For the "Start new project" prompt, `graph-sync-curator` should first check whether the current directory is already a graph-sync checkout. In an empty or uninitialized directory, it should coordinate with `graph-sync-repo-lifecycle` to create the project from the WordLift template before starting static entity curation.

## Claude Code Safety

Graph-sync projects often contain local API keys, service-account files, and sync artifacts. In project checkouts that use Claude Code, consider denying reads for local secret paths with `.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./.config/**)",
      "Read(./secrets/**)",
      "Read(./**/*service-account*.json)"
    ]
  }
}
```

Adjust the deny list to the project layout, and keep any machine-local Claude settings out of commits unless the project intentionally shares them.

## Tool Portability

The skills do not assume that `worai`, `uv`, `pipx`, `copier`, `pytest`, `ruff`, or project Python packages are globally installed.

When running tools, prefer:

1. Project-documented commands.
2. Project-local environments.
3. Confirmed local tools.
4. Pinned ephemeral runners such as `pipx run --spec ...` or `uvx --from ...`.
5. Explicit user approval before installing or fetching packages.

## Forward Testing

The `evals/prompts/` directory contains maintainer prompt fixtures for forward-testing skills. Use them as test inputs, not runtime skill references.

## Development

`pyproject.toml` is the source of truth for the agent kit version. After changing `[project].version`, sync plugin manifests with:

```bash
python scripts/sync_versions.py
```

Install development tools and local commit hooks with:

```bash
uv sync --dev
uv run pre-commit install
```

The pre-commit hooks sync `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` from `pyproject.toml`, then run the agent-kit validator.

## CI Validation

Pull requests and pushes to `main` run the agent-kit validation workflow. It checks version consistency across `pyproject.toml` and plugin manifests, required skill metadata, eval prompt fixtures, Claude Code plugin strict validation, and the release archive shape. Release tags must match the `pyproject.toml` version.

## Marketplace Publication

Publishing a release tag creates the GitHub release archive and updates `wordlift/agent-marketplace` so both Codex and Claude Code install the new tag.

The release workflow uses a GitHub App installation token to push the marketplace update. Create a GitHub App installed on `wordlift/agent-marketplace` with repository Contents read/write permission, then configure these values in `graph-sync-agent-kit`:

- Repository variable `AGENT_MARKETPLACE_APP_CLIENT_ID`: the GitHub App client ID.
- Repository secret `AGENT_MARKETPLACE_APP_PRIVATE_KEY`: the full PEM private key for the GitHub App.

The app installation should be restricted to `wordlift/agent-marketplace` unless it needs to publish additional plugins.
