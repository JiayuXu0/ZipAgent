#!/usr/bin/env python3
"""测试阿里云Qwen API配置

"""

import os
from dotenv import load_dotenv, find_dotenv
from liteagent import Agent, LiteLLMModel, Runner, function_tool

# 自动查找并加载.env文件（从当前目录向上查找）
load_dotenv(find_dotenv())

# 如果没有找到.env，提示用户
if not os.getenv("API_KEY"):
    print("⚠️ 未找到API_KEY配置")
    print("请确保项目根目录有.env文件，或设置环境变量")
    print("参考.env.example创建你的.env文件")

# 从环境变量创建模型配置
qwen_model = LiteLLMModel(
    model_name=os.getenv("MODEL"),
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
    max_tokens=int(os.getenv("MAX_TOKENS")),
    temperature=float(os.getenv("TEMPERATURE")),
)


@function_tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city}今天晴天，温度25℃，空气质量良好"


@function_tool
def calculate_math(a: int, b: int, operation: str = "add") -> str:
    """数学计算"""
    if operation == "add":
        result = a + b
        return f"{a} + {b} = {result}"
    elif operation == "multiply":
        result = a * b
        return f"{a} × {b} = {result}"
    else:
        return f"不支持的运算：{operation}"


def test_basic_chat():
    """测试基本对话"""
    print("💬 测试基本对话...")

    agent = Agent(
        name="QwenAgent",
        instructions="你是一个helpful的AI助手",
        model=qwen_model,
    )

    result = Runner.run(agent, "你好，请简单介绍一下自己")
    print(f"✅ 响应: {result.content}")
    print(f"✅ 成功: {result.success}")

    return result.success


def test_weather_tool():
    """测试天气工具调用"""
    print("\n🌤️ 测试天气工具...")

    agent = Agent(
        name="WeatherBot",
        instructions="你是天气助手，可以查询天气。收到工具结果后，请友好地告诉用户天气情况。",
        model=qwen_model,
        tools=[get_weather],
    )

    result = Runner.run(agent, "上海的天气怎么样？")
    print(f"✅ 响应: {result.content}")
    print(f"✅ 成功: {result.success}")

    return result.success


def test_math_tool():
    """测试数学工具调用"""
    print("\n🔢 测试数学工具...")

    agent = Agent(
        name="MathBot",
        instructions="你是数学助手，可以做加法和乘法运算。收到工具结果后，请告诉用户计算结果。",
        model=qwen_model,
        tools=[calculate_math],
    )

    result = Runner.run(agent, "请帮我计算 23 × 17")
    print(f"✅ 响应: {result.content}")
    print(f"✅ 成功: {result.success}")

    return result.success


def test_multiple_rounds():
    """测试多轮对话"""
    print("\n🔄 测试多轮对话...")

    from liteagent import Context

    agent = Agent(
        name="ChatBot",
        instructions="你是聊天助手，记住用户说的话",
        model=qwen_model,
    )

    context = Context()

    # 第一轮
    result1 = Runner.run(agent, "我的名字是小王，我喜欢编程", context)
    print(f"第1轮: {result1.content}")

    # 第二轮
    result2 = Runner.run(agent, "你还记得我的名字和爱好吗？", context)
    print(f"第2轮: {result2.content}")

    return result1.success and result2.success


def main():
    print("🚀 阿里云Qwen API测试")
    print("=" * 50)

    results = []

    try:
        # 测试1: 基本对话
        results.append(test_basic_chat())

        # 测试2: 天气工具
        results.append(test_weather_tool())

        # 测试3: 数学工具
        results.append(test_math_tool())

        # 测试4: 多轮对话
        results.append(test_multiple_rounds())

        # 结果统计
        success_count = sum(results)
        total_count = len(results)
        success_rate = success_count / total_count * 100

        print("\n📊 测试结果:")
        print(f"✅ 成功: {success_count}/{total_count}")
        print(f"✅ 成功率: {success_rate:.1f}%")

        if success_count == total_count:
            print("🎉 所有测试通过！Qwen API配置完美！")
        elif success_count >= total_count * 0.75:
            print("👍 大部分测试通过！API基本可用！")
        else:
            print("⚠️ 部分测试失败，请检查配置")

    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
