"""
MCP 工具集成模块

基于官方 MCP Python SDK 实现，提供 MCP 服务器的工具导入和管理功能。
支持工具选择、进程管理和与 LiteAgent 工具系统的统一集成。

使用示例:
    from liteagent import Agent, function_tool
    from liteagent.mcp_tool import MCPToolPool

    @function_tool
    def calculate(x: int) -> int:
        return x * 2

    tool_pool = MCPToolPool()
    amap_tools = await tool_pool.add_mcp_server(
        "amap",
        command="npx",
        args=["-y", "@amap/amap-maps-mcp-server"],
        env={"AMAP_MAPS_API_KEY": "your_key"},
        tools=["search_location"]  # 可选，默认全部
    )

    # 统一格式！
    agent = Agent(tools=[calculate, amap_tools])
"""

import asyncio
import os
import uuid
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from typing import TypeVar

    MCPToolGroupType = TypeVar("MCPToolGroupType", bound="MCPToolGroup")

from .exceptions import ToolError
from .tool import Tool, ToolResult

# MCP 相关导入
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None


class MCPError(ToolError):
    """MCP 相关错误"""


class MCPNotAvailableError(MCPError):
    """MCP SDK 未安装"""

    def __init__(self):
        super().__init__(
            "MCP SDK 未安装。请运行: uv add mcp", tool_name="mcp_sdk"
        )


class MCPServerError(MCPError):
    """MCP 服务器错误"""


class MCPCommunicationError(MCPError):
    """MCP 通信错误"""


@dataclass
class MCPServerConfig:
    """MCP 服务器配置"""

    name: str
    command: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] | None = None
    tools: list[str] | None = None  # 指定要导入的工具，None 表示全部


class MCPClient:
    """MCP 客户端，基于官方 SDK 实现"""

    def __init__(self, config: MCPServerConfig):
        if not MCP_AVAILABLE:
            raise MCPNotAvailableError()

        self.config = config
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self.stdio = None
        self.write = None
        self.is_connected = False

    async def connect(self) -> None:
        """连接到 MCP 服务器"""
        if self.is_connected:
            return

        try:
            # 准备环境变量
            env = dict(os.environ)
            if self.config.env:
                env.update(self.config.env)

            # 创建服务器参数
            server_params = StdioServerParameters(
                command=self.config.command, args=self.config.args, env=env
            )

            # 建立连接
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport

            # 创建会话
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )

            # 初始化连接
            await self.session.initialize()
            self.is_connected = True

        except Exception as e:
            raise MCPServerError(f"连接 MCP 服务器失败: {e}")

    async def list_tools(self) -> list[dict[str, Any]]:
        """获取工具列表"""
        if not self.is_connected or not self.session:
            raise MCPCommunicationError("未连接到 MCP 服务器")

        try:
            response = await self.session.list_tools()
            tools = []

            for tool in response.tools:
                tool_dict = {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                }
                tools.append(tool_dict)

            return tools

        except Exception as e:
            raise MCPCommunicationError(f"获取工具列表失败: {e}")

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """调用工具"""
        if not self.is_connected or not self.session:
            raise MCPCommunicationError("未连接到 MCP 服务器")

        try:
            result = await self.session.call_tool(name, arguments)

            # 处理结果
            if hasattr(result, "content") and result.content:
                content = result.content
                if isinstance(content, list) and len(content) > 0:
                    first_item = content[0]
                    if hasattr(first_item, "text"):
                        return first_item.text
                    elif hasattr(first_item, "data"):
                        return first_item.data
                    else:
                        return str(first_item)
                return str(content)

            return str(result)

        except Exception as e:
            raise MCPCommunicationError(f"调用工具 '{name}' 失败: {e}")

    async def close(self) -> None:
        """关闭连接"""
        if self.exit_stack:
            await self.exit_stack.aclose()
        self.is_connected = False


