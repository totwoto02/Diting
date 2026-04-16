# MFS 开发方案调整记录

**时间**: 2026-04-13 17:41 GMT+8  
**调整内容**: Copaw → OpenCode + OMO

---

## 调整原因

1. **Copaw 局限性**
   - 通用 subagent，非专业编程工具
   - 无 IDE 支持，调试效率低
   - 代码质量不可控

2. **OpenCode 优势**
   - 专业编程 IDE
   - 内置 AI 辅助（通义灵码/豆包 Code）
   - 支持实时调试、代码补全
   - 人机协同更高效

3. **OMO 模式优势**
   - Online: AI 辅助编程
   - Merge: 人机协同审查
   - Offline: 独立开发 + 定期同步

---

## 新方案：OpenCode + OMO

### 开发流程

```
1. main 任务拆解 → OMO 任务包
2. OMO Agent 开发 → OpenCode 环境
3. 代码审查 → main + 用户
4. Git 提交 → develop 分支
5. 继续下一个任务
```

### OMO Agent 配置

| 任务 | 模型选择 | 理由 |
|------|---------|------|
| Task 1: 项目初始化 | ✅ 已完成 (Copaw) | 已有成果可继续使用 |
| Task 2: MFT 表结构 | qwen-coder-plus | 代码生成能力强 |
| Task 3: MCP Server | qwen-coder-plus | MCP 协议理解好 |
| Task 4: 集成测试 | qwen-coder | 测试用例生成 |
| Task 5: 文档编写 | qwen-plus | 文档撰写能力强 |

### 工具配置

**OpenCode 插件**:
- 通义灵码 (代码补全)
- 豆包 Code (对话辅助)

**Git 工作流**:
- 每个 Task 创建 feature 分支
- 完成后 PR 到 develop
- main 负责审查

---

## 成果保留

**Copaw 已完成工作** (继续使用):
- ✅ 项目目录结构
- ✅ 32 个测试用例 (100% 通过)
- ✅ Git 仓库初始化
- ✅ 88% 测试覆盖率

**调整部分**:
- ⚠️ Task 2 起改用 OpenCode + OMO
- ⚠️ 后续任务由 OMO Agent 执行

---

## 时间影响

| 项目 | 原计划 | 调整后 | 影响 |
|------|-------|-------|------|
| Task 1 | ✅ 已完成 | ✅ 已完成 | 无 |
| Task 2-8 | 14 天 | 12 天 | -2 天 (效率提升) |
| 总周期 | 14 天 | 13 天 | -1 天 |

---

## 风险与应对

| 风险 | 概率 | 应对措施 |
|------|-----|---------|
| OMO Agent 不熟悉项目 | 低 | 提供详细文档 + PHASE1_PLAN.md |
| OpenCode 环境问题 | 低 | 国内直连，无需代理 |
| 代码风格不一致 | 中 | main 负责审查 + pre-commit hooks |

---

**决策人**: 用户确认  
**执行人**: main  
**状态**: ✅ 已执行
