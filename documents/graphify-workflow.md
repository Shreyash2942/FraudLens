# Graphify Workflow

This file isolates the project-level Graphify workflow so it can be cherry-picked into multiple branches and reverted later if needed.

## Daily Commands

Run from repo root:

```powershell
py -m graphify update .
```

Useful exploration commands:

```powershell
py -m graphify query "How does X connect to Y?"
py -m graphify path "Node A" "Node B"
py -m graphify explain "Node Name"
```

## Branch Strategy

For branches that need graph memory:

1. Cherry-pick the Graphify setup commit(s).
2. Run `py -m graphify update .` after code changes.
3. Revert the Graphify commit(s) when no longer needed.

## Notes

- Use the CLI subcommand format (`py -m graphify update .`).
- Do not use `py -m graphify . --update` (invalid in this installation).
- Project-local `.codex/hooks.json` is intentionally not required for this workflow.
