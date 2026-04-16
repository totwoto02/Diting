# Phase 2: 三步走战略执行计划

**项目名称**: MFS (Memory File System) - AI 记忆的 Git + NTFS  
**阶段**: Phase 2 - 三步走战略（基于 Phase 1 成果扩展）  
**周期**: 2026-04-14 ~ 2026-05-30（约 7 周）  
**开发模式**: TDD (Test-Driven Development)  

---

## 一、Phase 1 成果回顾

### 1.1 已完成的核心功能

| 模块 | 文件 | 状态 | 说明 |
|------|------|------|------|
| **MFT 管理器** | `mfs/mft.py` | ✅ 已完成 | 记忆元数据管理，CRUD 操作 |
| **数据库** | `mfs/database.py` | ✅ 已完成 | SQLite 连接管理，初始化 |
| **MCP Server** | `mfs/mcp_server.py` | ✅ 已完成 | mfs_read/write/search 工具 |
| **配置管理** | `mfs/config.py` | ✅ 已完成 | 配置文件管理 |
| **错误处理** | `mfs/errors.py` | ✅ 已完成 | 自定义异常体系 |
| **测试套件** | `tests/*.py` (15 文件) | ✅ 已完成 | 101 测试，覆盖率 93.71% |
| **文档** | `docs/*.md` (7 文件) | ✅ 已完成 | API/部署/开发者文档 |
| **发布准备** | `setup.py`, `.github/` | ✅ 已完成 | PyPI 打包，GitHub 配置 |

### 1.2 Phase 1 测试覆盖

```
测试文件：15 个
测试用例：101 个
通过率：100%
代码覆盖率：93.71%
性能指标：
  - 读取延迟：0.00ms
  - 写入延迟：0.28ms
  - 搜索延迟：50.44ms
```

### 1.3 Phase 1 交付物

- GitHub 仓库：`github.com/xxx/mfs-memory`
- PyPI 包：`mfs-memory` (v0.1.0 准备就绪)
- 完整文档：README + API + DEPLOY + DEVELOPER

---

## 二、战略总览：三步走

| Step | 目标 | 核心功能 | 基于 Phase 1 | 时间 |
|------|------|---------|-------------|------|
| **Step 1** | **MVP 快速发布** | 自动切片 + 自动还原 + 一键安装 + 自动图谱 | ✅ 复用 MFT + MCP | 2-3 周 |
| **Step 2** | **FTS5+ 图谱完善** | FTS5 全文检索 + 拼装优化 + 防幻觉 | ✅ 扩展搜索 + 安全 | 4-6 周 |
| **Step 3** | **向量支持（预留）** | 向量检索接口（暂不执行） | ⏳ 预留接口 | 待定 |

### 定位口号

**Step 1 MVP**:
```
MFS：一键安装的全自动记忆系统
"写入即切片，读取即还原"——完整闭环，无需操作
```

**Step 2 完善**:
```
MFS：智能搜索 + 防幻觉的记忆系统
"FTS5 + 知识图谱"——精准搜索 + 智能提示
```

**Step 3 向量**:
```
MFS：专业级记忆解决方案
"向量 + FTS5"——高端环境双引擎搜索
```

---

## 三、Step 1: MVP（2-3 周）

**目标**: 吸引云服务器专业用户，让他们体验并参与开发

**核心功能**（全部自动化）:

| 功能 | 说明 | 基于 Phase 1 | 自动化程度 |
|------|------|-------------|----------|
| SQLite + MFT | 基础存储 | ✅ 复用 `mft.py` | - |
| **自动切片** | 写入时自动切片（500-2000 字） | ✅ 新增 | ✅全自动 |
| **自动还原** | 读取时自动拼装（原文还原） | ✅ 新增 | ✅全自动 |
| MCP Server | mfs_read/write/search | ✅ 扩展 `mcp_server.py` | - |
| **一键安装** | pip install + MCP 自动注册 | ✅ 完善 `setup.py` | ✅全自动 |
| **自动构建图谱** | 从记忆内容自动构建 | ✅ 新增 | ✅全自动 |

---

### Task 1.1: Phase 1 成果复用 + lcn_pointers 扩展（Week 1, Day 1-2）

**负责人**: OMO Agent  
**监督**: main  
**预计时间**: 2 天  

