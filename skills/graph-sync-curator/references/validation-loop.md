# Validation Loop

Semantic curation changes need runtime and output validation, not only unit tests.

## Validation Order

Use a tiered approach:

1. Project-documented validation command.
2. Tests when present.
3. Lint when configured.
4. Graph-sync CLI smoke checks for generated projects, using the project-documented runner or the `graph-sync-project` CLI resolution policy.
5. Selector checks on fetched sample pages (`graph-sync-project` `scripts/fetch_page.py --xpath`).
6. Real sync/audit validation for semantic curation changes.

## Curation Validation

For each cluster:

- Name the target account and get the user's confirmation (`kg_check.py account`); a sync writes to that account's graph at once.
- Run a real sync when credentials and environment allow it: `--debug --output-dir output`, with the operating-system settings in `graph-sync-project` `references/local-runs.md`.
- Read `output/graph_sync_report.md` and `output/graph_sync_failures.csv`; fix failing pages or explain them.
- Inspect debug TTL/output artifacts.
- Check sample pages in the graph (`kg_check.py page`) and look for twins (`kg_check.py twins`).
- Clear the cache (`kg_check.py clear-cache`) so the API link serves the new data.
- Audit schema.org issues.
- Audit Google errors and warnings.
- Fix schema.org issues and Google errors.
- Attempt to fix Google warnings when practical.
- Re-run until the cluster meets the agreed acceptance criteria.
- When a change re-mints IRIs (a type change, a new title source), tell the user the old entities stay in the graph, and list them after the sync; never delete them (`graph-sync-project` `references/kg-checks.md`).

## Acceptance Notes

Record:

- What cluster was validated.
- Which sample URLs were used.
- Which account the sync wrote to.
- Which checks passed.
- Remaining warnings and why they remain.
- Any assumptions that should be revisited after more pages are sampled.

## Closeout

After validation passes:

- Inspect `git status`.
- Summarize semantic changes.
- Summarize validation results.
- If project changes exist, ask whether to prepare a commit handoff to `graph-sync-repo-lifecycle`.
- If no project changes exist, say that there is nothing to commit.
- Require explicit user confirmation before any push.
