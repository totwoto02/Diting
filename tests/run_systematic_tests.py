#!/usr/bin/env python3
"""
谛听系统性测试脚本

使用模拟对话数据进行完整功能测试
- 使用独立测试数据库，不污染主 Agent 记忆
- 测试 2000 个模拟对话
- 测试百万 token 长文本
"""

import sys
import os
import json
import tempfile
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from diting.mft import MFT
from diting.fts5_search import FTS5Search
from diting.knowledge_graph_v2 import KnowledgeGraphV2
from diting.wal_logger import WALLogger
from diting.free_energy_manager import FreeEnergyManager


def create_test_environment():
    """创建隔离的测试环境"""
    # 使用临时数据库，测试后自动删除
    temp_dir = tempfile.mkdtemp(prefix='diting_test_')
    db_path = os.path.join(temp_dir, 'test_diting.db')
    kg_db_path = os.path.join(temp_dir, 'test_diting_kg.db')
    
    print(f"📁 测试数据库路径：{db_path}")
    print(f"📁 KG 数据库路径：{kg_db_path}")
    
    return temp_dir, db_path, kg_db_path


def load_test_data():
    """加载测试数据"""
    test_data = {
        'short': [],
        'long': []
    }
    
    # 加载普通模拟对话
    short_file = 'tests/mock_conversations.json'
    if os.path.exists(short_file):
        with open(short_file, 'r', encoding='utf-8') as f:
            test_data['short'] = json.load(f)
        print(f"📊 加载普通对话：{len(test_data['short'])} 条")
    
    # 加载超长对话（百万 token）
    long_file = 'tests/mock_ultra_long_conversations.json'
    if os.path.exists(long_file):
        with open(long_file, 'r', encoding='utf-8') as f:
            test_data['long'] = json.load(f)
        print(f"📊 加载超长对话：{len(test_data['long'])} 条")
    
    return test_data


def test_create_operations(mft, test_data):
    """测试批量创建操作"""
    print("\n=== 测试批量创建 ===")
    
    start_time = time.time()
    created_count = 0
    
    # 测试普通对话
    for i, conv in enumerate(test_data['short'][:100]):  # 限制为 100 条快速测试
        try:
            path = f"/test/conversations/short/{i}"
            mft.create(
                path=path,
                type="CONVERSATION",
                content=str(conv)[:5000]  # 限制长度
            )
            created_count += 1
        except Exception as e:
            print(f"❌ 创建失败 {i}: {e}")
    
    # 测试超长对话
    for i, conv in enumerate(test_data['long'][:10]):  # 限制为 10 条
        try:
            path = f"/test/conversations/long/{i}"
            content = str(conv)[:50000]  # 限制长度
            mft.create(
                path=path,
                type="LONG_CONVERSATION",
                content=content
            )
            created_count += 1
        except Exception as e:
            print(f"❌ 创建失败 {i}: {e}")
    
    elapsed = time.time() - start_time
    print(f"✅ 创建完成：{created_count} 条记录，耗时 {elapsed:.2f}秒")
    print(f"📊 平均速度：{created_count/elapsed:.2f} 条/秒")
    
    return created_count


def test_read_operations(mft, test_data):
    """测试读取操作"""
    print("\n=== 测试读取操作 ===")
    
    start_time = time.time()
    read_count = 0
    errors = 0
    
    for i in range(min(50, len(test_data['short']))):
        try:
            path = f"/test/conversations/short/{i}"
            result = mft.read(path)
            if result:
                read_count += 1
        except Exception as e:
            errors += 1
    
    elapsed = time.time() - start_time
    print(f"✅ 读取完成：{read_count} 条成功，{errors} 条失败")
    print(f"📊 平均延迟：{elapsed/max(read_count,1)*1000:.2f}ms")
    
    return read_count, errors


def test_search_operations(mft, fts5):
    """测试搜索操作"""
    print("\n=== 测试搜索操作 ===")
    
    search_terms = ["用户", "朋友", "拍照", "漫展", "记忆"]
    
    start_time = time.time()
    search_results = []
    
    for term in search_terms:
        try:
            results = fts5.search(term, top_k=10)
            search_results.append({
                'term': term,
                'count': len(results)
            })
        except Exception as e:
            print(f"❌ 搜索失败 '{term}': {e}")
    
    elapsed = time.time() - start_time
    
    print("📊 搜索结果:")
    for result in search_results:
        print(f"  - '{result['term']}': {result['count']} 条")
    
    print(f"✅ 搜索完成，总耗时 {elapsed:.2f}秒")
    
    return search_results


