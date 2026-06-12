## Output Type Guidelines

### Interactive Prototypes

- **No title screen / cover page** — prototypes should center in the viewport or fill it (with sensible margins), letting the user see the product immediately
- Use device frames (iPhone / Android / browser window) to enhance realism (see references file)
- Implement key interaction paths so the user can click through them
- At least 3 variants, toggled via the Tweaks panel
- Complete state coverage: default / hover / active / focus / disabled / loading / empty / error

### HTML Slide Decks / Presentations

- Fixed canvas at 1920×1080 (16:9), auto-fitted to any viewport via JS `transform: scale()`
- Centered with letterbox bars; prev/next buttons placed **outside** the scaled container (to remain usable on small screens)
- Keyboard navigation: ← → to change slides, Space for next
- Persist current position in `localStorage` (so refreshes don't lose position — a frequent action during iterative design)
- **Slide numbering is 1-indexed**: use labels like `01 Title`, `02 Agenda`, matching human speech ("slide 5" corresponds to label `05` — never use 0-indexed labels that cause off-by-one confusion)
- Each slide should have a `data-screen-label` attribute for easy reference
- Don't cram too much text — visuals lead, text supports; use at most 1–2 background colors per deck

### Data Visualization Dashboards

- Chart.js (simple) or D3.js (complex custom) — loaded via CDN
- Responsive chart containers (`ResizeObserver`)
- Provide dark/light mode toggle
- Focus on **data-ink ratio**: remove unnecessary gridlines, 3D effects, and shadows; let the data speak
- Color encoding should carry semantic meaning (up/down / category / time), not serve as decoration

### Animation / Video Demos

Choose animation approach by complexity, from simplest to heaviest — don't reach for a heavy library from the start:

1. **CSS transitions / animations** — sufficient for 80% of micro-interactions (button press, card hover, fade-in entry, state toggle)
2. **Simple React state + setTimeout / requestAnimationFrame** — simple frame-by-frame or event-driven animations
3. **Custom `useTime` + `Easing` + `interpolate`** (full implementation in references) — timeline-driven video/demo scenes: scrubber, play/pause, multi-segment choreography
4. **Fallback: Popmotion** (`https://unpkg.com/popmotion@11.0.5/dist/popmotion.min.js`) — only if the above three layers genuinely can't cover the use case

> Avoid importing Framer Motion / GSAP / Lottie and other heavy libraries — they introduce bundle-size overhead, version-compatibility issues, and problems with React 18's inline Babel mode. Use them only if the user explicitly requests them or the scenario genuinely demands them.

Additional requirements:
- Provide play/pause button and progress bar (scrubber)
- Define a unified easing-function library (reuse the same set of easings within a project) for consistent motion language
- Don't add a "title screen" to video-type artifacts — go straight into the main content

### Static Visual Comparison vs. Full Flow

- **Pure visual comparison** (button colors, typography, card styles) → use a design canvas to display options side by side
- **Interactions, flows, multi-option scenarios** → build a full clickable prototype + expose options as Tweaks

---
