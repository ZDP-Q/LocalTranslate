#!/bin/bash

# ====================================================================
# Nuitka 编译脚本 - Linux/macOS
# ====================================================================

set -e

GUI=false
ONEFILE=false
STANDALONE=true

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --gui)
            GUI=true
            shift
            ;;
        --onefile)
            ONEFILE=true
            STANDALONE=false
            shift
            ;;
        --standalone)
            STANDALONE=true
            shift
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

echo "====================================="
echo "  AI Translation System - 编译工具  "
echo "====================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3"
    exit 1
fi

# 确定编译目标
if [ "$GUI" = true ]; then
    TARGET="translate-gui"
    ENTRY_POINT="src/translator/gui/__init__.py"
    OUTPUT_NAME="TranslateGUI"
    echo "编译目标: GUI 应用"
else
    TARGET="translate"
    ENTRY_POINT="src/translator/cli/__init__.py"
    OUTPUT_NAME="Translate"
    echo "编译目标: CLI 应用"
fi

# 构建 Nuitka 命令
NUITKA_ARGS=(
    "-m" "nuitka"
    "--assume-yes-for-downloads"
    "--output-dir=build"
    "--output-filename=$OUTPUT_NAME"
)

# 编译模式
if [ "$ONEFILE" = true ]; then
    NUITKA_ARGS+=("--onefile")
    echo "模式: 单文件"
elif [ "$STANDALONE" = true ]; then
    NUITKA_ARGS+=("--standalone")
    echo "模式: 独立目录"
else
    echo "模式: 加速"
fi

# 包含必要的包
NUITKA_ARGS+=(
    "--include-package=translator"
    "--include-package=torch"
    "--include-package=transformers"
    "--include-package=accelerate"
    "--include-package=huggingface_hub"
    "--include-package=pydantic"
    "--include-package=pydantic_settings"
    "--include-package=typer"
    "--include-package=rich"
)

if [ "$GUI" = true ]; then
    NUITKA_ARGS+=("--include-package=PySide6")
fi

# 数据文件
NUITKA_ARGS+=(
    "--include-data-dir=src/translator=translator"
    "--nofollow-import-to=pytest"
    "--nofollow-import-to=setuptools"
)

# 优化选项
NUITKA_ARGS+=(
    "--enable-plugin=anti-bloat"
    "--python-flag=no_site"
    "--python-flag=no_warnings"
)

# 添加入口点
NUITKA_ARGS+=("$ENTRY_POINT")

echo ""
echo "开始编译..."
echo "命令: python3 ${NUITKA_ARGS[*]}"
echo ""

# 执行编译
if python3 "${NUITKA_ARGS[@]}"; then
    echo ""
    echo "====================================="
    echo "  编译成功！"
    echo "====================================="
    echo ""
    echo "输出目录: build/"
    
    if [ "$ONEFILE" = true ]; then
        echo "可执行文件: build/$OUTPUT_NAME"
    else
        echo "可执行文件: build/$OUTPUT_NAME.dist/$OUTPUT_NAME"
    fi
    
    echo ""
    echo "提示: 首次运行需要联网下载模型，或使用:"
    echo "  translate download -o ./models"
    echo "  然后设置环境变量 TRANSLATOR_MODEL_PATH"
else
    echo "编译失败！"
    exit 1
fi
