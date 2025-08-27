"""Context 模块测试"""

from datetime import datetime

from zipagent import Context
from zipagent.context import Usage


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
        sample_context.turn_count = 3

        sample_context.clear_messages()

        assert len(sample_context.messages) == 0
        assert sample_context.turn_count == 0  # 轮次应该重置

    # === 新增功能的测试 ===

    def test_context_metadata_initialization(self) -> None:
        """测试 Context 元数据初始化"""
        context = Context()

        # 检查自动生成的元数据
        assert context.context_id is not None
        assert isinstance(context.context_id, str)
        assert len(context.context_id) == 36  # UUID 长度

        assert isinstance(context.created_at, datetime)
        assert context.created_at <= datetime.now()

        assert context.last_agent is None
        assert context.turn_count == 0

    def test_context_id_uniqueness(self) -> None:
        """测试 Context ID 唯一性"""
        context1 = Context()
        context2 = Context()

        assert context1.context_id != context2.context_id

    def test_get_summary(self) -> None:
        """测试获取 Context 摘要"""
        context = Context()
        context.add_message("user", "测试消息")
        context.last_agent = "TestBot"
        context.turn_count = 2
        context.usage.total_tokens = 100

        summary = context.get_summary()

        assert "context_id" in summary
        assert "created_at" in summary
        assert "last_agent" in summary
        assert "turn_count" in summary
        assert "message_count" in summary
        assert "total_tokens" in summary

        assert summary["context_id"] == context.context_id
        assert summary["last_agent"] == "TestBot"
        assert summary["turn_count"] == 2
        assert summary["message_count"] == 1
        assert summary["total_tokens"] == 100

    def test_clone_basic(self) -> None:
        """测试 Context 基础克隆功能"""
        original = Context()
        original.add_message("user", "原始消息")
        original.set_data("key", "value")
        original.last_agent = "OriginalBot"
        original.turn_count = 3

        cloned = original.clone()

        # 验证克隆的正确性
        assert cloned.context_id == original.context_id  # 相同会话ID
        assert cloned.created_at == original.created_at
        assert cloned.last_agent == original.last_agent
        assert cloned.turn_count == original.turn_count
        assert len(cloned.messages) == len(original.messages)
        assert cloned.data == original.data

    def test_clone_deep_copy(self) -> None:
        """测试 Context 深拷贝特性"""
        original = Context()
        original.add_message("user", "消息1")
        original.set_data("nested", {"key": "value"})

        cloned = original.clone()

        # 验证是不同的对象
        assert cloned is not original
        assert cloned.messages is not original.messages
        assert cloned.data is not original.data
        assert cloned.usage is not original.usage

        # 修改克隆应该不影响原始
        cloned.add_message("user", "消息2")
        cloned.data["nested"]["key"] = "modified"

        assert len(original.messages) == 1
        assert len(cloned.messages) == 2
        assert original.data["nested"]["key"] == "value"
        assert cloned.data["nested"]["key"] == "modified"

    def test_clone_usage_independence(self) -> None:
        """测试克隆后 Usage 统计的独立性"""
        original = Context()
        original.usage.input_tokens = 100
        original.usage.output_tokens = 200
        original.usage.total_tokens = 300

        cloned = original.clone()

        # 修改克隆的使用量
        cloned.usage.input_tokens = 150

        # 验证原始不受影响
        assert original.usage.input_tokens == 100
        assert cloned.usage.input_tokens == 150

    def test_string_representation(self) -> None:
        """测试 Context 字符串表示"""
        context = Context()
        context.add_message("user", "测试")
        context.turn_count = 1

        str_repr = str(context)

        assert "Context(id=" in str_repr
        assert "messages=1" in str_repr
        assert "turns=1" in str_repr
        assert "usage=" in str_repr

    def test_context_evolution(self) -> None:
        """测试 Context 在对话过程中的演进"""
        context = Context()

        # 模拟对话进程
        context.last_agent = "Agent1"
        context.turn_count = 1
        context.add_message("user", "第一个问题")

        # 切换Agent
        context.last_agent = "Agent2"
        context.turn_count = 2
        context.add_message("assistant", "Agent2的回复")

        # 验证状态
        assert context.last_agent == "Agent2"
        assert context.turn_count == 2
        assert len(context.messages) == 2

    def test_metadata_persistence_after_clone(self) -> None:
        """测试克隆后元数据的持久性"""
        original = Context()
        original.last_agent = "TestAgent"
        original.turn_count = 5

        cloned = original.clone()

        # 元数据应该保持一致
        assert cloned.last_agent == "TestAgent"
        assert cloned.turn_count == 5
        assert cloned.context_id == original.context_id
        assert cloned.created_at == original.created_at
