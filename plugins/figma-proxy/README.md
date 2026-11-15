# figma-proxy

Claude Code plugin that installs [figma-proxy-mcp](https://github.com/Semmargl/figma-proxy-mcp),
a free, open-source (MIT), **read-only** MCP server for Figma to code, plus one short
skill (`figma-proxy-basics`) that tells Claude which tool to use when.

## What you get

| Tool | Purpose |
|---|---|
| `get_figma_component` | Tokenized design IR of a node: `summary:true` for sections and tokens, `format:"flat", lean:true` per section, CSS variables and a Tailwind theme |
| `render_node_png` | PNG of a node (reference image) |
| `verify_render` | Renders your HTML in headless Chromium and diffs it against the Figma PNG (SSIM, pixel diff, diff regions) |
| `export_svg`, `migrate_all_svgs` | Icon export |
| `get_figma_file`, `get_cached_components`, `get_component_by_name`, `list_svg_cache` | File data and cached results |

## Install

```
/plugin marketplace add Semmargl/harness-plugins
/plugin install figma-proxy@harness-plugins
```

When you enable the plugin, Claude Code asks for your **Figma personal access token**
and keeps it in secure storage (it is a `sensitive` user config value, not written to
`settings.json`).

Create the token in Figma: Settings -> Security -> Personal access tokens -> Generate new
token, scope **File content: Read-only**, with an expiry date.

## Requirements

- Node.js 20 or newer (the server runs with `npx -y figma-proxy-mcp@1.1.0 --stdio`).
- For `verify_render` only: `npx playwright install chromium` once.
- Setup check: `FIGMA_API_KEY=<token> npx -y figma-proxy-mcp@1.1.0 --check`.

## Security and network

- Read-only toward Figma. No telemetry.
- `npx` downloads the pinned package `figma-proxy-mcp@1.1.0` from the npm registry on
  first start.
- Hosts the server contacts: `api.figma.com` (token sent in the `X-Figma-Token` header)
  and Figma's image storage for PNG/SVG downloads at short-lived signed URLs (currently
  an `*.s3.*.amazonaws.com` host chosen by Figma; no token sent).
- Local files: a component registry in the OS temp dir, verify_render diff images in
  the OS temp dir, and SVGs only where you ask it to save them.
- Full details: [SECURITY.md](https://github.com/Semmargl/figma-proxy-mcp/blob/main/SECURITY.md).

## License

MIT. See [LICENSE](./LICENSE).

Want the full gated Figma → React workflow with fix loops and fidelity thresholds? See Figma to React, Verified on Agensi: https://www.agensi.io/creators/vladyslav-humeniuk
