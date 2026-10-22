# Graph Sync CI Checklist

## Minimum Smoke Coverage
- The project-documented graph-sync CLI smoke command succeeds.
- If no project command is documented, resolve the CLI with `references/cli-resolution.md` before trying `worai`, `uv run worai`, `pipx run --spec worai==<version> worai`, or `uvx --from worai==<version> worai`.
- Profile loads from `worai.toml` under `[profiles.<name>]`.
- Route selection order is validated with representative URLs.
- Relative and absolute mapping paths are both validated.
- `.j2`/`.liquid` mapping template resolution is validated.
- Static templates patch once per run.
- Postprocessors load from the profile's `postprocessors.toml` when it exists, otherwise from `_base`'s, and run in manifest order.

## Suggested Fixture Set
- One small mapping-only profile.
- One profile with templated mapping (`.j2` or `.liquid`).
- One profile with at least one custom postprocessor.
- One failure-path fixture with `keep_temp_on_error = true`.

## CI Assertions
- At least one postprocessor class is loaded and executed.
- Output graph exists after postprocessor run.
- No unexpected callback-level hard failures in smoke scenarios.

## Tests In Generated Repositories
- Tests that assert modeling choices (no `schema:Product` in any mapping, a fixed route order) describe a past decision, not policy. When an agreed modeling fix contradicts such a test, update the test in the same change.
