"""
Storage Backend 存储后端测试用例

目标：覆盖率 77% → 90%+
"""

import pytest
import tempfile
import os
from pathlib import Path
from diting.storage_backend import (
    StorageBackend, LocalStorage, S3Storage, 
    OSSStorage, StorageManager
)


class TestLocalStorage:
    """本地存储测试"""

    @pytest.fixture
    def storage(self, tmp_path):
        """创建临时存储目录"""
        return LocalStorage(str(tmp_path))

    def test_init_creates_directory(self, tmp_path):
        """测试初始化创建目录"""
        new_dir = tmp_path / "new_storage"
        storage = LocalStorage(str(new_dir))
        
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_save_and_load(self, storage):
        """测试保存和加载"""
        data = b"Hello World"
        
        result_path = storage.save("test.txt", data)
        
        assert os.path.exists(result_path)
        loaded_data = storage.load("test.txt")
        assert loaded_data == data

    def test_save_creates_parent_directories(self, storage):
        """测试保存时创建父目录"""
        data = b"Nested file"
        
        result_path = storage.save("nested/dir/file.txt", data)
        
        assert os.path.exists(result_path)
        assert Path(result_path).parent.exists()

    def test_load_nonexistent_file(self, storage):
        """测试加载不存在的文件"""
        with pytest.raises(FileNotFoundError):
            storage.load("nonexistent.txt")

    def test_delete_existing_file(self, storage):
        """测试删除存在的文件"""
        storage.save("to_delete.txt", b"data")
        
        assert storage.exists("to_delete.txt")
        
        storage.delete("to_delete.txt")
        
        assert not storage.exists("to_delete.txt")

    def test_delete_nonexistent_file(self, storage):
        """测试删除不存在的文件（不应抛出异常）"""
        # 不应抛出异常
        storage.delete("nonexistent.txt")

    def test_exists_true(self, storage):
        """测试文件存在"""
        storage.save("exists.txt", b"data")
        
        assert storage.exists("exists.txt") is True

    def test_exists_false(self, storage):
        """测试文件不存在"""
        assert storage.exists("not_exists.txt") is False

    def test_save_overwrite(self, storage):
        """测试覆盖已有文件"""
        storage.save("file.txt", b"original")
        storage.save("file.txt", b"overwritten")
        
        loaded = storage.load("file.txt")
        assert loaded == b"overwritten"

    def test_load_binary_data(self, storage):
        """测试加载二进制数据"""
        # 包含各种字节值
        data = bytes(range(256))
        
        storage.save("binary.bin", data)
        loaded = storage.load("binary.bin")
        
        assert loaded == data

    def test_save_empty_file(self, storage):
        """测试保存空文件"""
        storage.save("empty.txt", b"")
        
        assert storage.exists("empty.txt")
        loaded = storage.load("empty.txt")
        assert loaded == b""

    def test_unicode_filename(self, storage):
        """测试 Unicode 文件名"""
        storage.save("中文文件.txt", b"data")
        
        assert storage.exists("中文文件.txt")
        loaded = storage.load("中文文件.txt")
        assert loaded == b"data"

    def test_special_characters_in_path(self, storage):
        """测试路径中的特殊字符"""
        storage.save("file-with_special.chars.txt", b"data")
        
        assert storage.exists("file-with_special.chars.txt")


class TestS3Storage:
    """S3 存储测试（配置测试）"""

    def test_init_default_config(self):
        """测试默认配置初始化"""
        storage = S3Storage({})
        
        assert storage.bucket == 'diting-storage'
        assert storage.region == 'us-east-1'
        assert storage.access_key is None
        assert storage.secret_key is None

    def test_init_custom_config(self):
        """测试自定义配置初始化"""
        config = {
            'bucket': 'my-bucket',
            'region': 'cn-north-1',
            'access_key': 'AK_TEST',
            'secret_key': 'SK_TEST'
        }
        storage = S3Storage(config)
        
        assert storage.bucket == 'my-bucket'
        assert storage.region == 'cn-north-1'
        assert storage.access_key == 'AK_TEST'
        assert storage.secret_key == 'SK_TEST'

    def test_init_partial_config(self):
        """测试部分配置初始化"""
        config = {
            'bucket': 'custom-bucket'
        }
        storage = S3Storage(config)
        
        assert storage.bucket == 'custom-bucket'
        assert storage.region == 'us-east-1'  # 默认值


class TestOSSStorage:
    """OSS 存储测试（配置测试）"""

    def test_init_default_config(self):
        """测试默认配置初始化"""
        storage = OSSStorage({})
        
        assert storage.bucket == 'diting-storage'
        assert storage.endpoint == 'oss-cn-hangzhou.aliyuncs.com'
        assert storage.access_key_id is None
        assert storage.access_key_secret is None

    def test_init_custom_config(self):
        """测试自定义配置初始化"""
        config = {
            'bucket': 'my-oss-bucket',
            'endpoint': 'oss-cn-beijing.aliyuncs.com',
            'access_key_id': 'OSS_AK',
            'access_key_secret': 'OSS_SK'
        }
        storage = OSSStorage(config)
        
        assert storage.bucket == 'my-oss-bucket'
        assert storage.endpoint == 'oss-cn-beijing.aliyuncs.com'
        assert storage.access_key_id == 'OSS_AK'
        assert storage.access_key_secret == 'OSS_SK'


