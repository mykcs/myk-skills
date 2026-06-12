## Tools

| Tool | Args | Returns | Note |
|------|------|---------|------|
| `navigate` | `url`, `newTab`(bool), `group_title` | `{success, url, tabId}` | Always use `newTab:true` on first call. `group_title` sets the tab group's visible label |
| `find_tab` | `url`, `active`(bool) | `{success, url, tabId}` | **Reuse an already-open tab** — pass any URL or domain; `active:true` picks the tab the user is currently viewing, default picks the leftmost match |
| `snapshot` | — | `{url, title, tree}` with `@e` refs | **Accessibility tree** (text) — use this to read page content and locate elements |
| `click` | `selector` (@e ref or CSS) | `{success, tag, text}` | Synthetic `el.click()` |
| `fill` | `selector`, `value` | `{success, tag, mode}` | Works on `<input>`/`<textarea>` AND `[contenteditable]` (ProseMirror/Lexical/Slate). `mode` is `"value"` or `"contenteditable"` |
| `evaluate` | `code` (supports async/await) | `{type, value}` | |
| `screenshot` | `format`(png\|jpeg), `quality`(0-100), optional `selector` (@e/CSS) | `{format, dataLength, data}` (base64) | Full page floods context — use helper script (saves to disk, returns path). With `selector` only that element is captured (small, OK to call API directly) |
| `network` | `cmd`(start\|stop\|list\|detail), `filter`, `requestId` | request/response data | |
| `upload` | `selector`, `files`(string[]) | `{success, fileCount}` | |
| `save_as_pdf` | `paper_format`, `landscape`, `scale`, `print_background`, `file_name` | `{path, sizeBytes, mimeType, pageTitle}` | Render current page → PDF, saved under `/tmp/kimi-webbridge-pdfs/` |
| `list_tabs` | — | `{success, tabs:[{tabId, url, title, active, groupTitle}]}` | Inspect tabs in the current session |
| `close_tab` | — | `{success, closed: bool}` | Close the current tab in the session |
| `close_session` | — | `{success, closed: int}` | Close all tabs — `closed` is the count. Always call at task end |

### Using find_tab

Use `find_tab` when the user explicitly asks to operate on an already-open tab. It matches by domain, so any URL on the same site works. Without `active:true`, returns the leftmost matching tab; with `active:true`, returns the tab the user is currently viewing — pass it when the user says "用我打开的 X" / "在我当前的 X 页面上".

```bash
curl -s -X POST http://127.0.0.1:10086/command \
  -d '{"action":"find_tab","args":{"url":"https://www.kimi.com","active":true},"session":"kimi"}'
```

If `find_tab` returns "no open tab found", the page is not open — fall back to `navigate` with `newTab:true`.

### Call Format

```bash
curl -s -X POST http://127.0.0.1:10086/command \
  -H 'Content-Type: application/json' \
  -d '{"action":"navigate","args":{"url":"https://example.com","newTab":true}}'
```
