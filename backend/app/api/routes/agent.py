"""
Agent 对话接口
Round1 - 最小版本
只做一次 LLM 调用， 不走Loop、不用工具
先验证 HTTP -> Moonshot -> 回复这个路径
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.agent.moonshot_client import chat_completion
from app.models.user import User

router = APIRouter(prefix="/agent", tags=["agent"])

class ChatIn(BaseModel):
    """前端发来的对话请求"""
    message: str

class ChatOut(BaseModel):
    """返回给前端的回复"""
    reply: str

@router.post("/chat", response_model=ChatOut)
async def chat(data: ChatIn, current_user: User=Depends(get_current_user)):
    # 构造 messages 数组
    messages = [
        {"role": "system", "content": "你是一名专业的运动营养学专家，兼健身健美的专业人士，有多年的健美比赛经验并获得过健美职业卡，擅长增肌、减脂、塑形，现在为用户提供专业的健身指导和营养建议，回答要具体、贴合用户情况。"},
        {"role": "user", "content": data.message}
    ]

    # 调用 Moonshot API
    response = await chat_completion(messages=messages)

    # 从 response 中取出 assistant 的回复文本
    reply = response["choices"][0]["message"]["content"]


    return ChatOut(reply=reply)