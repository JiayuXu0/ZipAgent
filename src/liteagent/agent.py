"""Agent - 代理核心模块"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .model import LiteLLMModel, Model
from .tool import Tool


@dataclass
class Agent:
    """智能代理类"""

    name: str
    """代理名称"""

    instructions: str
    """系统指令"""

    model: Optional[Model] = None
    """使用的LLM模型"""

    tools: List[Tool] = field(default_factory=list)
    """可用工具列表"""

    def __post_init__(self) -> None:
        """初始化后处理"""
        # 如果没有指定模型，使用默认的LiteLLM模型
        if self.model is None:
            self.model = LiteLLMModel()

    def get_system_message(self) -> Dict[str, str]:
        """获取系统消息"""
        system_content = self.instructions

        # 如果有工具，添加工具使用说明
        if self.tools:
            tool_names = [tool.name for tool in self.tools]
            system_content += f"\n\n你可以使用以下工具: {', '.join(tool_names)}"
            system_content += "\n当需要使用工具时，请调用相应的函数。"

        return {
            "role": "system",
            "content": system_content
        }

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """获取工具的schema定义"""
        return [tool.to_dict() for tool in self.tools]

    def find_tool(self, name: str) -> Optional[Tool]:
        """根据名称查找工具"""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def add_tool(self, tool: Tool) -> None:
        """添加工具"""
        self.tools.append(tool)

    def remove_tool(self, name: str) -> bool:
        """移除工具"""
        for i, tool in enumerate(self.tools):
            if tool.name == name:
                self.tools.pop(i)
                return True
        return False

    def __str__(self) -> str:
        return f"Agent(name={self.name}, tools={len(self.tools)})"
