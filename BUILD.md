# Nuitka 编译指南

## 📦 使用 Nuitka 编译可执行文件

本项目支持使用 Nuitka 将 Python 代码编译为原生可执行文件，大幅提升启动速度和运行性能。

## 🚀 快速开始

### Windows

```powershell
# 编译 CLI 版本（独立目录）
.\build.ps1

# 编译 CLI 版本（单文件）
.\build.ps1 -Onefile

# 编译 GUI 版本
.\build.ps1 -Gui

# 编译 GUI 单文件版本
.\build.ps1 -Gui -Onefile
```

### Linux / macOS

```bash
# 添加执行权限
chmod +x build.sh

# 编译 CLI 版本（独立目录）
./build.sh

# 编译 CLI 版本（单文件）
./build.sh --onefile

# 编译 GUI 版本
./build.sh --gui

# 编译 GUI 单文件版本
./build.sh --gui --onefile
```

## 📋 前置要求

### 必需组件

1. **Python 3.11+** - 已安装并配置
2. **C 编译器**:
   - Windows: Visual Studio 2019+ 或 MinGW64
   - Linux: GCC
   - macOS: Xcode Command Line Tools

3. **Nuitka**:
   ```bash
   uv pip install nuitka ordered-set
   ```

### 可选组件

- **ccache** - 加速重复编译
- **upx** - 压缩可执行文件（使用 `--onefile` 时）

## 🔧 编译选项

### 编译模式

| 模式 | 参数 | 说明 | 大小 | 启动速度 |
|------|------|------|------|----------|
| **独立目录** | `--standalone` (默认) | 包含所有依赖的目录 | 较大 | 快 |
| **单文件** | `--onefile` | 单个可执行文件 | 较小 | 较慢（首次解压） |
| **加速** | 无 | 仅编译，仍需 Python 环境 | 最小 | 最快 |

### 目标应用

- **CLI**: 命令行翻译工具
- **GUI**: 图形界面应用

## 📁 输出结构

### 独立目录模式

```
build/
├── Translate.dist/          # CLI 版本
│   ├── Translate.exe        # 主程序
│   ├── python3xx.dll        # Python 运行时
│   ├── translator/          # 包文件
│   └── [其他依赖 DLL]
└── TranslateGUI.dist/       # GUI 版本
    ├── TranslateGUI.exe
    └── [依赖文件]
```

### 单文件模式

```
build/
├── Translate.exe            # CLI 单文件
└── TranslateGUI.exe         # GUI 单文件
```

## 🎯 使用编译后的程序

### CLI 版本

```bash
# Windows
.\build\Translate.dist\Translate.exe --help
.\build\Translate.dist\Translate.exe -t "Hello" -d en2zh

# Linux/macOS
./build/Translate.dist/Translate --help
./build/Translate.dist/Translate -t "Hello" -d en2zh
```

### GUI 版本

直接双击运行 `TranslateGUI.exe`

## 📝 注意事项

### 1. 模型文件

编译后的程序**不包含**翻译模型（~4GB），首次运行需要：

**方式 1: 自动下载**
```bash
# 首次运行会自动下载模型到 ~/.cache/huggingface
./Translate.exe -t "test" -d en2zh
```

**方式 2: 手动配置本地模型**
```bash
# 1. 下载模型
./Translate.exe download -o ./models

# 2. 设置环境变量
# Windows
set TRANSLATOR_MODEL_PATH=D:\path\to\models\tencent--HY-MT1.5-1.8B

# Linux/macOS
export TRANSLATOR_MODEL_PATH=/path/to/models/tencent--HY-MT1.5-1.8B

# 3. 运行
./Translate.exe -t "Hello" -d en2zh
```

### 2. 环境变量

编译后的程序仍然支持所有环境变量配置：

```bash
TRANSLATOR_MODEL_PATH=/path/to/model
TRANSLATOR_MODEL_USE_BFLOAT16=true
TRANSLATOR_LOG_LEVEL=INFO
HF_ENDPOINT=https://hf-mirror.com  # 中国镜像
```

