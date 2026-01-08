"""
配置管理模块
使用 Pydantic Settings 进行类型安全的配置管理
"""

from translator.config.settings import Settings, get_settings

settings = get_settings()

__all__ = ["Settings", "get_settings", "settings"]
