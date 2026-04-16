## 八、风险管理

### 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|-----|------|---------|
| 向量模型选择不当 | 中 | 中 | 预留模型切换接口，支持热切换 |
| ChromaDB 性能瓶颈 | 低 | 中 | 预留 Qdrant 切换方案 |
| 拼装算法复杂度高 | 中 | 中 | 先实现基础版，后续优化 |
| 切片策略不匹配场景 | 中 | 中 | 支持多种策略 + 用户自定义 |

### 进度风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|-----|------|---------|
| 向量库集成延期 | 中 | 中 | 提前调研文档，准备 Demo |
| 性能优化不达标 | 中 | 中 | 预留缓冲时间，分阶段优化 |
| 集成测试发现问题多 | 高 | 中 | 提前进行小规模测试 |

---
## 九、交付物清单

### 代码 (~3000 行)

| 文件 | 说明 | 行数预估 |
|------|------|---------|
| `mfs/slicers/*.py` | 切片器模块 | ~500 |
| `mfs/vector_store.py` | 向量库封装 | ~300 |
| `mfs/embedding.py` | 向量模型封装 | ~200 |
| `mfs/chunk_manager.py` | Chunk 管理 | ~250 |
| `mfs/assembler.py` | 拼装器 | ~400 |
| `mfs/cache.py` | LRU 缓存 | ~200 |
| `tests/test_*.py` | 测试文件 | ~800 |
| `benchmarks/*.py` | 性能测试 | ~150 |
| **新增总计** | | **~2800 行** |

### 文档

| 文件 | 说明 |
|------|------|
| `docs/SLICING_STRATEGY.md` | 切片策略说明 |
| `docs/VECTOR_INTEGRATION.md` | 向量库集成指南 |
| `docs/ASSEMBLER.md` | 拼装器使用指南 |
| `docs/PERFORMANCE.md` | 性能优化指南 |
| `README.md` (更新) | 添加 Phase 2 功能 |
| `docs/API.md` (更新) | 添加新接口说明 |

---
## 十、关键决策点

| 日期 | 决策内容 | 决策人 | 状态 |
|------|---------|-------|------|
| Day 1 | 切片策略确认 | 用户 | ⏳ 待确认 |
| Day 1 | 向量库/模型选型确认 | 用户 | ⏳ 待确认 |
| Week 3 | MFT 指针设计审查 | 用户 | ⏳ 待确认 |
| Week 5 | 性能优化方案审查 | 用户 | ⏳ 待确认 |
| Week 6 | Phase 2 发布审查 | 用户 | ⏳ 待确认 |

---
## 十一、附录：命令速查

```bash
# 安装 Phase 2 依赖
pip install chromadb sentence-transformers

# 运行切片器测试
pytest tests/test_slicers.py -v

# 运行向量库测试
pytest tests/test_vector_store.py -v

# 运行性能基准测试
python benchmarks/benchmark_phase2.py

# 生成覆盖率报告
pytest --cov=mfs --cov-report=html --cov-fail-under=80
```

---
**文档版本**: v1.0  
**创建时间**: 2026-04-14  
**维护人**: main
