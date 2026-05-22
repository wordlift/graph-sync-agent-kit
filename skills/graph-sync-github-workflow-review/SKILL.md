---
name: graph-sync-github-workflow-review
description: "GitHub Actions review workflow for WordLift graph-sync projects. Use when reviewing or optimizing graph-sync workflow files, reusable workflow inputs, profile dispatch, caching, CI runtime, GitHub Actions cost, reliability, or required quality gates."
---

# Graph Sync GitHub Workflow Review

## Overview

Use this skill to review graph-sync GitHub Actions workflows for reliability, speed, cost, and governance while preserving quality gates.

Use `graph-sync-project` when workflow changes affect runtime project contracts or docs/specs.

## Review Focus

Check:

- Workflow triggers and path filters.
- Profile-based dispatch behavior.
- Reusable workflow inputs.
- `wordlift/graph-sync` action version and pinned `worai_version`.
- Dependency setup and cache configuration.
- Job timeouts and concurrency.
- Artifact upload behavior.
- Secret usage and least privilege permissions.
- CI signal quality and cost impact.

## Process

When reviewing:

- Read the workflow file and relevant project docs.
- Identify reliability risks first.
- Identify unnecessary runtime or compute waste.
- Recommend measurable improvements.
- Avoid weakening required checks unless the user explicitly approves it.
- Keep workflow changes observable through logs, summaries, or artifacts.

## Output

For reviews, lead with findings ordered by severity. Include file/line references when possible, then list open questions and a short summary.
