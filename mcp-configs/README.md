# MCP 配置打包清单

**打包时间**: 2026-04-16  
**打包位置**: `/root/.openclaw/workspace/projects/mfs-memory/mcp-configs/`  

---

## 📦 配置文件清单

| 平台 | 文件名 | 大小 | MCP 服务器 | 状态 |
|------|--------|------|-----------|------|
| **Claude Code** | `claude-code-mcp.json` | 824B | mfs-memory, hermes, filesystem | ✅ 已打包 |
| **OpenCode** | `opencode-mcp.json` | 902B | mfs-memory, hermes, filesystem | ✅ 已打包 |
| **Hermes** | `hermes-mcp.json` | 711B | mfs-memory, filesystem | ✅ 已打包 |
| **OpenClaw** | `openclaw-mcp.json` | 867B | mfs-memory, hermes, filesystem | ✅ 已打包 |

---

## 🔧 安装方法

### Claude Code 用户

```bash
cp /root/.openclaw/workspace/projects/mfs-memory/mcp-configs/claude-code-mcp.json \
   ~/.config/claude/mcp.json

# 验证
cat ~/.config/claude/mcp.json | jq '.mcpServers | keys'
```

**输出**:
```json
["filesystem", "hermes", "mfs-memory"]
```

---

### OpenCode 用户

```bash
cp /root/.openclaw/workspace/projects/mfs-memory/mcp-configs/opencode-mcp.json \
   ~/.opencode/mcp.json

# 验证
cat ~/.opencode/mcp.json | jq '.mcp.servers | keys'
```

**输出**:
```json
["filesystem", "hermes", "mfs-memory"]
```

---

### Hermes 用户

```bash
cp /root/.openclaw/workspace/projects/mfs-memory/mcp-configs/hermes-mcp.json \
   ~/.hermes/mcp.json

# 验证
cat ~/.hermes/mcp.json | jq '.mcpServers | keys'
```

**输出**:
```json
["filesystem", "mfs-memory"]
```

---

### OpenClaw 用户

```bash
cp /root/.openclaw/workspace/projects/mfs-memory/mcp-configs/openclaw-mcp.json \
   ~/.openclaw/mcp.json

# 验证
cat ~/.openclaw/mcp.json | jq '.mcpServers | keys'
```

**输出**:
```json
["filesystem", "hermes", "mfs-memory"]
```

---

## 📊 配置对比

| 配置项 | Claude Code | OpenCode | Hermes | OpenClaw |
|--------|-------------|---------|--------|----------|
| **根节点** | `mcpServers` | `mcp.servers` | `mcpServers` | `mcpServers` |
| **MFS 配置** | ✅ | ✅ | ✅ | ✅ |
| **Hermes 配置** | ✅ | ✅ | ❌ | ✅ |
| **Filesystem 配置** | ✅ | ✅ | ✅ | ✅ |
| **特殊配置** | - | - | - | channel, agent |

---

## 🎯 MCP 服务器说明

### 1. mfs-memory

**功能**: MFS 记忆系统

**工具**:
- `mfs_read` - 读取记忆
- `mfs_write` - 写入记忆
- `mfs_search` - 搜索记忆

**配置**:
```json
{
  "command": "python3",
  "args": ["-m", "mfs.mcp_server"],
  "cwd": "/root/.openclaw/workspace/projects/mfs-memory",
  "env": {
    "MFS_DB_PATH": "/root/.openclaw/workspace/projects/mfs-memory/mfs.db",
    "PYTHONPATH": "/root/.openclaw/workspace/projects/mfs-memory"
  }
}
```

---

### 2. hermes

**功能**: Hermes MCP (Onairos 人格系统)

**配置**:
```json
{
  "command": "onairos-hermes-mcp",
  "args": [],
  "env": {}
}
```

---

### 3. filesystem

**功能**: 文件系统访问

**工具**:
- `read_file` - 读取文件
- `write_file` - 写入文件
- `list_directory` - 列出目录
- `search_files` - 搜索文件

**配置**:
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/root/.openclaw/workspace"],
  "env": {}
}
```

---

## ⚠️ 注意事项

### 环境变量

确保以下环境变量已设置：

```bash
export MFS_DB_PATH="/root/.openclaw/workspace/projects/mfs-memory/mfs.db"
export PYTHONPATH="/root/.openclaw/workspace/projects/mfs-memory"
```

### 路径配置

MFS MCP 服务器工作目录：
```
/root/.openclaw/workspace/projects/mfs-memory/
```

### 权限要求

确保有以下权限：
- ✅ 读取/写入 MFS 数据库
- ✅ 执行 Python 脚本
- ✅ 执行 npm/npx 命令

---

## 📝 配置文件结构

### Claude Code / Hermes / OpenClaw

```json
{
  "$schema": "https://.../mcp-config-v1.json",
  "mcpServers": {
    "mfs-memory": { ... },
    "hermes": { ... },
    "filesystem": { ... }
  }
}
```

### OpenCode

```json
{
  "$schema": "https://.../mcp-config-v1.json",
  "mcp": {
    "servers": {
      "mfs-memory": { ... },
      "hermes": { ... },
      "filesystem": { ... }
    }
  }
}
```

---

## 🚀 快速测试

### 测试 MFS MCP

```bash
# 任意平台
python3 -c "
from mfs.mcp_server import MCPServer
server = MCPServer(db_path='mfs.db')
print('✅ MFS MCP 服务器正常')
server.close()
"
```

### 测试 Hermes MCP

```bash
onairos-hermes-mcp --version
```

### 测试 Filesystem MCP

```bash
npx -y @modelcontextprotocol/server-filesystem --help
```

---

## 📞 故障排查

### 问题 1: MCP 服务器未找到

```
Error: MCP server 'mfs-memory' not found
```

**解决**:
```bash
# 检查配置文件
cat ~/.config/claude/mcp.json | jq '.mcpServers.mfs-memory'

# 验证 MFS 路径
ls -la /root/.openclaw/workspace/projects/mfs-memory/
```

### 问题 2: 数据库锁定

```
sqlite3.OperationalError: database is locked
```

**解决**:
```bash
# 检查是否有多个进程
ps aux | grep mfs.mcp_server

# 关闭多余进程
kill <PID>
```

### 问题 3: 命令未找到

```
command not found: onairos-hermes-mcp
```

**解决**:
```bash
# 重新安装
npm install -g onairos-hermes-mcp

# 添加到 PATH
export PATH=$PATH:~/.nvm/versions/node/v22.22.0/bin
```

---

## 🎊 总结

**打包成果**:
- ✅ 4 个平台 MCP 配置
- ✅ 配置文件目录
- ✅ 安装说明文档
- ✅ 故障排查指南

**可以立即使用！** 📦

---

**打包负责人**: main (管家)  
**完成时间**: 2026-04-16  
**配置文件位置**: `/root/.openclaw/workspace/projects/mfs-memory/mcp-configs/`
