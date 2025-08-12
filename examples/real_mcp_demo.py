"""
真实的 MCP 工具使用示例

展示如何在实际环境中使用 MCP 工具与 LiteAgent 集成。
需要安装 MCP SDK: uv add mcp
"""

import asyncio

from dotenv import load_dotenv

from liteagent import Agent, Runner, function_tool

# 加载环境变量
load_dotenv()


async def real_amap_demo():
    """真实的高德地图 MCP 演示"""
    try:
        from liteagent import MCPToolPool
        print("✅ MCP 工具支持已启用")
    except ImportError:
        print("❌ 请先安装 MCP SDK: uv add mcp")
        return

    # 检查 API key
    amap_api_key = "aa49489bbe0255ab108e386e6395411a"
    if not amap_api_key:
        print("❌ 请设置环境变量 AMAP_MAPS_API_KEY")
        print("可以在 .env 文件中添加: AMAP_MAPS_API_KEY=your_key_here")
        return

    # 定义辅助工具
    @function_tool
    def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> str:
        """计算两点间的直线距离（简化版）
        
        Args:
            lat1: 起点纬度
            lng1: 起点经度  
            lat2: 终点纬度
            lng2: 终点经度
            
        Returns:
            距离描述
        """
        import math

        # 简化的距离计算（不考虑地球曲率）
        lat_diff = abs(lat1 - lat2)
        lng_diff = abs(lng1 - lng2)
        distance = math.sqrt(lat_diff**2 + lng_diff**2) * 111  # 大约转换为公里

        return f"直线距离约 {distance:.2f} 公里"

    print("🔧 创建工具池并加载高德地图工具...")
    tool_pool = MCPToolPool()

    try:
        # 加载高德地图工具
        amap_tools = await tool_pool.add_mcp_server(
            "amap",
            command="npx",
            args=["-y", "@amap/amap-maps-mcp-server"],
            env={"AMAP_MAPS_API_KEY": "aa49489bbe0255ab108e386e6395411a"}
            # 不指定 tools 参数，导入所有可用工具
        )

        print("✅ 高德地图工具加载成功!")
        print(f"可用工具: {', '.join(amap_tools.get_tool_names())}")

        # 创建智能地图助手
        agent = Agent(
            name="地图助手",
            instructions="""你是一个专业的地图助手，具有以下能力：
1. 使用高德地图API搜索位置、获取路线规划
2. 计算两点间的直线距离
3. 提供详细的地理信息和导航建议

请始终提供准确、有用的地理信息，并在可能的情况下使用实际的地图数据。""",
            tools=[calculate_distance, amap_tools]  # 统一格式！
        )

        print("\n🤖 智能地图助手创建成功")
        print(f"总工具数: {len(agent._get_all_tools())}")
        print(f"工具列表: {[tool.name for tool in agent._get_all_tools()]}")

        # 交互式演示
        print("\n🗺️ 开始交互式演示...")
        print("你可以询问：")
        print("- 搜索地点：'帮我搜索北京大学的位置'")
        print("- 路线规划：'从北京西站到首都机场怎么走'")
        print("- 距离计算：'计算两个坐标点的距离'")
        print("\n输入 'quit' 退出")

        while True:
            try:
                user_input = input("\n🙋 用户: ").strip()
                if user_input.lower() in ['quit', 'exit', '退出']:
                    break

                if not user_input:
                    continue

                print("🤖 助手思考中...")

                # 使用 Runner 执行对话
                result = Runner.run(agent, user_input)
                print(f"🤖 助手: {result.content}")

            except KeyboardInterrupt:
                print("\n👋 用户中断，退出演示")
                break
            except Exception as e:
                print(f"❌ 执行出错: {e}")

    except Exception as e:
        print(f"❌ 工具加载失败: {e}")
        print("可能的原因：")
        print("1. 网络连接问题")
        print("2. API key 无效")
        print("3. @amap/amap-maps-mcp-server 包未找到")

    finally:
        # 清理资源
        print("\n🧹 清理资源...")
        await tool_pool.close_all()


async def test_tool_integration():
    """测试工具集成的基本功能"""
    try:
        from liteagent import MCPToolGroup, MCPToolPool

        print("🧪 测试工具集成...")

        # 测试工具池创建
        pool = MCPToolPool()
        print("✅ 工具池创建成功")

        # 测试工具组创建

        # 模拟工具（仅用于测试）
        mock_tools = []
        tool_group = MCPToolGroup("test", mock_tools)
        print("✅ 工具组创建成功")

        print("✅ 基础集成测试通过")

    except Exception as e:
        print(f"❌ 集成测试失败: {e}")


if __name__ == "__main__":
    print("🌟 LiteAgent 真实 MCP 工具演示")
    print("=" * 50)

    # 先运行基础测试
    asyncio.run(test_tool_integration())

    print("\n" + "=" * 50)

    # 运行真实演示
    asyncio.run(real_amap_demo())
