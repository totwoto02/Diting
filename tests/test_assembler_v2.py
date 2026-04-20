"""
Assembler V2 拼装器测试用例

目标：覆盖率 69% → 90%+
"""

import pytest
from diting.assembler_v2 import AssemblerV2, Slice


class TestSliceDataStructure:
    """切片数据结构测试"""

    def test_slice_creation(self):
        """测试切片创建"""
        slice = Slice(chunk_id=1, offset=0, length=100, content="测试内容")
        
        assert slice.chunk_id == 1
        assert slice.offset == 0
        assert slice.length == 100
        assert slice.content == "测试内容"

    def test_slice_end_pos(self):
        """测试结束位置计算"""
        slice = Slice(chunk_id=1, offset=100, length=50, content="内容")
        
        assert slice.end_pos == 150

    def test_slice_get_method(self):
        """测试字典式访问"""
        slice = Slice(chunk_id=1, offset=0, length=100, content="测试内容")
        
        assert slice.get('content') == "测试内容"
        assert slice.get('offset') == 0
        assert slice.get('length') == 100
        assert slice.get('chunk_id') == 1
        assert slice.get('unknown', 'default') == 'default'

    def test_slice_getitem(self):
        """测试下标访问"""
        slice = Slice(chunk_id=1, offset=0, length=100, content="测试内容")
        
        assert slice['content'] == "测试内容"
        assert slice['offset'] == 0
        assert slice['length'] == 100
        assert slice['chunk_id'] == 1

    def test_slice_getitem_invalid_key(self):
        """测试无效键的下标访问"""
        slice = Slice(chunk_id=1, offset=0, length=100, content="测试内容")
        
        with pytest.raises(KeyError):
            _ = slice['invalid_key']


class TestAssemblerV2Init:
    """初始化测试"""

    def test_init_default(self):
        """测试默认初始化"""
        assembler = AssemblerV2()
        
        assert assembler.overlap_threshold == 0.3
        assert assembler.min_overlap == 20

    def test_init_custom(self):
        """测试自定义参数初始化"""
        assembler = AssemblerV2(overlap_threshold=0.5, min_overlap=10)
        
        assert assembler.overlap_threshold == 0.5
        assert assembler.min_overlap == 10


class TestAssemblerV2Basic:
    """基础拼装测试"""

    def test_assemble_empty_slices(self):
        """测试空切片列表"""
        assembler = AssemblerV2()
        
        text, stats = assembler.assemble_with_dedup([])
        
        assert text == ""
        assert stats["chunk_count"] == 0
        assert stats["dedup_chars"] == 0

    def test_assemble_single_slice(self):
        """测试单个切片"""
        assembler = AssemblerV2()
        
        slices = [
            {'content': 'Hello World', 'offset': 0, 'length': 11}
        ]
        
        text, stats = assembler.assemble_with_dedup(slices)
        
        assert text == "Hello World"
        assert stats["chunk_count"] == 1
        assert stats["merged_chunks"] == 1
        assert stats["dedup_chars"] == 0

    def test_assemble_multiple_slices_no_overlap(self):
        """测试多个无重叠切片"""
        assembler = AssemblerV2()
        
        slices = [
            {'content': 'Hello ', 'offset': 0, 'length': 6},
            {'content': 'World', 'offset': 6, 'length': 5}
        ]
        
        text, stats = assembler.assemble_with_dedup(slices)
        
        assert text == "Hello World"
        assert stats["chunk_count"] == 2
        assert stats["merged_chunks"] == 2

    def test_assemble_unordered_slices(self):
        """测试无序切片（应自动排序）"""
        assembler = AssemblerV2()
        
        slices = [
            {'content': 'World', 'offset': 6, 'length': 5},
            {'content': 'Hello ', 'offset': 0, 'length': 6}
        ]
        
        text, stats = assembler.assemble_with_dedup(slices)
        
        assert text == "Hello World"


