# 双 Agent 模拟测试运行指南

**版本**: v1.0  
**最后更新**: 2026-04-15

---

## 🎯 测试目标

通过模拟人类用户与 MFS+OpenClaw 的对话，测试：
- ✅ 记忆存储准确性
- ✅ 检索性能
- ✅ **幻觉检测（重点）**
- ✅ 长期稳定性
- ✅ 资源消耗

---

## 📋 测试配置

| 参数 | 值 | 说明 |
|------|-----|------|
| **总请求数** | 2000 次 | 完整测试周期 |
| **总时长** | 15 小时 | 模拟真实使用 |
| **请求频率** | 133.3 次/小时 | 平均 ~27 秒/次 |
| **对话场景** | 5 类 | 日常/重要事件/学习/情感/工作 |

---

## 🚀 运行方式

### 方式 1: 快速模式（验证用）

```bash
# 不等待间隔，快速完成 2000 次请求
# 用于验证系统正常性
# 耗时：~5 秒

python3 tests/dual_agent_simulation.py
```

### 方式 2: 正常模式（生产测试）

```bash
# 按照 27 秒间隔执行
# 模拟真实使用场景
# 耗时：15 小时

# 修改脚本中的 fast_mode = False
# 或者使用命令行参数（待实现）

python3 tests/dual_agent_simulation.py
```

### 方式 3: 后台运行（推荐）

```bash
# 使用 nohup 后台运行
nohup python3 tests/dual_agent_simulation.py > simulation.log 2>&1 &

# 查看进度
tail -f simulation.log

# 查看 PID
ps aux | grep dual_agent
```

### 方式 4: 分阶段运行

```bash
# 每 4 小时运行一次，共 4 次
# 便于中断和恢复

# 阶段 1 (0-4 小时)
python3 tests/dual_agent_simulation.py --requests 500 --output phase1

# 阶段 2 (4-8 小时)
python3 tests/dual_agent_simulation.py --requests 500 --output phase2

# ...
```

---

## 📊 监控测试进度

### 实时日志

```bash
# 查看最新进度
tail -f tests/simulation_results/*.txt

# 查看检查点
ls -lh tests/simulation_results/checkpoint_*.json
```

### 性能指标

```bash
# 查看 JSON 报告
cat tests/simulation_results/final_report.json | python3 -m json.tool

# 提取关键指标
python3 << 'EOF'
import json
with open('tests/simulation_results/final_report.json') as f:
    data = json.load(f)
    print(f"总交互：{data['test_summary']['total_interactions']}")
    print(f"幻觉数：{data['hallucination_analysis']['total']}")
    print(f"幻觉率：{data['hallucination_analysis']['rate']}")
    print(f"平均延迟：{data['mfs_stats']['avg_latency_ms']:.2f}ms")
EOF
```

---

## 📁 输出文件

### 检查点文件

```
simulation_results/
├── checkpoint_1.json    # 第 100 次请求
├── checkpoint_2.json    # 第 200 次请求
├── ...
├── checkpoint_20.json   # 第 2000 次请求
├── final_report.json    # 最终报告
└── summary.txt          # 文本摘要
```

### 文件内容

**checkpoint_N.json**:
```json
{
  "checkpoint_id": 1,
  "timestamp": "2026-04-15T15:08:05",
  "total_interactions": 100,
  "results": [...],  // 最近 100 条交互
  "mfs_stats": {...},
  "human_memory": [...]
}
```

**final_report.json**:
```json
{
  "test_summary": {
    "start_time": "...",
    "end_time": "...",
    "duration_hours": 15.0,
    "total_interactions": 2000,
    "requests_per_hour": 133.3
  },
  "mfs_stats": {...},
  "hallucination_analysis": {...},
  "sample_interactions": [...],
  "recent_interactions": [...]
}
```

---

## 🎭 对话场景

### 场景 1: 日常对话 (20%)
- 天气查询
- 短期记忆检索
- 任务创建
- 项目追踪
- 人物关系

### 场景 2: 重要事件 (20%)
- 时间约定
- 地点确认
- 重要性标记
- 备选方案
- 历史经验

### 场景 3: 知识学习 (20%)
- 概念定义
- 技术原理
- 性能对比
- 优化方法
- 使用指南

### 场景 4: 情感交流 (20%)
- 情绪记录
- 关系分析
- 自我反思
- 行为解读
- 情感建议

### 场景 5: 工作协作 (20%)
- 任务管理
- 进度追踪
- 人员分工
- 质量指标
- 风险管理

---

## 🛡️ 幻觉检测机制

### 检测流程

```
1. 用户提问
   ↓
2. MFS 检索记忆
   ↓
3. 生成响应
   ↓
4. 存储到 Integrity Tracker
   ↓
5. 计算内容哈希
   ↓
6. 下次检索时验证
   ↓
7. 如果哈希不匹配 → 标记为幻觉
```

### 幻觉类型

