# Example: bad vs good handoff

Scenario: a 3-hour session adding token refresh to a web app's API client.

## Bad

```markdown
## TL;DR
We worked on auth. Fixed some bugs and refactored the client. Almost done.

## Done
- Looked at the auth code
- Discussed options
- Fixed the config
- Tests mostly pass

## Next
- Finish it
```

Why it fails:

- "Fixed the config": which file, which key, what value?
- "Discussed options": which one won, and why? The next session will reopen the debate.
- "Tests mostly pass": which fail, with what error?
- "Finish it": not an action. The next session must re-read everything to find out what
  "it" is.

## Good

```markdown
## Repository state at handoff
- branch: `feat/token-refresh`
- last commits: a1b2c3d add refresh interceptor | 9f8e7d6 extract tokenStore
- changed files at handoff time: `src/api/client.ts`, `src/api/client.test.ts`

## TL;DR
Adding silent access-token refresh to the API client. Interceptor works; 1 of 14 tests
fails (concurrent 401s trigger two refresh calls). Next: add a single-flight lock.
Blocked on nothing.

## Done
- 401 responses now trigger one refresh + retry of the original request.
- Token storage extracted to `src/auth/tokenStore.ts` (memory + sessionStorage).

## Files
| File | Action | Why |
|---|---|---|
| `src/api/client.ts` | modified: `createClient()`, new `onResponseError()` | refresh interceptor |
| `src/auth/tokenStore.ts` | created | single place for token get/set/clear |
| `src/api/client.test.ts` | modified: 4 new tests | refresh + retry coverage |
| `.env.example` | modified: added `AUTH_REFRESH_URL` | new config key |

## Decisions
| Decision | Alternatives | Reason |
|---|---|---|
| Refresh on 401, not on a timer | proactive refresh 60 s before expiry | server clock skew up to 5 min made timers unreliable |
| sessionStorage, not localStorage | localStorage, cookie | user wants logout on tab close; cookie needs backend change |

## Key context
- Refresh endpoint returns 400 (not 401) for an expired refresh token; handled as logout.
- Tried an Axios retry plugin: retries before refresh completes, rejected.
- Credentials for the staging API: in the team password manager, entry "staging api". (Not copied here.)

## Open questions / blockers
- Should a failed refresh redirect to /login or show a modal? Owner: user (product call).
```

```markdown
# Next steps
1. Run `npm test -- client.test.ts` and confirm only "concurrent 401s" fails (1 min).
2. Add a single-flight promise in `onResponseError()` so parallel 401s share one refresh (20 min).
3. Add a test with 3 parallel requests returning 401 (10 min).
4. Ask the user about /login vs modal, then implement (15 min).

## Deferred
- Proactive refresh timer: revisit only if the server fixes clock skew.

## Out of scope
- Backend changes to set httpOnly cookies.
```

Resulting cold-start prompt:

```
Continue from a previous session.
- Summary: .handoff/2026-03-12_1840_token-refresh/summary.md
- Next steps: .handoff/2026-03-12_1840_token-refresh/next_steps.md

Context: adding silent access-token refresh to the API client; one concurrency test fails.
First actions once I confirm:
1. Run the client tests, confirm the single failure
2. Add a single-flight lock in onResponseError()
3. Add a parallel-401 test

Read both files, verify they match the repo, then wait for my go-ahead.
```
