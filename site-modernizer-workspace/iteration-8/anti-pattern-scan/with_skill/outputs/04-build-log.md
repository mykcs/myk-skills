# Build Log

## Initial Build (before fixes)
```
> mock-anti-pattern-site@1.0.0 build
> astro build

Error [ERR_MODULE_NOT_FOUND]: Cannot find module '.../node_modules/.bin/dist/cli/index.js'
```
**Resolution**: Clean install (`rm -rf node_modules package-lock.json && npm install`)

## Build After Clean Install (before fixes)
```
19:50:42 [build] output: "static"
19:50:42 [build] mode: "static"
19:50:42 [vite] ✓ built in 279ms
19:50:42 [vite] ✓ 13 modules transformed.
19:50:42 ▶ src/pages/index.astro
19:50:42   └─ /index.html (+4ms)
19:50:42 ✓ Completed in 7ms.
19:50:42 [build] 1 page(s) built in 368ms
19:50:42 [build] Complete!
```
**Status**: PASS

## astro check (before fixes)
```
src/pages/index.astro:13:44 - error ts(2339): Property 'frontmatter' does not exist on type 'unknown'.
src/pages/index.astro:13:36 - error ts(2339): Property 'url' does not exist on type 'unknown'.

Result (3 files):
- 2 errors
- 0 warnings
- 0 hints
```
**Status**: FAIL

## Build After Fixes (missing hero.png)
```
[ERROR] [vite] ✗ Build failed in 282ms
Could not resolve "../assets/hero.png" from "src/components/Gallery.astro"
```
**Status**: FAIL
**Resolution**: Generated placeholder `src/assets/hero.png`

## Build After Fixes (with hero.png)
```
19:52:05 [build] output: "static"
19:52:05 [vite] ✓ built in 328ms
19:52:06 ▶ src/pages/index.astro
19:52:06   └─ /index.html (+6ms)
19:52:06 ✓ Completed in 11ms.
19:52:07   ▶ /_astro/hero.DoXX-APV_X4H0O.webp (before: 2kB, after: 0kB) (+1.39s) (1/2)
19:52:07   ▶ /_astro/hero.DoXX-APV_ZG1eFx.webp (before: 2kB, after: 0kB) (+8ms) (2/2)
19:52:07 [build] 1 page(s) built in 1.81s
19:52:07 [build] Complete!
```
**Status**: PASS

## astro check After Fixes (before removing unused var)
```
src/pages/index.astro:12:7 - warning ts(6133): 'themeColor' is declared but its value is never read.

Result (3 files):
- 0 errors
- 0 warnings
- 1 hint
```
**Status**: PASS (with 1 hint)

## Final astro check (after removing unused var)
```
Result (3 files):
- 0 errors
- 0 warnings
- 0 hints
```
**Status**: PASS

## Final Build
```
19:52:25 [vite] ✓ built in 36ms
19:52:25 ▶ src/pages/index.astro
19:52:25   └─ /index.html (+10ms)
19:52:25   ▶ /_astro/hero.C_WWi07p_hx290.webp (reused cache entry) (+1ms) (1/2)
19:52:25   ▶ /_astro/hero.C_WWi07p_Z1mxTxm.webp (reused cache entry) (+0ms) (2/2)
19:52:25 [build] 1 page(s) built in 431ms
19:52:25 [build] Complete!
```
**Status**: PASS
