# 本地测试指南

**目标**: 确保本地测试与 CI 流程一致，避免推送后失败

---

## 🚀 完整本地测试流程

### 1. 代码风格检查

```bash
# 使用 ruff（快速）
ruff check diting/

# 或使用 flake8（与 CI 一致）
flake8 diting/ --max-line-length=100
```

**检查项**:
- ✅ E501: 行长度不超过 100 字符
- ✅ E302: 顶部空 2 行
- ✅ E303: 不超过 3 个空行
- ✅ F401: 未使用的导入
- ✅ W292: 文件末尾换行

### 2. 运行测试

```bash
# 完整测试套件
pytest tests/ -v --tb=short

# 快速测试（跳过慢测试）
pytest tests/ -v --tb=short -m "not slow"

# 单个测试文件
pytest tests/test_mft.py -v
```

### 3. 覆盖率检查

```bash
# 生成覆盖率报告
pytest tests/ --cov=diting --cov-report=term-missing

# 确保覆盖率达标
pytest tests/ --cov=diting --cov-fail-under=80
```

### 4. Git 提交前检查清单

```bash
# ✅ 代码风格
ruff check diting/
flake8 diting/ --max-line-length=100

# ✅ 测试通过
pytest tests/ -q

# ✅ 覆盖率达标
pytest tests/ --cov=diting --cov-fail-under=80

# ✅ Git 状态
git status
git diff --stat
```

---

## 📋 Pre-commit 检查（推荐配置）

创建 `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--line-length=100]
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
```

安装:
```bash
pip install pre-commit
pre-commit install
```

---

## ⚠️ 常见错误

### E501: line too long (XXX > 100 characters)

**原因**: 行长度超过 100 字符

**修复**:
```python
# ❌ 错误（108 字符）
cursor.execute("""INSERT INTO wal_log (operation, v_path, content, source_agent, evidence, confidence, timestamp, version, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'COMMITTED')""")

# ✅ 正确（拆分到多行）
cursor.execute("""
    INSERT INTO wal_log 
    (operation, v_path, content, source_agent, 
     evidence, confidence, timestamp, version, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'COMMITTED')
""")
```

### F401: imported but unused

**原因**: 导入了未使用的模块

**修复**:
```python
# ❌ 错误
from typing import Dict, List, Optional  # Optional 未使用

# ✅ 正确
from typing import Dict, List
```

### E302: expected 2 blank lines, found 1

**原因**: 函数/类定义前缺少空行

**修复**:
```python
# ❌ 错误
import os
def foo():
    pass

# ✅ 正确
import os


def foo():
    pass
```

---

## 🔧 快速修复命令

```bash
# 自动格式化代码
ruff check diting/ --fix
black diting/

# 排序导入
isort diting/

# 检查但不修复
ruff check diting/
flake8 diting/ --max-line-length=100
```

---

## 📊 CI 检查项对照

| 检查项 | 本地命令 | CI 命令 |
|--------|---------|--------|
| **代码风格** | `flake8 diting/ --max-line-length=100` | `flake8 diting/ --max-line-length=100` |
| **单元测试** | `pytest tests/ -v` | `pytest tests/ -v --cov=diting` |
| **覆盖率** | `pytest --cov=diting --cov-fail-under=80` | `pytest --cov=diting --cov-fail-under=65` |
| **导入排序** | `ruff check diting/` | - |

---

## 🎯 推送前最终检查

```bash
# 1. 代码风格
flake8 diting/ --max-line-length=100 && echo "✅ 风格检查通过"

# 2. 测试通过
pytest tests/ -q && echo "✅ 测试通过"

# 3. 覆盖率达标
pytest tests/ --cov=diting --cov-fail-under=80 && echo "✅ 覆盖率达标"

# 4. Git 审查
git log -p -3  # 审查最近提交

# 5. 等待用户推送
# ⏸️ AI 禁止执行 git push
```

---

**最后更新**: 2026-04-18  
**维护者**: AI Assistant
