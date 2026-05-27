# Eval: Repo Lifecycle Init

Use `$graph-sync-repo-lifecycle`.

Create a new graph-sync project named `graph-sync-example-com` from the WordLift template.

Requirements:

- Use the GitHub template source.
- Use `--defaults` and non-interactive Copier data instead of relying on terminal prompts.
- Provide required template data, including `source_type` and safe WordLift API key handling.
- Use `CHANGE_ME` for `api_key` with validation disabled during generation, then explicitly ask the user to replace it immediately after Copier finishes.
- Include every source-specific required value for the selected `source_type`.
- Initialize git.
- Check for secrets before the first commit.
- Create an initial commit only after reviewing `git status`.

Expected output:

- Commands run or proposed, including required `--data` values for the selected source type.
- Clear post-Copier instruction to replace the `CHANGE_ME` API key before sync, validation, or commit.
- Files checked for secrets.
- Initial commit summary.
- Any setup warnings.