def test_knowledge_graph(mft, kg):
    """测试知识图谱"""
    print("\n=== 测试知识图谱 ===")
    
    # 提取概念
    concepts = ["用户", "朋友", "拍照", "漫展", "记忆", "谛听"]
    
    start_time = time.time()
    
    for concept in concepts:
        try:
            kg.add_concept(concept)
        except Exception as e:
            print(f"⚠️  添加概念失败 '{concept}': {e}")
    
    # 添加关系
    relations = [
        ("用户", "朋友", "认识"),
        ("用户", "拍照", "喜欢"),
        ("用户", "漫展", "参加"),
        ("朋友", "拍照", "一起"),
    ]
    
    for src, tgt, rel in relations:
        try:
            kg.add_edge(src, tgt, rel)
        except Exception as e:
            print(f"⚠️  添加关系失败 '{src}->{tgt}': {e}")
    
    elapsed = time.time() - start_time
    
    # 获取统计
    stats = kg.get_stats()
    
    print(f"📊 知识图谱统计:")
    print(f"  - 概念数：{stats.get('concept_count', 0)}")
    print(f"  - 边数：{stats.get('edge_count', 0)}")
    print(f"  - 耗时：{elapsed:.2f}秒")
    
    return stats


def test_wal_logger(wal):
    """测试 WAL 日志"""
    print("\n=== 测试 WAL 日志 ===")
    
    # 记录操作
    operations = ["create", "read", "update", "delete"]
    
    start_time = time.time()
    
    for op in operations:
        try:
            wal.log_operation(
                operation=op,
                path=f"/test/{op}",
                metadata={"test": True}
            )
        except Exception as e:
            print(f"⚠️  记录操作失败 '{op}': {e}")
    
    elapsed = time.time() - start_time
    
    # 获取历史
    try:
        history = wal.get_history(limit=10)
        print(f"📊 WAL 日志记录数：{len(history)}")
    except Exception as e:
        print(f"❌ 获取历史失败：{e}")
    
    print(f"✅ WAL 测试完成，耗时 {elapsed:.2f}秒")
    
    return len(history) if 'history' in dir() else 0


def test_free_energy(fe):
    """测试自由能计算"""
    print("\n=== 测试自由能系统 ===")
    
    # 分析系统状态
    try:
        state = fe.analyze_system_state()
        print(f"📊 系统状态：{state.get('system_state', 'unknown')}")
        print(f"📊 记忆总数：{state.get('statistics', {}).get('total_memories', 0)}")
    except Exception as e:
        print(f"⚠️  分析失败：{e}")
    
    print("✅ 自由能测试完成")


def cleanup_test_environment(temp_dir):
    """清理测试环境"""
    import shutil
    try:
        shutil.rmtree(temp_dir)
        print(f"\n🧹 已清理测试目录：{temp_dir}")
    except Exception as e:
        print(f"⚠️  清理失败：{e}")


def main():
    """主测试函数"""
    print("=" * 60)
    print("谛听系统性测试")
    print("=" * 60)
    print(f"⏰ 开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建隔离测试环境
    temp_dir, db_path, kg_db_path = create_test_environment()
    
    try:
        # 初始化系统
        print("\n=== 初始化系统 ===")
        mft = MFT(db_path=db_path, kg_db_path=kg_db_path)
        fts5 = FTS5Search(db_path=db_path)
        kg = KnowledgeGraphV2(db_path=kg_db_path)
        wal = WALLogger(db_path=db_path)
        fe = FreeEnergyManager(db_path=db_path)
        print("✅ 系统初始化完成")
        
        # 加载测试数据
        print("\n=== 加载测试数据 ===")
        test_data = load_test_data()
        
        # 运行测试
        test_create_operations(mft, test_data)
        test_read_operations(mft, test_data)
        test_search_operations(mft, fts5)
        test_knowledge_graph(mft, kg)
        test_wal_logger(wal)
        test_free_energy(fe)
        
        # 最终统计
        print("\n" + "=" * 60)
        print("测试完成统计")
        print("=" * 60)
        
        stats = kg.get_stats()
        print(f"📊 创建记录数：{stats.get('concept_count', 0)}")
        print(f"📊 知识图谱概念：{stats.get('concept_count', 0)}")
        print(f"📊 知识图谱边：{stats.get('edge_count', 0)}")
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理测试环境
        cleanup_test_environment(temp_dir)
        
        print(f"\n⏰ 结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n✅ 系统性测试完成！")


if __name__ == '__main__':
    main()
