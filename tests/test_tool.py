"""Tool 模块测试"""

from zipagent import Tool, function_tool
from zipagent.tool import ToolResult


class TestToolResult:
    """ToolResult 类测试"""

    def test_tool_result_success(self) -> None:
        """测试成功的工具结果"""
        result = ToolResult(
            name="test_tool",
            arguments={"x": 1},
            result="success",
            success=True,
        )

        assert result.name == "test_tool"
        assert result.arguments == {"x": 1}
        assert result.result == "success"
        assert result.success is True
        assert result.error is None

    def test_tool_result_failure(self) -> None:
        """测试失败的工具结果"""
        result = ToolResult(
            name="test_tool",
            arguments={"x": 1},
            result=None,
            success=False,
            error="错误信息",
        )

        assert result.success is False
        assert result.error == "错误信息"


class TestTool:
    """Tool 类测试"""

    def test_tool_initialization(self) -> None:
        """测试 Tool 初始化"""

        def test_func(x: int, y: str = "default") -> str:
            return f"{x}-{y}"

        tool = Tool("test_tool", "测试工具", test_func)

        assert tool.name == "test_tool"
        assert tool.description == "测试工具"
        assert tool.function == test_func
        assert tool.schema is not None

    def test_tool_schema_generation(self) -> None:
        """测试 Tool schema 生成"""

        def test_func(x: int, y: str = "default") -> str:
            return f"{x}-{y}"

        tool = Tool("test_tool", "测试工具", test_func)
        schema = tool.schema

        assert schema["type"] == "function"
        assert schema["function"]["name"] == "test_tool"
        assert schema["function"]["description"] == "测试工具"

        params = schema["function"]["parameters"]
        assert params["type"] == "object"
        assert "x" in params["properties"]
        assert "y" in params["properties"]
        assert params["properties"]["x"]["type"] == "integer"
        assert params["properties"]["y"]["type"] == "string"
        assert params["required"] == ["x"]  # y 有默认值，不是必需的

    def test_tool_execute_success(self) -> None:
        """测试工具执行成功"""

        def test_func(x: int, y: int) -> int:
            return x + y

        tool = Tool("add", "加法", test_func)
        result = tool.execute({"x": 2, "y": 3})

        assert result.success is True
        assert result.result == 5
        assert result.error is None

    def test_tool_execute_failure(self) -> None:
        """测试工具执行失败"""

        def test_func(x: int) -> int:
            raise ValueError("测试错误")

        tool = Tool("error_func", "错误函数", test_func)
        result = tool.execute({"x": 1})

        assert result.success is False
        assert result.result is None
        assert "测试错误" in result.error

    def test_tool_to_dict(self) -> None:
        """测试工具转换为字典"""

        def test_func(x: int) -> int:
            return x * 2

        tool = Tool("double", "翻倍", test_func)
        tool_dict = tool.to_dict()

        assert tool_dict == tool.schema


class TestFunctionTool:
    """function_tool 装饰器测试"""

    def test_function_tool_decorator_no_args(self) -> None:
        """测试无参数的装饰器"""

        @function_tool
        def test_func(x: int) -> int:
            """测试函数"""
            return x * 2

        assert isinstance(test_func, Tool)
        assert test_func.name == "test_func"
        assert test_func.description == "测试函数"

    def test_function_tool_decorator_with_args(self) -> None:
        """测试带参数的装饰器"""

        @function_tool(name="custom_name", description="自定义描述")
        def test_func(x: int) -> int:
            return x * 2

        assert isinstance(test_func, Tool)
        assert test_func.name == "custom_name"
        assert test_func.description == "自定义描述"

    def test_function_tool_decorator_no_docstring(self) -> None:
        """测试没有文档字符串的函数"""

        @function_tool
        def test_func(x: int) -> int:
            return x * 2

        assert test_func.description == "Function test_func"

    def test_function_tool_execution(self) -> None:
        """测试装饰器创建的工具执行"""

        @function_tool
        def multiply(x: int, y: int) -> int:
            """乘法运算"""
            return x * y

        result = multiply.execute({"x": 3, "y": 4})

        assert result.success is True
        assert result.result == 12
