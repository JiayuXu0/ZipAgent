"""pytest 配置和共享 fixtures"""

from unittest.mock import Mock

import pytest

from zipagent import Agent, Context, Tool, function_tool
from zipagent.model import Model, ModelResponse, Usage


@pytest.fixture
def mock_model() -> Mock:
    """创建一个模拟的 Model 对象"""
    model = Mock(spec=Model)
    model.generate.return_value = ModelResponse(
        content="测试响应",
        tool_calls=[],
        usage=Usage(input_tokens=10, output_tokens=20, total_tokens=30),
        finish_reason="stop",
    )
    return model


@pytest.fixture
def sample_agent(mock_model: Mock) -> Agent:
    """创建一个示例 Agent"""
    return Agent(
        name="TestAgent", instructions="你是一个测试助手", model=mock_model
    )


@pytest.fixture
def sample_context() -> Context:
    """创建一个示例 Context"""
    return Context()


@pytest.fixture
def sample_tool() -> Tool:
    """创建一个示例工具"""

    @function_tool
    def test_function(x: int, y: int) -> int:
        """测试函数：返回两数之和"""
        return x + y

    return test_function


@pytest.fixture
def agent_with_tools(mock_model: Mock, sample_tool: Tool) -> Agent:
    """创建一个带工具的 Agent"""
    agent = Agent(
        name="TestAgentWithTools",
        instructions="你是一个可以使用工具的测试助手",
        model=mock_model,
        tools=[sample_tool],
    )
    return agent
