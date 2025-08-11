"""Agent - 代理核心模块"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

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

    tools: List[Tool] = field(default_factory=list)
    """可用工具列表"""

    thinking_tool_mode: bool = False
    """是否启用思考模式的工具调用格式，要求在调用工具前先输出 <thinking> 标签"""

    def __post_init__(self) -> None:
        """初始化后处理"""
        # 如果没有指定模型，使用默认的OpenAI模型
        if self.model is None:
            self.model = OpenAIModel()

    def get_system_message(self) -> Dict[str, str]:
        """获取系统消息"""
        system_content = self.instructions

        # 如果有工具，添加工具使用说明
        if self.tools:
            if self.thinking_tool_mode:
                # thinking模式下提供详细的工具信息
                system_content += "\n\n你可以使用以下工具："
                for tool in self.tools:
                    system_content += f"\n- {tool.name}: {tool.description}"
                    # 添加参数信息
                    if hasattr(tool, 'schema') and 'parameters' in tool.schema.get('function', {}):
                        params = tool.schema['function']['parameters'].get('properties', {})
                        if params:
                            param_info = []
                            for param_name, param_data in params.items():
                                param_desc = param_data.get('description', param_name)
                                param_info.append(f"{param_name}({param_desc})")
                            system_content += f" 参数: {', '.join(param_info)}"
            else:
                # 普通模式下只显示工具名称
                tool_names = [tool.name for tool in self.tools]
                system_content += (
                    f"\n\n你可以使用以下工具: {', '.join(tool_names)}"
                )

            if self.thinking_tool_mode:
                # 严格的思考模式工具调用格式要求
                system_content += """

**严格要求：调用工具时必须严格按此格式，无例外！**

强制格式（违反将导致错误）：
1. 调用工具前必须先写 <thinking>
2. thinking后必须写 <tool_call>  
3. 绝对不允许直接调用工具

正确格式（必须完全遵守）：
<thinking>
我需要分析这个问题：[详细说明]
我选择使用某工具的原因：[详细说明]  
我的执行步骤：[详细说明]
</thinking>

<tool_call>
<name>具体工具名</name>
<args>
<参数名>参数值</参数名>
</args>
</tool_call>

重要：如果需要调用多个工具，必须连续输出多个<tool_call>块：
<tool_call>
<name>第一个工具</name>
<args><参数>值</参数></args>
</tool_call>

<tool_call>
<name>第二个工具</name>
<args><参数>值</参数></args>
</tool_call>

绝对强制示例：
<thinking>
用户要计算 8*6，这是乘法运算。
我必须用计算器工具确保准确。
步骤：解析表达式，调用calculate工具。
</thinking>

<tool_call>
<name>calculate</name>
<args>
<expression>8*6</expression>
</args>
</tool_call>

警告：不按此格式会导致执行失败！必须包含thinking！"""
            else:
                system_content += "\n当需要使用工具时，请调用相应的函数。"

        return {"role": "system", "content": system_content}

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
