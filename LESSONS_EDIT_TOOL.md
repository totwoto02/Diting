# Edit 工具失败原因分析与解决方案

**创建时间**: 2026-04-13  
**事件**: MFS 项目文档编辑多次失败  
**影响**: 进度延迟约 5 分钟，但最终通过 write 解决  

---

## 一、失败案例回顾

### 失败案例 1: PHASE1_PLAN.md 技术风险表

**时间**: 16:34 GMT+8  
**操作**: 尝试更新技术风险表（Claude Code → OpenCode）

**失败原因**:
```
错误：Could not find the exact text in file
原因：文件内容在之前的 edit 中已被更新，但我的 oldText 基于旧版本
```

**问题代码**:
```python
# 我尝试匹配的旧文本
| Claude Code 接入失败 | 低 | 高 | 准备备用测试方案 (Cursor) |

# 但文件实际内容已被之前的 edit 改为
| OpenCode 接入失败 | 低 | 高 | 准备备用测试方案 (OpenClaw 原生) |
```

---

### 失败案例 2: PROGRESS_LOG.md 关键决策记录

**时间**: 16:36 GMT+8  
**操作**: 添加 TDD 开发模式决策记录

**失败原因**:
```
错误：Could not find the exact text in file
原因：文件在 16:34 已被 write 完全重写，我的 oldText 基于更早的版本
```

**问题代码**:
```python
# 我尝试匹配的旧文本（来自 16:32 版本）
| 2026-04-13 | 验收标准：OpenClaw + OpenCode | 用户确认 |

# 但文件实际内容已被 write 重写为全新格式
```

---

### 失败案例 3: PHASE1_PLAN.md 风险表（再次尝试）

**时间**: 16:38 GMT+8  
**操作**: 再次尝试更新技术风险表

**失败原因**:
```
错误：Could not find the exact text in file
原因：文本匹配要求严格（包括空格、换行、标点），我的 oldText 有细微差异
```

**问题代码**:
```python
# 我尝试匹配的文本（有细微差异）
| 风险 | 概率 | 影响 | 应对措施 |
|------|-----|------|---------||  # ← 多了一个 |

# 文件实际内容
| 风险 | 概率 | 影响 | 应对措施 |
|------|-----|------|---------|
```

---

## 二、根本原因分析

### 原因 1: 文件状态不同步 ⭐⭐⭐⭐⭐

**问题描述**:
- 我对文件内容的认知基于上一次 read
- 但文件可能已被其他操作（write/edit）更新
- 我的 oldText 基于旧版本，导致匹配失败

**触发场景**:
1. 连续多次 edit 同一文件
2. edit 和 write 混合使用
3. 长时间间隔后再次 edit

**影响程度**: 🔴 高（导致 3 次失败）

---

### 原因 2: 文本匹配过于严格 ⭐⭐⭐⭐

**问题描述**:
- edit 工具要求 oldText 完全匹配（包括空格、换行、标点）
- 细微差异（如多余的空格、换行符）都会导致失败
- 人类难以精确感知这些差异

**触发场景**:
1. Markdown 表格（容易有多余空格）
2. 多行文本块（换行符可能不同）
3. 从记忆或上下文复制的文本

**影响程度**: 🟡 中（导致 1 次失败）

---

### 原因 3: 未遵循安全编辑流程 ⭐⭐⭐⭐⭐

**问题描述**:
- 我没有严格遵守"先 read 再 edit"的流程
- 假设文件内容未变，直接使用旧版本 oldText
- 这是最严重的流程违规

**触发场景**:
1. 短时间内多次 edit
2. 认为文件"应该"没变
3. 为了节省时间跳过 read

**影响程度**: 🔴 高（导致所有失败）

---

## 三、解决方案

### 方案 1: 严格执行安全编辑流程 ⭐⭐⭐⭐⭐

**流程**:
```
1. read 获取最新内容    ← 必须执行
2. 立即 edit             ← 不要间隔其他操作
3. 验证 edit 结果        ← grep 或 read 确认
```

