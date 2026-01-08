# AI Translation System

企业级 AI 翻译系统，基于 **Tencent HY-MT1.5** (1.8B) 模型，采用 src-layout 架构，支持中英日互译。

## ✨ 特性

- 🌍 **多语言支持**: 中英日三语互译（6个方向）
- ⚡ **高性能**: bfloat16 精度 + GPU 加速
- 🎨 **双界面**: 现代 CLI (Typer + Rich) + GUI (PySide6)
- 📦 **批量处理**: 文件翻译、批量翻译
- 🔧 **企业级**: src-layout、Pydantic 配置、完整测试
- 📝 **多格式**: TXT / JSON 输入输出

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone <repo-url>
cd ai-translation-system

# 安装依赖（推荐使用 uv）
uv sync
uv sync --extra dev  # 开发依赖
```

### 基础使用

```bash
# 单文本翻译
uv run translate --text "Hello" -d en2zh

# 交互模式
uv run translate -I -d en2zh

# 文件翻译
uv run translate -i input.txt -o output.txt -d en2zh

# GUI 界面
uv run translate-gui

# 查看支持的语言
uv run translate languages

# 显示版本
uv run translate version
```

## 📖 使用指南

### 命令行 (CLI)

```bash
# 基础翻译
uv run translate --text "Hello, world!" -d en2zh
# 输出: 你好，世界！

# 中译英
uv run translate -t "你好" -d zh2en
# 输出: Hello
```
Hello, world!
Good morning!
How are you?
```

执行翻译：
```bash
python main.py --input input.txt --output output.txt --direction en2zh
```

输出文件 `output.txt`：
```
你好，世界！
早上好！
你好吗？
```

# 日译中
uv run translate -t "こんにちは" -d ja2zh
# 输出: 你好

# 交互模式（输入 exit/quit/q 退出）
uv run translate -I -d en2zh
> Hello!
Translation: 你好！
> exit

# 文件翻译
uv run translate -i input.txt -o output.txt -d en2zh

# JSON 格式
uv run translate -i input.json -o output.json -f json -d en2zh

# 自定义提示词
uv run translate -t "Hello" -d en2zh -p "Translate to formal Chinese:"

# 使用本地模型
uv run translate -t "Hello" -d en2zh -m /path/to/model

# 禁用 bfloat16（兼容旧 GPU）
uv run translate -t "Hello" -d en2zh --no-bfloat16
```

### 图形界面 (GUI)

```bash
uv run translate-gui
```

特性：
- 🎨 **Catppuccin Mocha** 深色主题
- 📤 **文件操作**: 加载/保存 TXT/JSON
- 📋 **剪贴板**: 一键复制结果
- 🔄 **语言切换**: 动态切换翻译方向
- 📊 **实时进度**: 翻译进度条显示

### 文件格式

#### TXT 格式（每行一个文本）

```txt
Hello, world!
Good morning
How are you?
```

#### JSON 格式（数组）

```json
[
  "Hello, world!",
  "Good morning",
  "How are you?"
]
```

## 🏗️ 项目结构

```
src/translator/
├── __init__.py           # 包导出
├── config/
│   ├── settings.py       # Pydantic Settings 配置
│   └── languages.py      # 语言方向注册表
├── core/
│   ├── engine.py         # TranslationEngine 翻译引擎
│   ├── models.py         # Pydantic 数据模型
│   └── exceptions.py     # 异常层次结构
├── cli/
│   └── __init__.py       # Typer CLI (Rich 美化)
├── gui/
│   ├── app.py            # PySide6 主窗口
│   ├── styles.py         # QSS 样式
│   └── components.py     # 可复用组件
└── utils/
    ├── logging.py        # 结构化日志
    └── file_handler.py   # 文件 I/O
```

## ⚙️ 配置

通过环境变量或 `.env` 文件配置：

```bash
TRANSLATOR_MODEL_NAME=tencent/HY-MT1.5-1.8B
TRANSLATOR_MODEL_USE_BFLOAT16=true
TRANSLATOR_LOG_LEVEL=INFO
TRANSLATOR_GUI_THEME=dark
```

## 🧪 测试

```bash
# 运行所有测试
uv run pytest