| 类型 | 说明 | 检测方法 |
|------|------|---------|
| **记忆篡改** | 存储内容被修改 | 哈希验证 |
| **无中生有** | 检索到不存在的记忆 | 路径验证 |
| **张冠李戴** | 记忆内容混淆 | 上下文比对 |
| **时间错乱** | 时间戳不一致 | 时间验证 |

### 幻觉率计算

```
幻觉率 = 检测到的幻觉数 / 总请求数 × 100%

目标：< 0.1%
优秀：< 0.01%
完美：0%
```

---

## 📈 预期结果

### 性能指标

| 指标 | 预期值 | 优秀 | 良好 | 需优化 |
|------|--------|------|------|-------|
| **平均延迟** | <5ms | <2ms | <5ms | >10ms |
| **写入速度** | >100 条/秒 | >200 | >100 | <50 |
| **搜索延迟** | <1ms | <0.5ms | <1ms | >5ms |
| **幻觉率** | <0.1% | 0% | <0.1% | >1% |
| **内存占用** | <100MB | <50MB | <100MB | >200MB |

### 资源消耗

| 资源 | 预期 | 说明 |
|------|------|------|
| **CPU** | <10% | 单核占用 |
| **内存** | 50-100MB | 峰值 |
| **磁盘** | <10MB | 数据库大小 |
| **网络** | 0 | 本地测试 |

---

## ⚠️ 注意事项

### 运行前

- [ ] 确认磁盘空间充足（至少 100MB）
- [ ] 确认 Python 环境正常
- [ ] 关闭不必要的后台进程
- [ ] 确保 15 小时内不会断电

### 运行中

- [ ] 定期检查日志输出
- [ ] 监控资源占用
- [ ] 如有异常及时中断
- [ ] 保留检查点文件

### 运行后

- [ ] 验证最终报告完整性
- [ ] 分析幻觉检测结果
- [ ] 保存测试数据
- [ ] 清理临时文件（可选）

---

## 🔧 故障排查

### 问题 1: 测试中断

**解决**:
```bash
# 从最近的检查点恢复
# （需要实现恢复功能，目前需重新开始）
```

### 问题 2: 内存占用过高

**解决**:
```bash
# 减少检查点保存频率
# 修改：checkpoint_interval = 100 → 200
```

### 问题 3: 幻觉率异常

**解决**:
```bash
# 检查 Integrity Tracker
# 查看具体幻觉案例
cat tests/simulation_results/final_report.json | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d['sample_interactions'][:5])"
```

### 问题 4: 性能下降

**解决**:
```bash
# 检查数据库大小
ls -lh /tmp/tmp*.db

# 清理临时文件
rm -f /tmp/tmp*.db /tmp/tmp*.db_kg
```

---

## 📊 结果分析

### 快速分析脚本

```bash
python3 << 'EOF'
import json

with open('tests/simulation_results/final_report.json') as f:
    data = json.load(f)

print("=" * 70)
print("双 Agent 模拟测试结果")
print("=" * 70)

summary = data['test_summary']
print(f"\n测试时长：{summary['duration_hours']:.2f} 小时")
print(f"总交互：{summary['total_interactions']} 次")
print(f"平均速率：{summary['requests_per_hour']:.1f} 次/小时")

mfs = data['mfs_stats']
print(f"\nMFS 性能:")
print(f"  平均延迟：{mfs['avg_latency_ms']:.2f}ms")
print(f"  记忆数：{mfs['mft']['total']}")
print(f"  KG 概念：{mfs['kg']['concept_count']}")

hallucination = data['hallucination_analysis']
print(f"\n幻觉检测:")
print(f"  总数：{hallucination['total']}")
print(f"  比率：{hallucination['rate']}")

# 评级
print(f"\n综合评级:", end=" ")
if hallucination['total'] == 0 and mfs['avg_latency_ms'] < 2:
    print("⭐⭐⭐⭐⭐ 优秀")
elif hallucination['total'] < 5 and mfs['avg_latency_ms'] < 5:
    print("⭐⭐⭐⭐ 良好")
else:
    print("⭐⭐⭐ 需优化")
EOF
```

---

## 📝 测试记录模板

```markdown
# 测试记录

**测试日期**: 2026-04-15  
**测试人员**: [姓名]  
**测试模式**: [快速/正常/后台]

## 测试结果

- 总交互：____ 次
- 测试时长：____ 小时
- 平均速率：____ 次/小时

## 性能指标

- 平均延迟：____ ms
- 幻觉数：____
- 幻觉率：____ %

## 问题记录

1. [问题描述]
2. [解决方案]

## 结论

[测试结论和改进建议]
```

---

## 📞 获取帮助

**文档位置**:
- 测试脚本：`tests/dual_agent_simulation.py`
- 运行指南：`tests/RUN_SIMULATION.md`
- 结果目录：`tests/simulation_results/`

**日志位置**:
- 实时日志：`simulation.log`（后台模式）
- 检查点：`tests/simulation_results/checkpoint_*.json`
- 最终报告：`tests/simulation_results/final_report.json`

---

**最后更新**: 2026-04-15  
**维护人**: MFS Team  
**版本**: v1.0
