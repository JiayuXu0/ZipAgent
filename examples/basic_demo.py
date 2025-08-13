#!/usr/bin/env python3
"""
LiteAgent 基础功能演示

展示核心功能：
1. 基础 Agent 创建和使用
2. function_tool 装饰器
3. Context 管理和多轮对话
4. 异常处理
"""

from datetime import datetime

from liteagent import Agent, Context, Runner, function_tool


# ========== 工具定义 ==========

@function_tool
def calculate(expression: str) -> str:
    """计算数学表达式
    
    Args:
        expression: 数学表达式，如 "2+2", "10*5"
    """
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"


@function_tool
def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@function_tool
def save_note(content: str) -> str:
    """保存笔记
    
    Args:
        content: 要保存的笔记内容
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"笔记已保存 [{timestamp}]: {content}"


# ========== 演示函数 ==========

def demo_1_basic_usage():
    """演示1: 基础用法"""
    print("=" * 50)
    print("🔧 演示1: 基础 Agent 用法")
    print("=" * 50)

    # 创建 Agent
    agent = Agent(
        name="MathAssistant",
        instructions="你是一个数学助手，可以帮助用户进行计算",
        tools=[calculate],
    )

    print("🤖 Agent 创建成功")
    print(f"工具数量: {len(agent.tools)}")
    
    # 简单对话
    print("\n💬 简单计算演示:")
    result = Runner.run(agent, "请计算 23 + 45")
    print(f"结果: {result.content}")


def demo_2_context_management():
    """演示2: Context 管理"""
    print("\n" + "=" * 50)
    print("📝 演示2: Context 管理和多轮对话")
    print("=" * 50)

    # 创建多功能 Agent
    agent = Agent(
        name="Assistant", 
        instructions="你是一个助手，可以计算、记笔记、查时间",
        tools=[calculate, save_note, get_current_time]
    )

    # 手动创建 Context 进行多轮对话
    context = Context()
    
    print("🔄 多轮对话演示:")
    
    # 第一轮
    result1 = Runner.run(agent, "现在几点了？", context=context)
    print(f"第1轮: {result1.content}")
    
    # 第二轮 (有上下文)
    result2 = Runner.run(agent, "帮我记录一下刚才的时间", context=context)
    print(f"第2轮: {result2.content}")
    
    # 第三轮
    result3 = Runner.run(agent, "计算一下 12 * 8", context=context)
    print(f"第3轮: {result3.content}")
    
    # 查看 Context 状态
    print(f"\n📊 Context 状态:")
    print(f"- 消息数量: {len(context.messages)}")
    print(f"- Token 使用: {context.usage}")


def demo_3_context_features():
    """演示3: Context 高级功能"""
    print("\n" + "=" * 50)
    print("⚙️ 演示3: Context 高级功能")
    print("=" * 50)

    agent = Agent(
        name="DataAgent",
        instructions="你是一个数据助手",
        tools=[calculate, save_note]
    )

    # 创建 Context 并设置自定义数据
    context = Context()
    context.set_data("user_name", "张三")
    context.set_data("session_id", "session_001")
    
    print("📋 Context 自定义数据:")
    print(f"- 用户名: {context.get_data('user_name')}")
    print(f"- 会话ID: {context.get_data('session_id')}")
    
    # 对话
    result = Runner.run(agent, "你好，帮我计算 100 / 4", context=context)
    print(f"\n💬 对话结果: {result.content}")
    
    # Context 克隆
    context_clone = context.clone()
    print(f"\n🔄 Context 克隆:")
    print(f"- 原始消息数: {len(context.messages)}")
    print(f"- 克隆消息数: {len(context_clone.messages)}")
    print(f"- 用户名保持: {context_clone.get_data('user_name')}")


def demo_4_error_handling():
    """演示4: 异常处理"""
    print("\n" + "=" * 50)
    print("⚠️ 演示4: 异常处理")
    print("=" * 50)

    @function_tool
    def divide(a: float, b: float) -> str:
        """除法运算，可能出错"""
        if b == 0:
            raise ValueError("除数不能为零")
        return f"{a} ÷ {b} = {a / b}"

    agent = Agent(
        name="SafeAgent",
        instructions="你是一个安全的计算助手",
        tools=[divide, calculate]
    )
    
    print("🧪 正常计算:")
    try:
        result = Runner.run(agent, "计算 10 除以 2")
        print(f"结果: {result.content}")
    except Exception as e:
        print(f"异常: {e}")
    
    print("\n🚨 异常计算:")
    try:
        result = Runner.run(agent, "计算 10 除以 0")
        print(f"结果: {result.content}")
    except Exception as e:
        print(f"捕获异常: {e}")
    
    print("\n🔧 错误表达式:")
    try:
        result = Runner.run(agent, "计算 2 +++ 3")
        print(f"结果: {result.content}")
    except Exception as e:
        print(f"捕获异常: {e}")


def main():
    """主演示函数"""
    print("🚀 LiteAgent 基础功能演示")
    print("展示核心功能：基础用法、Context管理、异常处理")
    
    try:
        demo_1_basic_usage()
        demo_2_context_management()
        demo_3_context_features()
        demo_4_error_handling()
        
        print("\n" + "=" * 50)
        print("✅ 所有演示完成！")
        print("💡 要了解更多功能:")
        print("  - 流式输出: python stream_demo.py")
        print("  - MCP工具: python mcp_demo.py")
        
    except KeyboardInterrupt:
        print("\n⏹️ 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")


if __name__ == "__main__":
    main()