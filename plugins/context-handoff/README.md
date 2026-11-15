# context-handoff

Claude Code plugin with one skill, `context-handoff`, that ends a long AI coding session
cleanly and lets you continue it cheaply in a fresh chat.

## What it does

- **CREATE** ("wrap up", "handoff", "save state", "continue in a new chat"): writes a
  compact handoff (state, decisions, files touched, open threads, exact next steps) to
  `.handoff/<timestamp>_<slug>/summary.md` and `next_steps.md`, scans it for
  secret-looking strings, and returns a short cold-start prompt to paste into a new chat.
- **RESUME** ("resume from <path>"): loads a handoff in the new session and checks it
  against the current repository before continuing.

The next session starts from about 1-2k tokens instead of re-paying for a long or
expired context cache.

## Install

```
/plugin marketplace add Semmargl/harness-plugins
/plugin install context-handoff@harness-plugins
```

## Requirements

- Python 3.8+ for the helper script `skills/context-handoff/scripts/new_handoff.py`
  (standard library only).
- Git is optional; if present, the script records a read-only snapshot (branch, last
  commits, changed files).

## Security

- No network access. The script only creates files under `.handoff/` (or the folder you
  pass with `--dir`) in your project and runs read-only `git` commands.
- `--scan` flags secret-looking strings so they don't end up in a handoff.

## License

MIT. See [LICENSE](./LICENSE).
