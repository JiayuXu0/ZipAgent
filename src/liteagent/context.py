"""Context - 上下文管理模块"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Usage:
    """Token使用统计"""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    def add(self, other: 'Usage') -> None:
        """累加使用量"""
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.total_tokens += other.total_tokens


@dataclass
class Context:
    """Agent运行上下文，管理对话历史、状态和统计信息"""

    messages: List[Dict[str, Any]] = field(default_factory=list)
    """对话消息历史"""

    usage: Usage = field(default_factory=Usage)
    """Token使用统计"""

    data: Dict[str, Any] = field(default_factory=dict)
    """自定义数据存储"""

    def add_message(self, role: str, content: str, **kwargs: Any) -> None:
        """添加消息到对话历史"""
        message = {"role": role, "content": content}
        if kwargs:
            message.update(kwargs)
        self.messages.append(message)

    def add_tool_call(self, tool_name: str, arguments: Dict[str, Any], result: Any) -> None:
        """添加工具调用记录"""
        # 添加助手的工具调用消息
        self.messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": f"call_{len(self.messages)}",
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": str(arguments)
                }
            }]
        })

        # 添加工具执行结果
        self.messages.append({
            "role": "tool",
            "content": str(result),
            "tool_call_id": f"call_{len(self.messages) - 1}"
        })

    def get_messages_for_api(self) -> List[Dict[str, Any]]:
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

    def __str__(self) -> str:
        return f"Context(messages={len(self.messages)}, usage={self.usage})"
