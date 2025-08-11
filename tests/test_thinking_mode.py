"""测试思考模式功能"""

from unittest.mock import Mock

import pytest

from liteagent import Agent, Runner, function_tool
from liteagent.context import Context
from liteagent.model import ModelResponse
from liteagent.context import Usage


@function_tool  
def test_calculate(expression: str) -> str:
    """测试计算工具"""
    return str(eval(expression))


class TestThinkingMode:
    """思考模式测试"""

    def test_agent_thinking_mode_default(self) -> None:
        """测试Agent默认关闭思考模式"""
        agent = Agent(
            name="TestAgent",
            instructions="测试",
            tools=[test_calculate]
        )
        
        assert agent.thinking_tool_mode is False

    def test_agent_thinking_mode_enabled(self) -> None:
        """测试Agent启用思考模式"""
        agent = Agent(
            name="TestAgent", 
            instructions="测试",
            tools=[test_calculate],
            thinking_tool_mode=True
        )
        
        assert agent.thinking_tool_mode is True

    def test_system_message_normal_mode(self) -> None:
        """测试普通模式的系统消息"""
        agent = Agent(
            name="TestAgent",
            instructions="你是测试助手",
            tools=[test_calculate],
            thinking_tool_mode=False
        )
        
        message = agent.get_system_message()
        content = message["content"]
        
        assert "你是测试助手" in content
        assert "test_calculate" in content
        assert "当需要使用工具时，请调用相应的函数。" in content
        assert "<thinking>" not in content

    def test_system_message_thinking_mode(self) -> None:
        """测试思考模式的系统消息"""
        agent = Agent(
            name="TestAgent",
            instructions="你是测试助手", 
            tools=[test_calculate],
            thinking_tool_mode=True
        )
        
        message = agent.get_system_message()
        content = message["content"]
        
        assert "你是测试助手" in content
        assert "test_calculate" in content
        assert "严格要求：调用工具时必须严格按此格式" in content
        assert "<thinking>" in content
        assert "<tool_call>" in content
        assert "绝对强制示例" in content
        assert "警告：不按此格式会导致执行失败" in content

    def test_runner_thinking_mode_override(self, mock_model: Mock) -> None:
        """测试Runner.run方法的thinking_mode覆盖功能"""
        # 创建默认关闭思考模式的Agent
        agent = Agent(
            name="TestAgent",
            instructions="测试",
            tools=[test_calculate],
            thinking_tool_mode=False,
            model=mock_model
        )
        
        # 模拟模型返回
        mock_model.generate.return_value = ModelResponse(
            content="测试回复",
            tool_calls=[],
            usage=Usage(),
            finish_reason="stop"
        )
        
        # 验证默认状态
        assert agent.thinking_tool_mode is False
        
        # 运行时启用思考模式  
        context = Context()
        Runner.run(agent, "测试", context, thinking_tool_mode=True)
        
        # 验证运行后Agent状态恢复
        assert agent.thinking_tool_mode is False
        
        # 验证系统消息被正确更新（通过检查上下文中的消息）
        messages = context.get_messages_for_api()
        system_message = messages[0]["content"]
        assert "严格要求：调用工具时必须严格按此格式" in system_message

    def test_runner_thinking_mode_no_override(self, mock_model: Mock) -> None:
        """测试Runner.run不覆盖时使用Agent原始设置"""
        # 创建启用思考模式的Agent
        agent = Agent(
            name="TestAgent", 
            instructions="测试",
            tools=[test_calculate],
            thinking_tool_mode=True,
            model=mock_model
        )
        
        # 模拟模型返回
        mock_model.generate.return_value = ModelResponse(
            content="测试回复",
            tool_calls=[],
            usage=Usage(),
            finish_reason="stop"
        )
        
        # 运行时不指定thinking_tool_mode
        context = Context()
        Runner.run(agent, "测试", context)
        
        # 验证Agent状态未改变
        assert agent.thinking_tool_mode is True
        
        # 验证系统消息使用了思考模式
        messages = context.get_messages_for_api()
        system_message = messages[0]["content"]
        assert "严格要求：调用工具时必须严格按此格式" in system_message

    def test_runner_disable_thinking_mode(self, mock_model: Mock) -> None:
        """测试Runner.run运行时关闭思考模式"""
        # 创建默认启用思考模式的Agent
        agent = Agent(
            name="TestAgent",
            instructions="测试",
            tools=[test_calculate],  
            thinking_tool_mode=True,
            model=mock_model
        )
        
        # 模拟模型返回
        mock_model.generate.return_value = ModelResponse(
            content="测试回复",
            tool_calls=[],
            usage=Usage(),
            finish_reason="stop"
        )
        
        # 验证初始状态
        assert agent.thinking_tool_mode is True
        
        # 运行时关闭思考模式
        context = Context()
        Runner.run(agent, "测试", context, thinking_tool_mode=False)
        
        # 验证运行后Agent状态恢复
        assert agent.thinking_tool_mode is True
        
        # 验证系统消息使用了普通模式
        messages = context.get_messages_for_api()
        system_message = messages[0]["content"] 
        assert "当需要使用工具时，请调用相应的函数。" in system_message
        assert "严格要求：调用工具时必须严格按此格式" not in system_message