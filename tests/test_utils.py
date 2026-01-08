"""
文件处理测试
"""

import json
import pytest
from pathlib import Path

from translator.utils.file_handler import FileHandler
from translator.core.models import FileFormat
from translator.core.exceptions import FileProcessingError


class TestFileHandler:
    """文件处理器测试"""
    
    def test_read_txt(self, tmp_path):
        """测试读取 TXT"""
        file = tmp_path / "test.txt"
        file.write_text("Line 1\nLine 2\nLine 3", encoding="utf-8")
        
        handler = FileHandler()
        result = handler.read(file)
        
        assert len(result) == 3
        assert result[0] == "Line 1"
    
    def test_read_json(self, tmp_path):
        """测试读取 JSON"""
        file = tmp_path / "test.json"
        data = ["Item 1", "Item 2", "Item 3"]
        file.write_text(json.dumps(data), encoding="utf-8")
        
        handler = FileHandler()
        result = handler.read(file, FileFormat.JSON)
        
        assert len(result) == 3
        assert result[0] == "Item 1"
    
    def test_read_nonexistent(self, tmp_path):
        """测试读取不存在的文件"""
        handler = FileHandler()
        
        with pytest.raises(FileProcessingError) as exc:
            handler.read(tmp_path / "nonexistent.txt")
        
        assert "not found" in str(exc.value).lower()
    
    def test_write_txt(self, tmp_path):
        """测试写入 TXT"""
        file = tmp_path / "output.txt"
        data = ["Line 1", "Line 2"]
        
        handler = FileHandler()
        handler.write(file, data, FileFormat.TXT)
        
        content = file.read_text(encoding="utf-8")
        assert "Line 1" in content
        assert "Line 2" in content
    
    def test_write_json(self, tmp_path):
        """测试写入 JSON"""
        file = tmp_path / "output.json"
        data = ["Item 1", "Item 2"]
        
        handler = FileHandler()
        handler.write(file, data, FileFormat.JSON)
        
        result = json.loads(file.read_text(encoding="utf-8"))
        assert result == data
    
    def test_auto_detect_format(self):
        """测试自动检测格式"""
        assert FileHandler.detect_format("file.txt") == FileFormat.TXT
        assert FileHandler.detect_format("file.json") == FileFormat.JSON
        assert FileHandler.detect_format(Path("dir/file.json")) == FileFormat.JSON
    
    def test_create_parent_dirs(self, tmp_path):
        """测试自动创建父目录"""
        file = tmp_path / "subdir" / "nested" / "output.txt"
        
        handler = FileHandler()
        handler.write(file, ["test"])
        
        assert file.exists()
