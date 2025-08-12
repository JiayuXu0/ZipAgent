"""Runner - Agent运行引擎"""

import json
from typing import Optional

from .agent import Agent
from .context import Context


class RunResult:
    """运行结果"""

    def __init__(
        self,
        content: str,
        context: Context,
        success: bool = True,
        error: Optional[str] = None,
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
        context: Optional[Context] = None,
        max_turns: int = 10,
    ) -> RunResult:
        """
        运行Agent处理用户输入

        Args:
            agent: 要运行的Agent
            user_input: 用户输入
            context: 上下文（可选，用于多轮对话）
            max_turns: 最大循环次数，防止无限循环

        Returns:
            RunResult: 包含最终结果和上下文的对象
        """
        if context is None:
            context = Context()

        try:
            # 添加系统消息（如果是新对话）
            if not context.messages:
                system_msg = agent.get_system_message()
                context.add_message(system_msg["role"], system_msg["content"])

            # 添加用户消息
            context.add_message("user", user_input)

            # 显示问题
            print(f"\n📝 问题：{user_input}")

            # 主执行循环
            for turn in range(max_turns):
                # 获取当前消息列表
                messages = context.get_messages_for_api()

                # 获取可用工具
                tools = agent.get_tools_schema() if agent.tools else None

                # 调用模型
                assert agent.model is not None, (
                    "Agent model should not be None after initialization"
                )
                response = agent.model.generate(messages, tools)

                # 累计使用量统计
                context.usage.add(response.usage)

                # 如果有思考内容（content），先处理
                if response.content:
                    # 只有当同时有工具调用时，才将content显示为思考过程
                    if response.tool_calls:
                        # 显示思考内容
                        print(f"\n💭 思考：{response.content.strip()}")
                        # 将思考内容添加到上下文
                        context.add_message("assistant", response.content)
                    else:
                        # 没有工具调用，这就是最终结果
                        context.add_message("assistant", response.content)
                        print(f"\n✅ 回答：{response.content.strip()}")
                        return RunResult(response.content, context)

                # 如果有工具调用，执行工具
                if response.tool_calls:
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
                            print(f"\n🔧 工具：{tool_name}({arguments})")
                            tool_result = tool.execute(arguments)

                            if tool_result.success:
                                print(f"📊 工具结果：{tool_result.result}")
                                # 将工具调用和结果添加到上下文
                                context.add_tool_call(
                                    tool_name, arguments, tool_result.result
                                )
                                has_tool_results = True
                            else:
                                # 工具执行失败
                                error_msg = f"工具 {tool_name} 执行失败: {tool_result.error}"
                                print(f"❌ 工具错误：{error_msg}")
                                context.add_message("system", error_msg)
                        else:
                            # 找不到工具
                            error_msg = f"找不到工具: {tool_name}"
                            print(f"❌ 错误：{error_msg}")
                            context.add_message("system", error_msg)

                    # 如果有工具结果，继续下一轮
                    if has_tool_results:
                        continue

                # 如果既没有工具调用，也没有文本回复，说明出现了问题
                if not response.tool_calls:
                    error_msg = "模型没有返回任何内容"
                    return RunResult(
                        "", context, success=False, error=error_msg
                    )

            # 超过最大轮次
            error_msg = f"达到最大执行轮次 ({max_turns})，可能存在无限循环"
            return RunResult("", context, success=False, error=error_msg)

        except Exception as e:
            error_msg = f"运行过程中出现错误: {e!s}"
            return RunResult("", context, success=False, error=error_msg)

    @staticmethod
    def chat(agent: Agent, context: Optional[Context] = None) -> Context:
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
