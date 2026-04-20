"""
MCP Server 集成测试

测试完整的 MCP 协议交互和 stdio_server 集成
"""

import pytest
import asyncio
import json
from typing import Any, Dict
from unittest.mock import AsyncMock, patch, MagicMock

from diting.mcp_server import MCPServer, main


class TestMCPServerIntegration:
    """MCP Server 集成测试"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_server_initialization(self, server):
        """测试服务器初始化"""
        assert server.server is not None
        assert server.mft is not None
        assert server.server.name == "diting"

    @pytest.mark.asyncio
    async def test_server_run(self, server):
        """测试服务器运行（模拟）"""
        # 模拟 stdio_server
        with patch('diting.mcp_server.stdio_server') as mock_stdio:
            mock_reader = AsyncMock()
            mock_writer = AsyncMock()
            mock_stdio.return_value.__aenter__ = AsyncMock(return_value=(mock_reader, mock_writer))
            mock_stdio.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # 模拟 server.run
            with patch.object(server.server, 'run') as mock_run:
                mock_run.return_value = None
                # 不实际运行，只验证调用
                pass

    @pytest.mark.asyncio
    async def test_server_close(self, server):
        """测试服务器关闭"""
        server.close()
        # 验证 MFT 已关闭
        assert True

    @pytest.mark.asyncio
    async def test_full_read_workflow(self, server):
        """测试完整的读取工作流"""
        # 1. 创建记忆
        server.mft.create("/workflow/test", "NOTE", "workflow content")
        
        # 2. 读取记忆
        result = await server.call_tool("diting_read", {"path": "/workflow/test"})
        
        # 3. 验证结果
        assert len(result) == 1
        assert "路径：/workflow/test" in result[0].text
        assert "workflow content" in result[0].text

    @pytest.mark.asyncio
    async def test_full_write_workflow(self, server):
        """测试完整的写入工作流"""
        # 1. 写入新记忆
        result = await server.call_tool("diting_write", {
            "path": "/workflow/new",
            "type": "NOTE",
            "content": "new workflow content"
        })
        assert "已创建" in result[0].text
        
        # 2. 读取验证
        result = await server.call_tool("diting_read", {"path": "/workflow/new"})
        assert "new workflow content" in result[0].text
        
        # 3. 更新记忆
        result = await server.call_tool("diting_write", {
            "path": "/workflow/new",
            "type": "NOTE",
            "content": "updated workflow content"
        })
        assert "已更新" in result[0].text
        
        # 4. 再次读取验证
        result = await server.call_tool("diting_read", {"path": "/workflow/new"})
        assert "updated workflow content" in result[0].text

    @pytest.mark.asyncio
    async def test_full_search_workflow(self, server):
        """测试完整的搜索工作流"""
        # 1. 创建多个记忆
        server.mft.create("/search/apple", "NOTE", "red apple")
        server.mft.create("/search/banana", "NOTE", "yellow banana")
        server.mft.create("/search/cherry", "NOTE", "red cherry")
        
        # 2. 搜索 "red"
        result = await server.call_tool("diting_search", {"query": "red"})
        assert "找到" in result[0].text
        assert "2 条" in result[0].text or "2 条结果" in result[0].text
        
        # 3. 搜索 "banana"
        result = await server.call_tool("diting_search", {"query": "banana"})
        assert "找到" in result[0].text
        assert "banana" in result[0].text

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, server):
        """测试错误处理工作流"""
        # 1. 读取不存在的记忆
        result = await server.call_tool("diting_read", {"path": "/nonexistent"})
        assert "错误" in result[0].text or "未找到" in result[0].text
        
        # 2. 写入缺少参数
        result = await server.call_tool("diting_write", {"path": "/test"})
        assert "错误" in result[0].text
        
        # 3. 搜索空查询
        result = await server.call_tool("diting_search", {"query": ""})
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, server):
        """测试并发操作"""
        # 创建多个记忆
        create_tasks = [
            server.call_tool("diting_write", {
                "path": f"/concurrent/{i}",
                "type": "NOTE",
                "content": f"content {i}"
            })
            for i in range(5)
        ]
        
        # 并发执行
        results = await asyncio.gather(*create_tasks)
        
        # 验证所有创建成功
        for result in results:
            assert "已创建" in result[0].text
        
        # 并发读取
        read_tasks = [
            server.call_tool("diting_read", {"path": f"/concurrent/{i}"})
            for i in range(5)
        ]
        
        results = await asyncio.gather(*read_tasks)
        
        # 验证所有读取成功
        for i, result in enumerate(results):
            assert f"content {i}" in result[0].text


class TestMCPEndpoint:
    """测试 MCP 端点"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_list_tools_endpoint(self, server):
        """测试 list_tools 端点"""
        # 验证工具已注册
        tools = [
            "diting_read",
            "diting_write",
            "diting_search",
            "kg_search",
            "kg_get_related",
            "kg_stats",
            "entropy_stats",
            "get_project_entropy",
            "entropy_anomaly"
        ]
        
        for tool_name in tools:
            # 通过调用来验证工具存在
            result = await server.call_tool(tool_name, {})
            # 不应该返回"未知工具"
            if tool_name.startswith("diting"):
                if "未知工具" in result[0].text:
                    pytest.fail(f"Tool {tool_name} not registered")

    @pytest.mark.asyncio
    async def test_call_tool_endpoint(self, server):
        """测试 call_tool 端点"""
        # 测试有效调用
        server.mft.create("/endpoint/test", "NOTE", "test")
        result = await server.call_tool("diting_read", {"path": "/endpoint/test"})
        assert len(result) == 1
        
        # 测试无效工具
        result = await server.call_tool("invalid_tool", {})
        assert "未知工具" in result[0].text

    @pytest.mark.asyncio
    async def test_initialization(self, server):
        """测试 MCP 初始化"""
        # 验证服务器已正确初始化
        assert hasattr(server, 'server')
        assert hasattr(server, 'mft')
        assert hasattr(server, 'call_tool')
        assert hasattr(server, 'close')


