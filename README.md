# harness-plugins

A Claude Code plugin marketplace with two free, MIT-licensed plugins by Vladyslav Humeniuk.

| Plugin | What it is |
|---|---|
| [`figma-proxy`](./plugins/figma-proxy) | Installs the read-only Figma MCP server [figma-proxy-mcp](https://github.com/Semmargl/figma-proxy-mcp) (tokenized design IR, Tailwind theme, PNG/SVG export, `verify_render` visual diff) plus a basics skill |
| [`context-handoff`](./plugins/context-handoff) | Skill that ends a long session with a compact handoff and resumes it in a fresh chat from about 1-2k tokens |

## Install

```
/plugin marketplace add Semmargl/harness-plugins
/plugin install figma-proxy@harness-plugins
/plugin install context-handoff@harness-plugins
```

From a shell: `claude plugin marketplace add Semmargl/harness-plugins`, then
`claude plugin install figma-proxy@harness-plugins`.

## Requirements

- Claude Code with plugin support.
- `figma-proxy`: Node.js 20+, a Figma personal access token (scope **File content:
  Read-only**; the plugin asks for it on enable and stores it in secure storage), and
  for `verify_render` only, `npx playwright install chromium` once.
- `context-handoff`: Python 3.8+ (standard library only).

## Security notes

- **figma-proxy**: runs `npx -y figma-proxy-mcp@1.1.0 --stdio` (pinned version,
  downloaded from the npm registry). The MCP server contacts only `api.figma.com` and
  Figma's image CDN (signed URLs for PNG/SVG downloads, no token sent). Read-only toward
  Figma, no telemetry. Details in the server's
  [SECURITY.md](https://github.com/Semmargl/figma-proxy-mcp/blob/main/SECURITY.md).
- **context-handoff**: no network access. It writes handoff files inside your project
  and runs read-only `git` commands.
- No credentials are stored in this repository.

## Links

- More skills: [Agensi profile](https://www.agensi.io/creators/vladyslav-humeniuk)
- [ai-upgrade.online](https://ai-upgrade.online): AI-adoption audits for dev teams

Want the full gated Figma → React workflow with fix loops and fidelity thresholds? See Figma to React, Verified on Agensi: https://www.agensi.io/creators/vladyslav-humeniuk

## License

MIT. See [LICENSE](./LICENSE).
