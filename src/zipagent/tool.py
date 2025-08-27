"""Tool - 工具系统模块"""

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, get_type_hints


@dataclass
class ToolResult:
    """工具执行结果"""

    name: str
    arguments: dict[str, Any]
    result: Any
    success: bool = True
    error: str | None = None


class Tool:
    """工具基类"""

    def __init__(
        self, name: str, description: str, function: Callable[..., Any]
    ):
        self.name = name
        self.description = description
        self.function = function
        self.schema = self._generate_schema()

    def _generate_schema(self) -> dict[str, Any]:
        """生成工具的JSON Schema"""
        sig = inspect.signature(self.function)
        type_hints = get_type_hints(self.function)

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            param_type = type_hints.get(param_name, str)

            # 简化的类型映射
            if param_type is str:
                prop_type = "string"
            elif param_type is int:
                prop_type = "integer"
            elif param_type is float:
                prop_type = "number"
            elif param_type is bool:
                prop_type = "boolean"
            else:
                prop_type = "string"

            properties[param_name] = {
                "type": prop_type,
                "description": f"Parameter {param_name}",
            }

            # 检查是否为必需参数
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        """执行工具"""
        try:
            result = self.function(**arguments)
            return ToolResult(
                name=self.name,
                arguments=arguments,
                result=result,
                success=True,
            )
        except Exception as e:
            return ToolResult(
                name=self.name,
                arguments=arguments,
                result=None,
                success=False,
                error=str(e),
            )

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式，用于API调用"""
        return self.schema


def function_tool(
    func: Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    description: str | None = None,
) -> Callable[[Callable[..., Any]], Tool] | Tool:
    """
    将Python函数转换为Tool的装饰器

    用法:
    @function_tool
    def my_func(x: int) -> str:
        return str(x)

    或
    @function_tool(name="custom_name", description="Custom description")
    def my_func(x: int) -> str:
        return str(x)
    """

    def decorator(f: Callable[..., Any]) -> Tool:
        tool_name = name or f.__name__
        tool_description = description or f.__doc__ or f"Function {f.__name__}"
        return Tool(tool_name, tool_description, f)

    if func is None:
        # 带参数调用: @function_tool(name="xxx")
        return decorator
    else:
        # 无参数调用: @function_tool
        return decorator(func)
