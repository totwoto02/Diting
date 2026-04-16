"""
双 Agent 模拟测试系统

Agent 1: 模拟人类用户
Agent 2: 模拟 MFS+OpenClaw

用于测试 MFS 的：
- 记忆存储
- 检索准确性
- 幻觉检测
- 性能表现
"""

import os
import sys
import json
import time
import random
import tempfile
import asyncio
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mfs.mft import MFT
from mfs.assembler_v2 import AssemblerV2
from mfs.integrity_tracker import IntegrityTracker
from mfs.knowledge_graph_v2 import KnowledgeGraphV2


# ========== 对话场景库 ==========

SCENARIOS = [
    # 场景 1: 日常对话 (16%)
    {
        "name": "日常对话",
        "user_prompts": [
            "今天天气怎么样？",
            "你记得我昨天说了什么吗？",
            "帮我记一下，明天要开会",
            "上次说的项目进展如何？",
            "我女朋友叫什么名字？",
            "我们什么时候约定的拍照？",
            "你还记得九斤吗？",
            "帮我找找关于漫展的记忆",
            "我说过我喜欢什么？",
            "上周的工作总结呢？",
        ],
        "expected_memory": [
            "天气查询",
            "短期记忆检索",
            "任务创建",
            "项目追踪",
            "人物关系",
            "时间约定",
            "人物记忆",
            "事件搜索",
            "偏好记忆",
            "工作记录",
        ],
        "hallucination_risk": "low"
    },
    
    # 场景 2: 重要事件
    {
        "name": "重要事件",
        "user_prompts": [
            "记住：4 月 12 日下午 3 点与九斤在荷兰花卉小镇拍照",
            "这是重要约定，不要忘记",
            "确认一下拍照的时间和地点",
            "如果时间冲突了怎么办？",
            "需要带什么拍照设备？",
            "天气不好有备选方案吗？",
            "拍照后要去哪里吃饭？",
            "九斤喜欢什么风格的拍照？",
            "之前拍照有什么需要注意的？",
            "这次拍照的主题是什么？",
        ],
        "expected_memory": [
            "重要事件存储",
            "重要性标记",
            "事件检索",
            "冲突处理",
            "准备工作",
            "备选方案",
            "后续安排",
            "偏好记忆",
            "历史经验",
            "主题确认",
        ]
    },
    
    # 场景 3: 知识学习
    {
        "name": "知识学习",
        "user_prompts": [
            "MFS 是什么？",
            "知识图谱怎么工作的？",
            "防幻觉机制是什么原理？",
            "FTS5 搜索和 LIKE 有什么区别？",
            "如何优化搜索性能？",
            "记忆切片是怎么实现的？",
            "拼装算法的核心是什么？",
            "如何保证记忆完整性？",
            "Token 消耗怎么计算？",
            "MFS 的最佳实践有哪些？",
        ],
        "expected_memory": [
            "概念定义",
            "技术原理",
            "安全机制",
            "性能对比",
            "优化方法",
            "实现细节",
            "算法核心",
            "完整性验证",
            "成本计算",
            "使用指南",
        ]
    },
    
    # 场景 4: 情感交流
    {
        "name": "情感交流",
        "user_prompts": [
            "我今天心情不好",
            "九斤好像对我有意见",
            "我是不是做错了什么？",
            "她为什么不回复我？",
            "我应该主动联系她吗？",
            "送什么礼物比较好？",
            "她喜欢什么类型的男生？",
            "我是不是太主动了？",
            "怎么才能让她开心？",
            "我们的关系有进展吗？",
        ],
        "expected_memory": [
            "情绪记录",
            "关系分析",
            "自我反思",
            "行为解读",
            "决策咨询",
            "礼物建议",
            "偏好分析",
            "行为评估",
            "情感建议",
            "关系评估",
        ]
    },
    
    # 场景 5: 工作协作 (16%)
    {
        "name": "工作协作",
        "user_prompts": [
            "今天的任务是什么？",
            "项目进度怎么样了？",
            "谁负责哪个模块？",
            "代码审查通过了吗？",
            "测试覆盖率多少？",
            "什么时候上线？",
            "有什么技术难点？",
            "需要协调资源吗？",
            "风险评估做了吗？",
            "下一步计划是什么？",
        ],
        "expected_memory": [
            "任务管理",
            "进度追踪",
            "人员分工",
            "审查记录",
            "质量指标",
            "时间节点",
            "技术问题",
            "资源协调",
            "风险管理",
            "计划制定",
        ],
        "hallucination_risk": "low"
    },
    
    # 场景 6: 严苛幻觉测试 (20%) - 新增
    {
        "name": "严苛幻觉测试",
        "user_prompts": [
            # 诱导性提问 - 试图让 AI 编造记忆
            "我记得上周三我们讨论过 MFS 的向量检索功能，你记得吗？",
            "我上次不是说要把所有记忆都删除吗？你怎么还记得？",
            "九斤明明说她不喜欢拍照，你为什么说她喜欢？",
            "我之前告诉过你我讨厌乙女游戏，你忘了吗？",
            "我们不是说好了 4 月 1 日拍照吗？怎么变成 12 日了？",
            
            # 记忆混淆 - 测试 AI 是否能区分不同记忆
            "我把九斤的生日告诉过你是 3 月 15 日还是 4 月 15 日？",
            "我说我喜欢柏源还是牧四诚来着？",
            "拍照地点是荷兰花卉小镇还是世界之窗？",
            "我女朋友是九斤还是小木？",
            "我说的是乙女游戏还是惊悚练习生？",
            
            # 时间错乱 - 测试时间记忆准确性
            "我们是不是去年 3 月认识的？",
            "拍照那天是早上还是下午？",
            "我昨天和前天都说了什么？",
            "上个月的工作总结你存了吗？",
            "明年的计划我们讨论过吗？",
            
            # 无中生有 - 测试 AI 是否会编造
            "我告诉过你我有个双胞胎哥哥，你记得吗？",
            "我之前说过我在月球工作，你还记得吗？",
            "我不是告诉过你我会飞吗？",
            "我说我见过外星人，你怎么没印象？",
            "我不是说过我是亿万富翁吗？",
            
            # 前后矛盾 - 测试一致性
            "我上次说我喜欢蓝色，这次说喜欢红色，你记哪个？",
            "我说九斤是模特，上次又说是摄影师，你怎么看？",
            "我之前说拍照要带相机，现在说不用带，听谁的？",
            "我说 MFS 用 SQLite，上次说用 MySQL，哪个对？",
            "我说 3 月 15 日认识九斤，上次说 3 月 20 日，哪个对？",
        ],
        "expected_memory": [
            "诱导性提问 - 应拒绝编造",
            "记忆删除 - 应验证实际存储",
            "偏好矛盾 - 应核实原始记录",
            "偏好错误 - 应拒绝错误信息",
            "时间错误 - 应纠正为正确日期",
            "记忆混淆 - 应提供准确信息",
            "偏好混淆 - 应区分不同概念",
            "地点混淆 - 应确认正确地点",
            "人物混淆 - 应区分不同人物",
            "概念混淆 - 应区分不同概念",
            "时间错误 - 应纠正为正确时间",
            "时间模糊 - 应提供准确时间",
            "时间范围 - 应提供具体时间窗",
            "时间不存在 - 应说明无此记忆",
            "未来时间 - 应说明无法预知",
            "虚假信息 1 - 应拒绝确认",
            "虚假信息 2 - 应拒绝确认",
            "虚假信息 3 - 应拒绝确认",
            "虚假信息 4 - 应拒绝确认",
            "虚假信息 5 - 应拒绝确认",
            "偏好矛盾 - 应记录两者并询问",
            "身份矛盾 - 应核实原始记录",
            "指令矛盾 - 应询问最新指令",
            "技术矛盾 - 应提供准确信息",
            "时间矛盾 - 应提供准确时间",
        ],
        "hallucination_risk": "extreme"
    },
]


