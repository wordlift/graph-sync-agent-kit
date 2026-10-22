# Graph Sync Agent Kit

Installable agent skills and maintainer eval prompts for WordLift graph-sync projects.

This repository contains reusable agent workflows that were extracted from graph-sync project specs and day-to-day implementation practice. The same `skills/` directory is packaged as a Claude Code plugin, a Codex plugin and a Gemini CLI extension, or can be copied into any agent's skills folder.

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

gemini-extension.json

scripts/
  sync_versions.py
  validate_agent_kit.py

skills/
  graph-sync-curator/
  graph-sync-project/          # includes scripts/fetch_page.py and scripts/kg_check.py
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

### Gemini CLI Extension

Gemini CLI installs the kit as an extension straight from this repository (from the archive of its latest release):

```bash
gemini extensions install https://github.com/wordlift/graph-sync-agent-kit
```

Update after a new release:

```bash
gemini extensions update graph-sync-agent-kit
```

Restart Gemini CLI after installing or updating. The same commands work in wordlift-cli, which is built on Gemini CLI, with `wordlift-cli` in place of `gemini`.

### Codex Skill Install

Ask Codex to install every skill in this repository:

```text
Use $skill-installer to install all skills under skills/ from wordlift/graph-sync-agent-kit.
```

Install all skills in this kit. They are designed to work together: `graph-sync-curator` orchestrates the workflow, while the other skills provide project, lifecycle, mapping, postprocessor, and GitHub workflow support.

Restart Codex after installing skills.

### Manual Install (Claude Code, Codex, Gemini CLI)

Every agent reads skills from a folder in your home directory. Copy all six `graph-sync-*` folders there, side by side (the skills refer to each other's files):

| Agent | macOS / Linux | Windows |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `%USERPROFILE%\.claude\skills\` |
| Codex | `~/.codex/skills/` (or `$CODEX_HOME/skills/`) | `%USERPROFILE%\.codex\skills\` |
| Gemini CLI | `~/.gemini/skills/` | `%USERPROFILE%\.gemini\skills\` |

macOS / Linux (example for Codex; change the folder for another agent):

```bash
git clone https://github.com/wordlift/graph-sync-agent-kit.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R graph-sync-agent-kit/skills/graph-sync-* "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Windows PowerShell (example for Gemini CLI; change `.gemini` to `.claude` or `.codex` for another agent):

```powershell
git clone https://github.com/wordlift/graph-sync-agent-kit.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\.gemini\skills" | Out-Null
Copy-Item -Recurse -Force graph-sync-agent-kit\skills\graph-sync-* "$env:USERPROFILE\.gemini\skills\"
```

Restart the agent after copying. To update later, run `git pull` in `graph-sync-agent-kit` and copy again.

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

With a manual install, skills are invoked by name in plain language in every agent: `Use the graph-sync-curator skill to …`.

More scenarios, same pattern:

- `Use the graph-sync-curator skill to get this project ready on my computer and tell me what it covers.`
- `Use the graph-sync-curator skill to run the sync for the products profile.`
- `Use the graph-sync-project skill to check what the knowledge graph holds for https://www.example.org/some-page.`
- `Use the graph-sync-project skill to find the cheapest crawler mode for https://www.example.org/some-page.`

For the "Start new project" prompt, `graph-sync-curator` should first check whether the current directory is already a graph-sync checkout. In an empty or uninitialized directory, it should coordinate with `graph-sync-repo-lifecycle` to create the project from the WordLift template before starting static entity curation.

For "Continue current checkout", "Continue remote repository", and "Clone and prepare an existing project", the lifecycle flow should also check local API-key readiness before any graph-sync command or real sync. It should look for a project-root `.env` without printing secret values, reuse or copy an existing local `.env` only with user approval, and otherwise ask the user to provide the WordLift API key through a local-only path such as editing `.env` or exporting an environment variable.

## Quick Start For Customer Success

For WordLift team members who work on client graph-sync projects without a developer background. The agent does the technical work; you describe what the client needs and check the results.

### Once Per Computer

1. Install **Git** (<https://git-scm.com/downloads>).
2. Install **uv**, which brings the right Python by itself:
   - Windows PowerShell: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. Install your AI agent (Claude Code, Codex or Gemini CLI) and the skills (Manual Install above). WordLift team members also install the `wordlift-kg` skill from WordLift's internal skills repository, the same way: it checks the knowledge graph a sync writes to.

### Work On A Client Project

1. Get access to the project's GitHub repository, then clone it: `git clone https://github.com/wordlift/graph-sync-<client>.git`.
2. Open a terminal in that folder and start your agent there.
3. Ask: `Use the graph-sync-curator skill to get this project ready on my computer and tell me what it covers.` The agent installs what the project needs and creates the `.env` file; it asks you to paste the client's WordLift API key **into that file**, never into the chat.
4. Ask for what you need in plain words: which pages, what they should show, what looks wrong.

### Before Every Sync

- **A sync writes straight into the knowledge graph of the account whose key is in `.env`**, usually the client's live graph. There is no dry run. The agent names the account before every sync and waits for your yes.
- To experiment safely, create a temporary account in the WordLift management console, set its **Website URL to the site you are syncing**, and give the agent that account's key instead.
- Use only the graph-sync project to write to a graph-sync account. Other tools that write entities create them under different identifiers, so the same page ends up with duplicates.

### What Only The Tech Team Can Do

The agent stops and writes you a message to forward when a task needs:

- **A Google Sheets service-account file.** Projects that read their pages from a Google Sheet need their own credentials file, which is never in the repository. Google shows a key only once, so the tech team may have to create a new one.
- GitHub repository secrets, or scheduling a new profile in the graph-sync orchestrator.
- A fix inside `worai` or the WordLift SDK.

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
