# Task 5 失败教训总结

**创建时间**: 2026-04-13 20:55  
**任务**: MFS Phase 1 Task 5: 文档编写  
**状态**: ⚠️ 启动失败 3 次，最终成功

---

## 一、失败经过

### 第一次尝试 (20:30)

```
sessions_spawn 调用
status: error
error: invalid agent params: unknown channel: qqbot
```

**错误原因**: sessions_spawn 参数错误

### 第二次尝试 (20:50)

```
sessions_spawn 调用 (简化参数)
status: error
error: invalid agent params: unknown channel: qqbot
```

**错误原因**: 同样的错误，未找到根本原因

### 第三次尝试 (20:50)

```
sessions_spawn 调用 (再次简化参数)
status: error
error: invalid agent params: unknown channel: qqbot
```

**错误原因**: 仍然未找到根本原因

### 第四次尝试 (20:50)

```
sessions_spawn 调用 (按照 Task 4 的方法)
status: accepted ✅
```

**成功原因**: 完全复制 Task 4 的成功参数

---

## 二、根本原因分析

### 错误信息解读

```
invalid agent params: unknown channel: qqbot
```

**含义**: `sessions_spawn` 工具在 qqbot channel 上不可用或不支持

### 为什么 Task 4 成功了？

**Task 4 启动时间**: 20:06  
**Task 4 启动状态**: ✅ accepted

**对比分析**:
| 项目 | Task 4 | Task 5 (失败) | Task 5 (成功) |
|------|-------|--------------|--------------|
| 启动时间 | 20:06 | 20:30 | 20:50 |
| 状态 | accepted | error | accepted |
| 参数 | 标准 | 简化 | 标准 |
| channel | qqbot | qqbot | qqbot |

**结论**: Task 4 和 Task 5 都使用相同的 channel (qqbot)，但 Task 4 成功了。说明 **sessions_spawn 在 qqbot channel 是可用的**，问题在于参数配置。

### 真正的失败原因

1. **第一次失败**: 参数可能有问题 (task 描述过长或格式问题)
2. **第二次失败**: 继续尝试错误的参数组合
3. **第三次失败**: 仍未找到正确方法
4. **第四次成功**: 完全复制 Task 4 的成功参数

**核心教训**: **不要尝试"创新"参数，应该复制已成功的参数格式**

---

## 三、正确使用 OpenCode+OMO 的方法

### 3.1 sessions_spawn 参数规范

**标准参数** (已验证可用):

```python
sessions_spawn(
    task="任务描述...",           # 必需：清晰简洁
    mode="run",                   # 必需：run 或 session
    label="任务标签",             # 必需：唯一标识
    cleanup="keep",               # 推荐：keep 或 delete
)
```

**可选参数**:
- `runTimeoutSeconds`: 超时时间 (秒)
- `thread`: 是否线程绑定 (true/false)
- `sandbox`: 沙箱模式 (inherit/require)

**不要使用的参数**:
- ❌ `channel`: 不要手动指定 channel
- ❌ `accountId`: 不要手动指定 accountId
- ❌ 其他未文档化的参数

### 3.2 Task 描述最佳实践

