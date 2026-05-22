# Validation Loop

Semantic curation changes need runtime and output validation, not only unit tests.

## Validation Order

Use a tiered approach:

1. Project-documented validation command.
2. Tests when present.
3. Lint when configured.
4. Graph-sync CLI smoke checks for generated projects, using the project-documented runner or the `graph-sync-project` CLI resolution policy.
5. Real sync/audit validation for semantic curation changes.

## Curation Validation

For each cluster:

- Run a real sync when credentials and environment allow it.
- Inspect debug TTL/output artifacts.
- Audit schema.org issues.
- Audit Google errors and warnings.
- Fix schema.org issues and Google errors.
- Attempt to fix Google warnings when practical.
- Re-run until the cluster meets the agreed acceptance criteria.

## Acceptance Notes

Record:

- What cluster was validated.
- Which sample URLs were used.
- Which checks passed.
- Remaining warnings and why they remain.
- Any assumptions that should be revisited after more pages are sampled.

## Closeout

After validation passes:

- Summarize semantic changes.
- Summarize validation results.
- Recommend commit/push handoff to `graph-sync-repo-lifecycle`.
- Require explicit user confirmation before any push.
