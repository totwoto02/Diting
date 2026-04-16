#!/bin/bash
# MFS Phase 1 MVP 发布脚本 - 安装 wheel 并构建
cd /root/.openclaw/workspace/projects/mfs-memory
echo "========================================"
echo "MFS Phase 1 MVP 发布 - 安装 wheel 并构建"
echo "========================================"
echo ""
echo "Step 1: 安装 wheel 包..."
pip3 install wheel --quiet
echo "✅ wheel 已安装"
echo ""
echo "Step 2: 构建 wheel..."
python3 setup.py bdist_wheel 2>&1 | tail -10
echo ""
echo "Step 3: 验证构建产物..."
ls -lh dist/
echo ""
echo "========================================"
echo "✅ 发布构建完成！"
echo "========================================"
echo ""
echo "已生成:"
echo "  - sdist: mfs_memory-0.1.0.tar.gz"
echo "  - wheel: mfs_memory-0.1.0-py3-none-any.whl"
echo ""
echo "下一步:"
echo "  1. 创建 GitHub 仓库: https://github.com/new"
echo "  2. 推送代码: git push -u origin main"
echo "  3. 上传 PyPI: twine upload dist/*"
echo ""
