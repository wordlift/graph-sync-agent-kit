# Graph Sync Agent Kit

Installable Codex skills and maintainer eval prompts for WordLift graph-sync projects.

This repository contains reusable agent workflows that were extracted from graph-sync project specs and day-to-day implementation practice. The skills are intended to be installed into Codex environments and used across graph-sync project repositories.

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
skills/
  graph-sync-curator/
  graph-sync-project/
  graph-sync-repo-lifecycle/
  graph-sync-yarrrml-review/
  graph-sync-postprocessor-authoring/
  graph-sync-github-workflow-review/

evals/
  prompts/
```

The `skills/` folders are the installable runtime units. The `evals/prompts/` files are maintainer fixtures for forward-testing skills and should not be installed as skills.

## Installation

Install skills from:

```text
git@github.com:wordlift/graph-sync-agent-kit.git
```

### Codex-Assisted Install

Ask Codex to install every skill in this repository:

```text
Use $skill-installer to install all skills under skills/ from wordlift/graph-sync-agent-kit.
```

Install all skills in this kit. They are designed to work together: `graph-sync-curator` orchestrates the workflow, while the other skills provide project, lifecycle, mapping, postprocessor, and GitHub workflow support.

Restart Codex after installing skills.

### Manual Install

Clone the repository and copy all skill folders into Codex's skills directory:

```bash
git clone git@github.com:wordlift/graph-sync-agent-kit.git
cd graph-sync-agent-kit
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/graph-sync-* "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Restart Codex after copying skills.

## Usage

The prompts below are intentionally concrete. Replace `example.org`, repository URLs, profiles, and cluster names with the project you are working on.

### Start new project

```text
Use $graph-sync-curator to start the graph-sync workflow for www.example.org.
```

### Continue an existing project

```text
Use $graph-sync-curator to continue the graph-sync workflow for this existing project.
```

```text
Use $graph-sync-curator to continue the graph-sync workflow for git@github.com:wordlift/graph-sync-example-org.git.
```

### Create project repository

```text
Use $graph-sync-repo-lifecycle to create a new graph-sync project for example.org from the WordLift graph-sync template.

Use the project name graph-sync-example-org and prepare it for the first working session.
```

### Clone and prepare an existing project

```text
Use $graph-sync-repo-lifecycle to clone git@github.com:wordlift/graph-sync-example-org.git and prepare the checkout for work.
```

### Create static entities

```text
Use $graph-sync-curator to create the static entities for example.org and propose the graph-sync project files that should represent them.
```

### Parse a sitemap and prioritize clusters

```text
Use $graph-sync-curator to parse the sitemap for example.org and recommend the next content cluster to implement.
```

### Work on a content cluster

```text
Use $graph-sync-curator to work on the product pages cluster for example.org and propose the graph-sync changes needed for that cluster.
```

### Update project files safely

```text
Use $graph-sync-project to implement the agreed product page mapping changes in this graph-sync project.
```

### Review a YARRRML mapping

```text
Use $graph-sync-yarrrml-review to review the mapping for Product pages.
```

### Author a postprocessor

```text
Use $graph-sync-postprocessor-authoring to add a postprocessor that normalizes VideoObject relationships for example.org pages.
```

### Review the GitHub workflow

```text
Use $graph-sync-github-workflow-review to review the graph-sync GitHub Actions workflow.
```

### Close out a successful session

```text
Use $graph-sync-repo-lifecycle to close out this graph-sync project session.

The curation changes have been validated. Prepare a safe commit and ask before pushing.
```

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
