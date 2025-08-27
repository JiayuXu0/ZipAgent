"""测试异常系统"""

from zipagent.exceptions import (
    ConfigurationError,
    ContextError,
    MaxTurnsError,
    ModelError,
    ResponseParseError,
    StreamError,
    TokenLimitError,
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
    ZipAgentError,
    create_error_with_context,
)


class TestZipAgentError:
    """测试基础异常类"""

    def test_basic_error(self):
        """测试基础异常创建"""
        error = ZipAgentError("测试错误")
        assert str(error) == "测试错误"
        assert error.message == "测试错误"
        assert error.details == {}
        assert error.original_error is None

    def test_error_with_details(self):
        """测试带详情的异常"""
        details = {"key": "value", "count": 42}
        error = ZipAgentError("测试错误", details=details)
        assert error.details == details

    def test_error_with_original(self):
        """测试带原始异常的错误"""
        original = ValueError("原始错误")
        error = ZipAgentError("包装错误", original_error=original)
        assert error.original_error == original
        assert "原因: 原始错误" in str(error)


class TestModelError:
    """测试模型错误"""

    def test_model_error(self):
        """测试模型错误创建"""
        error = ModelError(
            "API调用失败", model_name="gpt-3.5-turbo", status_code=429
        )
        assert error.message == "API调用失败"
        assert error.details["model_name"] == "gpt-3.5-turbo"
        assert error.details["status_code"] == 429

    def test_model_error_minimal(self):
        """测试最小模型错误"""
        error = ModelError("简单错误")
        assert error.details["model_name"] is None
        assert error.details["status_code"] is None


class TestToolError:
    """测试工具错误"""

    def test_tool_error(self):
        """测试工具错误创建"""
        error = ToolError(
            "工具执行失败", tool_name="calculator", arguments={"a": 1, "b": 2}
        )
        assert error.message == "工具执行失败"
        assert error.details["tool_name"] == "calculator"
        assert error.details["arguments"] == {"a": 1, "b": 2}

    def test_tool_not_found(self):
        """测试工具未找到错误"""
        error = ToolNotFoundError("my_tool")
        assert "找不到工具: my_tool" in str(error)
        assert error.details["tool_name"] == "my_tool"

    def test_tool_execution_error(self):
        """测试工具执行错误"""
        original = RuntimeError("执行失败")
        error = ToolExecutionError(
            tool_name="api_call",
            arguments={"url": "http://example.com"},
            error=original,
        )
        assert "工具 'api_call' 执行失败" in str(error)
        assert error.details["tool_name"] == "api_call"
        assert error.details["arguments"]["url"] == "http://example.com"
        assert error.original_error == original


class TestContextError:
    """测试上下文错误"""

    def test_context_error(self):
        """测试上下文错误"""
        error = ContextError("上下文无效")
        assert isinstance(error, ZipAgentError)
        assert error.message == "上下文无效"

    def test_token_limit_error(self):
        """测试Token限制错误"""
        error = TokenLimitError(5000, 4000)
        assert "5000 > 4000" in str(error)
        assert error.details["current_tokens"] == 5000
        assert error.details["max_tokens"] == 4000

    def test_token_limit_custom_message(self):
        """测试自定义消息的Token限制错误"""
        error = TokenLimitError(5000, 4000, "自定义错误消息")
        assert str(error) == "自定义错误消息"
        assert error.details["current_tokens"] == 5000


class TestMaxTurnsError:
    """测试最大轮次错误"""

    def test_max_turns_error(self):
        """测试最大轮次错误"""
        error = MaxTurnsError(10)
        assert "达到最大执行轮次 (10)" in str(error)
        assert "可能存在无限循环" in str(error)
        assert error.details["max_turns"] == 10


class TestResponseParseError:
    """测试响应解析错误"""

    def test_response_parse_error(self):
        """测试响应解析错误"""
        raw_response = {"data": "x" * 1000}  # 长响应
        error = ResponseParseError("解析失败", raw_response=raw_response)
        assert error.message == "解析失败"
        # 验证响应被截断到500字符
        assert len(error.details["raw_response"]) <= 500

    def test_response_parse_no_raw(self):
        """测试没有原始响应的解析错误"""
        error = ResponseParseError("解析失败")
        assert error.details["raw_response"] == "None"


class TestConfigurationError:
    """测试配置错误"""

    def test_configuration_error(self):
        """测试配置错误"""
        error = ConfigurationError("配置无效", config_key="api_key")
        assert error.message == "配置无效"
        assert error.details["config_key"] == "api_key"

    def test_configuration_error_no_key(self):
        """测试没有键的配置错误"""
        error = ConfigurationError("配置错误")
        assert error.details == {}


class TestStreamError:
    """测试流式错误"""

    def test_stream_error(self):
        """测试流式错误"""
        error = StreamError("流式处理失败")
        assert isinstance(error, ZipAgentError)
        assert error.message == "流式处理失败"


class TestErrorWithContext:
    """测试带上下文的错误创建"""

    def test_create_error_with_context(self):
        """测试创建带上下文的错误"""
        error = create_error_with_context(
            ModelError,
            "测试错误",
            agent_name="TestAgent",
            user_input="这是一个很长的用户输入" * 20,
        )

        assert isinstance(error, ModelError)
        assert error.details["agent_name"] == "TestAgent"
        # 验证用户输入被截断到100字符
        assert len(error.details["user_input"]) == 100
        # ModelError 没有传入 model_name 参数，所以应该为 None
        assert error.details["model_name"] is None

    def test_create_error_minimal(self):
        """测试最小上下文错误"""
        error = create_error_with_context(ZipAgentError, "简单错误")
        assert error.message == "简单错误"
        assert "agent_name" not in error.details
        assert "user_input" not in error.details
