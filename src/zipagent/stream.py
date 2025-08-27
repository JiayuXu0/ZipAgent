"""Stream - 流式输出事件模块"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class StreamEventType(Enum):
    """流式事件类型"""

    QUESTION = "question"  # 用户问题
    THINKING = "thinking"  # AI 思考过程
    THINKING_DELTA = "thinking_delta"  # AI 思考增量内容
    TOOL_CALL = "tool_call"  # 工具调用
    TOOL_RESULT = "tool_result"  # 工具结果
    ANSWER = "answer"  # 最终回答
    ANSWER_DELTA = "answer_delta"  # 回答增量内容
    ERROR = "error"  # 错误信息


@dataclass
class StreamEvent:
    """流式事件数据类"""

    type: StreamEventType
    content: str | None = None
    tool_name: str | None = None
    tool_args: dict[str, Any] | None = None
    tool_result: str | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        """确保事件类型是 StreamEventType 枚举"""
        if isinstance(self.type, str):
            self.type = StreamEventType(self.type)

    @classmethod
    def question(cls, content: str) -> "StreamEvent":
        """创建问题事件"""
        return cls(type=StreamEventType.QUESTION, content=content)

    @classmethod
    def thinking(cls, content: str) -> "StreamEvent":
        """创建思考事件"""
        return cls(type=StreamEventType.THINKING, content=content)

    @classmethod
    def thinking_delta(cls, content: str) -> "StreamEvent":
        """创建思考增量事件"""
        return cls(type=StreamEventType.THINKING_DELTA, content=content)

    @classmethod
    def tool_call(
        cls, tool_name: str, tool_args: dict[str, Any]
    ) -> "StreamEvent":
        """创建工具调用事件"""
        return cls(
            type=StreamEventType.TOOL_CALL,
            tool_name=tool_name,
            tool_args=tool_args,
        )

    @classmethod
    def create_tool_result(cls, tool_name: str, result: str) -> "StreamEvent":
        """创建工具结果事件"""
        return cls(
            type=StreamEventType.TOOL_RESULT,
            tool_name=tool_name,
            tool_result=result,
        )

    @classmethod
    def answer(cls, content: str) -> "StreamEvent":
        """创建回答事件"""
        return cls(type=StreamEventType.ANSWER, content=content)

    @classmethod
    def answer_delta(cls, content: str) -> "StreamEvent":
        """创建回答增量事件"""
        return cls(type=StreamEventType.ANSWER_DELTA, content=content)

    @classmethod
    def create_error(cls, error: str) -> "StreamEvent":
        """创建错误事件"""
        return cls(type=StreamEventType.ERROR, error=error)

    def __str__(self) -> str:
        """字符串表示"""
        if self.type == StreamEventType.QUESTION:
            return f"问题: {self.content}"
        elif self.type == StreamEventType.THINKING:
            return f"思考: {self.content}"
        elif self.type == StreamEventType.THINKING_DELTA:
            return f"思考增量: {self.content}"
        elif self.type == StreamEventType.TOOL_CALL:
            return f"工具调用: {self.tool_name}({self.tool_args})"
        elif self.type == StreamEventType.TOOL_RESULT:
            return f"工具结果: {self.tool_result}"
        elif self.type == StreamEventType.ANSWER:
            return f"回答: {self.content}"
        elif self.type == StreamEventType.ANSWER_DELTA:
            return f"回答增量: {self.content}"
        elif self.type == StreamEventType.ERROR:
            return f"错误: {self.error}"
        else:
            return f"{self.type.value}: {self.content or ''}"
