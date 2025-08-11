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
    def generate(self, messages: List[Dict[str, Any]],
                tools: Optional[List[Dict[str, Any]]] = None) -> ModelResponse:
        """生成模型响应"""
        pass


class LiteLLMModel(Model):
    """基于LiteLLM的模型实现，支持多种模型提供商"""

    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None,
                 base_url: Optional[str] = None, **kwargs: Any):
        """
        初始化LiteLLM模型

        Args:
            model_name: 模型名称，如果不指定会从环境变量MODEL读取
            api_key: API密钥，如果不指定会从环境变量API_KEY读取
            base_url: API基础URL，如果不指定会从环境变量BASE_URL读取
            **kwargs: 其他参数
        """
        try:
            import litellm  # noqa: F401

            # 从环境变量或参数获取配置
            self.model_name = model_name or os.getenv("MODEL", "gpt-3.5-turbo")
            self.api_key = api_key or os.getenv("API_KEY")
            self.base_url = base_url or os.getenv("BASE_URL")

            # 构建kwargs
            self.kwargs = kwargs.copy()
            if self.api_key:
                self.kwargs["api_key"] = self.api_key
            if self.base_url:
                self.kwargs["base_url"] = self.base_url

        except ImportError as e:
            raise ImportError("需要安装litellm包: pip install litellm") from e

    def generate(self, messages: List[Dict[str, Any]],
                tools: Optional[List[Dict[str, Any]]] = None) -> ModelResponse:
        """调用LiteLLM生成响应"""
        try:
            import litellm

            # 准备API调用参数
            call_kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000,
                **self.kwargs  # 包含api_key等参数
            }

            # 如果有工具，添加到请求中
            if tools:
                call_kwargs["tools"] = tools
                call_kwargs["tool_choice"] = "auto"

            # 调用LiteLLM API
            response = litellm.completion(**call_kwargs)

            # 解析响应
            message = response.choices[0].message
            content = message.content if hasattr(message, 'content') else None
            tool_calls: List[Dict[str, Any]] = []

            # 处理工具调用
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_calls = []
                for call in message.tool_calls:
                    tool_call = {
                        "id": getattr(call, 'id', f"call_{len(tool_calls)}"),
                        "type": getattr(call, 'type', 'function'),
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments
                        }
                    }
                    tool_calls.append(tool_call)

            # 解析使用量
            usage = Usage()
            if hasattr(response, 'usage') and response.usage:
                usage.input_tokens = getattr(response.usage, 'prompt_tokens', 0) or 0
                usage.output_tokens = getattr(response.usage, 'completion_tokens', 0) or 0
                usage.total_tokens = getattr(response.usage, 'total_tokens', 0) or 0

            return ModelResponse(
                content=content,
                tool_calls=tool_calls,
                usage=usage,
                finish_reason=getattr(response.choices[0], 'finish_reason', 'stop') or "stop"
            )

        except Exception as e:
            # 简单的错误处理
            return ModelResponse(
                content=f"模型调用出错: {e!s}",
                tool_calls=[],
                usage=Usage(),
                finish_reason="error"
            )


# 为了兼容性，提供OpenAI别名
OpenAIModel = LiteLLMModel
