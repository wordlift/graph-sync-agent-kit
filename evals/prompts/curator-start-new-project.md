# Eval: Curator Start New Project

Use `$graph-sync-curator`.

Start the graph-sync workflow for `www.example.org` from an empty directory that is not a git repository and does not contain graph-sync project files.

Requirements:

- Detect that the current directory is not an initialized graph-sync project.
- Do not create static entities, mappings, templates, or curation notes before project initialization.
- Coordinate with `$graph-sync-repo-lifecycle` to create a new project from the WordLift graph-sync template.
- Infer a reasonable project name such as `graph-sync-example-org`.
- Ask only for details that cannot be inferred safely, such as template trust or first-commit preferences.

Expected output:

- Workspace readiness check.
- Repo-lifecycle handoff or initialization plan before curation work.
- No static entity draft as the first action.