class TestStorageManager:
    """存储管理器测试"""

    def test_init_default_local(self, tmp_path):
        """测试默认本地存储初始化"""
        config = {
            'backend': 'local',
            'local': {'root_path': str(tmp_path)}
        }
        manager = StorageManager(config)
        
        assert isinstance(manager.backend, LocalStorage)

    def test_init_s3_backend(self):
        """测试 S3 后端初始化"""
        config = {
            'backend': 's3',
            's3': {'bucket': 'test-bucket'}
        }
        manager = StorageManager(config)
        
        assert isinstance(manager.backend, S3Storage)
        assert manager.backend.bucket == 'test-bucket'

    def test_init_oss_backend(self):
        """测试 OSS 后端初始化"""
        config = {
            'backend': 'oss',
            'oss': {'bucket': 'test-oss-bucket'}
        }
        manager = StorageManager(config)
        
        assert isinstance(manager.backend, OSSStorage)
        assert manager.backend.bucket == 'test-oss-bucket'

    def test_init_default_fallback(self):
        """测试默认回退到本地存储"""
        config = {
            'backend': 'unknown'  # 未知类型
        }
        manager = StorageManager(config)
        
        assert isinstance(manager.backend, LocalStorage)

    def test_save_and_load(self, tmp_path):
        """测试管理器保存和加载"""
        config = {
            'backend': 'local',
            'local': {'root_path': str(tmp_path)}
        }
        manager = StorageManager(config)
        
        manager.save('test.txt', b'data')
        loaded = manager.load('test.txt')
        
        assert loaded == b'data'

    def test_delete(self, tmp_path):
        """测试管理器删除"""
        config = {
            'backend': 'local',
            'local': {'root_path': str(tmp_path)}
        }
        manager = StorageManager(config)
        
        manager.save('to_delete.txt', b'data')
        assert manager.exists('to_delete.txt')
        
        manager.delete('to_delete.txt')
        assert not manager.exists('to_delete.txt')

    def test_exists(self, tmp_path):
        """测试管理器存在检查"""
        config = {
            'backend': 'local',
            'local': {'root_path': str(tmp_path)}
        }
        manager = StorageManager(config)
        
        assert manager.exists('nonexistent.txt') is False
        manager.save('exists.txt', b'data')
        assert manager.exists('exists.txt') is True


class TestStorageBackendAbstract:
    """抽象基类测试"""

    def test_abstract_methods(self):
        """测试抽象方法必须实现"""
        # 尝试实例化抽象类应该失败
        with pytest.raises(TypeError):
            StorageBackend()

    def test_concrete_implementation(self, tmp_path):
        """测试具体实现"""
        storage = LocalStorage(str(tmp_path))
        
        # 应该能够调用所有抽象方法
        storage.save("test.txt", b"data")
        data = storage.load("test.txt")
        assert data == b"data"
        assert storage.exists("test.txt")
        storage.delete("test.txt")
        assert not storage.exists("test.txt")


class TestStorageManagerEdgeCases:
    """StorageManager 边界测试"""

    def test_init_empty_config(self):
        """测试空配置初始化"""
        manager = StorageManager({})
        
        # 应该使用默认本地存储
        assert isinstance(manager.backend, LocalStorage)

    def test_init_none_config(self):
        """测试 None 配置初始化"""
        manager = StorageManager(None)
        
        assert isinstance(manager.backend, LocalStorage)

    def test_save_s3_not_implemented(self):
        """测试 S3 保存未完全实现"""
        config = {
            'backend': 's3',
            's3': {'bucket': 'test'}
        }
        manager = StorageManager(config)
        
        # S3 save 返回占位 URL
        path = manager.save('test.txt', b'data')
        assert path == 's3://test/test.txt'

    def test_load_s3_not_implemented(self):
        """测试 S3 加载抛出异常"""
        config = {
            'backend': 's3',
            's3': {'bucket': 'test'}
        }
        manager = StorageManager(config)
        
        with pytest.raises(NotImplementedError):
            manager.load('test.txt')

    def test_delete_s3_noop(self):
        """测试 S3 删除无操作"""
        config = {
            'backend': 's3',
            's3': {'bucket': 'test'}
        }
        manager = StorageManager(config)
        
        # 不应抛出异常
        manager.delete('test.txt')

    def test_exists_s3_false(self):
        """测试 S3 存在检查返回 False"""
        config = {
            'backend': 's3',
            's3': {'bucket': 'test'}
        }
        manager = StorageManager(config)
        
        assert manager.exists('test.txt') is False

    def test_save_oss_returns_url(self):
        """测试 OSS 保存返回 URL"""
        config = {
            'backend': 'oss',
            'oss': {'bucket': 'test-oss'}
        }
        manager = StorageManager(config)
        
        path = manager.save('test.txt', b'data')
        assert path == 'oss://test-oss/test.txt'

    def test_load_oss_not_implemented(self):
        """测试 OSS 加载抛出异常"""
        config = {
            'backend': 'oss',
            'oss': {'bucket': 'test'}
        }
        manager = StorageManager(config)
        
        with pytest.raises(NotImplementedError):
            manager.load('test.txt')

    def test_delete_oss_noop(self):
        """测试 OSS 删除无操作"""
        config = {
            'backend': 'oss',
            'oss': {'bucket': 'test'}
        }
        manager = StorageManager(config)
        
        manager.delete('test.txt')

    def test_exists_oss_false(self):
        """测试 OSS 存在检查返回 False"""
        config = {
            'backend': 'oss',
            'oss': {'bucket': 'test'}
        }
        manager = StorageManager(config)
        
        assert manager.exists('test.txt') is False
