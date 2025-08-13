# ZipAgent

[![PyPI version](https://badge.fury.io/py/zipagent.svg)](https://badge.fury.io/py/zipagent)
[![Python version](https://img.shields.io/pypi/pyversions/zipagent.svg)](https://pypi.org/project/zipagent/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/JiayuXu0/LiteAgent/workflows/tests/badge.svg)](https://github.com/JiayuXu0/LiteAgent/actions)

> 🚀 轻量级的 AI Agent 框架，让 AI 工具集成变得简单高效

ZipAgent 是一个现代化的 Python AI Agent 框架，专注于简洁、高效和易扩展。无论是构建聊天机器人、智能助手还是复杂的 AI 工作流，ZipAgent 都能让你快速上手。

## ✨ 核心特性

- **🎯 简洁 API**: 极简设计，几行代码构建 AI Agent
- **🔧 工具系统**: 强大的 `@function_tool` 装饰器，轻松扩展 AI 能力
- **🌊 流式输出**: 完整的流式处理支持，提供实时交互体验
- **📝 上下文管理**: 自动管理对话历史和上下文状态
- **🔗 MCP 集成**: 原生支持 Model Context Protocol，集成外部工具
- **⚡ 现代化**: 基于 Python 3.10+，支持异步编程
- **🧪 高质量**: 120+ 测试用例，78% 代码覆盖率

## 🚀 快速开始

### 安装

```bash
pip install zipagent
```

### 5分钟上手

```python
from zipagent import Agent, Runner, function_tool

# 1. 定义工具
@function_tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    return str(eval(expression))

# 2. 创建 Agent
agent = Agent(
    name="MathAssistant",
    instructions="你是一个数学助手",
    tools=[calculate]
)

# 3. 开始对话
result = Runner.run(agent, "计算 23 + 45")
print(result.content)  # "23 + 45 的计算结果是 68"
```

## 📚 功能展示

### 🌊 流式输出

```python
from zipagent import StreamEventType

# 实时流式响应
for event in Runner.run_stream(agent, "解释什么是人工智能"):
    if event.type == StreamEventType.ANSWER_DELTA:
        print(event.content, end="", flush=True)  # 打字机效果
    elif event.type == StreamEventType.TOOL_CALL:
        print(f"🔧 调用工具: {event.tool_name}")
```

### 📝 上下文管理

```python
from zipagent import Context

# 多轮对话
context = Context()

result1 = Runner.run(agent, "我叫小明", context=context)
result2 = Runner.run(agent, "我叫什么名字？", context=context)
print(result2.content)  # "你叫小明"

# 对话统计
print(f"对话轮数: {context.turn_count}")
print(f"Token 使用: {context.usage}")
```

### 🔗 MCP 工具集成

```python
from zipagent import MCPTool

# 连接外部 MCP 工具
async def demo():
    # 连接高德地图工具
    amap_tools = await MCPTool.connect(
        command="npx",
        args=["-y", "@amap/amap-maps-mcp-server"],
        env={"AMAP_MAPS_API_KEY": "your_key"}
    )
    
    # 混合使用本地工具和 MCP 工具
    agent = Agent(
        name="MapAssistant",
        instructions="你是一个地图助手",
        tools=[calculate, amap_tools]  # 统一接口！
    )
    
    result = Runner.run(agent, "北京今天天气怎么样？")
    print(result.content)
```

## 🔧 高级功能

### 异常处理

```python
from zipagent import ToolExecutionError, MaxTurnsError

try:
    result = Runner.run(agent, "计算 10 / 0", max_turns=3)
except ToolExecutionError as e:
    print(f"工具执行失败: {e.details['tool_name']}")
except MaxTurnsError as e:
    print(f"达到最大轮次: {e.details['max_turns']}")
```

### 自定义模型

```python
from zipagent import OpenAIModel

# 自定义模型配置
model = OpenAIModel(
    model="gpt-4",
    api_key="your_api_key",
    base_url="https://api.openai.com/v1"
)

agent = Agent(
    name="CustomAgent",
    instructions="你是一个助手",
    tools=[calculate],
    model=model
)
```

## 🎯 使用场景

- **💬 聊天机器人**: 客服、问答、闲聊机器人
- **🔧 智能助手**: 代码助手、写作助手、数据分析助手  
- **🌐 工具集成**: 集成 API、数据库、第三方服务
- **📊 工作流自动化**: 复杂的多步骤任务自动化
- **🔍 知识问答**: 基于知识库的智能问答系统

## 📖 完整示例

查看 `examples/` 目录获取更多示例：

- [`basic_demo.py`](examples/basic_demo.py) - 基础功能演示
- [`stream_demo.py`](examples/stream_demo.py) - 流式输出演示
- [`mcp_demo.py`](examples/mcp_demo.py) - MCP 工具集成演示

```bash
# 运行示例
python examples/basic_demo.py
python examples/stream_demo.py
python examples/mcp_demo.py
```

## 🏗️ 项目架构

```
ZipAgent/
├── src/zipagent/           # 核心框架
│   ├── agent.py            # Agent 核心类
│   ├── context.py          # 上下文管理
│   ├── model.py            # LLM 模型抽象
│   ├── runner.py           # 执行引擎
│   ├── tool.py             # 工具系统
│   ├── stream.py           # 流式处理
│   ├── mcp_tool.py         # MCP 工具集成
│   └── exceptions.py       # 异常系统
├── examples/               # 使用示例
├── tests/                  # 测试套件（120+ 测试）
└── docs/                   # 文档
```

## 📦 依赖

**核心依赖**:
- `openai` - OpenAI API 客户端
- `pydantic` - 数据验证

**可选依赖**:
- `mcp` - MCP 工具支持
- `nest-asyncio` - 嵌套异步支持
- `python-dotenv` - 环境变量管理

## 🛠️ 开发

### 本地开发环境

```bash
# 克隆项目
git clone https://github.com/JiayuXu0/LiteAgent.git
cd LiteAgent

# 使用 uv 管理依赖（推荐）
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# 运行测试
uv run pytest

# 代码检查
uv run ruff check --fix
uv run pyright
```

### 贡献指南

我们欢迎各种形式的贡献！

1. 🐛 **报告 Bug**: 提交 [Issue](https://github.com/JiayuXu0/LiteAgent/issues)
2. 💡 **功能建议**: 讨论新功能想法
3. 📝 **文档改进**: 完善文档和示例
4. 🔧 **代码贡献**: 提交 Pull Request

### 开发规范

- 使用 `ruff` 进行代码格式化和检查
- 使用 `pyright` 进行类型检查
- 编写测试用例，保持高覆盖率
- 遵循语义化版本规范

## 📊 性能

- ⚡ **启动速度**: 毫秒级初始化
- 🔄 **并发能力**: 支持异步并发处理
- 💾 **内存占用**: 轻量级设计，低内存占用
- 📦 **包大小**: Wheel 包仅 ~15KB

## 🗺️ 路线图

- [ ] **多模型支持**: Claude、Gemini、本地模型
- [ ] **插件系统**: 更丰富的扩展机制
- [ ] **可视化界面**: Web UI 和监控面板
- [ ] **分布式支持**: 多实例协作
- [ ] **性能优化**: 缓存和批处理优化

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 致谢

感谢所有贡献者和社区支持！

- OpenAI - 提供强大的 LLM API
- MCP 社区 - Model Context Protocol 标准
- Python 生态 - 优秀的开发工具链

---

⭐ 如果这个项目对你有帮助，请给我们一个 Star！
