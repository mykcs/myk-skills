#!/usr/bin/env python3
"""
rich_audit.py — Layer 1 Mechanical Audit for the ~/.claude/ and ~/.omc/ ecosystem.
Produces a structured JSON report covering six dimensions:
Integrity, Consistency, Timeliness, Redundancy, Performance, Security.

Usage:
    python3 ~/.agents/skills/rich-audit/scripts/rich_audit.py [--fix] [--output path.json]

Options:
    --fix      Apply safe, non-destructive auto-fixes and re-audit.
    --output   Write JSON report to the specified path (default: stdout).
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

HOME = Path.home()
CLAUDE_DIR = HOME / ".claude"
OMC_DIR = HOME / ".omc"
BACKUP_DIR = CLAUDE_DIR / "backups"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.datetime.now().isoformat()


def backup_path(src: Path) -> Path:
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = BACKUP_DIR / f"rich-audit-{ts}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    dest = backup_dir / src.relative_to(HOME)
    dest.parent.mkdir(parents=True, exist_ok=True)
    return dest


def safe_copy(src: Path, dest: Path) -> None:
    import shutil
    shutil.copy2(src, dest)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


# Known public API / marketplace domains that commonly appear in configs
# but do NOT contain embedded credentials — excluded to avoid false positives.
_PUBLIC_API_DOMAINS = {
    "modelcontextprotocol.io",
    "sentry.io",
    "github.com",
    "api.github.com",
    "raw.githubusercontent.com",
    "cdn.jsdelivr.net",
    "registry.npmjs.org",
    "pypi.org",
    "crates.io",
    "hub.docker.com",
    "registry.hub.docker.com",
}


def _is_public_api_url(url: str) -> bool:
    """Return True if the URL looks like a public API/marketplace endpoint, not a secret."""
    for domain in _PUBLIC_API_DOMAINS:
        if domain in url:
            return True
    return False


def grep_secrets(text: str) -> list[dict]:
    """Scan text for common secret patterns. Conservative — avoids false positives."""
    findings = []

    # High-confidence exact patterns
    exact_patterns = [
        (r'sk-[a-zA-Z0-9]{48}', "OpenAI-style API key"),
        (r'gh[pousr]_[A-Za-z0-9_]{36,}', "GitHub token"),
        (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID"),
        (r'[sr]g-[a-zA-Z0-9]{32,}', "Cloudflare/Generic API token"),
        (r'https?://[^/\s:@]+:[^@\s]+@[^/\s]+', "URL with embedded credentials"),
    ]
    for pat, label in exact_patterns:
        for m in re.finditer(pat, text):
            matched = m.group()
            if label == "URL with embedded credentials":
                # Guard: skip public API URLs
                if _is_public_api_url(matched):
                    continue
                # Guard: if the "credential" part (between : and @) contains JSON punctuation,
                # this is a false positive from matching across JSON boundaries like
                # https://host"},{"version":"1.0","source":"name -> host:1.0","source":"name@
                # Extract credential portion for inspection
                cred_match = re.search(r'https?://[^/\s:@]+:([^@]+)@', matched)
                if cred_match:
                    cred_part = cred_match.group(1)
                    # JSON structure chars indicate a false positive (e.g. 1.5.5","source":"...)
                    if '"' in cred_part or ',' in cred_part:
                        continue
            findings.append({"pattern": label, "position": m.span(), "snippet": matched[:20] + "..."})

    # Context-aware patterns: only flag if near a secret keyword
    secret_keywords = [
        "api_key", "apikey", "api-key", "secret", "token", "password", "passwd",
        "auth", "bearer", "credential", "private_key", "access_key", "app_key"
    ]
    # Look for KEYWORD = "long-random-string" or KEYWORD: long-random-string
    context_pat = re.compile(
        r'(?:' + '|'.join(secret_keywords) + r')\s*[:=]\s*["\']?([A-Za-z0-9_/+=\-]{32,})["\']?',
        re.IGNORECASE
    )
    for m in context_pat.finditer(text):
        val = m.group(1)
        # Exclude common non-secrets: file paths, booleans, sample values
        if any(c in val for c in ['/']) and val.count('/') >= 2:
            continue
        if val.lower() in ('true', 'false', 'null', 'undefined', 'example', 'placeholder'):
            continue
        findings.append({"pattern": "Context-aware secret", "position": m.span(), "snippet": val[:20] + "..."})

    return findings


def is_json_valid(path: Path) -> tuple[bool, str]:
    try:
        json.loads(path.read_text())
        return True, ""
    except json.JSONDecodeError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Dimension checkers
# ---------------------------------------------------------------------------

def check_integrity(report: dict) -> list[dict]:
    findings = []

    # OMC plugin directories referenced by hooks exist
    # Lesson from session: Plugin directory missing causes all hooks to fail with
    # "Failed to run: Plugin directory does not exist" errors.
    plugins_dir = CLAUDE_DIR / "plugins" / "cache"
    if plugins_dir.exists():
        for hook_file in (CLAUDE_DIR / "hooks").rglob("*.json"):
            try:
                hooks_cfg = json.loads(hook_file.read_text())
                hooks_section = hooks_cfg.get("hooks", {})
                if isinstance(hooks_section, dict):
                    for event_type, hook_list in hooks_section.items():
                        if not isinstance(hook_list, list):
                            continue
                        for hook_def in hook_list:
                            if not isinstance(hook_def, dict):
                                continue
                            for inner_hook in hook_def.get("hooks", []):
                                if not isinstance(inner_hook, dict):
                                    continue
                                cmd = inner_hook.get("command", "")
                                for part in cmd.split():
                                    if "plugins/cache/" in part:
                                        plugin_path = Path(part.replace("$HOME", str(HOME)).replace("${HOME}", str(HOME)))
                                        if not plugin_path.exists() and not plugin_path.is_absolute():
                                            plugin_path = HOME / part.lstrip("~/")
                                        if not plugin_path.exists() and "plugins/cache" in str(plugin_path):
                                            findings.append({
                                                "severity": "HIGH",
                                                "file": str(hook_file),
                                                "line": None,
                                                "message": f"Hook references missing plugin directory: {part}",
                                                "auto_fix": None,
                                            })
            except Exception:
                pass

    # Hook scripts exist
    hooks_dir = CLAUDE_DIR / "hooks"
    hooks_json = CLAUDE_DIR / "hooks" / "hooks.json"
    if hooks_json.exists():
        try:
            hooks_cfg = json.loads(hooks_json.read_text())
            hooks_section = hooks_cfg.get("hooks", {})
            for event_type, hook_list in hooks_section.items() if isinstance(hooks_section, dict) else []:
                if not isinstance(hook_list, list):
                    continue
                for hook_def in hook_list:
                    if not isinstance(hook_def, dict):
                        continue
                    for inner_hook in hook_def.get("hooks", []):
                        if not isinstance(inner_hook, dict):
                            continue
                        cmd = inner_hook.get("command", "")
                        if not cmd:
                            continue
                        # Extract first token as script path
                        parts = cmd.split()
                        if parts:
                            script = Path(parts[0].replace("$HOME", str(HOME)).replace("${HOME}", str(HOME)))
                            if not script.exists() and not script.is_absolute():
                                script = CLAUDE_DIR / "scripts" / script.name
                            if not script.exists():
                                findings.append({
                                    "severity": "HIGH",
                                    "file": str(hooks_json),
                                    "line": None,
                                    "message": f"Hook '{event_type}/{hook_def.get('id', 'unknown')}' points to missing script: {cmd}",
                                    "auto_fix": "remove_hook",
                                    "auto_fix_target": str(hooks_json),
                                    "auto_fix_data": {
                                        "event_type": event_type,
                                        "hook_id": hook_def.get("id", "unknown"),
                                        "command": cmd,
                                    },
                                })
        except Exception as e:
            findings.append({"severity": "HIGH", "file": str(hooks_json), "line": None,
                             "message": f"hooks.json unreadable: {e}", "auto_fix": None})

    # settings.json validity
    settings = CLAUDE_DIR / "settings.json"
    if settings.exists():
        ok, err = is_json_valid(settings)
        if not ok:
            findings.append({
                "severity": "HIGH",
                "file": str(settings),
                "line": None,
                "message": f"settings.json invalid JSON: {err}",
                "auto_fix": "reformat_json",
                "auto_fix_target": str(settings),
            })

    # ECC gateguard-fact-force hook detection
    # Lesson from session: This hook blocks the first Bash/Edit/Write of every session,
    # forcing a manual fact statement. It must be explicitly disabled via ECC_DISABLED_HOOKS.
    if settings.exists():
        try:
            settings_data = json.loads(settings.read_text())
            env = settings_data.get("env", {})
            disabled_hooks = env.get("ECC_DISABLED_HOOKS", "")
            if "gateguard-fact-force" not in disabled_hooks:
                findings.append({
                    "severity": "MED",
                    "file": str(settings),
                    "line": None,
                    "message": "ECC gateguard-fact-force hook is active — it will block the first Bash/Edit/Write of every session. Add 'gateguard-fact-force' to ECC_DISABLED_HOOKS in env.",
                    "auto_fix": None,
                })
        except Exception:
            pass

    # MCP configs validity
    mcp_file = HOME / ".mcp.json"
    if mcp_file.exists():
        ok, err = is_json_valid(mcp_file)
        if not ok:
            findings.append({"severity": "MED", "file": str(mcp_file), "line": None,
                             "message": f".mcp.json invalid JSON: {err}", "auto_fix": None})

    # Submodule version map — for marketplace plugins managed via git submodule
    # the cache dir name may match the submodule tag even when installed_plugins.json
    # hasn't been updated yet (upgrade-in-progress scenario).
    submodule_versions: dict[str, str] = {}
    marketplaces_dir = CLAUDE_DIR / "plugins" / "marketplaces"
    if marketplaces_dir.exists():
        for vendor_dir in marketplaces_dir.iterdir():
            if not vendor_dir.is_dir():
                continue
            for plugin_dir in vendor_dir.iterdir():
                if not plugin_dir.is_dir() or not (plugin_dir / ".git").exists():
                    continue
                try:
                    result = subprocess.run(
                        ["git", "-C", str(plugin_dir), "describe", "--tags", "--exact-match"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        tag = result.stdout.strip().lstrip("v")
                        # key format: "plugin_name@marketplace"
                        plugin_key = f"{plugin_dir.name}@{vendor_dir.name}"
                        submodule_versions[plugin_key] = tag
                except Exception:
                    pass

    # Plugin residue detection
    # Lesson from session: Uninstalling a plugin leaves its cache dir referenced by hooks,
    # causing "Plugin directory does not exist" errors every session until restart.
    # Also: after upgrade, installed_plugins.json may lag behind submodule tag,
    # causing false-positive orphan reports on the NEW cache dir.
    installed_plugins_file = CLAUDE_DIR / "plugins" / "installed_plugins.json"
    if installed_plugins_file.exists():
        try:
            ip_data = json.loads(installed_plugins_file.read_text())
            registered_paths = set()
            for plugin_entries in ip_data.get("plugins", {}).values():
                for entry in plugin_entries:
                    install_path = entry.get("installPath")
                    if install_path:
                        registered_paths.add(Path(install_path))
                        if not Path(install_path).exists():
                            findings.append({
                                "severity": "HIGH",
                                "file": str(installed_plugins_file),
                                "line": None,
                                "message": f"Installed plugin path missing: {install_path} ({entry.get('scope')} scope). Plugin may have been partially uninstalled or cache corrupted.",
                                "auto_fix": None,
                            })
            # Orphan cache detection (with upgrade-aware exclusion)
            cache_dir = CLAUDE_DIR / "plugins" / "cache"
            if cache_dir.exists():
                for vendor_dir in cache_dir.iterdir():
                    if not vendor_dir.is_dir():
                        continue
                    for plugin_dir in vendor_dir.iterdir():
                        if not plugin_dir.is_dir():
                            continue
                        for version_dir in plugin_dir.iterdir():
                            if not version_dir.is_dir() and not version_dir.is_symlink():
                                continue
                            # CASE-085 workaround detection: symlink from old version -> new version
                            if version_dir.is_symlink():
                                target = version_dir.resolve()
                                findings.append({
                                    "severity": "MED",
                                    "file": str(version_dir),
                                    "line": None,
                                    "message": f"Symlink workaround detected: {version_dir} -> {target}. Indicates stale hook cache reference (CASE-085). Run '/plugin install {plugin_dir.name}@{vendor_dir.name}' in a NEW session to flush framework hook registry, then remove symlink.",
                                    "auto_fix": None,
                                })
                                continue
                            if version_dir in registered_paths:
                                continue
                            # Active-session exclusion: if cache dir has .in_use files, it's managed by the framework
                            in_use_dir = version_dir / ".in_use"
                            if in_use_dir.exists() and in_use_dir.is_dir() and any(in_use_dir.iterdir()):
                                continue
                            # Marketplace runtime copy exclusion: if a counterpart exists in marketplaces/,
                            # this cache dir is a framework-managed runtime copy, not an orphan.
                            # Two possible layouts: marketplaces/<vendor>/<plugin>/ or marketplaces/<vendor>/ (vendor=plugin)
                            mp_base = CLAUDE_DIR / "plugins" / "marketplaces" / vendor_dir.name
                            if (mp_base / plugin_dir.name).exists() or (mp_base / ".mcp.json").exists():
                                continue
                            # Upgrade-aware exclusion: if cache dir matches submodule tag, it's not an orphan
                            plugin_key = f"{plugin_dir.name}@{vendor_dir.name}"
                            dir_version = version_dir.name
                            if plugin_key in submodule_versions and submodule_versions[plugin_key] == dir_version:
                                continue
                            findings.append({
                                "severity": "MED",
                                "file": str(version_dir),
                                "line": None,
                                "message": f"Orphan plugin cache directory not registered in installed_plugins.json: {version_dir}. May be leftover from previous uninstall.",
                                "auto_fix": None,
                            })
        except Exception:
            pass

    # Plugin version drift detection
    # Lesson from session: installed_plugins.json version field can diverge from
    # actual cache directory name after plugin upgrades, causing hook resolution failures.
    if installed_plugins_file.exists():
        try:
            ip_data = json.loads(installed_plugins_file.read_text())
            for plugin_name, plugin_entries in ip_data.get("plugins", {}).items():
                for entry in plugin_entries:
                    install_path = entry.get("installPath", "")
                    registered_version = entry.get("version", "")
                    if install_path and registered_version:
                        # Marketplace plugins: installPath points to the plugin root dir
                        # (e.g. marketplaces/omc/ or marketplaces/vendor/plugins/name/),
                        # so basename is the plugin name, not a version number.
                        if "marketplaces/" in install_path:
                            continue
                        actual_version = Path(install_path).name
                        if actual_version != registered_version:
                            findings.append({
                                "severity": "HIGH",
                                "file": str(installed_plugins_file),
                                "line": None,
                                "message": f"Plugin version drift for {plugin_name}: registered='{registered_version}' but cache dir='{actual_version}' at {install_path}",
                                "auto_fix": None,
                            })
        except Exception:
            pass

    # Registry lag detection (submodule ahead of installed_plugins.json)
    # Lesson from session: installed_plugins.json may not be updated during
    # 'omc update' or manual submodule upgrade, causing the NEW cache to be
    # misreported as orphan and the OLD cache to remain registered.
    if installed_plugins_file.exists() and submodule_versions:
        try:
            ip_data = json.loads(installed_plugins_file.read_text())
            for plugin_name, plugin_entries in ip_data.get("plugins", {}).items():
                for entry in plugin_entries:
                    install_path = entry.get("installPath", "")
                    registered_version = entry.get("version", "")
                    if not install_path or not registered_version:
                        continue
                    # Extract vendor/plugin from installPath: .../cache/<vendor>/<plugin>/<version>
                    parts = Path(install_path).parts
                    if len(parts) >= 2:
                        vendor = parts[-3] if "cache" in parts else ""
                        plugin = parts[-2] if vendor else ""
                        plugin_key = f"{plugin}@{vendor}"
                        if plugin_key in submodule_versions:
                            submodule_ver = submodule_versions[plugin_key]
                            if registered_version != submodule_ver:
                                findings.append({
                                    "severity": "MED",
                                    "file": str(installed_plugins_file),
                                    "line": None,
                                    "message": f"Registry lag for {plugin_name}: installed_plugins.json has v{registered_version} but submodule tag is v{submodule_ver}. Update registry or run '/plugin install {plugin_name}' in a new session.",
                                    "auto_fix": None,
                                })
        except Exception:
            pass

    # Hardcoded stale plugin cache path detection in hook scripts
    # Lesson from session: Hook scripts (not just hooks.json) can contain hardcoded
    # references to old plugin cache paths that no longer exist, especially when
    # plugins move from cache/ to marketplaces/ after upgrade.
    # Example: omc-orchestrator.mjs referencing cache/everything-claude-code/2.0.0-rc.1
    # when the actual plugin is in marketplaces/ecc/skills/continuous-learning-v2/.
    for script_file in (CLAUDE_DIR / "hooks").rglob("*"):
        if not script_file.is_file():
            continue
        if script_file.suffix not in (".sh", ".mjs", ".js", ".py", ".json"):
            continue
        try:
            content = script_file.read_text()
        except Exception:
            continue
        # Match absolute paths to plugin cache directories
        # Patterns: /Users/<name>/.claude/plugins/cache/... or $HOME/.claude/plugins/cache/... or ~/.claude/plugins/cache/...
        cache_path_pattern = re.compile(
            r'(?:/Users/[^/]+|\$HOME|~)/\.claude/plugins/cache/[^"\'\s]+'
        )
        for match in cache_path_pattern.finditer(content):
            path_str = match.group(0)
            resolved = path_str.replace("$HOME", str(HOME)).replace("~", str(HOME))
            full_path = Path(resolved)
            if full_path.exists():
                continue
            line_no = content[:match.start()].count("\n") + 1
            findings.append({
                "severity": "HIGH",
                "file": str(script_file),
                "line": line_no,
                "message": f"Hook script references non-existent plugin cache path: {path_str}. Plugin may have been moved to marketplaces or cache was cleaned after upgrade.",
                "auto_fix": None,
            })

    # fnm lazy loading detection
    # Lesson from session: _fnm_lazy_load shell function is not exported to child
    # processes, causing MCP server spawning to fail with "command not found: node".
    for shell_rc in [HOME / ".zshrc", HOME / ".bashrc"]:
        if shell_rc.exists():
            text = shell_rc.read_text()
            if "_fnm_lazy_load" in text:
                findings.append({
                    "severity": "MED",
                    "file": str(shell_rc),
                    "line": None,
                    "message": "fnm lazy loading detected (_fnm_lazy_load). This breaks MCP server spawning because the function is not exported to child processes. Replace with direct 'eval \"$(fnm env --use-on-cd)\"'.",
                    "auto_fix": None,
                })

    # Git runtime tracking detection
    # Lesson from session: Runtime directories (.omc/state/, homunculus/, logs/)
    # were accidentally committed to git, causing pollution and merge conflicts.
    gitignore = CLAUDE_DIR / ".gitignore"
    if gitignore.exists():
        gitignore_content = gitignore.read_text()
        required_patterns = [".omc/state/", "homunculus/", ".claude/logs/", ".claude/.cache/"]
        for pattern in required_patterns:
            if pattern not in gitignore_content:
                findings.append({
                    "severity": "MED",
                    "file": str(gitignore),
                    "line": None,
                    "message": f"Runtime directory '{pattern}' not covered by .gitignore — risk of committing transient state files.",
                    "auto_fix": "append_gitignore",
                    "auto_fix_target": str(gitignore),
                    "auto_fix_data": pattern,
                })

    # HUD cache stale detection
    # Lesson from session: omc-hud-cache.sh OUTPUT_FILE can be empty if async
    # rendering never completes, leaving "[OMC] Starting..." visible permanently.
    hud_script = CLAUDE_DIR / "hud" / "omc-hud-cache.sh"
    if hud_script.exists():
        text = hud_script.read_text()
        for line in text.splitlines():
            if "OUTPUT_FILE" in line and "=" in line:
                output_file_match = re.search(r'OUTPUT_FILE=["\']?([^"\'\s]+)', line)
                if output_file_match:
                    output_file = Path(output_file_match.group(1).replace("$HOME", str(HOME)).replace("${HOME}", str(HOME)))
                    if output_file.exists() and output_file.stat().st_size == 0:
                        findings.append({
                            "severity": "MED",
                            "file": str(hud_script),
                            "line": None,
                            "message": f"HUD cache file is empty (0 bytes): {output_file}. Async rendering may have failed to populate it.",
                            "auto_fix": None,
                        })
                    break

    # Referenced paths in rules exist
    rules_dir = CLAUDE_DIR / "rules"
    if rules_dir.exists():
        for rule_file in rules_dir.rglob("*.md"):
            rel = rule_file.relative_to(rules_dir)
            if any(part in ("archive", "backups") for part in rel.parts):
                continue
            content = rule_file.read_text()
            for m in re.finditer(r'`(~?[/.][^`]+)`', content):
                ref = m.group(1)
                ref_path = Path(ref.replace("~", str(HOME)))
                if "/" in ref and not ref_path.exists() and not ref.endswith((".md", ".json", ".sh", ".py")):
                    continue  # Might be a URL fragment or generic path
                if ref.startswith("~/") and not ref_path.exists() and ref.endswith((".md", ".json", ".sh", ".py")):
                    findings.append({
                        "severity": "MED",
                        "file": str(rule_file),
                        "line": None,
                        "message": f"Rule references non-existent path: {ref}",
                        "auto_fix": None,
                    })

    return findings


def check_consistency(report: dict) -> list[dict]:
    findings = []

    # Look for potential rule conflicts by scanning for key phrases
    rules_dir = CLAUDE_DIR / "rules"
    rule_texts: dict[str, str] = {}
    if rules_dir.exists():
        for rule_file in rules_dir.rglob("*.md"):
            text = rule_file.read_text()
            lines = text.splitlines()
            in_code_block = False
            filtered_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    continue
                if "WRONG" in stripped or "ANTI-PATTERN" in stripped or "Anti-patterns" in stripped:
                    continue
                filtered_lines.append(line)
            rule_texts[rule_file.name] = "\n".join(filtered_lines).lower()

    # Simple conflict heuristics
    conflict_pairs = [
        ("never use git push", "git push", "Direct git push ban vs push mention"),
        ("no apology", "sorry", "No-apology rule vs apology text"),
        ("always create new objects", "mutate", "Immutability rule vs mutation mention"),
    ]

    # Split each rule into paragraphs (blank-line separated) for proximity-aware
    # conflict detection. A conflict only fires when phrase_a and phrase_b appear
    # on DIFFERENT LINES within the same paragraph — not when they co-appear in
    # a single sentence (e.g. "always create new objects, never mutate" is the rule
    # itself, not a conflict with itself).
    def _paragraphs(text: str) -> list[str]:
        return [p.strip() for p in text.split("\n\n") if p.strip()]

    def _lines(para: str) -> list[str]:
        return [l.strip() for l in para.split("\n") if l.strip()]

    files = list(rule_texts.keys())
    for f1 in files:
        text_lower = rule_texts[f1]
        for phrase_a, phrase_b, desc in conflict_pairs:
            for para in _paragraphs(text_lower):
                lines_with_a = [l for l in _lines(para) if phrase_a in l]
                lines_with_b = [l for l in _lines(para) if phrase_b in l]
                # Conflict only when they appear on DIFFERENT lines — co-presence on
                # the same line (e.g. "always create new objects, never mutate") is
                # the rule itself, not a self-conflict.
                if lines_with_a and lines_with_b and lines_with_a != lines_with_b:
                    findings.append({
                        "severity": "MED",
                        "file": f1,
                        "line": None,
                        "message": f"Possible internal conflict: {desc}",
                        "auto_fix": None,
                    })
                    break  # one finding per file per conflict pair

    # Memory references match actual files
    memory_dir = CLAUDE_DIR / "memory"
    if memory_dir.exists():
        for mem_file in memory_dir.rglob("*.md"):
            content = mem_file.read_text()
            for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content):
                raw = m.group(2).replace("~", str(HOME))
                link_path = Path(raw)
                if not link_path.is_absolute():
                    link_path = mem_file.parent / link_path
                if link_path.suffix in (".md", ".json", ".sh") and not link_path.exists():
                    findings.append({
                        "severity": "LOW",
                        "file": str(mem_file),
                        "line": None,
                        "message": f"Memory references missing file: {link_path}",
                        "auto_fix": None,
                    })

    # Ghost case references detection
    # Lesson from session: CASE files reference other cases in `related:` frontmatter
    # that may have been renamed, archived, or deleted, creating broken links.
    # v2.0: Recurse into archive-*/ subdirs to detect references to archived cases
    # (previously these were false positives in L3 mem0 gap detection).
    cases_dir = CLAUDE_DIR / "knowledge" / "cases" / "wiki"
    if cases_dir.exists():
        for case_file in cases_dir.rglob("CASE-*.md"):
            content = case_file.read_text()
            # Extract related field from frontmatter
            related_match = re.search(r'^related:\s*\[(.*?)\]', content, re.MULTILINE | re.DOTALL)
            if related_match:
                related_items = [item.strip().strip('"').strip("'") for item in related_match.group(1).split(",")]
                for related in related_items:
                    if not related:
                        continue
                    # Check if it's a URL or path
                    if related.startswith("http"):
                        continue
                    # Try to resolve in cases, rules, or memory directories
                    import glob as _glob
                    search_patterns = [
                        str(cases_dir / f"*{related}*"),
                        str(CLAUDE_DIR / "rules" / f"{related}.md"),
                        str(CLAUDE_DIR / "rules" / "archive" / f"{related}.md"),
                        str(CLAUDE_DIR / "memory" / f"{related}.md"),
                        str(CLAUDE_DIR / "memory" / "reference" / f"{related}.md"),
                        str(CLAUDE_DIR / "memory" / "feedback" / f"{related}.md"),
                        str(CLAUDE_DIR / "memory" / "project" / f"{related}.md"),
                    ]
                    found = any(_glob.glob(p) for p in search_patterns)
                    if not found:
                        findings.append({
                            "severity": "LOW",
                            "file": str(case_file),
                            "line": None,
                            "message": f"Ghost case reference: '{related}' listed in related: but file does not exist.",
                            "auto_fix": None,
                        })

    # Frontmatter date mismatch detection
    # Lesson from session: CASE filename date can diverge from YAML frontmatter date,
    # causing confusion about when the issue actually occurred.
    if cases_dir.exists():
        for case_file in cases_dir.rglob("CASE-*.md"):
            content = case_file.read_text()
            # Extract date from filename: CASE-XXXX-YYYYMMDD
            filename_date_match = re.search(r'CASE-[^-]+-(\d{8})', case_file.name)
            frontmatter_date_match = re.search(r'^date:\s*(\d{4}-\d{2}-\d{2})', content, re.MULTILINE)
            if filename_date_match and frontmatter_date_match:
                filename_date = filename_date_match.group(1)
                frontmatter_date = frontmatter_date_match.group(1).replace("-", "")
                if filename_date != frontmatter_date:
                    findings.append({
                        "severity": "LOW",
                        "file": str(case_file),
                        "line": None,
                        "message": f"Frontmatter date mismatch: filename has '{filename_date}' but YAML says '{frontmatter_date_match.group(1)}'.",
                        "auto_fix": None,
                    })

    return findings


def check_timeliness(report: dict) -> list[dict]:
    findings = []
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=30)

    # Backup file count threshold
    if BACKUP_DIR.exists():
        backups = list(BACKUP_DIR.iterdir())
        if len(backups) > 50:
            findings.append({
                "severity": "LOW",
                "file": str(BACKUP_DIR),
                "line": None,
                "message": f"Backup directory has {len(backups)} items (>50); consider pruning.",
                "auto_fix": None,
            })

    # Memories untouched > 30 days (skipped if reviewed frontmatter is recent)
    memory_dir = CLAUDE_DIR / "memory"
    cutoff_days = 90  # Skip mtime check if reviewed within 90 days
    if memory_dir.exists():
        for mem_file in memory_dir.rglob("*.md"):
            mtime = datetime.datetime.fromtimestamp(mem_file.stat().st_mtime)
            if mtime >= cutoff:
                continue
            # Check for reviewed frontmatter
            content = mem_file.read_text(errors="ignore")
            reviewed_match = re.search(r"^reviewed:\s*(\d{4}-\d{2}-\d{2})", content, re.MULTILINE)
            if reviewed_match:
                reviewed_date = datetime.datetime.strptime(reviewed_match.group(1), "%Y-%m-%d")
                review_cutoff = now - datetime.timedelta(days=cutoff_days)
                if reviewed_date >= review_cutoff:
                    continue  # Skip: has recent review
            findings.append({
                "severity": "LOW",
                "file": str(mem_file),
                "line": None,
                "message": f"Memory file untouched for {(now - mtime).days} days.",
                "auto_fix": None,
            })

    # Skills without SKILL.md
    # v2.1: removed — this duplicate emission is now in check_skill_health().
    # Previously emitted the same finding in two dimensions (timeliness AND
    # skill_health), causing double-counting and dragging health_score.
    # The skill_health check is the canonical home for skill structural issues
    # (line count, description size, missing SKILL.md).

    # Obsolete directories check
    obsolete_names = {"_archive", ".old", "backup", "tmp"}
    for root in (CLAUDE_DIR, OMC_DIR):
        if root.exists():
            for p in root.rglob("*"):
                if p.is_dir() and p.name.lower() in obsolete_names:
                    # Skip .git internal directories (e.g. .git/refs/heads/backup)
                    if ".git" in p.parts:
                        continue
                    findings.append({
                        "severity": "LOW",
                        "file": str(p),
                        "line": None,
                        "message": f"Potentially obsolete directory: {p.name}",
                        "auto_fix": None,
                    })

    return findings


def check_redundancy(report: dict) -> list[dict]:
    findings = []


# ---------------------------------------------------------------------------
# v2.1 — Skill health dimension
# ---------------------------------------------------------------------------
SKILL_MAX_LINES = 500  # Anthropic official limit (code.claude.com/docs/en/skills)
SKILL_MAX_DESC_CHARS = 1536  # description+when_to_use truncation threshold

# v2.1: Skills subdirs that are NOT real skills (structural, framework, etc).
# Module-level so check_timeliness and check_skill_health can both use it.
# v1.0.0 reported 25 false positives from these dirs.
SKILL_STRUCTURAL_EXCLUDE = {
    # dotfile metadata dirs
    ".git", ".omc", ".cache", ".claude-plugin",
    # tool/asset/template dirs that are NOT skills
    "scripts", "templates", "assets", "themes", "examples",
    "reference", "references", "docs", "plugins", "shared", "core",
    # language-specific framework subdirs (may or may not be skills — verify)
    "python", "typescript", "go", "java", "csharp", "ruby", "php",
}


def check_skill_health(report: dict) -> list[dict]:
    """v2.1: Check skill portfolio against Anthropic official size limits.

    Two checks per code.claude.com/docs/en/skills:
      1. SKILL.md > 500 lines → MED (WARN)
      2. frontmatter description+when_to_use > 1536 chars → MED (WARN)
      3. SKILL.md missing in non-structural dir → MED (was 25 FPs in v1.0.0)

    Skills in SKILL_STRUCTURAL_EXCLUDE are skipped (not real skills).

    Source of truth: ~/.agents/skills/ (per CLAUDE.md "Skills 管理" 2026-06-01
    refactor). ~/.claude/skills/ is a consumer symlink; may or may not be
    present depending on local setup. Scanning the source of truth directly
    ensures consistent results across machines.
    """
    findings = []
    skills_dir = HOME / ".agents" / "skills"
    if not skills_dir.exists():
        return findings

    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        if skill_dir.name in SKILL_STRUCTURAL_EXCLUDE:
            continue
        if skill_dir.name.startswith(".") and skill_dir.name not in SKILL_STRUCTURAL_EXCLUDE:
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            findings.append({
                "severity": "MED",
                "file": str(skill_dir),
                "line": None,
                "message": f"Skill directory missing SKILL.md: {skill_dir.name}",
                "auto_fix": None,
            })
            continue

        # Check 1: line count
        try:
            line_count = sum(1 for _ in skill_file.open())
        except OSError:
            continue
        if line_count > SKILL_MAX_LINES:
            findings.append({
                "severity": "MED",
                "file": str(skill_file),
                "line": None,
                "message": f"SKILL.md exceeds {SKILL_MAX_LINES} lines ({line_count}). Anthropic limit; split into reference files per code.claude.com/docs/en/skills.",
                "auto_fix": None,
            })

        # Check 2: description+when_to_use char count
        try:
            content = skill_file.read_text()
        except OSError:
            continue
        import re as _re
        fm_match = _re.match(r'^---\n(.*?)\n---\n', content, _re.DOTALL)
        if not fm_match:
            continue
        fm = fm_match.group(1)
        desc_match = _re.search(r'^description:\s*(.*?)(?=^[a-z_]+:|\Z)', fm, _re.MULTILINE | _re.DOTALL)
        wtu_match = _re.search(r'^when_to_use:\s*(.*?)(?=^[a-z_]+:|\Z)', fm, _re.MULTILINE | _re.DOTALL)
        desc_chars = 0
        if desc_match:
            desc_chars += len(desc_match.group(1).strip().strip('"\''))
        if wtu_match:
            desc_chars += len(wtu_match.group(1).strip().strip('"\''))
        if desc_chars > SKILL_MAX_DESC_CHARS:
            findings.append({
                "severity": "MED",
                "file": str(skill_file),
                "line": None,
                "message": f"frontmatter description+when_to_use exceeds {SKILL_MAX_DESC_CHARS} chars ({desc_chars}). Truncated in skill listing; consolidate fields.",
                "auto_fix": None,
            })

    return findings


def check_redundancy(report: dict) -> list[dict]:
    findings = []

    # Duplicate rules (content similarity via hash)
    rules_dir = CLAUDE_DIR / "rules"
    hashes: dict[str, list[str]] = {}
    if rules_dir.exists():
        for rule_file in rules_dir.rglob("*.md"):
            rel = rule_file.relative_to(rules_dir)
            if any(part in ("archive", "backups") for part in rel.parts):
                continue
            content = rule_file.read_text().strip()
            h = hashlib.sha256(content.encode()).hexdigest()
            hashes.setdefault(h, []).append(str(rule_file))
        for h, paths in hashes.items():
            if len(paths) > 1:
                findings.append({
                    "severity": "MED",
                    "file": paths[0],
                    "line": None,
                    "message": f"Identical rule content found in {len(paths)} files: {', '.join(Path(p).name for p in paths)}",
                    "auto_fix": "merge_duplicate_rules",
                    "auto_fix_target": paths[0],
                    "auto_fix_data": paths,
                })

    # Unused scripts not referenced by anything
    # v2.1: comprehensive reference scan (hooks + rules + skills + settings +
    # cross-scripts). Previous version only checked hooks, which gave false
    # positives for scripts referenced from rules/behavioral-*.md or skills.
    scripts_dir = CLAUDE_DIR / "scripts"
    if scripts_dir.exists():
        all_scripts = {f.name for f in scripts_dir.iterdir() if f.is_file()}
        referenced: set[str] = set()

        # 1) Hook references (settings.json + hooks/hooks.json + settings.local.json)
        for settings_path in (CLAUDE_DIR / "settings.json",
                              CLAUDE_DIR / "settings.local.json",
                              CLAUDE_DIR / "hooks" / "hooks.json"):
            if not settings_path.exists():
                continue
            try:
                content = settings_path.read_text()
            except OSError:
                continue
            for s in all_scripts:
                if s in content:
                    referenced.add(s)

        # 2) Rules references
        rules_dir = CLAUDE_DIR / "rules"
        if rules_dir.exists():
            for rule_file in rules_dir.rglob("*.md"):
                try:
                    content = rule_file.read_text()
                except OSError:
                    continue
                for s in all_scripts:
                    if s in content:
                        referenced.add(s)

        # 3) Skills references (in ~/.agents/skills/)
        agents_skills = HOME / ".agents" / "skills"
        if agents_skills.exists():
            for skill_file in agents_skills.rglob("SKILL.md"):
                try:
                    content = skill_file.read_text()
                except OSError:
                    continue
                for s in all_scripts:
                    if s in content:
                        referenced.add(s)

        # 4) Cross-script references (one script calls another)
        for s in all_scripts:
            script_path = scripts_dir / s
            try:
                content = script_path.read_text()
            except OSError:
                continue
            for other in all_scripts:
                if other != s and other in content:
                    referenced.add(other)

        # 5) CLAUDE.md / settings.local.json explicit allowlists
        for extra_path in (CLAUDE_DIR / "CLAUDE.md", CLAUDE_DIR / "settings.local.json"):
            if not extra_path.exists():
                continue
            try:
                content = extra_path.read_text()
            except OSError:
                continue
            for s in all_scripts:
                if s in content:
                    referenced.add(s)

        # Independent CLI tools not meant to be called by anything (CLI tools)
        independent_scripts = {
            "smart-autopush.sh", "ap-intent.sh", "evolve.sh",
            "evolution-trigger.sh", "evolution-distill.sh",
            "backup-settings.sh", "fix-hook-missing.py",
            "case-lint.py", "notion_safe_ops.py",
            "bitable-sync-guard.py", "gh-api-push.sh",
            "omc-quality-benchmark.sh", "memory-audit.sh",
            "test_rich_audit.py",
            # v2.1: audit/CLI tools (invoked manually or by future hooks)
            "check-skills.sh", "l2-check.sh", "omc-version-sync.sh",
            "context-verify.sh", "smart-push.sh", "evolve.sh",
        }
        for script in all_scripts - referenced:
            if script in ("rich-audit.py", "rich_audit.py") or script in independent_scripts:
                continue
            # Skip already-archived scripts
            if (scripts_dir / "archive-2026-06" / script).exists():
                continue
            # v2.1: orphan script (truly no references anywhere).
            # Auto-archive to scripts/archive-YYYY-MM/ (preserves evidence chain).
            target = scripts_dir / script
            findings.append({
                "severity": "LOW",
                "file": str(target),
                "line": None,
                "message": f"Orphan script (no references in hooks/rules/skills/settings): {script}",
                "auto_fix": "archive_orphan_script",
                "auto_fix_target": str(target),
            })

    return findings


def check_performance(report: dict) -> list[dict]:
    findings = []
    scripts_dir = CLAUDE_DIR / "scripts"
    if not scripts_dir.exists():
        return findings

    for script_file in scripts_dir.rglob("*"):
        if not script_file.is_file():
            continue
        if script_file.name in ("rich-audit.py", "rich_audit.py"):
            continue
        # Skip nested state/cache directories inside scripts
        if ".omc" in script_file.parts or ".cache" in script_file.parts:
            continue
        try:
            text = script_file.read_text()
        except Exception:
            continue

        if "while True" in text or "for ;;" in text:
            findings.append({
                "severity": "MED",
                "file": str(script_file),
                "line": None,
                "message": "Potential unbounded loop detected.",
                "auto_fix": None,
            })

        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if "git add -A" in line or "git add ." in line:
                findings.append({
                    "severity": "MED",
                    "file": str(script_file),
                    "line": None,
                    "message": "Script uses broad 'git add -A' — prefer explicit file lists.",
                    "auto_fix": None,
                })
                break

        curls = text.count("curl ")
        if curls > 3:
            findings.append({
                "severity": "LOW",
                "file": str(script_file),
                "line": None,
                "message": f"Multiple curl calls ({curls}) without caching — consider batching.",
                "auto_fix": None,
            })

    return findings


ARCH_HEALTH_THRESHOLDS = {
    "max_total_rules_lines": 3000,
    "max_claude_md_lines": 200,  # v2.1: aligned with Anthropic official target
                                  # (https://code.claude.com/docs/en/memory) + R1
                                  # rule change in rules/behavioral-workflow.md
    "max_single_rule_lines": 600,
    "max_rule_files": 15,
    "max_behavioral_prefix_files": 6,
    "max_archive_files": 50,
    "min_frontmatter_coverage": 1.0,
    "max_claude_md_operational_content": 0.25,
}


def _count_lines(path: Path) -> int:
    try:
        return len(path.read_text().splitlines())
    except Exception:
        return 0


def _has_frontmatter(path: Path) -> bool:
    try:
        text = path.read_text()
        if not text.startswith("---\n"):
            return False
        # Search for the closing --- anywhere before the first non-YAML content.
        # Use a generous limit (4000 bytes) to handle frontmatter with many
        # multi-byte characters (e.g. CJK description fields).
        closing_pos = text.find("\n---", 4)
        if closing_pos == -1 or closing_pos > 4000:
            return False
        return text[closing_pos:closing_pos + 4] == "\n---"
    except Exception:
        return False


def _claude_md_operational_ratio(path: Path) -> float:
    """Return the fraction of CLAUDE.md lines that contain operational details
    (code blocks, shell commands, specific file paths) rather than principles."""
    try:
        import re
        lines = path.read_text().splitlines()
        if not lines:
            return 0.0
        operational = 0
        in_code_block = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                operational += 1
                continue
            if in_code_block:
                operational += 1
                continue
            if re.match(r"^(\$ |# |git |npm |pnpm |python3 |node |cd |mkdir |curl |wget |scp |ssh |docker |kubectl )", stripped):
                operational += 1
                continue
            if re.search(r"(scripts/|bin/|\.sh|\.py)\b", stripped) and ("run" in stripped.lower() or "execute" in stripped.lower() or "./" in stripped):
                operational += 1
                continue
        return operational / len(lines)
    except Exception:
        return 0.0


def check_architecture(report: dict) -> list[dict]:
    """Layer 1.5: architecture-health (quantitative thresholds vs Anthropic guidance)."""
    findings: list[dict] = []
    rules_dir = CLAUDE_DIR / "rules"
    claude_md = CLAUDE_DIR / "CLAUDE.md"

    if not rules_dir.exists():
        return findings

    # Active rules = top-level .md files (exclude archive/, common/ stays counted)
    active_files = [
        f for f in rules_dir.rglob("*.md")
        if "archive" not in f.parts and "detailed" not in f.parts
    ]
    archive_files = [f for f in rules_dir.rglob("*.md") if "archive" in f.parts]

    # Total active line budget
    total_lines = sum(_count_lines(f) for f in active_files)
    if total_lines > ARCH_HEALTH_THRESHOLDS["max_total_rules_lines"]:
        findings.append({
            "severity": "HIGH",
            "file": str(rules_dir),
            "line": None,
            "message": (
                f"Active rules total {total_lines} lines exceeds budget "
                f"{ARCH_HEALTH_THRESHOLDS['max_total_rules_lines']} (Anthropic context-window guidance). "
                f"Context-window dilution risk — consolidate to behavioral-* layer or move to archive."
            ),
            "auto_fix": None,
        })

    # Active file count ceiling
    if len(active_files) > ARCH_HEALTH_THRESHOLDS["max_rule_files"]:
        findings.append({
            "severity": "MED",
            "file": str(rules_dir),
            "line": None,
            "message": (
                f"{len(active_files)} active rule files exceeds ceiling "
                f"{ARCH_HEALTH_THRESHOLDS['max_rule_files']}. Merge by decision layer."
            ),
            "auto_fix": None,
        })

    # Per-file ceiling — single rule must fit attention budget
    for f in active_files:
        lines = _count_lines(f)
        if lines > ARCH_HEALTH_THRESHOLDS["max_single_rule_lines"]:
            findings.append({
                "severity": "MED",
                "file": str(f),
                "line": None,
                "message": (
                    f"Rule file {lines} lines exceeds {ARCH_HEALTH_THRESHOLDS['max_single_rule_lines']}-line "
                    f"attention ceiling. Split summary vs detailed sections."
                ),
                "auto_fix": None,
            })

    # behavioral-* prefix fragmentation
    behavioral_files = [f for f in active_files if f.name.startswith("behavioral-")]
    if len(behavioral_files) > ARCH_HEALTH_THRESHOLDS["max_behavioral_prefix_files"]:
        findings.append({
            "severity": "HIGH",
            "file": str(rules_dir),
            "line": None,
            "message": (
                f"{len(behavioral_files)} behavioral-* files exceeds "
                f"{ARCH_HEALTH_THRESHOLDS['max_behavioral_prefix_files']}-file ceiling. "
                f"Merge by decision layer (operating/thinking/tech/safety)."
            ),
            "auto_fix": None,
        })

    # CLAUDE.md ceiling
    if claude_md.exists():
        lines = _count_lines(claude_md)
        if lines > ARCH_HEALTH_THRESHOLDS["max_claude_md_lines"]:
            findings.append({
                "severity": "HIGH",
                "file": str(claude_md),
                "line": None,
                "message": (
                    f"CLAUDE.md {lines} lines exceeds {ARCH_HEALTH_THRESHOLDS['max_claude_md_lines']}-line "
                    f"ceiling. Move details into rules/ or memory/."
                ),
                "auto_fix": None,
            })

        # CLAUDE.md operational content ratio — should be principles, not scripts
        op_ratio = _claude_md_operational_ratio(claude_md)
        max_ratio = ARCH_HEALTH_THRESHOLDS["max_claude_md_operational_content"]
        if op_ratio > max_ratio:
            findings.append({
                "severity": "MED",
                "file": str(claude_md),
                "line": None,
                "message": (
                    f"CLAUDE.md operational content {op_ratio:.1%} exceeds threshold {max_ratio:.1%}. "
                    f"Move commands/scripts into rules/ or scripts/."
                ),
                "auto_fix": None,
            })

    # Frontmatter coverage on active rules
    if active_files:
        with_fm = sum(1 for f in active_files if _has_frontmatter(f))
        coverage = with_fm / len(active_files)
        if coverage < ARCH_HEALTH_THRESHOLDS["min_frontmatter_coverage"]:
            missing = [str(f) for f in active_files if not _has_frontmatter(f)]
            findings.append({
                "severity": "LOW",
                "file": str(rules_dir),
                "line": None,
                "message": (
                    f"Frontmatter coverage {coverage:.0%} < required "
                    f"{ARCH_HEALTH_THRESHOLDS['min_frontmatter_coverage']:.0%}. "
                    f"Missing on: {', '.join(missing[:5])}{'...' if len(missing) > 5 else ''}"
                ),
                "auto_fix": None,
            })

    # Archive bloat — orphaned retired rules
    if len(archive_files) > ARCH_HEALTH_THRESHOLDS["max_archive_files"]:
        findings.append({
            "severity": "LOW",
            "file": str(rules_dir / "archive"),
            "line": None,
            "message": (
                f"{len(archive_files)} archived rule files exceeds "
                f"{ARCH_HEALTH_THRESHOLDS['max_archive_files']}. Consider deletion or knowledge/cases/ migration."
            ),
            "auto_fix": None,
        })

    return findings


_EXCLUDED_DIRS = {
    "plugins/marketplaces", "plugins/cache",
    ".omc/state/checkpoints", ".omc/state/sessions",
}


def _is_excluded(path: Path) -> bool:
    try:
        rel = path.relative_to(HOME)
        rel_str = str(rel).replace("\\", "/")
        for excluded in _EXCLUDED_DIRS:
            if excluded in rel_str:
                return True
        return False
    except ValueError:
        return False


def check_security(report: dict) -> list[dict]:
    findings = []

    # Scan scripts and configs for hardcoded secrets
    for root in (CLAUDE_DIR / "scripts", CLAUDE_DIR, OMC_DIR):
        if not root.exists():
            continue
        for f in root.rglob("*"):
            if not f.is_file():
                continue
            if _is_excluded(f):
                continue
            if f.name.startswith("test_"):
                continue
            if f.suffix not in (".sh", ".py", ".mjs", ".json", ".md", ".yaml", ".yml", ".env"):
                continue
            try:
                text = f.read_text()
            except Exception:
                continue
            secrets = grep_secrets(text)
            for s in secrets:
                findings.append({
                    "severity": "HIGH",
                    "file": str(f),
                    "line": None,
                    "message": f"Possible hardcoded secret ({s['pattern']}): {s['snippet']}",
                    "auto_fix": None,
                })

    # Files with 777 permissions
    for root in (CLAUDE_DIR, OMC_DIR):
        if not root.exists():
            continue
        for f in root.rglob("*"):
            if not f.is_file():
                continue
            mode = f.stat().st_mode
            if mode & stat.S_IRWXO == stat.S_IRWXO:
                findings.append({
                    "severity": "HIGH",
                    "file": str(f),
                    "line": None,
                    "message": f"File has world-writable permissions ({oct(mode)[-3:]}).",
                    "auto_fix": "fix_permissions",
                    "auto_fix_target": str(f),
                })

    return findings


# ---------------------------------------------------------------------------
# Auto-fix engine
# ---------------------------------------------------------------------------

def apply_fix(finding: dict) -> dict:
    """Apply a single safe auto-fix. Returns updated finding with fix_result."""
    fix_type = finding.get("auto_fix")
    target = finding.get("auto_fix_target")
    if not fix_type or not target:
        finding["fix_result"] = "skipped"
        return finding

    target_path = Path(target)

    # Backup before any mutation
    if target_path.exists():
        dest = backup_path(target_path)
        safe_copy(target_path, dest)

    try:
        if fix_type == "remove_hook":
            hook_data = finding.get("auto_fix_data", {})
            event_type = hook_data.get("event_type")
            hook_id = hook_data.get("hook_id")
            hooks_json = target_path
            if hooks_json.exists():
                cfg = json.loads(hooks_json.read_text())
                hooks_section = cfg.get("hooks", {})
                if isinstance(hooks_section, dict) and event_type in hooks_section:
                    original_count = len(hooks_section[event_type])
                    cfg["hooks"][event_type] = [
                        h for h in hooks_section[event_type]
                        if not (isinstance(h, dict) and h.get("id") == hook_id)
                    ]
                    removed = original_count - len(cfg["hooks"][event_type])
                    if removed > 0:
                        hooks_json.write_text(json.dumps(cfg, indent=2) + "\n")
                        finding["fix_result"] = f"removed_hook ({removed})"
                    else:
                        finding["fix_result"] = "no_match"

        elif fix_type == "reformat_json":
            text = target_path.read_text()
            # Try to parse with comment stripping (JSONC)
            cleaned = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
            cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
            data = json.loads(cleaned)
            target_path.write_text(json.dumps(data, indent=2))
            finding["fix_result"] = "reformatted_json"

        elif fix_type == "fix_permissions":
            os.chmod(target_path, 0o644)
            finding["fix_result"] = "fixed_permissions_644"

        elif fix_type == "append_gitignore":
            pattern = finding.get("auto_fix_data", "")
            if pattern:
                with open(target_path, "a") as f:
                    f.write(f"\n{pattern}\n")
                finding["fix_result"] = f"appended_gitignore_{pattern}"
            else:
                finding["fix_result"] = "no_pattern"

        elif fix_type == "merge_duplicate_rules":
            # Mark for AI-layer handling; script layer just flags it
            finding["fix_result"] = "flagged_for_ai_merge"

        elif fix_type == "archive_orphan_script":
            # v2.1: move orphan script to scripts/archive-YYYY-MM/<name>.
            # Preserves evidence chain; can be restored manually.
            ts = datetime.datetime.now().strftime("%Y-%m")
            archive_dir = target_path.parent / f"archive-{ts}"
            archive_dir.mkdir(exist_ok=True)
            dest = archive_dir / target_path.name
            if dest.exists():
                # Avoid clobber; suffix with timestamp
                dest = archive_dir / f"{target_path.stem}.{ts}{target_path.suffix or ''}"
            target_path.rename(dest)
            finding["fix_result"] = f"archived_to_{archive_dir.name}_{target_path.name}"

        else:
            finding["fix_result"] = "unsupported"

    except Exception as e:
        finding["fix_result"] = f"error: {e}"

    return finding


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def calculate_score(findings: list[dict]) -> int:
    """v2.1: Calculate active (non-archive) health score.

    Uses SEVERITY_PENALTY_V21 (LOW=0.5 instead of 2) and excludes
    archive-path findings to prevent noise from dragging the score.
    """
    active = [f for f in findings if not _is_archive_finding(f)]
    base = 100.0
    for f in active:
        base -= SEVERITY_PENALTY_V21.get(f.get("severity", "LOW"), 0.5)
    return int(max(0, min(100, base)))


# 8-dimension weighted scoring model (per rich-audit v2.0 spec)
# Weights sum to 1.0. Each dimension's raw_score = 100 - (sum of penalties).
DIMENSION_WEIGHTS = {
    "architecture": 0.25,
    "integrity": 0.30,
    "security": 0.20,
    "consistency": 0.10,
    "github_sync": 0.05,
    "timeliness": 0.05,
    "redundancy": 0.03,
    "performance": 0.02,
}
# Map of dimension function name → score_breakdown key (alias for backwards compat)
DIMENSION_ALIAS = {
    "integrity": "integrity",
    "consistency": "consistency",
    "architecture": "architecture",
    "timeliness": "timeliness",
    "redundancy": "redundancy",
    "performance": "performance",
    "security": "security",
}


# ---------------------------------------------------------------------------
# v2.1 benchmark scoring constants
# ---------------------------------------------------------------------------
# Health tier thresholds (overall health_score → tier)
HEALTH_TIERS = [
    (90, "Excellent", "优秀 — 几乎所有维度健康"),
    (75, "Good", "良好 — 少量可优化项"),
    (60, "OK", "一般 — 建议关注"),
    (40, "Warning", "警告 — 需主动修复"),
    (0, "Critical", "严重 — 需立即处理"),
]

# v2.1 severity penalty table (replaces v2.0 flat penalties)
# v2.0: HIGH=10, MED=5, LOW=2 — caused 200 LOW to drag health_score to 0
# v2.1: HIGH=15, MED=5, LOW=0.5 — INFO findings (no penalty) for archive noise
SEVERITY_PENALTY_V21 = {
    "HIGH": 15.0,
    "MED": 5.0,
    "LOW": 0.5,
    "INFO": 0.0,
}

# v2.1: per-dimension minimum raw score to prevent single dim from tanking overall
# v2.0 issue: consistency had 196 ghost-ref findings, raw=0, dragged total down
# v2.1: cap at 30 — dim can be unhealthy but not catastrophic
DIMENSION_MIN_RAW = 30

# v2.1: dimension default weights (overridable via ~/.claude/audit-config.json)
DEFAULT_DIMENSION_WEIGHTS = {
    "architecture": 0.18,
    "integrity": 0.25,
    "security": 0.20,
    "consistency": 0.15,
    "github_sync": 0.08,
    "timeliness": 0.04,
    "redundancy": 0.03,
    "performance": 0.02,
    "skill_health": 0.05,
}

# v2.1: archive path detection
ARCHIVE_PATH_MARKERS = ("/archive-", "/archive/", "archive-2026", "archive-2025")


def _is_archive_finding(finding: dict) -> bool:
    """v2.1: Classify whether a finding is in an archived location.

    Archived findings don't count toward active health_score.
    """
    file_path = finding.get("file", "")
    return any(marker in file_path for marker in ARCHIVE_PATH_MARKERS)


def _load_audit_config() -> dict:
    """v2.1: Load dimension weights from ~/.claude/audit-config.json if present.

    Returns: dict with optional 'dimension_weights' override.
    Fallback: empty dict (use defaults).
    """
    config_path = Path.home() / ".claude" / "audit-config.json"
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _compute_health_tier(score: float) -> dict:
    """v2.1: Map health_score to tier classification.

    Returns: {tier, label, description, color_hint}
    """
    for threshold, tier, desc in HEALTH_TIERS:
        if score >= threshold:
            return {
                "tier": tier,
                "label_zh": desc,
                "score": score,
                "color_hint": {
                    "Excellent": "green", "Good": "green", "OK": "yellow",
                    "Warning": "orange", "Critical": "red",
                }[tier],
            }
    return {"tier": "Critical", "label_zh": "严重", "score": score, "color_hint": "red"}


def _score_breakdown(dimensions: dict[str, dict]) -> dict[str, dict]:
    """Compute 8-dimension weighted score breakdown (v2.1).

    Each dimension: {raw, weight, contribution, findings_count,
                     active_count, archive_count}.

    v2.1 changes:
      - Use SEVERITY_PENALTY_V21 (LOW=0.5 instead of 2)
      - Cap dim raw at DIMENSION_MIN_RAW (30) — no dim can be catastrophic
      - Use configurable DEFAULT_DIMENSION_WEIGHTS (overridable via audit-config.json)
      - Separate active_findings from archive_findings
    """
    config = _load_audit_config()
    weights = config.get("dimension_weights", DEFAULT_DIMENSION_WEIGHTS)

    breakdown: dict[str, dict] = {}
    total_contribution = 0.0
    for dim_name, weight in weights.items():
        dim_data = dimensions.get(dim_name, {"findings": [], "findings_count": 0})
        all_findings = dim_data.get("findings", [])
        # Separate active from archive
        active = [f for f in all_findings if not _is_archive_finding(f)]
        archive = [f for f in all_findings if _is_archive_finding(f)]
        # Calculate raw score from ACTIVE findings only
        raw = 100.0 - sum(
            SEVERITY_PENALTY_V21.get(f.get("severity", "LOW"), 0.5) for f in active
        )
        raw = max(DIMENSION_MIN_RAW, min(100, raw))
        contribution = round(raw * weight, 2)
        total_contribution += contribution
        breakdown[dim_name] = {
            "raw": raw,
            "weight": weight,
            "contribution": contribution,
            "findings_count": len(all_findings),
            "active_count": len(active),
            "archive_count": len(archive),
        }
    breakdown["_total_weighted"] = round(total_contribution, 2)
    return breakdown


def _action_plan(findings: list[dict]) -> dict[str, list[dict]]:
    """Group findings into P0/P1/P2 priority buckets.

    P0: HIGH severity or auto_fix=rm (delete dangling references)
    P1: MED severity with auto_fix
    P2: LOW severity or no auto_fix
    """
    plan: dict[str, list[dict]] = {"P0": [], "P1": [], "P2": []}
    for f in findings:
        sev = f.get("severity", "LOW")
        auto = f.get("auto_fix")
        if sev == "HIGH" or auto == "rm":
            bucket = "P0"
        elif sev == "MED" and auto:
            bucket = "P1"
        else:
            bucket = "P2"
        plan[bucket].append({
            "severity": sev,
            "file": f.get("file"),
            "message": f.get("message"),
            "auto_fix": auto,
            "is_archive": _is_archive_finding(f),
        })
    return plan


def _archive_health(all_findings: list[dict]) -> dict:
    """v2.1: Report on archived findings separately from active health.

    Returns: {archive_count, by_severity, sample_messages, score}
    Archive score uses the same v2.1 penalty table but with no dim cap.
    """
    archive = [f for f in all_findings if _is_archive_finding(f)]
    by_sev: dict[str, int] = {}
    for f in archive:
        sev = f.get("severity", "LOW")
        by_sev[sev] = by_sev.get(sev, 0) + 1
    raw = 100.0 - sum(
        SEVERITY_PENALTY_V21.get(f.get("severity", "LOW"), 0.5) for f in archive
    )
    raw = max(0, min(100, raw))
    return {
        "total": len(archive),
        "by_severity": by_sev,
        "raw_score": round(raw, 2),
        "tier": _compute_health_tier(raw),
    }


def _detect_project_modes() -> dict[str, Any]:
    """Auto-detect current workspace project type.

    Returns: {python: bool, python_ml: bool, node: bool, ...}
    Used to scope audit findings to the right project context.
    """
    cwd = Path.cwd()
    modes: dict[str, Any] = {
        "python": False,
        "python_ml": False,
        "node": False,
        "rust": False,
        "go": False,
        "current_workspace": str(cwd),
    }
    # Python detection
    has_pyproject = (cwd / "pyproject.toml").exists()
    has_requirements = (cwd / "requirements.txt").exists()
    if has_pyproject or has_requirements:
        modes["python"] = True
        # Check for ML stack
        try:
            content = ""
            if has_pyproject:
                content = (cwd / "pyproject.toml").read_text()
            elif has_requirements:
                content = (cwd / "requirements.txt").read_text()
            ml_keywords = ("torch", "tensorflow", "jax", "transformers", "wandb", "pytorch")
            modes["python_ml"] = any(kw in content.lower() for kw in ml_keywords)
        except Exception:
            pass
    # Node detection
    if (cwd / "package.json").exists():
        modes["node"] = True
    # Rust detection
    if (cwd / "Cargo.toml").exists():
        modes["rust"] = True
    # Go detection
    if (cwd / "go.mod").exists():
        modes["go"] = True
    return modes


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="rich-audit Layer 1 mechanical scan")
    parser.add_argument("--fix", action="store_true", help="Apply safe auto-fixes")
    parser.add_argument("--filter-archive", action="store_true",
                        help="Exclude archive-*/ findings from output (cleaner noise-free report)")
    parser.add_argument("--output", type=str, default=None, help="Output JSON path")
    args = parser.parse_args()

    report = {
        "meta": {
            "tool": "rich-audit.py",
            "version": "2.2.0",
            "timestamp": now_iso(),
            "fix_mode": args.fix,
        },
        "project_modes": _detect_project_modes(),
        "dimensions": {},
    }

    dimension_funcs = [
        ("integrity", check_integrity),
        ("consistency", check_consistency),
        ("architecture", check_architecture),
        ("timeliness", check_timeliness),
        ("redundancy", check_redundancy),
        ("performance", check_performance),
        ("security", check_security),
        ("skill_health", check_skill_health),
    ]

    all_findings: list[dict] = []
    for dim_name, dim_fn in dimension_funcs:
        findings = dim_fn(report)
        # v2.1: --filter-archive option suppresses archive-path findings.
        # Archive is tracked separately in archive_health; this is purely
        # for cleaner display when user wants to focus on active drift.
        if args.filter_archive:
            findings = [f for f in findings if not _is_archive_finding(f)]
        report["dimensions"][dim_name] = {
            "findings_count": len(findings),
            "findings": findings,
        }
        all_findings.extend(findings)

    report["summary"] = {
        "total_findings": len(all_findings),
        "active_findings": sum(1 for f in all_findings if not _is_archive_finding(f)),
        "archive_findings": sum(1 for f in all_findings if _is_archive_finding(f)),
        "severity_counts": {
            "HIGH": sum(1 for f in all_findings if f["severity"] == "HIGH"),
            "MED": sum(1 for f in all_findings if f["severity"] == "MED"),
            "LOW": sum(1 for f in all_findings if f["severity"] == "LOW"),
        },
        "health_score": calculate_score(all_findings),
        "health_tier": _compute_health_tier(calculate_score(all_findings)),
        "score_breakdown": _score_breakdown(report["dimensions"]),
        "archive_health": _archive_health(all_findings),
        "action_plan": _action_plan(all_findings),
    }

    # Auto-fix pass
    if args.fix:
        fixable = [f for f in all_findings if f.get("auto_fix")]
        fixed = []
        for f in fixable:
            updated = apply_fix(f)
            fixed.append(updated)
        report["fixes_applied"] = fixed
        report["fixes_count"] = len(fixed)

        # Re-audit after fix
        if fixed:
            all_findings_after: list[dict] = []
            for dim_name, dim_fn in dimension_funcs:
                findings = dim_fn(report)
                report["dimensions"][dim_name] = {
                    "findings_count": len(findings),
                    "findings": findings,
                }
                all_findings_after.extend(findings)
            report["summary"]["health_score_after"] = calculate_score(all_findings_after)
            report["summary"]["health_tier_after"] = _compute_health_tier(
                calculate_score(all_findings_after)
            )
            report["summary"]["score_breakdown_after"] = _score_breakdown(report["dimensions"])
            report["summary"]["archive_health_after"] = _archive_health(all_findings_after)

    json_output = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(json_output)
        print(f"Report written to {args.output}")
    else:
        print(json_output)


if __name__ == "__main__":
    main()
