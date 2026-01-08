# AI Translation System - Copilot Instructions

## Project Overview

企业级 AI 翻译系统，基于 **Tencent HY-MT1.5** (1.8B 参数)，采用 src-layout 架构，支持中英日互译。

## Architecture

```
src/translator/
├── __init__.py           # 包导出
├── config/
│   ├── __init__.py       # 配置入口 (Settings, get_settings)
│   ├── settings.py       # Pydantic Settings 配置管理
│   └── languages.py      # 语言方向注册表 (LanguageRegistry)
├── core/
│   ├── __init__.py       # 核心模块导出
│   ├── engine.py         # TranslationEngine 翻译引擎
│   ├── models.py         # Pydantic 数据模型
│   └── exceptions.py     # 异常层次结构
├── cli/
│   └── __init__.py       # Typer CLI (Rich 美化输出)
├── gui/
│   ├── __init__.py       # GUI 导出
│   ├── app.py            # PySide6 主窗口
│   ├── styles.py         # QSS 样式定义
│   └── components.py     # 可复用组件
└── utils/
    ├── __init__.py       # 工具导出
    ├── logging.py        # 结构化日志
    └── file_handler.py   # 文件 I/O
tests/                    # pytest 测试
```

### Key Design Patterns

```python
# 配置使用 Pydantic Settings (支持环境变量和 .env)
from src.translator.config import settings
print(settings.model.name)  # TRANSLATOR_MODEL_NAME

# 翻译引擎支持上下文管理器
with TranslationEngine() as engine:
    result = engine.translate_text("Hello", "en2zh")

# 语言方向通过注册表管理
LanguageRegistry.register(LanguageDirection(...))
direction = LanguageRegistry.get("en2zh")
```

## Development Commands

```bash
# 安装依赖
uv sync
uv sync --extra dev  # 开发依赖

# 运行应用
uv run translate --text "Hello" -d en2zh  # 单文本翻译
uv run translate -I -d en2zh              # 交互模式
uv run translate languages                # 显示支持的语言
uv run translate version                  # 显示版本信息
uv run translate-gui                      # 启动 GUI

# 文件翻译
uv run translate -i input.txt -o output.txt -d en2zh

# 测试
uv run pytest
uv run pytest --cov=src/translator

# 代码质量
uv run ruff check src/
uv run ruff format src/
uv run mypy src/

# Pre-commit
pre-commit install
pre-commit run --all-files
```

## Configuration

通过环境变量或 `.env` 文件配置:

```bash
TRANSLATOR_MODEL_NAME=tencent/HY-MT1.5-1.8B
TRANSLATOR_MODEL_USE_BFLOAT16=true
TRANSLATOR_LOG_LEVEL=INFO
TRANSLATOR_GUI_THEME=dark
```

## Important Conventions

1. **类型注解**: 所有公共 API 必须有完整类型注解
2. **异常处理**: 使用 `TranslatorError` 异常层次，包含 `code` 和 `details`
3. **数据模型**: 使用 Pydantic `BaseModel` 进行验证
4. **日志**: 使用 `get_logger(__name__)` 获取模块日志器
5. **文件编码**: 所有 I/O 显式使用 UTF-8
6. **导入路径**: 使用 `from translator.xxx` 而不是 `from src.translator.xxx`

## Extending the System

### 添加新语言方向
```python
# src/translator/config/languages.py
LanguageRegistry.register(LanguageDirection(
    code="ko2en",
    source="ko",
    target="en",
    prompt="Translate into English...",
    description="Korean to English",
    display="🇰🇷 韩语 → 🇺🇸 英语"
))
```

### 添加新配置项
```python
# src/translator/config/settings.py
class NewSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TRANSLATOR_NEW_")
    option: str = Field(default="value")

# 在 Settings 类中添加
new: NewSettings = Field(default_factory=NewSettings)
```

## Dependencies

| 包 | 用途 |
|---|---|
| `pydantic-settings` | 类型安全配置管理 |
| `typer` + `rich` | 现代 CLI 框架 |
| `PySide6` | Qt6 GUI |
| `torch` + `transformers` | 模型推理 |
| `ruff` | Linting + Formatting |
| `pytest` | 测试框架 |
