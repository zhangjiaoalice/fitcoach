"""
全局配置： 用pydantic-settings 从 .env 中读取配置
将所有环境相关的值集中到一个Settings 对象中，代码通过 settings.xxx 访问
-BaseSettings 会自动从环境变量 / .env 文件读取同名字段
- @lru_cache 保证整个进程值创建一个 Settings 实例（单例）
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # model_config 告诉 pydantic 去哪读 .env、 忽略多余的变量
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra="ignore"
    )

    #  数据库
    database_url: str

    # JWT
    jwt_secret: str = "dev_5bf71d85386f308417246b4b86774e964c812ec26faf4a94e4856dbab1f9e84e"
    jwt_algorithm: str ="HS256"
    jwt_expire_minutes: int = 1440

    # Moonshot
    moonshot_api_key: str = ""
    moonshot_base_url: str = "https://api.moonshot.cn/v1"
    moonshot_model: str = "moonshot-v1-8k"


@lru_cache
def get_settings() -> Settings:
    """全局唯一入口。其他模块用 get_settings() 拿配置"""
    return Settings()