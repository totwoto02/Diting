# MFS (Memory File System) 项目计划

**创建时间**: 2026-04-13  
**项目状态**: Phase 1 准备中  
**负责人**: main (管家) + Copaw (开发)  

---

## 一、项目概述

### 1.1 项目愿景

打造 **"AI 记忆的 Git + NTFS"** —— 将 NTFS 文件系统的严谨性引入 AI 记忆系统，成为 Agent 时代的基础设施级开源项目。

### 1.2 核心价值

| 当前痛点 | MFS 解决方案 |
|---------|-------------|
| 信息只存在于上下文，没落盘 | MFT 元数据强制结构化存储 |
| 上下文压缩导致失忆 | WAL 日志 + 两阶段提交 |
| 向量检索张冠李戴 | B+ Tree 语义路由树 |
| AI 胡乱修改记忆 | 证据校验 + 待审核机制 |
| 记忆碎片无法拼装 | VCN/LCN 动态拼装器 |

### 1.3 技术定位

```
对上伪装成文件系统（FUSE/MCP）
对下实现为严谨的分布式数据库（SQLite + 向量库）
```

---

## 二、架构设计

### 2.1 三层拓扑

```
┌─────────────────────────────────────────────────┐
│              Agent 层                            │
│  OpenCode │ OpenClaw │ CoPaw │ Claude Code    │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│           接口层：伪装与桥接                      │
│    FUSE 虚拟文件系统 (~/.mfs)  │  MCP Server   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│            MFS 核心引擎                          │
│  Journal Logger │ MFT Manager │ Assembler │ GC │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│            物理存储层                            │
│  SQLite/LMDB │ Qdrant/Chroma │ 本地磁盘 Blob   │
└─────────────────────────────────────────────────┘
```

### 2.2 核心组件

| 组件 | 职责 | 技术选型 |
|------|------|---------|
| **MFT Manager** | 记忆元数据管理 | SQLite + B+ Tree |
| **Journal Logger** | WAL 预写日志 | 自定义实现 |
| **Assembler** | VCN/LCN 记忆拼装 | 时间戳 + 语义排序 |
| **Garbage Collector** | 记忆碎片整理 | 定期清理 + 衰减 |

---

## 三、开发阶段

### Phase 1: MVP (单机版 SQLite + MCP)

**目标**: 跑通"伪文件系统"概念

**时间**: 7-14 天

**核心任务**:
- [ ] MFT 表结构设计与实现
- [ ] SQLite 数据库初始化
- [ ] MCP Server 开发 (mfs_read/mfs_write/mfs_search)
- [ ] OpenClaw 接入测试
- [ ] OpenCode 接入测试
- [ ] 基础文档编写

**验收标准**:
- [ ] OpenClaw 能通过 MCP 成功写入记忆
- [ ] OpenCode 能通过 MCP 成功写入记忆
- [ ] 新开会话能准确读取之前写入的记忆
- [ ] 读写延迟 < 100ms
- [ ] GitHub 仓库创建 + README 发布

**开发分工**:
- 我 (main): 任务拆解、进度监督、代码审查、文档编写
- Copaw: 核心代码开发

**成本预估**: $70-130/月 (Token 消耗)

---

### Phase 2: 引入向量与拼装 (VCN/LCN)

**目标**: 解决长文本记忆的切片与还原问题

**时间**: 4-6 周

**核心任务**:
- [ ] 文本自动切片策略 (按语义/长度/段落)
- [ ] 向量库集成 (ChromaDB 本地模式)
- [ ] MFT 指针关联 (lcn_pointers 字段)
- [ ] Assembler 动态拼装算法
- [ ] 性能优化 (LRU 缓存 + 并行捞取)

**验收标准**:
- [ ] 写入 5000 字文档，能精准召回不同段落
- [ ] 拼装后文本逻辑连贯
- [ ] 读取延迟 < 200ms

---

