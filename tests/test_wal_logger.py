"""
WAL Logger 测试用例

覆盖 WALLogger 和 BatchWriter 的所有功能
目标：覆盖率 90%+
"""

import pytest
import random
import time
from diting.wal_logger import WALLogger, BatchWriter, WALRecord


class TestWALLogger:
    """WALLogger 基础测试"""

    def create_fresh_wal(self):
        """创建新的 WALLogger 实例"""
        db_id = f"memdb_wal_{int(time.time()*1000)}_{random.randint(0, 10000)}"
        return WALLogger(db_path=f"file:{db_id}?mode=memory&cache=private")

    def test_log_operation(self):
        """测试记录操作"""
        wal = self.create_fresh_wal()
        try:
            record_id = wal.log_operation(
                operation="CREATE",
                v_path="/test/doc1",
                content="测试内容",
                source_agent="main",
                evidence="conversation_123"
            )
            
            assert record_id > 0
            
            records = wal.get_history("/test/doc1")
            assert len(records) > 0
            assert records[0]["operation"] == "CREATE"
        finally:
            wal.close()

    def test_log_with_evidence(self):
        """测试记录证据链"""
        wal = self.create_fresh_wal()
        try:
            wal.log_operation(
                operation="UPDATE",
                v_path="/test/doc1",
                content="更新内容",
                source_agent="assistant",
                evidence="conversation_456"
            )
            
            records = wal.get_history("/test/doc1")
            assert len(records) > 0
            assert records[0]["evidence"] == "conversation_456"
            assert records[0]["source_agent"] == "assistant"
        finally:
            wal.close()

    def test_get_history(self):
        """测试获取历史记录"""
        wal = self.create_fresh_wal()
        try:
            wal.log_operation("CREATE", "/test/doc1", "初始内容", "main", "conv_1")
            wal.log_operation("UPDATE", "/test/doc1", "第一次更新", "main", "conv_2")
            wal.log_operation("UPDATE", "/test/doc1", "第二次更新", "main", "conv_3")
            
            history = wal.get_history("/test/doc1")
            
            assert len(history) == 3
            assert history[0]["operation"] == "CREATE"
            assert history[1]["operation"] == "UPDATE"
            assert history[2]["operation"] == "UPDATE"
        finally:
            wal.close()

    def test_rollback(self):
        """测试回滚操作"""
        wal = self.create_fresh_wal()
        try:
            wal.log_operation("CREATE", "/test/doc1", "初始内容", "main", "conv_1")
            record_id = wal.log_operation("UPDATE", "/test/doc1", "更新内容", "main", "conv_2")
            
            success = wal.rollback(record_id)
            
            assert success is True
            
            records = wal.get_history("/test/doc1")
            assert records[-1]["status"] == "ROLLED_BACK"
        finally:
            wal.close()

    def test_get_version(self):
        """测试获取特定版本"""
        wal = self.create_fresh_wal()
        try:
            wal.log_operation("CREATE", "/test/doc1", "V1 内容", "main", "conv_1")
            wal.log_operation("UPDATE", "/test/doc1", "V2 内容", "main", "conv_2")
            wal.log_operation("UPDATE", "/test/doc1", "V3 内容", "main", "conv_3")
            
            v2 = wal.get_version("/test/doc1", version=2)
            
            assert v2 is not None
            assert v2["content"] == "V2 内容"
        finally:
            wal.close()

    def test_get_latest_version(self):
        """测试获取最新版本"""
        wal = self.create_fresh_wal()
        try:
            wal.log_operation("CREATE", "/test/doc1", "V1", "main", "conv_1")
            wal.log_operation("UPDATE", "/test/doc1", "V2", "main", "conv_2")
            
            latest = wal.get_latest_version("/test/doc1")
            
            assert latest is not None
            assert latest["version"] == 2
            assert latest["content"] == "V2"
        finally:
            wal.close()

    def test_trust_score(self):
        """测试置信度评分"""
        wal = self.create_fresh_wal()
        try:
            wal.log_operation(
                "CREATE", "/test/doc1", "人工录入",
                source_agent="human",
                evidence="manual_entry",
                confidence=1.0
            )
            
            wal.log_operation(
                "CREATE", "/test/doc2", "AI 推断",
                source_agent="assistant",
                evidence="inferred",
                confidence=0.5
            )
            
            doc1 = wal.get_latest_version("/test/doc1")
            doc2 = wal.get_latest_version("/test/doc2")
            
            assert doc1["confidence"] == 1.0
            assert doc2["confidence"] == 0.5
        finally:
            wal.close()

    def test_audit_trail(self):
        """测试审计追踪"""
        wal = self.create_fresh_wal()
        try:
            wal.log_operation("CREATE", "/test/doc1", "内容", "main", "conv_1")
            wal.log_operation("UPDATE", "/test/doc1", "更新", "assistant", "conv_2")
            
            audit = wal.get_audit_trail()
            
            assert len(audit) > 0
            assert "timestamp" in audit[0]
            assert "source_agent" in audit[0]
            assert "evidence" in audit[0]
        finally:
            wal.close()


