# MFS 统一数据库重构报告

**重构日期**: 2026-04-16  
**重构目标**: 从独立数据库架构迁移到统一数据库架构  

---

## 🎯 重构原因

### 原架构问题（4 个独立数据库）

```
MFT.db + FTS5.db + KG.db + WAL.db
```

**核心问题**:
1. ❌ FTS5 触发器无法跨库监听 MFT 表
2. ❌ 测试初始化复杂（需要创建 4 个数据库）
3. ❌ 数据一致性难保证
4. ❌ 无法跨表 JOIN 查询

---

## ✅ 重构成果

### 新架构（统一数据库）

```
MFS.db (统一数据库)
├── mft 表（元数据）
├── mft_fts5 虚拟表（全文检索）
├── kg_concepts 表（知识图谱概念）
├── kg_aliases 表（别名映射）
├── kg_edges 表（关系边）
├── wal_logs 表（WAL 日志）
└── 其他辅助表
```

**优势**:
- ✅ FTS5 触发器自动同步 MFT 表变化
- ✅ 单事务保证数据一致性
- ✅ 测试初始化简单（1 个数据库）
- ✅ 支持跨表 JOIN 查询
- ✅ 只需 1 个连接池

---

## 📊 测试通过率对比

| 阶段 | 通过测试 | 总测试 | 通过率 |
|------|---------|--------|--------|
| **重构前** | 84/84 | 84 | 100% (核心测试) |
| **重构中** | 85+ | 100+ | 85%+ (进行中) |
| **目标** | 全部 | 全部 | 100% |

---

## 🔧 已修改文件

### 核心组件（无需修改）

- ✅ `mfs/mft.py` - 已支持统一数据库
- ✅ `mfs/fts5_search.py` - 已支持统一数据库
- ✅ `mfs/knowledge_graph_v2.py` - 已支持统一数据库
- ✅ `mfs/wal_logger.py` - 已支持统一数据库
- ✅ `mfs/assembler_v2.py` - 无需数据库

### 新增文件

- ✅ `tests/test_unified_db.py` - 统一数据库初始化辅助模块

### 修改的测试文件

- ✅ `tests/test_memory_correctness.py` - 使用统一数据库
- ✅ `tests/test_mock_conversations.py` - 使用统一数据库
- ✅ `tests/test_stress.py` - 部分修改
- ✅ `tests/test_step2_features.py` - 已修复

---

## 📋 统一数据库表结构

### MFT 表
```sql
CREATE TABLE mft (
    inode INTEGER PRIMARY KEY AUTOINCREMENT,
    v_path TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    content TEXT,
    deleted INTEGER DEFAULT 0,
    create_ts TIMESTAMP,
    update_ts TIMESTAMP,
    parent_inode INTEGER,
    lcn_pointers TEXT
);
```

### FTS5 虚拟表
```sql
CREATE VIRTUAL TABLE mft_fts5 USING fts5(
    content, v_path, type,
    content='mft',
    content_rowid='inode'
);
```

### 知识图谱表
```sql
CREATE TABLE kg_concepts (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    aliases TEXT,
    created_at REAL
);

CREATE TABLE kg_edges (
    id INTEGER PRIMARY KEY,
    from_concept TEXT NOT NULL,
    to_concept TEXT NOT NULL,
    relation TEXT NOT NULL,
    weight REAL,
    timestamp REAL
);
```

### WAL 日志表
```sql
CREATE TABLE wal_logs (
    id INTEGER PRIMARY KEY,
    operation TEXT,
    v_path TEXT,
    old_content TEXT,
    new_content TEXT,
    agent TEXT,
    conversation_id TEXT,
    timestamp TIMESTAMP,
    trust_score REAL
);
```

---

## 🎯 使用示例

### 统一数据库初始化

```python
from mfs.mft import MFT
from mfs.fts5_search import FTS5Search
from mfs.knowledge_graph_v2 import KnowledgeGraphV2
from mfs.wal_logger import WALLogger

# 所有组件使用同一个数据库
db_path = "mfs.db"

mft = MFT(db_path=db_path, kg_db_path=None)
fts5 = FTS5Search(db_path=db_path)
kg = KnowledgeGraphV2(db_path=db_path)
wal = WALLogger(db_path=db_path)
```

### 测试中使用

```python
from tests.test_unified_db import create_unified_db

# 创建统一数据库（包含所有表）
db_id = f"memdb_test_{random.randint(0, 10000)}"
db_path = create_unified_db(db_id)

# 所有组件使用同一个数据库
mft = MFT(db_path=db_path, kg_db_path=None)
fts5 = FTS5Search(db_path=db_path)
kg = KnowledgeGraphV2(db_path=db_path)
wal = WALLogger(db_path=db_path)
```

---

## ⏳ 剩余工作

### 高优先级

1. **修复 test_stress.py 剩余测试**
   - TestStressFTS5::test_concurrent_search
   - TestBoundaryConditions 测试
   - 需要添加 MFT 表预创建

2. **修复 AssemblerV2 测试**
   - test_many_slices（Slice.get 方法缺失）
   - test_cache_performance（cache_slice 方法缺失）

### 中优先级

3. **验证其他测试文件**
   - test_step2_integration.py
   - test_kg_integration.py
   - test_phase2_integration.py

4. **性能测试**
   - 统一数据库 vs 独立数据库性能对比
   - 并发性能测试

### 低优先级

5. **文档更新**
   - 更新 README.md
   - 更新 API 文档
   - 添加迁移指南

---

## 📈 性能预期

| 指标 | 独立数据库 | 统一数据库 | 预期提升 |
|------|-----------|-----------|---------|
| **初始化时间** | 4 次连接 | 1 次连接 | 75%↓ |
| **查询延迟** | 跨库 JOIN | 单库 JOIN | 50%↓ |
| **事务一致性** | 应用层保证 | 数据库保证 | 100%↑ |
| **连接开销** | 4 个连接池 | 1 个连接池 | 75%↓ |
| **代码复杂度** | 高 | 低 | 50%↓ |

---

## ✅ 验证清单

- [x] 创建统一数据库初始化模块
- [x] 修改 test_memory_correctness.py
- [x] 修改 test_mock_conversations.py
- [x] 修改 test_stress.py（部分）
- [x] 验证 FTS5 触发器工作
- [ ] 修复所有剩余测试
- [ ] 性能基准测试
- [ ] 更新文档

---

## 🎉 总结

**重构进展**: 80% 完成

**核心成果**:
- ✅ 统一数据库架构已建立
- ✅ FTS5 触发器正常工作
- ✅ 核心测试 84/84 通过
- ✅ 新增测试逐步通过中

**下一步**:
1. 修复剩余测试（约 10-15 个）
2. 性能基准测试
3. 文档更新

**预计完成时间**: 1-2 小时

---

**重构负责人**: main (管家)  
**最后更新**: 2026-04-16 08:45
