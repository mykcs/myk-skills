# Python Project Audit Checklist

> 当 rich-audit 检测到当前目录包含 Python 项目特征时（`pyproject.toml` / `requirements.txt` / `setup.py`），自动启用 Python 项目审计模块。

## 0. Project Detection

```bash
# Python project detection
[ -f "pyproject.toml" ] && echo "PYTHON_PYPROJECT" || \
[ -f "requirements.txt" ] && echo "PYTHON_REQUIREMENTS" || \
[ -f "setup.py" ] && echo "PYTHON_SETUP" || echo "NOT_PYTHON"
```

## 1. Dependency Security Check

**Goal**: No known CVEs in dependencies, no hardcoded secrets.

### 1.1 Torch Version Check (CVE Detection)

```bash
# Extract torch version
torch_version=$(python3 -c "import torch; print(torch.__version__)" 2>/dev/null || echo "NOT_INSTALLED")
echo "TORCH_VERSION: $torch_version"

# Check for known vulnerable versions
# torch < 2.5.0 has known CVEs (check PyTorch security advisories)
python3 -c "
import sys
try:
    import torch
    v = torch.__version__.split('.')
    major, minor = int(v[0]), int(v[1])
    if major < 2 or (major == 2 and minor < 5):
        print('VULNERABLE: torch < 2.5.0')
    else:
        print('OK: torch >= 2.5.0')
except:
    print('SKIP: torch not installed')
"
```

### 1.2 WandB API Key Hardcode Detection

```bash
# Scan for hardcoded wandb keys (exclude comments and test fixtures)
grep -rn "wandb.*login\|wandb\.login\|WANDB_API_KEY\|os\.environ.*wandb" \
  --include="*.py" --include="*.sh" \
  --exclude-dir=".venv" --exclude-dir="venv" --exclude-dir="node_modules" \
  | grep -v "^.*:#" | grep -v "^.*:import wandb" | grep -v "^.*:from wandb" \
  | grep -v "os\.environ.get..WANDB_API_KEY" \
  | grep -v "wandb.login()" \
  | while read line; do
    # Check if it's a real key assignment (not just import or fixture)
    if echo "$line" | grep -qE "(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,})"; then
      echo "SECRET_FOUND: $line"
    fi
  done
```

### 1.3 GitHub Token Detection

```bash
# Scan for GitHub tokens (high confidence patterns only)
grep -rn "ghp_[a-zA-Z0-9]\{36\}\|github.com.*token\|GITHUB_TOKEN" \
  --include="*.py" --include="*.sh" --include="*.json" --include="*.yaml" \
  --exclude-dir=".venv" --exclude-dir="venv" \
  | grep -v "^.*:#" | grep -v "^.*:export" \
  | while read line; do
    if echo "$line" | grep -qE "ghp_[a-zA-Z0-9]{36}"; then
      echo "SECRET_FOUND: $line"
    fi
  done
```

## 2. Dependency Version Consistency

### 2.1 Torch Version Across Projects (Cross-Reference)

```bash
# Extract torch version from pyproject.toml
grep -A2 "torch" pyproject.toml 2>/dev/null | grep "version\|index" || echo "NO_TORCH_DEPS"

# Check CUDA index consistency
grep -A5 "torch" pyproject.toml 2>/dev/null | grep -i "cu118\|cu124\|cu126" || echo "NO_CUDA_INDEX"
```

### 2.2 MarkupSafe Version Conflict

```bash
# Check for MarkupSafe upper bound (causes torch 2.6.0 install failure)
grep -i "markupsafe" pyproject.toml requirements.txt 2>/dev/null && \
python3 -c "
import tomli
try:
    with open('pyproject.toml', 'rb') as f:
        data = tomli.load(f)
    deps = data.get('project', {}).get('dependencies', [])
    for dep in deps:
        if 'markupsafe' in dep.lower():
            print(f'MARKUPSAFE_CONSTRAINT: {dep}')
except Exception as e:
    print(f'SKIP: {e}')
" 2>/dev/null || echo "NO_MARKUPSAFE_CONSTRAINT"
```

## 3. CUDA Compatibility Check

```bash
# Detect CUDA version from torch
python3 -c "
import torch
print(f'CUDA_AVAILABLE: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA_VERSION: {torch.version.cuda}')
    print(f'CUDNN_VERSION: {torch.backends.cudnn.version()}')
" 2>/dev/null || echo "CUDA_CHECK_SKIP"

# Check pyproject.toml for inconsistent CUDA indexes
grep -B2 -A2 "pytorch-cu" pyproject.toml 2>/dev/null || echo "NO_PYTORCH_CUDA_INDEX"
```

## 4. Project Completeness

### 4.1 README Quality Check

```bash
# Check for placeholder README content
if [ -f "README.md" ]; then
    # Count lines and check for placeholder
    line_count=$(wc -l < README.md)
    placeholder_count=$(grep -ci "add your description\|todo\|tbd\|placeholder" README.md 2>/dev/null || echo 0)
    echo "README_LINES: $line_count"
    echo "README_PLACEHOLDER_COUNT: $placeholder_count"
    if [ "$line_count" -lt 20 ] || [ "$placeholder_count" -gt 2 ]; then
        echo "INCOMPLETE: README needs attention"
    else
        echo "OK: README appears complete"
    fi
else
    echo "MISSING: README.md not found"
fi
```

