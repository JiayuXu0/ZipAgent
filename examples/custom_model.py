"""自定义模型实现示例"""

import random
from typing import Any, Dict, List, Optional

from liteagent import Agent, Context, Model, Runner
from liteagent.context import Usage
from liteagent.model import ModelResponse


class MockModel(Model):
    """模拟的 LLM 模型，用于测试和演示"""

    def __init__(self, name: str = "MockModel"):
        self.name = name
        self.call_count = 0

    def generate(self, messages: List[Dict[str, Any]],
                tools: Optional[List[Dict[str, Any]]] = None) -> ModelResponse:
        """生成模拟响应"""
        self.call_count += 1

        # 获取最后一条用户消息
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        # 根据消息内容生成不同的响应
        if "计算" in user_message and tools:
            # 模拟工具调用
            return ModelResponse(
                content=None,
                tool_calls=[{
                    "id": f"call_{self.call_count}",
                    "type": "function",
                    "function": {
                        "name": "calculate",
                        "arguments": '{"expression": "2 + 2"}'
                    }
                }],
                usage=Usage(input_tokens=10, output_tokens=15, total_tokens=25),
                finish_reason="tool_calls"
            )
        else:
            # 普通文本响应
            responses = [
                f"这是来自 {self.name} 的响应。",
                f"我已经处理了您的请求：{user_message[:20]}...",
                f"第 {self.call_count} 次调用的模拟响应。"
            ]

            return ModelResponse(
                content=random.choice(responses),
                tool_calls=[],
                usage=Usage(
                    input_tokens=len(user_message.split()),
                    output_tokens=20,
                    total_tokens=len(user_message.split()) + 20
                ),
                finish_reason="stop"
            )


class EchoModel(Model):
    """回显模型，简单地重复用户输入"""

    def generate(self, messages: List[Dict[str, Any]],
                tools: Optional[List[Dict[str, Any]]] = None) -> ModelResponse:
        """生成回显响应"""
        # 找到最后一条用户消息
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        # 回显用户消息
        response = f"你说的是：{user_message}"

        return ModelResponse(
            content=response,
            tool_calls=[],
            usage=Usage(
                input_tokens=len(user_message),
                output_tokens=len(response),
                total_tokens=len(user_message) + len(response)
            ),
            finish_reason="stop"
        )


def main():
    """演示自定义模型的使用"""

    print("=" * 50)
    print("自定义模型示例")
    print("=" * 50)

    # 示例 1: 使用 MockModel
    print("\n示例 1: MockModel")
    print("-" * 30)

    mock_model = MockModel("测试模型")
    agent1 = Agent(
        name="Mock助手",
        instructions="你是一个使用模拟模型的助手",
        model=mock_model
    )

    # 测试几次调用
    for i in range(3):
        result = Runner.run(agent1, f"这是第 {i+1} 条消息")
        print(f"请求 {i+1}: {result.content}")

    print(f"总调用次数: {mock_model.call_count}")

    # 示例 2: 使用 EchoModel
    print("\n示例 2: EchoModel")
    print("-" * 30)

    echo_model = EchoModel()
    agent2 = Agent(
        name="Echo助手",
        instructions="你是一个回显助手",
        model=echo_model
    )

    # 测试回显
    test_messages = [
        "你好，世界！",
        "LiteAgent 真棒",
        "这是一个回显测试"
    ]

    for msg in test_messages:
        result = Runner.run(agent2, msg)
        print(f"输入: {msg}")
        print(f"输出: {result.content}")
        print()

    # 示例 3: 多轮对话与 token 统计
    print("\n示例 3: 多轮对话与统计")
    print("-" * 30)

    context = Context()
    agent3 = Agent(
        name="统计助手",
        instructions="你是一个会统计 token 的助手",
        model=EchoModel()
    )

    messages = ["短消息", "这是一条稍微长一点的消息", "超长消息" * 10]

    for msg in messages:
        result = Runner.run(agent3, msg, context)
        print(f"消息: {msg[:30]}...")
        print(f"Token 使用: 输入={context.usage.input_tokens}, "
              f"输出={context.usage.output_tokens}, "
              f"总计={context.usage.total_tokens}")
        print()


if __name__ == "__main__":
    main()
