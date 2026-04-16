# Phase 1 MVP 执行计划 (TDD 模式)

**阶段**: Phase 1 - 单机版 SQLite + MCP  
**目标**: 跑通"伪文件系统"概念  
**周期**: 14 天 (2026-04-13 ~ 2026-04-27)  
**负责人**: main (监督) + Copaw (开发)  
**开发模式**: TDD (Test-Driven Development)  

---

## 一、TDD 开发流程

### 1.1 TDD 核心原则

```
1. 先写测试 (Red) - 在写任何功能代码之前，先写失败的测试
2. 写最少代码让测试通过 (Green) - 只写必要的代码让测试通过
3. 重构 (Refactor) - 优化代码质量，保持测试通过
```

### 1.2 TDD 开发流程示例

```python
# Step 1: 写测试 (tests/test_mft.py)
def test_mft_create():
    mft = MFT(':memory:')
    inode = mft.create('/test/rules', 'RULE', '测试规则')
    assert inode > 0

# Step 2: 运行测试 (会失败)
pytest tests/test_mft.py -v  # ❌ FAILED

# Step 3: 写实现代码 (mfs/mft.py)
class MFT:
    def create(self, v_path, type, content):
        # 实现逻辑
        return inode

# Step 4: 运行测试 (通过)
pytest tests/test_mft.py -v  # ✅ PASSED

# Step 5: 重构
# 优化代码质量，保持测试通过
```

### 1.3 测试覆盖率要求

| 模块 | 覆盖率要求 | 测试类型 |
|------|----------|---------|
| MFT 核心 | > 80% | 单元测试 |
| MCP Server | > 70% | 集成测试 |
| 数据库 | > 60% | 单元测试 |

---

## 二、Phase 1 目标

### 2.1 核心目标

```
用最简单的方式跑通 MFS 核心概念：
- 记忆用 SQLite 存储 (不用向量库，用 LIKE 查询)
- MCP Server 暴露 3 个工具 (read/write/search)
- OpenClaw 能通过 MCP 成功读写记忆
- OpenCode 能通过 MCP 成功读写记忆
- 新开会话能准确读取之前写入的记忆
```

### 2.2 验收标准

| 指标 | 目标值 | 测试方法 |
|------|-------|---------|
| **功能** | OpenClaw 成功写入记忆 | 手动测试 |
| **功能** | OpenCode 成功写入记忆 | 手动测试 |
| **功能** | 新会话能读取记忆 | 关闭会话后重新开启测试 |
| **性能** | 读写延迟 < 100ms | 基准测试脚本 |
| **文档** | README + API 文档齐全 | 人工审查 |
| **代码** | 单元测试覆盖率 > 80% | pytest --cov |

---

## 三、Git 版本管理策略

### 3.1 分支管理

```
main         - 主分支 (稳定版本，受保护)
  └── develop    - 开发分支 (日常开发)
       ├── feature/mft       - MFT 功能分支
       ├── feature/mcp       - MCP 功能分支
       └── feature/integration - 集成测试分支
```

**分支规则**:
- `main`: 只能通过 PR 合并，每次合并必须打 tag
- `develop`: 日常开发分支，所有功能分支从此分出
- `feature/*`: 功能开发分支，开发完成后合并回 develop
- `hotfix/*`: 紧急修复分支，从 main 分出，合并回 main 和 develop

### 3.2 提交规范 (Commit Convention)

```bash
# 格式：<type>(<scope>): <subject>

# type 类型
feat:     新功能 (feature)
fix:      修复 bug
docs:     文档更新
style:    代码格式 (不影响代码运行)
refactor: 重构 (即不是新增功能，也不是修改 bug)
test:     测试相关
chore:    构建过程或辅助工具变动

# 示例
feat(mft): 添加 MFT 创建功能
fix(mcp): 修复 mfs_read 工具的错误处理
docs(readme): 更新快速开始指南
test(mft): 添加 MFT 单元测试
devops(git): 添加 Git 分支保护规则
```