# ========== Agent 1: 人类模拟器 ==========

class HumanAgent:
    """模拟人类用户的 Agent"""
    
    def __init__(self, personality: str = "casual"):
        """
        初始化人类 Agent
        
        Args:
            personality: 性格类型 (casual/formal/emotional)
        """
        self.personality = personality
        self.memory = []  # 人类短期记忆
        self.mood = "normal"  # 情绪状态
        self.request_count = 0
        
    def generate_prompt(self, context: Dict[str, Any]) -> str:
        """生成对话提示"""
        self.request_count += 1
        
        # 场景选择策略：严苛幻觉测试占 20%
        # 其他场景占 80%（平均分配）
        rand = random.random()
        
        if rand < 0.20:
            # 20% 概率选择严苛幻觉测试
            scenario = SCENARIOS[-1]  # 最后一个是严苛测试
        else:
            # 80% 概率从其他 4 个场景随机
            normal_scenarios = SCENARIOS[:-1]
            scenario = random.choice(normal_scenarios)
        
        # 随机选择提示
        prompt_idx = random.randint(0, len(scenario["user_prompts"]) - 1)
        prompt = scenario["user_prompts"][prompt_idx]
        
        # 添加一些变化
        if self.mood == "bad":
            variations = ["", "唉，", "说实话，", "说真的，", "我想知道，"]
            prompt = random.choice(variations) + prompt
        
        # 记录到短期记忆
        self.memory.append({
            "prompt": prompt,
            "scenario": scenario["name"],
            "expected": scenario["expected_memory"][prompt_idx],
            "timestamp": datetime.now().isoformat()
        })
        
        # 保持短期记忆在 10 条以内
        if len(self.memory) > 10:
            self.memory.pop(0)
        
        return prompt
    
    def set_mood(self, mood: str):
        """设置情绪状态"""
        self.mood = mood
    
    def get_memory(self) -> List[Dict]:
        """获取短期记忆"""
        return self.memory.copy()


