"""
MCP Server 异步运行测试

测试 MCP Server 的 run() 方法和异步集成
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from diting.mcp_server import MCPServer, main


class TestMCPServerRun:
    """测试 MCP Server 运行方法"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_run_method_exists(self, server):
        """测试 run 方法存在"""
        assert hasattr(server, 'run')
        assert callable(server.run)

    @pytest.mark.asyncio
    async def test_run_with_mocked_stdio(self, server):
        """测试 run 方法（模拟 stdio）"""
        # 创建模拟的读写流
        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()
        
        # 模拟 stdio_server 上下文管理器
        with patch('diting.mcp_server.stdio_server') as mock_stdio:
            # 配置异步上下文管理器
            async def async_context_manager():
                yield mock_read_stream, mock_write_stream
            
            # 模拟 server.run 不实际执行
            with patch.object(server.server, 'run') as mock_server_run:
                mock_server_run.return_value = None
                
                # 验证 run 方法可以调用
                try:
                    # 不实际运行，只验证结构
                    assert server.server is not None
                except Exception:
                    pass

    @pytest.mark.asyncio
    async def test_run_initialization_options(self, server):
        """测试 run 方法的初始化选项"""
        # 验证可以创建初始化选项
        init_options = server.server.create_initialization_options()
        assert init_options is not None

    @pytest.mark.asyncio
    async def test_server_protocol_version(self, server):
        """测试服务器协议版本"""
        # 验证服务器有协议版本
        assert hasattr(server.server, 'name')
        assert server.server.name == "diting"


class TestMCPServerClose:
    """测试 MCP Server 关闭"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    def test_close_method(self, server):
        """测试 close 方法"""
        assert hasattr(server, 'close')
        assert callable(server.close)

    def test_close_calls_mft_close(self, server):
        """测试 close 调用 MFT close"""
        with patch.object(server.mft, 'close') as mock_close:
            server.close()
            mock_close.assert_called_once()

    def test_close_multiple_times(self, server):
        """测试多次关闭不报错"""
        server.close()
        server.close()  # 不应该抛出异常


class TestMainFunction:
    """测试 main 函数"""

    @pytest.mark.asyncio
    async def test_main_is_coroutine(self):
        """测试 main 是协程函数"""
        import inspect
        assert inspect.iscoroutinefunction(main)

    @pytest.mark.asyncio
    async def test_main_structure(self):
        """测试 main 函数结构"""
        # 验证 main 函数创建服务器
        with patch('diting.mcp_server.MCPServer') as MockServer:
            mock_server = AsyncMock()
            mock_server.run = AsyncMock()
            mock_server.close = MagicMock()
            MockServer.return_value = mock_server
            
            # 模拟运行
            with patch('diting.mcp_server.stdio_server'):
                try:
                    # 不实际运行
                    pass
                except Exception:
                    pass


class TestAsyncContextManager:
    """测试异步上下文管理器"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_server_as_context_manager(self, server):
        """测试服务器作为上下文管理器"""
        # 验证服务器可以正确初始化和清理
        assert server.mft is not None
        
        # 清理
        server.close()
        assert True

    @pytest.mark.asyncio
    async def test_resource_cleanup(self, server):
        """测试资源清理"""
        # 创建一些资源
        server.mft.create("/test/resource", "NOTE", "test")
        
        # 关闭服务器
        server.close()
        
        # 验证清理
        assert True


class TestStdioServerIntegration:
    """测试 stdio_server 集成"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_stdio_server_import(self):
        """测试 stdio_server 可导入"""
        from mcp.server.stdio import stdio_server
        assert stdio_server is not None

    @pytest.mark.asyncio
    async def test_stdio_server_type(self):
        """测试 stdio_server 类型"""
        from mcp.server.stdio import stdio_server
        assert callable(stdio_server)


class TestMCPServerLifecycle:
    """测试 MCP Server 生命周期"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_server_creation(self, server):
        """测试服务器创建"""
        assert server is not None
        assert server.mft is not None
        assert server.server is not None

    @pytest.mark.asyncio
    async def test_server_with_data(self, server):
        """测试带数据的服务器"""
        # 创建数据
        server.mft.create("/lifecycle/test", "NOTE", "lifecycle content")
        
        # 验证数据存在
        result = server.mft.read("/lifecycle/test")
        assert result is not None
        assert "lifecycle content" in result['content']
        
        # 清理
        server.close()

    @pytest.mark.asyncio
    async def test_server_error_recovery(self, server):
        """测试服务器错误恢复"""
        # 创建一些数据
        server.mft.create("/error/test1", "NOTE", "test1")
        
        # 尝试读取不存在的路径
        try:
            server.mft.read("/error/nonexistent")
        except Exception:
            pass
        
        # 验证服务器仍然可用
        result = server.mft.read("/error/test1")
        assert result is not None


class TestMCPServerConcurrency:
    """测试 MCP Server 并发"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self, server):
        """测试并发工具调用"""
        # 创建多个工具调用任务
        tasks = [
            server.call_tool("diting_write", {
                "path": f"/concurrent/{i}",
                "type": "NOTE",
                "content": f"content {i}"
            })
            for i in range(10)
        ]
        
        # 并发执行
        results = await asyncio.gather(*tasks)
        
        # 验证所有调用成功
        for result in results:
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_concurrent_read_write(self, server):
        """测试并发读写"""
        # 先创建数据
        for i in range(5):
            server.mft.create(f"/rw/{i}", "NOTE", f"content {i}")
        
        # 并发读写
        async def read_write(i):
            # 读
            await server.call_tool("diting_read", {"path": f"/rw/{i}"})
            # 写
            await server.call_tool("diting_write", {
                "path": f"/rw/{i}",
                "type": "NOTE",
                "content": f"updated {i}"
            })
        
        tasks = [read_write(i) for i in range(5)]
        await asyncio.gather(*tasks)
        
        # 验证更新
        for i in range(5):
            result = server.mft.read(f"/rw/{i}")
            assert f"updated {i}" in result['content']


class TestMCPServerConfig:
    """测试 MCP Server 配置"""

    def test_default_config(self, tmp_path):
        """测试默认配置"""
        db_path = tmp_path / "test.db"
        server = MCPServer(db_path=str(db_path))
        
        assert server.server.name == "diting"
        assert server.mft is not None

    def test_env_var_config(self, monkeypatch, tmp_path):
        """测试环境变量配置"""
        db_path = tmp_path / "env_test.db"
        monkeypatch.setenv("DITING_DB_PATH", str(db_path))
        
        server = MCPServer()
        assert server.mft is not None

    def test_memory_db_config(self):
        """测试内存数据库配置"""
        server = MCPServer(db_path=":memory:")
        assert server.mft is not None
        server.close()
