"""Agent - 代理核心模块"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from .model import Model, OpenAIModel
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

    tools: List[Union[Tool, "MCPToolGroup"]] = field(default_factory=list)
    """可用工具列表，支持 Tool 和 MCPToolGroup"""

    def __post_init__(self) -> None:
        """初始化后处理"""
        # 如果没有指定模型，使用默认的OpenAI模型
        if self.model is None:
            self.model = OpenAIModel()

        # 展开 MCPToolGroup 为实际的工具列表
        self._expand_tool_groups()

    def get_system_message(self) -> Dict[str, str]:
        """获取系统消息"""
        system_content = self.instructions

        # 如果有工具，添加工具使用说明
        if self.tools:
            tool_names = [tool.name for tool in self._get_all_tools()]
            system_content += (
                f"\n\n你可以使用以下工具: {', '.join(tool_names)}"
            )
            system_content += "\n当需要使用工具时，请调用相应的函数。"

        return {"role": "system", "content": system_content}

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """获取工具的schema定义"""
        return [tool.to_dict() for tool in self._get_all_tools()]

    def find_tool(self, name: str) -> Optional[Tool]:
        """根据名称查找工具"""
        for tool in self._get_all_tools():
            if tool.name == name:
                return tool
        return None

    def add_tool(self, tool: Union[Tool, "MCPToolGroup"]) -> None:
        """添加工具或工具组"""
        self.tools.append(tool)

    def remove_tool(self, name: str) -> bool:
        """移除工具"""
        all_tools = self._get_all_tools()
        for i, tool in enumerate(all_tools):
            if tool.name == name:
                # 找到在原始列表中的位置并移除
                self._remove_tool_from_original_list(tool)
                return True
        return False

    def _expand_tool_groups(self) -> None:
        """展开工具组（内部方法，已废弃，保持向后兼容）"""
        pass

    def _get_all_tools(self) -> List[Tool]:
        """获取所有工具的扁平化列表"""
        all_tools = []
        for item in self.tools:
            if hasattr(item, '__iter__') and not isinstance(item, (str, bytes)):
                # 这是一个工具组（MCPToolGroup）
                all_tools.extend(item)
            else:
                # 这是一个普通工具
                all_tools.append(item)
        return all_tools

    def _remove_tool_from_original_list(self, target_tool: Tool) -> None:
        """从原始工具列表中移除指定工具"""
        for i, item in enumerate(self.tools):
            if hasattr(item, '__iter__') and not isinstance(item, (str, bytes)):
                # 这是一个工具组
                if target_tool in item.tools:
                    item.tools.remove(target_tool)
                    # 如果工具组为空，移除整个工具组
                    if not item.tools:
                        self.tools.pop(i)
                    break
            else:
                # 这是一个普通工具
                if item == target_tool:
                    self.tools.pop(i)
                    break

    def __str__(self) -> str:
        return f"Agent(name={self.name}, tools={len(self._get_all_tools())})"
