"""Pipeline Node 抽象基类

定义 Pipeline 中每个节点的接口和基础行为。
所有节点通过链式连接实现 ASR → VLM+LLM → TTS 的处理流程。
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
import asyncio


class PipelineNode(ABC):
    """Pipeline 节点基类

    每个节点负责处理数据并传递给下一个节点。
    通过 set_next() 方法构建处理链。
    """

    def __init__(self, name: str):
        self.name = name
        self.next_node: Optional["PipelineNode"] = None
        self.orchestrator: Optional["PipelineOrchestrator"] = None

    @abstractmethod
    async def process(self, data: dict) -> dict:
        """处理数据并传递给下一个节点

        Args:
            data: 包含输入数据的字典，节点应原地修改或返回新字典

        Returns:
            处理后的数据字典
        """
        pass

    async def send_to_next(self, data: dict):
        """将数据传递给下一个节点"""
        if self.next_node:
            await self.next_node.process(data)

    def set_next(self, node: "PipelineNode") -> "PipelineNode":
        """设置下一个节点，支持链式调用

        Example:
            asr.set_next(vlm).set_next(tts)
        """
        self.next_node = node
        return node


class StubNode(PipelineNode):
    """Stub 节点 - 用于开发阶段保证 Pipeline 可运行

    不执行实际处理，仅将 stub_data 合并到输入数据中并传递给下一节点。
    """

    def __init__(self, name: str, stub_data: dict = None):
        super().__init__(name)
        self.stub_data = stub_data or {}

    async def process(self, data: dict) -> dict:
        """合并 stub 数据并传递给下一个节点"""
        data.update(self.stub_data)
        await self.send_to_next(data)
        return data