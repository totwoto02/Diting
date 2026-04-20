"""
Smart Trigger 智能触发器测试用例

目标：覆盖率 66% → 90%+
"""

import pytest
from diting.smart_trigger import SmartTrigger


class TestSmartTriggerBasic:
    """基础功能测试"""

    def test_init_default(self):
        """测试默认初始化"""
        trigger = SmartTrigger()
        
        assert trigger.enabled is True
        assert trigger.monthly_quota == 100
        assert trigger.quota_used == 0

    def test_init_with_config(self):
        """测试自定义配置初始化"""
        config = {
            'ENABLE_SMART_TRIGGER': False,
            'AI_MONTHLY_QUOTA': 50
        }
        trigger = SmartTrigger(config)
        
        assert trigger.enabled is False
        assert trigger.monthly_quota == 50

    def test_should_call_ai_disabled(self):
        """测试智能触发未启用"""
        trigger = SmartTrigger({'ENABLE_SMART_TRIGGER': False})
        
        file_info = {
            'type': 'audio',
            'size': 5 * 1024 * 1024,
            'filename': 'test.ogg',
            'memory_path': '/test',
            'user_marked': None
        }
        
        assert trigger.should_call_ai(file_info) is False

    def test_should_call_ai_user_force_true(self):
        """测试用户强制调用"""
        trigger = SmartTrigger()
        
        file_info = {
            'type': 'image',
            'size': 100,  # 很小
            'filename': 'test.png',
            'memory_path': '/temp',
            'user_marked': None
        }
        
        assert trigger.should_call_ai(file_info, user_preference=True) is True

    def test_should_call_ai_user_force_false(self):
        """测试用户强制不调用"""
        trigger = SmartTrigger()
        
        file_info = {
            'type': 'audio',
            'size': 5 * 1024 * 1024,
            'filename': 'important.ogg',
            'memory_path': '/important',
            'user_marked': 'important'
        }
        
        assert trigger.should_call_ai(file_info, user_preference=False) is False

    def test_should_call_ai_quota_exhausted(self):
        """测试配额用尽"""
        trigger = SmartTrigger({'AI_MONTHLY_QUOTA': 5})
        trigger.quota_used = 5
        
        file_info = {
            'type': 'audio',
            'size': 5 * 1024 * 1024,
            'filename': 'test.ogg',
            'memory_path': '/test',
            'user_marked': None
        }
        
        result = trigger.should_call_ai(file_info)
        assert result is False
        
        # 验证是因为配额用尽（而不是其他原因）
        # 当配额未满时，同样的文件应该返回 True
        trigger2 = SmartTrigger({'AI_MONTHLY_QUOTA': 5})
        trigger2.quota_used = 0
        # 但这个文件综合评分可能不高，所以我们用用户标记来确保
        file_info_marked = file_info.copy()
        file_info_marked['user_marked'] = 'important'
        result2 = trigger2.should_call_ai(file_info_marked)
        assert result2 is True


class TestSmartTriggerUserMarks:
    """用户标记测试"""

    def test_user_mark_important(self):
        """测试用户标记重要"""
        trigger = SmartTrigger()
        
        file_info = {
            'type': 'image',
            'size': 500 * 1024,
            'filename': 'test.png',
            'memory_path': '/test',
            'user_marked': 'important'
        }
        
        assert trigger.should_call_ai(file_info) is True

    def test_user_mark_skip_ai(self):
        """测试用户标记跳过 AI"""
        trigger = SmartTrigger()
        
        file_info = {
            'type': 'audio',
            'size': 5 * 1024 * 1024,
            'filename': 'test.ogg',
            'memory_path': '/test',
            'user_marked': 'skip_ai'
        }
        
        assert trigger.should_call_ai(file_info) is False

    def test_user_mark_archive(self):
        """测试用户标记归档"""
        trigger = SmartTrigger()
        
        file_info = {
            'type': 'audio',
            'size': 5 * 1024 * 1024,
            'filename': 'test.ogg',
            'memory_path': '/test',
            'user_marked': 'archive'
        }
        
        assert trigger.should_call_ai(file_info) is False