### Phase 3: 日志与防幻觉盾牌

**目标**: 解决 Agent"胡言乱修改记忆"的问题

**时间**: 4-6 周

**核心任务**:
- [ ] WAL 日志机制实现
- [ ] 证据校验规则引擎
- [ ] 待审核队列 + 用户确认流程
- [ ] 异常处理 + 回滚机制

**验收标准**:
- [ ] 新会话中尝试修改核心偏好，MFS 能拒绝或标记待审核
- [ ] 日志可追溯、可回滚
- [ ] 误拒绝率 < 5%

---

## 四、MFT 表结构设计

```sql
-- 记忆元数据主表
CREATE TABLE memory_mft (
    -- 核心字段
    inode INTEGER PRIMARY KEY AUTOINCREMENT,      -- 唯一记忆 ID
    v_path TEXT NOT NULL,                         -- 虚拟路径 (如 /work/projectA/rules)
    type TEXT CHECK(type IN ('FACT', 'RULE', 'EVENT', 'PREFERENCE', 'IDENTITY', 'CONSTRAINT')),
    status TEXT DEFAULT 'ACTIVE',                 -- ACTIVE, PENDING_REVIEW, ARCHIVED, MIGRATED
    version INTEGER DEFAULT 1,                    -- 乐观锁，防并发冲突
    
    -- 统计字段
    access_count INTEGER DEFAULT 0,               -- 热度统计 (类似 NTFS 最后访问时间)
    create_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modify_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 溯源字段
    source_agent TEXT,                            -- 是哪个 Agent 写入的
    source_evidence TEXT,                         -- 证据链 (来自哪次对话的哪句话)
    
    -- 存储字段
    lcn_pointers TEXT,                            -- 指向底层物理 Chunk 的指针
    content_cache TEXT,                           -- 内容缓存 (短文本直接存这里)
    
    -- 高级字段
    confidence REAL DEFAULT 1.0,                  -- 置信度 (0-1，AI 推断的记忆降低权重)
    expiration_ts TIMESTAMP,                      -- 过期时间 (某些记忆有有效期)
    dependency_inodes TEXT,                       -- 依赖关系 (如规则依赖某个事实)
    conflict_group TEXT,                          -- 冲突组 ID (互斥的记忆归为一组)
    tags TEXT,                                    -- 标签 (便于快速过滤)
    checksum TEXT,                                -- 内容校验和 (检测篡改)
    rollback_pointer TEXT                         -- 指向上一版本的指针 (支持回滚)
);

-- 索引
CREATE INDEX idx_v_path_prefix ON memory_mft(v_path TEXT PREFIX 50);
CREATE INDEX idx_status_type ON memory_mft(status, type);
CREATE INDEX idx_conflict_group ON memory_mft(conflict_group) WHERE conflict_group IS NOT NULL;
CREATE INDEX idx_create_ts ON memory_mft(create_ts);

-- WAL 日志表
CREATE TABLE memory_wal (
    log_id TEXT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operation TEXT CHECK(operation IN ('CREATE', 'UPDATE', 'DELETE', 'ARCHIVE')),
    inode INTEGER,
    old_value TEXT,
    new_value TEXT,
    source_agent TEXT,
    source_evidence TEXT,
    status TEXT CHECK(status IN ('PENDING', 'COMMITTED', 'ROLLED_BACK')),
    commit_ts TIMESTAMP,
    rollback_reason TEXT,
    FOREIGN KEY (inode) REFERENCES memory_mft(inode)
);
```

---

## 五、MCP 工具定义

### mfs_read

```python
def mfs_read(path: str) -> dict:
    """
    读取记忆文件
    
    Args:
        path: 虚拟路径 (如 /work/projectA/rules)
    
    Returns:
        {
            "success": bool,
            "content": str,
            "metadata": dict,
            "assembled_from": int  # 由多少个 Chunk 拼装
        }
    """
```

### mfs_write

