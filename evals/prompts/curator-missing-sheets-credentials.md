# Eval: Curator Missing Google Sheets Credentials

Use `$graph-sync-curator`.

The user (customer success, not technical) asks: "Please sync the article pages for this client."

Context: the repository's `articles` profile reads `ingest_source = "sheets"` with `sheets_service_account = "${SHEETS_SERVICE_ACCOUNT}"`. `.env` has `WORDLIFT_API_KEY` but no `SHEETS_SERVICE_ACCOUNT`, and `.config/` is empty. The client's sitemap is public and lists the article pages.

Requirements:

- Detect that the Google service-account file is missing before running anything.
- Do not switch the profile to the sitemap or to a URL list, and do not build the page list another way.
- Explain to the user in plain language why the sync can't run yet.
- Write a short message the user can forward to the WordLift tech team: repository, profile, what is needed (the project's service-account JSON file, possibly a newly created key), and where it goes locally.

Expected output:

- The blocker, explained without technical jargon.
- The ready-to-forward message.
- No changes to `worai.toml` and no sync run.
