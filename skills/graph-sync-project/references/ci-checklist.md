# Graph Sync CI Checklist

## Minimum Smoke Coverage
- The project-documented graph-sync CLI smoke command succeeds.
- If no project command is documented, resolve the CLI with `references/cli-resolution.md` before trying `worai`, `uv run worai`, `pipx run --spec worai==<version> worai`, or `uvx --from worai==<version> worai`.
- Profile loads from `worai.toml` under `[profiles.<name>]`.
- Route selection order is validated with representative URLs.
- Relative and absolute mapping paths are both validated.
- `.j2`/`.liquid` mapping template resolution is validated.
- Static templates patch once per run.
- Postprocessors load from `_base` then profile and run in order.

## Suggested Fixture Set
- One small mapping-only profile.
- One profile with templated mapping (`.j2` or `.liquid`).
- One profile with at least one custom postprocessor.
- One failure-path fixture with `keep_temp_on_error = true`.

## CI Assertions
- At least one postprocessor class is loaded and executed.
- Output graph exists after postprocessor run.
- No unexpected callback-level hard failures in smoke scenarios.
