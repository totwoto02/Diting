# Diting Skill - 记忆管理系统

> Diting (谛听) - AI 代理记忆管理系统
> 
> 支持语义搜索、知识图谱、多模态记忆、WAL 防幻觉盾牌

---

## 📦 初次安装引导

### 前置条件

- Python 3.11+
- SQLite3 (Python 内置)
- pip 或 uv 包管理器

### 安装步骤

```bash
# 1. 进入项目目录
cd /root/.openclaw/workspace/projects/Diting

# 2. 安装依赖
pip install -e .

# 或 uv
uv pip install -e .

# 3. 验证安装
python -c "from diting.mft import MFT; print('✅ Diting 安装成功')"

# 4. 初始化数据库（首次运行自动创建）
python -c "from diting.mft import MFT; mft = MFT(); print('✅ 数据库初始化成功')"
```

### 目录结构

```
Diting/
├── diting/                 # 核心模块
│   ├── mft.py             # 记忆文件树（核心）
│   ├── knowledge_graph.py # 知识图谱
│   ├── wal_logger.py      # WAL 防幻觉盾牌
│   ├── mcp_server.py      # MCP 服务器
│   └── ...
├── tests/                  # 测试用例
├── setup.py               # 安装配置
└── README.md              # 项目文档
```

---

## 🎯 核心功能

### 1. 记忆文件树 (MFT)

**虚拟文件系统**，支持：
- 树状路径结构 (`/category/subcategory/name`)
- 多种文件类型 (`NOTE`, `RULE`, `CODE`, `CONVERSATION`)
- 语义搜索 + FTS5 全文检索
- 版本历史追踪

**基本用法**：
```python
from diting.mft import MFT

mft = MFT(db_path="diting.db")

# 创建记忆
mft.create("/test/note1", "NOTE", "这是测试笔记")

# 读取记忆
record = mft.read("/test/note1")
print(record["content"])

# 搜索记忆
results = mft.search("测试", scope="/test")

# 更新记忆
mft.update("/test/note1", content="更新后的内容")

# 删除记忆
mft.delete("/test/note1")
```

### 2. 知识图谱 (KG)

**实体关系网络**，支持：
- 实体提取与存储
- 关系建模（父子、引用、相关）
- 图谱遍历与查询

**基本用法**：
```python
from diting.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph(db_path="diting_kg.db")

# 创建实体
kg.create_entity("user", "用户", {"name": "张三"})
kg.create_entity("project", "项目", {"name": "Diting"})

# 创建关系
kg.create_relation("user", "project", "WORKS_ON")

# 查询实体
entity = kg.get_entity("user")

# 查询关系
relations = kg.get_relations("user")
```

### 3. WAL 防幻觉盾牌

**操作审计追踪**，支持：
- 所有修改操作记录
- 证据链存储
- 回滚能力
- 置信度评分

**基本用法**：
```python
from diting.wal_logger import WALLogger

wal = WALLogger(db_path="diting_wal.db")

# 记录操作
record_id = wal.log_operation(
    operation="CREATE",
    v_path="/test/doc",
    content="内容",
    source_agent="main",
    evidence="conversation_123",
    confidence=1.0
)

# 查看历史
history = wal.get_history("/test/doc")

# 回滚操作
wal.rollback(record_id)

# 获取最新版本
latest = wal.get_latest_version("/test/doc")
```

### 4. 对话管理器

**混合模式对话存储**：
- 热数据：0-7 天，完整存储
- 温数据：7-30 天，摘要存储
- 冷数据：重要对话，永久保存

**基本用法**：
```python
from diting.dialog_manager import DialogManager
from diting.mft import MFT

mft = MFT()
dialog_mgr = DialogManager(mft)

# 添加对话
dialog_mgr.add_dialog("session1", "user", "你好")
dialog_mgr.add_dialog("session1", "assistant", "你好！有什么可以帮助你的？")

# 批量添加
messages = [
    {"role": "user", "content": "问题"},
    {"role": "assistant", "content": "回答"}
]
dialog_mgr.add_dialog_batch("session1", messages)

# 标记重要
dialog_mgr.mark_as_important("/dialog/hot/session1/msg", reason="重要信息")

# 搜索对话
results = dialog_mgr.search_dialogs("关键词")

# 获取历史
history = dialog_mgr.get_dialog_history("session1")
```

### 5. MCP 服务器

**AI 工具集成**，暴露 3 个工具：
- `diting_read` - 读取记忆
- `diting_write` - 写入记忆
- `diting_search` - 搜索记忆

**启动方式**：
```bash
# 直接运行
python -m diting.mcp_server

# 或作为模块
from diting.mcp_server import MCPServer
server = MCPServer(db_path="diting.db")
```