**具体操作**:
```python
# ✅ 正确做法
read(path="file.md")           # 获取最新内容
edit(path="file.md", ...)      # 立即编辑（不要间隔其他操作）
exec(command="grep xxx file.md")  # 验证结果

# ❌ 错误做法
edit(path="file.md", ...)      # 直接编辑（假设内容未变）
# 失败后再次 edit              # 基于旧版本再次尝试
```

**执行标准**:
- 每次 edit 前必须 read（除非 100% 确定文件未变）
- read 和 edit 之间不要插入其他操作
- edit 后立即验证结果

---

### 方案 2: 优先使用 write 替代 edit ⭐⭐⭐⭐

**适用场景**:
1. 重要文件（如 PROJECT_PLAN.md）
2. 多次 edit 失败后
3. 文件结构需要大改

**优势**:
- 不依赖旧内容，完全重写
- 避免匹配失败
- 结果可控

**劣势**:
- 会丢失文件原有内容（需先 read）
- token 消耗略高

**具体操作**:
```python
# ✅ write 流程
read(path="file.md")                    # 读取原内容
write(path="file.md", content=new_text) # 完全重写

# 适用场景：重要文档、多次 edit 失败后
```

**决策树**:
```
是否需要编辑文件？
  ↓
是重要文件/大改动？
  ↓ 是 → write（先 read 再 write）
  ↓ 否
小改动/简单替换？
  ↓ 是 → edit（先 read 再 edit）
  ↓ 否
是否需要多次 edit？
  ↓ 是 → write（合并为一次 write）
```

---

### 方案 3: 使用小文本块匹配 ⭐⭐⭐

**适用场景**:
- 必须使用 edit 时
- 文件较大，read 耗时

**具体操作**:
```python
# ✅ 使用小文本块（1-3 行）
edit(path="file.md", edits=[
    {"oldText": "| 风险 | 概率 |", "newText": "| 风险 | 概率 |"}
])

# ❌ 避免使用大文本块（10+ 行）
edit(path="file.md", edits=[
    {"oldText": "整个表格内容...", "newText": "..."}
])
```

**优势**:
- 匹配成功率高
- 易于定位问题

**劣势**:
- 需要多次 edit（增加失败概率）
- 不适合大改动

---

### 方案 4: 使用 exec 验证 ⭐⭐⭐⭐

**适用场景**:
- edit 后验证结果
- 检查关键信息是否记录

**具体操作**:
```python
# edit 后立即验证
edit(path="file.md", ...)
exec(command="grep -n '关键信息' file.md | head -5")

# 验证失败 → 立即修正
# 验证成功 → 继续下一步
```

**验证清单**:
```bash
# 检查关键信息是否记录
grep -n "OpenClaw" file.md
grep -n "TDD" file.md
grep -n "验收标准" file.md

# 检查文件完整性
wc -l file.md          # 行数检查
wc -c file.md          # 大小检查

# 检查 Git 状态（如已初始化）
git status
git diff
```

---

## 四、最佳实践总结

### 4.1 安全编辑流程（强制执行）

```markdown
## 编辑文件标准流程

1. **read 最新内容** → 获取当前文件状态
   ```
   read(path="file.md", limit=50)
   ```

2. **立即 edit** → 不要间隔其他操作
   ```
   edit(path="file.md", edits=[...])
   ```

3. **验证结果** → grep 或 read 确认
   ```
   exec(command="grep -n '关键信息' file.md")
   ```

4. **失败处理** → 最多重试 1 次，然后改用 write
   ```
   if edit 失败:
       read(path="file.md")  # 重新读取
       write(path="file.md", content=new_text)  # 改用 write
   ```
```

---

### 4.2 工具选择决策树

```
需要修改文件？
  ↓
文件是否重要/大改动？
  ↓ 是 → write（先 read 再 write）
  ↓ 否
是否 100% 确定文件内容？
  ↓ 否 → read + edit
  ↓ 是
是否小改动（1-3 行）？
  ↓ 是 → edit
  ↓ 否 → write
```

---

### 4.3 验证清单（每次 edit 后执行）

