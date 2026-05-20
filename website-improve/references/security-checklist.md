# 安全检查清单

> 面向 Astro 静态站点的安全快速扫描。静态站点攻击面较小，但仍需关注几个关键点。

---

## 1. `set:html` 审计

Astro 的 `set:html` 是最常见 XSS 风险点。

### 检测

```bash
grep -rn "set:html" src/ --include="*.astro"
```

### 评估标准

| 风险等级 | 场景 |
|----------|------|
| **CRITICAL** | `set:html={userInput}` — 直接渲染用户输入 |
| **HIGH** | `set:html={fetchedContent}` — 渲染外部获取的 HTML（如 CMS） |
| **MEDIUM** | `set:html={markdownHTML}` — 渲染 Markdown 转 HTML（依赖解析器安全性） |
| **LOW** | `set:html={staticHTML}` — 完全静态、硬编码的 HTML 片段 |

### 修复

```astro
<!-- 危险：直接用户输入 -->
<div set:html={userComment} />  ❌

<!-- 安全：纯文本转义 -->
<div>{userComment}</div>  ✅

<!-- 如必须渲染富文本，使用可信库 sanitize -->
<div set:html={DOMPurify.sanitize(userComment)} />  ⚠️ 需审查
```

---

## 2. Secrets & 凭证

### 检测

```bash
grep -rni "api_key\|apikey\|secret\|token\|password\|private_key" \
  src/ --include="*.astro" --include="*.ts" --include="*.js" \
  | grep -v "process.env\|import.meta.env\|NEXT_PUBLIC_\|VITE_"
```

### 通过标准

- 无硬编码密钥、密码、token
- 环境变量通过 `import.meta.env.*` 读取
- `.env` 在 `.gitignore` 中

### 修复

```astro
<!-- 错误 -->
<script>const API_KEY = "sk-abc123";</script>

<!-- 正确 -->
<script>const API_KEY = import.meta.env.PUBLIC_API_KEY;</script>
```

---

## 3. 依赖安全

### 检测

```bash
npm audit --audit-level=moderate
```

### 通过标准

- 0 critical / high severity
- 或：已评估并记录例外（非自动修复）

### 自动修复（安全时）

```bash
npm audit fix
```

**注意：** `npm audit fix` 可能引入破坏性变更。运行后必须 `npm run build` 验证。

---

## 4. 外部链接

### 检测

```bash
grep -rn 'href="http' src/ --include="*.astro" | grep -v 'rel="noopener"\|rel="noreferrer"'
```

### 修复

```astro
<!-- 错误 -->
<a href="https://external.com" target="_blank">外部链接</a>

<!-- 正确 -->
<a href="https://external.com" target="_blank" rel="noopener noreferrer">外部链接</a>
```

---

## 5. Content Security Policy (CSP)

### 推荐配置（通过 `<meta>` 或 HTTP header）

```html
<meta http-equiv="Content-Security-Policy"
  content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self';"
>
```

**注意：** `unsafe-inline` 对 script/style 是 Astro 静态站常见妥协。如使用 `nonce`，需服务端支持。

---

## 6. 快速扫描脚本

```bash
#!/bin/bash
echo "=== Security Quick Scan ==="

echo "--- set:html usage ---"
grep -rn "set:html" src/ --include="*.astro" || echo "PASS: no set:html"

echo "--- Hardcoded secrets ---"
grep -rni "api_key\|apikey\|secret\|token\|password" \
  src/ --include="*.astro" --include="*.ts" \
  | grep -v "process.env\|import.meta.env" \
  || echo "PASS: no hardcoded secrets"

echo "--- npm audit ---"
npm audit --audit-level=moderate --json 2>/dev/null | jq '.metadata.vulnerabilities' 2>/dev/null || npm audit --audit-level=moderate

echo "--- .env in gitignore ---"
grep "\.env" .gitignore || echo "WARN: .env not in .gitignore"

echo "--- External links without noopener ---"
grep -rn 'href="http' src/ --include="*.astro" | grep -v 'rel="noopener"\|rel="noreferrer"' || echo "PASS"
```