---

## 📋 使用规范

### 路径命名规范

| 路径前缀 | 用途 | 示例 |
|---------|------|------|
| `/conversations/` | 对话记录 | `/conversations/2026-04/20260420_session1` |
| `/rules/` | 规则配置 | `/rules/coding/python_style` |
| `/notes/` | 普通笔记 | `/notes/project_ideas` |
| `/code/` | 代码片段 | `/code/utils/string_helpers` |
| `/knowledge/` | 知识库 | `/knowledge/ai/transformer` |
| `/temp/` | 临时文件 | `/temp/cache_001` |

### 文件类型规范

| 类型 | 用途 | 内容格式 |
|------|------|---------|
| `NOTE` | 普通笔记 | 纯文本/Markdown |
| `RULE` | 规则配置 | YAML/JSON |
| `CODE` | 代码片段 | 编程语言源码 |
| `CONVERSATION` | 对话记录 | JSON 结构化 |
| `KNOWLEDGE` | 知识条目 | Markdown + 元数据 |

### 元数据规范

```python
metadata = {
    "status": "active",      # active/archived/deleted
    "tags": ["tag1", "tag2"], # 标签列表
    "source": "user_input",   # 来源
    "confidence": 1.0,        # 置信度 0-1
    "created_by": "main",     # 创建者
    "version": 1              # 版本号
}
```

### 最佳实践

1. **路径设计**：
   - ✅ `/project/module/type_name`
   - ❌ `/随便/写/什么`

2. **内容组织**：
   - 相关记忆放在同一路径下
   - 使用标签进行跨分类关联
   - 定期清理 `/temp/` 临时文件

3. **搜索优化**：
   - 使用 `scope` 参数限定搜索范围
   - 利用 FTS5 全文检索
   - 结合知识图谱进行关联查询

4. **性能考虑**：
   - 批量操作使用 `batch_create`
   - 定期清理过期数据
   - 使用 WAL 日志追踪关键操作

---

## 🔧 高级功能

### 批量处理

```python
from diting.batch_processor import BatchProcessor

processor = BatchProcessor(db_path="diting_batch.db")

# 入队任务
task_id = processor.enqueue("memory_export", {"paths": ["/test/*"]})

# 获取队列状态
status = processor.get_queue_status()

# 停止处理
processor.stop()
```

### 监控告警

```python
from diting.monitor import MonitorDashboard

monitor = MonitorDashboard(db_path="diting_monitor.db")

# 获取系统状态
status = monitor.get_system_status()
print(f"CPU: {status['system']['cpu_percent']}%")

# 记录指标
monitor.record_metric("memory_count", 100)

# 检查告警
alerts = monitor.check_alerts()
```

### 多模态支持

```python
from diting.multimodal_manager import MultimodalManager

mm = MultimodalManager()

# 处理图片
image_info = mm.process_image("/path/to/image.jpg")

# 处理音频
audio_transcript = mm.process_audio("/path/to/audio.ogg")

# 提取元数据
metadata = mm.extract_metadata("/path/to/file")
```

---

## 🧪 测试覆盖率

当前测试覆盖率：**85%**

| 模块 | 覆盖率 | 测试文件 |
|------|--------|---------|
| wal_logger.py | 100% | test_wal_logger.py |
| dialog_manager.py | 100% | test_dialog_manager.py |
| assembler_v2.py | 99% | test_assembler_v2.py |
| cache.py | 95% | - |
| knowledge_graph_v2.py | 94% | - |

运行测试：
```bash
cd /root/.openclaw/workspace/projects/Diting
pytest --cov=diting --cov-report=term-missing
```

---

## 📚 相关文档

- [README.md](./README.md) - 项目概述
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 架构设计
- [API.md](./API.md) - API 参考
- [CHANGELOG.md](./CHANGELOG.md) - 变更日志

---

## 🆘 常见问题

### Q: 数据库文件在哪里？
A: 默认在 `~/.openclaw/workspace/projects/Diting/diting.db`，可通过 `db_path` 参数自定义。

### Q: 如何备份记忆数据？
A: 直接复制 `.db` 文件即可，SQLite 支持热备份。

### Q: WAL 日志有什么用？
A: 记录所有修改操作，支持回滚和审计追踪，防止 AI 幻觉。

### Q: 知识图谱和 MFT 有什么区别？
A: MFT 是树状文件系统，KG 是网状关系图。MFT 适合层级存储，KG 适合关联查询。

### Q: 如何迁移旧版本数据？
A: 使用 `diting/migrations/` 下的迁移脚本自动升级。

---

*最后更新：2026-04-20*
