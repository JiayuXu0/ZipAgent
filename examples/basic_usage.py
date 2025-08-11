"""LiteAgent 基础使用示例"""

import os

from liteagent import Agent, Context, Runner, function_tool


# 定义一些工具函数
@function_tool
def calculate(expression: str) -> str:
    """计算数学表达式

    注意：实际使用中应该使用安全的表达式解析器，
    这里仅作演示用途。
    """
    try:
        # 限制可用的函数和操作
        allowed_names = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
        }
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"计算错误: {e!s}"


@function_tool(name="get_weather", description="获取天气信息")
def get_weather(city: str) -> str:
    """获取指定城市的天气（模拟）"""
    # 这里应该调用实际的天气 API
    weather_data = {
        "北京": "晴天，温度 25°C",
        "上海": "多云，温度 28°C",
        "深圳": "阵雨，温度 30°C",
    }
    return weather_data.get(city, f"未找到 {city} 的天气信息")


@function_tool
def search_web(query: str) -> str:
    """搜索网络信息（模拟）"""
    return f"搜索 '{query}' 的结果：这是一个模拟的搜索结果。"


def main():
    """主函数"""

    # 创建一个带工具的 Agent
    agent = Agent(
        name="智能助手",
        instructions="""你是一个有用的 AI 助手。
        你可以帮助用户进行数学计算、查询天气和搜索信息。
        请尽可能准确和有帮助地回答用户的问题。""",
        tools=[calculate, get_weather, search_web]
    )

    print("=" * 50)
    print("LiteAgent 示例程序")
    print("=" * 50)

    # 示例 1: 简单对话
    print("\n示例 1: 简单对话")
    print("-" * 30)
    result = Runner.run(agent, "你好，请介绍一下你自己")
    print(f"助手: {result.content}")

    # 示例 2: 使用工具 - 数学计算
    print("\n示例 2: 数学计算")
    print("-" * 30)
    result = Runner.run(agent, "请计算 (15 + 25) * 2")
    print(f"助手: {result.content}")

    # 示例 3: 使用工具 - 查询天气
    print("\n示例 3: 查询天气")
    print("-" * 30)
    result = Runner.run(agent, "北京和上海的天气怎么样？")
    print(f"助手: {result.content}")

    # 示例 4: 多轮对话
    print("\n示例 4: 多轮对话")
    print("-" * 30)
    context = Context()

    # 第一轮
    result = Runner.run(agent, "我想了解一下Python", context)
    print("用户: 我想了解一下Python")
    print(f"助手: {result.content}")

    # 第二轮，基于上下文继续对话
    result = Runner.run(agent, "它适合做什么类型的项目？", context)
    print("\n用户: 它适合做什么类型的项目？")
    print(f"助手: {result.content}")

    # 显示 token 使用情况
    print(f"\n总 Token 使用量: {context.usage.total_tokens}")

    # 示例 5: 交互式对话（可选）
    print("\n" + "=" * 50)
    print("进入交互式对话模式")
    print("输入 'quit' 或 'exit' 退出")
    print("=" * 50)

    # Runner.chat(agent)  # 取消注释以启用交互式对话


if __name__ == "__main__":
    # 确保设置了必要的环境变量
    if not os.getenv("API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("警告: 未设置 API_KEY 或 OPENAI_API_KEY 环境变量")
        print("请设置环境变量或创建 .env 文件")
        print("示例: export API_KEY=your_api_key")
    else:
        main()
