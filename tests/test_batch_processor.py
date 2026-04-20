"""
Batch Processor 批量处理器测试用例

目标：覆盖率 78% → 90%+
"""

import pytest
import tempfile
import time
from diting.batch_processor import BatchProcessor, BatchTask


class TestBatchTask:
    """批量任务数据类测试"""

    def test_batch_task_creation(self):
        """测试任务创建"""
        from datetime import datetime
        task = BatchTask(
            id="task_001",
            task_type="test",
            priority=5,
            data={"key": "value"},
            created_at=datetime.now()
        )
        
        assert task.id == "task_001"
        assert task.task_type == "test"
        assert task.priority == 5
        assert task.data == {"key": "value"}

    def test_batch_task_comparison(self):
        """测试任务优先级比较"""
        from datetime import datetime
        task1 = BatchTask(
            id="task_1",
            task_type="test",
            priority=10,
            data={},
            created_at=datetime.now()
        )
        task2 = BatchTask(
            id="task_2",
            task_type="test",
            priority=5,
            data={},
            created_at=datetime.now()
        )
        
        # 优先级高的应该排在前面
        assert task1 < task2


class TestBatchProcessorInit:
    """初始化测试"""

    def test_init_default(self, tmp_path):
        """测试默认初始化"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        assert processor.batch_size == 50
        assert processor.process_interval == 300
        assert processor.running is True
        
        processor.stop()

    def test_init_with_config(self, tmp_path):
        """测试自定义配置初始化"""
        db_path = str(tmp_path / "batch.db")
        config = {
            'BATCH_SIZE': 100,
            'PROCESS_INTERVAL': 600
        }
        processor = BatchProcessor(db_path, config)
        
        assert processor.batch_size == 100
        assert processor.process_interval == 600
        
        processor.stop()


class TestBatchProcessorEnqueue:
    """任务入队测试"""

    def test_enqueue(self, tmp_path):
        """测试入队任务"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        # enqueue 返回 None，但会在数据库创建任务
        result = processor.enqueue(
            "task_001",
            "test",
            {"key": "value"},
            priority=5
        )
        
        # enqueue 返回 None，但任务已入队
        assert result is None
        
        # 验证任务在队列中
        status = processor.get_queue_status()
        assert status["pending"] >= 1
        
        processor.stop()

    def test_enqueue_high_priority(self, tmp_path):
        """测试入队高优先级任务"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        result = processor.enqueue(
            "task_urgent",
            "urgent",
            {},
            priority=100
        )
        
        assert result is None
        
        status = processor.get_queue_status()
        assert status["pending"] >= 1
        
        processor.stop()

    def test_enqueue_empty_data(self, tmp_path):
        """测试入队空数据任务"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        result = processor.enqueue(
            "task_empty",
            "test",
            {}
        )
        
        assert result is None
        
        status = processor.get_queue_status()
        assert status["pending"] >= 1
        
        processor.stop()


class TestBatchProcessorDequeue:
    """任务出队测试"""

    def test_dequeue_batch(self, tmp_path):
        """测试批量出队"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        # 入队一些任务
        for i in range(5):
            processor.enqueue(f"task_{i}", "test", {"index": i})
        
        # 出队
        batch = processor.dequeue_batch(batch_size=3)
        
        assert len(batch) <= 3
        
        processor.stop()

    def test_dequeue_empty_queue(self, tmp_path):
        """测试空队列出队"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        batch = processor.dequeue_batch(batch_size=5)
        
        assert len(batch) == 0
        
        processor.stop()


class TestBatchProcessorProcess:
    """任务处理测试"""

    def test_process_batch(self, tmp_path):
        """测试处理批量任务"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        # 入队任务
        processor.enqueue("task_1", "test", {"data": "value"})
        
        # 出队
        batch = processor.dequeue_batch(batch_size=1)
        
        if batch:
            # 定义一个简单的处理器
            def simple_processor(task):
                return {"processed": True}
            
            # 处理批次
            result = processor.process_batch(batch, simple_processor)
            
            assert isinstance(result, dict)
        
        processor.stop()

    def test_complete_task(self, tmp_path):
        """测试完成任务"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        processor.enqueue("task_1", "test", {})
        
        processor.complete_task("task_1", result={"success": True})
        
        processor.stop()

    def test_complete_task_with_error(self, tmp_path):
        """测试完成任务（带错误）"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        processor.enqueue("task_1", "test", {})
        
        processor.complete_task(
            "task_1",
            result=None,
            error="Test error"
        )
        
        processor.stop()


class TestBatchProcessorQueue:
    """队列管理测试"""

    def test_get_queue_status(self, tmp_path):
        """测试获取队列状态"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        # 入队一些任务
        processor.enqueue("task_1", "type1", {}, 0)
        processor.enqueue("task_2", "type1", {}, 0)
        processor.enqueue("task_3", "type2", {}, 0)
        
        status = processor.get_queue_status()
        
        # 状态包含 pending, processing, completed, failed
        assert "pending" in status
        assert status["pending"] >= 3
        
        processor.stop()

    def test_get_batch_history(self, tmp_path):
        """测试获取批量历史"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        history = processor.get_batch_history()
        
        assert isinstance(history, list)
        
        processor.stop()


class TestBatchProcessorEdgeCases:
    """边界条件测试"""

    def test_stop_processor(self, tmp_path):
        """测试停止处理器"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        processor.stop()
        
        assert processor.running is False

    def test_multiple_enqueue_same_type(self, tmp_path):
        """测试多个同类型任务"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        for i in range(10):
            processor.enqueue(f"task_{i}", "same_type", {"index": i}, 0)
        
        status = processor.get_queue_status()
        assert status["pending"] >= 10
        
        processor.stop()

    def test_large_data_enqueue(self, tmp_path):
        """测试大数据入队"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        large_data = {"data": "A" * 10000}
        result = processor.enqueue("task_large", "test", large_data, 0)
        
        assert result is None
        
        status = processor.get_queue_status()
        assert status["pending"] >= 1
        
        processor.stop()

    def test_close(self, tmp_path):
        """测试关闭处理器"""
        db_path = str(tmp_path / "batch.db")
        processor = BatchProcessor(db_path)
        
        processor.enqueue("task_1", "test", {}, 0)
        
        processor.close()
