# Diting (谛听)

**DitingFS** - A Thermodynamics-Inspired Memory File System for AI Agents

**谛听文件系统** - 为 AI 代理设计的热力学启发式记忆管理系统

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 425 passed](https://img.shields.io/badge/tests-425%20passed-green.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-80%25-green.svg)]()

---

## 🦄 命名由来 / Naming Origin

**谛听**是地藏王菩萨的坐骑，能**听辨万物、识别真伪**。

**Diting** is the mount of Ksitigarbha Bodhisattva, capable of **hearing all things and distinguishing truth from falsehood**.

### 神兽特性与技术映射 / Divine Abilities & Technical Mapping

| 谛听能力 / Ability | 技术实现 / Implementation | 说明 / Description |
|----------|---------|------|
| **听 / Hear** | FTS5 全文检索 / FTS5 Full-Text Search | 聆听用户查询，快速检索记忆 / Listen to queries and retrieve memories quickly |
| **辨 / Distinguish** | 熵值计算 / Entropy Calculation | 辨别记忆争议性（熵值高低）/ Distinguish memory controversy (entropy level) |
| **真 / Truth** | WAL 审计日志 / WAL Audit Log | 真实记录，防止 AI 幻觉 / True records, prevent AI hallucination |
| **伪 / False** | 矛盾检测 / Contradiction Detection | 识别冲突记忆，标记高熵 / Identify conflicting memories, mark high entropy |

**寓意 / Philosophy:** 如谛听般辨别记忆真伪，如热力学般管理记忆能量。

Like Diting distinguishing truth from falsehood, like thermodynamics managing memory energy.

---

## 🎯 概述 / Overview

谛听 (DitingFS) 是一个为 AI 代理设计的复杂记忆管理系统，融合三大核心概念：

Diting (DitingFS) is a sophisticated memory management system designed for AI agents, integrating three core concepts:

1. **热力学四系统 / Thermodynamic Four Systems** - 能量 (U)、热度 (H)、温度 (T)、熵 (S)、自由能 (G)
2. **NTFS 文件系统架构 / NTFS File System Architecture** - MFT 主文件表、inode、虚拟路径 / MFT, inode, virtual paths
3. **防幻觉机制 / Anti-Hallucination Mechanism** - WAL 日志审计、矛盾检测、熵值判断 / WAL audit, contradiction detection, entropy judgment

### 核心特性 / Core Features

- 🔥 **热力学四系统** - 完整的能量/热度/温度/熵/自由能计算 / Complete U/H/T/S/G calculation
- 📁 **MFT 架构** - NTFS 式主文件表，支持虚拟路径管理 / NTFS-style MFT with virtual path support
- 🔍 **SQLite FTS5** - 全文检索，类 BM25 评分 / Full-text search with BM25-like scoring
- 🕸️ **知识图谱** - 自动概念提取和关系映射 / Automatic concept extraction and relationship mapping
- 🛡️ **防幻觉机制** - WAL 日志、审计追踪、回滚能力 / WAL logs, audit trails, rollback capability
- 🖼️ **多模态支持** - 图片、语音、文本，AI 生成摘要 / Image, audio, text with AI-generated summaries
- 🔒 **并发安全** - 线程安全操作，适当锁定 / Thread-safe operations with proper locking

---

## 🚀 快速开始 / Quick Start

### 安装 / Installation

```bash
# 克隆仓库 / Clone repository
git clone https://github.com/totwoto02/Diting.git
cd Diting

# 安装依赖 / Install dependencies
pip install -e .

# 运行测试 / Run tests
pytest tests/ -v
```

### 基础用法 / Basic Usage

```python
from diting.mft import MFT

# 初始化 MFT（主文件表）/ Initialize MFT (Master File Table)
mft = MFT(db_path="diting.db")

# 创建记忆 / Create memory
inode = mft.create(
    path="/user/preferences",
    type="NOTE",
    content="User prefers dark mode and concise responses"
)

# 读取记忆 / Read memory
result = mft.read("/user/preferences")
print(result["content"])

# 搜索记忆 / Search memories
results = mft.search("preferences", scope="all")
for r in results:
    print(f"Path: {r['v_path']}, Content: {r['content']}")

# 更新记忆 / Update memory
mft.update("/user/preferences", content="Updated preferences...")

# 删除记忆 / Delete memory
mft.delete("/user/preferences")
```

---

## 📚 核心概念 / Core Concepts

### 热力学类比 / Thermodynamics Analogy

| 热力学 / Thermodynamics | 谛听记忆系统 / Diting Memory System | 说明 / Description |
|--------|------------|------|
| **能量 (U) / Energy** | 访问次数 / Access Count | 记忆被访问的总次数 / Total accesses to memory |
| **热度 (H) / Heat** | 热度评分 / Heat Score | 近期访问频率 (0-100) / Recent access frequency (0-100) |
| **温度 (T) / Temperature** | 关联度 / Relevance | 与当前上下文的关联程度 / Relevance to current context |
| **熵 (S) / Entropy** | 争议性 / Controversy | 矛盾/不确定性水平 / Contradiction/uncertainty level |
| **自由能 (G) / Free Energy** | 有效性 / Validity | G = U - TS，决定记忆能否被提取 / Determines if memory can be extracted |

### 记忆状态 / Memory States

| 状态 / State | 热度评分 / Heat Score | 说明 / Description |
|------|---------|------|
| 🔥 **热 / Hot** | 70-100 | 频繁访问，高优先级 / Frequent access, high priority |
| 🌤️ **温 / Warm** | 40-69 | 中等访问频率 / Moderate access frequency |
| ❄️ **冷 / Cold** | 10-39 | 很少访问 / Rare access |
| 🧊 **冻 / Frozen** | 0-9 | 明确废弃/低有效性 / Explicitly废弃/low validity |

---

## 🔧 架构 / Architecture

```
Diting/
├── diting/
│   ├── mft.py              # 主文件表（核心）/ Master File Table (Core)
│   ├── fts5_search.py      # 全文检索 / Full-Text Search
│   ├── heat_manager.py     # 热度/温度系统 / Heat/Temperature System
│   ├── entropy_manager.py  # 熵系统 / Entropy System
│   ├── free_energy_manager.py  # 自由能计算 / Free Energy Calculation
│   ├── knowledge_graph.py  # 知识图谱 V2 / Knowledge Graph V2
│   ├── wal_logger.py       # WAL 日志（防幻觉）/ WAL Log (Anti-Hallucination)
│   ├── integrity_tracker.py  # 完整性追踪 / Integrity Tracker
│   └── ...
├── tests/
│   ├── test_mft.py
│   ├── test_fts5.py
│   ├── test_knowledge_graph.py
│   └── ...
├── docs/
│   ├── API.md
│   ├── DEVELOPER.md
│   └── ...
└── README.md
```

---

## 🧪 测试 / Testing

### 运行所有测试 / Run All Tests

```bash
pytest tests/ -v
```

### 测试覆盖率 / Test Coverage

```bash
pytest tests/ --cov=diting --cov-report=html
```

### 预期结果 / Expected Results

- ✅ **425 个测试** 通过 / tests passed
- ✅ **80% 覆盖率** / coverage
- ✅ **0 警告** / warnings

---

## 📖 文档 / Documentation

| 文档 / Document | 说明 / Description |
|------|------|
| [API.md](docs/API.md) | 完整 API 参考 / Complete API Reference |
| [DEVELOPER.md](docs/DEVELOPER.md) | 开发者指南 / Developer Guide |
| [INSTALL.md](docs/INSTALL.md) | 安装指南 / Installation Guide |
| [QUICKSTART.md](docs/QUICKSTART.md) | 快速入门 / Quick Start |

---

## 🔒 隐私与安全 / Privacy & Security

**重要 / Important**: 本项目仅用于**技术演示** / This project is for **technical demonstration** only.

- ✅ 代码库中不包含个人数据 / No personal data in codebase
- ✅ 所有测试数据使用通用示例 / All test data uses generic examples
- ✅ 配置文件（`.env`、凭证）已加入 gitignore / Config files (.env, credentials) in gitignore
- ✅ 敏感操作需要用户明确确认 / Sensitive operations require explicit user confirmation

**部署到 GitHub 前 / Before Deploying to GitHub:**
1. 审查所有文档中的个人信息 / Review all documents for personal information
2. 从测试文件中删除真实用户数据 / Remove real user data from test files
3. 确保 `.gitignore` 包含敏感文件 / Ensure .gitignore includes sensitive files
4. 使用环境变量存储凭证 / Use environment variables for credentials

---

## 🤝 MCP 集成 / MCP Integration

谛听提供 MCP（Model Context Protocol）服务器用于 AI 代理集成：

Diting provides MCP (Model Context Protocol) server for AI agent integration:

```json
{
  "mcpServers": {
    "diting": {
      "command": "python3",
      "args": ["-m", "diting.mcp_server"],
      "cwd": "/path/to/Diting",
      "env": {
        "DITING_DB_PATH": "/path/to/diting.db"
      }
    }
  }
}
```

### 可用工具 / Available Tools

- `mfs_read` - 按路径读取记忆 / Read memory by path
- `mfs_write` - 创建或更新记忆 / Create or update memory
- `mfs_search` - 按关键词搜索记忆 / Search memories by keyword
- `mfs_list` - 按类型列出记忆 / List memories by type

---

## 📊 性能 / Performance

| 操作 / Operation | 延迟 / Latency | 吞吐量 / Throughput |
|------|------|--------|
| **读取 / Read** | ~0.00ms | ~10,000 ops/s |
| **写入 / Write** | ~0.28ms | ~3,500 ops/s |
| **搜索 / Search** | ~50ms | ~20 ops/s |

*在标准硬件上测量，10K+ 记忆 / Measured on standard hardware with 10K+ memories*

---

## 🛠️ 开发 / Development

### 代码质量 / Code Quality

```bash
# 运行 linter / Run linter
ruff check diting/

# 格式化代码 / Format code
black diting/

# 运行测试 / Run tests
pytest tests/ -v
```

### Git 工作流 / Git Workflow

```bash
# 创建功能分支 / Create feature branch
git checkout -b feature/your-feature

# 提交变更 / Commit changes
git add .
git commit -m "feat: add new feature"

# 推送并创建 PR / Push and create PR
git push origin feature/your-feature
```

---

## 📝 许可证 / License

MIT License - 详见 / See [LICENSE](LICENSE)。

---

## 🙏 致谢 / Acknowledgments

- 灵感来源于 NTFS 文件系统设计 / Inspired by NTFS file system design
- 热力学原理应用于信息管理 / Thermodynamics principles applied to information management
- 为 OpenClaw AI 代理框架构建 / Built for OpenClaw AI agent framework

---

**版本 / Version**: 1.0.0.0  
**最后更新 / Last Updated**: 2026-04-18  
**维护者 / Maintainer**: [@totwoto02](https://github.com/totwoto02)
