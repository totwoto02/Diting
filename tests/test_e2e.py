"""
MCP 端到端协议测试

测试完整的 MCP 协议交互流程
"""

import pytest
import asyncio
from diting.mcp_server import MCPServer


class TestEndToEndWorkflow:
    """端到端工作流测试"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_full_crud_workflow(self, server):
        """测试完整的 CRUD 工作流"""
        # 1. Create - 创建记忆
        create_result = await server.call_tool("diting_write", {
            "path": "/e2e/crud",
            "type": "NOTE",
            "content": "initial content"
        })
        assert "已创建" in create_result[0].text
        
        # 2. Read - 读取记忆
        read_result = await server.call_tool("diting_read", {"path": "/e2e/crud"})
        assert "initial content" in read_result[0].text
        
        # 3. Update - 更新记忆
        update_result = await server.call_tool("diting_write", {
            "path": "/e2e/crud",
            "type": "NOTE",
            "content": "updated content"
        })
        assert "已更新" in update_result[0].text
        
        # 4. Read - 验证更新
        read_result = await server.call_tool("diting_read", {"path": "/e2e/crud"})
        assert "updated content" in read_result[0].text
        
        # 5. Search - 搜索记忆
        search_result = await server.call_tool("diting_search", {"query": "updated"})
        assert "/e2e/crud" in search_result[0].text

    @pytest.mark.asyncio
    async def test_multi_user_workflow(self, server):
        """测试多用户工作流"""
        # 用户 A 创建记忆
        await server.call_tool("diting_write", {
            "path": "/e2e/userA",
            "type": "NOTE",
            "content": "User A content"
        })
        
        # 用户 B 创建记忆
        await server.call_tool("diting_write", {
            "path": "/e2e/userB",
            "type": "NOTE",
            "content": "User B content"
        })
        
        # 用户 A 搜索自己的记忆
        result = await server.call_tool("diting_search", {"query": "User A"})
        assert "userA" in result[0].text
        
        # 用户 B 搜索自己的记忆
        result = await server.call_tool("diting_search", {"query": "User B"})
        assert "userB" in result[0].text

    @pytest.mark.asyncio
    async def test_nested_path_workflow(self, server):
        """测试嵌套路径工作流"""
        # 创建深层路径
        path = "/e2e/level1/level2/level3/level4"
        result = await server.call_tool("diting_write", {
            "path": path,
            "type": "NOTE",
            "content": "deep content"
        })
        assert "已创建" in result[0].text
        
        # 读取
        result = await server.call_tool("diting_read", {"path": path})
        assert "deep content" in result[0].text
        
        # 搜索
        result = await server.call_tool("diting_search", {"query": "deep"})
        assert "level4" in result[0].text


class TestEndToEndErrorHandling:
    """端到端错误处理测试"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, server):
        """测试错误恢复工作流"""
        # 1. 尝试读取不存在的路径
        result = await server.call_tool("diting_read", {"path": "/nonexistent"})
        assert len(result) == 1
        
        # 2. 创建路径
        result = await server.call_tool("diting_write", {
            "path": "/e2e/recovery",
            "type": "NOTE",
            "content": "recovery content"
        })
        assert "已创建" in result[0].text
        
        # 3. 验证可以正常读取
        result = await server.call_tool("diting_read", {"path": "/e2e/recovery"})
        assert "recovery content" in result[0].text

    @pytest.mark.asyncio
    async def test_invalid_input_handling(self, server):
        """测试无效输入处理"""
        # 缺少必需参数
        result = await server.call_tool("diting_write", {
            "path": "/e2e/invalid"
            # 缺少 type 和 content
        })
        assert "错误" in result[0].text
        
        # 服务器仍然可用
        result = await server.call_tool("diting_write", {
            "path": "/e2e/valid",
            "type": "NOTE",
            "content": "valid content"
        })
        assert "已创建" in result[0].text


