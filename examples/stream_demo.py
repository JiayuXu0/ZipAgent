#!/usr/bin/env python3
"""
LiteAgent 流式输出演示

展示所有流式输出功能：
1. 段落级流式输出
2. 逐字符流式输出（打字效果）
3. 回调式流式处理
4. 工具调用 + 流式输出
5. 交互式聊天应用
6. 性能对比分析
"""

import time

from zipagent import (
    Agent,
    Runner,
    StreamEvent,
    StreamEventType,
    function_tool,
)


# 定义工具函数
@function_tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        time.sleep(1)
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"


@function_tool
def search_info(query: str) -> str:
    """搜索信息（模拟）"""
    knowledge_base = {
        "python": "Python是一种高级编程语言，由Guido van Rossum于1991年首次发布",
        "ai": "人工智能是计算机科学的一个分支，致力于创造能够执行通常需要人类智能的任务的系统",
        "机器学习": "机器学习是人工智能的一个子领域，使计算机能够在没有明确编程的情况下学习和改进",
        "深度学习": "深度学习是机器学习的一个子集，使用多层神经网络来建模和理解复杂的数据模式",
    }

    for key, value in knowledge_base.items():
        if key.lower() in query.lower():
            return value

    return f"未找到关于'{query}'的相关信息"


@function_tool
def get_current_time() -> str:
    """获取当前时间"""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 创建不同类型的Agent
def create_simple_agent() -> Agent:
    """创建简单对话Agent"""
    return Agent(
        name="ChatBot",
        instructions="你是一个友好的聊天机器人，请用自然流畅的语言回答问题。",
    )


def create_tool_agent() -> Agent:
    """创建带工具的Agent"""
    return Agent(
        name="Assistant",
        instructions="""你是一个智能助手。重要规则：
        1. 在使用任何工具前，先详细说明你的思考过程
        2. 解释为什么需要使用这个工具
        3. 然后再进行工具调用
        4. 每一步工具都需要详细说明
        5. 最后提供完整的答案""",
        tools=[calculate, search_info, get_current_time],
    )


# 演示函数
def demo_1_basic_stream():
    """演示1：基础段落级流式输出"""
    print("=" * 60)
    print("🌊 演示1：基础段落级流式输出")
    print("=" * 60)

    agent = create_simple_agent()
    question = "请介绍一下Python编程语言的特点"

    print(f"💬 问题：{question}\n")

    for event in Runner.run_stream(agent, question):
        if event.type == StreamEventType.QUESTION:
            print(f"📝 问题：{event.content}")
        elif event.type == StreamEventType.ANSWER:
            print(f"🤖 回答：{event.content}")
        elif event.type == StreamEventType.ERROR:
            print(f"❌ 错误：{event.error}")


def demo_2_char_stream():
    """演示2：逐字符流式输出"""
    print("\n" + "=" * 60)
    print("✨ 演示2：逐字符流式输出（打字效果）")
    print("=" * 60)

    agent = create_simple_agent()
    question = "什么是人工智能？请简要说明"

    print(f"💬 问题：{question}\n")
    print("🤖 回答：", end="", flush=True)

    for event in Runner.run_stream(agent, question):
        if event.type == StreamEventType.ANSWER_DELTA:
            print(event.content, end="", flush=True)
            time.sleep(0.03)  # 控制打字速度
        elif event.type == StreamEventType.ANSWER:
            print(f"\n\n✅ 回答完成！总字符数：{len(event.content)}")
            break


def demo_3_callback_stream():
    """演示3：回调式流式输出"""
    print("\n" + "=" * 60)
    print("📞 演示3:回调式流式输出")
    print("=" * 60)

    agent = create_simple_agent()
    question = "请解释机器学习的基本概念"

    print(f"💬 问题:{question}\n")

    # 定义流式处理器
    class StreamProcessor:
        def __init__(self):
            self.char_count = 0
            self.start_time = time.time()

        def handle_stream(self, event: StreamEvent):
            if event.type == StreamEventType.QUESTION:
                print(f"📝 处理问题：{event.content}")

            elif event.type == StreamEventType.ANSWER:
                print("🤖 AI回答：")
                # 模拟逐字符显示
                for char in event.content:
                    print(char, end="", flush=True)
                    self.char_count += 1
                    time.sleep(0.02)

                elapsed = time.time() - self.start_time
                print(
                    f"\n\n📊 统计：{self.char_count}字符，耗时{elapsed:.2f}秒"
                )

    processor = StreamProcessor()
    Runner.run(agent, question, stream_callback=processor.handle_stream)