**好的 Task 描述**:
```markdown
# MFS Phase 1 Task 5: 文档编写

## 项目位置
`/root/.openclaw/workspace/projects/mfs-memory/`

## 任务目标
编写完整的用户文档和开发者文档。

## 子任务
1. README.md 完善 (30 分钟)
   - 项目介绍和特性
   - 快速开始指南

2. API 文档编写 (30 分钟)
   - 创建 docs/API.md
   - mfs_read/write/search 接口说明

## 验收标准
```bash
ls -la README.md docs/*.md
```

## 汇报要求
- 每完成一个子任务汇报进度
- 完成后提交总结报告

**现在立即开始执行！**
```

**不好的 Task 描述**:
```markdown
# Task 5

做文档编写工作，包括 README、API 文档等。
快点开始！
```

### 3.3 启动流程

**正确流程**:
```
1. 准备任务描述 (参考 Task 4 格式)
   ↓
2. 调用 sessions_spawn (标准参数)
   ↓
3. 检查返回状态
   ↓
   ├─ accepted ✅ → 等待完成通知
   └─ error ❌ → 检查错误信息
       ↓
       如果是 "unknown channel" → 复制 Task 4 参数
       如果是其他错误 → 分析并修正
```

### 3.4 错误处理流程

**错误类型 1**: `invalid agent params: unknown channel`

**解决方案**:
1. 不要添加 channel 参数
2. 完全复制 Task 4 的参数格式
3. 确保 task 描述使用标准 Markdown 格式

**错误类型 2**: `timeout`

**解决方案**:
1. 添加 `runTimeoutSeconds=3600` (1 小时)
2. 或者拆分任务为更小的子任务

**错误类型 3**: `no response`

**解决方案**:
1. 等待更长时间 (OMO Agent 可能需要时间启动)
2. 检查 subagents list 确认状态

---

## 四、最佳实践总结

### 4.1 参数配置

| 参数 | 推荐值 | 说明 |
|------|-------|------|
| mode | "run" | 一次性任务用 run，持续任务用 session |
| label | "MFS-TaskX-描述" | 唯一标识，便于追踪 |
| cleanup | "keep" | 保留 session 记录 |
| runTimeoutSeconds | 3600 | 1 小时超时 (可选) |

### 4.2 Task 描述格式

**必需章节**:
1. 项目位置
2. 任务目标
3. 子任务列表 (带时间估算)
4. 验收标准
5. 汇报要求

**推荐格式**:
```markdown
# MFS Phase 1 Task X: 任务名称

## 项目位置
`/path/to/project`

## 任务目标
简要描述任务目标。

## 子任务
1. 子任务 1 (时间估算)
   - 具体内容
2. 子任务 2 (时间估算)
   - 具体内容

## 验收标准
```bash
# 验收命令
```

## 汇报要求
- 每完成一个子任务汇报进度
- 遇到问题立即汇报
- 完成后提交总结报告

**现在立即开始执行！**
```

### 4.3 启动检查清单

启动前检查:
- [ ] Task 描述格式正确
- [ ] 参数使用标准配置
- [ ] label 唯一且描述性
- [ ] 项目位置正确
- [ ] 验收标准明确

启动后检查:
- [ ] status 为 "accepted"
- [ ] 获取 childSessionKey
- [ ] 记录 runId
- [ ] 更新 PROGRESS_LOG.md

---

## 五、教训应用

### 5.1 已更新文档

- ✅ SOUL.md - 工具使用规范
- ✅ EDIT_WORKFLOW.md - Edit 正确流程
- ✅ LESSONS_EDIT_TOOL.md - Edit 失败教训
- ✅ **LESSONS_OPENAME_OMO.md** (本文档) - OMO 使用教训

### 5.2 已固化流程

**OMO Agent 启动流程**:
```
1. 参考 Task 4 的成功参数
2. 使用标准 sessions_spawn 参数
3. 检查返回状态
4. 记录 session 信息
5. 更新进度日志
```

### 5.3 未来改进

1. **创建 Task 模板** - 标准化 Task 描述格式
2. **参数检查脚本** - 自动验证参数正确性
3. **错误处理手册** - 收集常见错误和解决方案

---

## 六、总结

### 核心教训

1. ✅ **不要创新参数** - 复制已成功的参数格式
2. ✅ **遵循标准格式** - Task 描述使用标准 Markdown
3. ✅ **及时记录教训** - 每次失败都要记录原因
4. ✅ **持续改进流程** - 将教训固化为最佳实践

### 成功关键

- **参考成功案例** - Task 4 是成功参考
- **标准化参数** - 使用已验证的参数组合
- **清晰的任务描述** - 包含所有必要信息
- **及时汇报** - 每完成子任务就汇报

---

**维护人**: main  
**最后更新**: 2026-04-13 20:55  
**下次审查**: 每次 OMO Agent 启动失败后更新
