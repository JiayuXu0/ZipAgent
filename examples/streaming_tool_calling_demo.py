#!/usr/bin/env python3
"""
ZipAgent 流式工具调用演示

测试流式响应中的工具调用，包括：
1. 流式思考过程
2. 实时工具调用
3. 工具结果处理
4. 多轮工具调用

使用本地 DeepSeek-V3 API 进行测试
"""

import json
import random
import time
from datetime import datetime

from zipagent import Agent, Context, OpenAIModel, Runner, function_tool

# ================== 工具定义 ==================


@function_tool
def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@function_tool
def calculate(expression: str) -> str:
    """计算数学表达式

    Args:
        expression: 数学表达式，如 "2+3*4" 或 "sqrt(16)"
    """
    try:
        # 安全的数学计算
        import math

        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({"abs": abs, "round": round})

        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"


@function_tool
def search_weather(city: str) -> str:
    """查询天气信息（模拟）

    Args:
        city: 城市名称
    """
    # 模拟API调用延迟
    time.sleep(0.5)

    # 模拟天气数据
    weathers = ["晴天", "多云", "小雨", "阴天"]
    temp = random.randint(15, 30)
    weather = random.choice(weathers)

    return f"{city}今天{weather}，温度{temp}°C"


@function_tool
def create_todo_item(task: str, priority: str = "medium") -> str:
    """创建待办事项

    Args:
        task: 任务描述
        priority: 优先级 (low/medium/high)
    """
    todo_id = random.randint(1000, 9999)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"✅ 已创建待办事项 #{todo_id}: {task} (优先级: {priority}, 创建时间: {timestamp})"


@function_tool
def get_system_info() -> str:
    """获取系统信息"""
    import platform

    import psutil

    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()

    return json.dumps(
        {
            "操作系统": platform.system(),
            "Python版本": platform.python_version(),
            "CPU使用率": f"{cpu_percent}%",
            "内存使用率": f"{memory.percent}%",
        },
        ensure_ascii=False,
        indent=2,
    )


# ================== 流式事件处理 ==================


class StreamingEventHandler:
    """流式事件处理器，用于实时显示不同类型的事件"""

    def __init__(self):
        self.event_count = 0
        self.current_thinking = ""
        self.current_answer = ""

    def handle_event(self, event):
        """处理流式事件"""
        self.event_count += 1

        if event.type.value == "question":
            print(f"\n🤔 用户问题: {event.content}")
            print("-" * 80)

        elif event.type.value == "thinking_delta":
            # 实时显示思考过程的增量
            self.current_thinking += event.content
            print(event.content, end="", flush=True)

        elif event.type.value == "thinking":
            # 思考完成
            print(f"\n💭 思考完成 (共{len(event.content)}字符)")
            print("-" * 80)

        elif event.type.value == "tool_call":
            # 工具调用
            print(f"\n🔧 调用工具: {event.tool_name}")
            print(
                f"📋 参数: {json.dumps(event.tool_args, ensure_ascii=False)}"
            )

        elif event.type.value == "tool_result":
            # 工具结果
            print(f"📊 工具结果: {event.tool_result}")
            print("-" * 80)

        elif event.type.value == "answer_delta":
            # 实时显示答案增量
            self.current_answer += event.content
            print(event.content, end="", flush=True)

        elif event.type.value == "answer":
            # 答案完成
            print(f"\n\n✅ 回答完成 (共{len(event.content)}字符)")
            print("-" * 80)

        elif event.type.value == "error":
            # 错误处理
            print(f"\n❌ 错误: {event.error}")
            print("-" * 80)


# ================== 主要演示函数 ==================


def create_agent():
    """创建配置好的Agent"""

    # 使用 SiliconFlow DeepSeek-V3.1 API
    model = OpenAIModel(
        model="deepseek-ai/DeepSeek-V3.1",
        api_key="sk-xxxxxx",
        base_url="https://api.siliconflow.cn/v1",
        temperature=0.7,
        max_tokens=2000,
    )

    # 创建Agent，包含多种工具
    agent = Agent(
        name="StreamingToolAgent",
        instructions="""你是一个智能助手，能够使用多种工具来帮助用户。

当你需要使用工具时，请先简要说明你的思考过程，然后调用相应的工具。
如果需要多个工具配合完成任务，请按逻辑顺序依次调用。

可用工具：
- get_current_time: 获取当前时间
- calculate: 进行数学计算
- search_weather: 查询天气信息
- create_todo_item: 创建待办事项
- get_system_info: 获取系统信息

请用中文回答，语言自然友好。""",
        model=model,
        tools=[
            get_current_time,
            calculate,
            search_weather,
            create_todo_item,
            get_system_info,
        ],
        use_system_prompt=True,
    )

    return agent


