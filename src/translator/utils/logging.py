"""
日志工具模块
提供结构化日志和上下文追踪
"""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime
from functools import lru_cache
from typing import Any, ClassVar

from translator.config import get_settings

# 请求追踪 ID
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


class JSONFormatter(logging.Formatter):
    """JSON 格式日志"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加请求 ID
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data

        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """带颜色的控制台日志"""

    COLORS: ClassVar[dict[str, str]] = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET: ClassVar[str] = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


class ContextLogger(logging.LoggerAdapter):
    """带上下文的日志适配器"""

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict]:
        extra = kwargs.get("extra", {})

        # 添加请求 ID
        request_id = request_id_var.get()
        if request_id:
            extra["request_id"] = request_id

        # 合并上下文
        extra.update(self.extra)
        kwargs["extra"] = extra

        return msg, kwargs


@lru_cache
def get_logger(name: str = "translator") -> logging.Logger:
    """获取配置好的日志器"""
    settings = get_settings()

    logger = logging.getLogger(name)
    logger.setLevel(settings.logging.level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(settings.logging.level)

    if settings.logging.json_output:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter(settings.logging.format))

    logger.addHandler(console_handler)

    # 文件处理器
    if settings.logging.file:
        file_handler = logging.FileHandler(settings.logging.file, encoding="utf-8")
        file_handler.setLevel(settings.logging.level)
        file_handler.setFormatter(logging.Formatter(settings.logging.format))
        logger.addHandler(file_handler)

    return logger


def log_with_context(logger: logging.Logger, level: int, message: str, **extra_data: Any) -> None:
    """带额外上下文的日志"""
    record = logger.makeRecord(logger.name, level, "(unknown file)", 0, message, (), None)
    record.extra_data = extra_data
    logger.handle(record)
