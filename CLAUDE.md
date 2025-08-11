# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述
LiteAgent 是一个轻量级的 AI Agent 框架，设计简洁且易于扩展。项目采用模块化架构，每个模块职责单一明确。

## 核心架构

### 模块结构
- **agent.py**: Agent 核心类，管理代理配置、指令和工具集
- **context.py**: 对话上下文管理，维护消息历史和 token 统计
- **model.py**: LLM 接口抽象层，基于 LiteLLM 支持多种模型
- **runner.py**: 执行引擎，处理工具调用循环和对话流程
- **tool.py**: 工具系统，支持函数装饰器自动转换

### 设计模式
- 策略模式：Model 抽象基类支持不同 LLM 实现
- 装饰器模式：@function_tool 简化工具创建
- 数据类：广泛使用 @dataclass 减少样板代码

## 开发环境设置

### 使用 uv 原生管理（推荐）
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone https://github.com/JiayuXu0/LiteAgent.git
cd LiteAgent

# uv 会自动创建虚拟环境并管理依赖
# 添加核心依赖
uv add litellm pydantic

# 添加开发依赖
uv add --dev pyright ruff pytest pytest-cov pytest-asyncio

# 添加可选依赖
uv add python-dotenv
```

### 验证安装
```bash
# 检查依赖状态
uv tree

# 检查虚拟环境
uv run python --version
uv run python -c "import liteagent; print('✅ 安装成功')"
```

### 环境变量配置
```bash
# 创建 .env 文件
MODEL=gpt-3.5-turbo  # 或其他支持的模型
API_KEY=your_api_key
BASE_URL=https://api.openai.com/v1  # 可选
```

## 常用开发命令

### 构建和打包
```bash
# 使用 uv 构建
uv build

# 构建后的文件在 dist/ 目录
# - liteagent-0.1.0-py3-none-any.whl  # wheel 包
# - liteagent-0.1.0.tar.gz             # 源码包

# 安装构建的 wheel 包
pip install dist/liteagent-0.1.0-py3-none-any.whl
```

### 类型检查
```bash
# 使用 uv run 运行 pyright
uv run pyright

# 检查特定目录
uv run pyright src/

# 检查特定文件
uv run pyright src/liteagent/agent.py
```

### 代码风格检查
```bash
# 运行 ruff 代码检查
uv run ruff check .

# 自动修复可修复的问题
uv run ruff check --fix .

# 格式化代码
uv run ruff format .

# 检查特定文件
uv run ruff check src/liteagent/
```

### 运行测试
```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_agent.py

# 运行并显示覆盖率
uv run pytest --cov=src/liteagent --cov-report=html

# 运行特定标记的测试
uv run pytest -m unit        # 只运行单元测试
uv run pytest -m integration # 只运行集成测试

# 详细输出
uv run pytest -v --cov-report=term-missing
```

### 当前项目状态
- ✅ **测试**: 30 个测试全部通过
- 📊 **覆盖率**: 60% (核心模块 90%+)
- 🔧 **依赖**: 2 个核心，5 个开发依赖
- 📦 **包大小**: wheel 12.4KB

## Git 工作流

项目采用 gitflow 规范：
- **feature/xxx**: 开发新特性分支
- **hotfix/xxx**: 修复紧急问题分支
- **master**: 主分支

```bash
# 创建新特性分支
git checkout -b feature/new-feature

# 创建修复分支
git checkout -b hotfix/fix-issue
```

## 代码规范

### 类型注解
所有函数和方法必须包含完整的类型注解：
```python
def process_message(content: str, role: str = "user") -> Dict[str, Any]:
    pass
```

### 错误处理
优先使用具体的异常类型，避免裸露的 except：
```python
try:
    result = tool.execute(args)
except ToolExecutionError as e:
    logger.error(f"Tool execution failed: {e}")
```

### 安全注意事项
- **避免 eval()**: runner.py:85 中的 eval() 存在安全风险，应替换为安全的 JSON 解析
- **敏感信息**: 永远不要在代码中硬编码 API 密钥或敏感信息

## 项目结构

```
LiteAgent/
├── src/
│   └── liteagent/          # 源代码包
│       ├── __init__.py      # 包入口和导出
│       ├── agent.py         # Agent 核心类
│       ├── context.py       # 上下文管理
│       ├── model.py         # LLM 接口抽象
│       ├── runner.py        # 执行引擎
│       └── tool.py          # 工具系统
├── tests/                   # 测试套件
│   ├── conftest.py         # pytest fixtures
│   ├── test_agent.py       # Agent 单元测试
│   ├── test_context.py     # Context 单元测试
│   └── test_tool.py        # Tool 单元测试
├── examples/               # 使用示例
│   ├── basic_usage.py      # 基础功能演示
│   └── custom_model.py     # 自定义模型示例
├── docs/                   # 文档目录
├── dist/                   # 构建输出（自动生成）
├── pyproject.toml         # 项目配置（支持 uv 和 pip）
├── README.md              # 项目说明
├── CLAUDE.md              # 本开发指南
├── LICENSE                # MIT 许可证
└── .gitignore            # Git 忽略配置
```

## 待改进事项

### 已验证功能
1. ✅ **uv 包管理**: 完全基于 uv 原生命令管理依赖
2. ✅ **代码质量**: pyright 类型检查，ruff 代码风格检查通过
3. ✅ **测试套件**: 30 个测试全部通过，覆盖率 60%
4. ✅ **包构建**: 成功构建 wheel 和源码包
5. ✅ **包安装**: 验证 wheel 包可正常安装和导入

### 待改进事项
1. **安全性**: 替换 runner.py:85 的 eval() 为安全的 JSON 解析
2. **日志系统**: 添加结构化日志替代 print 调试
3. **异步支持**: 实现异步 API 调用提高性能
4. **测试覆盖**: 增加更多测试用例，目标覆盖率 > 90%
5. **CI/CD**: 添加 GitHub Actions 自动化测试和发布
6. **文档**: 添加 API 文档和更多使用示例
7. **错误处理**: 更精细的异常类型和错误信息

## 验证过的工作流程

### 完整的开发流程
```bash
# 1. 设置项目
git clone https://github.com/JiayuXu0/LiteAgent.git
cd LiteAgent

# 2. 使用 uv 管理依赖
uv add litellm pydantic
uv add --dev pyright ruff pytest pytest-cov pytest-asyncio

# 3. 运行代码质量检查
uv run ruff check --fix .
uv run ruff format .
uv run pyright

# 4. 运行测试
uv run pytest --cov=src/liteagent

# 5. 构建包
uv build

# 6. 验证包
pip install dist/liteagent-0.1.0-py3-none-any.whl
```

## 快速开始示例

```python
from liteagent import Agent, Runner, function_tool

# 定义工具
@function_tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    # 注意：实际使用应该用安全的解析器
    return str(eval(expression))

# 创建 Agent
agent = Agent(
    name="Assistant",
    instructions="你是一个有用的助手",
    tools=[calculate]
)

# 运行对话
result = Runner.run(agent, "计算 2+2")
print(result.content)
```

## 项目特点
- ✅ **现代化工具链**: 基于 uv 的包管理
- ✅ **轻量级设计**: wheel 包仅 12.4KB
- ✅ **完整测试**: 30 个测试，60% 覆盖率
- ✅ **类型安全**: 完整的类型注解和 pyright 检查
- ✅ **代码质量**: ruff 代码风格检查和格式化
- ✅ **模块化架构**: 易于扩展和维护
- ✅ **多模型支持**: 通过 LiteLLM 支持多种 LLM 提供商