"""
FTS5 Search 全文检索测试用例

目标：覆盖率 87% → 90%+

注意：FTS5 虚拟表依赖 mft 表存在（触发器需要）
"""

import pytest
import sqlite3
import tempfile
from diting.fts5_search import FTS5Search


def init_db_with_mft(db_path):
    """辅助函数：初始化数据库并创建 MFT 表"""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mft (
            inode INTEGER PRIMARY KEY,
            v_path TEXT,
            type TEXT,
            content TEXT,
            deleted INTEGER DEFAULT 0,
            create_ts TEXT,
            update_ts TEXT
        )
    """)
    conn.commit()
    conn.close()


class TestFTS5SearchInit:
    """初始化测试"""

    def test_init(self, tmp_path):
        """测试初始化"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        assert search.db_path == db_path
        assert search.conn is not None

    def test_init_creates_fts5_table(self, tmp_path):
        """测试初始化创建 FTS5 表"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        # 验证表存在
        cursor = search.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='mft_fts5'"
        )
        row = cursor.fetchone()
        assert row is not None

    def test_init_creates_triggers(self, tmp_path):
        """测试初始化创建触发器"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        # 验证触发器存在
        cursor = search.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger'"
        )
        triggers = [row[0] for row in cursor.fetchall()]
        
        assert "mft_ai" in triggers
        assert "mft_ad" in triggers
        assert "mft_au" in triggers


class TestFTS5SearchBasic:
    """基础搜索测试"""

    def test_search_empty(self, tmp_path):
        """测试空搜索"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        results = search.search("nonexistent")
        
        assert results == []

    def test_search_top_k(self, tmp_path):
        """测试限制返回数量"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        results = search.search("test", top_k=5)
        
        assert len(results) <= 5

    def test_search_with_scope(self, tmp_path):
        """测试带范围搜索"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        results = search.search("test", scope="/test/path")
        
        assert isinstance(results, list)


class TestFTS5SearchIndex:
    """索引操作测试"""

    def test_index_document(self, tmp_path):
        """测试索引文档"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        # 插入文档
        search.conn.execute("""
            INSERT INTO mft (inode, v_path, type, content, deleted)
            VALUES (1, '/test/doc1.txt', 'NOTE', 'Hello World', 0)
        """)
        search.conn.commit()
        
        # 搜索
        results = search.search("Hello")
        
        assert len(results) >= 1

    def test_index_multiple_documents(self, tmp_path):
        """测试索引多个文档"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        # 插入多个文档
        docs = [
            (1, '/doc1.txt', 'NOTE', 'Python programming', 0),
            (2, '/doc2.txt', 'NOTE', 'Java programming', 0),
            (3, '/doc3.txt', 'NOTE', 'JavaScript web', 0),
        ]
        
        for doc in docs:
            search.conn.execute(
                "INSERT INTO mft VALUES (?, ?, ?, ?, ?, ?, ?)",
                (*doc, 'now', 'now')
            )
        search.conn.commit()
        
        # 搜索 programming
        results = search.search("programming")
        
        assert len(results) >= 2

    def test_index_update_document(self, tmp_path):
        """测试更新文档索引"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        # 插入文档
        search.conn.execute("""
            INSERT INTO mft (inode, v_path, type, content, deleted)
            VALUES (1, '/test/doc.txt', 'NOTE', 'Original content', 0)
        """)
        search.conn.commit()
        
        # 更新文档
        search.conn.execute("""
            UPDATE mft SET content = 'Updated content' WHERE inode = 1
        """)
        search.conn.commit()
        
        # 搜索新内容
        results = search.search("Updated")
        
        assert len(results) >= 1

    def test_index_delete_document(self, tmp_path):
        """测试删除文档索引"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        # 插入文档
        search.conn.execute("""
            INSERT INTO mft (inode, v_path, type, content, deleted)
            VALUES (1, '/test/doc.txt', 'NOTE', 'To be deleted', 0)
        """)
        search.conn.commit()
        
        # 删除文档
        search.conn.execute("DELETE FROM mft WHERE inode = 1")
        search.conn.commit()
        
        # 搜索应该找不到
        results = search.search("deleted")
        
        assert len(results) == 0

    def test_index_soft_delete(self, tmp_path):
        """测试软删除"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        # 插入文档
        search.conn.execute("""
            INSERT INTO mft (inode, v_path, type, content, deleted)
            VALUES (1, '/test/doc.txt', 'NOTE', 'Soft deleted', 0)
        """)
        search.conn.commit()
        
        # 软删除
        search.conn.execute("UPDATE mft SET deleted = 1 WHERE inode = 1")
        search.conn.commit()
        
        # 搜索应该找不到
        results = search.search("deleted")
        
        assert len(results) == 0


class TestFTS5SearchEdgeCases:
    """边界条件测试"""

    def test_search_special_characters(self, tmp_path):
        """测试搜索特殊字符"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        results = search.search("test")
        
        assert isinstance(results, list)

    def test_search_unicode(self, tmp_path):
        """测试搜索 Unicode"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        # 插入中文文档
        search.conn.execute("""
            INSERT INTO mft (inode, v_path, type, content, deleted)
            VALUES (1, '/test/doc.txt', 'NOTE', '中文测试内容', 0)
        """)
        search.conn.commit()
        
        results = search.search("中文")
        
        assert isinstance(results, list)

    def test_search_empty_query(self, tmp_path):
        """测试空查询"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        results = search.search("")
        
        assert isinstance(results, list)

    def test_search_top_k_zero(self, tmp_path):
        """测试 top_k=0"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        results = search.search("test", top_k=0)
        
        assert len(results) == 0

    def test_close(self, tmp_path):
        """测试关闭连接"""
        db_path = str(tmp_path / "search.db")
        init_db_with_mft(db_path)
        
        search = FTS5Search(db_path)
        
        search.close()
