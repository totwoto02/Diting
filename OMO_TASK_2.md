# OMO Task 2 开发任务包

**任务**: MFT 表结构设计完善  
**执行者**: OMO Agent (OpenCode + 通义灵码)  
**模型**: qwen-coder-plus (代码生成能力强)  
**预计时间**: 2-3 小时  

---

## 任务背景

MFS (Memory File System) Phase 1 Task 1 已完成：
- ✅ 32 个测试全部通过 (88% 覆盖率)
- ✅ Git 仓库初始化 (main + develop 分支)
- ✅ 项目结构完整

现在继续执行 Task 2。

---

## Task 2: MFT 表结构设计完善

### 子任务

#### 1. 完善 MFT 表结构 (30 分钟)

**文件**: `mfs/mft.py`, `mfs/database.py`

**任务**:
- [ ] 添加更多索引 (path/type/status)
- [ ] 优化查询性能
- [ ] 添加约束检查

**示例**:
```sql
-- 添加索引
CREATE INDEX idx_mft_path ON memory_mft(v_path);
CREATE INDEX idx_mft_type ON memory_mft(type);
CREATE INDEX idx_mft_status ON memory_mft(status);
CREATE INDEX idx_mft_create_ts ON memory_mft(create_ts);
```

#### 2. 添加并发写入测试 (30 分钟)

**文件**: `tests/test_concurrent.py`

**任务**:
- [ ] test_concurrent_write - 并发写入测试
- [ ] test_transaction_rollback - 事务回滚测试
- [ ] test_lock_mechanism - 锁机制测试

**示例**:
```python
def test_concurrent_write():
    # 多个线程同时写入
    # 验证无冲突
    pass
```

#### 3. 优化搜索性能 (30 分钟)

**文件**: `mfs/mft.py`

**任务**:
- [ ] 添加全文搜索支持 (FTS5)
- [ ] 优化 LIKE 查询
- [ ] 添加 LRU 缓存机制

#### 4. 代码质量改进 (30 分钟)

**文件**: `mfs/*.py`

**任务**:
- [ ] 添加类型注解
- [ ] 改进错误处理
- [ ] 优化日志记录

---

## 验收标准

```bash
# 1. 所有测试通过
pytest tests/ -v

# 2. 新增并发测试
pytest tests/test_concurrent.py -v

# 3. 测试覆盖率 > 90%
pytest --cov=mfs --cov-fail-under=90

# 4. 代码质量检查
flake8 mfs/ --max-line-length=100
mypy mfs/ --ignore-missing-imports
```

---

## Git 提交规范

**分支**: develop (或 feature/mft-perf)

**提交格式**:
```bash
feat(mft): 添加并发写入支持
test(mft): 添加并发测试用例
perf(mft): 优化搜索性能
style(mft): 添加类型注解
```

---

## 开发环境

**OpenCode 配置**:
- 通义灵码 (代码补全)
- 豆包 Code (对话辅助)

**Python**: 3.11.6  
**pytest**: 9.0.3  
**SQLite**: 内置  

---

## 参考文档

1. `PHASE1_PLAN.md` - Phase 1 详细计划
2. `docs/GIT_WORKFLOW.md` - Git 工作流指南
3. `PROGRESS_LOG.md` - 进度日志
4. `CHANGE_RECORD.md` - 方案调整记录

---

## 联系方式

**监督**: main (管家)  
**汇报频率**: 每 2 小时  
**问题反馈**: PROGRESS_LOG.md  

---

**开始时间**: 2026-04-13 17:43  
**预计完成**: 2026-04-13 20:00  

**现在立即开始！**