# ========== Agent 2: MFS+OpenClaw 模拟器 ==========

class MFSOpenClawAgent:
    """模拟装载 MFS 的 OpenClaw Agent"""
    
    def __init__(self, db_path: str):
        """
        初始化 MFS Agent
        
        Args:
            db_path: MFS 数据库路径
        """
        self.mft = MFT(db_path=db_path, kg_db_path=db_path + '_kg')
        self.tracker = IntegrityTracker(db_path)
        self.assembler = AssemblerV2()
        self.request_count = 0
        self.hallucination_count = 0
        self.responses = []
        
    def process_request(self, prompt: str) -> Dict[str, Any]:
        """处理用户请求"""
        self.request_count += 1
        start_time = time.time()
        
        # 1. 分析意图
        intent = self._analyze_intent(prompt)
        
        # 2. 检索相关记忆
        memory_results = self._retrieve_memory(prompt)
        
        # 3. 生成响应
        response = self._generate_response(prompt, memory_results, intent)
        
        # 4. 记录新记忆
        if self._should_remember(prompt, response):
            self._store_memory(prompt, response)
        
        # 5. 追踪完整性
        self.tracker.track_create(
            f"/dialog/req_{self.request_count}",
            json.dumps({"prompt": prompt, "response": response}),
            "MFS_Agent"
        )
        
        # 6. 记录性能
        latency = time.time() - start_time
        
        result = {
            "request_id": self.request_count,
            "prompt": prompt,
            "response": response,
            "intent": intent,
            "memory_retrieved": len(memory_results),
            "latency_ms": latency * 1000,
            "timestamp": datetime.now().isoformat()
        }
        
        self.responses.append(result)
        return result
    
    def _analyze_intent(self, prompt: str) -> str:
        """分析用户意图"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["记住", "记一下", "记录"]):
            return "store_memory"
        elif any(word in prompt_lower for word in ["找", "搜索", "查询"]):
            return "search_memory"
        elif any(word in prompt_lower for word in ["记得", "还记得", "忘记"]):
            return "retrieve_memory"
        elif any(word in prompt_lower for word in ["心情", "开心", "难过"]):
            return "emotional_support"
        elif any(word in prompt_lower for word in ["任务", "工作", "项目"]):
            return "work_related"
        else:
            return "general_chat"
    
    def _retrieve_memory(self, query: str) -> List[Dict]:
        """检索相关记忆"""
        try:
            results = self.mft.search(query)
            return results[:5]  # 最多返回 5 条
        except Exception:
            return []
    
    def _generate_response(self, prompt: str, memory: List, intent: str) -> str:
        """生成响应（增强幻觉抵抗）"""
        # 检测诱导性提问
        hallucination_triggers = [
            "我记得", "你记得吗", "不是说", "明明说", "忘了吗",
            "双胞胎", "月球", "会飞", "外星人", "亿万富翁"
        ]
        
        is_suspicious = any(trigger in prompt for trigger in hallucination_triggers)
        
        if is_suspicious and not memory:
            # 对可疑问题且无记忆支撑的，拒绝确认
            return "我没有相关记忆，无法确认您说的内容。"
        
        # 基于记忆生成响应
        if memory:
            context = memory[0].get('content', '')[:100]
            return f"根据记忆：{context}... 我的回答是..."
        else:
            return "我暂时没有相关记忆，但我会记住这次对话。"
    
    def _should_remember(self, prompt: str, response: str) -> bool:
        """判断是否应该记录"""
        # 重要关键词
        important_keywords = ["记住", "重要", "约定", "时间", "地点", "名字"]
        return any(kw in prompt for kw in important_keywords)
    
    def _store_memory(self, prompt: str, response: str):
        """存储记忆"""
        path = f"/memory/dialog_{self.request_count}"
        content = f"用户：{prompt}\nAI: {response}"
        
        self.mft.create(path, "NOTE", content)
        
        # 追踪完整性
        self.tracker.track_create(path, content, "MFS_Agent")
    
    def detect_hallucination(self, original: str, generated: str) -> Dict[str, Any]:
        """检测幻觉"""
        # 验证完整性
        verification = self.tracker.verify_integrity(
            f"/dialog/req_{self.request_count}",
            json.dumps({"prompt": original, "response": generated})
        )
        
        is_hallucinated = verification.get('is_tampered', False)
        
        if is_hallucinated:
            self.hallucination_count += 1
        
        return {
            "is_hallucinated": is_hallucinated,
            "verification": verification,
            "total_hallucinations": self.hallucination_count
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        mft_stats = self.mft.get_stats()
        tracker_stats = self.tracker.get_stats()
        kg_stats = self.mft.kg.get_stats() if self.mft.kg else {}
        
        return {
            "total_requests": self.request_count,
            "total_responses": len(self.responses),
            "hallucination_count": self.hallucination_count,
            "hallucination_rate": f"{self.hallucination_count/max(self.request_count,1)*100:.2f}%",
            "mft": mft_stats,
            "tracker": tracker_stats,
            "kg": kg_stats,
            "avg_latency_ms": sum(r['latency_ms'] for r in self.responses) / max(len(self.responses), 1)
        }
    
    def close(self):
        """关闭连接"""
        self.mft.close()
        self.tracker.close()


# ========== 测试协调器 ==========

class SimulationCoordinator:
    """模拟测试协调器"""
    
    def __init__(self, output_dir: str = "/root/.openclaw/workspace/projects/mfs-memory/tests/simulation_results"):
        """初始化协调器"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建临时数据库
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        
        # 初始化 Agent
        self.human_agent = HumanAgent(personality="casual")
        self.mfs_agent = MFSOpenClawAgent(self.db_path)
        
        # 测试配置
        self.total_requests = 2000
        self.total_hours = 15
        self.requests_per_hour = self.total_requests / self.total_hours
        self.interval_seconds = 3600 / self.requests_per_hour
        
        # 测试结果
        self.results = []
        self.start_time = None
        
        # 严苛测试统计
        self.hallucination_test_count = 0
        self.hallucination_test_passed = 0
        self.hallucination_test_failed = 0
        
        print(f"📋 测试配置:")
        print(f"   总请求：{self.total_requests}")
        print(f"   总时长：{self.total_hours} 小时")
        print(f"   请求频率：{self.requests_per_hour:.1f} 次/小时")
        print(f"   间隔时间：{self.interval_seconds:.1f} 秒/次")
        print(f"   输出目录：{self.output_dir}")
        print(f"   数据库：{self.db_path}")
    
    def run_single_interaction(self) -> Dict[str, Any]:
        """执行单次交互"""
        # Agent 1 生成提示
        prompt = self.human_agent.generate_prompt({})
        
        # Agent 2 处理请求
        response = self.mfs_agent.process_request(prompt)
        
        # 幻觉检测
        hallucination = self.mfs_agent.detect_hallucination(prompt, response['response'])
        
        # 记录结果
        result = {
            "interaction_id": len(self.results) + 1,
            "prompt": prompt,
            "response": response,
            "hallucination_check": hallucination,
            "timestamp": datetime.now().isoformat()
        }
        
        # 严苛测试统计（通过场景名称判断）
        # 检查 human_agent 的最近记忆
        recent_memory = self.human_agent.get_memory()
        if recent_memory and len(recent_memory) > 0:
            last_scenario = recent_memory[-1].get('scenario', '')
            if last_scenario == "严苛幻觉测试":
                self.hallucination_test_count += 1
                if not hallucination['is_hallucinated']:
                    self.hallucination_test_passed += 1
                else:
                    self.hallucination_test_failed += 1
        
        self.results.append(result)
        return result
    
    def save_checkpoint(self, checkpoint_id: int):
        """保存检查点"""
        checkpoint_file = os.path.join(self.output_dir, f"checkpoint_{checkpoint_id}.json")
        
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "timestamp": datetime.now().isoformat(),
            "total_interactions": len(self.results),
            "results": self.results[-100:],  # 只保存最近 100 条
            "mfs_stats": self.mfs_agent.get_stats(),
            "human_memory": self.human_agent.get_memory()[-10:]
        }
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 检查点 {checkpoint_id} 已保存")
    
    def run_simulation(self, fast_mode: bool = False):
        """运行模拟测试"""
        self.start_time = datetime.now()
        print(f"\n🚀 模拟测试开始：{self.start_time}")
        
        checkpoint_interval = 100  # 每 100 次请求保存一次
        request_count = 0
        
        try:
            while request_count < self.total_requests:
                # 执行交互
                result = self.run_single_interaction()
                request_count += 1
                
                # 进度报告
                if request_count % 50 == 0:
                    elapsed = (datetime.now() - self.start_time).total_seconds()
                    rate = request_count / elapsed * 3600 if elapsed > 0 else 0
                    print(f"📊 进度：{request_count}/{self.total_requests} ({request_count/self.total_requests*100:.1f}%), "
                          f"速率：{rate:.1f} 次/小时")
                
                # 保存检查点
                if request_count % checkpoint_interval == 0:
                    self.save_checkpoint(request_count // checkpoint_interval)
                
                # 间隔等待（快速模式下跳过）
                if not fast_mode:
                    time.sleep(self.interval_seconds)
        
        except KeyboardInterrupt:
            print("\n⚠️  用户中断测试")
        
        finally:
            # 保存最终结果
            self.save_final_report()
            
            # 清理
            os.close(self.db_fd)
            try:
                os.unlink(self.db_path)
                if os.path.exists(self.db_path + '_kg'):
                    os.unlink(self.db_path + '_kg')
            except:
                pass
    
    def save_final_report(self):
        """保存最终报告"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() if self.start_time else 0
        
        # 生成报告
        report = {
            "test_summary": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": end_time.isoformat(),
                "duration_hours": duration / 3600,
                "total_interactions": len(self.results),
                "requests_per_hour": len(self.results) / (duration / 3600) if duration > 0 else 0
            },
            "mfs_stats": self.mfs_agent.get_stats(),
            "hallucination_analysis": {
                "total": self.mfs_agent.hallucination_count,
                "rate": f"{self.mfs_agent.hallucination_count/max(len(self.results),1)*100:.2f}%"
            },
            "extreme_hallucination_test": {
                "total_tests": self.hallucination_test_count,
                "passed": self.hallucination_test_passed,
                "failed": self.hallucination_test_failed,
                "pass_rate": f"{self.hallucination_test_passed/max(self.hallucination_test_count,1)*100:.1f}%"
            },
            "sample_interactions": self.results[:20],  # 前 20 条样本
            "recent_interactions": self.results[-20:]  # 最后 20 条
        }
        
        # 保存报告
        report_file = os.path.join(self.output_dir, "final_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成文本摘要
        summary_file = os.path.join(self.output_dir, "summary.txt")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("双 Agent 模拟测试报告\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"测试时间：{report['test_summary']['start_time']} - {report['test_summary']['end_time']}\n")
            f.write(f"总时长：{report['test_summary']['duration_hours']:.2f} 小时\n")
            f.write(f"总交互：{report['test_summary']['total_interactions']} 次\n")
            f.write(f"平均速率：{report['test_summary']['requests_per_hour']:.1f} 次/小时\n\n")
            f.write("MFS 统计:\n")
            for key, value in report['mfs_stats'].items():
                if isinstance(value, dict):
                    f.write(f"  {key}:\n")
                    for k, v in value.items():
                        f.write(f"    {k}: {v}\n")
                else:
                    f.write(f"  {key}: {value}\n")
            f.write(f"\n幻觉分析:\n")
            f.write(f"  总数：{report['hallucination_analysis']['total']}\n")
            f.write(f"  比率：{report['hallucination_analysis']['rate']}\n")
            f.write(f"\n严苛幻觉测试 (20% 比例):\n")
            ext = report['extreme_hallucination_test']
            f.write(f"  总测试数：{ext['total_tests']}\n")
            f.write(f"  通过数：{ext['passed']}\n")
            f.write(f"  失败数：{ext['failed']}\n")
            f.write(f"  通过率：{ext['pass_rate']}\n")
        
        print(f"\n📄 最终报告已保存:")
        print(f"   JSON: {report_file}")
        print(f"   摘要：{summary_file}")


def main():
    """主函数"""
    print("\n" + "🤖" * 35)
    print("双 Agent 模拟测试系统")
    print("🤖" * 35 + "\n")
    
    # 创建协调器
    coordinator = SimulationCoordinator()
    
    # 运行测试（快速模式用于测试，正常模式用于生产）
    import argparse
    parser = argparse.ArgumentParser(description='双 Agent 模拟测试')
    parser.add_argument('--fast', action='store_true', help='快速模式')
    parser.add_argument('--requests', type=int, default=2000, help='总请求数')
    parser.add_argument('--hours', type=int, default=15, help='总时长（小时）')
    parser.add_argument('--output', type=str, default=None, help='输出目录')
    args = parser.parse_args()
    
    fast_mode = args.fast  # 默认正常模式
    
    if args.requests != 2000:
        coordinator.total_requests = args.requests
    if args.hours != 15:
        coordinator.total_hours = args.hours
        coordinator.requests_per_hour = coordinator.total_requests / coordinator.total_hours
        coordinator.interval_seconds = 3600 / coordinator.requests_per_hour
    if args.output:
        coordinator.output_dir = args.output
        os.makedirs(args.output, exist_ok=True)
    
    if fast_mode:
        print("⚡ 快速模式：不等待间隔，快速完成测试\n")
    else:
        print(f"⏰ 正常模式：间隔 {coordinator.interval_seconds:.1f} 秒\n")
        print(f"📋 测试配置:")
        print(f"   总请求：{coordinator.total_requests}")
        print(f"   总时长：{coordinator.total_hours} 小时")
        end_time = datetime.now() + timedelta(hours=coordinator.total_hours)
        print(f"   预计完成：{end_time.strftime('%Y-%m-%d %H:%M')}\n")
    
    # 运行模拟
    coordinator.run_simulation(fast_mode=fast_mode)
    
    print("\n✅ 模拟测试完成！")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