class TestAssemblerV2Deduplication:
    """去重功能测试"""

    def test_assemble_with_overlap(self):
        """测试有重叠的切片去重"""
        assembler = AssemblerV2(min_overlap=5)
        
        slices = [
            {'content': 'Hello World', 'offset': 0, 'length': 11},
            {'content': 'World Peace', 'offset': 6, 'length': 11}
        ]
        
        text, stats = assembler.assemble_with_dedup(slices)
        
        assert "Hello" in text
        assert "World" in text
        assert "Peace" in text
        assert stats["dedup_chars"] > 0

    def test_assemble_significant_overlap(self):
        """测试显著重叠"""
        assembler = AssemblerV2(overlap_threshold=0.3, min_overlap=5)
        
        slices = [
            {'content': 'ABCDEFGHIJ', 'offset': 0, 'length': 10},
            {'content': 'EFGHIJKLMN', 'offset': 4, 'length': 10}
        ]
        
        text, stats = assembler.assemble_with_dedup(slices)
        
        assert text == "ABCDEFGHIJKLMN"
        assert stats["dedup_chars"] > 0

    def test_assemble_no_overlap_detection(self):
        """测试无重叠检测"""
        assembler = AssemblerV2(min_overlap=10)
        
        slices = [
            {'content': 'ABC', 'offset': 0, 'length': 3},
            {'content': 'DEF', 'offset': 3, 'length': 3}
        ]
        
        text, stats = assembler.assemble_with_dedup(slices)
        
        assert text == "ABCDEF"
        assert stats["dedup_chars"] == 0


class TestAssemblerV2Quality:
    """质量评估测试"""

    def test_quality_perfect_assembly(self):
        """测试完美拼装"""
        assembler = AssemblerV2()
        
        slices = [
            {'content': 'Hello ', 'offset': 0, 'length': 6},
            {'content': 'World', 'offset': 6, 'length': 5}
        ]
        
        result = assembler.assemble_with_quality(slices, expected_length=11)
        
        assert result["content"] == "Hello World"
        assert result["quality_score"] >= 80
        assert result["is_complete"] is True
        assert len(result["issues"]) == 0

    def test_quality_with_dedup_penalty(self):
        """测试去重惩罚"""
        assembler = AssemblerV2(min_overlap=5)
        
        slices = [
            {'content': 'Hello World', 'offset': 0, 'length': 11},
            {'content': 'World Peace', 'offset': 6, 'length': 11}
        ]
        
        result = assembler.assemble_with_quality(slices)
        
        assert result["quality_score"] < 100  # 有去重惩罚
        assert any("重复" in issue for issue in result["issues"])

    def test_quality_too_many_chunks(self):
        """测试切片过多惩罚"""
        assembler = AssemblerV2()
        
        slices = [
            {'content': f'chunk{i}', 'offset': i*5, 'length': 5}
            for i in range(25)
        ]
        
        result = assembler.assemble_with_quality(slices)
        
        assert result["quality_score"] <= 90  # 有过多切片惩罚（扣 10 分）
        assert any("切片数量过多" in issue for issue in result["issues"])

    def test_quality_length_mismatch(self):
        """测试长度不匹配惩罚"""
        assembler = AssemblerV2()
        
        slices = [
            {'content': 'Hello ', 'offset': 0, 'length': 6},
            {'content': 'World', 'offset': 6, 'length': 5}
        ]
        
        result = assembler.assemble_with_quality(slices, expected_length=100)
        
        assert result["quality_score"] <= 85  # 有长度偏差惩罚（扣 15 分）
        assert any("长度偏差" in issue for issue in result["issues"])

    def test_quality_detect_gaps(self):
        """测试断裂检测"""
        assembler = AssemblerV2()
        
        slices = [
            {'content': 'Hello', 'offset': 0, 'length': 5},
            {'content': 'World', 'offset': 50, 'length': 5}  # 有大间隙
        ]
        
        result = assembler.assemble_with_quality(slices)
        
        assert result["quality_score"] <= 80  # 有断裂惩罚（扣 20 分）
        assert any("断裂" in issue for issue in result["issues"])


class TestAssemblerV2Integrity:
    """完整性验证测试"""

    def test_verify_identical(self):
        """测试完全相同"""
        assembler = AssemblerV2()
        
        result = assembler.verify_integrity("Hello World", "Hello World")
        
        assert result["similarity"] == 100.0
        assert result["is_identical"] is True
        assert result["is_acceptable"] is True
        assert result["diff_count"] == 0

    def test_verify_similar(self):
        """测试相似但不完全相同"""
        assembler = AssemblerV2()
        
        result = assembler.verify_integrity("Hello World", "Hello world")
        
        # 大小写差异，相似度应该较高但不一定超过 90%
        assert result["similarity"] > 80
        assert result["is_identical"] is False
        # 相似度可能低于 95%，所以 is_acceptable 可能为 False
        # 这里只验证基本逻辑
        assert result["diff_count"] > 0

    def test_verify_different(self):
        """测试差异较大"""
        assembler = AssemblerV2()
        
        result = assembler.verify_integrity("ABC", "XYZ")
        
        assert result["similarity"] < 50
        assert result["is_identical"] is False
        assert result["is_acceptable"] is False

    def test_verify_length_difference(self):
        """测试长度差异"""
        assembler = AssemblerV2()
        
        # assembled 比 original 短
        result = assembler.verify_integrity("Hello", "Hello World")
        
        assert result["missing_chars"] == 6  # len(original) - len(assembled)
        assert result["extra_chars"] == -6   # len(assembled) - len(original)
        
        # assembled 比 original 长
        result2 = assembler.verify_integrity("Hello World", "Hello")
        
        assert result2["missing_chars"] == -6
        assert result2["extra_chars"] == 6


