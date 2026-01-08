"""
AI Translation System
企业级翻译系统，基于 HY-MT1.5 模型
"""

from translator.config import settings
from translator.core.engine import TranslationEngine
from translator.core.models import TranslationRequest, TranslationResult

__version__ = "2.0.0"
__all__ = [
    "TranslationEngine",
    "TranslationRequest",
    "TranslationResult",
    "settings",
]