### 3.3 版本标签 (Tagging)

```bash
# v0.1.0 - Phase 1 MVP 发布
git tag -a v0.1.0 -m "Phase 1 MVP: SQLite + MCP"

# v0.2.0 - Phase 2 向量 + 拼装
git tag -a v0.2.0 -m "Phase 2: Vector + Assembler"

# v1.0.0 - Phase 3 日志 + 防幻觉
git tag -a v1.0.0 -m "Phase 3: WAL + Anti-Hallucination"
```

### 3.4 回滚策略

```bash
# 回滚到上一个稳定版本
git revert HEAD

# 回滚到特定 tag
git checkout v0.1.0

# 紧急回滚 (慎用)
git reset --hard v0.1.0
```

### 3.5 GitHub Actions CI/CD

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=mfs --cov-fail-under=80
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 四、详细任务拆解 (TDD)

### Task 1: 项目初始化 (Day 1)

**负责人**: Copaw  
**监督**: main  
**预计时间**: 4 小时  

**子任务** (TDD 优先):
```
1.1 创建 Python 项目结构
    - mfs/
      - __init__.py
      - mft.py          # MFT 管理器
      - database.py     # SQLite 连接管理
      - mcp_server.py   # MCP Server 实现
      - config.py       # 配置管理
    - tests/
      - __init__.py
      - test_mft.py     # 先写测试！
      - test_mcp.py
      - conftest.py     # pytest 配置
    - requirements.txt
    - setup.py
    - README.md

1.2 配置 TDD 环境
    - Python 3.11+ 环境检查
    - 安装依赖 (sqlite3, mcp, pytest, pytest-cov)
    - 配置 pytest (pytest.ini)
    - 配置 pre-commit hooks (自动运行测试)

1.3 初始化 Git 仓库 + 版本管理
    - git init
    - 创建.gitignore (Python + IDE + 敏感文件)
    - 创建.pre-commit-config.yaml (自动测试 + 代码检查)
    - 创建.gitattributes (行尾符统一)
    - 首次 commit (initial commit)
    - 创建 main 分支
    - 创建 develop 分支 (开发分支)
    - 创建 .github/ISSUE_TEMPLATE/ (问题模板)
    - 创建 .github/PULL_REQUEST_TEMPLATE.md (PR 模板)
```

**交付物**:
- [ ] 完整的项目目录结构
- [ ] requirements.txt (含所有依赖)
- [ ] pytest.ini (TDD 配置)
- [ ] .pre-commit-config.yaml (自动测试)
- [ ] Git 仓库初始化 + 分支策略
- [ ] .github/workflows/ci.yml (CI/CD)
- [ ] .github/PULL_REQUEST_TEMPLATE.md

**验收标准**:
```bash
# TDD 环境就绪
pytest --version  # ✅ 有输出
pytest --co -q    # ✅ 列出测试用例 (即使为空)
pre-commit --version  # ✅ 有输出

# Git 版本管理就绪
git branch -a   # ✅ 显示 main + develop 分支
git log --oneline  # ✅ 至少有 1 个 commit
git remote -v   # ✅ 配置远程仓库 (如有)
```

---

### Task 2: MFT 表结构设计 (Day 2)

**负责人**: Copaw  
**监督**: main  
**预计时间**: 6 小时  

**子任务** (TDD 流程):
```
2.1 先写测试 (Red)
    - tests/test_mft.py:
      - test_create() - 测试创建记忆
      - test_read() - 测试读取记忆
      - test_update() - 测试更新记忆
      - test_delete() - 测试删除记忆
      - test_search() - 测试搜索记忆
    - 运行测试 (会失败) ❌

2.2 写实现代码 (Green)
    - db/init.sql (DDL 语句)
    - database.py (连接管理 + 初始化)
    - mft.py (MFT 管理器 + CRUD)
    - 运行测试 (通过) ✅

2.3 重构 (Refactor)
    - 优化代码结构
    - 添加类型注解
    - 改进错误处理
    - 运行测试 (保持通过) ✅

2.4 测试覆盖率检查
    - pytest --cov=mfs/mft --cov-report=html
    - 覆盖率 > 80%
```

