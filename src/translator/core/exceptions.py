"""
异常定义模块
定义统一的异常层次结构
"""

from typing import Any


class TranslatorError(Exception):
    """翻译系统基础异常"""

    def __init__(
        self, message: str, *, code: str = "UNKNOWN_ERROR", details: dict[str, Any] | None = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {"code": self.code, "message": self.message, "details": self.details}


class ConfigurationError(TranslatorError):
    """配置错误"""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, code="CONFIG_ERROR", **kwargs)


class ModelError(TranslatorError):
    """模型相关错误的基类"""

    pass


class ModelLoadError(ModelError):
    """模型加载错误"""

    def __init__(self, message: str, model_name: str = "", **kwargs):
        details = kwargs.pop("details", {})
        details["model_name"] = model_name
        super().__init__(message, code="MODEL_LOAD_ERROR", details=details, **kwargs)


class ModelInferenceError(ModelError):
    """模型推理错误"""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, code="MODEL_INFERENCE_ERROR", **kwargs)


class TranslationError(TranslatorError):
    """翻译错误的基类"""

    pass


class UnsupportedLanguageError(TranslationError):
    """不支持的语言方向"""

    def __init__(self, direction: str, supported: list[str] | None = None):
        details = {"direction": direction}
        if supported:
            details["supported"] = supported
        super().__init__(
            f"Unsupported language direction: {direction}",
            code="UNSUPPORTED_LANGUAGE",
            details=details,
        )


class TranslationTimeoutError(TranslationError):
    """翻译超时"""

    def __init__(self, timeout: float):
        super().__init__(
            f"Translation timed out after {timeout}s",
            code="TRANSLATION_TIMEOUT",
            details={"timeout": timeout},
        )


class FileProcessingError(TranslatorError):
    """文件处理错误"""

    def __init__(self, message: str, file_path: str = "", **kwargs):
        details = kwargs.pop("details", {})
        details["file_path"] = file_path
        super().__init__(message, code="FILE_PROCESSING_ERROR", details=details, **kwargs)


class ValidationError(TranslatorError):
    """输入验证错误"""

    def __init__(self, message: str, field: str = "", **kwargs):
        details = kwargs.pop("details", {})
        details["field"] = field
        super().__init__(message, code="VALIDATION_ERROR", details=details, **kwargs)