class MCPTool(Tool):
    """MCP 工具包装器，将 MCP 工具包装为 ZipAgent 工具"""

    # 类级别的连接管理
    _global_pool: Optional["_MCPToolPool"] = None

    def __init__(
        self,
        name: str,
        description: str,
        schema: dict[str, Any],
        client: MCPClient,
    ):
        # 创建同步包装函数
        def mcp_function(**kwargs):
            return asyncio.run(client.call_tool(name, kwargs))

        super().__init__(name, description, mcp_function)
        self.mcp_client = client
        self.mcp_schema = schema

        # 转换 schema 为 OpenAI 格式
        self.schema = self._convert_mcp_schema(schema)

    @classmethod
    async def connect(
        cls,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        tools: list[str] | None = None,
        name: str | None = None,
    ) -> "MCPToolGroup":
        """
        连接到 MCP 服务器并返回工具组

        Args:
            command: 启动命令
            args: 命令参数
            env: 环境变量
            tools: 要导入的工具列表，None 表示导入全部
            name: 服务器名称（可选，自动生成唯一名称）

        Returns:
            MCP工具组，可直接放在 Agent.tools 列表中

        Example:
            amap_tools = await MCPTool.connect(
                command="npx",
                args=["-y", "@amap/amap-maps-mcp-server"],
                env={"AMAP_MAPS_API_KEY": "your_key"},
                tools=["maps_weather"]
            )

            agent = Agent(tools=[amap_tools])
        """
        # 获取或创建全局池
        if cls._global_pool is None:
            cls._global_pool = _MCPToolPool()

        # 生成唯一名称
        if name is None:
            name = f"mcp_{uuid.uuid4().hex[:8]}"

        # 使用内部池添加服务器
        return await cls._global_pool.add_mcp_server(
            name=name, command=command, args=args, env=env, tools=tools
        )

    @classmethod
    async def from_npm(
        cls,
        package: str,
        env: dict[str, str] | None = None,
        tools: list[str] | None = None,
        name: str | None = None,
    ) -> "MCPToolGroup":
        """
        从 npm 包快速创建 MCP 工具（便捷方法）

        Args:
            package: npm 包名
            env: 环境变量
            tools: 要导入的工具列表
            name: 服务器名称（可选）

        Returns:
            MCP工具组

        Example:
            weather_tool = await MCPTool.from_npm(
                "@amap/amap-maps-mcp-server",
                env={"AMAP_MAPS_API_KEY": "your_key"}
            )
        """
        return await cls.connect(
            command="npx",
            args=["-y", package],
            env=env,
            tools=tools,
            name=name,
        )

    @classmethod
    async def disconnect(cls, name: str) -> None:
        """
        断开特定的 MCP 连接

        Args:
            name: 服务器名称
        """
        if cls._global_pool:
            await cls._global_pool.remove_server(name)

    @classmethod
    async def disconnect_all(cls) -> None:
        """断开所有 MCP 连接"""
        if cls._global_pool:
            await cls._global_pool.close_all()
            cls._global_pool = None

    @classmethod
    def list_connections(cls) -> list[str]:
        """
        列出当前所有活动的 MCP 连接

        Returns:
            连接名称列表
        """
        if cls._global_pool:
            return list(cls._global_pool.clients.keys())
        return []

    def _convert_mcp_schema(
        self, mcp_schema: dict[str, Any]
    ) -> dict[str, Any]:
        """将 MCP schema 转换为 OpenAI Function Calling 格式"""
        input_schema = mcp_schema.get("inputSchema", {})

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": input_schema,
            },
        }

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        """执行 MCP 工具"""
        try:
            # 简化的异步调用处理
            try:
                # 尝试获取当前事件循环
                loop = asyncio.get_running_loop()
                # 如果在事件循环中，创建一个任务但同步等待
                import nest_asyncio

                nest_asyncio.apply()
                result = asyncio.run(
                    self.mcp_client.call_tool(self.name, arguments)
                )
            except ImportError:
                # 如果 nest_asyncio 不可用，使用替代方案
                try:
                    loop = asyncio.get_running_loop()
                    # 直接返回错误，提示需要异步环境
                    return ToolResult(
                        name=self.name,
                        arguments=arguments,
                        result=None,
                        success=False,
                        error="MCP tools require async environment. Consider using nest_asyncio or calling from async context.",
                    )
                except RuntimeError:
                    # 没有运行的事件循环，可以安全使用 asyncio.run
                    result = asyncio.run(
                        self.mcp_client.call_tool(self.name, arguments)
                    )
            except RuntimeError:
                # 没有运行的事件循环
                result = asyncio.run(
                    self.mcp_client.call_tool(self.name, arguments)
                )

            return ToolResult(
                name=self.name,
                arguments=arguments,
                result=result,
                success=True,
            )
        except Exception as e:
            return ToolResult(
                name=self.name,
                arguments=arguments,
                result=None,
                success=False,
                error=str(e),
            )


