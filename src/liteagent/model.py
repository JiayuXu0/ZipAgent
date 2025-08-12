"""Model - LLM交互接口模块"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .context import Usage

# 尝试加载环境变量
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv不是必需的依赖


@dataclass
class ModelResponse:
    """模型响应结果"""

    content: Optional[str]
    tool_calls: List[Dict[str, Any]]
    usage: Usage
    finish_reason: str


class Model(ABC):
    """LLM模型抽象基类"""

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> ModelResponse:
        """生成模型响应"""
        pass


class OpenAIModel(Model):
    """基于原生OpenAI的模型实现"""

    def __init__(
        self,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs: Any,
    ):
        """
        初始化OpenAI模型

        Args:
            model_name: 模型名称，如果不指定会从环境变量MODEL读取
            api_key: API密钥，如果不指定会从环境变量API_KEY读取
            base_url: API基础URL，如果不指定会从环境变量BASE_URL读取
            **kwargs: 其他参数
        """
        try:
            from openai import OpenAI

            # 从环境变量或参数获取配置
            self.model_name = model_name or os.getenv("MODEL", "gpt-3.5-turbo")
            self.api_key = api_key or os.getenv("API_KEY")
            self.base_url = base_url or os.getenv("BASE_URL")

            # 构建客户端参数
            client_kwargs = {}
            if self.api_key:
                client_kwargs["api_key"] = self.api_key
            if self.base_url:
                client_kwargs["base_url"] = self.base_url

            # 创建OpenAI客户端
            self.client = OpenAI(**client_kwargs)

            # 其他参数
            self.kwargs = kwargs.copy()

        except ImportError as e:
            raise ImportError("需要安装openai包: pip install openai") from e

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> ModelResponse:
        """调用OpenAI生成响应"""
        try:
            # 准备API调用参数
            call_kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000,
                **self.kwargs,
            }

            # 如果有工具，添加到请求中
            if tools:
                call_kwargs["tools"] = tools
                call_kwargs["tool_choice"] = "auto"

            # 调用OpenAI API
            response = self.client.chat.completions.create(**call_kwargs)

            # 解析响应
            message = response.choices[0].message
            content = message.content
            tool_calls: List[Dict[str, Any]] = []

            # 处理工具调用
            if message.tool_calls:
                for call in message.tool_calls:
                    tool_call = {
                        "id": call.id,
                        "type": call.type,
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    tool_calls.append(tool_call)

            # 解析使用量
            usage = Usage()
            if response.usage:
                usage.input_tokens = response.usage.prompt_tokens or 0
                usage.output_tokens = response.usage.completion_tokens or 0
                usage.total_tokens = response.usage.total_tokens or 0

            return ModelResponse(
                content=content,
                tool_calls=tool_calls,
                usage=usage,
                finish_reason=response.choices[0].finish_reason or "stop",
            )

        except Exception as e:
            # 简单的错误处理
            return ModelResponse(
                content=f"模型调用出错: {e!s}",
                tool_calls=[],
                usage=Usage(),
                finish_reason="error",
            )


# 为了向后兼容，保持LiteLLMModel别名
LiteLLMModel = OpenAIModel
