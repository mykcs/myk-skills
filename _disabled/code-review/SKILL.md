---
name: code-review
description: Reviews uncommitted changes for security vulnerabilities, code-quality issues, and best-practice violations, then blocks the commit if CRITICAL or HIGH issues are present.
when_to_use: |
  触发: commit 前审查 uncommitted changes (git diff HEAD) — 查 hardcoded 密钥 / 注入 / XSS 等 CRITICAL 安全 + 函数>50行 / 文件>800行等 HIGH 质量.
  产出: CRITICAL/HIGH/MEDIUM/LOW 分级报告 (文件+行号+建议修法); 有 CRITICAL/HIGH → block commit.
  不适用: 已提交历史代码审计 / 已合入 PR 的 review / 非 git 仓库.
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-19"
triggers:
  - code-review
  - /code-review
  - code review
  - commit 前审查
  - security review
  - uncommitted changes review

---


> Migrated from `~/.claude/commands/code-review.md` on 2026-06-15.
> Original slash command continues to work; this skill version supports auto-trigger by description keyword.

Comprehensive security and quality review of uncommitted changes:

1. Get changed files: git diff --name-only HEAD

2. For each changed file, check for:

**Security Issues (CRITICAL):**
- Hardcoded credentials, API keys, tokens
- SQL injection vulnerabilities
- XSS vulnerabilities  
- Missing input validation
- Insecure dependencies
- Path traversal risks

**Code Quality (HIGH):**
- Functions > 50 lines
- Files > 800 lines
- Nesting depth > 4 levels
- Missing error handling
- console.log statements
- TODO/FIXME comments
- Missing JSDoc for public APIs

**Best Practices (MEDIUM):**
- Mutation patterns (use immutable instead)
- Emoji usage in code/comments
- Missing tests for new code
- Accessibility issues (a11y)

3. Generate report with:
   - Severity: CRITICAL, HIGH, MEDIUM, LOW
   - File location and line numbers
   - Issue description
   - Suggested fix

4. Block commit if CRITICAL or HIGH issues found

Never approve code with security vulnerabilities!
