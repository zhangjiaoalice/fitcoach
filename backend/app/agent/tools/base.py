"""
Agent 工具基类
设计思想：
-  工具 = 名字(name) + 描述（description 给llm 看的说明文档） + 参数 schema + 执行函数（handler）
-  全局 TOOL_REGISTRY 用于存储所有的工具，Loop按名字查找
- ctx 传给 handler， 含 db/current_user, 工具通过它访问数据库
"""
# dataclass 是python的内置模块，@dataclass 装饰器能自为一个“主要用来存数据”的类生成 __init__,__repr__,__eq__ 等样板方法
from dataclasses import dataclass
from typing import Awaitable, Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

@dataclass
class AgentContext:
    """
    Agent 执行上下文，工具靠它拿到 DB 和当前用户信息
    Loop 会构造一次、透传给所有工具
    """
    db: AsyncSession
    current_user: User


class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict, # openai JSON schema 格式
        handler: Callable[[dict, AgentContext], Awaitable[Any]]
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler

    def to_openai_schema(self):
        """转换成openai JSON Schema 格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    # 执行工具函数
    async def run(self, arguments: dict, ctx: AgentContext) -> Any:
        """
            接收函数调用参数 arguments， Agent 执行函数调用， 返回工具调用结果
        """
        return await self.handler(arguments, ctx)

# 全局注册中心 - import工具模块是自动注册
TOOL_REGISTRY: dict[str, Tool] = {}

def register_tool(tool: Tool) -> None:
    TOOL_REGISTRY[tool.name] = tool

