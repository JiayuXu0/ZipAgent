<div align="center">

⭐ **如果这个项目对你有帮助，请给我们一个 Star！** ⭐

<p align="center">
  <img src="docs/assets/logo.jpg" alt="ZipAgent Logo" width="120"/>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=45&duration=3000&pause=1000&color=2E86AB&center=true&vCenter=true&width=300&height=60&lines=ZipAgent" alt="ZipAgent Title"/>
</p>

[![PyPI version](https://badge.fury.io/py/zipagent.svg)](https://badge.fury.io/py/zipagent)
[![Downloads](https://pepy.tech/badge/zipagent)](https://pepy.tech/project/zipagent)
[![Python version](https://img.shields.io/pypi/pyversions/zipagent.svg)](https://pypi.org/project/zipagent/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[📚 文档](https://jiayuxu0.github.io/zipagent) | [🚀 快速开始](#-快速开始) | [💬 讨论](https://github.com/JiayuXu0/ZipAgent/discussions) | [🐛 问题反馈](https://github.com/JiayuXu0/ZipAgent/issues) | [🌍 English](README_EN.md)

</div>

ZipAgent 是一个现代化的 Python AI Agent 框架，专注于简洁、高效和易扩展。**仅用 700 行核心代码实现 Agent 引擎、工具系统、对话管理的完整智能体框架，让你快速构建专属的 AI 助手。**

## 🎯 应用场景

<table>
<tr>
<td align="center">
  <img src="docs/assets/icon_chatbot.png" width="60px" alt="智能客服"/>
  <br/><b>智能客服</b><br/>
  <small>自动回答常见问题<br/>处理订单查询</small>
</td>
<td align="center">
  <img src="docs/assets/icon_code.png" width="60px" alt="代码助手"/>
  <br/><b>代码助手</b><br/>
  <small>代码review和生成<br/>bug修复建议</small>
</td>
<td align="center">
  <img src="docs/assets/icon_data.png" width="60px" alt="数据分析"/>
  <br/><b>数据分析</b><br/>
  <small>自动生成报表<br/>数据洞察发现</small>
</td>
</tr>
<tr>
<td align="center">
  <img src="docs/assets/icon_content.png" width="60px" alt="内容生成"/>
  <br/><b>内容生成</b><br/>
  <small>文章写作助手<br/>营销文案生成</small>
</td>
<td align="center">
  <img src="docs/assets/icon_automation.png" width="60px" alt="工作流自动化"/>
  <br/><b>工作流自动化</b><br/>
  <small>任务调度执行<br/>流程自动化</small>
</td>
<td align="center">
  <img src="docs/assets/icon_qa.png" width="60px" alt="知识问答"/>
  <br/><b>知识问答</b><br/>
  <small>企业知识库<br/>智能问答系统</small>
</td>
</tr>
</table>

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


## 🛠️ 开发

### 本地开发环境

```bash
# 克隆项目
git clone https://github.com/JiayuXu0/ZipAgent.git
cd ZipAgent

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

1. 🐛 **报告 Bug**: 提交 [Issue](https://github.com/JiayuXu0/ZipAgent/issues)
2. 💡 **功能建议**: 讨论新功能想法
3. 📝 **文档改进**: 完善文档和示例
4. 🔧 **代码贡献**: 提交 Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 致谢

感谢所有贡献者和社区支持！

- OpenAI - 提供强大的 LLM API
- MCP 社区 - Model Context Protocol 标准
- Python 生态 - 优秀的开发工具链