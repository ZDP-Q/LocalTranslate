"""
数据模型定义
使用 Pydantic 进行数据验证
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class TranslationStatus(str, Enum):
    """翻译状态"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranslationRequest(BaseModel):
    """翻译请求"""

    text: str = Field(..., min_length=1, max_length=50000, description="待翻译文本")
    direction: str = Field(default="en2zh", description="翻译方向")
    custom_prompt: str | None = Field(default=None, description="自定义提示词")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """验证并清理文本"""
        return v.strip()

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, v: str) -> str:
        """验证翻译方向格式"""
        if not v or "2" not in v:
            raise ValueError(f"Invalid direction format: {v}")
        return v.lower()


class TranslationResult(BaseModel):
    """翻译结果"""

    source_text: str = Field(..., description="原文")
    translated_text: str = Field(..., description="译文")
    direction: str = Field(..., description="翻译方向")
    status: TranslationStatus = Field(default=TranslationStatus.COMPLETED)

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    processing_time_ms: float | None = Field(default=None, description="处理时间(毫秒)")
    token_count: int | None = Field(default=None, description="生成的 token 数")
    error_message: str | None = Field(default=None, description="错误信息")

    model_config = {"frozen": False}


class BatchRequest(BaseModel):
    """批量翻译请求"""

    texts: list[str] = Field(..., min_length=1, max_length=1000)
    direction: str = Field(default="en2zh")
    custom_prompt: str | None = None

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, v: list[str]) -> list[str]:
        """验证并过滤空文本"""
        return [text.strip() for text in v if text.strip()]


class BatchResult(BaseModel):
    """批量翻译结果"""

    results: list[TranslationResult] = Field(default_factory=list)
    total: int = Field(..., description="总数")
    successful: int = Field(default=0, description="成功数")
    failed: int = Field(default=0, description="失败数")

    # 统计信息
    total_processing_time_ms: float = Field(default=0.0)
    average_time_per_item_ms: float = Field(default=0.0)

    def add_result(self, result: TranslationResult) -> None:
        """添加结果"""
        self.results.append(result)
        if result.status == TranslationStatus.COMPLETED:
            self.successful += 1
        else:
            self.failed += 1

        if result.processing_time_ms:
            self.total_processing_time_ms += result.processing_time_ms

        if self.results:
            self.average_time_per_item_ms = self.total_processing_time_ms / len(self.results)


class FileFormat(str, Enum):
    """支持的文件格式"""

    TXT = "txt"
    JSON = "json"

    @classmethod
    def from_extension(cls, ext: str) -> "FileFormat":
        """从扩展名获取格式"""
        ext = ext.lower().lstrip(".")
        try:
            return cls(ext)
        except ValueError:
            return cls.TXT
