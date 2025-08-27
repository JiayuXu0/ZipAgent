"""测试 Model 模块"""

import os
from unittest.mock import MagicMock, patch

import pytest

from zipagent.model import (
    Model,
    ModelResponse,
    OpenAIModel,
    StreamDelta,
    Usage,
)


class TestUsage:
    """测试 Usage 类"""

    def test_usage_initialization(self):
        """测试 Usage 初始化"""
        usage = Usage(input_tokens=10, output_tokens=20, total_tokens=30)
        assert usage.input_tokens == 10
        assert usage.output_tokens == 20
        assert usage.total_tokens == 30

    def test_usage_add(self):
        """测试 Usage 累加"""
        usage1 = Usage(10, 20, 30)
        usage2 = Usage(5, 15, 20)

        usage1.add(usage2)

        assert usage1.input_tokens == 15
        assert usage1.output_tokens == 35
        assert usage1.total_tokens == 50

    def test_usage_add_none(self):
        """测试累加 None"""
        usage = Usage(10, 20, 30)
        # Usage.add 需要另一个 Usage 对象，不能是 None
        usage2 = Usage(0, 0, 0)
        usage.add(usage2)

        assert usage.input_tokens == 10
        assert usage.output_tokens == 20
        assert usage.total_tokens == 30


class TestStreamDelta:
    """测试 StreamDelta 类"""

    def test_stream_delta_initialization(self):
        """测试 StreamDelta 初始化"""
        delta = StreamDelta(
            content="测试内容",
            tool_calls=[{"function": {"name": "test"}}],
            finish_reason="stop",
        )

        assert delta.content == "测试内容"
        assert delta.tool_calls[0]["function"]["name"] == "test"
        assert delta.finish_reason == "stop"

    def test_stream_delta_defaults(self):
        """测试默认值"""
        delta = StreamDelta()

        assert delta.content is None
        assert delta.tool_calls is None
        assert delta.finish_reason is None


class TestModelResponse:
    """测试 ModelResponse 类"""

    def test_model_response_initialization(self):
        """测试 ModelResponse 初始化"""
        usage = Usage(10, 20, 30)
        response = ModelResponse(
            content="测试回复",
            tool_calls=[{"function": {"name": "test"}}],
            usage=usage,
            finish_reason="stop",
        )

        assert response.content == "测试回复"
        assert response.tool_calls[0]["function"]["name"] == "test"
        assert response.usage == usage
        assert response.finish_reason == "stop"


class TestModel:
    """测试 Model 抽象类"""

    def test_model_abstract_methods(self):
        """测试抽象方法"""
        # Model 是抽象类，不能直接实例化
        with pytest.raises(TypeError):
            Model()

    def test_model_generate_stream_default(self):
        """测试默认的流式生成实现"""

        class ConcreteModel(Model):
            def generate(self, messages, tools=None):
                return ModelResponse(
                    content="测试内容",
                    tool_calls=None,
                    usage=Usage(10, 20, 30),
                    finish_reason="stop",
                )

        model = ConcreteModel()

        # 测试默认的 generate_stream 实现
        deltas = list(model.generate_stream([], None))

        # 应该逐字符返回
        assert len(deltas) > 0
        # 最后一个应该是完整响应
        assert isinstance(deltas[-1], ModelResponse)
        assert deltas[-1].content == "测试内容"


