# Privacy Policy — harness-plugins

_Last updated: 2026-11-16_

These plugins run entirely on your own machine inside your AI agent. The author does not operate any service for them and does not collect, receive, store, sell or share any data.

## figma-proxy
- Starts the open-source MCP server [`figma-proxy-mcp`](https://github.com/Semmargl/figma-proxy-mcp) locally (stdio).
- Your Figma personal access token is stored by your agent as a sensitive plugin setting and is sent only to Figma (`api.figma.com` and Figma's image CDN) to read the files you point it at. Use a read-only token.
- Cached components, SVGs and render/diff images are written to your OS temp folder (configurable). Nothing is sent anywhere else. No telemetry.

## handoff-resume (Context Handoff & Resume)
- No network access. Writes handoff files only to `.handoff/` in your project (configurable).
- The skill instructs the agent to redact secrets before writing, and ships a local secret scan.

## Contact
Questions: open an issue at https://github.com/Semmargl/harness-plugins/issues
