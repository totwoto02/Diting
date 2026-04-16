#!/bin/bash
# MFS Phase 1 MVP 发布脚本 - 上传到 TestPyPI
cd /root/.openclaw/workspace/projects/mfs-memory
echo "========================================"
echo "MFS Phase 1 MVP 发布 - 上传到 TestPyPI"
echo "========================================"
echo ""
echo "Step 1: 验证 PyPI 配置..."
if [ -f ~/.pypirc ]; then
    echo "✅ ~/.pypirc 存在"
else
    echo "❌ ~/.pypirc 不存在"
    exit 1
fi
echo ""
echo "Step 2: 上传到 TestPyPI (测试环境)..."
python3 -m twine upload --repository testpypi dist/* --verbose 2>&1 | tail -20
echo ""
echo "========================================"
echo "✅ TestPyPI 上传完成！"
echo "========================================"
echo ""
echo "验证:"
echo "  访问：https://test.pypi.org/project/mfs-memory/"
echo ""
echo "下一步:"
echo "  1. 验证 TestPyPI 安装: pip install --index-url https://test.pypi.org/simple/ mfs-memory"
echo "  2. 上传到正式 PyPI: twine upload dist/*"
echo "  3. 创建 GitHub 仓库并推送代码"
echo ""
