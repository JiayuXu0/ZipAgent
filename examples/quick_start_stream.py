#!/usr/bin/env python3
"""LiteAgent 流式输出快速开始示例

展示最常用的流式输出用法
"""

import time

from liteagent import (
    Agent,
    Runner,
    StreamEvent,
    StreamEventType,
    function_tool,
)


@function_tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"计算错误: {e}"


def demo_simple_chat():
    """简单聊天演示"""
    print("💬 简单聊天（逐字符显示）")
    print("-" * 40)

    agent = Agent(
        name="ChatBot",
        instructions="你是一个友好的助手，请用简洁明了的语言回答问题",
    )

    print("🤖 助手: ", end="", flush=True)

    # 逐字符显示回答
    for event in Runner.run_stream_char(agent, "请用一句话介绍Python"):
        if event.type == StreamEventType.ANSWER_DELTA:
            print(event.content, end="", flush=True)
            time.sleep(0.03)  # 控制显示速度
        elif event.type == StreamEventType.ANSWER:
            print("\n")
            break


def demo_tool_thinking():
    """工具调用 + 思考过程演示"""
    print("\n🔧 工具调用演示（显示思考过程）")
    print("-" * 40)

    agent = Agent(
        name="Calculator",
        instructions="在计算前，请先说明你的计算思路",
        tools=[calculate],
    )

    for event in Runner.run_stream_char(agent, "计算 (50 + 30) × 4"):
        if event.type == StreamEventType.THINKING_DELTA:
            # 思考过程用灰色显示（如果终端支持）
            print(f"\033[90m{event.content}\033[0m", end="", flush=True)
            time.sleep(0.02)
        elif event.type == StreamEventType.TOOL_CALL:
            print(f"\n🔧 调用: {event.tool_name}")
        elif event.type == StreamEventType.TOOL_RESULT:
            print(f"📊 结果: {event.tool_result}")
        elif event.type == StreamEventType.ANSWER_DELTA:
            print(event.content, end="", flush=True)
            time.sleep(0.03)
        elif event.type == StreamEventType.ANSWER:
            print("\n")
            break


def demo_callback_usage():
    """回调方式演示"""
    print("\n📞 回调方式演示")
    print("-" * 40)

    agent = Agent(name="Assistant", instructions="请简要回答问题")

    def stream_handler(event: StreamEvent):
        """流式事件处理器"""
        if event.type == StreamEventType.ANSWER:
            print("🤖 助手: ", end="", flush=True)
            # 模拟逐字显示
            for char in event.content:
                print(char, end="", flush=True)
                time.sleep(0.025)
            print()

    Runner.run(agent, "什么是机器学习？", stream_callback=stream_handler)


def main():
    """主函数 - 展示三种最常用的流式输出方式"""
    print("🚀 LiteAgent 流式输出快速开始")
    print("=" * 50)

    # 1. 最简单的逐字符显示
    demo_simple_chat()

    # 2. 工具调用 + 思考过程
    demo_tool_thinking()

    # 3. 回调方式处理
    demo_callback_usage()

    print("\n" + "=" * 50)
    print("📚 使用方法总结:")
    print()
    print("1️⃣ 逐字符流式输出（推荐）:")
    print("   for event in Runner.run_stream_char(agent, question):")
    print("       if event.type == StreamEventType.ANSWER_DELTA:")
    print("           print(event.content, end='', flush=True)")
    print()
    print("2️⃣ 段落级流式输出:")
    print("   for event in Runner.run_stream(agent, question):")
    print("       if event.type == StreamEventType.ANSWER:")
    print("           print(event.content)")
    print()
    print("3️⃣ 回调方式:")
    print("   Runner.run(agent, question, stream_callback=handler)")
    print()
    print("💡 选择建议:")
    print("   • CLI应用: 使用逐字符流式 (run_stream_char)")
    print("   • Web应用: 使用回调方式 (stream_callback)")
    print("   • 简单场景: 使用段落流式 (run_stream)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 演示结束!")
