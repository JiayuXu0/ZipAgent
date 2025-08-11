#!/usr/bin/env python3
"""演示思考模式的工具调用格式

这个示例展示了如何使用 thinking_tool_mode 功能，
要求AI在调用工具前先输出思考过程。
"""

from liteagent import Agent, Runner, function_tool


@function_tool
def calculate(expression: str) -> str:
    """计算数学表达式
    
    Args:
        expression: 数学表达式，如 "2+2", "10*5"
    
    Returns:
        计算结果的字符串形式
    """
    try:
        # 注意：实际使用应该用安全的解析器
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"


@function_tool
def get_weather(city: str) -> str:
    """获取城市天气信息
    
    Args:
        city: 城市名称
        
    Returns:
        天气信息
    """
    return f"{city}今天晴天，温度25℃，空气质量良好"


def demo_normal_mode():
    """演示普通模式（默认）"""
    print("=" * 60)
    print("🔧 普通模式演示")
    print("=" * 60)
    
    agent = Agent(
        name="计算助手",
        instructions="你是一个有用的计算助手",
        tools=[calculate, get_weather],
        thinking_tool_mode=True  # 关闭思考模式
    )
    
    result = Runner.run(agent, "请计算 15 * 8")
    print(f"用户: 请计算 15 * 8")
    print(f"助手: {result.content}")
    print()


def demo_thinking_mode():
    """演示思考模式"""
    print("=" * 60)
    print("🧠 思考模式演示")
    print("=" * 60)
    
    agent = Agent(
        name="思考助手",
        instructions="你是一个仔细思考的助手",
        tools=[calculate, get_weather],
        thinking_tool_mode=True  # 启用思考模式
    )
    
    result = Runner.run(agent, "请计算 15 * 8，然后告诉我北京的天气")
    print(f"用户: 请计算 15 * 8，然后告诉我北京的天气")
    print(f"助手: {result.content}")
    print()


def demo_runtime_override():
    """演示运行时覆盖模式"""
    print("=" * 60)
    print("⚙️ 运行时覆盖演示")
    print("=" * 60)
    
    # Agent默认关闭思考模式
    agent = Agent(
        name="普通助手",
        instructions="你是一个助手",
        tools=[calculate],
        thinking_tool_mode=True
    )
    
    # 但是在运行时启用思考模式
    result = Runner.run(
        agent, 
        "计算 100 / 4", 
        thinking_tool_mode=True  # 运行时覆盖为开启
    )
    print(f"用户: 计算 100 / 4")
    print(f"助手: {result.content}")
    print("注意：虽然Agent默认关闭思考模式，但运行时启用了")
    print()


def main():
    print("🚀 LiteAgent 思考模式工具调用演示")
    print()
    
    # 演示三种使用方式
    # demo_normal_mode()
    demo_thinking_mode()
    # demo_runtime_override()
    
    print("=" * 60)
    print("📝 说明:")
    print("1. 普通模式: 直接调用工具，无额外格式要求")
    print("2. 思考模式: 要求AI先输出<thinking>标签解释思路")
    print("3. 运行时覆盖: 可以在Runner.run()时临时改变模式")
    print("=" * 60)


if __name__ == "__main__":
    main()