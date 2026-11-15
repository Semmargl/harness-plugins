# What makes a good handoff

Run this list before outputting the cold-start prompt. Every "no" is something the next
session will have to rediscover, usually by re-reading files you already read.

## Content

- [ ] **TL;DR stands alone.** Someone who reads only the TL;DR knows what the thread is,
      what state it is in, and what is blocking it.
- [ ] **Files table is complete.** Every file created, modified, deleted, or read for a
      reason is listed with a repo-relative path and the function/section when relevant.
- [ ] **Every decision has a reason** and the alternatives that lost. No reason = it will
      be re-debated.
- [ ] **Dead ends are recorded.** "Tried X, it fails because Y" saves the next session
      from repeating the experiment.
- [ ] **Exact values are verbatim:** error messages, commands, versions, numbers,
      config keys, URLs of docs used. No paraphrase like "fixed the config".
- [ ] **State, not story.** No turn-by-turn narrative ("first we..., then you asked...").
- [ ] **Open questions name an owner** (user, teammate, upstream).
- [ ] **Gaps are marked.** If early details were lost to compaction, say so instead of
      guessing.

## Next steps

- [ ] Max 5 items, in order, each with file/command and a time estimate.
- [ ] Item 1 takes under 2 minutes.
- [ ] Only steps actually agreed in the session; no invented roadmap.
- [ ] Deferred and Out-of-scope blocks filled (or the file deleted if work is finished).

## Safety

- [ ] No secrets: API keys, tokens, passwords, cookies, private keys, connection strings,
      `.env` contents. Referenced by name only.
- [ ] No personal data the user did not ask to keep.
- [ ] `--scan` run and clean.
- [ ] User asked once whether `.handoff/` is git-ignored or committed.

## Probe test (answer from the files only)

1. Which files did we touch and what changed?
2. What did we decide on the main contested point, and why?
3. What is the first thing to do next?
4. What did we try and reject?

## Cold-start prompt

- [ ] One code block, nothing before or after it.
- [ ] ~80 words max, paths included.
- [ ] Works in a brand-new chat with no other context.
- [ ] Lists the first 3 actions (if next steps exist).
- [ ] Ends with "verify ... then wait for my go-ahead".

## Common failure modes

| Symptom in the next session | Cause |
|---|---|
| Re-reads half the repo to orient itself | Files table missing or vague |
| Re-proposes an approach you rejected | Dead end not recorded |
| Reverses a decision | Decision recorded without its reason |
| Starts coding immediately | Last line of the prompt removed |
| Edits based on outdated assumptions | RESUME skipped the staleness check |
