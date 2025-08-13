"""LiteAgent 异常系统

提供结构化的异常类型，帮助用户准确识别和处理错误。
"""

from typing import Any, Dict, Optional


class LiteAgentError(Exception):
    """LiteAgent 基础异常类"""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.original_error = original_error

    def __str__(self) -> str:
        if self.original_error:
            return f"{self.message} (原因: {self.original_error})"
        return self.message


class ModelError(LiteAgentError):
    """模型调用相关错误"""

    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        details = {"model_name": model_name, "status_code": status_code}
        super().__init__(message, details, **kwargs)


class ToolError(LiteAgentError):
    """工具执行相关错误"""

    def __init__(
        self,
        message: str,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        details = {"tool_name": tool_name, "arguments": arguments}
        super().__init__(message, details, **kwargs)


class ToolNotFoundError(ToolError):
    """找不到指定的工具"""

    def __init__(self, tool_name: str):
        super().__init__(
            f"找不到工具: {tool_name}",
            tool_name=tool_name
        )


class ToolExecutionError(ToolError):
    """工具执行失败"""

    def __init__(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        error: Exception
    ):
        super().__init__(
            f"工具 '{tool_name}' 执行失败",
            tool_name=tool_name,
            arguments=arguments,
            original_error=error
        )


class ContextError(LiteAgentError):
    """上下文管理相关错误"""
    pass


class TokenLimitError(ContextError):
    """Token 限制错误"""

    def __init__(
        self,
        current_tokens: int,
        max_tokens: int,
        message: Optional[str] = None
    ):
        msg = message or f"Token 数量超过限制: {current_tokens} > {max_tokens}"
        details = {"current_tokens": current_tokens, "max_tokens": max_tokens}
        super().__init__(msg, details)


class MaxTurnsError(LiteAgentError):
    """达到最大执行轮次"""

    def __init__(self, max_turns: int):
        super().__init__(
            f"达到最大执行轮次 ({max_turns})，可能存在无限循环",
            details={"max_turns": max_turns}
        )


class ResponseParseError(LiteAgentError):
    """响应解析错误"""

    def __init__(
        self,
        message: str,
        raw_response: Any = None,
        **kwargs
    ):
        details = {"raw_response": str(raw_response)[:500]}  # 限制长度
        super().__init__(message, details, **kwargs)


class ConfigurationError(LiteAgentError):
    """配置错误"""

    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {"config_key": config_key} if config_key else {}
        super().__init__(message, details)


class StreamError(LiteAgentError):
    """流式处理相关错误"""
    pass


# 工具函数：用于创建带上下文的异常
def create_error_with_context(
    error_class: type,
    message: str,
    agent_name: Optional[str] = None,
    user_input: Optional[str] = None,
    **kwargs
) -> LiteAgentError:
    """创建带有执行上下文的异常"""
    # 创建错误实例
    error = error_class(message, **kwargs)
    
    # 添加上下文信息到 details
    if agent_name:
        error.details["agent_name"] = agent_name
    if user_input:
        error.details["user_input"] = user_input[:100]  # 限制长度
    
    return error
