#!/bin/bash
# 启动正常模式测试（15 小时）

cd /root/.openclaw/workspace/projects/mfs-memory

echo "🚀 启动正常模式测试..."
echo "   总请求：2000 次"
echo "   总时长：15 小时"
echo "   间隔时间：27 秒"
echo ""

# 使用无缓冲模式运行
python3 -u tests/dual_agent_simulation.py 2>&1 | tee tests/simulation_normal.log
