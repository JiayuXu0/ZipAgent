#!/usr/bin/env python3
"""LiteAgent 逐字符流式输出演示

展示如何实现类似 ChatGPT 的逐字显示效果
"""

import time

from liteagent import Agent, Runner, StreamEventType, function_tool


@function_tool
def get_current_time() -> str:
    """获取当前时间"""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def simulate_char_stream():
    """模拟逐字符流式输出效果"""
    print("🎭 模拟逐字符流式输出演示")
    print("=" * 50)

    # 创建一个简单的Agent（不使用工具，专注展示文本流式效果）
    agent = Agent(
        name="ChatBot",
        instructions="你是一个友好的聊天机器人，请用自然、流畅的语言回答问题。回答要有一定长度，这样可以更好地展示流式效果。",
    )

    # 模拟问题
    question = "请介绍一下人工智能的发展历程"
    print(f"🤔 问题: {question}\n")
    print("🤖 回答: ", end="", flush=True)

    # 使用普通流式，然后手动逐字符显示来模拟效果
    result_content = ""

    try:
        for event in Runner.run_stream(agent, question):
            if event.type == StreamEventType.ANSWER:
                # 完整答案，我们逐字符显示
                for char in event.content:
                    print(char, end="", flush=True)
                    time.sleep(0.03)  # 模拟打字效果
                    result_content = event.content
                break

        print("\n\n✅ 流式输出完成！")
        print(f"📊 总字符数: {len(result_content)}")

    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")


def demo_with_deltas():
    """演示增量事件处理"""
    print("\n" + "=" * 50)
    print("🔤 增量事件处理演示")
    print("=" * 50)

    agent = Agent(
        name="Assistant",
        instructions="简洁地回答问题",
        tools=[get_current_time],
    )

    question = "现在几点了？"
    print(f"📝 问题: {question}")

    current_content = ""

    try:
        # 使用逐字符流式方法（虽然目前实现还不完整）
        for event in Runner.run_stream_char(agent, question):
            if event.type == StreamEventType.QUESTION:
                print(f"📋 收到问题: {event.content}")

            elif event.type == StreamEventType.THINKING_DELTA:
                # 思考增量
                print("💭 思考中...", end="", flush=True)
                current_content += event.content
                print(event.content, end="", flush=True)

            elif event.type == StreamEventType.ANSWER_DELTA:
                # 回答增量
                if not current_content:
                    print("\n🤖 回答: ", end="", flush=True)
                current_content += event.content
                print(event.content, end="", flush=True)
                time.sleep(0.05)  # 稍微慢一点显示

            elif event.type == StreamEventType.TOOL_CALL:
                print(f"\n🔧 调用工具: {event.tool_name}")

            elif event.type == StreamEventType.TOOL_RESULT:
                print(f"📊 工具结果: {event.tool_result}")

            elif event.type == StreamEventType.ANSWER:
                print("\n✅ 完成!")
                break

            elif event.type == StreamEventType.ERROR:
                print(f"\n❌ 错误: {event.error}")
                break

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")


def demo_real_time_display():
    """演示实时显示效果"""
    print("\n" + "=" * 50)
    print("⚡ 实时显示效果演示")
    print("=" * 50)

    # 模拟真实的流式数据
    sample_response = """人工智能（Artificial Intelligence，AI）的发展历程可以分为几个重要阶段：

1950年代 - 起源阶段：艾伦·图灵提出"图灵测试"，标志着AI概念的正式诞生。

1960年代 - 早期探索：研发出第一批专家系统，如ELIZA聊天程序。

1980年代 - 专家系统兴起：基于规则的系统开始在商业领域应用。

1990年代 - 机器学习发展：神经网络和统计学习方法逐渐成熟。

2010年代 - 深度学习革命：深度神经网络在图像识别、语音识别等领域取得突破。

2020年代至今 - 大模型时代：GPT、BERT等大规模语言模型推动了AI的快速发展。

现在，AI正朝着更加通用、安全、可解释的方向发展。"""

    print("🤖 AI回答: ", end="", flush=True)

    for char in sample_response:
        print(char, end="", flush=True)
        if char in "。！？\n":
            time.sleep(0.2)  # 句子结尾稍微停顿
        else:
            time.sleep(0.02)  # 正常字符打字速度

    print("\n\n🎯 这就是逐字符流式输出的效果！")


def main():
    print("🌊 LiteAgent 逐字符流式输出演示")
    print()

    # 演示不同的流式效果
    simulate_char_stream()

    # 演示增量事件（目前实现还不完整）
    # demo_with_deltas()

    # 演示理想的实时显示效果
    demo_real_time_display()

    print("\n" + "=" * 50)
    print("📝 说明:")
    print("• 第一个演示使用现有的流式API + 手动延迟模拟打字效果")
    print("• 第二个演示展示了理想中的逐字符流式效果")
    print("• 真正的逐字符流式需要LLM API支持streaming模式")
    print("• 当前实现已经为此做好了架构准备")

    print("\n🚀 特性优势:")
    print("• 更好的用户体验 - 实时看到AI思考过程")
    print("• 减少等待焦虑 - 立即开始显示内容")
    print("• 更自然的交互 - 类似人类对话节奏")
    print("• 支持中断处理 - 可以随时停止生成")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见!")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