### 3. 依赖冲突

如果编译时遇到依赖问题：

```bash
# 清理构建缓存
rm -rf build/ __pycache__/

# 重新编译
./build.sh
```

### 4. 文件大小

编译后的程序会比较大（~500MB-2GB），因为包含了：
- Python 运行时
- PyTorch 库
- Transformers 库
- 所有依赖包

可以使用 `--onefile` 减小发布大小，但首次启动会较慢。

## 🔍 高级选项

### 手动编译命令

如果需要更多控制，可以直接使用 Nuitka：

```bash
# CLI 版本
python -m nuitka \
    --standalone \
    --assume-yes-for-downloads \
    --output-dir=build \
    --output-filename=Translate \
    --include-package=translator \
    --include-package=torch \
    --include-package=transformers \
    --include-package=accelerate \
    --include-package=huggingface_hub \
    --include-package=pydantic \
    --include-package=pydantic_settings \
    --include-package=typer \
    --include-package=rich \
    --include-data-dir=src/translator=translator \
    --nofollow-import-to=pytest \
    --nofollow-import-to=setuptools \
    --enable-plugin=anti-bloat \
    translate_cli.py

# GUI 版本（Windows）
python -m nuitka \
    --standalone \
    --windows-console-mode=disable \
    --windows-icon-from-ico=assets/icon.ico \
    --include-package=PySide6 \
    [其他选项同上] \
    translate_gui.py
```

### 使用配置文件

```bash
python -m nuitka --use-nuitka-spec=nuitka.spec translate_cli.py
```

## 📊 性能对比

| 指标 | Python 解释器 | Nuitka 编译 | 提升 |
|------|---------------|-------------|------|
| 启动时间 | ~2-3s | ~0.5-1s | 2-3x |
| 首次翻译 | ~5s | ~5s | 相同 |
| 后续翻译 | ~0.1s | ~0.1s | 相同 |
| 文件大小 | ~50MB (依赖) | ~500MB-2GB | - |

**注意**: 模型推理性能相同，主要提升在程序启动速度。

## 🐛 常见问题

### Q: 编译失败 "C compiler not found"

**A**: 安装 C 编译器
- Windows: 安装 Visual Studio 2019+ (Community 版本) 或 MinGW64
- Linux: `sudo apt install gcc` 或 `sudo yum install gcc`
- macOS: `xcode-select --install`

### Q: 编译很慢

**A**: 首次编译会下载 Nuitka 缓存，后续编译会快很多。可以安装 ccache 加速：
```bash
# Windows: choco install ccache
# Linux: sudo apt install ccache
# macOS: brew install ccache
```

### Q: 可执行文件太大

**A**: 这是正常的，因为包含了所有依赖。可以：
1. 使用 `--onefile` 模式
2. 使用 UPX 压缩
3. 只编译需要的部分

### Q: 运行时找不到模型

**A**: 编译后的程序不包含模型文件，需要：
1. 首次运行时联网下载
2. 或预先下载模型并设置 `TRANSLATOR_MODEL_PATH` 环境变量

### Q: GUI 版本显示控制台窗口

**A**: 使用 `--windows-console-mode=disable` 选项（已包含在 `build.ps1 -Gui` 中）

## 📚 更多资源

- [Nuitka 官方文档](https://nuitka.net/doc/user-manual.html)
- [Nuitka GitHub](https://github.com/Nuitka/Nuitka)
- [性能优化指南](https://nuitka.net/pages/overview.html)

## 🔄 更新编译

当代码更新后，重新运行编译脚本即可：

```bash
# Windows
.\build.ps1

# Linux/macOS  
./build.sh
```

## 📦 发布建议

打包发布时建议：

1. **包含 README**：说明如何下载模型
2. **提供安装脚本**：自动配置环境变量
3. **测试环境**：在干净的系统上测试
4. **版本控制**：使用 `-v` 选项添加版本信息

```bash
python -m nuitka --standalone --product-version=2.1.0 translate_cli.py
```
