"""
核心模块测试
"""

import pytest
from translator.core.models import (
    TranslationRequest,
    TranslationResult,
    BatchResult,
    TranslationStatus,
    FileFormat
)
from translator.core.exceptions import (
    TranslatorError,
    UnsupportedLanguageError,
    ValidationError,
)


class TestTranslationRequest:
    """翻译请求测试"""
    
    def test_valid_request(self):
        """测试有效请求"""
        request = TranslationRequest(
            text="Hello, world!",
            direction="en2zh"
        )
        
        assert request.text == "Hello, world!"
        assert request.direction == "en2zh"
    
    def test_text_strip(self):
        """测试文本清理"""
        request = TranslationRequest(
            text="  Hello  ",
            direction="en2zh"
        )
        
        assert request.text == "Hello"
    
    def test_direction_lowercase(self):
        """测试方向小写"""
        request = TranslationRequest(
            text="Hello",
            direction="EN2ZH"
        )
        
        assert request.direction == "en2zh"
    
    def test_empty_text_raises(self):
        """测试空文本"""
        with pytest.raises(ValueError):
            TranslationRequest(text="", direction="en2zh")


class TestTranslationResult:
    """翻译结果测试"""
    
    def test_create_result(self):
        """测试创建结果"""
        result = TranslationResult(
            source_text="Hello",
            translated_text="你好",
            direction="en2zh",
            status=TranslationStatus.COMPLETED
        )
        
        assert result.source_text == "Hello"
        assert result.translated_text == "你好"
        assert result.status == TranslationStatus.COMPLETED
    
    def test_failed_result(self):
        """测试失败结果"""
        result = TranslationResult(
            source_text="Hello",
            translated_text="",
            direction="en2zh",
            status=TranslationStatus.FAILED,
            error_message="Test error"
        )
        
        assert result.status == TranslationStatus.FAILED
        assert result.error_message == "Test error"


class TestBatchResult:
    """批量结果测试"""
    
    def test_add_result(self):
        """测试添加结果"""
        batch = BatchResult(total=2)
        
        batch.add_result(TranslationResult(
            source_text="Hello",
            translated_text="你好",
            direction="en2zh",
            processing_time_ms=100.0
        ))
        
        assert batch.successful == 1
        assert batch.failed == 0
        assert len(batch.results) == 1
    
    def test_statistics(self):
        """测试统计信息"""
        batch = BatchResult(total=2)
        
        batch.add_result(TranslationResult(
            source_text="Hello",
            translated_text="你好",
            direction="en2zh",
            processing_time_ms=100.0
        ))
        batch.add_result(TranslationResult(
            source_text="World",
            translated_text="世界",
            direction="en2zh",
            processing_time_ms=200.0
        ))
        
        assert batch.total_processing_time_ms == 300.0
        assert batch.average_time_per_item_ms == 150.0


class TestExceptions:
    """异常测试"""
    
    def test_translator_error(self):
        """测试基础异常"""
        error = TranslatorError("Test error", code="TEST")
        
        assert str(error) == "[TEST] Test error"
        assert error.code == "TEST"
    
    def test_unsupported_language_error(self):
        """测试不支持的语言异常"""
        error = UnsupportedLanguageError("xx2yy", supported=["en2zh"])
        
        assert "xx2yy" in str(error)
        assert error.details["direction"] == "xx2yy"
    
    def test_error_to_dict(self):
        """测试异常转字典"""
        error = TranslatorError("Test", code="TEST", details={"key": "value"})
        
        d = error.to_dict()
        
        assert d["code"] == "TEST"
        assert d["message"] == "Test"
        assert d["details"]["key"] == "value"


class TestFileFormat:
    """文件格式测试"""
    
    def test_from_extension(self):
        """测试从扩展名获取格式"""
        assert FileFormat.from_extension(".txt") == FileFormat.TXT
        assert FileFormat.from_extension(".json") == FileFormat.JSON
        assert FileFormat.from_extension("txt") == FileFormat.TXT
    
    def test_unknown_extension(self):
        """测试未知扩展名"""
        assert FileFormat.from_extension(".xyz") == FileFormat.TXT