**子任务**:
```
1.1.1 Phase 1 代码审查
    - 审查 mft.py, database.py, mcp_server.py
    - 确认 Phase 1 测试全部通过
    - 确认 PyPI 包可安装

1.1.2 lcn_pointers 字段扩展
    - MFT 表添加 lcn_pointers 字段 (JSON 存储)
    - 每个指针包含：chunk_id, offset, length
    - 支持动态扩展

1.1.3 数据库迁移脚本
    - 从 Phase 1 schema 升级到 Phase 2 schema
    - 向后兼容 Phase 1 数据
```

**交付物**:
- `mfs/mft.py` (更新 lcn_pointers)
- `mfs/migrations/001_add_lcn_pointers.py`
- `tests/test_mft_v2.py`

**验收标准**:
- ✅ MFT 支持 lcn_pointers 字段
- ✅ Phase 1 测试全部通过
- ✅ 数据库迁移脚本可用

---

### Task 1.2: 自动切片 + 自动还原（Week 1, Day 3-5）

**负责人**: OMO Agent  
**监督**: main  
**预计时间**: 3 天  

**子任务**:
```
1.2.1 LengthSplitter 实现
    - 按长度切分 (500-2000 字)
    - 切片元数据管理 (offset, length, chunk_id)
    - 写入时自动触发切片

1.2.2 Assembler 自动还原实现
    - 按时间戳排序切片
    - 重叠部分自动去重
    - 读取时自动触发还原

1.2.3 单元测试
    - 测试 5000 字文档自动切分 → 自动还原
    - 测试还原后文本与原文 100% 一致
```

**交付物**:
- `mfs/slicers/__init__.py`
- `mfs/slicers/auto_slicer.py`
- `mfs/assembler.py`
- `tests/test_slicer.py`
- `tests/test_assembler.py`

**验收标准**:
- ✅ 写入 5000 字文档 → 自动切分 5-15 个切片
- ✅ 读取时自动还原 → 与原文 100% 一致
- ✅ 用户无需关心切片/还原过程

---

### Task 1.3: MCP Server 增强（Week 1, Day 6-7）

**负责人**: OMO Agent  
**监督**: main  
**预计时间**: 2 天  

**子任务**:
```
1.3.1 mfs_write 增强
    - 集成自动切片功能
    - 写入长文本时自动切片存储
    - 更新 lcn_pointers 字段

1.3.2 mfs_read 增强
    - 集成自动还原功能
    - 读取时自动捞取切片并拼装
    - 返回完整原文

1.3.3 mfs_search 增强
    - 基础 LIKE 搜索
    - 知识图谱扩展搜索（初步）
```

**交付物**:
- `mfs/mcp_server.py` (更新)
- `tests/test_mcp_v2.py`

**验收标准**:
- ✅ mfs_write 自动切片
- ✅ mfs_read 自动还原
- ✅ OpenClaw 能正常使用

---

### Task 1.4: 一键安装 MCP（Week 2, Day 1-2）

**负责人**: OMO Agent  
**监督**: main  
**预计时间**: 2 天  

**子任务**:
```
1.4.1 PyPI 包完善
    - 完善 setup.py 配置
    - pip install mfs-memory 一键安装

1.4.2 MCP 自动注册
    - 安装后自动生成 mcp_config.json
    - OpenClaw 自动识别 MCP Server
    - 用户无需手动配置

1.4.3 安装验证脚本
    - mfs-check-install 命令
    - 检测 MCP 是否正确注册
```

**交付物**:
- `setup.py` (完善)
- `mfs/cli/install_check.py`
- `docs/INSTALL.md`

**验收标准**:
- ✅ `pip install mfs-memory` 即可安装
- ✅ MCP 自动注册到 OpenClaw
- ✅ 用户无需手动配置

**安装流程示例**:
```bash
# 一键安装
pip install mfs-memory

# 安装验证
mfs-check-install
# 输出：✅ MFS MCP Server 已注册到 OpenClaw

# 立即使用（无需配置）
# OpenClaw 自动识别 mfs_read/mfs_write/mfs_search
```

---

### Task 1.5: 自动构建知识图谱（Week 2, Day 3-5）

**负责人**: OMO Agent  
**监督**: main  
**预计时间**: 3 天  

