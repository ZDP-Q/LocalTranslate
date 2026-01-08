"""
文件处理工具
支持多种格式的读写
"""

import json
from pathlib import Path

from translator.config import get_settings
from translator.core.exceptions import FileProcessingError
from translator.core.models import FileFormat


class FileHandler:
    """文件处理器"""

    def __init__(self, encoding: str | None = None):
        settings = get_settings()
        self.encoding = encoding or settings.default_encoding

    def read(self, path: Path | str, format: FileFormat | None = None) -> list[str]:
        """
        读取文件内容

        Args:
            path: 文件路径
            format: 文件格式，None 时自动检测

        Returns:
            文本列表
        """
        path = Path(path)

        if not path.exists():
            raise FileProcessingError(f"File not found: {path}", file_path=str(path))

        if format is None:
            format = FileFormat.from_extension(path.suffix)

        try:
            with open(path, encoding=self.encoding) as f:
                if format == FileFormat.JSON:
                    data = json.load(f)
                    if isinstance(data, list):
                        return [str(item) for item in data]
                    return [str(data)]
                else:
                    return [line.strip() for line in f if line.strip()]

        except json.JSONDecodeError as e:
            raise FileProcessingError(f"Invalid JSON format: {e}", file_path=str(path))
        except UnicodeDecodeError as e:
            raise FileProcessingError(
                f"Encoding error: {e}", file_path=str(path), details={"encoding": self.encoding}
            )
        except Exception as e:
            raise FileProcessingError(f"Failed to read file: {e}", file_path=str(path))

    def write(self, path: Path | str, data: list[str], format: FileFormat | None = None) -> None:
        """
        写入文件

        Args:
            path: 文件路径
            data: 文本列表
            format: 文件格式，None 时自动检测
        """
        path = Path(path)

        if format is None:
            format = FileFormat.from_extension(path.suffix)

        try:
            # 确保目录存在
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding=self.encoding) as f:
                if format == FileFormat.JSON:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    f.write("\n".join(data))
                    if data:
                        f.write("\n")

        except Exception as e:
            raise FileProcessingError(f"Failed to write file: {e}", file_path=str(path))

    @staticmethod
    def detect_format(path: Path | str) -> FileFormat:
        """检测文件格式"""
        return FileFormat.from_extension(Path(path).suffix)
