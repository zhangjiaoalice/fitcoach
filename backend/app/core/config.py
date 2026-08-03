"""全局配置：用 pydantic-settings 从 .env 读取。

这是 FastAPI 项目管理配置的标准方式——把所有环境相关的值集中到一个
Settings 对象，代码里通过 settings.xxx 访问，绝不硬编码密钥（见 PRD 7.2）。

这个文件是基建，AI 已写完，你读懂即可：
- BaseSettings 会自动从环境变量 / .env 文件读取同名字段
- @lru_cache 保证整个进程只创建一个 Settings 实例（单例）
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # model_config 告诉 pydantic 去哪读 .env、忽略多余变量
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- 数据库 ---
    database_url: str

    # --- JWT ---
    jwt_secret: str = "dev_secret_change_me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # --- Moonshot ---
    moonshot_api_key: str = ""
    moonshot_base_url: str = "https://api.moonshot.cn/v1"
    moonshot_model: str = "moonshot-v1-8k"


@lru_cache
def get_settings() -> Settings:
    """全局唯一入口。其他模块用 get_settings() 拿配置。"""
    return Settings()
