---
name: kimi-webbridge
description: |
  Kimi WebBridge lets AI control the user's real browser — navigate, click, type, read, screenshot, and interact with any website using the user's actual login sessions. Use this skill whenever the user wants to interact with websites, automate browser tasks, scrape web content, or perform any action requiring a real browser. Also use when the user mentions "browser", "webpage", "open URL", "screenshot", or asks to read/interact with any website. Use even for simple-sounding browser requests — the daemon handles all complexity.
---

# Kimi WebBridge

Control the user's real browser (with their login sessions) via a local daemon at `http://127.0.0.1:10086`.

## Health check (always do this first)

```bash
~/.kimi-webbridge/bin/kimi-webbridge status
```

Then act on the result:

- **`running: true` and `extension_connected: true`** — healthy. Proceed with the tool calls below.
- **Anything else** (command not found, `running: false`, `extension_connected: false`, errors) — **Read `references/operations.md`** in this skill directory. It has the install / start / diagnose routing table.

Don't guess fixes here — every non-healthy state is handled in `references/operations.md`.


📂 **Tools** → see [`references/tools-reference.md`](references/tools-reference.md) (loaded on demand)

## Sessions

Each session maps to a separate browser tab group. Use different session names for different sites to keep operations isolated.

Add `"session":"name"` to the request body:

```bash
curl -s -X POST http://127.0.0.1:10086/command \
  -d '{"action":"navigate","args":{"url":"https://example.com","newTab":true},"session":"my-task"}'
```

Always assign distinct session names when working with multiple sites in parallel.

## Screenshots: Use the Helper Script

**Never call the screenshot API directly** — it returns base64-encoded image data (hundreds of KB of text) that will flood the context window.

Use `scripts/screenshot.sh` instead. It decodes and saves the image to disk, returning only the file path:

```bash
# Default — saves to /tmp/kimi-webbridge-screenshots/{timestamp}.png
bash "$(dirname "$SKILL_PATH")/scripts/screenshot.sh"

# With a session
bash "$(dirname "$SKILL_PATH")/scripts/screenshot.sh" -s my-task

# Custom output path
bash "$(dirname "$SKILL_PATH")/scripts/screenshot.sh" -o /tmp/page.png

# JPEG format, quality 60
bash "$(dirname "$SKILL_PATH")/scripts/screenshot.sh" -f jpeg -q 60
```

After getting the file path, use the Read tool to view the image.

If `$SKILL_PATH` is unavailable, call the script by its absolute path.

## Prefer snapshot over CSS/JS selectors

`snapshot` returns interactive elements with `@e` refs based on semantic role/name. Use them directly with click/fill — they survive CSS class hash changes that break manually-written selectors.

Fall back to `evaluate` (JS) only when:
- The target has no `@e` ref in the snapshot
- You need attributes not in the snapshot (e.g., `href`)
- You need to dispatch complex event sequences, or scroll

## Evaluate Tips

- Always use compact `JSON.stringify(data)` — never add `null, 2` formatting. Indentation and newlines can inflate the response several times over, causing truncation during transmission.
- `evaluate` calls share the page's JS realm — re-declaring the same `const`/`let` across two calls throws `SyntaxError`. Wrap in an IIFE for a fresh scope: `(() => { const x = ...; return x; })()`.

## Text input — use `fill`

`fill` handles all three text input shapes. Pass selector (CSS or `@e` ref) + value:

| Target | What `fill` does | Returned `mode` |
|--------|------|------|
| `<input>` / `<textarea>` | Sets `.value` via native setter, fires `input`/`change`. | `"value"` |
| `[contenteditable]` (ProseMirror / TipTap / Lexical / Slate / Quill etc.) | Focuses, selects all existing content, calls `document.execCommand('insertText', ...)` which fires `beforeinput`/`input` with `inputType:'insertText'` and `data:value`. | `"contenteditable"` |
| Other element | Best-effort `.value` + events. | `"value"` |

`fill` is **clear-and-insert**: existing content is replaced. For "append to existing text", read the current value via `evaluate`, concatenate, then `fill` with the result.

## Form submit / special keys

There's no separate "press Enter" tool. To submit a form, click the submit button directly (`click` on the @e ref or selector). To dispatch a key event programmatically (e.g. Escape to close a modal):

```bash
{"action":"evaluate","args":{"code":"document.activeElement.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"}}
```

## Save the current page as PDF

`save_as_pdf` renders the current page to PDF, writes it to `/tmp/kimi-webbridge-pdfs/`, and returns the file path (the daemon strips the base64 — agent never sees raw PDF bytes).

All args optional:
- `paper_format`: `letter` (default) \| `a4` \| `legal` \| `a3` \| `tabloid`
- `landscape`: `false` (default)
- `scale`: `1.0` (default), range `[0.1, 2.0]`
- `print_background`: `true` (default) — keep background colors
- `file_name`: caller-supplied name; if absent, derived from page title

Decoded PDF cap is 100 MB. Above that the daemon refuses; reduce `scale` or split the page.

## Known limitations

- **Sites that strictly check `event.isTrusted`** (some banking portals, captcha challenges) reject `fill` and `click` because both go through DOM-level synthetic events (`isTrusted=false`). This is a product boundary, not a bug — no automation primitive that runs on the user's machine without stealing OS focus can produce trusted events on these sites.
- **Cross-origin iframes**: `fill`, `click`, `evaluate`, and `snapshot` operate on the top frame. If a target element lives in a same-page iframe from a different origin (e.g. embedded sandbox demos), navigate to the iframe's URL directly instead.

## Versions

Daemon, extension, and this skill share a 1:1 version string. Read both via:

```bash
~/.kimi-webbridge/bin/kimi-webbridge status
# {"version":"<daemon>", "extension_version":"<extension>"}
```

If a tool returns an error containing **"Please update the Kimi WebBridge extension"**, the user's extension is older than this skill. Tell the user:

> 请更新 Kimi WebBridge 浏览器扩展后重试：https://kimi.com/features/webbridge

Don't retry the failed tool. Don't auto-switch skill versions based on `extension_version` — the pairing protocol isn't finalized.