```python
def mfs_write(path: str, content: str, evidence: str = "") -> dict:
    """
    写入记忆文件
    
    Args:
        path: 虚拟路径
        content: 文件内容
        evidence: 证据链 (当前对话的 Message ID 或上下文摘要)
    
    Returns:
        {
            "success": bool,
            "inode": int,
            "status": "COMMITTED" | "PENDING_REVIEW",
            "message": str
        }
    """
```

### mfs_search

```python
def mfs_search(query: str, scope: str = "/") -> dict:
    """
    在特定语义目录下搜索记忆
    
    Args:
        query: 搜索关键词
        scope: 搜索范围 (路径前缀，如 /work/projectA)
    
    Returns:
        {
            "success": bool,
            "results": [
                {
                    "path": str,
                    "type": str,
                    "snippet": str,
                    "confidence": float
                }
            ],
            "total": int
        }
    """
```

---

## 六、时间表

### Phase 1 详细排期

| Day | 任务 | 负责人 | 交付物 |
|-----|------|--------|-------|
| 1 | 项目初始化 + 任务拆解 | main | 任务清单 |
| 2-3 | MFT 表结构设计 + SQLite 实现 | Copaw | mft.py, db.py |
| 4-5 | MCP Server 开发 (read/write) | Copaw | mcp_server.py |
| 6 | mfs_search 开发 | Copaw | search.py |
| 7 | 代码审查 + 修改意见 | main | review_notes.md |
| 8-9 | 问题修复 + 单元测试 | Copaw | tests/ |
| 10 | 集成测试 (Claude Code 接入) | main + Copaw | test_report.md |
| 11-12 | 文档编写 + 开源准备 | main | README.md, docs/ |
| 13-14 | 缓冲时间 (应对延期) | - | - |

---

## 七、风险管理

### 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|-----|------|---------|
| MFT 表设计缺陷 | 中 | 高 | 预留迁移脚本，支持 schema 升级 |
| MCP 协议不兼容 | 低 | 中 | 严格遵循官方 MCP 规范 |
| 性能不达标 | 中 | 中 | 加 LRU 缓存，优化 SQL 查询 |
| Copaw 开发延期 | 中 | 中 | 我每日监督，发现卡点立即介入 |

### 生态风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|-----|------|---------|
| 用户接受度低 | 中 | 中 | 提供迁移工具，从 memory.md 自动导入 |
| 竞品抢先发布 | 低 | 高 | 加快开发节奏，6 周内发布 MVP |

---

## 八、成功标准

### Phase 1 验收标准

- [ ] Claude Code 能通过 MCP 写入记忆
- [ ] 新开会话能准确读取之前写入的记忆
- [ ] 读写延迟 < 100ms
- [ ] GitHub Star > 100 (发布后 1 个月)
- [ ] 文档齐全 (README + API 文档 + 部署指南)

### 长期成功标准 (1 年)

- [ ] GitHub Star > 1000
- [ ] 10+ 社区贡献者
- [ ] 被主流 Agent 工具原生支持
- [ ] 形成插件/扩展生态

---

## 九、相关文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 项目计划 | `projects/mfs-memory/PROJECT_PLAN.md` | 本文档 |
| 技术设计 | `projects/mfs-memory/TECH_DESIGN.md` | 详细技术设计 |
| API 文档 | `projects/mfs-memory/API.md` | MCP 工具接口文档 |
| 进度日志 | `projects/mfs-memory/PROGRESS_LOG.md` | 每日进度记录 |
| 会议纪要 | `projects/mfs-memory/MEETINGS/` | 关键决策记录 |

---

## 十、变更记录

| 日期 | 变更内容 | 负责人 |
|------|---------|-------|
| 2026-04-13 | 初始版本创建 | main |

---

**备注**: 本文档为 MFS 项目的总计划文件，所有开发工作以此为准。如有变更，需更新本文档并记录变更原因。
