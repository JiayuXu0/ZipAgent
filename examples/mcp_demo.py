#!/usr/bin/env python3
"""
LiteAgent MCP 工具演示

展示 MCP (Model Context Protocol) 工具集成：
1. 新的 MCPTool.connect() API
2. 与 function_tool 混合使用
3. 系统提示集成
4. 真实环境使用案例
"""

import asyncio

from liteagent import Agent, Runner, function_tool


# ========== 工具定义 ==========

@function_tool
def calculate(expression: str) -> str:
    """计算数学表达式
    
    Args:
        expression: 要计算的数学表达式，如 "2+3*4"
    """
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"


@function_tool
def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> str:
    """计算两点间的直线距离（简化版）
    
    Args:
        lat1: 起点纬度
        lng1: 起点经度  
        lat2: 终点纬度
        lng2: 终点经度
    """
    import math
    
    lat_diff = abs(lat1 - lat2)
    lng_diff = abs(lng1 - lng2)
    distance = math.sqrt(lat_diff**2 + lng_diff**2) * 111  # 大约转换为公里
    
    return f"直线距离约 {distance:.2f} 公里"


# ========== 演示函数 ==========

async def demo_1_mcp_integration():
    """演示1: MCP 工具集成"""
    print("=" * 60)
    print("🔗 演示1: MCP 工具集成 - 新 API")
    print("=" * 60)
    
    try:
        from liteagent import MCPTool
        print("✅ MCP 工具支持已启用")
    except ImportError:
        print("❌ MCP 工具支持未启用，请安装: uv add mcp")
        return

    print("💡 新的使用方式:")
    print("  amap_tools = await MCPTool.connect(...)")
    print("  weather_tools = await MCPTool.from_npm('@weather/server')")
    print("  agent = Agent(tools=[function_tool, mcp_tools])")
    
    # 演示连接管理
    connections = MCPTool.list_connections()
    print(f"\n📊 当前连接数: {len(connections)}")


async def demo_2_system_prompt_integration():
    """演示2: 系统提示与 MCP 工具集成"""
    print("\n" + "=" * 60)
    print("📋 演示2: 系统提示功能")
    print("=" * 60)

    # 场景1: 使用默认系统提示
    print("📋 场景1: 使用默认系统提示")
    agent_default = Agent(
        name="标准助手",
        instructions="你是一个数学助手",
        tools=[calculate],
        use_system_prompt=True,  # 启用默认系统提示
    )

    system_msg = agent_default.get_system_message()
    print(f"系统提示长度: {len(system_msg['content'])} 字符")
    print("包含工具使用规范: ✅")

    # 场景2: 禁用系统提示
    print("\n📋 场景2: 禁用系统提示")
    agent_minimal = Agent(
        name="简洁助手",
        instructions="你是一个数学助手",
        tools=[calculate],
        use_system_prompt=False,  # 禁用系统提示
    )

    system_msg_minimal = agent_minimal.get_system_message()
    print(f"系统提示长度: {len(system_msg_minimal['content'])} 字符")
    print("仅包含基本指令: ✅")


async def demo_3_real_mcp_usage():
    """演示3: 真实 MCP 工具使用"""
    print("\n" + "=" * 60)
    print("🗺️ 演示3: 真实 MCP 工具使用 (高德地图)")
    print("=" * 60)
    
    try:
        from liteagent import MCPTool
        
        # 检查 API key
        amap_api_key = "aa49489bbe0255ab108e386e6395411a"
        if not amap_api_key:
            print("❌ 请设置高德地图 API key")
            return

        print("🔧 连接高德地图工具...")
        
        # 使用新的静态方法
        amap_tools = await MCPTool.connect(
            command="npx",
            args=["-y", "@amap/amap-maps-mcp-server"],
            env={"AMAP_MAPS_API_KEY": amap_api_key},
            tools=["maps_weather", "maps_text_search"],  # 只导入部分工具
            name="amap"
        )

        print("✅ 高德地图工具加载成功!")
        print(f"可用工具: {', '.join(amap_tools.get_tool_names())}")

        # 创建混合工具的 Agent
        agent = Agent(
            name="地图助手",
            instructions="""你是一个智能地图助手，具有以下能力：
1. 使用高德地图API搜索位置、获取天气
2. 计算两点间的直线距离
3. 提供详细的地理信息

请始终提供准确、有用的地理信息。""",
            tools=[calculate_distance, amap_tools],  # 混合使用！
            use_system_prompt=True  # 使用工具规范
        )

        print(f"\n🤖 智能地图助手创建成功")
        total_tools = len(agent.tools) + len(amap_tools)
        print(f"总工具数: {total_tools}")
        tool_names = ["calculate_distance"] + amap_tools.get_tool_names()
        print(f"工具列表: {tool_names}")

        # 连接状态
        connections = MCPTool.list_connections()
        print(f"\n📊 活动连接: {connections}")

        print("\n💡 可以尝试的问题:")
        print("- '北京今天天气怎么样？'")
        print("- '搜索北京大学的位置'")
        print("- '计算两个坐标点的距离'")

    except Exception as e:
        print(f"❌ 演示失败: {e}")
        print("可能的原因：网络问题、API key无效、或MCP包未找到")

    finally:
        # 清理资源
        print("\n🧹 清理资源...")
        try:
            await MCPTool.disconnect_all()
        except:
            pass


async def demo_4_quick_examples():
    """演示4: 快速使用示例"""
    print("\n" + "=" * 60)
    print("⚡ 演示4: 快速使用示例")
    print("=" * 60)

    print("🚀 API 对比:")
    print()
    print("# 旧版本 (复杂):")
    print("tool_pool = MCPToolPool()")
    print("amap_tools = await tool_pool.add_mcp_server(...)")
    print("await tool_pool.close_all()")
    print()
    print("# 新版本 (简洁):")
    print("amap_tools = await MCPTool.connect(...)")
    print("weather_tools = await MCPTool.from_npm('@weather/server')")
    print("await MCPTool.disconnect_all()  # 可选")
    print()
    print("# 统一的工具格式:")
    print("agent = Agent(tools=[function_tool, mcp_tool_group])")


async def main():
    """主演示函数"""
    print("🌟 LiteAgent MCP 工具演示")
    print("展示 MCP 工具集成的完整功能")
    
    try:
        await demo_1_mcp_integration()
        await demo_2_system_prompt_integration()
        await demo_3_real_mcp_usage()
        await demo_4_quick_examples()
        
        print("\n" + "=" * 60)
        print("✅ MCP 演示完成！")
        print("💡 要了解更多功能:")
        print("  - 基础功能: python basic_demo.py")
        print("  - 流式输出: python stream_demo.py")
        
    except KeyboardInterrupt:
        print("\n⏹️ 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")


if __name__ == "__main__":
    asyncio.run(main())