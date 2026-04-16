# 正常模式测试状态

**启动时间**: 2026-04-15 15:34:17  
**预计完成**: 2026-04-16 06:34 (15 小时后)  
**当前状态**: 🟢 运行中

---

## 📊 测试配置

| 参数 | 值 |
|------|-----|
| **总请求** | 2000 次 |
| **总时长** | 15 小时 |
| **请求频率** | 133.3 次/小时 |
| **间隔时间** | 27.0 秒/次 |
| **严苛测试占比** | 20% |

---

## 📋 监控方法

### 方法 1: 查看日志

```bash
tail -f tests/simulation_normal.log
```

### 方法 2: 运行检查脚本

```bash
bash tests/check_progress.sh
```

### 方法 3: 查看检查点

```bash
ls -lh tests/simulation_results/checkpoint_*.json
cat tests/simulation_results/checkpoint_1.json | python3 -m json.tool
```

---

## 📈 预期进度

| 时间 | 进度 | 检查点 |
|------|------|--------|
| 15:34 | 0% | 启动 |
| 16:00 | ~10% | checkpoint_1 |
| 16:25 | ~20% | checkpoint_2 |
| 17:00 | ~30% | checkpoint_3 |
| ... | ... | ... |
| 06:34 | 100% | 完成 |

---

## 🛡️ 严苛幻觉测试

**预期结果**:
- 总测试数：~400 次（20%）
- 通过率：>95%
- 幻觉率：<0.1%

**测试场景**:
1. 诱导性提问（编造记忆）
2. 记忆混淆（相似概念）
3. 时间错乱（日期错误）
4. 无中生有（虚假信息）
5. 前后矛盾（一致性）

---

## 📁 输出文件

```
tests/simulation_results/
├── checkpoint_1.json    # 第 100 次（约 16:00）
├── checkpoint_2.json    # 第 200 次（约 16:25）
├── ...
├── checkpoint_20.json   # 第 2000 次（约 06:34）
├── final_report.json    # 最终报告
└── summary.txt          # 文本摘要
```

---

## ⚠️ 注意事项

1. **不要中断** - 让测试完整运行 15 小时
2. **定期检查** - 每 1-2 小时查看进度
3. **保存日志** - 测试完成后保存完整日志
4. **磁盘空间** - 确保至少 100MB 可用空间

---

## 📞 故障排查

### 进程停止

```bash
# 检查进程
ps aux | grep dual_agent

# 重启测试
bash tests/start_normal_test.sh &
```

### 日志无输出

```bash
# 检查文件
ls -lh tests/simulation_normal.log

# 查看内容
cat tests/simulation_normal.log
```

### 检查点未保存

```bash
# 检查目录
ls -lh tests/simulation_results/

# 手动保存（紧急情况下）
# 需要实现手动保存功能
```

---

**最后更新**: 2026-04-15 15:34  
**下次检查**: 16:00（第一次检查点）
