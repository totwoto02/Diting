#!/bin/bash
# MFS Phase 1 MVP 发布脚本 - 构建 wheel
cd /root/.openclaw/workspace/projects/mfs-memory
echo "========================================"
echo "MFS Phase 1 MVP 发布 - Step 6: 构建 wheel"
echo "========================================"
echo ""
echo "正在构建 wheel..."
python3 setup.py bdist_wheel
echo ""
echo "构建产物:"
ls -lh dist/
echo ""
echo "========================================"
