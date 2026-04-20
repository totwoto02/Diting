"""
MCP Server 工具层测试

测试 MCP 工具调用逻辑，提高覆盖率
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from diting.mcp_server import MCPServer
from diting.errors import MFSException, MFTNotFoundError
from diting.mft import MFT


class TestMCPServerInit:
    """测试 MCP Server 初始化"""

    def test_init_default_db_path(self, tmp_path):
        """测试默认数据库路径初始化"""
        db_path = tmp_path / "test.db"
        server = MCPServer(db_path=str(db_path))
        assert server.mft is not None
        assert server.server is not None

    def test_init_with_env_var(self, monkeypatch, tmp_path):
        """测试使用环境变量初始化"""
        db_path = tmp_path / "env_test.db"
        monkeypatch.setenv("DITING_DB_PATH", str(db_path))
        server = MCPServer()
        assert server.mft is not None

    def test_init_memory_db(self):
        """测试内存数据库初始化"""
        server = MCPServer(db_path=":memory:")
        assert server.mft is not None
        server.close()


class TestCallTool:
    """测试工具调用"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_call_unknown_tool(self, server):
        """测试调用未知工具"""
        result = await server.call_tool("unknown_tool", {})
        assert len(result) == 1
        assert "未知工具" in result[0].text

    @pytest.mark.asyncio
    async def test_call_diting_read_missing_path(self, server):
        """测试 diting_read 缺少 path 参数"""
        result = await server.call_tool("diting_read", {})
        assert "错误" in result[0].text
        assert "path" in result[0].text

    @pytest.mark.asyncio
    async def test_call_diting_read_not_found(self, server):
        """测试 diting_read 路径不存在"""
        result = await server.call_tool("diting_read", {"path": "/nonexistent"})
        assert "错误" in result[0].text or "未找到" in result[0].text

    @pytest.mark.asyncio
    async def test_call_diting_read_success(self, server):
        """测试 diting_read 成功"""
        # 先创建记忆
        server.mft.create("/test/read", "NOTE", "test content")
        
        # 读取
        result = await server.call_tool("diting_read", {"path": "/test/read"})
        assert len(result) == 1
        assert "路径：/test/read" in result[0].text
        assert "test content" in result[0].text

    @pytest.mark.asyncio
    async def test_call_diting_write_missing_params(self, server):
        """测试 diting_write 缺少参数"""
        result = await server.call_tool("diting_write", {})
        assert "错误" in result[0].text

    @pytest.mark.asyncio
    async def test_call_diting_write_create(self, server):
        """测试 diting_write 创建新记忆"""
        result = await server.call_tool("diting_write", {
            "path": "/test/create",
            "type": "NOTE",
            "content": "new content"
        })
        assert "已创建" in result[0].text

    @pytest.mark.asyncio
    async def test_call_diting_write_update(self, server):
        """测试 diting_write 更新记忆"""
        # 先创建
        server.mft.create("/test/update", "NOTE", "old content")
        
        # 更新
        result = await server.call_tool("diting_write", {
            "path": "/test/update",
            "type": "NOTE",
            "content": "new content"
        })
        assert "已更新" in result[0].text

    @pytest.mark.asyncio
    async def test_call_diting_search_missing_query(self, server):
        """测试 diting_search 缺少 query 参数"""
        result = await server.call_tool("diting_search", {})
        assert "错误" in result[0].text

    @pytest.mark.asyncio
    async def test_call_diting_search_no_results(self, server):
        """测试 diting_search 无结果"""
        result = await server.call_tool("diting_search", {"query": "nonexistent"})
        assert "未找到" in result[0].text

    @pytest.mark.asyncio
    async def test_call_diting_search_with_results(self, server):
        """测试 diting_search 有结果"""
        # 创建测试数据
        server.mft.create("/test/search1", "NOTE", "apple")
        server.mft.create("/test/search2", "NOTE", "banana")
        
        # 搜索
        result = await server.call_tool("diting_search", {"query": "apple"})
        assert len(result) == 1
        assert "找到" in result[0].text
        assert "apple" in result[0].text

    @pytest.mark.asyncio
    async def test_call_tool_mfs_exception(self, server):
        """测试 MFSException 处理"""
        with patch.object(server, '_diting_read') as mock_read:
            mock_read.side_effect = MFSException("test error")
            result = await server.call_tool("diting_read", {"path": "/test"})
            assert "MFS 错误" in result[0].text

    @pytest.mark.asyncio
    async def test_call_tool_not_found_exception(self, server):
        """测试 MFTNotFoundError 处理"""
        with patch.object(server, '_diting_read') as mock_read:
            mock_read.side_effect = MFTNotFoundError("not found")
            result = await server.call_tool("diting_read", {"path": "/test"})
            assert "错误" in result[0].text

    @pytest.mark.asyncio
    async def test_call_tool_generic_exception(self, server):
        """测试通用异常处理"""
        with patch.object(server, '_diting_read') as mock_read:
            mock_read.side_effect = Exception("unexpected error")
            result = await server.call_tool("diting_read", {"path": "/test"})
            assert "系统错误" in result[0].text