class TestOpenAIModel:
    """测试 OpenAIModel 类"""

    @patch("openai.OpenAI")
    @patch.dict("os.environ", {}, clear=False)  # 不清除所有环境变量
    def test_openai_model_initialization(self, mock_openai):
        """测试 OpenAIModel 初始化"""
        # 确保测试环境变量不影响结果
        for key in [
            "MODEL",
            "API_KEY",
            "BASE_URL",
            "TEMPERATURE",
            "MAX_TOKENS",
        ]:
            os.environ.pop(key, None)

        model = OpenAIModel(
            model_name="gpt-3.5-turbo",
            api_key="test_key",
            base_url="https://api.openai.com/v1",
        )

        assert model.model_name == "gpt-3.5-turbo"
        assert model.temperature == 0.7
        assert model.max_tokens is None
        mock_openai.assert_called_once()

    @patch("openai.OpenAI")
    def test_openai_model_from_env(self, mock_openai):
        """测试从环境变量初始化"""
        with patch.dict(
            "os.environ",
            {
                "MODEL": "gpt-4",
                "API_KEY": "env_key",
                "BASE_URL": "https://custom.api.com/v1",
                "TEMPERATURE": "0.7",
                "MAX_TOKENS": "1000",
            },
        ):
            model = OpenAIModel()

            assert model.model_name == "gpt-4"
            assert model.temperature == 0.7
            assert model.max_tokens == 1000

    @patch("openai.OpenAI")
    def test_openai_model_generate(self, mock_openai_class):
        """测试 generate 方法"""
        # 创建 mock client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # 创建 mock response
        mock_choice = MagicMock()
        mock_choice.message.content = "测试回复"
        mock_choice.message.tool_calls = None
        mock_choice.finish_reason = "stop"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        mock_response.usage.total_tokens = 30

        mock_client.chat.completions.create.return_value = mock_response

        # 测试
        model = OpenAIModel(model_name="gpt-3.5-turbo", api_key="test")
        messages = [{"role": "user", "content": "测试"}]

        response = model.generate(messages)

        assert response.content == "测试回复"
        assert response.tool_calls is None
        assert response.usage.total_tokens == 30
        assert response.finish_reason == "stop"

        # 验证调用参数
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-3.5-turbo"
        assert call_args[1]["messages"] == messages

    @patch("openai.OpenAI")
    def test_openai_model_generate_with_tools(self, mock_openai_class):
        """测试带工具的 generate"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # 创建带工具调用的 mock response
        mock_tool_call = MagicMock()
        mock_tool_call.function.name = "test_tool"
        mock_tool_call.function.arguments = '{"arg": "value"}'

        mock_choice = MagicMock()
        mock_choice.message.content = "需要调用工具"
        mock_choice.message.tool_calls = [mock_tool_call]
        mock_choice.finish_reason = "tool_calls"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        mock_response.usage.total_tokens = 30

        mock_client.chat.completions.create.return_value = mock_response

        # 测试
        model = OpenAIModel(model_name="gpt-3.5-turbo", api_key="test")
        messages = [{"role": "user", "content": "测试"}]
        tools = [{"type": "function", "function": {"name": "test_tool"}}]

        response = model.generate(messages, tools)

        assert response.content == "需要调用工具"
        assert response.tool_calls is not None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["function"]["name"] == "test_tool"
        assert (
            response.tool_calls[0]["function"]["arguments"]
            == '{"arg": "value"}'
        )
        assert response.finish_reason == "tool_calls"

    @patch("openai.OpenAI")
    def test_openai_model_generate_stream(self, mock_openai_class):
        """测试流式生成"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # 创建 mock 流式响应
        mock_chunks = []

        # 第一个 chunk - 内容开始
        chunk1 = MagicMock()
        chunk1.choices = [MagicMock()]
        chunk1.choices[0].delta.content = "测"
        chunk1.choices[0].delta.tool_calls = None
        chunk1.choices[0].finish_reason = None
        chunk1.usage = None
        mock_chunks.append(chunk1)

        # 第二个 chunk - 更多内容
        chunk2 = MagicMock()
        chunk2.choices = [MagicMock()]
        chunk2.choices[0].delta.content = "试"
        chunk2.choices[0].delta.tool_calls = None
        chunk2.choices[0].finish_reason = None
        chunk2.usage = None
        mock_chunks.append(chunk2)

        # 最后一个 chunk - 带 usage
        chunk3 = MagicMock()
        chunk3.choices = [MagicMock()]
        chunk3.choices[0].delta.content = None
        chunk3.choices[0].delta.tool_calls = None
        chunk3.choices[0].finish_reason = "stop"
        chunk3.usage = MagicMock()
        chunk3.usage.input_tokens = 10
        chunk3.usage.output_tokens = 20
        chunk3.usage.total_tokens = 30
        mock_chunks.append(chunk3)

        mock_client.chat.completions.create.return_value = iter(mock_chunks)

        # 测试
        model = OpenAIModel(model_name="gpt-3.5-turbo", api_key="test")
        messages = [{"role": "user", "content": "测试"}]

        deltas = list(model.generate_stream(messages))

        # 验证增量内容
        assert len(deltas) == 3
        assert deltas[0].content == "测"
        assert deltas[1].content == "试"

        # 最后应该是完整响应
        assert isinstance(deltas[-1], ModelResponse)
        assert deltas[-1].content == "测试"
        assert deltas[-1].usage.total_tokens == 30

        # 验证调用参数
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["stream"] is True

    @patch("openai.OpenAI")
    def test_openai_model_error_handling(self, mock_openai_class):
        """测试错误处理"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # 模拟 API 错误
        mock_client.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        model = OpenAIModel(model_name="gpt-3.5-turbo", api_key="test")
        messages = [{"role": "user", "content": "测试"}]

        with pytest.raises(Exception) as exc_info:
            model.generate(messages)

        assert "API Error" in str(exc_info.value)
