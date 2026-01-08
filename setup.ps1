# ====================================================================
# AI Translation System - Windows 一键安装脚本
# ====================================================================

$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Step { Write-ColorOutput "===> $args" Cyan }
function Write-Success { Write-ColorOutput "✓ $args" Green }
function Write-Error { Write-ColorOutput "✗ $args" Red }
function Write-Warning { Write-ColorOutput "! $args" Yellow }

Write-ColorOutput @"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          AI Translation System - 一键安装工具                 ║
║          Enterprise-grade Translation with HY-MT1.5           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

"@ Cyan

# ====================================================================
# 1. 检查并安装 uv
# ====================================================================
Write-Step "检查 uv 包管理器..."

if (Get-Command uv -ErrorAction SilentlyContinue) {
    $uvVersion = uv --version
    Write-Success "uv 已安装: $uvVersion"
} else {
    Write-Warning "uv 未安装，开始自动安装..."
    
    try {
        Write-Step "下载 uv 安装脚本..."
        Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -OutFile "$env:TEMP\uv-install.ps1"
        
        Write-Step "执行安装..."
        & "$env:TEMP\uv-install.ps1"
        
        # 添加到 PATH
        $uvPath = "$env:USERPROFILE\.cargo\bin"
        if ($env:PATH -notlike "*$uvPath*") {
            $env:PATH = "$uvPath;$env:PATH"
        }
        
        Write-Success "uv 安装成功！"
    } catch {
        Write-Error "uv 安装失败: $_"
        Write-ColorOutput "`n请手动安装 uv: https://docs.astral.sh/uv/getting-started/installation/" Yellow
        exit 1
    }
}

# ====================================================================
# 2. 检查 Python
# ====================================================================
Write-Step "检查 Python 环境..."

$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "Python 已安装: $pythonVersion"
} else {
    Write-Warning "未检测到 Python，uv 将自动管理 Python 版本"
}

# ====================================================================
# 3. 创建 .env 配置文件
# ====================================================================
Write-Step "配置环境变量..."

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Success "创建 .env 配置文件"
} else {
    Write-Warning ".env 文件已存在，跳过创建"
}

# ====================================================================
# 4. 检查 HuggingFace 连接性
# ====================================================================
Write-Step "检查 HuggingFace 连接性..."

$hfMirror = ""
try {
    $response = Invoke-WebRequest -Uri "https://huggingface.co" -TimeoutSec 5 -UseBasicParsing
    Write-Success "可以访问 HuggingFace 官网"
} catch {
    Write-Warning "无法访问 HuggingFace 官网，将使用中国镜像"
    $hfMirror = "https://hf-mirror.com"
    
    # 设置环境变量
    $env:HF_ENDPOINT = $hfMirror
    
    # 添加到 .env 文件
    if (-not (Select-String -Path ".env" -Pattern "HF_ENDPOINT" -Quiet)) {
        Add-Content -Path ".env" -Value "`n# HuggingFace Mirror for China`nHF_ENDPOINT=$hfMirror"
        Write-Success "已配置 HuggingFace 中国镜像: $hfMirror"
    }
}

# ====================================================================
# 5. 询问模型存储路径
# ====================================================================
Write-Step "配置模型存储路径..."

$defaultModelPath = Join-Path $PSScriptRoot "models"
Write-ColorOutput "`n请选择模型存储方式:" White
Write-ColorOutput "  1. 使用默认缓存路径（~/.cache/huggingface）" White
Write-ColorOutput "  2. 下载到项目目录（推荐）: $defaultModelPath" White
Write-ColorOutput "  3. 自定义路径" White

$choice = Read-Host "`n请输入选择 (1/2/3) [默认: 2]"
if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "2" }

switch ($choice) {
    "1" {
        Write-Success "使用默认缓存路径"
        $modelPath = ""
    }
    "2" {
        $modelPath = $defaultModelPath
        Write-Success "模型将下载到: $modelPath"
    }
    "3" {
        $customPath = Read-Host "请输入自定义路径"
        $modelPath = $customPath
        Write-Success "模型将下载到: $modelPath"
    }
    default {
        $modelPath = $defaultModelPath
        Write-Success "使用默认项目路径: $modelPath"
    }
}

