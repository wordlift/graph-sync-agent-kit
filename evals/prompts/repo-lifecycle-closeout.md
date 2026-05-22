# Eval: Repo Lifecycle Closeout

Use `$graph-sync-repo-lifecycle`.

A graph-sync curation session has finished successfully. Prepare the repository for commit and push.

Requirements:

- Inspect git status.
- Summarize changed files.
- Check that `.env` and secrets are not staged.
- Run the project validation command if available.
- If validation passes, propose a commit message.
- Ask for explicit confirmation before pushing.

Expected output:

- Git status summary.
- Validation result.
- Commit message proposal.
- Clear confirmation question before remote push.
