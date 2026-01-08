# ====================================================================
# Nuitka 编译脚本 - Windows
# ====================================================================

param(
    [switch]$Gui = $false,
    [switch]$Onefile = $false,
    [switch]$Standalone = $true
)

$ErrorActionPreference = "Stop"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  AI Translation System - 编译工具  " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Nuitka
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "错误: 未找到 Python" -ForegroundColor Red
    exit 1
}

# 确定编译目标
if ($Gui) {
    $target = "translate-gui"
    $entryPoint = "src/translator/gui/__init__.py"
    $outputName = "TranslateGUI"
    Write-Host "编译目标: GUI 应用" -ForegroundColor Green
} else {
    $target = "translate"
    $entryPoint = "src/translator/cli/__init__.py"
    $outputName = "Translate"
    Write-Host "编译目标: CLI 应用" -ForegroundColor Green
}

# 构建 Nuitka 命令
$nuitkaArgs = @(
    "-m", "nuitka",
    "--assume-yes-for-downloads",
    "--output-dir=build",
    "--output-filename=$outputName"
)

# 编译模式
if ($Onefile) {
    $nuitkaArgs += "--onefile"
    Write-Host "模式: 单文件" -ForegroundColor Yellow
} elseif ($Standalone) {
    $nuitkaArgs += "--standalone"
    Write-Host "模式: 独立目录" -ForegroundColor Yellow
} else {
    Write-Host "模式: 加速" -ForegroundColor Yellow
}

# GUI 特定选项
if ($Gui) {
    $nuitkaArgs += @(
        "--windows-console-mode=disable",
        "--windows-icon-from-ico=assets/icon.ico"  # 如果有图标
    )
}

# 包含必要的包
$nuitkaArgs += @(
    "--include-package=translator",
    "--include-package=torch",
    "--include-package=transformers",
    "--include-package=accelerate",
    "--include-package=huggingface_hub",
    "--include-package=pydantic",
    "--include-package=pydantic_settings",
    "--include-package=typer",
    "--include-package=rich"
)

if ($Gui) {
    $nuitkaArgs += "--include-package=PySide6"
}

# 数据文件
$nuitkaArgs += @(
    "--include-data-dir=src/translator=translator",
    "--nofollow-import-to=pytest",
    "--nofollow-import-to=setuptools"
)

# 优化选项
$nuitkaArgs += @(
    "--enable-plugin=anti-bloat",
    "--python-flag=no_site",
    "--python-flag=no_warnings"
)

# 添加入口点
$nuitkaArgs += $entryPoint

Write-Host ""
Write-Host "开始编译..." -ForegroundColor Cyan
Write-Host "命令: python $($nuitkaArgs -join ' ')" -ForegroundColor Gray
Write-Host ""

# 执行编译
try {
    & python @nuitkaArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "=====================================" -ForegroundColor Green
        Write-Host "  编译成功！" -ForegroundColor Green
        Write-Host "=====================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "输出目录: build\" -ForegroundColor Cyan
        
        if ($Onefile) {
            Write-Host "可执行文件: build\$OutputName.exe" -ForegroundColor Cyan
        } else {
            Write-Host "可执行文件: build\$OutputName.dist\$OutputName.exe" -ForegroundColor Cyan
        }
        
        Write-Host ""
        Write-Host "提示: 首次运行需要联网下载模型，或使用:" -ForegroundColor Yellow
        Write-Host "  translate download -o ./models" -ForegroundColor Yellow
        Write-Host "  然后设置环境变量 TRANSLATOR_MODEL_PATH" -ForegroundColor Yellow
    } else {
        Write-Host "编译失败！" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "编译过程中出错: $_" -ForegroundColor Red
    exit 1
}