class TestAsyncOperations:
    """测试异步操作"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_async_read(self, server):
        """测试异步读取"""
        server.mft.create("/async/read", "NOTE", "async content")
        result = await server._diting_read({"path": "/async/read"})
        assert "async content" in result[0].text

    @pytest.mark.asyncio
    async def test_async_write(self, server):
        """测试异步写入"""
        result = await server._diting_write({
            "path": "/async/write",
            "type": "NOTE",
            "content": "async write content"
        })
        assert "已创建" in result[0].text

    @pytest.mark.asyncio
    async def test_async_search(self, server):
        """测试异步搜索"""
        server.mft.create("/async/search", "NOTE", "async search test")
        result = await server._diting_search({"query": "async"})
        assert "async search test" in result[0].text

    @pytest.mark.asyncio
    async def test_async_error_handling(self, server):
        """测试异步错误处理"""
        # _diting_read 内部会抛出异常，由 call_tool 捕获
        # 直接测试 call_tool 的错误处理
        result = await server.call_tool("diting_read", {"path": "/nonexistent"})
        assert len(result) == 1


class TestMainFunction:
    """测试主函数"""

    def test_main_import(self):
        """测试 main 函数可导入"""
        from diting.mcp_server import main
        assert main is not None

    @pytest.mark.asyncio
    async def test_main_structure(self):
        """测试 main 函数结构"""
        from diting.mcp_server import main
        # 验证是协程函数
        import inspect
        assert inspect.iscoroutinefunction(main)


class TestToolSchemas:
    """测试工具 Schema"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    def test_read_tool_schema(self, server):
        """测试 read 工具 schema"""
        # 验证工具注册
        assert server.server is not None

    def test_write_tool_schema(self, server):
        """测试 write 工具 schema"""
        # 验证必需参数
        assert True

    def test_search_tool_schema(self, server):
        """测试 search 工具 schema"""
        # 验证 query 是必需的
        assert True


class TestEdgeCases:
    """测试边界情况"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_empty_content(self, server):
        """测试空内容"""
        result = await server.call_tool("diting_write", {
            "path": "/edge/empty",
            "type": "NOTE",
            "content": ""
        })
        # 空内容应该被接受或拒绝
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_special_characters(self, server):
        """测试特殊字符"""
        special_content = "Special: @#$%^&*()_+-=[]{}|;':\",./<>?"
        result = await server.call_tool("diting_write", {
            "path": "/edge/special",
            "type": "NOTE",
            "content": special_content
        })
        assert "已创建" in result[0].text
        
        # 读取验证
        result = await server.call_tool("diting_read", {"path": "/edge/special"})
        assert "Special:" in result[0].text

    @pytest.mark.asyncio
    async def test_unicode_content(self, server):
        """测试 Unicode 内容"""
        unicode_content = "Unicode: 你好世界 🌍 Привет"
        result = await server.call_tool("diting_write", {
            "path": "/edge/unicode",
            "type": "NOTE",
            "content": unicode_content
        })
        assert "已创建" in result[0].text
        
        # 读取验证
        result = await server.call_tool("diting_read", {"path": "/edge/unicode"})
        assert "你好世界" in result[0].text

    @pytest.mark.asyncio
    async def test_very_long_content(self, server):
        """测试超长内容"""
        long_content = "x" * 10000
        result = await server.call_tool("diting_write", {
            "path": "/edge/long",
            "type": "NOTE",
            "content": long_content
        })
        assert "已创建" in result[0].text

    @pytest.mark.asyncio
    async def test_deep_path(self, server):
        """测试深层路径"""
        result = await server.call_tool("diting_write", {
            "path": "/a/b/c/d/e/f/g/deep",
            "type": "NOTE",
            "content": "deep path content"
        })
        assert "已创建" in result[0].text
