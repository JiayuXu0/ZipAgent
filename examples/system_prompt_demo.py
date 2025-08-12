#!/usr/bin/env python3
"""
系统提示文件功能演示

展示如何使用 system.md 文件来定制 AI 的工具使用行为。
"""

import asyncio
from liteagent import Agent, function_tool, MCPToolPool

@function_tool
def calculate(expression: str) -> str:
    """计算数学表达式
    
    Args:
        expression: 要计算的数学表达式，如 "2+3*4"
        
    Returns:
        计算结果
    """
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"

async def demo_system_prompt():
    """演示系统提示功能"""
    print("🎯 系统提示功能演示")
    print("=" * 40)
    
    # 场景1: 使用默认系统提示
    print("\n📋 场景1: 使用默认系统提示")
    print("默认的 system.md 文件定义了工具使用规范")
    
    agent_default = Agent(
        name="标准助手",
        instructions="你是一个数学助手",
        tools=[calculate],
        use_system_prompt=True  # 启用默认系统提示
    )
    
    system_msg = agent_default.get_system_message()
    print(f"系统提示长度: {len(system_msg['content'])} 字符")
    print("包含工具使用规范: ✅")
    
    # 场景2: 禁用系统提示
    print(f"\n📋 场景2: 禁用系统提示")
    agent_minimal = Agent(
        name="简洁助手", 
        instructions="你是一个数学助手",
        tools=[calculate],
        use_system_prompt=False  # 禁用系统提示
    )
    
    system_msg_minimal = agent_minimal.get_system_message()
    print(f"系统提示长度: {len(system_msg_minimal['content'])} 字符")
    print("仅包含基本指令: ✅")
    
    # 场景3: MCP 工具集成
    print(f"\n📋 场景3: MCP 工具集成演示")
    tool_pool = MCPToolPool()
    
    try:
        # 加载 MCP 工具
        print("正在加载高德地图工具...")
        amap_tools = await tool_pool.add_mcp_server(
            "amap",
            command="npx",
            args=["-y", "@amap/amap-maps-mcp-server"],
            env={"AMAP_MAPS_API_KEY": "aa49489bbe0255ab108e386e6395411a"},
            tools=["maps_weather"]
        )
        
        # 创建集成 Agent
        agent_integrated = Agent(
            name="智能助手",
            instructions="你是一个多功能助手，能够进行计算和查询天气",
            tools=[calculate, amap_tools],
            use_system_prompt=True  # 使用工具使用规范
        )
        
        system_msg_integrated = agent_integrated.get_system_message()
        print(f"集成后系统提示长度: {len(system_msg_integrated['content'])} 字符")
        print(f"包含工具: calculate, maps_weather")
        print("✅ MCP 工具与系统提示完美集成")
        
    except Exception as e:
        print(f"MCP 集成演示跳过: {e}")
    
    finally:
        await tool_pool.close_all()
    
    # 使用建议
    print(f"\n{'='*40}")
    print("💡 使用建议:")
    print("1. 保持默认的 system.md 文件以获得最佳工具使用体验")
    print("2. 可以自定义 system_prompt_file 参数使用不同的提示文件")
    print("3. 对于简单应用可以设置 use_system_prompt=False")
    print("4. 系统提示会自动与 function_tool 和 MCP 工具集成")
    
    print(f"\n🎉 演示完成！")

if __name__ == "__main__":
    asyncio.run(demo_system_prompt())