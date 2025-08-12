#!/usr/bin/env python3
"""
Context 管理功能演示

展示 LiteAgent 的自动对话记录和 Context 管理功能：
1. 自动创建和管理 Context
2. 连续对话（Context 复用）
3. 多 Agent 协作（Context 共享）
4. 对话历史查询和导出
"""

from datetime import datetime

from liteagent import Agent, Context, Runner, function_tool

# ========== 工具定义 ==========


@function_tool
def calculate(expression: str) -> str:
    """计算数学表达式

    Args:
        expression: 要计算的数学表达式，如 "2+2", "10*5"
    """
    try:
        # 注意：实际应用中应该使用安全的表达式解析器
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{e}"


@function_tool
def save_note(content: str) -> str:
    """保存笔记

    Args:
        content: 要保存的笔记内容
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"笔记已保存 [{timestamp}]: {content}"


@function_tool
def search_web(query: str) -> str:
    """模拟网络搜索

    Args:
        query: 搜索关键词
    """
    # 模拟搜索结果
    results = {
        "Python": "Python 是一种高级编程语言，以简洁易读著称",
        "AI": "人工智能是计算机科学的一个分支，致力于创建智能机器",
        "天气": "今天晴天，温度 20-25°C，适合外出",
    }

    for key, value in results.items():
        if key.lower() in query.lower():
            return f"搜索结果：{value}"

    return f"搜索 '{query}' 没有找到相关结果"


# ========== 场景 1: 基础使用 - 自动 Context 管理 ==========


def demo_basic_usage():
    """演示基础使用 - 自动创建和管理 Context"""
    print("\n" + "=" * 60)
    print("📝 场景 1: 基础使用 - 自动 Context 管理")
    print("=" * 60)

    # 创建 Agent
    agent = Agent(
        name="Assistant",
        instructions="你是一个智能助手，可以进行计算、保存笔记和搜索信息",
        tools=[calculate, save_note, search_web],
    )

    # 第一次调用 - Runner 自动创建 Context
    print("\n1️⃣ 第一次调用（自动创建 Context）:")
    result = Runner.run(agent, "你好，请记住我叫小明")

    # 获取自动创建的 Context
    ctx = result.context
    print("\n📊 Context 信息:")
    print(f"  - Context ID: {ctx.context_id}")
    print(f"  - 创建时间: {ctx.created_at}")
    print(f"  - 最后使用的 Agent: {ctx.last_agent}")
    print(f"  - 对话轮数: {ctx.turn_count}")
    print(f"  - 消息数量: {len(ctx.messages)}")

    # 查看摘要
    print("\n📋 Context 摘要:")
    summary = ctx.get_summary()
    for key, value in summary.items():
        print(f"  - {key}: {value}")

    return ctx


# ========== 场景 2: 连续对话 ==========


def demo_continuous_conversation(ctx: Context = None):
    """演示连续对话 - Context 复用"""
    print("\n" + "=" * 60)
    print("💬 场景 2: 连续对话 - Context 复用")
    print("=" * 60)

    agent = Agent(
        name="MathTutor",
        instructions="你是一个数学老师，帮助学生学习数学",
        tools=[calculate, save_note],
    )

    # 如果没有传入 context，创建新的
    if ctx is None:
        print("\n1️⃣ 开始新对话:")
        result = Runner.run(agent, "我想学习数学")
        ctx = result.context

    # 连续对话 - 传入相同的 Context
    print("\n2️⃣ 第二轮对话（复用 Context）:")
    result = Runner.run(agent, "帮我计算 15 * 23", context=ctx)
    print(f"  - 当前轮数: {ctx.turn_count}")
    print(f"  - 消息总数: {len(ctx.messages)}")

    print("\n3️⃣ 第三轮对话（继续复用）:")
    result = Runner.run(agent, "再算一个：99 + 88", context=ctx)
    print(f"  - 当前轮数: {ctx.turn_count}")
    print(f"  - 消息总数: {len(ctx.messages)}")

    print("\n4️⃣ 第四轮对话（验证记忆）:")
    result = Runner.run(
        agent, "刚才我们算了哪些题目？要回答100字", context=ctx
    )
    print(f"  - 当前轮数: {ctx.turn_count}")
    print(f"  - 消息总数: {len(ctx.messages)}")

    # 展示对话历史
    print("\n📜 对话历史片段:")
    for i, msg in enumerate(ctx.messages[-6:]):  # 显示最后6条消息
        role = msg.get("role")
        content = str(msg.get("content", ""))[:100]
        if content:
            print(f"  {i + 1}. [{role}]: {content}...")

    return ctx


# ========== 场景 3: 多 Agent 协作 ==========


def demo_multi_agent_collaboration():
    """演示多 Agent 协作 - Context 共享"""
    print("\n" + "=" * 60)
    print("🤝 场景 3: 多 Agent 协作 - Context 共享")
    print("=" * 60)

    # 创建三个不同角色的 Agent
    analyst = Agent(
        name="RequirementAnalyst",
        instructions="你是需求分析师，负责理解和分析用户需求",
        tools=[save_note],
    )

    designer = Agent(
        name="SystemDesigner",
        instructions="你是系统设计师，根据需求设计技术方案",
        tools=[save_note],
    )

    coder = Agent(
        name="Programmer",
        instructions="你是程序员，根据设计方案编写代码",
        tools=[save_note],
    )

    # Step 1: 需求分析师处理
    print("\n👤 需求分析师处理:")
    result1 = Runner.run(analyst, "用户需要一个待办事项管理应用")
    ctx_analyst = result1.context
    print(f"  - Agent: {ctx_analyst.last_agent}")
    print(f"  - Context ID: {ctx_analyst.context_id[:8]}...")

    # Step 2: 设计师接手（克隆 Context）
    print("\n👤 系统设计师接手:")
    ctx_designer = ctx_analyst.clone()  # 克隆 Context 保持独立
    result2 = Runner.run(
        designer, "基于上述需求，设计系统架构", context=ctx_designer
    )
    print(f"  - Agent: {ctx_designer.last_agent}")
    print(f"  - Context ID: {ctx_designer.context_id[:8]}...")
    print(
        f"  - 共享同一会话: {ctx_analyst.context_id == ctx_designer.context_id}"
    )

    # Step 3: 程序员实现（再次克隆）
    print("\n👤 程序员实现:")
    ctx_coder = ctx_designer.clone()
    result3 = Runner.run(
        coder, "根据设计方案，给出核心代码结构", context=ctx_coder
    )
    print(f"  - Agent: {ctx_coder.last_agent}")
    print(f"  - Context ID: {ctx_coder.context_id[:8]}...")

    # 对比三个 Context
    print("\n📊 Context 对比:")
    print(f"  分析师 Context: {len(ctx_analyst.messages)} 条消息")
    print(f"  设计师 Context: {len(ctx_designer.messages)} 条消息")
    print(f"  程序员 Context: {len(ctx_coder.messages)} 条消息")
    print(f"  都属于同一会话: {ctx_analyst.context_id}")

    return ctx_analyst, ctx_designer, ctx_coder


# ========== 场景 4: Context 导出和分析 ==========


def demo_context_export(ctx: Context):
    """演示 Context 导出和分析"""
    print("\n" + "=" * 60)
    print("💾 场景 4: Context 导出和分析")
    print("=" * 60)

    # 获取摘要
    summary = ctx.get_summary()
    print("\n📊 会话统计:")
    print(f"  - 会话 ID: {summary['context_id']}")
    print(f"  - 创建时间: {summary['created_at']}")
    print(f"  - 最后 Agent: {summary['last_agent']}")
    print(f"  - 对话轮数: {summary['turn_count']}")
    print(f"  - 消息总数: {summary['message_count']}")
    print(f"  - Token 使用: {summary['total_tokens']}")

    # 导出为 JSON（示例）
    export_data = {
        "session": summary,
        "messages": [
            {
                "role": msg.get("role"),
                "content": str(msg.get("content", ""))[:200],  # 截断长内容
                "timestamp": datetime.now().isoformat(),
            }
            for msg in ctx.messages
        ],
    }

    # 保存到文件（可选）
    filename = f"conversation_{ctx.context_id[:8]}.json"
    print("\n💾 导出数据结构示例:")
    print(f"  - 文件名: {filename}")
    print(f"  - 包含 {len(export_data['messages'])} 条消息")

    # 分析对话模式
    print("\n📈 对话模式分析:")
    role_counts = {}
    for msg in ctx.messages:
        role = msg.get("role")
        role_counts[role] = role_counts.get(role, 0) + 1

    for role, count in role_counts.items():
        print(f"  - {role}: {count} 条消息")

    # 识别工具调用
    tool_calls = [
        msg
        for msg in ctx.messages
        if msg.get("tool_calls") or msg.get("role") == "tool"
    ]
    print(f"\n🔧 工具调用: {len(tool_calls)} 次")

    return export_data


# ========== 场景 5: 高级用法 ==========


def demo_advanced_features():
    """演示高级功能"""
    print("\n" + "=" * 60)
    print("🚀 场景 5: 高级功能演示")
    print("=" * 60)

    # 1. 自定义 Context 数据存储
    print("\n1️⃣ 自定义数据存储:")
    ctx = Context()
    ctx.set_data("user_preferences", {"theme": "dark", "language": "zh"})
    ctx.set_data("session_type", "technical_support")

    print(f"  存储的数据: {ctx.data}")
    print(f"  获取特定数据: {ctx.get_data('user_preferences')}")

    # 2. Context 清空和重置
    print("\n2️⃣ Context 清空:")
    ctx.add_message("user", "测试消息1")
    ctx.add_message("assistant", "测试回复1")
    ctx.turn_count = 2

    print(f"  清空前: {len(ctx.messages)} 条消息, {ctx.turn_count} 轮对话")
    ctx.clear_messages()
    print(f"  清空后: {len(ctx.messages)} 条消息, {ctx.turn_count} 轮对话")
    print(f"  Context ID 保持不变: {ctx.context_id}")

    # 3. 比较原始和克隆的 Context
    print("\n3️⃣ Context 克隆深度测试:")
    original = Context()
    original.add_message("user", "原始消息")
    original.set_data("test", {"nested": "value"})

    cloned = original.clone()
    cloned.add_message("user", "克隆后添加")
    cloned.data["test"]["nested"] = "modified"

    print(f"  原始 Context 消息数: {len(original.messages)}")
    print(f"  克隆 Context 消息数: {len(cloned.messages)}")
    print(f"  原始数据未受影响: {original.data}")
    print(f"  克隆数据已修改: {cloned.data}")

    return ctx


# ========== 主函数 ==========


def main():
    """运行所有演示"""
    print("\n" + "🎯" * 30)
    print("       LiteAgent Context 管理功能演示")
    print("🎯" * 30)

    # 场景 1: 基础使用
    # ctx = demo_basic_usage()

    # # 场景 2: 连续对话
    ctx = demo_continuous_conversation()

    # # 场景 3: 多 Agent 协作
    # ctx_analyst, ctx_designer, ctx_coder = demo_multi_agent_collaboration()

    # # 场景 4: 导出和分析
    # export_data = demo_context_export(ctx)

    # # 场景 5: 高级功能
    # demo_advanced_features()

    # # 总结
    # print("\n" + "="*60)
    # print("✅ 演示完成！")
    # print("="*60)
    # print("\n关键特性总结:")
    # print("1. 🔄 自动 Context 管理 - 无需手动创建")
    # print("2. 💬 连续对话支持 - Context 复用保持上下文")
    # print("3. 🤝 多 Agent 协作 - Context 克隆实现共享")
    # print("4. 📊 会话分析 - 摘要、统计、导出")
    # print("5. 🎯 零配置 - 默认启用，向后兼容")

    # print("\n💡 提示:")
    # print("- Context 会自动记录所有对话")
    # print("- 使用 clone() 在 Agent 间安全共享")
    # print("- 通过 get_summary() 快速了解会话状态")
    # print("- Context ID 是会话的唯一标识")


if __name__ == "__main__":
    main()