class TestSmartTriggerFileSize:
    """文件大小测试"""

    def test_audio_size_ok(self):
        """测试音频文件大小合适"""
        trigger = SmartTrigger()
        
        file_info = {
            'type': 'audio',
            'size': 5 * 1024 * 1024,  # 5MB
            'filename': 'test.ogg',
            'memory_path': '/test',
            'user_marked': None
        }
        
        assert trigger._check_size_threshold('audio', 5 * 1024 * 1024) is True

    def test_audio_too_small(self):
        """测试音频文件太小"""
        trigger = SmartTrigger()
        
        assert trigger._check_size_threshold('audio', 5 * 1024) is False  # 5KB < 10KB

    def test_audio_too_large(self):
        """测试音频文件太大"""
        trigger = SmartTrigger()
        
        assert trigger._check_size_threshold('audio', 60 * 1024 * 1024) is False  # 60MB > 50MB

    def test_image_size_ok(self):
        """测试图片文件大小合适"""
        trigger = SmartTrigger()
        
        assert trigger._check_size_threshold('image', 500 * 1024) is True  # 500KB

    def test_image_too_small(self):
        """测试图片文件太小"""
        trigger = SmartTrigger()
        
        assert trigger._check_size_threshold('image', 50 * 1024) is False  # 50KB < 100KB

    def test_image_too_large(self):
        """测试图片文件太大"""
        trigger = SmartTrigger()
        
        assert trigger._check_size_threshold('image', 15 * 1024 * 1024) is False  # 15MB > 10MB

    def test_unknown_type_no_threshold(self):
        """测试未知文件类型（无阈值限制）"""
        trigger = SmartTrigger()
        
        assert trigger._check_size_threshold('unknown', 1000) is True


class TestSmartTriggerFilenameAnalysis:
    """文件名分析测试"""

    def test_filename_high_score_keywords(self):
        """测试高分关键词"""
        trigger = SmartTrigger()
        
        # 测试英文高分关键词（避免包含低分关键词如 test）
        high_keywords = ['project', 'meeting', 'note', 'contract', 'plan']
        
        for kw in high_keywords:
            score = trigger._analyze_filename(f'{kw}_report.txt')  # 使用 report 而非 test
            assert score == 0.9, f"关键词 {kw} 应该得高分"
        
        # 测试中文高分关键词
        score = trigger._analyze_filename('重要会议备忘.txt')
        assert score == 0.9, "中文高分关键词应该得高分"

    def test_filename_low_score_keywords(self):
        """测试低分关键词"""
        trigger = SmartTrigger()
        
        low_keywords = ['临时', '截图', '复制', '新建', '未命名', 'test',
                        'temp', 'screenshot', 'copy', 'untitled']
        
        for kw in low_keywords:
            score = trigger._analyze_filename(f'{kw}_file.txt')
            assert score == 0.2, f"关键词 {kw} 应该得低分"

    def test_filename_mixed_keywords(self):
        """测试混合关键词（高=低）"""
        trigger = SmartTrigger()
        
        score = trigger._analyze_filename('重要临时文件.txt')
        assert score == 0.5  # 高低抵消

    def test_filename_empty(self):
        """测试空文件名"""
        trigger = SmartTrigger()
        
        score = trigger._analyze_filename('')
        assert score == 0.5

    def test_filename_no_keywords(self):
        """测试无关键词文件名"""
        trigger = SmartTrigger()
        
        score = trigger._analyze_filename('random_file_123.txt')
        assert score == 0.5