def test_simple_tool_call():
    """测试简单的单工具调用"""
    print("🧪 测试1: 简单工具调用")
    print("=" * 100)

    agent = create_agent()
    handler = StreamingEventHandler()

    # 使用流式处理
    for event in Runner.run_stream(agent, "现在几点了？"):
        handler.handle_event(event)

    print("\n" + "=" * 100)


def test_calculation_tool():
    """测试数学计算工具"""
    print("\n🧪 测试2: 数学计算工具")
    print("=" * 100)

    agent = create_agent()
    handler = StreamingEventHandler()

    for event in Runner.run_stream(agent, "帮我计算 (25 + 35) * 2 的结果"):
        handler.handle_event(event)

    print("\n" + "=" * 100)


def test_multiple_tool_calls():
    """测试多工具调用"""
    print("\n🧪 测试3: 多工具调用")
    print("=" * 100)

    agent = create_agent()
    handler = StreamingEventHandler()

    for event in Runner.run_stream(
        agent,
        "帮我查一下北京的天气，然后创建一个高优先级的待办事项：根据天气准备合适的衣服",
    ):
        handler.handle_event(event)

    print("\n" + "=" * 100)


def test_complex_workflow():
    """测试复杂工作流"""
    print("\n🧪 测试4: 复杂工作流")
    print("=" * 100)

    agent = create_agent()
    handler = StreamingEventHandler()
    context = Context()

    # 第一轮：系统信息查询
    print("🔄 第一轮对话:")
    for event in Runner.run_stream(
        agent, "先帮我看看系统信息，然后告诉我现在时间", context
    ):
        handler.handle_event(event)

    print("\n🔄 第二轮对话:")
    # 第二轮：基于前面信息的进一步操作
    for event in Runner.run_stream(
        agent,
        "基于刚才的系统信息，如果CPU使用率超过50%，请创建一个待办事项提醒我优化性能",
        context,
    ):
        handler.handle_event(event)

    print("\n" + "=" * 100)


def test_error_handling():
    """测试错误处理"""
    print("\n🧪 测试5: 错误处理")
    print("=" * 100)

    agent = create_agent()
    handler = StreamingEventHandler()

    for event in Runner.run_stream(agent, "帮我计算 1/0 的结果"):
        handler.handle_event(event)

    print("\n" + "=" * 100)


def interactive_mode():
    """交互模式"""
    print("\n🎮 进入交互模式 (输入 'quit' 退出)")
    print("=" * 100)

    agent = create_agent()
    context = Context()

    while True:
        try:
            user_input = input("\n你: ").strip()

            if user_input.lower() in ["quit", "exit", "退出", "q"]:
                print("👋 再见！")
                break

            if not user_input:
                continue

            print(f"\n🤖 {agent.name}:")
            handler = StreamingEventHandler()

            for event in Runner.run_stream(agent, user_input, context):
                handler.handle_event(event)

        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 出现错误: {e}")


def main():
    """主函数"""
    print("🚀 ZipAgent 流式工具调用演示")
    print("=" * 100)
    print("本演示将测试不同场景下的流式工具调用：")
    print("- 简单工具调用")
    print("- 数学计算")
    print("- 多工具协作")
    print("- 复杂工作流")
    print("- 错误处理")
    print("- 交互模式")
    print("=" * 100)

    try:
        # 运行各种测试
        test_simple_tool_call()
        test_calculation_tool()
        test_multiple_tool_calls()
        test_complex_workflow()
        test_error_handling()

        # 询问是否进入交互模式
        choice = input("\n是否进入交互模式? (y/N): ").strip().lower()
        if choice in ["y", "yes", "是"]:
            interactive_mode()

    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback

        traceback.print_exc()

    print("\n🎉 演示完成！")


if __name__ == "__main__":
    main()
