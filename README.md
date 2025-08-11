# LiteAgent

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

轻量级的 AI Agent 框架，提供简洁而强大的 Agent 构建能力。

## 特性

- 🚀 **轻量级设计** - 核心代码简洁，易于理解和扩展
- 🔧 **模块化架构** - 清晰的模块划分，各组件职责单一
- 🎯 **完整类型支持** - 全面的类型注解，提高代码质量
- 🔌 **灵活的模型接口** - 支持 OpenAI 兼容的 API
- 🛠️ **优雅的工具系统** - 使用装饰器模式简化工具创建
- 🧠 **思考模式** - 可启用思考模式，要求 AI 在调用工具前显示思考过程
- 📊 **上下文管理** - 完整的对话历史和 token 统计

## 安装

### 使用 uv（推荐）

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆仓库
git clone https://github.com/JiayuXu0/LiteAgent.git
cd LiteAgent

# uv 会自动创建虚拟环境并安装依赖
uv add openai pydantic

# 安装开发依赖（可选）
uv add --dev pyright ruff pytest pytest-cov pytest-asyncio

# 以可编辑模式安装包（用于运行示例代码）
uv add --dev --editable .
```

### 从预构建的 wheel 包安装

```bash
# 下载并安装预构建的 wheel 包
pip install https://github.com/JiayuXu0/LiteAgent/releases/download/v0.1.0/liteagent-0.1.0-py3-none-any.whl

# 或从本地构建的包安装
uv build
pip install dist/liteagent-0.1.0-py3-none-any.whl
```

### 从源码安装（传统方式）

```bash
# 克隆仓库
git clone https://github.com/JiayuXu0/LiteAgent.git
cd LiteAgent

# 使用 pip 安装
pip install -e .
```

## 快速开始

### 基础使用

```python
from liteagent import Agent, Runner

# 创建一个简单的 Agent
agent = Agent(
    name="助手",
    instructions="你是一个有用的 AI 助手"
)

# 运行对话
result = Runner.run(agent, "你好，请介绍一下你自己")
print(result.content)
```

### 使用工具

```python
from liteagent import Agent, Runner, function_tool

# 定义工具函数
@function_tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    return str(eval(expression))  # 注意：实际使用应该用安全的解析器

# 创建带工具的 Agent
agent = Agent(
    name="计算助手",
    instructions="你是一个可以进行数学计算的助手",
    tools=[calculate]
)

# 使用工具
result = Runner.run(agent, "请计算 15 + 25")
print(result.content)
```

### 多轮对话

```python
from liteagent import Agent, Runner, Context

# 创建上下文以保持对话历史
context = Context()

agent = Agent(
    name="对话助手",
    instructions="你是一个友好的对话助手"
)

# 第一轮对话
result = Runner.run(agent, "我叫小明", context)
print(result.content)

# 第二轮对话（记住了之前的内容）
result = Runner.run(agent, "你还记得我的名字吗？", context)
print(result.content)

# 查看 token 使用情况
print(f"总 tokens: {context.usage.total_tokens}")
```

### 思考模式工具调用

```python
from liteagent import Agent, Runner, function_tool

@function_tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    return str(eval(expression))

# 方式1: Agent级别启用思考模式
agent = Agent(
    name="思考助手",
    instructions="你是一个仔细思考的助手",
    tools=[calculate],
    thinking_tool_mode=True  # 启用思考模式
)

result = Runner.run(agent, "计算 15 * 8")
print(result.content)
# 输出会包含 <thinking> 标签显示AI的思考过程

# 方式2: 运行时启用思考模式
normal_agent = Agent(
    name="普通助手",
    instructions="你是一个助手",
    tools=[calculate]
)

result = Runner.run(
    normal_agent, 
    "计算 100 / 4", 
    thinking_tool_mode=True  # 运行时覆盖启用
)
print(result.content)
```

### 自定义模型

```python
from liteagent import Agent, Model, ModelResponse
from liteagent.context import Usage

class CustomModel(Model):
    """自定义模型实现"""
    
    def generate(self, messages, tools=None):
        # 实现你的模型逻辑
        return ModelResponse(
            content="自定义响应",
            tool_calls=[],
            usage=Usage(),
            finish_reason="stop"
        )

# 使用自定义模型
agent = Agent(
    name="自定义助手",
    instructions="使用自定义模型",
    model=CustomModel()
)
```

## 环境配置

创建 `.env` 文件配置 API 密钥（参考 `.env.example`）：

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，填入你的配置
# 示例：使用阿里云Qwen API
MODEL=openai/qwen3-30b-a3b-instruct-2507
API_KEY=sk-your-api-key-here
BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 可选参数
MAX_TOKENS=1000
TEMPERATURE=0.7
```

示例代码会自动加载项目根目录的 `.env` 文件。

## 开发

### 设置开发环境

```bash
# 克隆仓库
git clone https://github.com/JiayuXu0/LiteAgent.git
cd LiteAgent

# 使用 uv 安装核心依赖
uv add openai pydantic

# 安装开发工具
uv add --dev pyright ruff pytest pytest-cov pytest-asyncio
```

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_agent.py

# 生成覆盖率报告
uv run pytest --cov=src/liteagent --cov-report=html
```

**当前测试状态**: ✅ 37 个测试全部通过，覆盖率 70%

### 代码质量检查

```bash
# 类型检查
uv run pyright

# 代码风格检查和自动修复
uv run ruff check --fix .

# 代码格式化
uv run ruff format .
```

### 构建发布

```bash
# 构建包
uv build

# 生成的文件在 dist/ 目录
ls dist/
# liteagent-0.1.0-py3-none-any.whl (12.4KB)
# liteagent-0.1.0.tar.gz (15.1KB)

# 验证构建的包
pip install dist/liteagent-0.1.0-py3-none-any.whl
```

## 项目结构

```
LiteAgent/
├── src/
│   └── liteagent/          # 源代码
│       ├── __init__.py      # 包入口
│       ├── agent.py         # Agent 核心类
│       ├── context.py       # 上下文管理
│       ├── model.py         # LLM 接口
│       ├── runner.py        # 执行引擎
│       └── tool.py          # 工具系统
├── tests/                   # 测试文件
│   ├── conftest.py         # pytest 配置
│   ├── test_agent.py       # Agent 测试
│   ├── test_context.py     # Context 测试
│   └── test_tool.py        # Tool 测试
├── examples/               # 示例代码
│   ├── basic_usage.py      # 基础示例
│   └── custom_model.py     # 自定义模型示例
├── docs/                   # 文档
├── pyproject.toml         # 项目配置
├── README.md              # 项目说明
├── CLAUDE.md              # 开发指南
└── LICENSE                # 许可证
```

## 贡献

欢迎贡献代码！请查看 [CLAUDE.md](CLAUDE.md) 了解开发指南。

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 项目状态

- 📦 **包大小**: wheel 12.4KB, 源码包 15.1KB
- 🧪 **测试状态**: 37 个测试全部通过
- 📊 **测试覆盖率**: 60% (核心模块 90%+)
- 🔧 **依赖**: 2 个核心依赖，5 个开发依赖
- ✅ **构建验证**: wheel 包可正常安装和导入

## 致谢

- 基于 [OpenAI 客户端](https://github.com/openai/openai-python) 提供 API 支持
- 使用 [uv](https://github.com/astral-sh/uv) 进行现代化包管理
- 使用 [Ruff](https://github.com/astral-sh/ruff) 进行代码质量控制
- 使用 [PyRight](https://github.com/microsoft/pyright) 进行静态类型检查