```bash
# 1. 检查关键信息
grep -n "关键信息" file.md

# 2. 检查文件完整性
wc -l file.md  # 行数不应大幅变化

# 3. 检查 Git 状态（如已初始化）
git diff file.md  # 查看变更

# 4. 抽样检查
read(path="file.md", offset=1, limit=10)
```

---

## 五、教训记录

### 5.1 核心教训

1. **永远不要假设文件内容未变** ⭐⭐⭐⭐⭐
   - 即使刚编辑过，也可能被其他操作更新
   - 必须 read 获取最新状态

2. **edit 失败最多重试 1 次** ⭐⭐⭐⭐
   - 第 1 次失败 → read 最新内容再试
   - 第 2 次失败 → 改用 write

3. **重要文件优先使用 write** ⭐⭐⭐⭐
   - PROJECT_PLAN.md、PHASE1_PLAN.md 等重要文档
   - 直接用 write 更安全可靠

4. **edit 后必须验证** ⭐⭐⭐⭐⭐
   - 不要假设 edit 成功
   - 用 grep 或 read 确认结果

---

### 5.2 本次事件时间线

```
16:21 - 创建 PROJECT_PLAN.md (write) ✅
16:23 - 创建 PROGRESS_LOG.md (write) ✅
16:25 - 创建 PHASE1_PLAN.md (write) ✅
16:30 - 更新 PROJECT_PLAN.md (edit) ✅ 成功
16:32 - 更新 PROGRESS_LOG.md (write) ✅ 成功
16:34 - 更新 PHASE1_PLAN.md (edit) ❌ 失败（旧版本匹配）
16:34 - 再次尝试 (edit) ❌ 失败（文本匹配问题）
16:36 - 更新 PROGRESS_LOG.md (edit) ❌ 失败（文件已重写）
16:38 - 改用 write 重写 PHASE1_PLAN.md ✅ 成功
16:44 - 改用 write 重写 PROGRESS_LOG.md ✅ 成功
```

**失败次数**: 3 次  
**成功次数**: 5 次（write）  
**延迟时间**: 约 5 分钟  

---

### 5.3 改进措施（已落实）

1. ✅ 在 SOUL.md 中添加工具使用规范
2. ✅ 创建 LESSONS_EDIT_TOOL.md（本文档）
3. ✅ 在 PROGRESS_LOG.md 中添加验证步骤
4. ✅ 未来 edit 前强制执行 read 流程

---

## 六、工具使用规范（更新到 SOUL.md）

### 6.1 文件编辑规范

```markdown
## 文件编辑工具选择

### write（推荐用于重要文件）

**适用场景**:
- 重要文档（PROJECT_PLAN.md、PHASE1_PLAN.md 等）
- 大改动（>10 行）
- edit 失败后

**流程**:
1. read 获取原内容
2. write 完全重写
3. grep 验证结果

### edit（仅用于小改动）

**适用场景**:
- 小改动（1-3 行）
- 非关键文件
- 100% 确定文件内容

**流程**:
1. read 获取最新内容（必须！）
2. 立即 edit（不要间隔其他操作）
3. grep 验证结果
4. 失败 → 重试 1 次 → 改用 write
```

### 6.2 验证规范

```markdown
## 文件操作验证

### 必须验证的场景
- write 后
- edit 后
- 多次 edit 后

### 验证方法
1. grep 关键信息
2. wc 检查文件大小
3. read 抽样检查
4. git diff（如已初始化）
```

---

## 七、PDCA 复盘

### Plan（计划）
- 分析 edit 失败原因
- 制定改进方案
- 创建教训文档

### Do（执行）
- 创建 LESSONS_EDIT_TOOL.md（本文档）
- 更新 SOUL.md（添加工具使用规范）
- 更新 PROGRESS_LOG.md（添加验证步骤）

### Check（检查）
- 验证文档已创建 ✅
- 验证 SOUL.md 已更新 ✅
- 验证流程已固化 ✅

### Act（修正/标准化）
- 将本文档纳入新人培训材料
- 在 TOOLS.md 中添加工具使用规范
- 未来类似任务强制执行安全编辑流程

---

**维护人**: main  
**最后更新**: 2026-04-13  
**下次复盘**: 2026-04-20（或再次发生 edit 失败时）
