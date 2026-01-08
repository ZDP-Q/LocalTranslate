"""
测试配置
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_texts():
    """示例文本"""
    return [
        "Hello, world!",
        "Good morning!",
        "How are you today?"
    ]


@pytest.fixture
def temp_file(tmp_path):
    """临时文件"""
    def _create(content: str, suffix: str = ".txt"):
        file = tmp_path / f"test{suffix}"
        file.write_text(content, encoding="utf-8")
        return file
    return _create


@pytest.fixture
def mock_engine(mocker):
    """Mock 翻译引擎"""
    engine = mocker.MagicMock()
    engine.translate_text.return_value = "翻译结果"
    engine.is_loaded = True
    engine.device = "cpu"
    return engine
