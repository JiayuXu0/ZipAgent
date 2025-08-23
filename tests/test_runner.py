"""测试 Runner 执行引擎"""

from unittest.mock import MagicMock, patch

from zipagent import (
    Agent,
    Context,
    ModelResponse,
    Runner,
    StreamEvent,
    StreamEventType,
    function_tool,
)
from zipagent.model import Usage, StreamDelta


def mock_generate_stream(content, tool_calls=None, usage=None):
    """辅助函数：模拟流式响应"""
    # 先逐字符yield StreamDelta
    if content:
        for char in content:
            yield StreamDelta(content=char)
    
    # 最后yield完整的ModelResponse
    yield ModelResponse(
        content=content,
        tool_calls=tool_calls,
        usage=usage or Usage(),
        finish_reason="stop"
    )


@function_tool
def add(a: int, b: int) -> int:
    """加法运算"""
    return a + b


@function_tool
def failing_tool() -> str:
    """一个会失败的工具"""
    raise ValueError("工具执行失败")


@function_tool
def echo(message: str) -> str:
    """回显消息"""
    return message


class TestRunner:
    """测试 Runner 类"""

    def test_run_simple_conversation(self):
        """测试简单对话"""
        # 创建 mock model
        mock_model = MagicMock()
        mock_model.generate.return_value = ModelResponse(
            content="你好！我是AI助手。",
            tool_calls=None,
            usage=Usage(input_tokens=10, output_tokens=20, total_tokens=30),
            finish_reason="stop",
        )
        # 模拟流式响应
        mock_model.generate_stream.return_value = mock_generate_stream(
            "你好！我是AI助手。",
            usage=Usage(input_tokens=10, output_tokens=20, total_tokens=30)
        )

        agent = Agent(
            name="TestAgent",
            instructions="你是一个友好的助手",
            model=mock_model,
        )

        result = Runner.run(agent, "你好")

        assert result.success is True
        assert result.content == "你好！我是AI助手。"
        assert result.context.usage.total_tokens == 30

        # 验证消息历史
        messages = result.context.messages
        assert len(messages) == 3  # system + user + assistant
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "你好"
        assert messages[2]["role"] == "assistant"
        assert messages[2]["content"] == "你好！我是AI助手。"

    def test_run_with_tool_call(self):
        """测试工具调用"""
        # 创建 mock model
        mock_model = MagicMock()

        # 第一次调用：返回工具调用
        mock_model.generate.side_effect = [
            ModelResponse(
                content="我需要计算这个加法。",
                tool_calls=[
                    {
                        "function": {
                            "name": "add",
                            "arguments": '{"a": 2, "b": 3}',
                        }
                    }
                ],
                usage=Usage(10, 20, 30),
                finish_reason="tool_calls",
            ),
            # 第二次调用：返回最终答案
            ModelResponse(
                content="2 + 3 = 5",
                tool_calls=None,
                usage=Usage(15, 25, 40),
                finish_reason="stop",
            ),
        ]

        agent = Agent(
            name="Calculator",
            instructions="你是一个计算器",
            model=mock_model,
            tools=[add],
        )

        result = Runner.run(agent, "计算 2 + 3")

        assert result.success is True
        assert "5" in result.content
        assert result.context.usage.total_tokens == 70  # 30 + 40

        # 验证工具调用记录
        messages = result.context.messages
        # system + user + assistant(thinking) + tool_call + tool_result + assistant(final)
        assert any(msg.get("role") == "tool" for msg in messages)

    def test_run_with_failing_tool(self):
        """测试工具执行失败"""
        mock_model = MagicMock()
        mock_model.generate.side_effect = [
            ModelResponse(
                content="调用工具",
                tool_calls=[
                    {"function": {"name": "failing_tool", "arguments": "{}"}}
                ],
                usage=Usage(10, 20, 30),
                finish_reason="tool_calls",
            ),
            ModelResponse(
                content="工具执行失败了",
                tool_calls=None,
                usage=Usage(10, 20, 30),
                finish_reason="stop",
            ),
        ]

        agent = Agent(
            name="TestAgent",
            instructions="测试",
            model=mock_model,
            tools=[failing_tool],
        )

        result = Runner.run(agent, "执行工具")

        # 工具失败但整体执行应该继续
        assert result.success is True

        # 验证错误消息被添加到上下文
        messages = result.context.messages
        error_messages = [
            m
            for m in messages
            if m.get("role") == "system" and "执行失败" in m.get("content", "")
        ]
        assert len(error_messages) > 0

    def test_run_with_max_turns(self):
        """测试最大轮次限制"""
        mock_model = MagicMock()
        # 总是返回工具调用，导致无限循环
        mock_model.generate.return_value = ModelResponse(
            content="继续调用",
            tool_calls=[
                {
                    "function": {
                        "name": "echo",
                        "arguments": '{"message": "loop"}',
                    }
                }
            ],
            usage=Usage(10, 20, 30),
            finish_reason="tool_calls",
        )

        agent = Agent(
            name="LoopAgent",
            instructions="测试循环",
            model=mock_model,
            tools=[echo],
        )

        result = Runner.run(agent, "开始", max_turns=3)

        assert result.success is False
        assert "最大执行轮次" in result.error

    def test_run_with_existing_context(self):
        """测试使用现有上下文"""
        mock_model = MagicMock()
        mock_model.generate.return_value = ModelResponse(
            content="继续对话",
            tool_calls=None,
            usage=Usage(10, 20, 30),
            finish_reason="stop",
        )

        # 创建一个有历史的上下文
        context = Context()
        context.add_message("user", "第一个问题")
        context.add_message("assistant", "第一个回答")

        agent = Agent(name="TestAgent", instructions="测试", model=mock_model)

        result = Runner.run(agent, "第二个问题", context=context)

        assert result.success is True
        # 应该包含: 2个历史 + 用户问题 + 助手回答 = 4个消息
        # system 消息不存储在 context 中，只在 API 调用时使用
        assert len(result.context.messages) == 4

    def test_run_with_stream_callback(self):
        """测试流式回调"""
        mock_model = MagicMock()
        mock_model.generate.return_value = ModelResponse(
            content="测试回答",
            tool_calls=None,
            usage=Usage(10, 20, 30),
            finish_reason="stop",
        )

        agent = Agent(name="TestAgent", instructions="测试", model=mock_model)

        # 记录流式事件
        events = []

        def callback(event: StreamEvent):
            events.append(event)

        result = Runner.run(agent, "测试", stream_callback=callback)

        assert result.success is True
        assert len(events) > 0

        # 验证事件类型
        event_types = [e.type for e in events]
        assert StreamEventType.QUESTION in event_types
        assert StreamEventType.ANSWER in event_types

    def test_run_stream(self):
        """测试流式运行"""
        mock_model = MagicMock()
        mock_model.generate.return_value = ModelResponse(
            content="流式回答",
            tool_calls=None,
            usage=Usage(10, 20, 30),
            finish_reason="stop",
        )

        agent = Agent(name="TestAgent", instructions="测试", model=mock_model)

        # 收集所有事件
        events = []
        for event in Runner.run_stream(agent, "测试流式"):
            events.append(event)
            if event.type == StreamEventType.ANSWER:
                break

        assert len(events) > 0

        # 验证事件顺序
        assert events[0].type == StreamEventType.QUESTION
        # 应该有 ANSWER_DELTA 事件（逐字符）
        delta_events = [
            e for e in events if e.type == StreamEventType.ANSWER_DELTA
        ]
        assert len(delta_events) > 0

        # 最后应该是完整的 ANSWER
        answer_events = [e for e in events if e.type == StreamEventType.ANSWER]
        assert len(answer_events) == 1
        assert answer_events[0].content == "流式回答"

    def test_run_stream_with_tool(self):
        """测试流式运行带工具调用"""
        mock_model = MagicMock()
        mock_model.generate.side_effect = [
            ModelResponse(
                content="需要计算",
                tool_calls=[
                    {
                        "function": {
                            "name": "add",
                            "arguments": '{"a": 5, "b": 7}',
                        }
                    }
                ],
                usage=Usage(10, 20, 30),
                finish_reason="tool_calls",
            ),
            ModelResponse(
                content="5 + 7 = 12",
                tool_calls=None,
                usage=Usage(10, 20, 30),
                finish_reason="stop",
            ),
        ]

        agent = Agent(
            name="Calculator",
            instructions="计算器",
            model=mock_model,
            tools=[add],
        )

        events = []
        for event in Runner.run_stream(agent, "计算 5 + 7"):
            events.append(event)
            if event.type == StreamEventType.ANSWER:
                break

        # 验证事件序列
        event_types = [e.type for e in events]
        assert StreamEventType.QUESTION in event_types
        assert StreamEventType.THINKING_DELTA in event_types  # 逐字符思考
        assert StreamEventType.THINKING in event_types
        assert StreamEventType.TOOL_CALL in event_types
        assert StreamEventType.TOOL_RESULT in event_types
        assert StreamEventType.ANSWER_DELTA in event_types
        assert StreamEventType.ANSWER in event_types

    def test_chat_mode(self):
        """测试聊天模式"""
        mock_model = MagicMock()
        mock_model.generate.return_value = ModelResponse(
            content="回答",
            tool_calls=None,
            usage=Usage(10, 20, 30),
            finish_reason="stop",
        )

        agent = Agent(
            name="ChatBot", instructions="聊天机器人", model=mock_model
        )

        # 模拟用户输入
        with patch("builtins.input", side_effect=["测试问题", "quit"]):
            context = Runner.chat(agent)

        assert len(context.messages) > 0
        assert context.usage.total_tokens > 0

    def test_model_no_response(self):
        """测试模型无响应"""
        mock_model = MagicMock()
        mock_model.generate.return_value = ModelResponse(
            content=None,
            tool_calls=None,
            usage=Usage(10, 20, 30),
            finish_reason="stop",
        )

        agent = Agent(name="TestAgent", instructions="测试", model=mock_model)

        result = Runner.run(agent, "测试")

        assert result.success is False
        assert "没有返回任何内容" in result.error

    def test_tool_not_found(self):
        """测试工具未找到"""
        mock_model = MagicMock()
        mock_model.generate.side_effect = [
            ModelResponse(
                content="调用工具",
                tool_calls=[
                    {
                        "function": {
                            "name": "non_existent_tool",
                            "arguments": "{}",
                        }
                    }
                ],
                usage=Usage(10, 20, 30),
                finish_reason="tool_calls",
            ),
            ModelResponse(
                content="工具不存在",
                tool_calls=None,
                usage=Usage(10, 20, 30),
                finish_reason="stop",
            ),
        ]

        agent = Agent(
            name="TestAgent",
            instructions="测试",
            model=mock_model,
            tools=[],  # 没有工具
        )

        result = Runner.run(agent, "调用不存在的工具")

        assert result.success is True

        # 验证错误消息
        messages = result.context.messages
        error_messages = [
            m
            for m in messages
            if m.get("role") == "system"
            and "找不到工具" in m.get("content", "")
        ]
        assert len(error_messages) > 0

    def test_invalid_tool_arguments(self):
        """测试无效的工具参数"""
        mock_model = MagicMock()
        mock_model.generate.side_effect = [
            ModelResponse(
                content="调用工具",
                tool_calls=[
                    {
                        "function": {
                            "name": "add",
                            "arguments": "invalid json",  # 无效的JSON
                        }
                    }
                ],
                usage=Usage(10, 20, 30),
                finish_reason="tool_calls",
            ),
            ModelResponse(
                content="参数错误",
                tool_calls=None,
                usage=Usage(10, 20, 30),
                finish_reason="stop",
            ),
        ]

        agent = Agent(
            name="TestAgent",
            instructions="测试",
            model=mock_model,
            tools=[add],
        )

        result = Runner.run(agent, "测试无效参数")

        # 应该使用空参数继续执行
        assert result.success is True
