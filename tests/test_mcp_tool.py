"""
MCP 工具集成测试

测试 MCP 工具的集成功能，包括工具组、工具池等。
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from zipagent import Agent, function_tool
from zipagent.mcp_tool import (
    MCPClient,
    MCPError,
    MCPNotAvailableError,
    MCPServerConfig,
    MCPTool,
    MCPToolGroup,
    _MCPToolPool,  # 现在是内部类
)


class TestMCPToolGroup:
    """测试 MCPToolGroup 类"""

    def test_tool_group_creation(self):
        """测试工具组创建"""
        # 创建模拟工具
        mock_tools = []
        for i in range(3):
            tool = Mock(spec=MCPTool)
            tool.name = f"tool_{i}"
            mock_tools.append(tool)

        # 创建工具组
        group = MCPToolGroup("test_group", mock_tools)

        assert group.name == "test_group"
        assert len(group) == 3
        assert group.get_tool_names() == ["tool_0", "tool_1", "tool_2"]

    def test_tool_group_iteration(self):
        """测试工具组迭代"""
        mock_tools = []
        for i in range(3):
            tool = Mock(spec=MCPTool)
            tool.name = f"tool_{i}"
            mock_tools.append(tool)

        group = MCPToolGroup("test", mock_tools)

        # 测试迭代
        tools_list = list(group)
        assert len(tools_list) == 3
        assert all(isinstance(tool, Mock) for tool in tools_list)

    def test_tool_group_indexing(self):
        """测试工具组索引访问"""
        mock_tools = []
        for i in range(3):
            tool = Mock(spec=MCPTool)
            tool.name = f"tool_{i}"
            mock_tools.append(tool)

        group = MCPToolGroup("test", mock_tools)

        # 测试数字索引
        assert group[0] == mock_tools[0]
        assert group[1] == mock_tools[1]

        # 测试名称索引
        assert group["tool_0"] == mock_tools[0]
        assert group["tool_1"] == mock_tools[1]
        assert group["nonexistent"] is None

    def test_find_tool(self):
        """测试工具查找"""
        mock_tools = []
        for i in range(3):
            tool = Mock(spec=MCPTool)
            tool.name = f"tool_{i}"
            mock_tools.append(tool)

        group = MCPToolGroup("test", mock_tools)

        assert group.find_tool("tool_0") == mock_tools[0]
        assert group.find_tool("tool_1") == mock_tools[1]
        assert group.find_tool("nonexistent") is None


class TestMCPToolPool:
    """测试 _MCPToolPool 类（内部实现）"""

    def test_pool_creation(self):
        """测试工具池创建"""
        pool = _MCPToolPool()
        assert len(pool.clients) == 0
        assert len(pool.tool_groups) == 0

    @pytest.mark.asyncio
    async def test_add_mcp_server_without_mcp(self):
        """测试在没有 MCP SDK 的情况下添加服务器"""
        with patch("zipagent.mcp_tool.MCP_AVAILABLE", False):
            pool = _MCPToolPool()

            with pytest.raises(MCPNotAvailableError):
                await pool.add_mcp_server(
                    "test", command="echo", args=["hello"]
                )

    @pytest.mark.asyncio
    async def test_remove_server(self):
        """测试移除服务器"""
        pool = _MCPToolPool()

        # 添加模拟客户端
        mock_client = AsyncMock(spec=MCPClient)
        mock_group = Mock(spec=MCPToolGroup)

        pool.clients["test"] = mock_client
        pool.tool_groups["test"] = mock_group

        # 移除服务器
        await pool.remove_server("test")

        # 验证清理
        assert "test" not in pool.clients
        assert "test" not in pool.tool_groups
        mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_all(self):
        """测试关闭所有服务器"""
        pool = _MCPToolPool()

        # 添加多个模拟客户端
        for i in range(3):
            mock_client = AsyncMock(spec=MCPClient)
            mock_group = Mock(spec=MCPToolGroup)

            pool.clients[f"test_{i}"] = mock_client
            pool.tool_groups[f"test_{i}"] = mock_group

        # 关闭所有
        await pool.close_all()

        # 验证清理
        assert len(pool.clients) == 0
        assert len(pool.tool_groups) == 0


class TestAgentIntegration:
    """测试 Agent 与 MCP 工具的集成"""

    def test_agent_with_mixed_tools(self):
        """测试 Agent 使用混合工具"""

        @function_tool
        def calculate(x: int) -> int:
            return x * 2

        # 创建模拟 MCP 工具组
        mock_mcp_tools = []
        for i in range(2):
            tool = Mock(spec=MCPTool)
            tool.name = f"mcp_tool_{i}"
            tool.to_dict.return_value = {
                "type": "function",
                "function": {
                    "name": f"mcp_tool_{i}",
                    "description": f"MCP tool {i}",
                    "parameters": {},
                },
            }
            mock_mcp_tools.append(tool)

        mcp_group = MCPToolGroup("mcp_group", mock_mcp_tools)

        # 创建 Agent
        agent = Agent(
            name="Test Agent",
            instructions="Test agent with mixed tools",
            tools=[calculate, mcp_group],
        )

        # 验证工具展开
        all_tools = agent._get_all_tools()
        assert len(all_tools) == 3  # 1 function_tool + 2 mcp_tools

        # 验证工具名称
        tool_names = [tool.name for tool in all_tools]
        assert "calculate" in tool_names
        assert "mcp_tool_0" in tool_names
        assert "mcp_tool_1" in tool_names

    def test_agent_find_tool_with_mcp(self):
        """测试 Agent 在混合工具中查找工具"""

        @function_tool
        def calculate(x: int) -> int:
            return x * 2

        # 创建模拟 MCP 工具
        mock_tool = Mock(spec=MCPTool)
        mock_tool.name = "search_location"
        mock_tool.to_dict.return_value = {
            "type": "function",
            "function": {
                "name": "search_location",
                "description": "Search location",
                "parameters": {},
            },
        }

        mcp_group = MCPToolGroup("amap", [mock_tool])

        agent = Agent(
            name="Test Agent",
            instructions="Test",
            tools=[calculate, mcp_group],
        )

        # 测试查找
        assert agent.find_tool("calculate") == calculate
        assert agent.find_tool("search_location") == mock_tool
        assert agent.find_tool("nonexistent") is None

    def test_agent_get_tools_schema_with_mcp(self):
        """测试 Agent 获取包含 MCP 工具的 schema"""

        @function_tool
        def calculate(x: int) -> int:
            return x * 2

        # 创建模拟 MCP 工具
        mock_tool = Mock(spec=MCPTool)
        mock_tool.name = "search_location"
        mock_tool.to_dict.return_value = {
            "type": "function",
            "function": {
                "name": "search_location",
                "description": "Search location",
                "parameters": {"type": "object", "properties": {}},
            },
        }

        mcp_group = MCPToolGroup("amap", [mock_tool])

        agent = Agent(
            name="Test Agent",
            instructions="Test",
            tools=[calculate, mcp_group],
        )

        # 获取 schema
        schemas = agent.get_tools_schema()
        assert len(schemas) == 2

        # 验证 schema 内容
        schema_names = [s["function"]["name"] for s in schemas]
        assert "calculate" in schema_names
        assert "search_location" in schema_names


class TestMCPServerConfig:
    """测试 MCP 服务器配置"""

    def test_config_creation(self):
        """测试配置创建"""
        config = MCPServerConfig(
            name="test",
            command="npx",
            args=["-y", "test-server"],
            env={"API_KEY": "test_key"},
            tools=["tool1", "tool2"],
        )

        assert config.name == "test"
        assert config.command == "npx"
        assert config.args == ["-y", "test-server"]
        assert config.env == {"API_KEY": "test_key"}
        assert config.tools == ["tool1", "tool2"]

    def test_config_defaults(self):
        """测试配置默认值"""
        config = MCPServerConfig(name="test", command="node")

        assert config.args == []
        assert config.env is None
        assert config.tools is None


@pytest.mark.integration
class TestMCPIntegration:
    """集成测试（需要真实的 MCP 环境）"""

    @pytest.mark.skip(reason="需要真实的 MCP 服务器")
    @pytest.mark.asyncio
    async def test_real_mcp_integration(self):
        """真实的 MCP 集成测试"""
        # 这个测试需要真实的 MCP 服务器环境
        # 在 CI/CD 环境中应该跳过或使用模拟服务器
        pass


class TestMCPErrors:
    """测试 MCP 错误处理"""

    def test_mcp_not_available_error(self):
        """测试 MCP 不可用错误"""
        error = MCPNotAvailableError()
        assert "MCP SDK 未安装" in str(error)

    def test_mcp_error_inheritance(self):
        """测试 MCP 错误继承关系"""
        from zipagent.exceptions import ToolError

        error = MCPError("test error", tool_name="test_tool")
        assert isinstance(error, ToolError)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
