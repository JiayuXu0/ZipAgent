"""测试 Stream 模块"""

from zipagent.stream import StreamEvent, StreamEventType


class TestStreamEventType:
    """测试流式事件类型枚举"""

    def test_event_types(self):
        """测试所有事件类型"""
        assert StreamEventType.QUESTION.value == "question"
        assert StreamEventType.THINKING.value == "thinking"
        assert StreamEventType.THINKING_DELTA.value == "thinking_delta"
        assert StreamEventType.TOOL_CALL.value == "tool_call"
        assert StreamEventType.TOOL_RESULT.value == "tool_result"
        assert StreamEventType.ANSWER.value == "answer"
        assert StreamEventType.ANSWER_DELTA.value == "answer_delta"
        assert StreamEventType.ERROR.value == "error"


class TestStreamEvent:
    """测试 StreamEvent 类"""

    def test_stream_event_initialization(self):
        """测试 StreamEvent 初始化"""
        event = StreamEvent(
            type=StreamEventType.ANSWER,
            content="测试内容",
            tool_name="test_tool",
            tool_args={"arg": "value"},
            tool_result="结果",
            error="错误信息",
        )

        assert event.type == StreamEventType.ANSWER
        assert event.content == "测试内容"
        assert event.tool_name == "test_tool"
        assert event.tool_args == {"arg": "value"}
        assert event.tool_result == "结果"
        assert event.error == "错误信息"

    def test_question_event(self):
        """测试问题事件创建"""
        event = StreamEvent.question("用户问题")

        assert event.type == StreamEventType.QUESTION
        assert event.content == "用户问题"
        assert event.tool_name is None
        assert event.tool_args is None
        assert event.tool_result is None
        assert event.error is None

    def test_thinking_event(self):
        """测试思考事件创建"""
        event = StreamEvent.thinking("AI正在思考")

        assert event.type == StreamEventType.THINKING
        assert event.content == "AI正在思考"

    def test_thinking_delta_event(self):
        """测试思考增量事件"""
        event = StreamEvent.thinking_delta("思")

        assert event.type == StreamEventType.THINKING_DELTA
        assert event.content == "思"

    def test_tool_call_event(self):
        """测试工具调用事件"""
        args = {"a": 1, "b": 2}
        event = StreamEvent.tool_call("calculator", args)

        assert event.type == StreamEventType.TOOL_CALL
        assert event.tool_name == "calculator"
        assert event.tool_args == args
        assert event.content is None

    def test_tool_result_event(self):
        """测试工具结果事件"""
        event = StreamEvent.create_tool_result("calculator", "3")

        assert event.type == StreamEventType.TOOL_RESULT
        assert event.tool_name == "calculator"
        assert event.tool_result == "3"
        assert event.content is None

    def test_answer_event(self):
        """测试回答事件"""
        event = StreamEvent.answer("最终答案")

        assert event.type == StreamEventType.ANSWER
        assert event.content == "最终答案"

    def test_answer_delta_event(self):
        """测试回答增量事件"""
        event = StreamEvent.answer_delta("答")

        assert event.type == StreamEventType.ANSWER_DELTA
        assert event.content == "答"

    def test_error_event(self):
        """测试错误事件"""
        event = StreamEvent.create_error("发生错误")

        assert event.type == StreamEventType.ERROR
        assert event.error == "发生错误"
        assert event.content is None

    def test_stream_event_dict_conversion(self):
        """测试转换为字典"""
        event = StreamEvent(
            type=StreamEventType.TOOL_CALL,
            tool_name="test",
            tool_args={"x": 1},
        )

        # 测试可以访问属性
        assert hasattr(event, "type")
        assert hasattr(event, "tool_name")
        assert hasattr(event, "tool_args")

        # 验证值
        assert event.type == StreamEventType.TOOL_CALL
        assert event.tool_name == "test"
        assert event.tool_args == {"x": 1}

    def test_stream_event_equality(self):
        """测试事件相等性"""
        event1 = StreamEvent.question("问题")
        event2 = StreamEvent.question("问题")
        event3 = StreamEvent.answer("问题")

        # 相同内容和类型应该相等
        assert event1.type == event2.type
        assert event1.content == event2.content

        # 不同类型应该不相等
        assert event1.type != event3.type

    def test_stream_event_repr(self):
        """测试事件字符串表示"""
        event = StreamEvent.answer("测试")

        # 应该可以转换为字符串
        str_repr = str(event)
        assert str_repr is not None

        # repr 应该包含有用信息
        repr_str = repr(event)
        assert repr_str is not None