**交付物**:
- [ ] tests/test_mft.py (先写！)
- [ ] db/init.sql (完整 DDL)
- [ ] mfs/mft.py (MFT 管理器)
- [ ] mfs/database.py (数据库连接)
- [ ] coverage.html (覆盖率报告)

**验收标准**:
```bash
# TDD 流程验证
pytest tests/test_mft.py -v  # ✅ 全部通过
pytest --cov=mfs/mft --cov-fail-under=80  # ✅ 覆盖率 > 80%
```

---

### Task 3: MCP Server 开发 - read/write (Day 3-4)

**负责人**: Copaw  
**监督**: main  
**预计时间**: 12 小时  

**子任务** (TDD 流程):
```
3.1 先写测试 (Red)
    - tests/test_mcp.py:
      - test_mfs_read() - 测试读取工具
      - test_mfs_write() - 测试写入工具
      - test_error_handling() - 测试错误处理
    - 运行测试 (会失败) ❌

3.2 学习 MCP 协议规范
    - 阅读 MCP 官方文档
    - 理解工具注册机制
    - 理解请求/响应格式

3.3 写实现代码 (Green)
    - mcp_server.py (MCP Server 实现)
    - errors.py (自定义异常)
    - 运行测试 (通过) ✅

3.4 重构 (Refactor)
    - 优化代码结构
    - 添加日志
    - 改进错误消息
    - 运行测试 (保持通过) ✅
```

**交付物**:
- [ ] tests/test_mcp.py (先写！)
- [ ] mfs/mcp_server.py (MCP Server 实现)
- [ ] mfs/errors.py (自定义异常)

**验收标准**:
```bash
# MCP 工具测试通过
pytest tests/test_mcp.py -v
pytest --cov=mfs/mcp_server --cov-fail-under=70
```

---

### Task 4: MCP Server 开发 - search (Day 5)

**负责人**: Copaw  
**监督**: main  
**预计时间**: 6 小时  

**子任务** (TDD 流程):
```
4.1 先写测试 (Red)
    - tests/test_search.py:
      - test_search_exact() - 测试精确匹配
      - test_search_fuzzy() - 测试模糊匹配
      - test_search_scope() - 测试范围过滤
    - 运行测试 (会失败) ❌

4.2 写实现代码 (Green)
    - mfs_search 工具实现
    - 运行测试 (通过) ✅

4.3 重构 (Refactor)
    - 优化搜索性能
    - 添加结果排序
    - 运行测试 (保持通过) ✅
```

**交付物**:
- [ ] tests/test_search.py (先写！)
- [ ] mfs_search 工具实现

**验收标准**:
```bash
# 搜索测试通过
pytest tests/test_search.py -v
```

---

### Task 5: 代码审查 + 修复 (Day 6-7)

**负责人**: main (审查) + Copaw (修复)  
**监督**: main  
**预计时间**: 8 小时  

**子任务**:
```
5.1 main 代码审查
    - 审查 MFT 表结构设计
    - 审查 MCP 工具实现
    - 审查错误处理
    - 审查测试覆盖率
    - 审查 Git 提交历史 (是否规范)
    - 编写 review_notes.md

5.2 Copaw 修复问题
    - 根据 review_notes 修复
    - 补充缺失的单元测试
    - 优化代码质量
    - 规范 Git 提交信息

5.3 代码质量检查
    - flake8 代码风格检查
    - mypy 类型检查
    - pytest 覆盖率检查

5.4 Git 版本管理检查
    - 检查分支是否规范 (feature/mft 等)
    - 检查提交信息是否符合规范
    - 准备 PR (Pull Request)
    - 合并到 develop 分支
```