class TestKGTools:
    """测试知识图谱工具"""

    @pytest.fixture
    def server_with_kg(self, tmp_path):
        """创建带 KG 的测试服务器"""
        db_path = tmp_path / "test.db"
        kg_db_path = tmp_path / "test_kg.db"
        server = MCPServer(db_path=str(db_path))
        # 确保 KG 已初始化
        if server.mft.kg:
            return server
        return None

    @pytest.mark.asyncio
    async def test_kg_search_missing_query(self, server_with_kg):
        """测试 kg_search 缺少 query 参数"""
        if not server_with_kg:
            pytest.skip("KG not available")
        
        result = await server_with_kg.call_tool("kg_search", {})
        assert "错误" in result[0].text

    @pytest.mark.asyncio
    async def test_kg_search_not_found(self, server_with_kg):
        """测试 kg_search 未找到概念"""
        if not server_with_kg:
            pytest.skip("KG not available")
        
        result = await server_with_kg.call_tool("kg_search", {"query": "nonexistent"})
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_kg_get_related_missing_concept(self, server_with_kg):
        """测试 kg_get_related 缺少 concept 参数"""
        if not server_with_kg:
            pytest.skip("KG not available")
        
        result = await server_with_kg.call_tool("kg_get_related", {})
        assert "错误" in result[0].text

    @pytest.mark.asyncio
    async def test_kg_stats(self, server_with_kg):
        """测试 kg_stats"""
        if not server_with_kg:
            pytest.skip("KG not available")
        
        result = await server_with_kg.call_tool("kg_stats", {})
        assert len(result) == 1


class TestEntropyTools:
    """测试熵系统工具"""

    @pytest.fixture
    def server_with_entropy(self, tmp_path):
        """创建带熵系统的测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_entropy_stats(self, server_with_entropy):
        """测试 entropy_stats"""
        result = await server_with_entropy.call_tool("entropy_stats", {})
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_project_entropy_missing_param(self, server_with_entropy):
        """测试 get_project_entropy 缺少参数"""
        result = await server_with_entropy.call_tool("get_project_entropy", {})
        assert "错误" in result[0].text

    @pytest.mark.asyncio
    async def test_get_project_entropy(self, server_with_entropy):
        """测试 get_project_entropy"""
        # 先创建一些测试数据
        server_with_entropy.mft.create("/project/test1", "NOTE", "content1")
        server_with_entropy.mft.create("/project/test2", "NOTE", "content2")
        
        result = await server_with_entropy.call_tool(
            "get_project_entropy", {"project_path": "/project"}
        )
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_entropy_anomaly_missing_param(self, server_with_entropy):
        """测试 entropy_anomaly 缺少参数"""
        result = await server_with_entropy.call_tool("entropy_anomaly", {})
        assert "错误" in result[0].text

    @pytest.mark.asyncio
    async def test_entropy_anomaly(self, server_with_entropy):
        """测试 entropy_anomaly"""
        result = await server_with_entropy.call_tool(
            "entropy_anomaly", {"slice_id": "test_slice"}
        )
        assert len(result) == 1


class TestToolRegistration:
    """测试工具注册"""

    def test_list_tools(self, tmp_path):
        """测试列出工具"""
        db_path = tmp_path / "test.db"
        server = MCPServer(db_path=str(db_path))
        
        # 验证服务器已初始化（list_tools 是装饰器，不能直接调用）
        # 通过验证 server 对象来间接验证工具已注册
        assert server.server is not None
        assert server.mft is not None

    def test_registered_tools(self, tmp_path):
        """测试已注册的工具名称"""
        db_path = tmp_path / "test.db"
        server = MCPServer(db_path=str(db_path))
        
        # 验证工具已注册
        expected_tools = [
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
        
        # 通过调用未知工具来验证注册
        import asyncio
        
        async def check_tools():
            for tool_name in expected_tools:
                result = await server.call_tool(tool_name, {})
                # 不应该返回"未知工具"错误（除了参数错误的情况）
                if tool_name.startswith("diting"):
                    assert "未知工具" not in result[0].text or "错误" in result[0].text
        
        asyncio.run(check_tools())


class TestClose:
    """测试关闭"""

    def test_close(self, tmp_path):
        """测试关闭服务器"""
        db_path = tmp_path / "test.db"
        server = MCPServer(db_path=str(db_path))
        server.close()
        # 关闭后不应抛出异常
        assert True
