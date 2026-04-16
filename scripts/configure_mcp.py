#!/usr/bin/env python3
"""
MCP 自动配置脚本

用法：python3 scripts/configure_mcp.py [mfs_path]
"""

import json
import os
import sys

def configure_mcp(mfs_path=None):
    """配置 MCP Server"""
    
    # 如果没有提供路径，使用当前目录
    if mfs_path is None:
        mfs_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # MCP 配置文件路径
    config_path = os.path.expanduser("~/.openclaw/workspace/config/mcporter.json")
    
    print(f"配置 MCP Server...")
    print(f"  MFS 路径：{mfs_path}")
    print(f"  配置文件：{config_path}")
    
    # 读取现有配置
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {"mcpServers": {}, "imports": []}
    
    # 添加或更新 MFS 配置
    mfs_config = {
        "description": "MFS Memory File System - Local MCP Server (v0.3.0)",
        "command": "python3",
        "args": ["-m", "mfs.mcp_server"],
        "cwd": mfs_path,
        "env": {
            "PYTHONPATH": mfs_path
        }
    }
    
    if "mfs-memory" not in config.get("mcpServers", {}):
        config.setdefault("mcpServers", {})["mfs-memory"] = mfs_config
        print("  ✅ MFS 配置已添加")
    else:
        config["mcpServers"]["mfs-memory"] = mfs_config
        print("  ✅ MFS 配置已更新")
    
    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ 配置已保存到：{config_path}")
    
    # 验证配置
    print("\n验证配置...")
    try:
        import subprocess
        result = subprocess.run(
            ["mcporter", "list", "mfs-memory"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and "6 tools" in result.stdout:
            print("  ✅ MCP 工具验证通过（6 个工具）")
        else:
            print("  ⚠️  需要重启 MCP daemon")
            print("  请运行：mcporter daemon restart")
    except Exception as e:
        print(f"  ⚠️  验证失败：{e}")
        print("  请手动运行：mcporter daemon restart")
    
    print("\n完成！")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        configure_mcp(sys.argv[1])
    else:
        configure_mcp()