**子任务**:
```
1.5.1 知识图谱结构设计
    - nodes (概念节点)
    - edges (关联边)
    - weight (关联权重)

1.5.2 自动构建算法
    - 从记忆内容提取关键词 (TF-IDF)
    - 计算概念共现频率 → 关联权重
    - 写入记忆时自动更新图谱

1.5.3 图谱存储
    - knowledge_graph.json (轻量级存储)
    - 与 MFT 关联 (记录关联的记忆路径)
```

**交付物**:
- `mfs/knowledge_graph.py`
- `mfs/graph_builder.py`
- `tests/test_knowledge_graph.py`

**验收标准**:
- ✅ 写入记忆时自动提取概念
- ✅ 自动构建概念关联
- ✅ 搜索时自动扩展相关概念

**自动化流程示例**:
```
用户写入记忆：
"I love 九斤，she plays 乙女游戏，likes 柏源"

自动提取概念：
["九斤", "乙女游戏", "柏源"]

自动构建关联：
九斤 → 乙女游戏 (weight: 0.8)
乙女游戏 → 柏源 (weight: 0.7)

用户无需操作，自动完成
```

---

### Task 1.6: 集成测试 + 文档 + 发布（Week 3）

**负责人**: OMO Agent + main  
**监督**: main  
**预计时间**: 5-7 天  

**子任务**:
```
1.6.1 OpenClaw 接入测试
    - MCP 工具注册验证
    - 真实场景测试 (写入→读取→搜索)
    - 验证自动切片/自动还原闭环

1.6.2 文档编写
    - README.md (更新，添加 Phase 2 功能)
    - docs/INSTALL.md (一键安装)
    - docs/QUICKSTART.md (10 分钟入门)
    - docs/AUTO_PIPELINE.md (自动切片 - 还原闭环)

1.6.3 GitHub + PyPI 发布
    - GitHub 仓库更新
    - PyPI 包发布 (v0.2.0)
    - 技术博客 ("一键安装的记忆系统")

1.6.4 用户反馈收集
    - GitHub Issues
    - 邀请专业用户参与开发
```

**交付物**:
- `README.md` (更新)
- `docs/INSTALL.md`
- `docs/QUICKSTART.md`
- GitHub Release v0.2.0
- PyPI v0.2.0

**验收标准**:
- ✅ GitHub Star > 10 (发布后 1 周)
- ✅ 有专业用户参与开发
- ✅ 文档齐全

---

## 四、Step 2: FTS5 + 知识图谱完善方案（4-6 周）

**目标**: 普及大众，提供好用、自动化的记忆管理

**核心功能**:

| 功能 | 说明 | 优先级 |
|------|------|--------|
| FTS5 全文检索 | BM25 排序 + 中文分词 | P0 |
| 拼装还原优化 | VCN/LCN 切片拼装优化 | P0 |
| 搜索体验优化 | 搜索结果解释 + UI 优化 | P1 |
| 防幻觉盾牌 | WAL 日志 + 证据校验 | P1 |
| 性能优化 | LRU 缓存 + 并行优化 | P1 |

---

### Task 2.1: FTS5 全文检索（Week 1）

**负责人**: OMO Agent  
**监督**: main  
**预计时间**: 5-7 天  

**子任务**:
```
2.1.1 FTS5 表结构设计
    - 创建虚拟表 memory_fts
    - 中文分词配置 (porter unicode61)

2.1.2 FTS5 搜索实现
    - BM25 排序
    - 多关键词搜索
    - 短语搜索
```

**交付物**:
- `mfs/fts5_search.py`
- `tests/test_fts5.py`

**验收标准**:
- ✅ FTS5 搜索延迟 < 10ms
- ✅ BM25 排序准确

---

### Task 2.2: 知识图谱优化（Week 2-3）

**负责人**: OMO Agent  
**监督**: main  
**预计时间**: 10-14 天  

**子任务**:
```
2.2.1 知识图谱结构优化
    - 支持多层级关联
    - 支持概念别名

2.2.2 搜索扩展优化
    - 搜索关键词自动扩展
    - 同义词关联搜索
    - 显示搜索提示 ("相关概念：乙女游戏")

2.2.3 搜索结果解释
    - 解释为什么找到这条记忆
    - 显示关联路径 (知识图谱)
```