class TestSmartTriggerPathAnalysis:
    """记忆路径分析测试"""

    def test_path_high_score(self):
        """测试高分路径"""
        trigger = SmartTrigger()
        
        high_paths = ['/important', '/projects', '/meetings', '/work',
                      '/关键', '/项目', '/会议', '/工作']
        
        for path in high_paths:
            score = trigger._analyze_memory_path(f'{path}/test')
            assert score == 0.9, f"路径 {path} 应该得高分"

    def test_path_low_score(self):
        """测试低分路径"""
        trigger = SmartTrigger()
        
        low_paths = ['/temp', '/cache', '/test', '/trash',
                     '/临时', '/缓存', '/测试', '/垃圾']
        
        for path in low_paths:
            score = trigger._analyze_memory_path(f'{path}/file')
            assert score == 0.2, f"路径 {path} 应该得低分"

    def test_path_empty(self):
        """测试空路径"""
        trigger = SmartTrigger()
        
        score = trigger._analyze_memory_path('')
        assert score == 0.5

    def test_path_normal(self):
        """测试普通路径"""
        trigger = SmartTrigger()
        
        score = trigger._analyze_memory_path('/photos/2026-04')
        assert score == 0.5


class TestSmartTriggerQuota:
    """配额管理测试"""

    def test_use_quota(self):
        """测试使用配额"""
        trigger = SmartTrigger()
        
        assert trigger.quota_used == 0
        trigger.use_quota()
        assert trigger.quota_used == 1
        trigger.use_quota()
        assert trigger.quota_used == 2

    def test_get_quota_status(self):
        """测试获取配额状态"""
        trigger = SmartTrigger({'AI_MONTHLY_QUOTA': 100})
        trigger.quota_used = 25
        
        status = trigger.get_quota_status()
        
        assert status['used'] == 25
        assert status['total'] == 100
        assert status['remaining'] == 75
        assert status['percentage'] == 25.0

    def test_reset_quota(self):
        """测试重置配额"""
        trigger = SmartTrigger()
        trigger.quota_used = 50
        
        trigger.reset_quota()
        
        assert trigger.quota_used == 0


class TestSmartTriggerScenarios:
    """综合场景测试"""

    def test_scenario_important_meeting_audio(self):
        """场景 1：重要会议录音"""
        trigger = SmartTrigger()
        
        file_info = {
            'type': 'audio',
            'size': 5 * 1024 * 1024,
            'filename': '重要会议录音.ogg',
            'memory_path': '/work/meetings/2026-04-15',
            'user_marked': None
        }
        
        assert trigger.should_call_ai(file_info) is True

    def test_scenario_temp_screenshot(self):
        """场景 2：临时截图"""
        trigger = SmartTrigger()
        
        file_info = {
            'type': 'image',
            'size': 500 * 1024,
            'filename': '截图 20260415.png',
            'memory_path': '/temp/screenshots',
            'user_marked': None
        }
        
        assert trigger.should_call_ai(file_info) is False

    def test_scenario_user_marked_important(self):
        """场景 3：用户标记重要"""
        trigger = SmartTrigger()
        
        file_info = {
            'type': 'image',
            'size': 2 * 1024 * 1024,
            'filename': 'photo.jpg',
            'memory_path': '/photos/2026-04',
            'user_marked': 'important'
        }
        
        assert trigger.should_call_ai(file_info) is True

    def test_scenario_video_large_file(self):
        """场景 4：大视频文件（低优先级）"""
        trigger = SmartTrigger()
        
        file_info = {
            'type': 'video',
            'size': 100 * 1024 * 1024,
            'filename': 'video.mp4',
            'memory_path': '/videos',
            'user_marked': None
        }
        
        # 视频优先级低 (0.3)，但文件类型权重只占 40%，综合评分可能低于 0.6
        result = trigger.should_call_ai(file_info)
        # 视频类型优先级 0.3 * 0.4 = 0.12，综合评分低
        assert result is False

    def test_scenario_normal_image(self):
        """场景 5：普通图片"""
        trigger = SmartTrigger()
        
        file_info = {
            'type': 'image',
            'size': 500 * 1024,
            'filename': 'normal_photo.jpg',
            'memory_path': '/photos/2026-04',
            'user_marked': None
        }
        
        result = trigger.should_call_ai(file_info)
        # 图片优先级 0.5，大小合适，文件名和路径都是默认 0.5
        # 0.5*0.4 + 1*0.3 + 0.5*0.2 + 0.5*0.1 = 0.2 + 0.3 + 0.1 + 0.05 = 0.65 > 0.6
        assert result is True
