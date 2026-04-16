#!/bin/bash
# 检查测试进度

echo "=== 双 Agent 模拟测试进度 ==="
echo ""

# 检查进程
echo "进程状态:"
ps aux | grep dual_agent | grep -v grep | head -3
echo ""

# 查看最新日志
echo "最新日志:"
tail -20 /root/.openclaw/workspace/projects/mfs-memory/tests/simulation_normal.log
echo ""

# 检查点文件
echo "检查点文件:"
ls -lh /root/.openclaw/workspace/projects/mfs-memory/tests/simulation_results/checkpoint_*.json 2>/dev/null | tail -5
echo ""

# 统计
echo "日志行数:"
wc -l /root/.openclaw/workspace/projects/mfs-memory/tests/simulation_normal.log