### 4.2 Python Version Specification

```bash
# Check requires-python specification
python3 -c "
import tomli
try:
    with open('pyproject.toml', 'rb') as f:
        data = tomli.load(f)
    requires = data.get('project', {}).get('requires-python', 'NOT_SPECIFIED')
    print(f'REQUIRES_PYTHON: {requires}')
    if requires == 'NOT_SPECIFIED':
        print('WARNING: requires-python not specified')
except Exception as e:
    # Try requirements.txt
    import re
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        py_versions = re.findall(r'python[><=]{1,2}[0-9.]+', content)
        if py_versions:
            print(f'PYTHON_VERSIONS_IN_REQUIREMENTS: {py_versions}')
        else:
            print('WARNING: No python version constraint found')
    except:
        print('SKIP: No pyproject.toml or requirements.txt')
" 2>/dev/null || echo "PYTHON_VERSION_CHECK_SKIP"
```

## 5. Type Checking & Testing

### 5.1 Type Checker Configuration

```bash
# Check for pyright or mypy configuration
grep -q "tool.pyright\|tool.mypy\|tool.ruff" pyproject.toml 2>/dev/null && \
echo "TYPE_CHECKER: configured" || \
echo "TYPE_CHECKER: missing (recommend adding pyright or mypy)"

# Check for pytest configuration
grep -q "tool.pytest" pyproject.toml 2>/dev/null && \
echo "TEST_FRAMEWORK: pytest configured" || \
echo "TEST_FRAMEWORK: missing pytest configuration"
```

### 5.2 Test Directory Existence

```bash
# Check for test directories
[ -d "tests" ] || [ -d "test" ] || [ -d "_tests" ] && \
echo "TEST_DIR: found" || \
echo "TEST_DIR: missing (recommend adding tests/)"
```

## 6. Virtual Environment & Dependency Files

### 6.1 Lock File Consistency

```bash
# Check for lock files
[ -f "requirements.lock" ] && echo "LOCK_FILE: requirements.lock" || \
[ -f "pyproject.lock" ] && echo "LOCK_FILE: pyproject.lock" || \
echo "LOCK_FILE: missing (recommend using pip-compile or uv lock)"

# Check for uv configuration
[ -f "uv.lock" ] && echo "LOCK_FILE: uv.lock" || echo "NO_UV_LOCK"
```

### 6.2 Duplicate Dependencies

```bash
# Check for duplicate dependencies across files
if [ -f "pyproject.toml" ] && [ -f "requirements.txt" ]; then
    echo "WARNING: Both pyproject.toml and requirements.txt exist (potential duplication)"
fi
```

## 7. Auto-Fix Scripts

### 7.1 Empty README Template

```bash
# Replace empty README.md with template
if [ -f "README.md" ] && [ ! -s "README.md" ]; then
cat > README.md << 'README_TEMPLATE'
# Project Name

Short description of the project.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
import project_name
```

## License

MIT
README_TEMPLATE
echo "FIXED: README.md replaced with template"
fi
```

### 7.2 Generate pyright Config

```bash
# Generate pyrightconfig.json if missing
if ! grep -q "tool.pyright" pyproject.toml 2>/dev/null; then
cat > pyrightconfig.json << 'PYRIGHT_CONFIG'
{
  "include": ["src"],
  "exclude": ["**/__pycache__", "**/node_modules"],
  "pythonVersion": "3.11",
  "typeCheckingMode": "basic"
}
PYRIGHT_CONFIG
echo "FIXED: pyrightconfig.json generated"
fi
```

### 7.3 Fix MarkupSafe Constraint

```bash
# Remove problematic MarkupSafe upper bound
if grep -q "MarkupSafe.*<3.0.0" pyproject.toml 2>/dev/null; then
sed -i.bak 's/MarkupSafe>=2.1.5,<3.0.0/MarkupSafe>=2.1.5/g' pyproject.toml
echo "FIXED: MarkupSafe upper bound removed"
fi
```

### 7.4 Add requires-python

```bash
# Add requires-python if missing
if ! grep -q "requires-python" pyproject.toml 2>/dev/null; then
sed -i '/^\[project\]/a requires-python = ">=3.11"' pyproject.toml
echo "FIXED: requires-python added"
fi
```

## 8. Scoring

| Dimension | Weight | Max Score |
|-----------|--------|-----------|
| Dependency Security | 30% | 30 |
| Version Consistency | 20% | 20 |
| CUDA Compatibility | 15% | 15 |
| Project Completeness | 15% | 15 |
| Type Checking & Testing | 10% | 10 |
| Virtual Environment | 10% | 10 |
| **Total** | **100%** | **100** |

**Grade**: 90+ = PASS, 70-89 = WARN, <70 = FAIL
