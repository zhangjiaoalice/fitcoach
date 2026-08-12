"""user 相关的 Pydantic Schema(API 的输入/输出格式)"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """注册请求体： 前端 post 过来的数据"""
    email: EmailStr
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    """响应体： 返回给前端用户的信息（不含任何密码字段）"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime

class UserLogin(BaseModel):
    """登录请求体"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """登录成功返回的令牌，token_type 固定 bearer 是 OAuth2 惯例"""
    access_token: str
    token_type: str = "bearer"