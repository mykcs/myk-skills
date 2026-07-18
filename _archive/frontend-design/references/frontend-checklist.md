# Frontend Project Audit Checklist

> 当 rich-audit 检测到当前目录包含 Astro 项目特征时（`astro.config.mjs` / `astro.config.ts` / `package.json` 中有 `astro` 依赖），自动启用前端审计模块。

## 0. Project Detection

```bash
# Astro detection
[ -f "astro.config.mjs" ] || [ -f "astro.config.ts" ] || grep -q '"astro"' package.json 2>/dev/null && echo "ASTRO_PROJECT" || echo "NOT_ASTRO"
```

## 1. Build Health Check

**Goal**: `npm run build` passes with zero errors.

**Procedure**:
```bash
npm run build 2>&1 | tee /tmp/build.log
# Check exit code
echo "EXIT_CODE: $?"
# Check for errors
grep -i "error\|failed\|cannot find module" /tmp/build.log | head -10
```

**Acceptance**: Exit code 0 and no error lines.

## 2. i18n Content Parity Check

**Goal**: `en.json` and `zh.json` have identical key sets. No hardcoded UI text in components.

**Procedure**:
```bash
# Key parity
node -e "console.log(Object.keys(require('./src/content/i18n/en.json')).sort().join('\n'))" > /tmp/en_keys.txt 2>/dev/null
node -e "console.log(Object.keys(require('./src/content/i18n/zh.json')).sort().join('\n'))" > /tmp/zh_keys.txt 2>/dev/null
diff /tmp/en_keys.txt /tmp/zh_keys.txt && echo "KEYS_MATCH" || echo "KEY_MISMATCH"

# Hardcoded string scan
grep -rn "[一-鿿]" src/ --include="*.astro" --include="*.ts" | grep -v "import.*from" | grep -v "t(" | head -20
grep -rn "[A-Z][a-z].{20,50}" src/ --include="*.astro" | grep -v "t(" | grep -v "import" | head -20
```

**Acceptance**: Empty diff and zero hardcoded strings.

## 3. Responsive Viewport Check

**Goal**: Zero layout regressions across 4 viewports.

**Required Viewports**:
| Device | Width | Height |
|--------|-------|--------|
| Mobile | 375px | 812px |
| Tablet | 768px | 1024px |
| Desktop | 1280px | 800px |
| Wide | 1920px | 1080px |

**Procedure** (after `npm run build`):
```bash
npm run preview -- --port 4321 &
PID=$!
sleep 3
# Use Playwright to check each viewport
# Report: console errors, horizontal overflow, clipped elements
kill $PID
```

**Acceptance**: Zero console errors, no horizontal overflow, no clipped elements at mobile width.

### 3.1 Text Rendering Across Viewports

**Goal**: Text content renders correctly at all viewport widths — no overflow, no clipping, readable font sizes.

**Required Viewports** (same as above):
| Device | Width | Height |
|--------|-------|--------|
| Mobile | 375px | 812px |
| Tablet | 768px | 1024px |
| Desktop | 1280px | 800px |
| Wide | 1920px | 1080px |

**Detection**:
```bash
# Check for hardcoded fixed widths that break responsive text
# Note: CSS has space after ":", use "width: *[0-9]" pattern
grep -rn "width: *[0-9]*px" src/ --include="*.astro" --include="*.css" | grep -v "max-width" | grep -v "%" | head -10

# Check for text-overflow CSS usage (warning)
grep -rn "text-overflow\|overflow-wrap\|word-break" src/ --include="*.astro" --include="*.css" | head -10

# Check for font-size without responsive units (no clamp/rem)
grep -rn "font-size: *[0-9]*px" src/ --include="*.astro" --include="*.css" | grep -v "clamp" | grep -v "rem" | head -10

# Check min font-size is not below readable threshold (12px)
grep -rn "font-size: *[0-9]*px" src/ --include="*.astro" --include="*.css" | awk -F: '{gsub(/[^0-9]/,"",$NF); if($NF+0 < 12 && $NF+0 > 0) print}' | head -5
```

**Acceptance**: All text elements have responsive sizing (clamp/rem/em), no fixed px font-size < 12px, no horizontal text overflow at 375px.

**Common issues**:
- Fixed `width: 800px` on text containers → overflows at mobile
- `font-size: 10px` or `11px` on body text → unreadable
- Long unbreakable strings (URLs, IDs) without `word-break: break-all`
- `text-overflow: ellipsis` without `overflow-wrap: anywhere`

## 4. Astro 2025 Compliance Check

Based on official Astro changelog and community best practices.

### 4.1 Component Migration
- [ ] `<ViewTransitions />` replaced with `<ClientRouter />` (Astro 4+)
- [ ] `<Image format="webp">` removed (Astro 6 auto-optimizes)
- [ ] `Astro.glob()` replaced with Content Collections

**Detection**:
```bash
grep -rn "ViewTransitions" src/ --include="*.astro" && echo "FOUND: ViewTransitions (migrate to ClientRouter)" || echo "OK: no ViewTransitions"
grep -rn 'format="webp"' src/ --include="*.astro" && echo "FOUND: Image format prop (remove)" || echo "OK: no format prop"
grep -rn "Astro.glob" src/ --include="*.astro" && echo "FOUND: Astro.glob (use Content Collections)" || echo "OK: no Astro.glob"
```

### 4.2 i18n Configuration
- [ ] `redirectToDefaultLocale` explicitly set (default changed to `false` in v6)
- [ ] `prefixDefaultLocale` consistent with routing strategy
- [ ] Fallback middleware only intercepts 404s

**Detection**:
```bash
grep -q "redirectToDefaultLocale" astro.config.mjs astro.config.ts 2>/dev/null && echo "OK: redirectToDefaultLocale set" || echo "MISSING: set redirectToDefaultLocale explicitly"
```

### 4.3 Tailwind Integration
- [ ] Using `@tailwindcss/vite` instead of deprecated `@astrojs/tailwind`

**Detection**:
```bash
grep -q "@astrojs/tailwind" package.json && echo "DEPRECATED: @astrojs/tailwind" || echo "OK: no deprecated Tailwind integration"
grep -q "@tailwindcss/vite" package.json && echo "OK: using @tailwindcss/vite" || echo "MISSING: @tailwindcss/vite"
```

### 4.4 Dependencies Security
- [ ] Vue i18n patched (CVE-2025-27597) if applicable
- [ ] No unused dependencies

**Detection**:
```bash
# Unused deps check
for pkg in lodash moment jquery; do
  grep -r "from ['\"]$pkg['\"]" src/ || echo "$pkg unused"
done
```

### 4.5 Performance
- [ ] Below-the-fold images have `loading="lazy"` and `decoding="async"`
- [ ] No Google Fonts CDN links (use `@fontsource/*`)

**Detection**:
```bash
grep -rn "fonts.googleapis.com\|fonts.gstatic.com" src/ public/ && echo "FOUND: Google Fonts CDN" || echo "OK: no Google Fonts"
grep -rn "<img" src/ | grep -v "loading=\"lazy\"" | head -10
```

## 5. Scoring

| Dimension | Weight | Max Score |
|-----------|--------|-----------|
| Build Health | 30% | 30 |
| i18n Parity | 25% | 25 |
| Responsive | 25% | 25 |
| Astro 2025 Compliance | 20% | 20 |
| **Total** | **100%** | **100** |

**Grade**: 90+ = PASS, 70-89 = WARN, <70 = FAIL
