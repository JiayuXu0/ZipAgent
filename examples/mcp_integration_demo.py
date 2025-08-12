"""
MCP 工具集成演示

展示如何将 MCP 服务器工具与 LiteAgent 集成使用的完整示例。
"""

import asyncio

from liteagent import Agent, function_tool


async def main():
    """主演示函数"""
    try:
        # 尝试导入 MCP 工具
        from liteagent import MCPToolPool
        print("✅ MCP 工具支持已启用")
    except ImportError:
        print("❌ MCP 工具支持未启用，请安装 MCP SDK: uv add mcp")
        return

    # 定义传统的 function_tool
    @function_tool
    def calculate(expression: str) -> str:
        """计算数学表达式
        
        Args:
            expression: 数学表达式，如 "2+2", "10*5"
            
        Returns:
            计算结果的字符串形式
        """
        try:
            result = eval(expression)  # 注意：实际使用应该用安全的解析器
            return str(result)
        except Exception as e:
            return f"计算错误: {e}"

    print("🔧 创建工具池...")
    tool_pool = MCPToolPool()

    # 演示1：高德地图工具（如果有 API key）
    amap_api_key = "aa49489bbe0255ab108e386e6395411a"  # 替换为实际的 API key

    if amap_api_key != "your_amap_api_key_here":
        try:
            print("🗺️ 加载高德地图工具...")
            amap_tools = await tool_pool.add_mcp_server(
                "amap",
                command="npx",
                args=["-y", "@amap/amap-maps-mcp-server"],
                env={"AMAP_MAPS_API_KEY": amap_api_key},
                tools=["maps_text_search", "maps_direction_driving", "maps_weather"]  # 只导入这几个工具
            )
            print(f"✅ 高德地图工具加载成功: {amap_tools.get_tool_names()}")

            # 创建带有混合工具的 Agent（统一格式！）
            agent = Agent(
                name="地图助手",
                instructions="你是一个智能地图助手，可以帮助用户搜索位置、计算路线和进行数学计算。",
                tools=[calculate, amap_tools]  # 混合使用！
            )

            print(f"🤖 Agent 创建成功，共有 {len(agent._get_all_tools())} 个工具")
            print("可用工具:", [tool.name for tool in agent._get_all_tools()])

        except Exception as e:
            print(f"❌ 高德地图工具加载失败: {e}")
            print("使用基础工具继续演示...")
            agent = Agent(
                name="计算助手",
                instructions="你是一个计算助手。",
                tools=[calculate]
            )
    else:
        print("⚠️ 未提供高德地图 API key，使用基础工具演示")
        agent = Agent(
            name="计算助手",
            instructions="你是一个计算助手。",
            tools=[calculate]
        )

    # 演示工具池管理
    print("\n📊 工具池状态:")
    print(f"- 服务器数量: {len(tool_pool.clients)}")
    print(f"- 工具组数量: {len(tool_pool.tool_groups)}")

    if tool_pool.tool_groups:
        for name, group in tool_pool.tool_groups.items():
            print(f"  - {name}: {group.get_tool_names()}")

    # 演示工具调用（这里只是展示结构，实际调用需要完整的 Runner）
    print("\n🛠️ Agent 工具配置:")
    print(f"- 系统消息: {agent.get_system_message()['content'][:100]}...")
    print(f"- 工具 Schema 数量: {len(agent.get_tools_schema())}")

    # 清理资源
    print("\n🧹 清理资源...")
    await tool_pool.close_all()
    print("✅ 演示完成")


async def simple_mcp_example():
    """简单的 MCP 工具使用示例"""
    try:
        from liteagent import function_tool, load_mcp_tools

        @function_tool
        def greet(name: str) -> str:
            """问候用户"""
            return f"Hello, {name}!"

        # 快速加载 MCP 工具（示例）
        # weather_tools = await load_mcp_tools(
        #     command="node",
        #     args=["weather-server.js"],
        #     tools=["get_weather", "get_forecast"]  # 可选参数
        # )

        # 统一的工具列表格式
        # agent = Agent(tools=[greet, weather_tools])

        print("🚀 简单示例：工具格式统一！")
        print("tools = [function_tool, mcp_tool_group]")
        print("agent = Agent(tools=tools)")

    except ImportError:
        print("MCP 支持未启用")


if __name__ == "__main__":
    print("🌟 LiteAgent MCP 工具集成演示")
    print("=" * 50)

    # 运行主演示
    asyncio.run(main())

    print("\n" + "=" * 50)

    # 运行简单示例
    asyncio.run(simple_mcp_example())
