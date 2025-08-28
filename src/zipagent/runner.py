"""Runner - Agent运行引擎"""

import json
from collections.abc import Callable, Generator

from .agent import Agent
from .context import Context
from .model import ModelResponse
from .stream import StreamEvent, StreamEventType


class RunResult:
    """运行结果"""

    def __init__(
        self,
        content: str,
        context: Context,
        success: bool = True,
        error: str | None = None,
    ):
        self.content = content
        self.context = context
        self.success = success
        self.error = error

    def __str__(self) -> str:
        return self.content

    def __repr__(self) -> str:
        return f"RunResult(content='{self.content[:50]}...', success={self.success})"


class Runner:
    """Agent运行器 - 核心执行引擎"""

    @staticmethod
    def run(
        agent: Agent,
        user_input: str,
        context: Context | None = None,
        max_turns: int = 10,
        stream_callback: Callable[[StreamEvent], None] | None = None,
    ) -> RunResult:
        """
        运行Agent处理用户输入（基于 run_stream 实现）

        Args:
            agent: 要运行的Agent
            user_input: 用户输入
            context: 上下文（可选，用于多轮对话）
            max_turns: 最大循环次数，防止无限循环
            stream_callback: 流式输出回调函数

        Returns:
            RunResult: 包含最终结果和上下文的对象
        """

        # 定义内部回调来处理流式事件
        def internal_callback(event: StreamEvent):
            # 如果有外部回调，先调用
            if stream_callback:
                stream_callback(event)
            else:
                # 默认的控制台输出
                if event.type == StreamEventType.QUESTION:
                    print(f"\n📝 问题：{event.content}")
                elif event.type == StreamEventType.THINKING:
                    print(f"\n💭 思考：{event.content}")
                elif event.type == StreamEventType.TOOL_CALL:
                    print(f"\n🔧 工具：{event.tool_name}({event.tool_args})")
                elif event.type == StreamEventType.TOOL_RESULT:
                    print(f"📊 工具结果：{event.tool_result}")
                elif event.type == StreamEventType.ANSWER:
                    print(f"\n✅ 回答：{event.content}")
                elif event.type == StreamEventType.ERROR:
                    print(f"\n❌ 错误：{event.error}")

        # 执行流式处理，收集最终结果
        try:
            # 使用生成器执行流式处理
            stream_generator = Runner.run_stream(
                agent, user_input, context, max_turns
            )

            # 遍历所有事件，并获取最终结果
            final_result = None
            try:
                while True:
                    event = next(stream_generator)
                    internal_callback(event)
            except StopIteration as e:
                final_result = e.value

            return final_result or RunResult(
                "", context or Context(), success=True
            )

        except Exception as e:
            # 处理其他异常
            error_msg = f"运行过程中出现错误: {e!s}"
            return RunResult(
                "", context or Context(), success=False, error=error_msg
            )

    @staticmethod
    def chat(agent: Agent, context: Context | None = None) -> Context:
        """
        启动交互式聊天模式

        Args:
            agent: 要使用的Agent
            context: 上下文（可选）

        Returns:
            Context: 最终的对话上下文
        """
        if context is None:
            context = Context()

        print(f"开始与 {agent.name} 对话，输入 'quit' 或 'exit' 退出")
        print("=" * 50)

        try:
            while True:
                user_input = input("\n你: ").strip()

                if user_input.lower() in ["quit", "exit", "退出", "q"]:
                    break

                if not user_input:
                    continue

                result = Runner.run(agent, user_input, context)

                if result.success:
                    print(f"\n{agent.name}: {result.content}")
                else:
                    print(f"\n[错误] {result.error}")

                print(f"[使用量] Tokens: {context.usage.total_tokens}")

        except KeyboardInterrupt:
            print("\n\n对话已结束")

        return context

    @staticmethod
    def run_stream(
        agent: Agent,
        user_input: str,
        context: Context | None = None,
        max_turns: int = 10,
    ) -> Generator[StreamEvent, None, RunResult]:
        """
        流式运行Agent处理用户输入（逐字符输出）

        Args:
            agent: 要运行的Agent
            user_input: 用户输入
            context: 上下文（可选，用于多轮对话）
            max_turns: 最大循环次数，防止无限循环

        Yields:
            StreamEvent: 流式事件（包含增量内容）

        Returns:
            RunResult: 最终运行结果
        """
        # 自动创建或使用现有 context
        if context is None:
            context = Context()
            # 记录 Agent 信息
            context.last_agent = agent.name

        # 如果是传入的 context，也更新 last_agent
        context.last_agent = agent.name

        try:
            # 添加系统消息（如果是新对话）
            if not context.messages:
                system_msg = agent.get_system_message()
                context.add_message(system_msg["role"], system_msg["content"])

            # 添加用户消息（新的一轮对话）
            context.add_message("user", user_input)
            context.turn_count += 1

            # 发送问题事件
            yield StreamEvent.question(user_input)

            # 预先缓存工具schema，避免在循环中重复计算
            tools_schema = agent.get_tools_schema() if agent.tools else None

            # 主执行循环
            for turn in range(max_turns):
                # 获取当前消息列表
                messages = context.get_messages_for_api()

                # 调用模型流式API
                assert agent.model is not None, (
                    "Agent model should not be None after initialization"
                )
                stream_generator = agent.model.generate_stream(messages, tools_schema)

                # 使用真正的流式处理
                full_content = ""
                response = None

                for stream_item in stream_generator:
                    if isinstance(stream_item, ModelResponse):
                        # 这是最终的ModelResponse
                        response = stream_item
                        break
                    elif (
                        hasattr(stream_item, "content")
                        and stream_item.content is not None
                    ):
                        # 这是StreamDelta，包含增量内容
                        delta_content = stream_item.content
                        full_content += delta_content

                        # 实时yield增量内容
                        yield StreamEvent.answer_delta(delta_content)

                # 处理完整响应
                if response:
                    # 累计使用量统计
                    context.usage.add(response.usage)

                    # 检查是否有工具调用
                    if response.tool_calls:
                        # 有工具调用，发送思考完成事件
                        yield StreamEvent.thinking(full_content)
                        # 将思考内容添加到上下文
                        context.add_message("assistant", full_content)
                    else:
                        # 没有工具调用，发送回答完成事件
                        yield StreamEvent.answer(full_content)
                        context.add_message("assistant", full_content)
                        return RunResult(full_content, context)

                # 如果有工具调用，执行工具
                if response and response.tool_calls:
                    has_tool_results = False

                    for tool_call in response.tool_calls:
                        # 解析工具调用
                        tool_name = tool_call["function"]["name"]

                        try:
                            arguments = json.loads(
                                tool_call["function"]["arguments"]
                            )
                        except json.JSONDecodeError:
                            # 如果JSON解析失败，尝试eval（简单处理）
                            try:
                                arguments = eval(
                                    tool_call["function"]["arguments"]
                                )
                            except Exception:
                                arguments = {}

                        # 查找并执行工具
                        tool = agent.find_tool(tool_name)
                        if tool:
                            # 发送工具调用事件
                            yield StreamEvent.tool_call(tool_name, arguments)

                            tool_result = tool.execute(arguments)

                            if tool_result.success:
                                # 发送工具结果事件
                                yield StreamEvent.create_tool_result(
                                    tool_name, tool_result.result
                                )
                                # 将工具调用和结果添加到上下文
                                context.add_tool_call(
                                    tool_name, arguments, tool_result.result
                                )
                                has_tool_results = True
                            else:
                                # 工具执行失败
                                error_msg = f"工具 {tool_name} 执行失败: {tool_result.error}"
                                yield StreamEvent.create_error(error_msg)
                                context.add_message("system", error_msg)
                        else:
                            # 找不到工具
                            error_msg = f"找不到工具: {tool_name}"
                            yield StreamEvent.create_error(error_msg)
                            context.add_message("system", error_msg)

                    # 如果有工具结果，继续下一轮
                    if has_tool_results:
                        continue

                # 如果既没有工具调用，也没有文本回复，说明出现了问题
                if not response or not response.tool_calls:
                    error_msg = "模型没有返回任何内容"
                    yield StreamEvent.create_error(error_msg)
                    return RunResult(
                        "", context, success=False, error=error_msg
                    )

            # 超过最大轮次
            error_msg = f"达到最大执行轮次 ({max_turns})，可能存在无限循环"
            yield StreamEvent.create_error(error_msg)
            return RunResult("", context, success=False, error=error_msg)

        except Exception as e:
            error_msg = f"运行过程中出现错误: {e!s}"
            yield StreamEvent.create_error(error_msg)
            return RunResult("", context, success=False, error=error_msg)
