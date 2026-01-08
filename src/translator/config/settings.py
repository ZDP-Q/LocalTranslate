"""
应用配置
支持环境变量和 .env 文件
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelSettings(BaseSettings):
    """模型相关配置"""

    model_config = SettingsConfigDict(env_prefix="TRANSLATOR_MODEL_")

    name: str = Field(default="tencent/HY-MT1.5-1.8B", description="模型名称或本地路径")
    path: Path | None = Field(default=None, description="本地模型路径（优先级高于 name）")
    device_map: str = Field(default="auto", description="设备映射策略")
    use_bfloat16: bool = Field(default=True, description="是否使用 bfloat16 精度")
    max_new_tokens: int = Field(default=2048, ge=128, le=8192, description="最大生成 token 数")
    do_sample: bool = Field(default=False, description="是否使用采样生成")
    temperature: float = Field(default=1.0, ge=0.0, le=2.0, description="采样温度")

    def get_model_name_or_path(self) -> str:
        """获取模型名称或路径（优先使用本地路径）"""
        if self.path and Path(self.path).exists():
            return str(self.path)
        return self.name


class LoggingSettings(BaseSettings):
    """日志配置"""

    model_config = SettingsConfigDict(env_prefix="TRANSLATOR_LOG_")

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="日志级别"
    )
    format: str = Field(
        default="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s",
        description="日志格式",
    )
    file: Path | None = Field(default=None, description="日志文件路径")
    json_output: bool = Field(default=False, description="是否输出 JSON 格式日志")


class GUISettings(BaseSettings):
    """GUI 配置"""

    model_config = SettingsConfigDict(env_prefix="TRANSLATOR_GUI_")

    theme: Literal["dark", "light"] = Field(default="dark", description="界面主题")
    window_width: int = Field(default=1100, ge=800)
    window_height: int = Field(default=800, ge=600)
    font_family: str = Field(default="Segoe UI, Microsoft YaHei, sans-serif")
    font_size: int = Field(default=10, ge=8, le=16)


class Settings(BaseSettings):
    """主配置类"""

    model_config = SettingsConfigDict(
        env_prefix="TRANSLATOR_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # 应用信息
    app_name: str = Field(default="AI Translation System")
    version: str = Field(default="2.0.0")
    debug: bool = Field(default=False)

    # 子配置
    model: ModelSettings = Field(default_factory=ModelSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    gui: GUISettings = Field(default_factory=GUISettings)

    # 文件处理
    default_encoding: str = Field(default="utf-8")
    batch_size: int = Field(default=10, ge=1, le=100)


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