**交付物**:
- [ ] review_notes.md (审查意见)
- [ ] 修复后的代码
- [ ] 覆盖率报告 (>80%)
- [ ] feature/* 分支 (已合并到 develop)

**验收标准**:
```bash
# 代码质量检查通过
flake8 mfs/ --max-line-length=100
mypy mfs/ --ignore-missing-imports
pytest --cov=mfs --cov-report=html --cov-fail-under=80

# Git 版本管理检查
git log --oneline --graph  # ✅ 提交历史清晰
git branch  # ✅ 分支结构清晰
```

---

### Task 6: 集成测试 (Day 8-9)

**负责人**: main + Copaw  
**监督**: main  
**预计时间**: 8 小时  

**子任务**:
```
6.1 准备测试环境
    - OpenClaw 环境检查 (已就绪)
    - OpenCode 安装 + 配置
    - 配置 MCP Server 地址
    - 准备测试数据

6.2 OpenClaw 接入测试
    - 测试 mfs_read 工具
    - 测试 mfs_write 工具
    - 测试 mfs_search 工具

6.3 OpenCode 接入测试
    - 配置 MCP Server
    - 测试写入记忆
    - 测试读取记忆
    - 测试搜索记忆

6.4 会话持久性测试
    - 写入记忆后关闭会话
    - 新开会话读取记忆
    - 验证数据一致性

6.5 性能基准测试
    - 读写延迟测试
    - 并发写入测试
    - 大数据量测试
```

**交付物**:
- [ ] tests/integration/ (集成测试脚本)
- [ ] test_report.md (测试报告)
- [ ] benchmark_results.json (性能数据)

**验收标准**:
```bash
# OpenClaw 集成测试通过
python tests/integration/test_openclaw.py

# OpenCode 集成测试通过
python tests/integration/test_opencode.py

# 性能达标
python tests/benchmark.py
# 输出：平均读写延迟 < 100ms
```

---

### Task 7: 文档编写 (Day 10-11)

**负责人**: main (主笔) + Copaw (辅助)  
**监督**: main  
**预计时间**: 8 小时  

**子任务**:
```
7.1 README.md
    - 项目介绍
    - 快速开始
    - 配置说明
    - 使用示例

7.2 API 文档
    - mfs_read 接口说明
    - mfs_write 接口说明
    - mfs_search 接口说明
    - 错误码说明

7.3 部署指南
    - 环境要求
    - 安装步骤
    - 配置 MCP
    - 常见问题

7.4 开发者文档
    - 代码结构说明
    - TDD 开发指南
    - 测试说明
```

**交付物**:
- [ ] README.md
- [ ] docs/API.md
- [ ] docs/DEPLOY.md
- [ ] docs/DEVELOPER.md

**验收标准**:
```markdown
# README 检查清单
- [ ] 项目介绍清晰
- [ ] 快速开始可执行
- [ ] 配置示例完整
- [ ] 使用示例可复现
```

---

### Task 8: 开源发布准备 (Day 12-13)

**负责人**: main + Copaw  
**监督**: main  
**预计时间**: 6 小时  

**子任务**:
```
8.1 GitHub 仓库创建
    - 创建仓库 (github.com/xxx/mfs-memory)
    - 上传代码 (git push origin main)
    - 配置 CI/CD (GitHub Actions)
    - 配置分支保护 (main 分支保护)
    - 配置 Code Owners

8.2 许可证选择
    - 选择 MIT 许可证
    - 添加 LICENSE 文件
    - 添加 COPYRIGHT 文件

8.3 发布 v0.1.0
    - 从 develop 合并到 main
    - 打 tag: git tag -a v0.1.0 -m "Phase 1 MVP"
    - 推送 tag: git push origin v0.1.0
    - 编写 Release Notes
    - 创建 GitHub Release
    - 发布到 PyPI (可选)

8.4 社区宣传
    - 编写 announcement
    - 准备社交媒体内容
    - 提交到 Hacker News / Reddit
```

**交付物**:
- [ ] GitHub 仓库 (公开)
- [ ] LICENSE 文件
- [ ] v0.1.0 Release (GitHub + PyPI)
- [ ] announcement.md
- [ ] 分支保护规则

**验收标准**:
```bash
# GitHub 仓库可访问
# https://github.com/xxx/mfs-memory

# v0.1.0 tag 已创建
git tag -l v0.1.0  # ✅ 显示 v0.1.0

# PyPI 包可安装 (可选)
pip install mfs-memory

# 分支保护已配置
# Settings -> Branches -> main branch protection
```

---

### Task 9: 缓冲时间 (Day 14)

**用途**: 应对延期/突发问题

**预留事项**:
```
- 修复集成测试发现的问题
- 补充缺失的文档
- 优化性能瓶颈
- 准备用户反馈收集
- Git 版本回滚测试 (验证可回滚性)
```

---

## 四、TDD 测试用例清单

### MFT 测试用例

```python
# tests/test_mft.py
def test_create():  # 测试创建
def test_read():  # 测试读取
def test_update():  # 测试更新
def test_delete():  # 测试删除
def test_search():  # 测试搜索
def test_search_by_path():  # 测试路径搜索
def test_search_by_type():  # 测试类型搜索
def test_concurrent_write():  # 测试并发写入
```

### MCP 测试用例

```python
# tests/test_mcp.py
def test_mfs_read():  # 测试读取工具
def test_mfs_write():  # 测试写入工具
def test_mfs_search():  # 测试搜索工具
def test_error_not_found():  # 测试文件不存在错误
def test_error_permission():  # 测试权限错误
```

### 集成测试用例

```python
# tests/integration/test_openclaw.py
def test_openclaw_write():  # OpenClaw 写入测试
def test_openclaw_read():  # OpenClaw 读取测试
def test_session_persistence():  # 会话持久性测试
```

---

## 五、每日监督机制

### 汇报时间点

| 时间 | 内容 | 负责人 |
|------|------|------|
| 早 8:00 | 昨日进度 + 今日计划 | Copaw → main |
| 晚 8:00 | 今日完成 + 问题反馈 | Copaw → main |

### 汇报模板

```markdown
## 进度汇报 (YYYY-MM-DD)

### 昨日完成
- [ ] Task X.X - 完成度 100%
- [ ] 测试用例：X 个通过 / Y 个失败

### 今日计划
- [ ] Task X.X - 预计完成度 100%
- [ ] 计划编写测试：X 个

### 遇到的问题
- 问题描述
- 已尝试的解决方案
- 是否需要 main 介入

### 测试覆盖率
- MFT: XX%
- MCP: XX%
- 总计：XX%

### 风险预警
- 🟢 正常 / 🟡 风险 / 🔴 延期
```

---

## 六、交付物清单

### 代码 (~1300 行)

| 文件 | 说明 | 行数预估 |
|------|------|---------|
| `mfs/__init__.py` | 包初始化 | 20 |
| `mfs/mft.py` | MFT 管理器 | 350 |
| `mfs/database.py` | 数据库连接 | 150 |
| `mfs/mcp_server.py` | MCP Server | 250 |
| `mfs/config.py` | 配置管理 | 50 |
| `mfs/errors.py` | 自定义异常 | 50 |
| `tests/test_mft.py` | MFT 测试 (先写！) | 250 |
| `tests/test_mcp.py` | MCP 测试 (先写！) | 200 |
| `tests/conftest.py` | pytest 配置 | 50 |
| **总计** | | **~1370 行** |

### 文档

| 文件 | 说明 |
|------|------|
| `README.md` | 项目介绍 + 快速开始 |
| `docs/API.md` | API 接口文档 |
| `docs/DEPLOY.md` | 部署指南 |
| `docs/DEVELOPER.md` | 开发者文档 (含 TDD 指南) |
| `PROJECT_PLAN.md` | 项目总计划 |
| `PHASE1_PLAN.md` | Phase 1 执行计划 |
| `PROGRESS_LOG.md` | 进度日志 |

---

## 七、风险与应对

### 技术风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|-----|------|---------|
| MCP 协议理解偏差 | 中 | 高 | main 协助审查协议文档 |
| SQLite 并发问题 | 低 | 中 | 使用 WAL 模式 + 超时重试 |
| 性能不达标 | 中 | 中 | 加 LRU 缓存 + SQL 优化 |
| OpenCode 接入失败 | 低 | 高 | 准备备用测试方案 (OpenClaw 原生) |
| TDD 进度慢 | 中 | 中 | 适当调整覆盖率要求 |

### 进度风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|-----|------|---------|
| Copaw 开发延期 | 中 | 中 | main 每日监督 + 及时介入 |
| 用户决策延迟 | 低 | 中 | 提前列出需决策事项 |
| 突发问题占用时间 | 中 | 中 | 预留 1 天缓冲时间 |

---

## 八、关键决策点

| 日期 | 决策内容 | 决策人 | 状态 |
|------|---------|-------|------|
| Day 1 | 技术栈确认 (Python + SQLite) | 用户 | ✅ 已确认 |
| Day 1 | 开发模式确认 (TDD) | 用户 | ✅ 已确认 |
| Day 2 | MFT 表结构最终版 | 用户 | ⏳ 待确认 |
| Day 5 | MCP 工具接口最终版 | 用户 | ⏳ 待确认 |
| Day 9 | 测试结果审查 | 用户 | ⏳ 待确认 |
| Day 13 | 发布前审查 | 用户 | ⏳ 待确认 |

---

## 九、成功度量

### Phase 1 成功标准

| 指标 | 目标值 | 实际值 | 状态 |
|------|-------|-------|------|
| 功能完整性 | 3 个 MCP 工具 | - | ⏳ |
| 读写延迟 | < 100ms | - | ⏳ |
| 测试覆盖率 | > 80% | - | ⏳ |
| 文档齐全 | 4 篇文档 | - | ⏳ |
| GitHub Star | > 0 (发布) | - | ⏳ |

### 长期成功标准 (参考)

| 指标 | 目标值 (1 年) |
|------|-------------|
| GitHub Star | > 1000 |
| 社区贡献者 | > 10 |
| 下游项目 | > 5 |
| 文档翻译 | > 3 种语言 |

---

## 十、附录

### A. 依赖列表

```txt
# requirements.txt
sqlite3  # Python 内置
mcp>=1.0.0  # MCP 协议
pytest>=7.0.0  # 测试框架
pytest-cov>=4.0.0  # 覆盖率
flake8>=6.0.0  # 代码风格
mypy>=1.0.0  # 类型检查
pre-commit>=3.0.0  # Git hooks
```

### B. 命令速查

```bash
# TDD 流程
pytest tests/test_xxx.py -v          # 运行测试
pytest --cov=mfs --cov-report=html   # 覆盖率报告
pytest --cov-fail-under=80           # 覆盖率检查

# 代码质量
flake8 mfs/ --max-line-length=100    # 代码风格
mypy mfs/ --ignore-missing-imports   # 类型检查

# Git hooks
pre-commit install                   # 安装 hooks
pre-commit run --all-files           # 运行所有检查

# 启动 MCP Server
python -m mfs.mcp_server

# 集成测试
python tests/integration/test_openclaw.py
python tests/integration/test_opencode.py
```

### C. 联系方式

| 角色 | 联系方式 |
|------|---------|
| main (管家) | OpenClaw 会话 |
| Copaw (开发) | sessions_spawn |
| 用户 | QQ Bot |

---

**文档版本**: v1.1 (TDD)  
**创建时间**: 2026-04-13  
**最后更新**: 2026-04-13  
**维护人**: main
