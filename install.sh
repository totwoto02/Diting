#!/bin/bash
# MFS Memory File System 一键安装脚本
# 版本：v0.3.0

set -e  # 遇到错误立即退出

echo "=============================================="
echo "MFS Memory File System v0.3.0 安装脚本"
echo "=============================================="
echo ""

# 检查 Python 版本
echo "[1/6] 检查 Python 版本..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "   Python 版本：$python_version"

if ! python3 -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ required'"; then
    echo "❌ 错误：需要 Python 3.11 或更高版本"
    exit 1
fi
echo "   ✅ Python 版本符合要求"
echo ""

# 检查 pip
echo "[2/6] 检查 pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误：未找到 pip3"
    exit 1
fi
echo "   ✅ pip3 已安装"
echo ""

# 安装依赖
echo "[3/6] 安装依赖..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt -q
    echo "   ✅ 依赖安装完成"
else
    echo "   ⚠️  requirements.txt 不存在，跳过"
fi
echo ""

# 安装 MFS
echo "[4/6] 安装 MFS..."
pip3 install -e . -q
echo "   ✅ MFS 安装完成"
echo ""

# 配置 MCP
echo "[5/6] 配置 MCP..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 scripts/configure_mcp.py "$SCRIPT_DIR" 2>/dev/null || {
    echo "   ⚠️  自动配置失败，请手动配置"
    echo "   编辑：~/.openclaw/workspace/config/mcporter.json"
}
echo ""

# 验证安装
echo "[6/6] 验证安装..."
if python3 -c "from mfs.mft import MFT; print('✅')" 2>/dev/null; then
    echo "   ✅ MFS 验证通过"
else
    echo "   ❌ MFS 验证失败"
    exit 1
fi

if mcporter list mfs-memory &>/dev/null; then
    echo "   ✅ MCP 工具验证通过"
else
    echo "   ⚠️  MCP 工具未就绪，请运行：mcporter daemon restart"
fi
echo ""

# 完成
echo "=============================================="
echo "🎉 MFS v0.3.0 安装完成！"
echo "=============================================="
echo ""
echo "下一步:"
echo "  1. 重启 MCP daemon: mcporter daemon restart"
echo "  2. 验证工具：mcporter list mfs-memory"
echo "  3. 运行测试：python3 -m pytest tests/ -v"
echo ""
echo "文档位置:"
echo "  - 使用指南：docs/README.md"
echo "  - API 文档：docs/API.md"
echo "  - 开发者：docs/DEVELOPER.md"
echo ""
