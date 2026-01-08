"""
语言配置
定义支持的语言方向和提示词模板
"""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class LanguageDirection:
    """语言方向定义"""

    code: str
    source: str
    target: str
    prompt: str
    description: str
    display: str

    @property
    def reverse_code(self) -> str:
        """获取反向代码"""
        return f"{self.target}2{self.source}"


class LanguageRegistry:
    """语言注册表"""

    _directions: ClassVar[dict[str, LanguageDirection]] = {}

    @classmethod
    def register(cls, direction: LanguageDirection) -> None:
        """注册语言方向"""
        cls._directions[direction.code] = direction

    @classmethod
    def get(cls, code: str) -> LanguageDirection | None:
        """获取语言方向"""
        return cls._directions.get(code)

    @classmethod
    def get_all(cls) -> dict[str, LanguageDirection]:
        """获取所有语言方向"""
        return cls._directions.copy()

    @classmethod
    def get_codes(cls) -> list[str]:
        """获取所有代码"""
        return list(cls._directions.keys())

    @classmethod
    def get_swap(cls, code: str) -> str | None:
        """获取交换后的代码"""
        direction = cls.get(code)
        if direction:
            return direction.reverse_code
        return None


# 预定义语言方向
_PREDEFINED_DIRECTIONS = [
    LanguageDirection(
        code="en2zh",
        source="en",
        target="zh",
        prompt="Translate the following segment into Chinese, without additional explanation.",
        description="English to Chinese",
        display="🇺🇸 英语 → 🇨🇳 中文",
    ),
    LanguageDirection(
        code="zh2en",
        source="zh",
        target="en",
        prompt="Translate the following segment into English, without additional explanation.",
        description="Chinese to English",
        display="🇨🇳 中文 → 🇺🇸 英语",
    ),
    LanguageDirection(
        code="en2ja",
        source="en",
        target="ja",
        prompt="Translate the following segment into Japanese, without additional explanation.",
        description="English to Japanese",
        display="🇺🇸 英语 → 🇯🇵 日语",
    ),
    LanguageDirection(
        code="ja2en",
        source="ja",
        target="en",
        prompt="Translate the following segment into English, without additional explanation.",
        description="Japanese to English",
        display="🇯🇵 日语 → 🇺🇸 英语",
    ),
    LanguageDirection(
        code="zh2ja",
        source="zh",
        target="ja",
        prompt="Translate the following segment into Japanese, without additional explanation.",
        description="Chinese to Japanese",
        display="🇨🇳 中文 → 🇯🇵 日语",
    ),
    LanguageDirection(
        code="ja2zh",
        source="ja",
        target="zh",
        prompt="Translate the following segment into Chinese, without additional explanation.",
        description="Japanese to Chinese",
        display="🇯🇵 日语 → 🇨🇳 中文",
    ),
]

# 注册预定义语言方向
for direction in _PREDEFINED_DIRECTIONS:
    LanguageRegistry.register(direction)
