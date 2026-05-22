# Graph Sync Agent Kit

Installable Codex skills and maintainer eval prompts for WordLift graph-sync projects.

This repository contains reusable agent workflows that were extracted from graph-sync project specs and day-to-day implementation practice. The skills are intended to be installed into Codex environments and used across graph-sync project repositories.

## Skill Inventory

- `graph-sync-curator`
  - Day-to-day semantic curation workflow: static entities, sitemap clustering, content-cluster prioritization, schema.org modeling, FAQ/video/authorship extraction, real syncs, and validation loops.
- `graph-sync-project`
  - Technical project workflow: `worai.toml`, mappings, static templates, postprocessor runtime behavior, troubleshooting, CI smoke checks, docs/spec synchronization, and portable CLI resolution.
- `graph-sync-repo-lifecycle`
  - Repository lifecycle workflow: create projects from the template, clone existing projects, initialize git, validate changes, commit, and push after explicit user confirmation.
- `graph-sync-yarrrml-review`
  - Focused YARRRML/RML mapping review for selector correctness, route compatibility, Morph-KGC behavior, duplicate mappings, extraction robustness, and schema.org output quality.
- `graph-sync-postprocessor-authoring`
  - Custom postprocessor authoring and debugging workflow, including manifest behavior, SDK runner usage, context compatibility, and failure artifacts.
- `graph-sync-github-workflow-review`
  - GitHub Actions review workflow for profile dispatch, caching, pinned `worai_version`, reliability, runtime, and cost.

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

Install the needed folders under `skills/` with your Codex skill installation flow.

Recommended MVP install set:

```text
skills/graph-sync-curator
skills/graph-sync-project
skills/graph-sync-repo-lifecycle
```

Add focused review/authoring skills as needed:

```text
skills/graph-sync-yarrrml-review
skills/graph-sync-postprocessor-authoring
skills/graph-sync-github-workflow-review
```

## Usage

The prompts below are intentionally concrete. Replace `example.org`, repository URLs, profiles, and cluster names with the project you are working on.

### Main curation workflow

```text
Use $graph-sync-curator to start the graph-sync curation workflow for www.example.org.
```

### Start a new project

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

## Validation

Validate each skill folder with the skill validator:

```bash
quick_validate.py skills/<skill-name>
```

The current scaffold has been validated for all six skill folders.

## Forward Testing

Use the prompt fixtures under `evals/prompts/` to test realistic workflows:

- `curator-static-entities.md`
- `curator-sitemap-clusters.md`
- `curator-content-cluster.md`
- `repo-lifecycle-init.md`
- `repo-lifecycle-closeout.md`
- `yarrrml-review.md`
- `postprocessor-authoring.md`
- `github-workflow-review.md`

Treat eval prompts as maintainer test inputs, not runtime skill references.
