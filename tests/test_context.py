"""Context 模块测试"""

from liteagent import Context
from liteagent.context import Usage


class TestUsage:
    """Usage 类测试"""

    def test_usage_initialization(self) -> None:
        """测试 Usage 初始化"""
        usage = Usage()

        assert usage.input_tokens == 0
        assert usage.output_tokens == 0
        assert usage.total_tokens == 0

    def test_usage_add(self) -> None:
        """测试 Usage 累加"""
        usage1 = Usage(input_tokens=10, output_tokens=20, total_tokens=30)
        usage2 = Usage(input_tokens=5, output_tokens=15, total_tokens=20)

        usage1.add(usage2)

        assert usage1.input_tokens == 15
        assert usage1.output_tokens == 35
        assert usage1.total_tokens == 50


class TestContext:
    """Context 类测试"""

    def test_context_initialization(self) -> None:
        """测试 Context 初始化"""
        context = Context()

        assert context.messages == []
        assert isinstance(context.usage, Usage)
        assert context.data == {}

    def test_add_message(self, sample_context: Context) -> None:
        """测试添加消息"""
        sample_context.add_message("user", "你好")

        assert len(sample_context.messages) == 1
        assert sample_context.messages[0]["role"] == "user"
        assert sample_context.messages[0]["content"] == "你好"

    def test_add_message_with_kwargs(self, sample_context: Context) -> None:
        """测试添加带额外参数的消息"""
        sample_context.add_message("user", "你好", name="用户1")

        assert sample_context.messages[0]["name"] == "用户1"

    def test_add_tool_call(self, sample_context: Context) -> None:
        """测试添加工具调用"""
        sample_context.add_tool_call(
            "test_tool", {"arg1": "value1"}, "tool_result"
        )

        assert len(sample_context.messages) == 2

        # 检查助手消息
        assistant_msg = sample_context.messages[0]
        assert assistant_msg["role"] == "assistant"
        assert assistant_msg["content"] is None
        assert len(assistant_msg["tool_calls"]) == 1
        assert (
            assistant_msg["tool_calls"][0]["function"]["name"] == "test_tool"
        )

        # 检查工具结果消息
        tool_msg = sample_context.messages[1]
        assert tool_msg["role"] == "tool"
        assert tool_msg["content"] == "tool_result"

    def test_get_messages_for_api(self, sample_context: Context) -> None:
        """测试获取 API 消息"""
        sample_context.add_message("user", "你好")
        sample_context.add_message("assistant", "你好！")

        messages = sample_context.get_messages_for_api()

        assert len(messages) == 2
        assert messages is not sample_context.messages  # 应该是副本
        assert messages[0]["content"] == "你好"

    def test_set_and_get_data(self, sample_context: Context) -> None:
        """测试设置和获取数据"""
        sample_context.set_data("key1", "value1")
        sample_context.set_data("key2", 42)

        assert sample_context.get_data("key1") == "value1"
        assert sample_context.get_data("key2") == 42
        assert sample_context.get_data("key3") is None
        assert sample_context.get_data("key3", "default") == "default"

    def test_clear_messages(self, sample_context: Context) -> None:
        """测试清空消息"""
        sample_context.add_message("user", "消息1")
        sample_context.add_message("assistant", "消息2")

        sample_context.clear_messages()

        assert len(sample_context.messages) == 0
