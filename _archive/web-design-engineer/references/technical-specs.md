## Technical Specifications

### HTML File Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Descriptive Title</title>
    <style>/* CSS */</style>
</head>
<body>
    <!-- Content -->
    <script>/* JS */</script>
</body>
</html>
```

### React + Babel (Inline JSX)

When building React prototypes, use **pinned-version** CDN scripts (keeping `integrity` hashes is recommended; remove them if the CDN is restricted):

```html
<script src="https://unpkg.com/react@18.3.1/umd/react.development.js"
        integrity="sha384-hD6/rw4ppMLGNu3tX5cjIb+uRZ7UkRJ6BPkLpg4hAu/6onKUg4lLsHAs9EBPT82L"
        crossorigin="anonymous"></script>
<script src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js"
        integrity="sha384-u6aeetuaXnQ38mYT8rp6sbXaQe3NL9t+IBXmnYxwkUI2Hw4bsp2Wvmx4yRQF1uAm"
        crossorigin="anonymous"></script>
<script src="https://unpkg.com/@babel/standalone@7.29.0/babel.min.js"
        integrity="sha384-m08KidiNqLdpJqLq95G/LEi8Qvjl/xUYll3QILypMoQ65QorJ9Lvtp2RXYGBFj1y"
        crossorigin="anonymous"></script>
```

#### Three Non-negotiable Hard Rules

**1. Never use `const styles = { ... }`** — Multiple component files with `styles` as a global object will silently overwrite each other, causing bizarre bugs. Always namespace with the component name:

```jsx
const terminalStyles = { container: { ... }, line: { ... } };
const headerStyles = { wrap: { ... } };
```

Or use inline `style={{...}}` directly. **Never use `styles` as a variable name.**

**2. Separate `<script type="text/babel">` blocks do not share scope** — Each Babel script is compiled independently. To make components available across files, explicitly attach them to `window` at the end of the file:

```jsx
function Terminal() { /* ... */ }
function Line() { /* ... */ }

Object.assign(window, { Terminal, Line });
```

**3. Do not use `scrollIntoView`** — In iframe-embedded preview environments, it disrupts outer-frame scrolling. For programmatic scrolling, use `element.scrollTop = ...` or `window.scrollTo({...})` instead.

#### Additional Notes

- Do not add `type="module"` to React CDN script tags — it breaks the Babel transpilation pipeline
- Import order: React → ReactDOM → Babel → your component files (each as `<script type="text/babel" src="...">`)

### CSS Best Practices

- Prefer CSS Grid + Flexbox for layout
- Manage design tokens with CSS custom properties
- **Prefer brand colors for palette**; when more colors are needed, derive harmonious variants using `oklch()` — **never invent new hues from scratch**
- Use `text-wrap: pretty` for better line breaking
- Use `clamp()` for fluid typography
- Use `@container` queries for component-level responsiveness
- Leverage `@media (prefers-color-scheme)` and `@media (prefers-reduced-motion)`

### File Management

- Use descriptive filenames: `Landing Page.html`, `Dashboard Prototype.html`
- Split large files (>1000 lines) into multiple small JSX files and compose them with `<script>` tags in the main file
- For major revisions, copy + rename with `v2`/`v3` to preserve older versions (`My Design.html` → `My Design v2.html`)
- For multiple variants, prefer **a single file + Tweaks toggles** over separate files
- Copy assets locally before referencing them — don't hotlink directly to user-provided assets

> 📚 **More code templates** (device frames, slide engine, animation timeline, Tweaks panel, dark mode, design canvas, data visualization) available in [references/advanced-patterns.md](references/advanced-patterns.md)

---
