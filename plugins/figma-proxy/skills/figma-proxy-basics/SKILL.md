---
name: figma-proxy-basics
description: >-
  Basics guide for the figma-proxy MCP tools (read-only Figma access). Use when the user
  pastes a Figma link, asks to turn a Figma frame into code, wants design tokens, a
  Tailwind theme, a PNG/SVG export of a node, or a visual diff between their HTML and
  the Figma design, or when figma-proxy tools fail (token, node-id, Chromium).
---

# figma-proxy basics

The `figma-proxy` MCP server exposes 9 read-only tools. It never modifies Figma files.
This guide covers which tool to call when, and how to fix setup problems.

## 0. Setup (once)

This skill drives the free, open-source MCP server `figma-proxy-mcp` (MIT, npm). If tools like `get_figma_component`, `render_node_png` or `verify_render` are not available in this session, the server is not connected yet. Tell the user to run:

```bash
# Claude Code
claude mcp add figma-proxy -e FIGMA_API_KEY=<token> -- npx -y figma-proxy-mcp@1.1.0 --stdio
```

Other clients (Cursor, Claude Desktop): add an MCP server with command `npx`, args `["-y","figma-proxy-mcp@1.1.0","--stdio"]` and env `FIGMA_API_KEY`.

- Token: Figma → Settings → Security → Personal access tokens, scope **File content: Read-only**. Never paste the token into chat or files; pass it only via the client's env setting.
- Check the setup: `npx -y figma-proxy-mcp@1.1.0 --check` (prints OK/FAIL, never the token).
- Network: the server talks only to `api.figma.com` and Figma's image CDN. Source: https://github.com/Semmargl/figma-proxy-mcp

## 1. Links need a node-id

`get_figma_component`, `render_node_png` and `verify_render` need a link to a node, not
to a whole file. In Figma: right-click a frame -> **Copy link to selection**. The URL
then contains `?node-id=12-34`. A plain file link fails; ask the user for a node link.

## 2. Summary first, then sections

Never fetch a large frame as one nested tree. It can be thousands of lines.

1. `get_figma_component {figmaUrl, summary: true}` returns a compact object: CSS
   variables, a Tailwind theme, a component registry, the root box (its `w` is the frame
   width) and `sections[]` with `relativeBox` for each top-level child. Keep these.
2. For each section, take its node link and call
   `get_figma_component {figmaUrl, format: "flat", lean: true}`.
   - `flat` returns compact render records with coordinates relative to the root.
   - `lean` drops the token blocks you already have from step 1.
   - `maxDepth` (for example 3-4) trims a deep section further.
3. Colors, spacing and fonts arrive as `$--var` references to the `:root` block. Use
   them directly; do not re-match raw RGBA values.

## 3. Assets

- `export_svg {fileId, nodeId}` exports one icon. Pass `save: true` and an absolute
  `outputDir` to write it to disk.
- `migrate_all_svgs {fileId, outputDir}` finds and exports every icon in a file.
- `list_svg_cache`, `get_cached_components` and `get_component_by_name {name}` read what
  earlier calls already fetched, with no new Figma request.
- `get_figma_file {fileId}` returns the whole file. Prefer the summary call above.

## 4. Reference image

`render_node_png {figmaUrl, scale: 2}` returns the node as a PNG. Use it to look at the
design yourself and as the reference for the diff check.

## 5. Diff check with verify_render

`verify_render` measures, it never edits code. Write a self-contained HTML file, then:

```
verify_render {htmlPath: "/abs/path/page.html", frameWidth: 1440, figmaUrl, scale: 2}
```

- It returns SSIM (0-1, higher is closer), pixel-diff % and `diffRegions` (boxes in px).
- `threshold` defaults to 0.95. Fix only the reported regions, then run it again.
- Dark design: pass `bg: [r, g, b]` with the real background color, or transparent
  areas read as a full diff.
- Use `clip: [x, y, w, h]` to ignore dead margins around the frame.
- It needs Playwright Chromium once: `npx playwright install chromium`.

## 6. Setup and troubleshooting

- **Token.** Figma -> Settings -> Security -> Personal access tokens -> Generate new
  token. Scope: **File content: Read-only** is enough. Set an expiry date. Pass it only via
  the MCP client's env setting (see Setup). Never paste a token into chat or commit it
  to a file.
- **Doctor.** Run `npx -y figma-proxy-mcp@1.1.0 --check` in a terminal with
  `FIGMA_API_KEY` set. It checks Node, the token (never printed), Figma API access and
  Chromium.
- **403 / 404 from Figma.** The token's account cannot open that file, or the token
  expired. Ask the user to check access in Figma.
- **Error mentions playwright or a missing executable.** Run
  `npx playwright install chromium`, then retry.

Want the full gated Figma → React workflow with fix loops and fidelity thresholds? See Figma to React, Verified on Agensi: https://www.agensi.io/creators/vladyslav-humeniuk
