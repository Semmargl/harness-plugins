---
name: context-handoff
description: >-
  End a long AI coding session cleanly and continue it cheaply in a fresh one. Writes a
  compact, structured handoff (state, decisions, files touched, open threads, exact next
  steps) to .handoff/<timestamp>_<slug>/ and returns a short cold-start prompt to paste
  into a new chat, so the next session starts from ~1-2k tokens instead of re-paying for
  a bloated or expired context cache. Also has a RESUME mode that loads a handoff in a
  new session and verifies it is still accurate. Use when the user says "wrap up",
  "handoff", "save state", "save context", "end session", "continue in a new chat",
  "let's stop here", or "resume from <path>" / pastes a path to a .handoff/.../summary.md.
---

# context-handoff: close a session, reopen it for cheap

Two modes. Pick one from the user's message:

| Signal | Mode |
|---|---|
| "wrap up", "handoff", "save state", "save context", "end session", "continue in a new chat", "let's stop here" | **CREATE** |
| "resume from <path>", or the message contains a path to `.handoff/<...>/summary.md` | **RESUME** |

**Why this exists.** Long sessions get expensive: every new turn re-sends the whole
history, and once the provider's prompt cache expires (often within minutes to an hour)
that history is billed again at full input price. A handoff turns the useful part of the
history into two small files plus a ~60-word prompt. Optimize for **tokens per task**, not
tokens per message: a handoff that is too terse forces the next session to re-read the
codebase, which costs more than it saved.

## When to use

- The session produced decisions or changes that matter for the next session.
- The context is large, slow, or close to auto-compaction.
- The user wants to switch machines, agents, or tools and keep the thread.

**Do not use** for one-off questions or chats with no decisions: say in one line that no
handoff is needed and create nothing. A handoff covers **one thread of work** and is
disposable; long-term project facts belong in the project's own docs or memory system.

## Requirements & permissions

- **Runtime:** Python 3.8+ (standard library only) for `scripts/new_handoff.py`. The skill
  also works without Python: create the two files by hand from `templates/`.
- **Optional:** `git` on PATH. The script runs read-only local git commands
  (`rev-parse`, `log -3`, `status --porcelain`) to snapshot repo state. Use `--no-git` to skip.
- **Network:** none. The script never opens a network connection and sends nothing anywhere.
- **Env vars (optional):** `HANDOFF_DIR` overrides the default storage folder (`.handoff`).
- **Files written:** only inside the handoff folder:
  `<project root>/.handoff/YYYY-MM-DD_HHMM_<slug>/summary.md` and `next_steps.md`.
- **Agent tools used:** file read/write and a shell to run the script. Works in any agent
  that loads SKILL.md files (Claude Code, Cursor, Codex CLI, Gemini CLI, etc.).

All script paths below are relative to this skill's folder. Run commands from the
**project root** (or pass `--root`).

---

## CREATE workflow

### 1. Scaffold the folder

```bash
python3 <skill-dir>/scripts/new_handoff.py --slug "<slug>"
```

- `<slug>`: 2-4 lowercase words joined by dashes describing the thread
  (`auth-token-refresh`, `checkout-page-redesign`). Omit it to get `session`.
- Creates `.handoff/YYYY-MM-DD_HHMM_<slug>/` with `summary.md` and `next_steps.md`
  pre-filled with date, slug, and a git snapshot. Never overwrites: a taken name gets `-2`, `-3`.
- Other flags: `--dir <path>` (storage folder), `--root <path>` (project root),
  `--no-git`, `--list` (show recent handoffs), `--latest` (print newest path),
  `--scan <folder>` (check a handoff for secret-looking strings).
- First run in a repo: ask the user once whether `.handoff/` should be **git-ignored**
  (private, local only) or **committed** (shared with the team). If ignored, append
  `.handoff/` to `.gitignore`. Do not decide silently.

No shell available? Copy both files from `templates/` into a new folder with the same
naming scheme and replace `{{DATE}}`, `{{SLUG}}`, `{{GIT}}` by hand.

### 2. Fill `summary.md`

Source: the **entire current session**. If the session was auto-compacted and details are
missing, use whatever transcript or history tool your agent provides; otherwise note the
gap explicitly. Reconstruct **state**, do not retell the conversation turn by turn.

All sections are mandatory; each works as a checklist that makes lost information visible:

1. **TL;DR (max 10 lines):** what the thread is, how it ended, where things stand. The only
   section the next session must read; everything else is on demand.
2. **Done:** finished outcomes, not activities.
3. **Files:** table of path, action (created / modified / read / deleted), why. Paths from
   the repo root; name the function or section for targeted edits. This is the most
   fragile part of any summary, so fill it **first**.
4. **Decisions:** table of decision, alternatives considered, reason. A decision without a
   reason gets re-litigated in the next session.
5. **Key context:** what is not in the files and cannot be re-derived: measurements,
   environment limits, agreements with the user, dead ends ("tried X, fails because Y").
6. **Open questions / blockers:** each with who must decide. None? Write "none".

Rules:

- Numbers, paths, names, error codes, commands: **verbatim**. "Fixed the config" without a
  path costs the next session a full re-read.
