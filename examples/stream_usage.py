#!/usr/bin/env python3
"""LiteAgent 流式输出使用示例

演示如何使用流式输出功能
"""

from liteagent import (
    Agent,
    Runner,
    StreamEvent,
    StreamEventType,
    function_tool,
)


@function_tool
def calculate(expression: str) -> str:
    """计算数学表达式

    Args:
        expression: 数学表达式，如 "2+2", "10*5"

    Returns:
        计算结果的字符串形式
    """
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"


@function_tool
def get_weather(city: str) -> str:
    """获取城市天气（模拟）

    Args:
        city: 城市名称

    Returns:
        天气信息
    """
    weather_data = {
        "北京": "晴天，温度 20°C",
        "上海": "多云，温度 22°C",
        "深圳": "小雨，温度 25°C",
    }
    return weather_data.get(city, f"{city}的天气数据暂时无法获取")


def demo_callback_style():
    """演示回调风格的流式输出"""
    print("=" * 60)
    print("回调风格示例")
    print("=" * 60)

    agent = Agent(
        name="Assistant",
        instructions="你是一个有用的助手，可以进行计算和查询天气",
        tools=[calculate, get_weather],
    )

    def stream_handler(event: StreamEvent):
        """流式事件处理器"""
        if event.type == StreamEventType.QUESTION:
            print(f"📝 问题: {event.content}")
        elif event.type == StreamEventType.THINKING:
            print(f"💭 思考: {event.content}")
        elif event.type == StreamEventType.TOOL_CALL:
            print(f"🔧 调用工具: {event.tool_name}({event.tool_args})")
        elif event.type == StreamEventType.TOOL_RESULT:
            print(f"📊 工具结果: {event.tool_result}")
        elif event.type == StreamEventType.ANSWER:
            print(f"✅ 回答: {event.content}")
        elif event.type == StreamEventType.ERROR:
            print(f"❌ 错误: {event.error}")

    # 使用回调方式
    result = Runner.run(
        agent=agent,
        user_input="计算 15 * 8 的结果",
        stream_callback=stream_handler,
    )

    print(f"\n最终结果: {result.content}")


def demo_generator_style():
    """演示生成器风格的流式输出"""
    print("\n" + "=" * 60)
    print("生成器风格示例 - 真正的流式处理")
    print("=" * 60)

    agent = Agent(
        name="WeatherBot",
        instructions="你是一个天气助手，可以查询天气和进行相关计算",
        tools=[calculate, get_weather],
    )

    # 使用生成器方式 - 每个事件会立即处理
    print("开始流式处理，每个事件会立即显示...")

    for event in Runner.run_stream(agent, "北京和上海的平均温度是多少？"):
        if event.type == StreamEventType.QUESTION:
            print(f"📝 用户问题: {event.content}")
        elif event.type == StreamEventType.THINKING:
            print(f"💭 AI思考: {event.content}")
        elif event.type == StreamEventType.TOOL_CALL:
            print(f"🔧 调用工具: {event.tool_name} -> {event.tool_args}")
        elif event.type == StreamEventType.TOOL_RESULT:
            print(f"📊 工具输出: {event.tool_result}")
        elif event.type == StreamEventType.ANSWER:
            print(f"✅ 最终答案: {event.content}")
        elif event.type == StreamEventType.ERROR:
            print(f"❌ 出现错误: {event.error}")

    print("🎉 流式处理完成！")


def demo_custom_handler():
    """演示自定义处理器"""
    print("\n" + "=" * 60)
    print("自定义处理器示例")
    print("=" * 60)

    class CustomStreamHandler:
        def __init__(self):
            self.events = []
            self.step = 1

        def handle(self, event: StreamEvent):
            self.events.append(event)

            if event.type == StreamEventType.QUESTION:
                print(f"步骤 {self.step}: 收到问题 - {event.content}")
                self.step += 1
            elif event.type == StreamEventType.THINKING:
                print(f"步骤 {self.step}: AI正在思考...")
                # 只显示思考的前50个字符
                content = (
                    event.content[:50] + "..."
                    if len(event.content) > 50
                    else event.content
                )
                print(f"         思考内容: {content}")
                self.step += 1
            elif event.type == StreamEventType.TOOL_CALL:
                print(f"步骤 {self.step}: 调用工具 {event.tool_name}")
                self.step += 1
            elif event.type == StreamEventType.TOOL_RESULT:
                print(
                    f"步骤 {self.step}: 工具执行完成，结果: {event.tool_result}"
                )
                self.step += 1
            elif event.type == StreamEventType.ANSWER:
                print(f"步骤 {self.step}: 生成最终回答")
                print(f"         回答内容: {event.content}")
                self.step += 1

        def get_summary(self):
            return f"总共处理了 {len(self.events)} 个事件"

    agent = Agent(
        name="Calculator", instructions="你是一个计算助手", tools=[calculate]
    )

    handler = CustomStreamHandler()

    result = Runner.run(
        agent=agent,
        user_input="计算 (25 + 75) / 4 的值",
        stream_callback=handler.handle,
    )

    print(f"\n{handler.get_summary()}")
    print(f"最终结果: {result.content}")


def main():
    print("🚀 LiteAgent 流式输出功能演示")

    # 演示三种使用方式
    # demo_callback_style()
    demo_generator_style()
    # demo_custom_handler()


if __name__ == "__main__":
    main()
