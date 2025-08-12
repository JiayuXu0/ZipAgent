"""Simple Agent Framework - 简化的Agent框架实现"""

from .agent import Agent
from .context import Context
from .exceptions import (
    ConfigurationError,
    ContextError,
    LiteAgentError,
    MaxTurnsError,
    ModelError,
    ResponseParseError,
    StreamError,
    TokenLimitError,
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
)
from .model import LiteLLMModel, Model, ModelResponse, OpenAIModel, StreamDelta
from .runner import Runner, RunResult
from .stream import StreamEvent, StreamEventType
from .tool import Tool, function_tool

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
    # 异常类
    "LiteAgentError",
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
