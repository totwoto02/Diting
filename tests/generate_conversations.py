#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成超长多轮对话数据，用于 MFS 系统高压测试
每个对话 100K-250K 字，100-300 条消息
"""

import json
import random
import datetime
from typing import List, Dict, Any

# 基础配置
OUTPUT_FILE = "/root/.openclaw/workspace/projects/mfs-memory/tests/mock_ultra_long_conversations.json"

# 场景定义
SCENARIOS = [
    {"id": "ultra_conv_001", "type": "work", "name": "项目规划", "tags": ["长对话", "工作", "项目规划", "多轮交互"]},
    {"id": "ultra_conv_002", "type": "work", "name": "技术文档", "tags": ["长对话", "工作", "技术文档", "方案设计"]},
    {"id": "ultra_conv_003", "type": "personal", "name": "人物档案", "tags": ["长对话", "个人", "人物档案", "关系网络"]},
    {"id": "ultra_conv_004", "type": "learning", "name": "学习课程", "tags": ["长对话", "学习", "课程笔记", "知识整理"]},
    {"id": "ultra_conv_005", "type": "event", "name": "会议纪要", "tags": ["长对话", "事件", "会议纪要", "决策记录"]},
    {"id": "ultra_conv_006", "type": "work", "name": "代码审查", "tags": ["长对话", "工作", "代码审查", "技术讨论"]},
    {"id": "ultra_conv_007", "type": "event", "name": "旅行计划", "tags": ["长对话", "事件", "旅行规划", "详细记录"]},
    {"id": "ultra_conv_008", "type": "learning", "name": "研究笔记", "tags": ["长对话", "学习", "研究笔记", "发现记录"]},
    {"id": "ultra_conv_009", "type": "work", "name": "产品讨论", "tags": ["长对话", "工作", "产品设计", "反馈循环"]},
    {"id": "ultra_conv_010", "type": "personal", "name": "个人日记", "tags": ["长对话", "个人", "日记记录", "反思总结"]},
]

# 人物名称库
CHARACTERS = {
    "work": ["张经理", "李工程师", "王产品", "赵测试", "孙架构师", "周主管", "吴开发", "郑设计师", "钱分析师", "冯运营"],
    "personal": ["小明", "小红", "小刚", "小丽", "小强", "小芳", "小伟", "小敏", "小杰", "小婷"],
    "learning": ["陈教授", "刘导师", "杨学长", "黄同学", "林研究员", "徐博士", "朱老师", "何助教", "高师兄", "罗师姐"],
}

# 项目/概念名称库
PROJECTS = {
    "work": ["MFS 记忆系统", "智能助手项目", "数据平台升级", "API 网关重构", "微服务迁移", "监控系统优化", "自动化测试框架", "文档管理系统", "知识库建设", "性能优化专项"],
    "personal": ["家庭装修", "健身计划", "理财规划", "技能提升", "人脉拓展", "健康管理", "兴趣培养", "旅行清单", "阅读计划", "社交活动"],
    "learning": ["深度学习课程", "分布式系统", "算法进阶", "架构设计", "云计算认证", "数据分析", "自然语言处理", "计算机视觉", "区块链研究", "量子计算探索"],
}

# 操作类型
OPERATION_TYPES = ["CREATE", "UPDATE", "SEARCH", "DELETE", "LINK", "TAG", "EXPORT", "IMPORT"]

# 生成时间戳
def generate_timestamp(base_date: datetime.datetime, offset_minutes: int) -> str:
    """生成 ISO 格式时间戳"""
    new_date = base_date + datetime.timedelta(minutes=offset_minutes)
    return new_date.isoformat() + "Z"

# 生成长文本内容
def generate_long_content(scenario_type: str, min_chars: int = 5000, max_chars: int = 10000) -> str:
    """生成指定长度的详细内容"""
    
    templates = {
        "work": [
            "关于这个项目的详细技术方案，我们需要从以下几个维度进行深入分析。首先，在架构设计层面，考虑到系统的可扩展性和维护性，我们建议采用微服务架构，将核心功能模块进行解耦。每个服务都应该有明确的职责边界，通过 API 网关进行统一管理和调度。在数据库设计方面，我们建议采用读写分离的策略，主库负责写操作，从库负责读操作，这样可以有效提升系统的整体性能。同时，为了保证数据的一致性，我们需要实现分布式事务机制，可以采用 TCC 模式或者 Saga 模式。在缓存策略上，我们建议采用多级缓存架构，包括本地缓存和分布式缓存，这样可以有效降低数据库的压力。关于安全性方面，我们需要实现完善的认证授权机制，采用 OAuth2.0 协议，并结合 JWT 令牌进行身份验证。同时，所有的敏感数据都需要进行加密存储和传输，采用 AES-256 加密算法。在监控和告警方面，我们需要建立完整的监控体系，包括基础设施监控、应用性能监控、业务指标监控等，并设置合理的告警阈值，确保问题能够及时发现和处理。",
            "在本次项目的需求分析阶段，我们与多个业务部门进行了深入的沟通和调研。通过访谈、问卷、数据分析等多种方式，我们收集了大量的需求信息。经过整理和分析，我们将需求分为核心需求、重要需求和一般需求三个优先级。核心需求包括用户管理、权限控制、数据处理、报表生成等功能模块，这些是系统必须实现的基础功能。重要需求包括工作流引擎、消息通知、数据导入导出、第三方集成等功能，这些功能可以显著提升用户体验和工作效率。一般需求包括界面美化、操作优化、帮助文档、培训材料等，这些功能可以在后续版本中逐步完善。在技术选型方面，我们对比了多种技术方案，包括前端框架（React、Vue、Angular）、后端框架（Spring Boot、Django、Node.js）、数据库（MySQL、PostgreSQL、MongoDB）等，最终根据项目特点和团队技术栈做出了最佳选择。",
            "关于代码质量的保障措施，我们制定了严格的代码规范和审查流程。首先，所有的代码都必须遵循团队制定的编码规范，包括命名规范、注释规范、格式规范等。我们使用 ESLint、Prettier 等工具进行自动化代码检查，确保代码风格的一致性。其次，我们实行代码审查制度，所有的代码在合并到主分支之前都必须经过至少一位同事的审查。审查的重点包括代码逻辑的正确性、性能优化、安全性、可维护性等方面。我们鼓励审查者提出建设性的意见，帮助代码作者改进代码质量。第三，我们建立了完善的测试体系，包括单元测试、集成测试、端到端测试等。我们要求核心功能的代码覆盖率不低于 80%，关键业务逻辑的代码覆盖率不低于 90%。我们使用 Jest、Mocha 等测试框架，结合 CI/CD 流程，确保每次代码提交都会自动运行测试。",
        ],
        "personal": [
            "今天是一个值得纪念的日子，回想过去这段时间的经历，我感慨万千。从一开始的迷茫和不确定，到逐渐找到方向和节奏，这个过程充满了挑战和收获。在个人成长方面，我最大的收获是学会了如何更好地管理时间和情绪。以前我总是容易被各种琐事分散注意力，现在我已经能够优先处理重要的事情，并且保持专注。在健康方面，我坚持每天锻炼，无论是跑步、游泳还是瑜伽，都让我感受到了身体的变化和活力的提升。饮食方面，我也开始注重营养均衡，减少油腻和糖分的摄入，多吃蔬菜水果和优质蛋白。在人际关系方面，我学会了更好地倾听和理解他人，不再急于表达自己的观点，而是先尝试站在对方的角度思考问题。这让我的人际关系变得更加和谐，也收获了很多真挚的友谊。",
            "关于未来的规划，我有很多想法和期待。在职业发展方面，我希望能够在接下来的一年里取得更大的突破。具体来说，我计划深入学习人工智能和机器学习相关的知识，掌握更多的技术技能，提升自己的核心竞争力。同时，我也希望能够参与更多有挑战性的项目，积累更多的实战经验。在个人生活方面，我希望能够保持工作与生活的平衡，给自己留出更多的时间来陪伴家人和朋友。我计划每个月至少安排一次家庭聚会，每季度安排一次短途旅行，每年安排一次长途旅行。这些活动不仅可以放松身心，也可以增进与家人朋友之间的感情。在学习方面，我制定了一个详细的阅读计划，每个月至少阅读两本书，涵盖技术、管理、心理、历史等多个领域。我相信持续的学习和思考可以让我保持进步，不断拓展自己的认知边界。",
            "最近我在反思自己的沟通方式，发现有很多可以改进的地方。以前我在与人交流时，常常急于表达自己的观点，而忽略了对方的感受和需求。现在我意识到，有效的沟通不仅仅是表达自己的想法，更重要的是倾听和理解对方。我开始尝试在对话中多用开放式问题，少用封闭式问题，这样可以引导对方更多地表达自己的想法。我也开始注意自己的非语言沟通，包括眼神接触、肢体语言、语调变化等，这些细节往往能够传递很多信息。在冲突处理方面，我也学会了更加理性和冷静，不再情绪化地回应，而是先冷静下来，分析问题的根源，然后寻找双方都能接受的解决方案。这些改变让我的人际关系变得更加和谐，也让我成为了一个更好的沟通者。",
        ],
        "learning": [
            "在深度学习的研究过程中，我逐渐理解了神经网络的工作原理和训练机制。首先，从基础的前向传播开始，输入数据经过多层神经元的处理，每一层都会对数据进行变换和提取，最终得到输出结果。在这个过程中，激活函数起到了关键作用，它引入了非线性因素，使得神经网络能够拟合复杂的函数关系。常用的激活函数包括 ReLU、Sigmoid、Tanh 等，它们各有优缺点，需要根据具体场景选择合适的激活函数。在反向传播过程中，我们使用梯度下降算法来更新网络参数，最小化损失函数。这个过程中，学习率的选择非常重要，过大的学习率可能导致训练不稳定，过小的学习率则会导致训练速度过慢。为了解决这个问题，人们提出了很多优化算法，如 Momentum、Adam、RMSprop 等，这些算法能够自适应地调整学习率，提高训练效率和稳定性。",
            "关于分布式系统的设计原则，我总结了几点关键的经验。首先是 CAP 定理，它指出在分布式系统中，一致性（Consistency）、可用性（Availability）和分区容错性（Partition tolerance）三者不可兼得，最多只能同时满足两个。在实际应用中，我们需要根据业务场景进行权衡。对于金融系统等对一致性要求高的场景，我们通常选择 CP 系统；对于社交网络等对可用性要求高的场景，我们通常选择 AP 系统。其次是分布式一致性问题，为了解决这个问题，人们提出了很多算法，如 Paxos、Raft、ZAB 等。这些算法的核心思想是通过多数派投票来达成共识，确保分布式系统中的各个节点能够就某个值达成一致。在实际应用中，我们可以使用 ZooKeeper、etcd 等成熟的分布式协调服务来简化开发。",
            "在研究自然语言处理的过程中，我深入学习了 Transformer 架构及其变体。Transformer 模型的核心是自注意力机制（Self-Attention），它能够捕捉序列中任意两个位置之间的依赖关系，无论它们相距多远。这与传统的 RNN、LSTM 等模型相比，具有更好的并行性和更长的依赖捕捉能力。在 Transformer 的基础上，人们提出了很多优秀的预训练模型，如 BERT、GPT、T5 等。这些模型在大规模语料上进行预训练，然后在具体任务上进行微调，取得了非常好的效果。BERT 采用双向编码器，适合理解类任务；GPT 采用单向解码器，适合生成类任务；T5 采用编码器 - 解码器结构，适合转换类任务。在选择预训练模型时，我们需要根据具体任务的特点进行选择。",
        ],
    }
    
    content_list = templates.get(scenario_type, templates["work"])
    base_content = random.choice(content_list)
    
    # 扩展到目标长度
    while len(base_content) < min_chars:
        base_content += " " + random.choice(content_list)
    
    # 添加一些变化
    variations = [
        f"\n\n【补充说明】{random.randint(2020, 2026)}年{random.randint(1, 12)}月{random.randint(1, 28)}日更新：",
        f"\n\n【相关文档】参见附件文档编号 DOC-{random.randint(1000, 9999)}，版本 v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
        f"\n\n【负责人】{random.choice(CHARACTERS.get(scenario_type, CHARACTERS['work']))}，联系方式：{random.randint(10000000000, 19999999999)}",
        f"\n\n【优先级】P{random.randint(0, 3)} - {'紧急' if random.random() > 0.7 else '重要' if random.random() > 0.5 else '一般'}",
        f"\n\n【状态】{'进行中' if random.random() > 0.5 else '已完成' if random.random() > 0.7 else '待开始'}",
    ]
    
    return base_content + random.choice(variations)

# 生成代码块
def generate_code_block(scenario_type: str) -> str:
    """生成代码块内容"""
    
    codes = {
        "work": [
            '''```python
# MFS 记忆系统核心模块
class MemoryFileSystem:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.storage = StorageBackend(self.config['storage'])
        self.index = IndexEngine(self.config['index'])
        self.cache = CacheLayer(self.config['cache'])
    
    async def create(self, path: str, content: bytes, metadata: dict = None) -> str:
        """创建文件节点"""
        node_id = generate_uuid()
        node = MemoryNode(
            id=node_id,
            path=path,
            content=content,
            metadata=metadata or {},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        await self.storage.save(node)
        await self.index.index_node(node)
        return node_id
    
    async def update(self, node_id: str, content: bytes = None, metadata: dict = None) -> bool:
        """更新文件节点"""
        node = await self.storage.get(node_id)
        if not node:
            raise FileNotFoundError(f"Node {node_id} not found")
        if content:
            node.content = content
        if metadata:
            node.metadata.update(metadata)
        node.updated_at = datetime.now()
        await self.storage.save(node)
        await self.index.update_node(node)
        return True
```''',
            '''```typescript
// API 网关接口定义
interface MemoryAPI {
  // 文件操作
  createFile(request: CreateFileRequest): Promise<CreateFileResponse>;
  updateFile(request: UpdateFileRequest): Promise<UpdateFileResponse>;
  deleteFile(request: DeleteFileRequest): Promise<DeleteFileResponse>;
  getFile(request: GetFileRequest): Promise<GetFileResponse>;
  
  // 搜索操作
  search(request: SearchRequest): Promise<SearchResponse>;
  suggest(request: SuggestRequest): Promise<SuggestResponse>;
  
  // 权限管理
  grantPermission(request: GrantPermissionRequest): Promise<GrantPermissionResponse>;
  revokePermission(request: RevokePermissionRequest): Promise<RevokePermissionResponse>;
  
  // 统计分析
  getStats(request: GetStatsRequest): Promise<GetStatsResponse>;
  getMetrics(request: GetMetricsRequest): Promise<GetMetricsResponse>;
}

// 错误处理
class MemoryError extends Error {
  constructor(
    public code: string,
    public message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'MemoryError';
  }
}
```''',
        ],
        "learning": [
            '''```python
# Transformer 自注意力机制实现
import torch
import torch.nn as nn
import math

class SelfAttention(nn.Module):
    def __init__(self, embed_size: int, num_heads: int):
        super().__init__()
        self.embed_size = embed_size
        self.num_heads = num_heads
        self.head_size = embed_size // num_heads
        
        self.query = nn.Linear(embed_size, embed_size)
        self.key = nn.Linear(embed_size, embed_size)
        self.value = nn.Linear(embed_size, embed_size)
        self.output = nn.Linear(embed_size, embed_size)
        
    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        batch_size, seq_len, _ = x.shape
        
        # 计算 Q, K, V
        Q = self.query(x).view(batch_size, seq_len, self.num_heads, self.head_size).transpose(1, 2)
        K = self.key(x).view(batch_size, seq_len, self.num_heads, self.head_size).transpose(1, 2)
        V = self.value(x).view(batch_size, seq_len, self.num_heads, self.head_size).transpose(1, 2)
        
        # 计算注意力分数
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.head_size)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        
        attention = torch.softmax(scores, dim=-1)
        output = torch.matmul(attention, V)
        
        # 合并多头输出
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.embed_size)
        return self.output(output)
```''',
        ],
        "personal": [
            '''```markdown
# 个人年度目标规划

## 📊 职业发展
- [ ] 完成 AI 工程师认证
- [ ] 主导至少 2 个核心项目
- [ ] 发表 1 篇技术文章
- [ ] 参加 3 次技术会议

## 🏃 健康管理
- [ ] 每周锻炼 4 次，每次 30 分钟以上
- [ ] 体重控制在 70±2kg
- [ ] 体脂率降至 15% 以下
- [ ] 每天睡眠 7-8 小时

## 📚 学习成长
- [ ] 阅读 24 本书（技术 8 本，管理 4 本，其他 12 本）
- [ ] 完成 2 门在线课程
- [ ] 学习一门新语言（日语/西班牙语）
- [ ] 每周写 1 篇学习总结

## 💰 财务规划
- [ ] 储蓄率达到收入的 30%
- [ ] 建立 6 个月应急基金
- [ ] 开始定投指数基金
- [ ] 学习理财知识，阅读 5 本理财书籍
```''',
        ],
    }
    
    code_list = codes.get(scenario_type, codes["work"])
    return random.choice(code_list)

# 生成单条消息
def generate_message(
    role: str,
    scenario_type: str,
    message_index: int,
    total_messages: int,
    base_date: datetime.datetime,
    conversation_context: Dict[str, Any]
) -> Dict[str, str]:
    """生成单条消息"""
    
    # 计算时间偏移（模拟真实对话的时间间隔）
    if message_index == 0:
        offset = 0
    elif message_index < 10:
        offset = message_index * random.randint(1, 5)
    elif message_index < 50:
        offset = 10 + message_index * random.randint(2, 10)
    else:
        offset = 100 + message_index * random.randint(5, 30)
    
    timestamp = generate_timestamp(base_date, offset)
    
    # 根据角色和位置生成内容
    if role == "user":
        if message_index == 0:
            # 开场白
            openings = {
                "work": [
                    f"你好，我想和你讨论一下{random.choice(PROJECTS['work'])}的相关事宜。",
                    f"关于{random.choice(PROJECTS['work'])}项目，我有一些想法想和你交流。",
                    f"我们什么时候可以开始{random.choice(PROJECTS['work'])}的需求分析？",
                ],
                "personal": [
                    f"最近我在思考一些问题，想和你聊聊。",
                    "今天有些感悟想记录下来，也听听你的建议。",
                    f"关于{random.choice(PROJECTS['personal'])}，我有些新的想法。",
                ],
                "learning": [
                    f"我在学习{random.choice(PROJECTS['learning'])}时遇到了一些问题。",
                    "今天学习的内容很有收获，想和你讨论一下。",
                    f"关于{random.choice(CHARACTERS['learning'])}提到的概念，我有些疑问。",
                ],
            }
            content = random.choice(openings.get(scenario_type, openings["work"]))
        elif message_index == total_messages - 1:
            # 结束语
            endings = [
                "好的，谢谢你的帮助，我先去执行了。",
                "明白了，我们下次再继续讨论。",
                "好的，我会按照这个方案进行，有问题再联系你。",
                "感谢详细的解答，我收获很多。",
            ]
            content = random.choice(endings)
        elif random.random() < 0.1:
            # 10% 的概率生成长文本
            content = generate_long_content(scenario_type)
        elif random.random() < 0.15:
            # 15% 的概率生成带代码的消息
            content = f"我写了一段代码，你看看有没有问题：\n\n{generate_code_block(scenario_type)}"
        else:
            # 普通消息
            contents = {
                "work": [
                    f"这个方案的可行性如何？需要考虑哪些风险？",
                    f"{random.choice(CHARACTERS['work'])}建议我们先做个原型验证一下。",
                    "能否详细说明一下技术实现的具体步骤？",
                    f"关于{random.choice(PROJECTS['work'])}的进度，目前遇到了一些挑战。",
                    "这个需求是否需要调整优先级？",
                    f"我整理了相关的文档，路径是 /work/{random.choice(PROJECTS['work'])}/docs/",
                    "是否需要安排一次评审会议？",
                    f"预算方面，初步估算需要{random.randint(10, 500)}万。",
                ],
                "personal": [
                    "你觉得这个决定明智吗？",
                    f"我和{random.choice(CHARACTERS['personal'])}聊了聊，他/她也这么认为。",
                    "我有些犹豫，想听听你的看法。",
                    f"关于{random.choice(PROJECTS['personal'])}，你有什么建议？",
                    "今天发生了一些事情，让我重新思考这个问题。",
                    "我觉得需要制定一个更详细的计划。",
                    f"回顾过去，我发现{random.randint(1, 12)}个月前做的决定现在看来的确有问题。",
                ],
                "learning": [
                    f"这个概念和{random.choice(PROJECTS['learning'])}有什么联系吗？",
                    "我查了一些资料，但还是不太理解。",
                    f"{random.choice(CHARACTERS['learning'])}推荐的论文我看了，很有启发。",
                    "能否用更通俗的例子解释一下？",
                    "我做了个笔记，整理了一下知识点。",
                    "这个理论和实际应用之间有什么差距？",
                    f"我准备深入研究{random.choice(PROJECTS['learning'])}这个方向。",
                ],
            }
            content_list = contents.get(scenario_type, contents["work"])
            content = random.choice(content_list)
            
            # 偶尔添加一些追问
            if random.random() < 0.3:
                follow_ups = [
                    "另外，我还想问一下...",
                    "对了，还有一个问题...",
                    "补充一点，...",
                    "顺便提一下，...",
                ]
                content = random.choice(follow_ups) + content
    
    else:  # assistant
        if message_index == 1:
            # 首次回复
            responses = [
                "你好！很高兴能和你讨论这个问题。让我先了解一下具体情况...",
                "好的，我来帮你分析一下。首先我们需要明确几个关键点...",
                "感谢你的信任。关于这个问题，我有以下几点建议...",
            ]
            content = random.choice(responses)
        elif random.random() < 0.08:
            # 8% 的概率生成详细回复（长文本）
            content = "让我详细分析一下这个问题：\n\n" + generate_long_content(scenario_type)
        elif random.random() < 0.1:
            # 10% 的概率生成带代码的回复
            content = "根据你的需求，我建议这样实现：\n\n" + generate_code_block(scenario_type)
        else:
            # 普通回复
            responses = {
                "work": [
                    "从技术角度来看，这个方案是可行的。建议分三个阶段实施：第一阶段完成基础架构搭建，第二阶段实现核心功能，第三阶段进行优化和测试。",
                    "我理解你的顾虑。确实，这个方案存在一些风险，主要包括技术风险、时间风险和人员风险。我们可以制定相应的应对措施。",
                    f"根据历史数据，类似{random.choice(PROJECTS['work'])}的项目平均周期是{random.randint(3, 12)}个月，预算在{random.randint(50, 500)}万左右。",
                    "建议我们先进行一次全面的需求调研，邀请相关业务部门参与，确保需求的完整性和准确性。",
                    f"我查了一下相关文档，在 /work/{random.choice(PROJECTS['work'])}/ 目录下有一些参考资料。",
                    "这个决策需要综合考虑多个因素，包括技术可行性、成本效益、时间窗口等。",
                ],
                "personal": [
                    "我理解你的感受。这种情况下，最重要的是先冷静下来，理性分析问题。",
                    "从旁观者的角度看，我觉得你可以考虑以下几个方面：首先...其次...最后...",
                    "这是一个重要的决定，建议你多给自己一些时间思考，也可以和信任的人商量。",
                    f"回顾你之前的经历，{random.choice(CHARACTERS['personal'])}的事情处理得就很好，可以借鉴当时的经验。",
                    "我觉得你的想法很有价值，但执行层面可能需要更详细的规划。",
                    "人生就是这样，充满了各种选择和不确定性。重要的是做出选择后坚定地走下去。",
                ],
                "learning": [
                    "这个概念确实有些抽象。让我换个方式解释：想象一下...",
                    f"你提到的{random.choice(PROJECTS['learning'])}是一个很好的切入点。从这个角度出发，我们可以...",
                    "我建议你先掌握基础知识，然后再深入理解高级概念。学习路径应该是循序渐进的。",
                    f"{random.choice(CHARACTERS['learning'])}在这个领域很有研究，可以参考他/她的论文和演讲。",
                    "理论知识固然重要，但实践同样关键。建议你边学边做，通过项目来巩固理解。",
                    "这个领域发展很快，建议你关注最新的研究进展和行业动态。",
                ],
            }
            content_list = responses.get(scenario_type, responses["work"])
            content = random.choice(content_list)
            
            # 偶尔添加操作建议
            if random.random() < 0.2:
                ops = [
                    f"需要我帮你创建一个相关的文档吗？路径可以是 /{scenario_type}/{random.choice(PROJECTS.get(scenario_type, PROJECTS['work']))}/",
                    "我可以帮你整理一份详细的笔记，方便后续查阅。",
                    "要不要把这个讨论记录下来，方便以后回顾？",
                    f"建议把这个知识点添加到 /{scenario_type}/knowledge_base/ 中。",
                ]
                content += "\n\n" + random.choice(ops)
    
    return {
        "role": role,
        "content": content,
        "timestamp": timestamp,
    }

# 生成操作记录
def generate_operations(
    scenario_type: str,
    conversation_id: str,
    num_operations: int
) -> List[Dict[str, Any]]:
    """生成操作记录"""
    
    operations = []
    base_paths = {
        "work": ["/work", "/projects", "/docs", "/archive"],
        "personal": ["/personal", "/memories", "/journal", "/plans"],
        "learning": ["/learning", "/notes", "/courses", "/research"],
    }
    
    paths = base_paths.get(scenario_type, base_paths["work"])
    projects = PROJECTS.get(scenario_type, PROJECTS["work"])
    
    for i in range(num_operations):
        op_type = random.choice(OPERATION_TYPES)
        project = random.choice(projects)
        path = f"{random.choice(paths)}/{project}/{random.choice(['docs', 'notes', 'data', 'config'])}/item_{random.randint(1, 999)}"
        
        operation = {
            "type": op_type,
            "path": path,
            "timestamp": f"2026-{random.randint(1, 4):02d}-{random.randint(1, 28):02d}T{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}Z",
        }
        
        if op_type in ["CREATE", "UPDATE"]:
            operation["content"] = f"内容摘要：关于{project}的第{random.randint(1, 100)}条记录"
            operation["metadata"] = {
                "author": random.choice(CHARACTERS.get(scenario_type, CHARACTERS["work"])),
                "version": f"v{random.randint(1, 5)}.{random.randint(0, 9)}",
                "tags": [f"tag_{random.randint(1, 20)}" for _ in range(random.randint(1, 5))],
            }
        elif op_type == "SEARCH":
            operation["query"] = f"搜索关键词：{project} {random.choice(['需求', '设计', '实现', '测试', '文档'])}"
            operation["results_count"] = random.randint(0, 100)
        elif op_type == "DELETE":
            operation["reason"] = random.choice(["过期清理", "重复数据", "用户请求", "系统维护"])
        
        operations.append(operation)
    
    return operations

# 生成单个对话
def generate_conversation(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """生成单个完整对话"""
    
    conversation_id = scenario["id"]
    scenario_type = scenario["type"]
    
    # 随机确定消息数量（100-300）
    message_count = random.randint(100, 300)
    
    # 生成基础日期（过去 30 天内的随机日期）
    base_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))
    base_date = base_date.replace(hour=random.randint(8, 22), minute=0, second=0)
    
    # 生成对话上下文
    conversation_context = {
        "participants": random.sample(CHARACTERS.get(scenario_type, CHARACTERS["work"]), k=3),
        "main_project": random.choice(PROJECTS.get(scenario_type, PROJECTS["work"])),
        "key_topics": [f"topic_{i}" for i in range(random.randint(3, 8))],
    }
    
    # 生成消息
    messages = []
    for i in range(message_count):
        role = "user" if i % 2 == 0 else "assistant"
        message = generate_message(
            role=role,
            scenario_type=scenario_type,
            message_index=i,
            total_messages=message_count,
            base_date=base_date,
            conversation_context=conversation_context
        )
        messages.append(message)
    
    # 生成操作记录（每个对话 20-50 个操作）
    num_operations = random.randint(20, 50)
    operations = generate_operations(scenario_type, conversation_id, num_operations)
    
    # 计算总字数
    total_chars = sum(len(msg["content"]) for msg in messages)
    
    # 如果字数不足，添加更多长内容
    while total_chars < 100000:
        # 在随机位置插入长文本消息
        insert_pos = random.randint(10, len(messages) - 10)
        long_msg = {
            "role": "user" if insert_pos % 2 == 0 else "assistant",
            "content": generate_long_content(scenario_type, min_chars=8000, max_chars=15000),
            "timestamp": generate_timestamp(base_date, insert_pos * 5),
        }
        messages.insert(insert_pos, long_msg)
        total_chars = sum(len(msg["content"]) for msg in messages)
    
    return {
        "conversation_id": conversation_id,
        "scenario": scenario["name"],
        "scenario_type": scenario_type,
        "total_chars": total_chars,
        "message_count": len(messages),
        "operation_count": len(operations),
        "messages": messages,
        "operations": operations,
        "tags": scenario["tags"],
        "metadata": {
            "generated_at": datetime.datetime.now().isoformat() + "Z",
            "participants": conversation_context["participants"],
            "main_project": conversation_context["main_project"],
        },
    }

# 主函数
def main():
    print("开始生成超长对话数据...")
    print(f"目标文件：{OUTPUT_FILE}")
    print(f"场景数量：{len(SCENARIOS)}")
    print()
    
    conversations = []
    total_chars = 0
    total_messages = 0
    total_operations = 0
    
    for i, scenario in enumerate(SCENARIOS, 1):
        print(f"[{i}/{len(SCENARIOS)}] 生成对话 {scenario['id']} - {scenario['name']}...")
        
        conversation = generate_conversation(scenario)
        conversations.append(conversation)
        
        total_chars += conversation["total_chars"]
        total_messages += conversation["message_count"]
        total_operations += conversation["operation_count"]
        
        print(f"  ✓ 完成 - 字数：{conversation['total_chars']:,}, 消息数：{conversation['message_count']}, 操作数：{conversation['operation_count']}")
    
    # 写入文件
    print(f"\n正在写入文件...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)
    
    # 验证文件
    print(f"验证文件...")
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    
    file_size = os.path.getsize(OUTPUT_FILE)
    
    # 输出摘要报告
    print("\n" + "="*60)
    print("生成完成！摘要报告：")
    print("="*60)
    print(f"输出文件：{OUTPUT_FILE}")
    print(f"文件大小：{file_size / 1024 / 1024:.2f} MB")
    print(f"对话数量：{len(conversations)}")
    print(f"总字数：{total_chars:,}")
    print(f"总消息数：{total_messages:,}")
    print(f"总操作数：{total_operations:,}")
    print(f"平均每个对话字数：{total_chars // len(conversations):,}")
    print(f"平均每个对话消息数：{total_messages // len(conversations)}")
    print(f"平均每个对话操作数：{total_operations // len(conversations)}")
    print()
    print("各对话详情：")
    for conv in conversations:
        print(f"  {conv['conversation_id']} - {conv['scenario']}: {conv['total_chars']:,}字，{conv['message_count']}条消息，{conv['operation_count']}个操作")
    print()
    print(f"✓ JSON 格式验证通过")
    print(f"✓ 总数据量：{file_size / 1024 / 1024:.2f} MB {'✓' if file_size > 1024 * 1024 else '⚠ 小于 1MB'}")
    print("="*60)

if __name__ == "__main__":
    import os
    main()