class TestEndToEndPerformance:
    """端到端性能测试"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_bulk_create_performance(self, server):
        """测试批量创建性能"""
        import time
        
        start = time.time()
        
        # 批量创建 50 个记忆
        tasks = [
            server.call_tool("diting_write", {
                "path": f"/e2e/bulk/{i}",
                "type": "NOTE",
                "content": f"bulk content {i}"
            })
            for i in range(50)
        ]
        
        results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start
        
        # 验证所有创建成功
        for result in results:
            assert "已创建" in result[0].text
        
        # 性能检查（应该在 5 秒内完成）
        assert elapsed < 5.0

    @pytest.mark.asyncio
    async def test_bulk_search_performance(self, server):
        """测试批量搜索性能"""
        import time
        
        # 先创建数据
        for i in range(20):
            await server.call_tool("diting_write", {
                "path": f"/e2e/search/{i}",
                "type": "NOTE",
                "content": f"search content {i}"
            })
        
        start = time.time()
        
        # 批量搜索
        tasks = [
            server.call_tool("diting_search", {"query": f"content {i}"})
            for i in range(20)
        ]
        
        results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start
        
        # 验证所有搜索有结果
        for result in results:
            assert "找到" in result[0].text
        
        # 性能检查
        assert elapsed < 5.0


class TestEndToEndConsistency:
    """端到端一致性测试"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_read_after_write_consistency(self, server):
        """测试写后读一致性"""
        # 写入
        await server.call_tool("diting_write", {
            "path": "/e2e/consistency",
            "type": "NOTE",
            "content": "consistent content"
        })
        
        # 立即读取
        result = await server.call_tool("diting_read", {"path": "/e2e/consistency"})
        
        # 验证一致性
        assert "consistent content" in result[0].text

    @pytest.mark.asyncio
    async def test_search_after_write_consistency(self, server):
        """测试写后搜索一致性"""
        # 写入
        await server.call_tool("diting_write", {
            "path": "/e2e/search_consistency",
            "type": "NOTE",
            "content": "searchable content unique_12345"
        })
        
        # 立即搜索
        result = await server.call_tool("diting_search", {"query": "unique_12345"})
        
        # 验证可搜索
        assert "search_consistency" in result[0].text


class TestEndToEndIntegration:
    """端到端集成测试"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        kg_db_path = tmp_path / "test_kg.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_memory_and_kg_integration(self, server):
        """测试记忆和 KG 集成"""
        # 创建记忆
        await server.call_tool("diting_write", {
            "path": "/e2e/integration",
            "type": "NOTE",
            "content": "integration test"
        })
        
        # KG 工具可用
        result = await server.call_tool("kg_stats", {})
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_all_tools_available(self, server):
        """测试所有工具可用"""
        tools = [
            "diting_read",
            "diting_write",
            "diting_search",
            "kg_stats",
            "entropy_stats"
        ]
        
        for tool in tools:
            result = await server.call_tool(tool, {})
            assert len(result) == 1, f"Tool {tool} failed"


class TestEndToEndScenarios:
    """端到端场景测试"""

    @pytest.fixture
    def server(self, tmp_path):
        """创建测试服务器"""
        db_path = tmp_path / "test.db"
        return MCPServer(db_path=str(db_path))

    @pytest.mark.asyncio
    async def test_knowledge_base_scenario(self, server):
        """测试知识库场景"""
        # 创建知识库
        articles = [
            ("/kb/python", "Python is a programming language"),
            ("/kb/java", "Java is a programming language"),
            ("/kb/javascript", "JavaScript is a scripting language"),
        ]
        
        for path, content in articles:
            await server.call_tool("diting_write", {
                "path": path,
                "type": "NOTE",
                "content": content
            })
        
        # 搜索编程语言
        result = await server.call_tool("diting_search", {"query": "programming language"})
        assert "找到" in result[0].text
        
        # 搜索特定语言
        result = await server.call_tool("diting_search", {"query": "Python"})
        assert "python" in result[0].text

    @pytest.mark.asyncio
    async def test_notes_scenario(self, server):
        """测试笔记场景"""
        # 创建笔记
        notes = [
            ("/notes/meeting_1", "Meeting notes 2026-04-19"),
            ("/notes/idea_1", "Great idea for project"),
            ("/notes/todo_1", "TODO: finish testing"),
        ]
        
        for path, content in notes:
            await server.call_tool("diting_write", {
                "path": path,
                "type": "NOTE",
                "content": content
            })
        
        # 搜索笔记
        result = await server.call_tool("diting_search", {"query": "TODO"})
        assert "todo" in result[0].text