**交付物**:
- `mfs/knowledge_graph_v2.py`
- `mfs/search_enhanced.py`
- `docs/SEARCH_GUIDE.md`

**验收标准**:
- ✅ 搜索"九斤"能提示"相关概念：乙女游戏"
- ✅ 搜索结果解释清晰

---

### Task 2.3: 拼装还原优化（Week 4）

**负责人**: OMO Agent  
**监督**: main  
**预计时间**: 5-7 天  

**子任务**:
```
2.3.1 VCN/LCN 拼装优化
    - 按时间戳排序优化
    - 重叠部分去重优化
    - 逻辑连贯性检查

2.3.2 性能优化
    - LRU 缓存
    - 并行捞取切片
```

**交付物**:
- `mfs/assembler_v2.py`
- `mfs/cache.py`
- `tests/test_assembler_v2.py`

**验收标准**:
- ✅ 拼装还原准确率 > 99%
- ✅ 拼装延迟 < 50ms

---

### Task 2.4: 防幻觉盾牌（Week 5）

**负责人**: OMO Agent  
**监督**: main  
**预计时间**: 5-7 天  

**子任务**:
```
2.4.1 WAL 日志实现
    - 预写日志记录
    - 操作可追溯

2.4.2 证据校验
    - 写入时记录证据 (对话 ID)
    - 修改时校验证据

2.4.3 回滚机制
    - 支持回滚到历史版本
```

**交付物**:
- `mfs/wal_logger.py`
- `tests/test_wal.py`

**验收标准**:
- ✅ WAL 日志可追溯
- ✅ 支持回滚操作

---

### Task 2.5: 集成测试 + 文档 + Demo（Week 6）

**负责人**: OMO Agent + main  
**监督**: main  
**预计时间**: 5-7 天  

**子任务**:
```
2.5.1 集成测试
    - FTS5 搜索测试
    - 知识图谱扩展测试
    - 拼装还原测试

2.5.2 文档完善
    - docs/USER_GUIDE.md
    - docs/KNOWLEDGE_GRAPH.md
    - Demo 视频 (展示效果)

2.5.3 技术博客
    - "FTS5+ 知识图谱方案介绍"
    - 提交到 Hacker News
```

**交付物**:
- `docs/USER_GUIDE.md`
- Demo 视频
- 技术博客

**验收标准**:
- ✅ GitHub Star > 50 (发布后 1 月)
- ✅ 有大众用户使用

---

## 五、Step 3: 向量支持（预留接口，暂不执行）

**目标**: 满足不差钱的专业用户需求

**说明**: 仅预留接口定义，不实现具体功能。等 Step 2 完成后，根据用户反馈决定是否执行。

### Task 3.1: 向量接口定义（仅定义）

**负责人**: main  
**预计时间**: 1-2 天  

**子任务**:
```
3.1.1 接口文件创建
    - mfs/vector_interface.py (接口定义)
    - 定义 VectorSearch 抽象类
    - 定义 MultiSourceEmbedding 抽象类

3.1.2 配置预留
    - config.yaml (向量配置预留)
    - 文档说明 (如何启用向量)
```

**交付物**:
- `mfs/vector_interface.py`
- `docs/VECTOR_SUPPORT.md`

**⚠️ 说明**: 仅定义接口，不实现功能。

---

## 六、时间表

| Week | 任务 | 里程碑 |
|------|------|--------|
| **Week 1** | Task 1.1-1.2 | Phase 1 复用 + 自动切片/还原 |
| **Week 2** | Task 1.3-1.5 | MCP 增强 + 一键安装 + 自动图谱 |
| **Week 3** | Task 1.6 | MVP 发布 (v0.2.0) |
| **Week 4** | Task 2.1 | FTS5 全文检索 |
| **Week 5-6** | Task 2.2 | 知识图谱优化 |
| **Week 7** | Task 2.3 | 拼装还原优化 |
| **Week 8** | Task 2.4 | 防幻觉盾牌 |
| **Week 9** | Task 2.5 | Step 2 发布 (v0.3.0) |
| **待定** | Task 3.1 | 向量接口 (预留) |

---

## 七、与 Phase 1 的差异

