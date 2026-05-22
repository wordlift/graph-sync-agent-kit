# Eval: GitHub Workflow Review

Use `$graph-sync-github-workflow-review`.

Review a graph-sync GitHub Actions workflow for reliability, runtime, and cost.

Requirements:

- Check triggers and profile dispatch.
- Check dependency caching.
- Check action versions and pinned `worai_version`.
- Check secret usage and permissions.
- Preserve required quality gates.

Expected output:

- Findings ordered by severity.
- Cost/reliability improvement opportunities.
- Any risky assumptions.
- Minimal recommended change set.