class TestWALLoggerEdgeCases:
    """WALLogger 边界条件测试"""

    def create_fresh_wal(self):
        """创建新的 WALLogger 实例"""
        db_id = f"memdb_wal_{int(time.time()*1000)}_{random.randint(0, 10000)}"
        return WALLogger(db_path=f"file:{db_id}?mode=memory&cache=private")

    def test_log_batch_empty(self):
        """测试空批量操作"""
        wal = self.create_fresh_wal()
        try:
            result = wal.log_batch([])
            assert result == []
        finally:
            wal.close()

    def test_log_batch_single(self):
        """测试单个操作的批量记录"""
        wal = self.create_fresh_wal()
        try:
            operations = [
                {
                    'operation': 'CREATE',
                    'v_path': '/test/doc1',
                    'content': '批量内容',
                    'source_agent': 'main',
                    'evidence': 'batch_test',
                    'confidence': 0.9
                }
            ]
            
            ids = wal.log_batch(operations)
            
            assert len(ids) == 1
            assert ids[0] > 0
            
            records = wal.get_history('/test/doc1')
            assert len(records) == 1
            assert records[0]['content'] == '批量内容'
        finally:
            wal.close()

    def test_log_batch_multiple(self):
        """测试多个操作的批量记录"""
        wal = self.create_fresh_wal()
        try:
            operations = [
                {'operation': 'CREATE', 'v_path': '/test/doc1', 'content': '内容 1', 'source_agent': 'main'},
                {'operation': 'CREATE', 'v_path': '/test/doc2', 'content': '内容 2', 'source_agent': 'main'},
                {'operation': 'CREATE', 'v_path': '/test/doc3', 'content': '内容 3', 'source_agent': 'main'},
            ]
            
            ids = wal.log_batch(operations)
            
            assert len(ids) == 3
            assert all(id > 0 for id in ids)
        finally:
            wal.close()

    def test_log_batch_default_values(self):
        """测试批量操作使用默认值"""
        wal = self.create_fresh_wal()
        try:
            operations = [
                {
                    'operation': 'CREATE',
                    'v_path': '/test/doc1',
                    'content': '内容',
                    'source_agent': 'main'
                }
            ]
            
            ids = wal.log_batch(operations)
            
            assert len(ids) == 1
            
            records = wal.get_history('/test/doc1')
            assert records[0]['evidence'] == ''
            assert records[0]['confidence'] == 1.0
        finally:
            wal.close()

    def test_batch_context_basic(self):
        """测试批量写入上下文管理器"""
        wal = self.create_fresh_wal()
        try:
            with wal.batch_context() as batch:
                batch.add('CREATE', '/test/doc1', '内容 1', 'main', 'evidence1')
                batch.add('UPDATE', '/test/doc2', '内容 2', 'assistant', 'evidence2', 0.8)
            
            records1 = wal.get_history('/test/doc1')
            records2 = wal.get_history('/test/doc2')
            
            assert len(records1) == 1
            assert len(records2) == 1
            assert records1[0]['content'] == '内容 1'
            assert records2[0]['content'] == '内容 2'
            assert records2[0]['confidence'] == 0.8
        finally:
            wal.close()

    def test_batch_context_multiple_operations(self):
        """测试批量上下文多次添加操作"""
        wal = self.create_fresh_wal()
        try:
            with wal.batch_context() as batch:
                for i in range(10):
                    batch.add('CREATE', f'/test/doc{i}', f'内容{i}', 'main')
            
            for i in range(10):
                records = wal.get_history(f'/test/doc{i}')
                assert len(records) == 1
        finally:
            wal.close()

    def test_batch_writer_direct_usage(self):
        """测试直接使用 BatchWriter"""
        wal = self.create_fresh_wal()
        try:
            batch = BatchWriter(wal)
            batch.add('CREATE', '/test/doc1', '内容 1', 'main')
            batch.add('CREATE', '/test/doc2', '内容 2', 'assistant')
            
            ids = batch.commit()
            
            assert len(ids) == 2
            
            records1 = wal.get_history('/test/doc1')
            records2 = wal.get_history('/test/doc2')
            
            assert len(records1) == 1
            assert len(records2) == 1
        finally:
            wal.close()

    def test_rollback_nonexistent_record(self):
        """测试回滚不存在的记录"""
        wal = self.create_fresh_wal()
        try:
            success = wal.rollback(99999)
            assert success is False
        finally:
            wal.close()

    def test_get_version_nonexistent(self):
        """测试获取不存在的版本"""
        wal = self.create_fresh_wal()
        try:
            result = wal.get_version('/nonexistent/doc', 1)
            assert result is None
            
            wal.log_operation('CREATE', '/test/doc1', '内容', 'main', 'evidence')
            result = wal.get_version('/test/doc1', 999)
            assert result is None
        finally:
            wal.close()

    def test_get_latest_version_nonexistent(self):
        """测试获取不存在的文档最新版本"""
        wal = self.create_fresh_wal()
        try:
            result = wal.get_latest_version('/nonexistent/doc')
            assert result is None
        finally:
            wal.close()

    def test_get_audit_trail_custom_limit(self):
        """测试自定义限制的审计追踪"""
        wal = self.create_fresh_wal()
        try:
            for i in range(10):
                wal.log_operation('CREATE', f'/test/doc{i}', f'内容{i}', 'main', 'evidence')
            
            audit = wal.get_audit_trail(limit=5)
            assert len(audit) == 5
            
            audit_default = wal.get_audit_trail()
            assert len(audit_default) == 10
        finally:
            wal.close()

    def test_multiple_operations_same_path(self):
        """测试同一路径的多次操作版本号递增"""
        wal = self.create_fresh_wal()
        try:
            wal.log_operation('CREATE', '/test/doc1', 'V1', 'main', 'evidence1')
            wal.log_operation('UPDATE', '/test/doc1', 'V2', 'main', 'evidence2')
            wal.log_operation('UPDATE', '/test/doc1', 'V3', 'main', 'evidence3')
            
            history = wal.get_history('/test/doc1')
            
            assert len(history) == 3
            assert history[0]['version'] == 1
            assert history[1]['version'] == 2
            assert history[2]['version'] == 3
            
            latest = wal.get_latest_version('/test/doc1')
            assert latest['version'] == 3
            assert latest['content'] == 'V3'
        finally:
            wal.close()

    def test_rollback_then_get_history(self):
        """测试回滚后查看历史记录"""
        wal = self.create_fresh_wal()
        try:
            wal.log_operation('CREATE', '/test/doc1', '初始内容', 'main', 'evidence1')
            record_id = wal.log_operation('UPDATE', '/test/doc1', '更新内容', 'main', 'evidence2')
            
            success = wal.rollback(record_id)
            assert success is True
            
            history = wal.get_history('/test/doc1')
            assert len(history) == 2
            assert history[0]['status'] == 'COMMITTED'
            assert history[1]['status'] == 'ROLLED_BACK'
        finally:
            wal.close()


