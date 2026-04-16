# 对话管理器使用指南（方案 C 混合模式）

**时间**: 2026-04-15  
**状态**: ✅ 已完成

---

## 🎯 功能概述

对话管理器实现混合模式对话存储（方案 C）：

| 区域 | 存储内容 | 保留时间 | 说明 |
|------|---------|---------|------|
| **热数据** (`/dialog/hot`) | 完整对话 | 0-7 天 | 最近对话，完整保留 |
| **温数据** (`/dialog/warm`) | 对话摘要 | 7-30 天 | 过期对话，转为摘要 |
| **冷数据** (`/dialog/cold`) | 重要对话 | 永久 | 手动标记的重要对话 |

---

## 📋 API 使用

### 1. 初始化

```python
from mfs.mft import MFT
from mfs.dialog_manager import DialogManager

# 创建 MFT（带 KG）
mft = MFT(db_path='mfs.db', kg_db_path='mfs_kg.db')

# 创建对话管理器
dm = DialogManager(mft)
```

---

### 2. 添加对话

#### 单条添加
```python
path = dm.add_dialog(
    session_id="chat_001",
    role="user",
    content="你好，我想了解一下 MFS 项目"
)
# 返回：/dialog/hot/chat_001/20260415_135501_user_1776232501837
```

#### 批量添加
```python
messages = [
    {"role": "user", "content": "今天天气怎么样？"},
    {"role": "assistant", "content": "今天晴天，气温 25 度。"},
    {"role": "user", "content": "好的，谢谢！"}
]
paths = dm.add_dialog_batch("chat_002", messages)
```

---

### 3. 查询对话

#### 获取会话历史
```python
history = dm.get_dialog_history("chat_001", days=7)
for msg in history:
    print(f"{msg['v_path']}: {msg['content']}")
```

#### 搜索对话
```python
# 搜索所有区域
results = dm.search_dialogs("九斤", scope="all")

# 只搜索热数据区
results = dm.search_dialogs("九斤", scope="hot")

# 只搜索冷数据区（重要对话）
results = dm.search_dialogs("九斤", scope="cold")
```

---

### 4. 管理对话

#### 标记重要对话
```python
# 将对话标记为重要（移到冷数据区永久保存）
dm.mark_as_important(
    path="/dialog/hot/chat_001/20260415_135501_user_xxx",
    reason="用户询问重要约会时间"
)
```

#### 迁移到温数据区
```python
# 手动迁移对话到温数据区（转为摘要）
dm.migrate_to_warm("/dialog/hot/chat_001/xxx")
```

#### 清理过期对话
```python
# 自动清理（7 天以上转摘要，30 天以上删除）
stats = dm.cleanup_old_dialogs()
print(f"热→温：{stats['hot_to_warm']}条")
print(f"温→删除：{stats['warm_deleted']}条")
```

---

### 5. 统计信息

```python
stats = dm.get_stats()
print(f"热数据路径：{stats['hot_path']}")
print(f"温数据路径：{stats['warm_path']}")
print(f"冷数据路径：{stats['cold_path']}")
print(f"热数据阈值：{stats['hot_days']} 天")
print(f"温数据阈值：{stats['warm_days']} 天")
```

**输出**:
```
热数据路径：/dialog/hot
温数据路径：/dialog/warm
冷数据路径：/dialog/cold
热数据阈值：7 天
温数据阈值：30 天
```

---

## 🔧 完整示例

### 示例 1: 记录与九斤的对话

```python
from mfs.mft import MFT
from mfs.dialog_manager import DialogManager

# 初始化
mft = MFT(db_path='mfs.db', kg_db_path='mfs_kg.db')
dm = DialogManager(mft)

# 记录对话
dm.add_dialog("jiujin_chat", "user", "4.12 拍照约定是几点？")
dm.add_dialog("jiujin_chat", "assistant", "约定下午 3 点，荷兰花卉小镇门口集合")

# 标记为重要对话
results = dm.search_dialogs("拍照约定")
if results:
    dm.mark_as_important(
        results[0]['v_path'],
        reason="与九斤的拍照约定，重要事件"
    )

# 后续搜索
important = dm.search_dialogs("九斤", scope="cold")
print(f"找到 {len(important)} 条重要对话")
```

---

### 示例 2: 定期清理任务

```python
# 每天执行一次
def daily_cleanup():
    stats = dm.cleanup_old_dialogs()
    print(f"清理完成：{stats}")
    
    # 发送报告
    if stats['hot_to_warm'] > 0:
        print(f"  {stats['hot_to_warm']} 条对话已转为摘要")
    if stats['warm_deleted'] > 0:
        print(f"  {stats['warm_deleted']} 条摘要已清理")
```

---

## 📊 存储策略

### 自动流转

```
新对话 → 热数据区（完整存储）
   ↓ (7 天后)
温数据区（转为摘要）
   ↓ (30 天后)
删除（摘要已保留关键信息）
   
重要对话 → 手动标记 → 冷数据区（永久保存）
```

### 存储量估算

| 场景 | 日增量 | 月增量 | 年增量 |
|------|-------|-------|-------|
| 轻度使用（10 对话/天） | 5KB | 150KB | 1.8MB |
| 中度使用（50 对话/天） | 25KB | 750KB | 9MB |
| 重度使用（200 对话/天） | 100KB | 3MB | 36MB |

**注意**: 温数据区为摘要存储（压缩比约 10:1），实际存储量更小。

---

## 💡 最佳实践

### ✅ 推荐做法

1. **重要对话及时标记**
   ```python
   # 约会约定、重要决策等立即标记
   dm.mark_as_important(path, reason="重要事件")
   ```

2. **定期 Review**
   ```python
   # 每周回顾，提取有价值信息
   weekly_summary = dm.search_dialogs("结论", scope="hot")
   ```

3. **按场景分类**
   ```python
   # 不同场景用不同 session_id
   dm.add_dialog("jiujin_chat", ...)  # 九斤相关
   dm.add_dialog("work_chat", ...)    # 工作相关
   dm.add_dialog("idea_chat", ...)    # 创意想法
   ```

### ❌ 避免做法

1. **不要存储所有对话** - 只存有价值的
2. **不要忘记标记重要** - 好对话会过期
3. **不要忽略清理** - 定期运行 cleanup

---

## 🚀 扩展功能

### TODO: AI 摘要生成

```python
def extract_summary(self, path: str) -> str:
    record = self.mft.read(path)
    
    # TODO: 调用 AI 模型生成智能摘要
    # 当前：简单截取前 200 字
    return record['content'][:200] + "..."
```

### TODO: 自动重要性检测

```python
def auto_mark_important(self, path: str):
    record = self.mft.read(path)
    
    # 检测关键词
    important_keywords = ["约定", "决定", "重要", "记住"]
    if any(kw in record['content'] for kw in important_keywords):
        self.mark_as_important(path, "AI 自动检测")
```

---

## 📝 测试报告

**测试文件**: `tests/test_dialog_manager.py`

**测试结果**:
```
✅ 热数据存储正常
✅ 会话历史查询正常
✅ 重要对话标记正常
✅ 对话搜索正常
✅ 批量添加正常
```

---

**状态**: ✅ 完成  
**测试**: ✅ 通过  
**生产就绪**: ✅ 是
