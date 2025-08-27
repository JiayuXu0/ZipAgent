"""Agent - 代理核心模块"""

import os
from dataclasses import dataclass, field
from typing import Any, Union

from .model import Model, OpenAIModel
from .tool import Tool


@dataclass
class Agent:
    """智能代理类"""

    name: str
    """代理名称"""

    instructions: str
    """系统指令"""

    model: Model | None = None
    """使用的LLM模型"""

    tools: list[Union[Tool, "MCPToolGroup"]] = field(default_factory=list)
    """可用工具列表，支持 Tool 和 MCPToolGroup"""

    use_system_prompt: bool = True
    """是否启用默认系统提示"""

    system_prompt_file: str | None = "system.md"
    """系统提示文件名，默认为 system.md（在 liteagent 包目录下）"""

    def __post_init__(self) -> None:
        """初始化后处理"""
        # 如果没有指定模型，使用默认的OpenAI模型
        if self.model is None:
            self.model = OpenAIModel()

        # 展开 MCPToolGroup 为实际的工具列表
        self._expand_tool_groups()

    def get_system_message(self) -> dict[str, str]:
        """获取系统消息"""
        system_content = self.instructions

        # 如果启用默认系统提示，尝试读取系统提示文件
        if self.use_system_prompt and self.system_prompt_file:
            default_prompt = self._load_system_prompt()
            if default_prompt:
                system_content = default_prompt + "\n\n" + system_content

        # 如果有工具，添加工具使用说明
        if self.tools:
            tool_names = [tool.name for tool in self._get_all_tools()]
            system_content += (
                f"\n\n你可以使用以下工具: {', '.join(tool_names)}"
            )
            system_content += "\n当需要使用工具时，请调用相应的函数。"

        return {"role": "system", "content": system_content}

    def _load_system_prompt(self) -> str | None:
        """加载系统提示文件"""
        if not self.system_prompt_file:
            return None

        try:
            # 如果是绝对路径，直接使用
            if os.path.isabs(self.system_prompt_file):
                file_path = self.system_prompt_file
            else:
                # 相对路径：先尝试 zipagent 包目录，再尝试当前工作目录
                package_dir = os.path.dirname(__file__)
                package_file_path = os.path.join(
                    package_dir, self.system_prompt_file
                )

                if os.path.exists(package_file_path):
                    file_path = package_file_path
                else:
                    # 回退到当前工作目录
                    file_path = os.path.join(
                        os.getcwd(), self.system_prompt_file
                    )

            # 检查文件是否存在
            if not os.path.exists(file_path):
                return None

            # 读取文件内容
            with open(file_path, encoding="utf-8") as f:
                content = f.read().strip()

            return content if content else None

        except Exception:
            # 读取失败时静默忽略
            return None

    def get_tools_schema(self) -> list[dict[str, Any]]:
        """获取工具的schema定义"""
        return [tool.to_dict() for tool in self._get_all_tools()]

    def find_tool(self, name: str) -> Tool | None:
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

    def _get_all_tools(self) -> list[Tool]:
        """获取所有工具的扁平化列表"""
        all_tools = []
        for item in self.tools:
            if hasattr(item, "__iter__") and not isinstance(
                item, (str, bytes)
            ):
                # 这是一个工具组（MCPToolGroup）
                all_tools.extend(item)
            else:
                # 这是一个普通工具
                all_tools.append(item)
        return all_tools

    def _remove_tool_from_original_list(self, target_tool: Tool) -> None:
        """从原始工具列表中移除指定工具"""
        for i, item in enumerate(self.tools):
            if hasattr(item, "__iter__") and not isinstance(
                item, (str, bytes)
            ):
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