# 带覆盖率
uv run pytest --cov=src/translator

# 详细输出
uv run pytest -v
```

## 🛠️ 开发

```bash
# 代码检查
uv run ruff check src/

# 代码格式化
uv run ruff format src/

# 类型检查
uv run mypy src/

# Pre-commit 钩子
pre-commit install
pre-commit run --all-files
```

## 📝 支持的语言方向


| 代码 | 方向 | 说明 |
|------|------|------|
| `en2zh` | 🇺🇸 → 🇨🇳 | English to Chinese |
| `zh2en` | 🇨🇳 → 🇺🇸 | Chinese to English |
| `en2ja` | 🇺🇸 → 🇯🇵 | English to Japanese |
| `ja2en` | 🇯🇵 → 🇺🇸 | Japanese to English |
| `zh2ja` | 🇨🇳 → 🇯🇵 | Chinese to Japanese |
| `ja2zh` | 🇯🇵 → 🇨🇳 | Japanese to Chinese |

## 🔌 API 使用

在 Python 代码中使用翻译引擎：

```python
from translator import TranslationEngine, TranslationRequest

# 初始化引擎
engine = TranslationEngine().load()

# 单文本翻译
result = engine.translate_text("Hello", "en2zh")
print(result)  # 你好

# 使用上下文管理器
with TranslationEngine() as engine:
    result = engine.translate_text("Hello", "en2zh")
    print(result)

# 批量翻译
texts = ["Hello", "Good morning"]
batch_result = engine.translate_batch(texts, "en2zh")
print(f"成功: {batch_result.success_count}/{batch_result.total}")
for r in batch_result.results:
    print(f"{r.source} -> {r.translation}")

# 文件翻译
from pathlib import Path
result = engine.translate_file(
    input_path=Path("input.txt"),
    output_path=Path("output.txt"),
    direction="en2zh"
)
```

## 📋 命令行选项

| 选项 | 短选项 | 说明 | 默认值 |
|------|--------|------|--------|
| `--text` | `-t` | 要翻译的文本 | - |
| `--input` | `-i` | 输入文件路径 | - |
| `--output` | `-o` | 输出文件路径 | - |
| `--direction` | `-d` | 翻译方向 | `en2zh` |
| `--interactive` | `-I` | 交互式模式 | `False` |
| `--model` | `-m` | 模型名称或路径 | 配置中的默认值 |
| `--no-bfloat16` | - | 禁用 bfloat16 | `False` |
| `--max-tokens` | - | 最大生成 token 数 | `2048` |
| `--prompt` | `-p` | 自定义翻译提示词 | - |
| `--format` | `-f` | 文件格式 (txt/json) | `txt` |
| `--verbose` | `-v` | 详细输出 | `False` |

## 🚨 常见问题

**Q: 首次运行很慢？**  
A: 第一次需要下载 ~4GB 模型，后续使用会从缓存加载。

**Q: CUDA out of memory？**  
A: 尝试使用 `--no-bfloat16` 或减少 `--max-tokens`。

**Q: 支持离线使用吗？**  
A: 首次联网下载模型后可离线使用。

**Q: 如何自定义翻译风格？**  
A: 使用 `--prompt` 参数提供自定义提示词。

## 📦 依赖项

| 包 | 版本 | 用途 |
|---|---|---|
| `torch` | >=2.0.0 | PyTorch 深度学习框架 |
| `transformers` | >=4.30.0 | HuggingFace 模型库 |
| `accelerate` | >=0.20.0 | 模型加速 |
| `pydantic` | >=2.0.0 | 数据验证 |
| `pydantic-settings` | >=2.0.0 | 配置管理 |
| `typer` | >=0.9.0 | CLI 框架 |
| `rich` | >=13.0.0 | 终端美化 |
| `PySide6` | >=6.5.0 | Qt6 GUI |

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🔗 相关链接

- [Tencent HY-MT1.5 Model](https://huggingface.co/tencent/HY-MT1.5-1.8B)
- [Transformers](https://github.com/huggingface/transformers)
- [Project Documentation](#)

---

**企业级 AI 翻译系统** - 基于 Tencent HY-MT1.5 | 支持中英日互译 | MIT License
