"""
知识图谱工具详细测试

测试 KG 工具的所有功能和边缘情况
"""

import pytest
from diting.mcp_server import MCPServer
from diting.knowledge_graph_v2 import KnowledgeGraphV2


class TestKGSearchDetailed:
    """详细的 KG 搜索测试"""

    @pytest.fixture
    def server_with_kg(self, tmp_path):
        """创建带 KG 的测试服务器"""
        db_path = tmp_path / "test.db"
        kg_db_path = tmp_path / "test_kg.db"
        server = MCPServer(db_path=str(db_path))
        
        # 添加测试概念
        if server.mft.kg:
            server.mft.kg.add_concept("python", "technology")
            server.mft.kg.add_concept("programming", "activity")
            server.mft.kg.add_concept("language", "concept")
            server.mft.kg.add_edge("python", "programming", "is_a")
            server.mft.kg.add_edge("programming", "language", "related")
        
        return server

    @pytest.mark.asyncio
    async def test_kg_search_with_results(self, server_with_kg):
        """测试 kg_search 有结果"""
        if not server_with_kg.mft.kg:
            pytest.skip("KG not available")
        
        result = await server_with_kg.call_tool("kg_search", {"query": "python"})
        assert len(result) == 1
        assert "python" in result[0].text

    @pytest.mark.asyncio
    async def test_kg_search_with_depth(self, server_with_kg):
        """测试 kg_search 带深度参数"""
        if not server_with_kg.mft.kg:
            pytest.skip("KG not available")
        
        result = await server_with_kg.call_tool("kg_search", {
            "query": "python",
            "max_depth": 3
        })
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_kg_search_empty_query(self, server_with_kg):
        """测试 kg_search 空查询"""
        if not server_with_kg.mft.kg:
            pytest.skip("KG not available")
        
        result = await server_with_kg.call_tool("kg_search", {"query": ""})
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_kg_search_no_expansion(self, server_with_kg):
        """测试 kg_search 无扩展"""
        if not server_with_kg.mft.kg:
            pytest.skip("KG not available")
        
        result = await server_with_kg.call_tool("kg_search", {
            "query": "nonexistent_concept"
        })
        assert len(result) == 1


class TestKGGetRelatedDetailed:
    """详细的 KG 关联概念测试"""

    @pytest.fixture
    def server_with_kg(self, tmp_path):
        """创建带 KG 的测试服务器"""
        db_path = tmp_path / "test.db"
        kg_db_path = tmp_path / "test_kg.db"
        server = MCPServer(db_path=str(db_path))
        
        # 添加测试概念和边
        if server.mft.kg:
            server.mft.kg.add_concept("AI", "field")
            server.mft.kg.add_concept("Machine Learning", "technology")
            server.mft.kg.add_concept("Deep Learning", "technology")
            server.mft.kg.add_edge("AI", "Machine Learning", "includes")
            server.mft.kg.add_edge("Machine Learning", "Deep Learning", "includes")
        
        return server

    @pytest.mark.asyncio
    async def test_kg_get_related_with_results(self, server_with_kg):
        """测试 kg_get_related 有结果"""
        if not server_with_kg.mft.kg:
            pytest.skip("KG not available")
        
        result = await server_with_kg.call_tool("kg_get_related", {
            "concept": "AI"
        })
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_kg_get_related_with_top_k(self, server_with_kg):
        """测试 kg_get_related 带 top_k 参数"""
        if not server_with_kg.mft.kg:
            pytest.skip("KG not available")
        
        result = await server_with_kg.call_tool("kg_get_related", {
            "concept": "AI",
            "top_k": 10
        })
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_kg_get_related_no_connections(self, server_with_kg):
        """测试 kg_get_related 无关联"""
        if not server_with_kg.mft.kg:
            pytest.skip("KG not available")
        
        # 添加一个孤立概念
        server_with_kg.mft.kg.add_concept("isolated", "concept")
        
        result = await server_with_kg.call_tool("kg_get_related", {
            "concept": "isolated"
        })
        assert len(result) == 1
        assert "没有关联" in result[0].text or "关联概念" in result[0].text


class TestKGStatsDetailed:
    """详细的 KG 统计测试"""

    @pytest.fixture
    def server_with_populated_kg(self, tmp_path):
        """创建带 populated KG 的测试服务器"""
        db_path = tmp_path / "test.db"
        kg_db_path = tmp_path / "test_kg.db"
        server = MCPServer(db_path=str(db_path))
        
        # 添加多个概念和边
        if server.mft.kg:
            concepts = [("A", "concept"), ("B", "concept"), ("C", "concept"), ("D", "concept"), ("E", "concept")]
            for c, t in concepts:
                server.mft.kg.add_concept(c, t)
            
            # 添加边
            server.mft.kg.add_edge("A", "B", "rel1")
            server.mft.kg.add_edge("B", "C", "rel2")
            server.mft.kg.add_edge("C", "D", "rel3")
        
        return server

    @pytest.mark.asyncio
    async def test_kg_stats_with_data(self, server_with_populated_kg):
        """测试 kg_stats 有数据"""
        if not server_with_populated_kg.mft.kg:
            pytest.skip("KG not available")
        
        result = await server_with_populated_kg.call_tool("kg_stats", {})
        assert len(result) == 1
        assert "概念数" in result[0].text or "概念" in result[0].text

    @pytest.mark.asyncio
    async def test_kg_stats_empty(self, tmp_path):
        """测试 kg_stats 空图谱"""
        db_path = tmp_path / "test.db"
        server = MCPServer(db_path=str(db_path))
        
        if not server.mft.kg:
            pytest.skip("KG not available")
        
        result = await server.call_tool("kg_stats", {})
        assert len(result) == 1


