"""Agent 模块测试"""

from unittest.mock import Mock

from zipagent import Agent, Tool
from zipagent.model import OpenAIModel


class TestAgent:
    """Agent 类测试"""

    def test_agent_initialization(self, mock_model: Mock) -> None:
        """测试 Agent 初始化"""
        agent = Agent(
            name="TestAgent", instructions="测试指令", model=mock_model
        )

        assert agent.name == "TestAgent"
        assert agent.instructions == "测试指令"
        assert agent.model == mock_model
        assert agent.tools == []

    def test_agent_default_model(self) -> None:
        """测试 Agent 使用默认模型"""
        agent = Agent(name="TestAgent", instructions="测试指令")

        assert isinstance(agent.model, OpenAIModel)

    def test_get_system_message_without_tools(
        self, sample_agent: Agent
    ) -> None:
        """测试获取系统消息（无工具）"""
        # 禁用系统提示进行测试
        sample_agent.use_system_prompt = False
        message = sample_agent.get_system_message()

        assert message["role"] == "system"
        assert message["content"] == "你是一个测试助手"

    def test_get_system_message_with_tools(
        self, agent_with_tools: Agent
    ) -> None:
        """测试获取系统消息（有工具）"""
        message = agent_with_tools.get_system_message()

        assert message["role"] == "system"
        assert "你是一个可以使用工具的测试助手" in message["content"]
        assert "test_function" in message["content"]

    def test_add_tool(self, sample_agent: Agent, sample_tool: Tool) -> None:
        """测试添加工具"""
        sample_agent.add_tool(sample_tool)

        assert len(sample_agent.tools) == 1
        assert sample_agent.tools[0] == sample_tool

    def test_find_tool(self, agent_with_tools: Agent) -> None:
        """测试查找工具"""
        tool = agent_with_tools.find_tool("test_function")

        assert tool is not None
        assert tool.name == "test_function"

    def test_find_tool_not_found(self, agent_with_tools: Agent) -> None:
        """测试查找不存在的工具"""
        tool = agent_with_tools.find_tool("non_existent")

        assert tool is None

    def test_remove_tool(self, agent_with_tools: Agent) -> None:
        """测试移除工具"""
        result = agent_with_tools.remove_tool("test_function")

        assert result is True
        assert len(agent_with_tools.tools) == 0

    def test_remove_tool_not_found(self, agent_with_tools: Agent) -> None:
        """测试移除不存在的工具"""
        result = agent_with_tools.remove_tool("non_existent")

        assert result is False
        assert len(agent_with_tools.tools) == 1

    def test_get_tools_schema(self, agent_with_tools: Agent) -> None:
        """测试获取工具 schema"""
        schemas = agent_with_tools.get_tools_schema()

        assert len(schemas) == 1
        assert schemas[0]["type"] == "function"
        assert schemas[0]["function"]["name"] == "test_function"
