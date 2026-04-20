# Diting 记忆系统使用指南

## 🎯 概述

谛听 (Diting) 是一个为 AI 代理设计的热力学启发式记忆管理系统，现已配置为 MCP Server，可供 OpenClaw 使用。

## 📦 安装状态

### ✅ 已完成
- [x] Diting 项目安装 (`/root/.openclaw/workspace/projects/Diting`)
- [x] MCP 配置更新 (`/root/.openclaw/workspace/config/mcporter.json`)
- [x] Skill 创建 (`/root/.openclaw/workspace/skills/diting-memory/`)
- [x] 数据库初始化 (`diting.db`, `diting_kg.db`)

### 📊 项目状态
- **版本**: 1.0.0.0
- **测试**: 428 passed
- **覆盖率**: 80%
- **GitHub**: https://github.com/totwoto02/Diting

## 🔧 MCP 配置

Diting MCP Server 配置位置：`/root/.openclaw/workspace/config/mcporter.json`

```json
{
  "mcpServers": {
    "diting": {
      "description": "Diting (谛听) - AI 记忆的 Git + NTFS，热力学四系统记忆管理",
      "command": "python3",
      "args": ["-m", "diting.mcp_server"],
      "cwd": "/root/.openclaw/workspace/projects/Diting",
      "env": {
        "DITING_DB_PATH": "/root/.openclaw/workspace/projects/Diting/diting.db",
        "PYTHONPATH": "/root/.openclaw/workspace/projects/Diting"
      }
    }
  }
}
```

## 🛠️ 可用工具

| 工具 | 功能 | 示例 |
|------|------|------|
| `mfs_read` | 按路径读取记忆 | 读取 `/user/preferences` |
| `mfs_write` | 创建或更新记忆 | 创建新的记忆条目 |
| `mfs_search` | 按关键词搜索 | 搜索 "preferences" |
| `mfs_list` | 按类型列出记忆 | 列出所有 NOTE 类型 |

## 🌡️ 热力学四系统

### 1. 内能系统 (U - Access Count)
- **物理类比**: 物体内部的总能量
- **技术实现**: 访问次数追踪
- **公式**: `U = 基础分 + 访问次数 × 权重 + 时间衰减`

### 2. 温度系统 (T - Relevance)
- **物理类比**: 热量传递的驱动力（温差）
- **技术实现**: BM25 关联度计算
- **公式**: `T = BM25 评分 × 0.7 + 路径匹配 × 0.3`

### 3. 熵系统 (S - Controversy)
- **物理类比**: 系统的混乱程度
- **技术实现**: 矛盾检测
- **公式**: `S = 矛盾检测分数 × 权重 + 不确定性 × 权重`

### 4. 自由能系统 (G - Validity)
- **物理类比**: 系统能够做"有用功"的能量
- **技术实现**: 记忆有效性判断
- **公式**: `G = U - T × S × 100`

## 📈 记忆状态

### 热度状态
| 状态 | 热度评分 | 说明 |
|------|---------|------|
| 🔥 **热** | 70-100 | 频繁访问，高内能 |
| 🌤️ **温** | 40-69 | 中等访问频率 |
| ❄️ **冷** | 10-39 | 很少访问，低内能 |
| 🧊 **冻** | 0-9 | 明确废弃/负自由能 |

### 自由能状态
| 状态 | 自由能 | 说明 |
|------|--------|------|
| 🚀 **可提取** | G > 50 | 高有效性，优先提取 |
| ✅ **可用** | 0 < G ≤ 50 | 可被提取和使用 |
| ⚠️ **临界** | G ≈ 0 | 临界状态，可能不稳定 |
| 🔒 **抑制** | G < 0 | 自由能为负，不应提取 |

## 📁 文件结构

```
/root/.openclaw/workspace/projects/Diting/
├── diting/                 # 核心模块
│   ├── mft.py              # 主文件表
│   ├── fts5_search.py      # 全文检索
│   ├── heat_manager.py     # 热度/温度
│   ├── entropy_manager.py  # 熵系统
│   ├── free_energy_manager.py  # 自由能
│   ├── knowledge_graph.py  # 知识图谱
│   ├── wal_logger.py       # WAL 日志
│   ├── integrity_tracker.py  # 完整性追踪
│   └── mcp_server.py       # MCP 服务器
├── tests/                  # 测试
├── docs/                   # 文档
├── diting.db               # 主数据库
├── diting_kg.db            # 知识图谱数据库
└── README.md               # 项目说明
```

## 🚀 使用示例

### 通过 MCP 调用

```python
# 读取记忆
result = await mcp.call_tool("mfs_read", {
  "path": "/user/preferences"
})

# 写入记忆
result = await mcp.call_tool("mfs_write", {
  "path": "/user/preferences",
  "type": "NOTE",
  "content": "User prefers dark mode"
})

# 搜索记忆
results = await mcp.call_tool("mfs_search", {
  "query": "preferences",
  "scope": "all"
})
```

### 通过 Skill 调用

当用户提到"谛听"、"记忆管理"等关键词时，自动激活 `diting-memory` skill。

## 🔄 记忆架构

```
┌─────────────────────────────────────┐
│         AI Agent (main)             │
├─────────────────────────────────────┤
│  记忆访问层                          │
│  - memory_search (语义搜索)          │
│  - memory_get (文件读取)             │
│  - diting.mcp_server (MCP 调用)     │
├─────────────────────────────────────┤
│  存储层                              │
│  - MD 文件 (原始存储) ✅              │
│  - Diting DB (索引 + 检索增强) ✅     │
└─────────────────────────────────────┘
```

**当前设计**: MD 文件是原始存储层，Diting 是检索增强层。

## ⚠️ 注意事项

1. **MCP 配置**: 确保 `mcporter.json` 中 diting 配置正确
2. **数据库路径**: 默认为 `/root/.openclaw/workspace/projects/Diting/diting.db`
3. **环境变量**: `DITING_DB_PATH` 和 `PYTHONPATH` 必须设置
4. **长期迁移**: 未来可考虑完全迁移到 Diting DB 存储

## 🔍 验证安装

```bash
# 1. 检查 MCP 模块
cd /root/.openclaw/workspace/projects/Diting
python3 -c "import diting.mcp_server; print('✅ MCP Server 可导入')"

# 2. 检查数据库
ls -la diting.db diting_kg.db

# 3. 运行测试
pytest tests/ -q

# 4. 检查 MCP 配置
cat /root/.openclaw/workspace/config/mcporter.json | grep -A 10 '"diting"'
```

## 📚 相关文档

- [README.md](README.md) - 项目总览
- [docs/API.md](docs/API.md) - API 参考
- [docs/DEVELOPER.md](docs/DEVELOPER.md) - 开发者指南
- [docs/MCP_KG_TOOLS_USAGE.md](docs/MCP_KG_TOOLS_USAGE.md) - MCP 工具使用

## 🌐 GitHub

- **仓库**: https://github.com/totwoto02/Diting
- **Issues**: https://github.com/totwoto02/Diting/issues
- **Actions**: https://github.com/totwoto02/Diting/actions

---

*最后更新：2026-04-19*
