"""Simple Agent Framework - 简化的Agent框架实现"""

__version__ = "0.1.7"

from .agent import Agent
from .context import Context
from .exceptions import (
    ConfigurationError,
    ContextError,
    MaxTurnsError,
    ModelError,
    ResponseParseError,
    StreamError,
    TokenLimitError,
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
    ZipAgentError,
)
from .model import LiteLLMModel, Model, ModelResponse, OpenAIModel, StreamDelta
from .runner import Runner, RunResult
from .stream import StreamEvent, StreamEventType
from .tool import Tool, function_tool

# MCP 工具相关导入（可选）
try:
    from .mcp_tool import MCPTool, MCPToolGroup

    _MCP_AVAILABLE = True
except ImportError:
    _MCP_AVAILABLE = False
    MCPTool = None
    MCPToolGroup = None

__version__ = "0.1.0"

__all__ = [
    # 核心类
    "Agent",
    "Context",
    "Model",
    "Runner",
    "Tool",
    # 模型相关
    "LiteLLMModel",
    "ModelResponse",
    "OpenAIModel",
    "StreamDelta",
    # 运行结果
    "RunResult",
    # 流式处理
    "StreamEvent",
    "StreamEventType",
    # 工具装饰器
    "function_tool",
    # MCP 工具（可选）
    *(["MCPTool", "MCPToolGroup"] if _MCP_AVAILABLE else []),
    # 异常类
    "ZipAgentError",
    "ModelError",
    "ToolError",
    "ToolNotFoundError",
    "ToolExecutionError",
    "ContextError",
    "TokenLimitError",
    "MaxTurnsError",
    "ResponseParseError",
    "ConfigurationError",
    "StreamError",
]
