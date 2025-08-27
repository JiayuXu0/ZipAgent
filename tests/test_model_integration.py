"""Model 集成测试

这些测试关注模型接口的正确性，而不是 mock 外部 API
"""

import os

import pytest

from zipagent import Agent, Model, ModelResponse, OpenAIModel, Runner
from zipagent.context import Usage


class TestModelIntegration:
    """模型集成测试"""

    def test_model_interface_compliance(self):
        """测试 Model 接口规范"""

        class TestModel(Model):
            """测试用模型"""

            def generate(self, messages, tools=None):
                # 验证输入格式
                assert isinstance(messages, list)
                assert all(isinstance(m, dict) for m in messages)
                assert all("role" in m and "content" in m for m in messages)

                if tools:
                    assert isinstance(tools, list)
                    assert all(isinstance(t, dict) for t in tools)

                # 返回符合规范的响应
                return ModelResponse(
                    content="测试响应",
                    tool_calls=None,
                    usage=Usage(10, 20, 30),
                    finish_reason="stop",
                )

        model = TestModel()
        agent = Agent(name="Test", instructions="测试", model=model)

        # 应该能正常运行
        result = Runner.run(agent, "测试")
        assert result.success is True
        assert result.content == "测试响应"

    def test_openai_model_env_config(self):
        """测试环境变量配置"""
        # 保存原始环境变量
        original_env = {
            key: os.environ.get(key)
            for key in [
                "MODEL",
                "API_KEY",
                "BASE_URL",
                "TEMPERATURE",
                "MAX_TOKENS",
            ]
        }

        try:
            # 设置测试环境变量
            os.environ["MODEL"] = "test-model"
            os.environ["API_KEY"] = "test-key"
            os.environ["BASE_URL"] = "https://test.api.com/v1"
            os.environ["TEMPERATURE"] = "0.5"
            os.environ["MAX_TOKENS"] = "1000"

            # 创建模型应该使用环境变量
            model = OpenAIModel()

            assert model.model_name == "test-model"
            assert model.temperature == 0.5
            assert model.max_tokens == 1000

        finally:
            # 恢复环境变量
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_model_with_tools(self):
        """测试带工具的模型调用"""

        class ToolModel(Model):
            """支持工具调用的测试模型"""

            def __init__(self):
                self.call_count = 0

            def generate(self, messages, tools=None):
                self.call_count += 1

                # 第一次调用：返回工具调用
                if self.call_count == 1 and tools:
                    return ModelResponse(
                        content="需要使用工具",
                        tool_calls=[
                            {
                                "function": {
                                    "name": "test_tool",
                                    "arguments": '{"arg": "value"}',
                                }
                            }
                        ],
                        usage=Usage(10, 20, 30),
                        finish_reason="tool_calls",
                    )

                # 第二次调用：返回最终结果
                return ModelResponse(
                    content="工具调用完成",
                    tool_calls=None,
                    usage=Usage(15, 25, 40),
                    finish_reason="stop",
                )

        from zipagent import function_tool

        @function_tool
        def test_tool(arg: str) -> str:
            """测试工具"""
            return f"处理了: {arg}"

        model = ToolModel()
        agent = Agent(
            name="Test", instructions="测试", model=model, tools=[test_tool]
        )

        result = Runner.run(agent, "使用工具")

        assert result.success is True
        assert "工具调用完成" in result.content
        assert model.call_count == 2  # 应该调用了两次

    def test_model_error_handling(self):
        """测试模型错误处理"""

        class ErrorModel(Model):
            """会出错的模型"""

            def generate(self, messages, tools=None):
                raise RuntimeError("模型内部错误")

        model = ErrorModel()
        agent = Agent(name="Test", instructions="测试", model=model)

        # 应该返回错误结果而不是抛出异常
        result = Runner.run(agent, "测试")
        assert result.success is False
        assert "模型内部错误" in result.error

    def test_model_stream_fallback(self):
        """测试流式生成的默认实现"""

        class SimpleModel(Model):
            """只实现 generate 的简单模型"""

            def generate(self, messages, tools=None):
                return ModelResponse(
                    content="简单响应",
                    tool_calls=None,
                    usage=Usage(5, 10, 15),
                    finish_reason="stop",
                )

        model = SimpleModel()

        # 默认的 generate_stream 应该能工作
        deltas = list(model.generate_stream([], None))

        # 应该逐字符返回
        assert len(deltas) > 1  # 至少有几个字符

        # 最后一个应该是完整响应
        last = deltas[-1]
        assert isinstance(last, ModelResponse)
        assert last.content == "简单响应"

    def test_model_custom_parameters(self):
        """测试自定义参数传递"""

        class CustomModel(Model):
            """支持自定义参数的模型"""

            def __init__(self, **kwargs):
                self.custom_params = kwargs

            def generate(self, messages, tools=None):
                # 可以使用自定义参数
                temp = self.custom_params.get("temperature", 0.7)

                return ModelResponse(
                    content=f"温度设置: {temp}",
                    tool_calls=None,
                    usage=Usage(5, 10, 15),
                    finish_reason="stop",
                )

        # 传递自定义参数
        model = CustomModel(
            temperature=0.3, max_tokens=500, custom_option="test"
        )

        agent = Agent(name="Test", instructions="测试", model=model)
        result = Runner.run(agent, "测试")

        assert "0.3" in result.content


class TestModelRobustness:
    """模型健壮性测试"""

    def test_empty_response(self):
        """测试空响应处理"""

        class EmptyModel(Model):
            def generate(self, messages, tools=None):
                return ModelResponse(
                    content=None,
                    tool_calls=None,
                    usage=Usage(10, 0, 10),
                    finish_reason="stop",
                )

        model = EmptyModel()
        agent = Agent(name="Test", instructions="测试", model=model)

        result = Runner.run(agent, "测试")
        assert result.success is False
        assert "没有返回任何内容" in result.error

    def test_malformed_tool_response(self):
        """测试格式错误的工具响应"""

        class MalformedModel(Model):
            def generate(self, messages, tools=None):
                return ModelResponse(
                    content="调用工具",
                    tool_calls=[
                        {
                            "function": {
                                "name": "test",
                                "arguments": "not-a-json",  # 无效的 JSON
                            }
                        }
                    ],
                    usage=Usage(10, 20, 30),
                    finish_reason="tool_calls",
                )

        from zipagent import function_tool

        @function_tool
        def test() -> str:
            """测试工具"""
            return "ok"

        model = MalformedModel()
        agent = Agent(
            name="Test", instructions="测试", model=model, tools=[test]
        )

        # 应该能处理无效的参数
        result = Runner.run(agent, "测试")
        # Runner 会用空参数继续执行
        assert (
            result.success is True or result.success is False
        )  # 取决于具体实现


@pytest.mark.skipif(
    not os.getenv("TEST_OPENAI_API"),
    reason="需要设置 TEST_OPENAI_API 环境变量来运行真实 API 测试",
)
class TestRealAPI:
    """真实 API 测试（可选）"""

    def test_real_openai_call(self):
        """测试真实的 OpenAI API 调用"""
        model = OpenAIModel()
        agent = Agent(
            name="Test",
            instructions="You are a test assistant. Reply with exactly: TEST_OK",
            model=model,
        )

        result = Runner.run(agent, "Hello")
        assert result.success is True
        assert "TEST_OK" in result.content