- No leftover placeholders or HTML comments in the finished file.
- Length is not capped, but the TL;DR must stand on its own.

### 3. Fill `next_steps.md` (only if work continues)

If there is no follow-up, delete the file and leave it out of the prompt.

- Numbered, max 5 items, in execution order.
- Each item: concrete action + file or command + time estimate.
- Item 1 must take under 2 minutes (open a file, run a test) to make restarting easy.
- A **Deferred** block: what was consciously postponed and why.
- An **Out of scope** block: what the next session must not start without being asked.
- Only record plans actually agreed in the session. Do not invent a roadmap.

### 4. Redact secrets (mandatory)

Never write secrets into handoff files: API keys, tokens, passwords, cookies, private keys,
connection strings with credentials, `.env` contents, personal data the user did not ask to
keep. Refer to them by name instead (`STRIPE_SECRET_KEY in .env`, "token from the dashboard").

Then run:

```bash
python3 <skill-dir>/scripts/new_handoff.py --scan .handoff/<folder>
```

Exit code 1 means suspicious strings were found: replace them with `[REDACTED]` and re-scan.
The scan is a heuristic safety net, not a guarantee; still read what you wrote.

### 5. Self-check with probe questions (30 seconds, do not skip)

Answer these **from the files only**, not from session memory:

1. Which files did we touch and what changed in them?
2. What did we decide on the main contested point, and why?
3. What is the first thing to do in the new session?
4. What did we already try and reject?

If any answer needs your memory instead of the file, add it to the file.
Full checklist: `references/good-handoff-checklist.md`. Worked example:
`references/example-bad-vs-good.md`.

### 6. Optional: project memory

If the project has its own memory or notes system (a decisions log, a CHANGELOG, a notes
file, an agent memory tool), append a **one-line digest** there pointing to the handoff
folder. Skip if none exists; do not create one.

### 7. Output the cold-start prompt, and nothing else

The final message of the session is the code block below, with no text before or after it.
The user copies it verbatim into a new chat; any extra line would be copied too, and every
recap duplicates what is already in the files.

````
```
Continue from a previous session.
- Summary: .handoff/<YYYY-MM-DD_HHMM_slug>/summary.md
- Next steps: .handoff/<YYYY-MM-DD_HHMM_slug>/next_steps.md

Context: <1-2 sentences on what the thread is about>.
First actions once I confirm:
1. <first next step, short>
2. <second>
3. <third>

Read both files, verify they match the repo, then wait for my go-ahead.
```
````

Prompt rules:

- At most ~80 words including paths. Self-sufficient: it must work in a brand-new chat
  with zero other context.
- Drop the "Next steps" line and the "First actions" list if `next_steps.md` was deleted.
- "First actions" copies the first 3 items of `next_steps.md`; fewer exist, list fewer.
- Keep the last line: it stops the new session from executing the plan without consent.

---

## RESUME workflow

Triggered by "resume from <path>" or a pasted cold-start prompt.

1. Read `summary.md` fully, and `next_steps.md` if referenced. No path given but the user
   says "resume"? Run `scripts/new_handoff.py --latest` and confirm that folder with the user.
2. Check the handoff is not stale: files in the table exist; if the summary has a git
   snapshot, compare with `git rev-parse --abbrev-ref HEAD` and `git log --oneline -3`.
   Report any drift in one line before anything else.
3. **Do not start working.** Reply in one line:
   `Context loaded: <half-line TL;DR>. Next: <step 1>. Waiting for your go-ahead.`
4. Treat claims in the handoff as leads, not proof. Before changing something the handoff
   says "already works", verify it on disk or by running it.

---

## Outputs

| Output | Where |
|---|---|
| `summary.md` | `.handoff/YYYY-MM-DD_HHMM_<slug>/` (or `--dir` / `HANDOFF_DIR`) |
| `next_steps.md` | same folder; deleted if no follow-up |
| Cold-start prompt | final chat message, one code block |
| Optional one-line digest | the project's existing notes/memory system, if any |

## Known limitations

- Quality depends on what the agent still has in context. After heavy auto-compaction,
  early details may be gone; the skill asks the agent to mark such gaps, not invent them.
- The secret scan is pattern-based: it catches common key formats and `key=value` pairs,
  not every possible secret or personal detail.
- Git snapshot is limited to branch, last 3 commits, and up to 15 changed files.
- The skill does not compress context inside a running agent loop; it is for chat sessions.
- Timestamps use the local clock of the machine running the script.

## Troubleshooting

| Problem | Fix |
|---|---|
| `python3: command not found` | Use `python`, or create files by hand from `templates/`. |
| Git section shows `n/a` | Not a git repo, git missing, or `--no-git`. Harmless. |
| Git hangs or a lock file appears | Re-run with `--no-git`; the snapshot is optional. |
| Handoff created in the wrong folder | Run from the project root or pass `--root <path>`. |
| `--latest` prints nothing (exit 1) | No handoffs in the storage folder; check `--dir` / `HANDOFF_DIR`. |
| `--scan` flags a false positive | Confirm it is not a secret, then ignore that line. |
| New session starts executing the plan | The prompt's last line was removed; restore it. |