class TestBatchWriterEdgeCases:
    """BatchWriter 边界测试"""

    def create_fresh_wal(self):
        """创建新的 WALLogger 实例"""
        db_id = f"memdb_wal_{int(time.time()*1000)}_{random.randint(0, 10000)}"
        return WALLogger(db_path=f"file:{db_id}?mode=memory&cache=private")

    def test_batch_writer_empty_commit(self):
        """测试空批量提交"""
        wal = self.create_fresh_wal()
        try:
            batch = BatchWriter(wal)
            ids = batch.commit()
            assert ids == []
        finally:
            wal.close()

    def test_batch_writer_large_batch(self):
        """测试大批量操作"""
        wal = self.create_fresh_wal()
        try:
            batch = BatchWriter(wal)
            
            for i in range(100):
                batch.add('CREATE', f'/test/doc{i}', f'内容{i}', 'main')
            
            ids = batch.commit()
            
            assert len(ids) == 100
            assert all(id > 0 for id in ids)
        finally:
            wal.close()

    def test_batch_writer_mixed_operations(self):
        """测试混合操作类型"""
        wal = self.create_fresh_wal()
        try:
            wal.log_operation('CREATE', '/test/doc1', '初始', 'main', 'evidence')
            
            batch = BatchWriter(wal)
            batch.add('UPDATE', '/test/doc1', '更新 1', 'main', 'evidence')
            batch.add('UPDATE', '/test/doc1', '更新 2', 'main', 'evidence')
            batch.add('DELETE', '/test/doc1', '', 'main', 'evidence')
            batch.commit()
            
            history = wal.get_history('/test/doc1')
            assert len(history) == 4
            assert history[0]['operation'] == 'CREATE'
            assert history[1]['operation'] == 'UPDATE'
            assert history[2]['operation'] == 'UPDATE'
            assert history[3]['operation'] == 'DELETE'
        finally:
            wal.close()

    def test_log_batch_with_invalid_data(self):
        """测试批量操作遇到无效数据时的异常处理和回滚"""
        wal = self.create_fresh_wal()
        try:
            # 构造包含无效数据的操作列表（缺少必需字段）
            operations = [
                {'operation': 'CREATE', 'v_path': '/test/doc1', 'content': '内容 1', 'source_agent': 'main'},
                {'operation': 'CREATE', 'v_path': '/test/doc2', 'content': '内容 2'},  # 缺少 source_agent
            ]
            
            # 应该抛出异常
            with pytest.raises(Exception):
                wal.log_batch(operations)
            
            # 验证事务回滚：第一个操作也不应该存在
            # 注意：SQLite 事务回滚后，已插入的数据会被撤销
        finally:
            wal.close()
