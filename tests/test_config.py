"""
配置模块测试
"""

import pytest
from translator.config import Settings, get_settings


class TestSettings:
    """配置测试"""
    
    def test_default_settings(self):
        """测试默认配置"""
        settings = Settings()
        
        assert settings.app_name == "AI Translation System"
        assert settings.version == "2.0.0"
        assert settings.debug is False
    
    def test_model_settings(self):
        """测试模型配置"""
        settings = Settings()
        
        assert settings.model.name == "tencent/HY-MT1.5-1.8B"
        assert settings.model.use_bfloat16 is True
        assert settings.model.max_new_tokens == 2048
    
    def test_get_settings_singleton(self):
        """测试配置单例"""
        s1 = get_settings()
        s2 = get_settings()
        
        assert s1 is s2


class TestLanguageRegistry:
    """语言注册表测试"""
    
    def test_get_direction(self):
        """测试获取语言方向"""
        from src.translator.config.languages import LanguageRegistry
        
        direction = LanguageRegistry.get("en2zh")
        
        assert direction is not None
        assert direction.source == "en"
        assert direction.target == "zh"
    
    def test_get_codes(self):
        """测试获取所有代码"""
        from src.translator.config.languages import LanguageRegistry
        
        codes = LanguageRegistry.get_codes()
        
        assert "en2zh" in codes
        assert "zh2en" in codes
        assert len(codes) == 6
    
    def test_get_swap(self):
        """测试获取交换代码"""
        from src.translator.config.languages import LanguageRegistry
        
        swap = LanguageRegistry.get_swap("en2zh")
        
        assert swap == "zh2en"
