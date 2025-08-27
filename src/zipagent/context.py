"""Context - 上下文管理模块"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Usage:
    """Token使用统计"""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    def add(self, other: "Usage") -> None:
        """累加使用量"""
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.total_tokens += other.total_tokens


@dataclass
class Context:
    """Agent运行上下文，管理对话历史、状态和统计信息"""

    messages: list[dict[str, Any]] = field(default_factory=list)
    """对话消息历史"""

    usage: Usage = field(default_factory=Usage)
    """Token使用统计"""

    data: dict[str, Any] = field(default_factory=dict)
    """自定义数据存储"""

    # === 新增元数据字段 ===
    context_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    """上下文唯一标识"""

    created_at: datetime = field(default_factory=datetime.now)
    """创建时间"""

    last_agent: str | None = None
    """最后使用的 Agent 名称"""

    turn_count: int = 0
    """对话轮次计数"""

    def add_message(self, role: str, content: str, **kwargs: Any) -> None:
        """添加消息到对话历史"""
        message = {"role": role, "content": content}
        if kwargs:
            message.update(kwargs)
        self.messages.append(message)

    def add_tool_call(
        self, tool_name: str, arguments: dict[str, Any], result: Any
    ) -> None:
        """添加工具调用记录"""
        # 添加助手的工具调用消息
        self.messages.append(
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": f"call_{len(self.messages)}",
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": str(arguments),
                        },
                    }
                ],
            }
        )

        # 添加工具执行结果
        self.messages.append(
            {
                "role": "tool",
                "content": str(result),
                "tool_call_id": f"call_{len(self.messages) - 1}",
            }
        )

    def get_messages_for_api(self) -> list[dict[str, Any]]:
        """获取适合API调用的消息格式"""
        return self.messages.copy()

    def set_data(self, key: str, value: Any) -> None:
        """设置上下文数据"""
        self.data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        """获取上下文数据"""
        return self.data.get(key, default)

    def clear_messages(self) -> None:
        """清空对话历史"""
        self.messages.clear()
        self.turn_count = 0

    def get_summary(self) -> dict[str, Any]:
        """获取上下文摘要信息"""
        return {
            "context_id": self.context_id,
            "created_at": self.created_at.isoformat(),
            "last_agent": self.last_agent,
            "turn_count": self.turn_count,
            "message_count": len(self.messages),
            "total_tokens": self.usage.total_tokens,
        }

    def clone(self) -> "Context":
        """克隆上下文（用于传递给其他 Agent）"""
        import copy

        new_context = Context()
        new_context.messages = copy.deepcopy(self.messages)
        new_context.usage = Usage(
            self.usage.input_tokens,
            self.usage.output_tokens,
            self.usage.total_tokens,
        )
        new_context.data = copy.deepcopy(self.data)
        # 保持相同的 context_id 表示是同一个对话
        new_context.context_id = self.context_id
        new_context.created_at = self.created_at
        new_context.last_agent = self.last_agent
        new_context.turn_count = self.turn_count
        return new_context

    def __str__(self) -> str:
        return f"Context(id={self.context_id[:8]}..., messages={len(self.messages)}, turns={self.turn_count}, usage={self.usage})"
