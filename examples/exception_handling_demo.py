#!/usr/bin/env python3
"""LiteAgent 异常处理演示

展示如何使用结构化异常系统进行错误处理
"""

from liteagent import (
    Agent,
    LiteAgentError,
    MaxTurnsError,
    ModelError,
    Runner,
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
    function_tool,
)


# 定义一些会出错的工具
@function_tool
def divide(a: float, b: float) -> float:
    """除法运算"""
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b


@function_tool
def unstable_api() -> str:
    """模拟不稳定的API调用"""
    import random
    
    if random.random() < 0.5:
        raise ConnectionError("API 连接失败")
    return "API 调用成功"


def demo_tool_error():
    """演示工具错误处理"""
    print("=" * 60)
    print("🔧 工具错误处理演示")
    print("=" * 60)
    
    agent = Agent(
        name="Calculator",
        instructions="你是一个计算助手",
        tools=[divide]
    )
    
    # 测试除零错误
    try:
        result = Runner.run(agent, "计算 10 除以 0")
        print(f"结果: {result.content}")
    except ToolExecutionError as e:
        print(f"❌ 工具执行错误: {e}")
        print(f"   - 工具名: {e.details['tool_name']}")
        print(f"   - 参数: {e.details['arguments']}")
        print(f"   - 原始错误: {e.original_error}")
    except LiteAgentError as e:
        print(f"❌ Agent错误: {e}")


def demo_max_turns_error():
    """演示最大轮次错误"""
    print("\n" + "=" * 60)
    print("🔄 最大轮次错误演示")
    print("=" * 60)
    
    @function_tool
    def recursive_tool() -> str:
        """一个会导致无限循环的工具"""
        return "请再次调用这个工具"
    
    agent = Agent(
        name="RecursiveAgent",
        instructions="总是调用可用的工具",
        tools=[recursive_tool]
    )
    
    try:
        result = Runner.run(agent, "开始", max_turns=3)
    except MaxTurnsError as e:
        print(f"❌ 达到最大轮次: {e}")
        print(f"   - 最大轮次: {e.details['max_turns']}")


def demo_tool_not_found():
    """演示工具未找到错误"""
    print("\n" + "=" * 60)
    print("🔍 工具未找到错误演示")
    print("=" * 60)
    
    agent = Agent(
        name="LimitedAgent",
        instructions="你可以调用 search_web 工具搜索信息",
        tools=[]  # 没有提供任何工具
    )
    
    try:
        # Agent可能会尝试调用不存在的工具
        result = Runner.run(agent, "搜索最新的AI新闻")
        print(f"结果: {result.content}")
    except ToolNotFoundError as e:
        print(f"❌ 工具未找到: {e}")
        print(f"   - 尝试调用的工具: {e.details['tool_name']}")


def demo_model_error():
    """演示模型错误处理"""
    print("\n" + "=" * 60)
    print("🤖 模型错误处理演示")
    print("=" * 60)
    
    from liteagent import OpenAIModel
    
    # 使用无效的API key
    try:
        model = OpenAIModel(
            model="gpt-3.5-turbo",
            api_key="invalid_key",
            base_url="https://api.openai.com/v1"
        )
        
        agent = Agent(
            name="TestAgent",
            instructions="你是一个测试助手",
            model=model
        )
        
        result = Runner.run(agent, "Hello")
    except ModelError as e:
        print(f"❌ 模型错误: {e}")
        if e.details.get('status_code'):
            print(f"   - 状态码: {e.details['status_code']}")
        if e.details.get('model_name'):
            print(f"   - 模型: {e.details['model_name']}")


def demo_graceful_error_handling():
    """演示优雅的错误处理和降级策略"""
    print("\n" + "=" * 60)
    print("✨ 优雅错误处理演示")
    print("=" * 60)
    
    agent = Agent(
        name="RobustAgent",
        instructions="尽力帮助用户，如果工具失败就用文字说明",
        tools=[unstable_api]
    )
    
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            print(f"\n尝试 {attempt + 1}/{max_retries}...")
            result = Runner.run(agent, "调用API获取数据")
            print(f"✅ 成功: {result.content}")
            break
        except ToolExecutionError as e:
            print(f"⚠️ 工具执行失败: {e.original_error}")
            if attempt < max_retries - 1:
                print("   重试中...")
            else:
                print("❌ 所有重试都失败了")
                # 降级策略：不使用工具
                agent_without_tools = Agent(
                    name="FallbackAgent",
                    instructions="直接回答，不要使用工具"
                )
                result = Runner.run(agent_without_tools, "API暂时不可用，请说明情况")
                print(f"📝 降级响应: {result.content}")
        except LiteAgentError as e:
            print(f"❌ 其他错误: {e}")
            break


def demo_custom_error_handler():
    """演示自定义错误处理器"""
    print("\n" + "=" * 60)
    print("🎯 自定义错误处理器演示")
    print("=" * 60)
    
    class ErrorHandler:
        """错误处理器，可以记录、报警、重试等"""
        
        def __init__(self):
            self.error_log = []
        
        def handle(self, error: LiteAgentError):
            """处理错误"""
            # 记录错误
            self.error_log.append({
                "type": type(error).__name__,
                "message": str(error),
                "details": error.details
            })
            
            # 根据错误类型采取不同策略
            if isinstance(error, ToolExecutionError):
                print(f"🔧 记录工具错误: {error.details['tool_name']}")
                # 可以发送告警、记录指标等
            elif isinstance(error, MaxTurnsError):
                print(f"🔄 记录循环错误: 轮次={error.details['max_turns']}")
            elif isinstance(error, ModelError):
                print(f"🤖 记录模型错误: {error.message}")
            else:
                print(f"❓ 记录未知错误: {error}")
        
        def get_statistics(self):
            """获取错误统计"""
            from collections import Counter
            error_types = Counter(e["type"] for e in self.error_log)
            return dict(error_types)
    
    # 使用错误处理器
    handler = ErrorHandler()
    agent = Agent(
        name="TestAgent",
        instructions="测试各种错误",
        tools=[divide, unstable_api]
    )
    
    # 测试多个场景
    test_cases = [
        "计算 10 除以 0",
        "调用API",
        "计算 100 除以 5",
    ]
    
    for test in test_cases:
        try:
            print(f"\n测试: {test}")
            result = Runner.run(agent, test)
            print(f"✅ 成功: {result.content}")
        except LiteAgentError as e:
            handler.handle(e)
    
    # 显示错误统计
    stats = handler.get_statistics()
    if stats:
        print(f"\n📊 错误统计: {stats}")


def main():
    """主演示程序"""
    print("🚀 LiteAgent 异常处理系统演示")
    print("\n本演示展示如何使用结构化异常进行错误处理")
    
    try:
        # 演示各种错误场景
        demo_tool_error()
        demo_max_turns_error()
        # demo_tool_not_found()  # 这个需要模型配合
        # demo_model_error()  # 这个需要真实的API调用
        demo_graceful_error_handling()
        demo_custom_error_handler()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 未预期的错误: {e}")
    
    print("\n" + "=" * 60)
    print("📝 总结：")
    print("1. 结构化异常提供了丰富的错误上下文")
    print("2. 用户可以根据异常类型采取不同的处理策略")
    print("3. 异常系统支持优雅降级和错误恢复")
    print("4. 便于监控、日志记录和调试")


if __name__ == "__main__":
    main()