#!/usr/bin/env python3
"""LiteAgent 基础使用示例

演示如何快速创建和运行一个AI Agent
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


def main():
    # 创建Agent
    agent = Agent(
        name="MathAssistant",
        instructions="你是一个数学助手，可以帮助用户进行计算",
        tools=[calculate]
    )
    
    # 运行对话
    print("🤖 数学助手已启动")
    print("-" * 40)
    
    # 示例1：简单计算
    result = Runner.run(agent, "请计算 23 + 45")
    print(f"问: 请计算 23 + 45")
    print(f"答: {result.content}")
    print()
    
    # 示例2：复杂计算
    result = Runner.run(agent, "计算 (100 + 200) * 3 / 2")
    print(f"问: 计算 (100 + 200) * 3 / 2")
    print(f"答: {result.content}")


if __name__ == "__main__":
    main()