| 维度 | Phase 1 | Phase 2 |
|------|---------|---------|
| **存储** | SQLite (LIKE 搜索) | SQLite + FTS5 |
| **切片** | 无 (整段存储) | 自动切片 (500-2000 字) |
| **还原** | 无 | 自动还原 (拼装) |
| **检索** | 关键词匹配 | FTS5 + 知识图谱扩展 |
| **安装** | 手动配置 | 一键安装 (pip install) |
| **图谱** | 无 | 自动构建知识图谱 |
| **复杂度** | 低 (MVP) | 中 (生产可用) |
| **代码量** | ~1300 行 | ~3000 行 (新增~1700 行) |

---

## 八、风险管理

### 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|-----|------|---------|
| 自动切片算法不完善 | 中 | 中 | 先实现基础版，后续优化 |
| 知识图谱构建不准确 | 中 | 中 | 支持手动修正 |
| FTS5 中文分词问题 | 低 | 中 | 使用 porter unicode61 |
| 拼装还原准确率低 | 中 | 高 | 添加校验机制 |

### 进度风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|-----|------|---------|
| MVP 开发延期 | 中 | 高 | 每日监督 + 及时介入 |
| 用户反馈少 | 高 | 中 | 主动邀请专业用户 |
| 技术博客质量低 | 中 | 中 | main 主笔 + 多次审核 |

### 市场风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|-----|------|---------|
| 目标用户群体太小 | 高 | 高 | 明确定位为"低价服务器 + 长文本" |
| 竞品已占据心智 | 高 | 高 | 快速发布 MVP，抢占定位 |
| 与 OpenClaw 原生重叠 | 高 | 中 | 差异化定位 (长文本 + 自动化) |

---

## 九、交付物清单

### Step 1 MVP 交付物

| 文件 | 说明 | 基于 Phase 1 |
|------|------|-------------|
| `mfs/mft.py` | MFT 管理器 (更新) | ✅ 扩展 lcn_pointers |
| `mfs/slicers/auto_slicer.py` | 自动切片器 | ✅ 新增 |
| `mfs/assembler.py` | 自动还原器 | ✅ 新增 |
| `mfs/mcp_server.py` | MCP Server (增强) | ✅ 扩展 |
| `mfs/knowledge_graph.py` | 知识图谱 | ✅ 新增 |
| `setup.py` | PyPI 包配置 (完善) | ✅ 完善 |
| `README.md` | 快速开始 (更新) | ✅ 更新 |
| GitHub Release v0.2.0 | 发布 | ✅ 基于 v0.1.0 |

### Step 2 完善方案交付物

| 文件 | 说明 |
|------|------|
| `mfs/fts5_search.py` | FTS5 搜索 |
| `mfs/knowledge_graph_v2.py` | 知识图谱优化 |
| `mfs/assembler_v2.py` | 拼装还原优化 |
| `mfs/wal_logger.py` | WAL 日志 |
| `docs/USER_GUIDE.md` | 用户指南 |
| Demo 视频 | 展示效果 |
| GitHub Release v0.3.0 | 发布 |

---

## 十、关键决策点

| 日期 | 决策内容 | 决策人 | 状态 |
|------|---------|-------|------|
| Day 1 | Phase 1 成果审查 | 用户 | ⏳ 待确认 |
| Week 1 | 自动切片算法确认 | 用户 | ⏳ 待确认 |
| Week 2 | 一键安装方案确认 | 用户 | ⏳ 待确认 |
| Week 3 | MVP 发布审查 | 用户 | ⏳ 待确认 |
| Week 6 | Step 2 发布审查 | 用户 | ⏳ 待确认 |
| 待定 | Step 3 向量支持执行决策 | 用户 | ⏳ 待定 |

---

## 十一、附录：命令速查

```bash
# Step 1 MVP 安装
pip install mfs-memory

# 安装验证
mfs-check-install

# 运行测试
pytest tests/ -v

# 生成覆盖率报告
pytest --cov=mfs --cov-report=html --cov-fail-under=80

# 启动 MCP Server
python -m mfs.mcp_server
```

---

**文档版本**: v2.0 (三步走战略，基于 Phase 1 扩展)  
**创建时间**: 2026-04-14  
**最后更新**: 2026-04-14  
**维护人**: main