class TestKGEdgeCases:
    """KG 工具边界情况测试"""

    @pytest.fixture
    def server_with_kg(self, tmp_path):
        """创建带 KG 的测试服务器"""
        db_path = tmp_path / "test.db"
        kg_db_path = tmp_path / "test_kg.db"
        server = MCPServer(db_path=str(db_path))
        
        # 添加测试数据
        if server.mft.kg:
            server.mft.kg.add_concept("test", "concept")
            server.mft.kg.add_concept("测试", "concept")  # Unicode 概念
        
        return server

    @pytest.mark.asyncio
    async def test_kg_search_unicode(self, server_with_kg):
        """测试 kg_search Unicode 查询"""
        if not server_with_kg.mft.kg:
            pytest.skip("KG not available")
        
        result = await server_with_kg.call_tool("kg_search", {"query": "测试"})
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_kg_get_related_unicode(self, server_with_kg):
        """测试 kg_get_related Unicode 概念"""
        if not server_with_kg.mft.kg:
            pytest.skip("KG not available")
        
        result = await server_with_kg.call_tool("kg_get_related", {
            "concept": "测试"
        })
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_kg_search_special_chars(self, server_with_kg):
        """测试 kg_search 特殊字符"""
        if not server_with_kg.mft.kg:
            pytest.skip("KG not available")
        
        result = await server_with_kg.call_tool("kg_search", {
            "query": "test@#$%"
        })
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_kg_get_related_null_concept(self, server_with_kg):
        """测试 kg_get_related null 概念"""
        if not server_with_kg.mft.kg:
            pytest.skip("KG not available")
        
        result = await server_with_kg.call_tool("kg_get_related", {
            "concept": None
        })
        assert "错误" in result[0].text


class TestKGWithMFTIntegration:
    """KG 与 MFT 集成测试"""

    @pytest.fixture
    def server_with_full_data(self, tmp_path):
        """创建带完整数据的测试服务器"""
        db_path = tmp_path / "test.db"
        kg_db_path = tmp_path / "test_kg.db"
        server = MCPServer(db_path=str(db_path))
        
        # 添加记忆和 KG 概念
        if server.mft.kg:
            server.mft.create("/kg/python", "NOTE", "Python programming language")
            server.mft.create("/kg/ml", "NOTE", "Machine Learning")
            server.mft.kg.add_concept("Python", "language")
            server.mft.kg.add_concept("ML", "field")
            server.mft.kg.add_edge("Python", "ML", "used_in")
        
        return server

    @pytest.mark.asyncio
    async def test_kg_search_after_memory_create(self, server_with_full_data):
        """测试创建记忆后 KG 搜索"""
        if not server_with_full_data.mft.kg:
            pytest.skip("KG not available")
        
        # 创建新记忆
        server_with_full_data.mft.create("/kg/new", "NOTE", "Deep Learning")
        
        # KG 搜索
        result = await server_with_full_data.call_tool("kg_search", {"query": "Python"})
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_kg_stats_after_multiple_operations(self, server_with_full_data):
        """测试多次操作后 KG 统计"""
        if not server_with_full_data.mft.kg:
            pytest.skip("KG not available")
        
        # 多次添加概念
        server_with_full_data.mft.kg.add_concept("AI", "field")
        server_with_full_data.mft.kg.add_concept("NLP", "field")
        server_with_full_data.mft.kg.add_edge("AI", "NLP", "includes")
        
        # 获取统计
        result = await server_with_full_data.call_tool("kg_stats", {})
        assert "概念数" in result[0].text or "概念" in result[0].text


class TestKGPerformance:
    """KG 性能测试"""

    @pytest.fixture
    def server_with_large_kg(self, tmp_path):
        """创建带大型 KG 的测试服务器"""
        db_path = tmp_path / "test.db"
        kg_db_path = tmp_path / "test_kg.db"
        server = MCPServer(db_path=str(db_path))
        
        # 添加大量概念
        if server.mft.kg:
            for i in range(50):
                server.mft.kg.add_concept(f"concept_{i}", "concept")
                if i > 0:
                    server.mft.kg.add_edge(f"concept_{i-1}", f"concept_{i}", "related")
        
        return server

    @pytest.mark.asyncio
    async def test_kg_search_performance(self, server_with_large_kg):
        """测试 kg_search 性能"""
        if not server_with_large_kg.mft.kg:
            pytest.skip("KG not available")
        
        import time
        start = time.time()
        
        result = await server_with_large_kg.call_tool("kg_search", {
            "query": "concept_25"
        })
        
        elapsed = time.time() - start
        assert elapsed < 5.0  # 应该在 5 秒内完成
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_kg_get_related_performance(self, server_with_large_kg):
        """测试 kg_get_related 性能"""
        if not server_with_large_kg.mft.kg:
            pytest.skip("KG not available")
        
        import time
        start = time.time()
        
        result = await server_with_large_kg.call_tool("kg_get_related", {
            "concept": "concept_25",
            "top_k": 10
        })
        
        elapsed = time.time() - start
        assert elapsed < 5.0
        assert len(result) == 1