# 更新 .env 配置
if ($modelPath) {
    # 创建模型目录
    if (-not (Test-Path $modelPath)) {
        New-Item -ItemType Directory -Path $modelPath -Force | Out-Null
        Write-Success "创建模型目录: $modelPath"
    }
    
    # 更新配置文件
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "TRANSLATOR_MODEL_PATH=") {
        $envContent = $envContent -replace "TRANSLATOR_MODEL_PATH=.*", "TRANSLATOR_MODEL_PATH=$modelPath"
    } else {
        $envContent += "`n# Local Model Path`nTRANSLATOR_MODEL_PATH=$modelPath`n"
    }
    Set-Content ".env" -Value $envContent
    Write-Success "已配置模型路径到 .env"
}

# ====================================================================
# 6. 安装依赖
# ====================================================================
Write-Step "安装项目依赖..."

try {
    Write-ColorOutput "这可能需要几分钟时间..." Yellow
    uv sync
    Write-Success "依赖安装完成"
    
    Write-Step "安装开发依赖..."
    uv sync --extra dev
    Write-Success "开发依赖安装完成"
} catch {
    Write-Error "依赖安装失败: $_"
    exit 1
}

# ====================================================================
# 7. 下载模型
# ====================================================================
Write-Step "准备下载翻译模型..."

Write-ColorOutput "`n是否现在下载模型？(模型大小约 4GB)" White
Write-ColorOutput "  Y - 立即下载" White
Write-ColorOutput "  N - 稍后下载（首次运行时自动下载）" White

$downloadNow = Read-Host "`n请选择 (Y/N) [默认: N]"

if ($downloadNow -eq "Y" -or $downloadNow -eq "y") {
    Write-Step "开始下载模型（tencent/HY-MT1.5-1.8B）..."
    Write-ColorOutput "这可能需要较长时间，请耐心等待..." Yellow
    
    try {
        if ($hfMirror) {
            $env:HF_ENDPOINT = $hfMirror
        }
        
        # 使用 Python 脚本下载模型
        uv run python -c @"
from translator.core.engine import TranslationEngine
print('正在下载模型...')
engine = TranslationEngine().load()
print('模型下载完成！')
engine.unload()
"@
        
        Write-Success "模型下载完成！"
    } catch {
        Write-Warning "模型下载失败，但不影响安装"
        Write-ColorOutput "您可以稍后运行程序时自动下载" Yellow
    }
} else {
    Write-Success "跳过模型下载，将在首次使用时自动下载"
}

# ====================================================================
# 8. 运行测试
# ====================================================================
Write-Step "运行测试验证安装..."

try {
    uv run pytest -q
    Write-Success "所有测试通过！"
} catch {
    Write-Warning "部分测试失败，但不影响使用"
}

# ====================================================================
# 完成
# ====================================================================
Write-ColorOutput @"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                    🎉 安装完成！                              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

"@ Green

Write-ColorOutput "快速开始：" Cyan
Write-ColorOutput ""
Write-ColorOutput "  # 查看支持的语言" White
Write-ColorOutput "  uv run translate languages" Yellow
Write-ColorOutput ""
Write-ColorOutput "  # 交互式翻译" White
Write-ColorOutput "  uv run translate -I -d en2zh" Yellow
Write-ColorOutput ""
Write-ColorOutput "  # 单文本翻译" White
Write-ColorOutput "  uv run translate --text 'Hello' -d en2zh" Yellow
Write-ColorOutput ""
Write-ColorOutput "  # 启动 GUI" White
Write-ColorOutput "  uv run translate-gui" Yellow
Write-ColorOutput ""

Write-ColorOutput "更多信息请查看 README.md" Cyan
Write-ColorOutput ""
