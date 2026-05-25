# Eval: GitHub Workflow Review

Use `$graph-sync-github-workflow-review`.

Review the following GitHub Actions workflow for `graph-sync-morganstanley-com`:

```yaml
name: Graph Sync

on:
  workflow_dispatch:
    inputs:
      profile:
        description: "Profile to run"
        required: true
        default: articles

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install worai
        run: pip install worai

      - name: Run graph sync
        run: worai --config worai.toml graph sync run --profile ${{ github.event.inputs.profile }}
        env:
          WORDLIFT_KEY: ${{ secrets.WORDLIFT_KEY }}
```

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
