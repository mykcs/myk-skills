---
name: myk-skills-development-patterns
description: Auto-generated skill from repository analysis. Teaches core development patterns and workflows used in the myk-skills repository. Python codebase focused on schema migration, documentation synchronization, audit automation, and protocol management.
---

# myk-skills Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill teaches the core development patterns and workflows used in the `myk-skills` repository. The codebase is Python-based, with a focus on schema migration, documentation synchronization, audit automation, and protocol management. It emphasizes clear coding conventions, robust migration scripts, and systematic workflow automation, supporting maintainable and scalable skill development.

## Coding Conventions

- **File Naming:**  
  Use kebab-case for all file names.  
  _Example:_  
  ```
  paper-card-schema-upgrade.md
  bin/migrate.py
  ```

- **Import Style:**  
  Use relative imports within modules.  
  _Example:_  
  ```python
  from .utils import parse_card
  ```

- **Export Style:**  
  Use named exports (explicitly define what is exported).  
  _Example:_  
  ```python
  __all__ = ["migrate_paper_card", "extract_paper_cards_from_doc"]
  ```

- **Commit Messages:**  
  Follow the [Conventional Commits](https://www.conventionalcommits.org/) standard.  
  Prefixes: `feat`, `docs`, `fix`, `refactor`, `perf`  
  _Example:_  
  ```
  feat: add support for new paper card enum fields in migration script
  ```

## Workflows

### Paper Card Schema Upgrade
**Trigger:** When a new paper card format version is released or schema changes are needed.  
**Command:** `/upgrade-paper-card-schema`

1. Update `SKILL.md` with new changelog, description, and section headers for the new version.
2. Rewrite or extend `references/paper-card.md` to include new frontmatter, relationship sections, and usage guidance.
3. Rewrite or extend `references/paper-entry.md` to add new template fields, enums, and detailed instructions.
4. Update `bin/migrate.py` header docstring to document new migration logic and fields.
5. Implement or update migration logic in `bin/migrate.py` to handle new fields, enums, and LLM checks.
6. Test migration script in dry-run mode and verify output.
7. Prepare for batch migration of all relevant docx files.

_Code Example (migration logic snippet):_
```python
def migrate_paper_card(card):
    # Add new enum field with default
    card['status'] = card.get('status', 'pending')
    # Perform LLM check if required
    if 'llm_check' in card:
        card['llm_verified'] = run_llm_check(card)
    return card
```

---

### Docx Batch Migration with migrate.py
**Trigger:** When all documentation needs to be migrated to the latest paper card schema version.  
**Command:** `/migrate-docx-paper-cards`

1. Implement or refine `extract_paper_cards_from_doc` logic to accurately identify paper card blocks.
2. Integrate or update status detection heuristics and OpenReview API fallback in `bin/migrate.py`.
3. Generate new DocxXML blocks for the upgraded paper card format.
4. Optimize migration to use batch `block_replace` instead of multiple `block_delete`/`block_insert` calls.
5. Run dry-run migration and audit results (migrated/skipped/failed).
6. Execute actual migration across all docx files.
7. Snapshot docx JSON before migration for rollback safety.
8. Mark or skip papers with low confidence for manual review.

_Code Example (batch migration):_
```python
for docx_file in docx_files:
    cards = extract_paper_cards_from_doc(docx_file)
    new_blocks = [upgrade_card(card) for card in cards]
    docx_file.replace_blocks(cards, new_blocks)
```

---

### Multi-Script Audit Exit Code Normalization
**Trigger:** When audit/detection scripts are updated or new scripts are added to the toolchain.  
**Command:** `/normalize-audit-exit-codes`

1. Identify all scripts that report findings via exit code.
2. Refactor each script to always exit 0 on successful execution, regardless of findings.
3. Ensure findings are reported in structured JSON output (count, by_type, by_severity, etc.).
4. Update wrapper scripts to propagate only true execution failures as exit 1.
5. Test all scripts in bash pipelines to confirm correct chaining and output.
6. Document the new convention for downstream consumers.

_Code Example (exit code normalization):_
```python
import sys
import json

def main():
    findings = run_audit()
    print(json.dumps(findings))
    sys.exit(0)  # Always exit 0 unless an execution error occurs

if __name__ == "__main__":
    main()
```

---

### Protocol Rename and Layer Update
**Trigger:** When a protocol or methodology is renamed or its structure changes.  
**Command:** `/rename-protocol`

1. Rename protocol in all relevant markdown files (README, SKILL.md, references).
2. Update reports and scripts to use new protocol name and terminology.
3. Synchronize any taxonomy or matrix changes (e.g., downgrade matrix, layer structure).
4. Test for consistency across all documentation and tool outputs.

_Code Example (protocol rename):_
```bash
# Example: Rename Tri-Search to Force-All-Search
grep -rl 'Tri-Search' . | xargs sed -i 's/Tri-Search/Force-All-Search/g'
```

## Testing Patterns

- **Test File Naming:**  
  Test files use the pattern `*.test.*` (e.g., `migrate.test.py`).

- **Framework:**  
  No specific testing framework detected; use standard Python `unittest` or `pytest` conventions.

- **Example:**
  ```python
  # migrate.test.py
  def test_migrate_paper_card():
      card = {"title": "Test"}
      migrated = migrate_paper_card(card)
      assert "status" in migrated
  ```

## Commands

| Command                      | Purpose                                                        |
|------------------------------|----------------------------------------------------------------|
| /upgrade-paper-card-schema    | Upgrade paper card schema and update documentation/scripts      |
| /migrate-docx-paper-cards     | Batch-migrate all docx paper cards to the new schema           |
| /normalize-audit-exit-codes   | Normalize audit script exit codes and output handling           |
| /rename-protocol              | Rename protocol and update all references and documentation     |
```
