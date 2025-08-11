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
        thinking_tool_mode: Optional[bool] = None,
    ) -> RunResult:
        """
        运行Agent处理用户输入

        Args:
            agent: 要运行的Agent
            user_input: 用户输入
            context: 上下文（可选，用于多轮对话）
            max_turns: 最大循环次数，防止无限循环
            thinking_tool_mode: 是否启用思考模式，覆盖Agent的设置

        Returns:
            RunResult: 包含最终结果和上下文的对象
        """
        if context is None:
            context = Context()

        # 临时修改Agent的thinking_tool_mode设置（如果指定了覆盖）
        original_thinking_mode = agent.thinking_tool_mode
        if thinking_tool_mode is not None:
            agent.thinking_tool_mode = thinking_tool_mode

        try:
            # 添加系统消息（如果是新对话）
            if not context.messages:
                system_msg = agent.get_system_message()
                context.add_message(system_msg["role"], system_msg["content"])

            # 添加用户消息
            context.add_message("user", user_input)

            # 主执行循环
            thinking_content = ""  # 保存thinking内容

            for turn in range(max_turns):
                # 获取当前消息列表
                messages = context.get_messages_for_api()

                # 获取可用工具
                tools = agent.get_tools_schema() if agent.tools else None

                # 调用模型
                assert agent.model is not None, (
                    "Agent model should not be None after initialization"
                )
                # 在思考模式下不使用原生工具调用，让AI输出自定义格式
                use_native_tools = not agent.thinking_tool_mode
                response = agent.model.generate(messages, tools, use_native_tools)

                # 累计使用量统计
                context.usage.add(response.usage)

                # 在thinking模式下保存第一轮的thinking内容
                if agent.thinking_tool_mode and turn == 0 and response.content:
                    if "<thinking>" in response.content:
                        thinking_content = response.content

                # 如果有工具调用，执行工具
                if response.tool_calls:
                    has_tool_results = False
                    
                    # 显示思考过程（如果是thinking模式）
                    if agent.thinking_tool_mode and turn == 0 and response.content:
                        # 在thinking模式下，第一轮的response.content包含了思考内容（已去除XML标签）
                        thinking_lines = response.content.strip().split('\n')
                        if thinking_lines:
                            print(f"💭 AI分析思考:")
                            for line in thinking_lines:
                                if line.strip():
                                    print(f"   {line.strip()}")
                            print()

                    for i, tool_call in enumerate(response.tool_calls, 1):
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
                            # 显示工具调用
                            print(f"🔧 步骤 {i}: 调用工具 {tool_name}")
                            print(f"   参数: {arguments}")
                            
                            tool_result = tool.execute(arguments)

                            if tool_result.success:
                                print(f"   ✅ 执行成功: {tool_result.result}")
                                # 将工具调用和结果添加到上下文
                                context.add_tool_call(
                                    tool_name, arguments, tool_result.result
                                )
                                has_tool_results = True
                            else:
                                # 工具执行失败
                                print(f"   ❌ 执行失败: {tool_result.error}")
                                error_msg = f"工具 {tool_name} 执行失败: {tool_result.error}"
                                context.add_message("system", error_msg)
                        else:
                            # 找不到工具
                            print(f"   ❌ 找不到工具: {tool_name}")
                            error_msg = f"找不到工具: {tool_name}"
                            context.add_message("system", error_msg)
                        print()  # 空行分隔

                    # 如果有工具结果，继续下一轮
                    if has_tool_results:
                        continue

                # 如果有文本回复，这就是最终结果
                if response.content:
                    final_content = response.content
                    
                    # 显示最终回复
                    if turn > 0:  # 如果有过工具调用
                        print("📋 最终回复:")
                        print(f"   {response.content}")
                    
                    # 在thinking模式下，如果有工具调用历史，在上下文中保存完整内容
                    if agent.thinking_tool_mode and thinking_content and turn > 0:
                        # 只有在有工具调用后的回复中才合并thinking内容（用于上下文）
                        final_content = thinking_content + "\n\n" + response.content

                    context.add_message("assistant", final_content)
                    return RunResult(response.content, context)  # 返回给用户的只是回复内容

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
        finally:
            # 恢复Agent的原始thinking_tool_mode设置
            if thinking_tool_mode is not None:
                agent.thinking_tool_mode = original_thinking_mode

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
