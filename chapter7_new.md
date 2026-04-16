## 七、低价服务器适配方案（重要）

### 7.1 环境约束

| 约束 | 影响 | 级别 |
|------|------|------|
| **无 GPU** | 向量计算速度降低 10-50倍 | 🔴 高 |
| **2GB 内存** | 无法加载大型向量模型（BGE-M3约2.3GB） | 🔴 高 |
| **4GB 内存** | 可勉强加载，但剩余空间紧张 | 🟡 中 |

### 7.2 多模型/API 兼容架构（核心设计）

**设计目标**：同时支持本地模型 + 远程 API，自动适配不同环境，扩大支持范围。

#### 7.2.1 支持的向量源（全部兼容）

| 类型 | 名称 | 内存/成本 | 向量维度 | 适用场景 |
|------|------|----------|---------|---------|
| **本地模型** | m3e-small | ~200MB | 256 | 2GB环境、低延迟需求 |
| **本地模型** | m3e-base | ~800MB | 768 | 4GB环境、平衡性能 |
| **本地模型** | BGE-M3 | ~2.3GB | 1024 | >4GB环境、高质量向量 |
| **远程API** | 百度智能云 | ¥0.002/次 | 768 | 无本地资源、稳定国内网络 |
| **远程API** | 阿里云向量 | ¥0.001/次 | 768 | 无本地资源、性价比优先 |
| **远程API** | OpenAI Embedding | $0.0001/次 | 1536 | 国际环境、高质量向量 |

#### 7.2.2 统一配置管理

```yaml
# config.yaml - 向量源配置
embedding:
  # 首选方案（按优先级排序）
  sources:
    - name: m3e-base        # 首选：本地模型（平衡）
      type: local
      model: m3e-base
      dimension: 768
      memory_limit: 800MB
    
    - name: m3e-small       # 备选：本地模型（轻量）
      type: local
      model: m3e-small
      dimension: 256
      memory_limit: 200MB
    
    - name: baidu-api       # 备选：远程API
      type: remote
      api_url: https://cloud.baidu.com/embedding
      api_key: ${BAIDU_API_KEY}
      dimension: 768
    
    - name: aliyun-api      # 备选：远程API
      type: remote
      api_url: https://api.aliyun.com/embedding
      api_key: ${ALIYUN_API_KEY}
      dimension: 768
  
  # 自动切换规则
  auto_switch:
    enabled: true
    rules:
      - condition: "memory_available < 500MB"
        action: "switch_to m3e-small"
      
      - condition: "memory_available < 200MB"
        action: "switch_to baidu-api"
      
      - condition: "model_load_failed"
        action: "try_next_source"
      
      - condition: "api_timeout > 5s"
        action: "switch_to_local_model"
```

#### 7.2.3 自动适配逻辑

```python
# mfs/embedding.py - 多源兼容实现
class MultiSourceEmbedding:
    """
    同时兼容多个本地模型 + 远程 API
    自动检测环境并选择最优方案
    """
    
    def __init__(self, config):
        self.sources = config['embedding']['sources']
        self.auto_switch = config['embedding']['auto_switch']
        self.current_source = None
        self.load_priority()
    
    def load_priority(self):
        """按优先级依次尝试加载"""
        for source in self.sources:
            if self.can_load(source):
                self.current_source = self.init_source(source)
                return True
        raise RuntimeError("所有向量源均不可用")
    
    def can_load(self, source):
        """检测是否可以加载该向量源"""
        if source['type'] == 'local':
            # 检测内存是否足够
            available = get_available_memory()
            return available >= source['memory_limit']
        elif source['type'] == 'remote':
            # 检测网络连通性
            return check_api_available(source['api_url'])
        return False
    
    def encode(self, texts):
        """向量化文本（自动切换）"""
        try:
            return self.current_source.encode(texts)
        except Exception as e:
            # 自动切换到下一个可用源
            self.switch_to_next()
            return self.current_source.encode(texts)
    
    def switch_to_next(self):
        """切换到下一个可用的向量源"""
        current_idx = self.sources.index(self.current_source.config)
        for i in range(current_idx + 1, len(self.sources)):
            if self.can_load(self.sources[i]):
                self.current_source = self.init_source(self.sources[i])
                log.warning(f"向量源已切换: {self.current_source.name}")
                return
        raise RuntimeError("无可用的备用向量源")
```

#### 7.2.4 环境自动检测

| 检测项 | 检测方法 | 决策逻辑 |
|--------|---------|---------|
| **可用内存** | `psutil.virtual_memory().available` | < 200MB → API；< 800MB → m3e-small；> 800MB → m3e-base |
| **GPU 状态** | `torch.cuda.is_available()` | 有GPU → 加速向量化；无GPU → CPU计算 |
| **网络连通** | `ping API服务器` | API可用 → 远程向量；不可用 → 本地模型 |
| **调用频率** | 统计最近1小时调用量 | > 10000次 → 本地模型（成本优化） |

### 7.3 内存管理策略

- **延迟加载**：启动时不加载模型，首次使用时按需加载
- **内存释放**：长时间未使用时释放模型内存（gc.collect，30分钟阈值）
- **批量处理**：减少模型加载次数，批量编码（batch_size=32）
- **模型卸载**：内存紧张时自动卸载大模型，切换到轻量模型或API

### 7.4 ChromaDB 内存优化

- 使用 `duckdb+parquet` 磁盘存储模式（节省 ~70% 内存）
- 禁用匿名遥测数据
- 持久化目录设置
- 支持向量维度动态适配（256/768/1024）

### 7.5 无 GPU 性能预估

| 操作 | GPU 环境 | CPU 环境 (2核) | 远程 API | 延迟对比 |
|------|---------|---------------|---------|---------|
| 单文本向量化 (512维) | ~5ms | ~50-200ms | ~100-500ms | 10-40倍 |
| 批量向量化 (32条) | ~50ms | ~500-2000ms | ~300-1500ms | 10-40倍 |
| 向量搜索 (1000条) | ~5ms | ~10-30ms | ~20-50ms | 2-6倍 |

**性能优先级**：GPU 本地 > CPU 本地 > 远程 API

### 7.6 验收标准调整（低价服务器）

| 指标 | 原目标值 | 低价服务器调整值 | 远程 API 模式 |
|------|---------|----------------|-------------|
| 写入延迟 | <500ms | <1000ms（CPU本地） | <1500ms |
| 向量搜索延迟 | <50ms | <100ms（CPU本地） | <150ms |
| 内存占用 | 无限制 | <1GB（模型+ChromaDB） | <100MB |
| 向量源切换时间 | - | <5秒 | <3秒 |

### 7.7 兼容性矩阵（完整支持范围）

| 环境 | 首选方案 | 备选方案 | 降级方案 |
|------|---------|---------|---------|
| **高端服务器（>8GB + GPU）** | BGE-M3 (GPU加速) | m3e-base | 百度API |
| **中端服务器（4-8GB）** | m3e-base | m3e-small | 阿里云API |
| **低端服务器（2-4GB）** | m3e-small | 百度API | OpenAI API |
| **极低资源（<2GB）** | 百度API | 阿里云API | 无本地模型 |
| **无网络环境** | m3e-small | m3e-base | 无API |

---