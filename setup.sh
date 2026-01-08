#!/bin/bash

# ====================================================================
# AI Translation System - Linux/macOS 一键安装脚本
# ====================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 输出函数
print_step() { echo -e "${CYAN}===> $1${NC}"; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_warning() { echo -e "${YELLOW}! $1${NC}"; }

echo -e "${CYAN}"
cat << "EOF"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          AI Translation System - 一键安装工具                 ║
║          Enterprise-grade Translation with HY-MT1.5           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

EOF
echo -e "${NC}"

# ====================================================================
# 1. 检查并安装 uv
# ====================================================================
print_step "检查 uv 包管理器..."

if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    print_success "uv 已安装: $UV_VERSION"
else
    print_warning "uv 未安装，开始自动安装..."
    
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        # 添加到当前 shell
        export PATH="$HOME/.cargo/bin:$PATH"
        print_success "uv 安装成功！"
    else
        print_error "uv 安装失败"
        echo "请手动安装 uv: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
fi

# ====================================================================
# 2. 检查 Python
# ====================================================================
print_step "检查 Python 环境..."

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python 已安装: $PYTHON_VERSION"
else
    print_warning "未检测到 Python，uv 将自动管理 Python 版本"
fi

# ====================================================================
# 3. 创建 .env 配置文件
# ====================================================================
print_step "配置环境变量..."

if [ ! -f ".env" ]; then
    cp ".env.example" ".env"
    print_success "创建 .env 配置文件"
else
    print_warning ".env 文件已存在，跳过创建"
fi

# ====================================================================
# 4. 检查 HuggingFace 连接性
# ====================================================================
print_step "检查 HuggingFace 连接性..."

HF_MIRROR=""
if curl -s --connect-timeout 5 https://huggingface.co > /dev/null 2>&1; then
    print_success "可以访问 HuggingFace 官网"
else
    print_warning "无法访问 HuggingFace 官网，将使用中国镜像"
    HF_MIRROR="https://hf-mirror.com"
    
    # 设置环境变量
    export HF_ENDPOINT=$HF_MIRROR
    
    # 添加到 .env 文件
    if ! grep -q "HF_ENDPOINT" .env; then
        echo "" >> .env
        echo "# HuggingFace Mirror for China" >> .env
        echo "HF_ENDPOINT=$HF_MIRROR" >> .env
        print_success "已配置 HuggingFace 中国镜像: $HF_MIRROR"
    fi
fi

# ====================================================================
# 5. 询问模型存储路径
# ====================================================================
print_step "配置模型存储路径..."

DEFAULT_MODEL_PATH="$(pwd)/models"
echo ""
echo "请选择模型存储方式:"
echo "  1. 使用默认缓存路径（~/.cache/huggingface）"
echo "  2. 下载到项目目录（推荐）: $DEFAULT_MODEL_PATH"
echo "  3. 自定义路径"
echo ""

read -p "请输入选择 (1/2/3) [默认: 2]: " CHOICE
CHOICE=${CHOICE:-2}

case $CHOICE in
    1)
        print_success "使用默认缓存路径"
        MODEL_PATH=""
        ;;
    2)
        MODEL_PATH="$DEFAULT_MODEL_PATH"
        print_success "模型将下载到: $MODEL_PATH"
        ;;
    3)
        read -p "请输入自定义路径: " CUSTOM_PATH
        MODEL_PATH="$CUSTOM_PATH"
        print_success "模型将下载到: $MODEL_PATH"
        ;;
    *)
        MODEL_PATH="$DEFAULT_MODEL_PATH"
        print_success "使用默认项目路径: $MODEL_PATH"
        ;;
esac

# 更新 .env 配置
if [ -n "$MODEL_PATH" ]; then
    # 创建模型目录
    if [ ! -d "$MODEL_PATH" ]; then
        mkdir -p "$MODEL_PATH"
        print_success "创建模型目录: $MODEL_PATH"
    fi
    
    # 更新配置文件
    if grep -q "TRANSLATOR_MODEL_PATH=" .env; then
        sed -i.bak "s|TRANSLATOR_MODEL_PATH=.*|TRANSLATOR_MODEL_PATH=$MODEL_PATH|" .env
        rm -f .env.bak
    else
        echo "" >> .env
        echo "# Local Model Path" >> .env
        echo "TRANSLATOR_MODEL_PATH=$MODEL_PATH" >> .env
    fi
    print_success "已配置模型路径到 .env"
fi

# ====================================================================
# 6. 安装依赖
# ====================================================================
print_step "安装项目依赖..."

echo -e "${YELLOW}这可能需要几分钟时间...${NC}"
if uv sync; then
    print_success "依赖安装完成"
else
    print_error "依赖安装失败"
    exit 1
fi

print_step "安装开发依赖..."
if uv sync --extra dev; then
    print_success "开发依赖安装完成"
else
    print_warning "开发依赖安装失败，但不影响使用"
fi

# ====================================================================
# 7. 下载模型
# ====================================================================
print_step "准备下载翻译模型..."

echo ""
echo "是否现在下载模型？(模型大小约 4GB)"
echo "  Y - 立即下载"
echo "  N - 稍后下载（首次运行时自动下载）"
echo ""

read -p "请选择 (Y/N) [默认: N]: " DOWNLOAD_NOW
DOWNLOAD_NOW=${DOWNLOAD_NOW:-N}

if [ "$DOWNLOAD_NOW" = "Y" ] || [ "$DOWNLOAD_NOW" = "y" ]; then
    print_step "开始下载模型（tencent/HY-MT1.5-1.8B）..."
    echo -e "${YELLOW}这可能需要较长时间，请耐心等待...${NC}"
    
    if [ -n "$HF_MIRROR" ]; then
        export HF_ENDPOINT=$HF_MIRROR
    fi
    
    # 使用 Python 脚本下载模型
    if uv run python -c "
from translator.core.engine import TranslationEngine
print('正在下载模型...')
engine = TranslationEngine().load()
print('模型下载完成！')
engine.unload()
"; then
        print_success "模型下载完成！"
    else
        print_warning "模型下载失败，但不影响安装"
        echo "您可以稍后运行程序时自动下载"
    fi
else
    print_success "跳过模型下载，将在首次使用时自动下载"
fi

# ====================================================================
# 8. 运行测试
# ====================================================================
print_step "运行测试验证安装..."

if uv run pytest -q; then
    print_success "所有测试通过！"
else
    print_warning "部分测试失败，但不影响使用"
fi

# ====================================================================
# 完成
# ====================================================================
echo -e "${GREEN}"
cat << "EOF"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                    🎉 安装完成！                              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

EOF
echo -e "${NC}"

echo -e "${CYAN}快速开始：${NC}"
echo ""
echo -e "  ${NC}# 查看支持的语言${NC}"
echo -e "  ${YELLOW}uv run translate languages${NC}"
echo ""
echo -e "  ${NC}# 交互式翻译${NC}"
echo -e "  ${YELLOW}uv run translate -I -d en2zh${NC}"
echo ""
echo -e "  ${NC}# 单文本翻译${NC}"
echo -e "  ${YELLOW}uv run translate --text 'Hello' -d en2zh${NC}"
echo ""
echo -e "  ${NC}# 启动 GUI${NC}"
echo -e "  ${YELLOW}uv run translate-gui${NC}"
echo ""

echo -e "${CYAN}更多信息请查看 README.md${NC}"
echo ""
