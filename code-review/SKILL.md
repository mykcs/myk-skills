---
name: code-review
description: Reviews uncommitted changes for security vulnerabilities, code-quality issues, and best-practice violations, then blocks the commit if CRITICAL or HIGH issues are present.
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-19"
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