def demo_4_tool_with_stream():
    """演示4：工具调用 + 逐字符流式输出"""
    print("\n" + "=" * 60)
    print("🔧 演示4：工具调用 + 逐字符流式输出")
    print("=" * 60)

    agent = create_tool_agent()
    question = (
        "现在几点了？然后帮我计算 现在的小时乘以5，将现在得到的小时数再乘以20"
    )

    print(f"💬 问题：{question}\n")

    current_thinking = ""
    current_answer = ""

    for event in Runner.run_stream(agent, question):
        if event.type == StreamEventType.QUESTION:
            print(f"📝 问题：{event.content}")

        elif event.type == StreamEventType.THINKING_DELTA:
            # 思考过程逐字符显示
            if not current_thinking:
                print("\n🧠 AI思考：", end="", flush=True)
            current_thinking += event.content
            print(event.content, end="", flush=True)
            time.sleep(0.02)

        elif event.type == StreamEventType.THINKING:
            if current_thinking:
                print("\n   💡 思考完成")
            current_thinking = ""

        elif event.type == StreamEventType.TOOL_CALL:
            print(f"\n🔧 调用工具：{event.tool_name}({event.tool_args})")

        elif event.type == StreamEventType.TOOL_RESULT:
            print(f"📊 工具结果：{event.tool_result}")

        elif event.type == StreamEventType.ANSWER_DELTA:
            # 最终回答逐字符显示
            if not current_answer:
                print("\n✅ 最终回答：", end="", flush=True)
            current_answer += event.content
            print(event.content, end="", flush=True)
            time.sleep(0.025)

        elif event.type == StreamEventType.ANSWER:
            print("\n\n🎉 任务完成！")
            break

        elif event.type == StreamEventType.ERROR:
            print(f"\n❌ 错误：{event.error}")
            break


def demo_5_interactive_chat():
    """演示5：交互式聊天应用"""
    print("\n" + "=" * 60)
    print("💬 演示5：交互式聊天（逐字符显示）")
    print("=" * 60)

    agent = create_tool_agent()
    print("🤖 智能助手已启动！输入 'quit' 退出")
    print("支持的功能：计算、信息搜索、时间查询")
    print("-" * 40)

    try:
        while True:
            user_input = input("\n👤 你：").strip()

            if user_input.lower() in ["quit", "exit", "退出", "q"]:
                print("👋 再见！")
                break

            if not user_input:
                continue

            print("🤖 助手：", end="", flush=True)

            # 使用逐字符流式输出
            for event in Runner.run_stream(agent, user_input):
                if event.type == StreamEventType.THINKING_DELTA:
                    # 思考过程用不同颜色显示（如果终端支持）
                    print(
                        f"\033[90m{event.content}\033[0m", end="", flush=True
                    )
                    time.sleep(0.01)

                elif event.type == StreamEventType.TOOL_CALL:
                    print(f"\n    🔧 [{event.tool_name}]", end="", flush=True)

                elif event.type == StreamEventType.ANSWER_DELTA:
                    print(event.content, end="", flush=True)
                    time.sleep(0.03)

                elif event.type == StreamEventType.ANSWER:
                    print()  # 换行
                    break

                elif event.type == StreamEventType.ERROR:
                    print(f"\n❌ {event.error}")
                    break

    except KeyboardInterrupt:
        print("\n\n👋 聊天已结束！")


def demo_6_performance_comparison():
    """演示6：性能对比"""
    print("\n" + "=" * 60)
    print("⚡ 演示6：不同流式方式性能对比")
    print("=" * 60)

    agent = create_simple_agent()
    question = "请详细介绍深度学习的发展历程和主要应用"

    print(f"💬 测试问题：{question}\n")

    # 1. 传统方式
    print("1️⃣ 传统方式（一次性显示）")
    start_time = time.time()
    result = Runner.run(agent, question)
    traditional_time = time.time() - start_time
    print(f"⏱️ 耗时：{traditional_time:.2f}秒，字符数：{len(result.content)}")

    # 2. 逐字符流式（仅计时，不实际显示）
    print("\n2️⃣ 段落级流式（立即显示完整段落）")
    start_time = time.time()
    for event in Runner.run_stream(agent, question):
        if event.type == StreamEventType.ANSWER:
            stream_time = time.time() - start_time
            print(f"⏱️ 耗时：{stream_time:.2f}秒，字符数：{len(event.content)}")
            break

    # 3. 逐字符流式（仅计时，不实际显示）
    print("\n3️⃣ 逐字符流式（打字效果）")
    start_time = time.time()
    char_count = 0
    for event in Runner.run_stream(agent, question):
        if event.type == StreamEventType.ANSWER_DELTA:
            char_count += len(event.content)
        elif event.type == StreamEventType.ANSWER:
            char_stream_time = time.time() - start_time
            print(f"⏱️ 耗时：{char_stream_time:.2f}秒，字符数：{char_count}")
            break

    print("\n📊 性能分析：")
    print(f"  • 传统方式：{traditional_time:.2f}秒（用户需要等待全部完成）")
    print(f"  • 段落流式：{stream_time:.2f}秒（用户立即看到结果）")
    print(f"  • 字符流式：{char_stream_time:.2f}秒（最佳用户体验）")


def main():
    """主演示函数"""
    print("🚀 ZipAgent 完整流式输出演示")
    print("本演示将展示所有流式输出功能和使用场景")

    try:
        # 基础演示
        # demo_1_basic_stream()
        # demo_2_char_stream()
        # demo_3_callback_stream()
        demo_4_tool_with_stream()

        # 性能对比
        # demo_6_performance_comparison()

        # 交互式演示（用户可选）
        print("\n" + "=" * 60)
        choice = input("🤔 是否要体验交互式聊天？(y/N): ").strip().lower()
        if choice in ["y", "yes", "是"]:
            demo_5_interactive_chat()

    except KeyboardInterrupt:
        print("\n\n⏹️ 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示出错：{e}")


if __name__ == "__main__":
    main()