class MCPToolGroup:
    """MCP 工具组，包含多个 MCP 工具，可以直接放在 Agent.tools 列表中"""

    def __init__(self, name: str, tools: list[MCPTool]):
        self.name = name
        self.tools = tools
        self._tools_dict = {tool.name: tool for tool in tools}

    def __iter__(self):
        """支持迭代"""
        return iter(self.tools)

    def __len__(self):
        """支持 len() 函数"""
        return len(self.tools)

    def __getitem__(self, key):
        """支持索引和名称访问"""
        if isinstance(key, int):
            return self.tools[key]
        elif isinstance(key, str):
            return self._tools_dict.get(key)
        else:
            raise TypeError("Key must be int or str")

    def __repr__(self):
        tool_names = [tool.name for tool in self.tools]
        return f"MCPToolGroup(name='{self.name}', tools={tool_names})"

    def get_tool_names(self) -> list[str]:
        """获取所有工具名称"""
        return [tool.name for tool in self.tools]

    def find_tool(self, name: str) -> MCPTool | None:
        """根据名称查找工具"""
        return self._tools_dict.get(name)


class _MCPToolPool:
    """MCP 工具池（内部实现），管理多个 MCP 服务器和工具"""

    def __init__(self):
        self.clients: dict[str, MCPClient] = {}
        self.tool_groups: dict[str, MCPToolGroup] = {}

    async def add_mcp_server(
        self,
        name: str,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        tools: list[str] | None = None,
    ) -> MCPToolGroup:
        """
        添加 MCP 服务器并导入工具

        Args:
            name: 服务器名称
            command: 启动命令
            args: 命令参数
            env: 环境变量
            tools: 要导入的工具列表，None 表示导入全部

        Returns:
            MCP工具组，可直接放在 Agent.tools 列表中
        """
        if name in self.clients:
            raise MCPError(f"MCP 服务器 '{name}' 已存在")

        # 创建配置
        config = MCPServerConfig(
            name=name, command=command, args=args or [], env=env, tools=tools
        )

        # 创建客户端并连接
        client = MCPClient(config)
        await client.connect()

        # 获取工具列表
        available_tools = await client.list_tools()

        # 过滤工具（如果指定了特定工具）
        if tools:
            tool_set = set(tools)
            available_tools = [
                t for t in available_tools if t.get("name") in tool_set
            ]

        # 创建工具实例
        mcp_tools = []
        for tool_info in available_tools:
            tool = MCPTool(
                name=tool_info["name"],
                description=tool_info.get(
                    "description", f"MCP tool {tool_info['name']}"
                ),
                schema=tool_info,
                client=client,
            )
            mcp_tools.append(tool)

        # 创建工具组
        tool_group = MCPToolGroup(name, mcp_tools)

        # 保存到池中
        self.clients[name] = client
        self.tool_groups[name] = tool_group

        return tool_group

    async def remove_server(self, name: str) -> None:
        """移除 MCP 服务器"""
        if name in self.clients:
            await self.clients[name].close()
            del self.clients[name]
            del self.tool_groups[name]

    def get_tool_group(self, name: str) -> MCPToolGroup | None:
        """获取指定的工具组"""
        return self.tool_groups.get(name)

    def get_all_tool_groups(self) -> list[MCPToolGroup]:
        """获取所有工具组"""
        return list(self.tool_groups.values())

    def get_all_tools(self) -> list[Tool]:
        """获取所有工具（扁平化列表）"""
        all_tools = []
        for tool_group in self.tool_groups.values():
            all_tools.extend(tool_group.tools)
        return all_tools

    async def close_all(self) -> None:
        """关闭所有 MCP 服务器"""
        for name in list(self.clients.keys()):
            await self.remove_server(name)


# 便捷函数 - 保留以支持向后兼容，但标记为已弃用
async def load_mcp_tools(
    command: str,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
    tools: list[str] | None = None,
) -> "MCPToolGroup":
    """
    快速加载 MCP 工具的便捷函数

    警告: 此函数已弃用，请使用 MCPTool.connect() 代替

    Args:
        command: 启动命令
        args: 命令参数
        env: 环境变量
        tools: 要导入的工具列表，None 表示导入全部

    Returns:
        MCP工具组
    """
    import warnings

    warnings.warn(
        "load_mcp_tools() is deprecated, use MCPTool.connect() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return await MCPTool.connect(
        command=command, args=args, env=env, tools=tools
    )
