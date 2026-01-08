"""
模型下载工具

支持从 HuggingFace 下载模型到本地
"""

import os
import sys
from pathlib import Path

from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

console = Console()


def download_model(
    model_name: str = "tencent/HY-MT1.5-1.8B",
    local_dir: str | None = None,
    use_mirror: bool = False,
) -> Path:
    """
    下载模型到本地

    Args:
        model_name: 模型名称
        local_dir: 本地存储目录
        use_mirror: 是否使用中国镜像

    Returns:
        模型本地路径
    """
    from huggingface_hub import snapshot_download

    # 设置镜像
    if use_mirror:
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        console.print("[cyan]使用 HuggingFace 中国镜像[/cyan]")

    # 确定下载路径
    if local_dir is None:
        local_dir = Path.cwd() / "models" / model_name.replace("/", "--")
    else:
        local_dir = Path(local_dir)

    local_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[cyan]开始下载模型: {model_name}[/cyan]")
    console.print(f"[cyan]目标路径: {local_dir}[/cyan]")
    console.print("[yellow]这可能需要较长时间，请耐心等待...[/yellow]\n")

    try:
        # 下载模型
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("下载中...", total=None)

            model_path = snapshot_download(
                repo_id=model_name,
                local_dir=str(local_dir),
                local_dir_use_symlinks=False,
                resume_download=True,
            )

            progress.update(task, completed=100)

        console.print("\n[green]✓ 模型下载完成！[/green]")
        console.print(f"[green]模型路径: {model_path}[/green]")

        return Path(model_path)

    except Exception as e:
        console.print(f"\n[red]✗ 下载失败: {e}[/red]")
        raise


def check_model_exists(model_path: str | Path) -> bool:
    """检查本地模型是否存在"""
    model_path = Path(model_path)

    # 检查必要的模型文件
    required_files = ["config.json", "tokenizer_config.json"]

    if not model_path.exists():
        return False

    return all((model_path / file).exists() for file in required_files)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="下载翻译模型")
    parser.add_argument(
        "--model",
        "-m",
        default="tencent/HY-MT1.5-1.8B",
        help="模型名称",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="输出目录",
    )
    parser.add_argument(
        "--mirror",
        action="store_true",
        help="使用中国镜像",
    )

    args = parser.parse_args()

    try:
        download_model(
            model_name=args.model,
            local_dir=args.output,
            use_mirror=args.mirror,
        )
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