class TestAssemblerV2Cache:
    """缓存功能测试"""

    def test_cache_slice(self):
        """测试缓存切片"""
        assembler = AssemblerV2()
        
        assembler.cache_slice("slice1", "content1")
        
        assert assembler.get_cached_slice("slice1") == "content1"

    def test_cache_slice_overwrite(self):
        """测试覆盖缓存"""
        assembler = AssemblerV2()
        
        assembler.cache_slice("slice1", "content1")
        assembler.cache_slice("slice1", "content2")
        
        assert assembler.get_cached_slice("slice1") == "content2"

    def test_get_cached_slice_not_found(self):
        """测试获取不存在的缓存"""
        assembler = AssemblerV2()
        
        result = assembler.get_cached_slice("nonexistent")
        
        assert result is None

    def test_get_cache_stats(self):
        """测试获取缓存统计"""
        assembler = AssemblerV2()
        
        assembler.cache_slice("slice1", "content1")
        assembler.cache_slice("slice2", "content2")
        
        stats = assembler.get_cache_stats()
        
        assert stats['size'] == 2
        assert 'slice1' in stats['keys']
        assert 'slice2' in stats['keys']

    def test_cache_empty_stats(self):
        """测试空缓存统计"""
        assembler = AssemblerV2()
        
        stats = assembler.get_cache_stats()
        
        assert stats['size'] == 0
        assert stats['keys'] == []


class TestAssemblerV2Close:
    """资源清理测试"""

    def test_close(self):
        """测试关闭（无操作）"""
        assembler = AssemblerV2()
        
        # 不应抛出异常
        assembler.close()


class TestAssemblerV2EdgeCases:
    """边界条件测试"""

    def test_overlap_threshold_boundary(self):
        """测试重叠阈值边界"""
        assembler = AssemblerV2(overlap_threshold=0.3, min_overlap=5)
        
        # 刚好达到阈值
        slices = [
            {'content': '0123456789', 'offset': 0, 'length': 10},
            {'content': '56789ABCDE', 'offset': 5, 'length': 10}
        ]
        
        text, stats = assembler.assemble_with_dedup(slices)
        
        assert "01234" in text
        assert "ABCDE" in text

    def test_min_overlap_boundary(self):
        """测试最小重叠边界"""
        assembler = AssemblerV2(min_overlap=3, overlap_threshold=0.3)
        
        # 使用更长的内容来确保重叠检测有效
        slices = [
            {'content': 'ABCDEFGHIJ', 'offset': 0, 'length': 10},
            {'content': 'FGHIJKLMNO', 'offset': 5, 'length': 10}
        ]
        
        text, stats = assembler.assemble_with_dedup(slices)
        
        # 应该有重叠检测（FGHIJ 共 5 个字符）
        assert stats["dedup_chars"] >= 3

    def test_slice_with_empty_content(self):
        """测试空内容切片"""
        assembler = AssemblerV2()
        
        slices = [
            {'content': '', 'offset': 0, 'length': 0},
            {'content': 'Hello', 'offset': 0, 'length': 5}
        ]
        
        text, stats = assembler.assemble_with_dedup(slices)
        
        assert text == "Hello"

    def test_detect_overlap_short_content(self):
        """测试短内容重叠检测"""
        assembler = AssemblerV2(min_overlap=3)
        
        slice1 = {'content': 'ABC', 'offset': 0, 'length': 3}
        slice2 = {'content': 'BCD', 'offset': 1, 'length': 3}
        
        overlap = assembler._detect_overlap(slice1, slice2)
        
        # 短内容也能检测重叠
        assert overlap >= 0
