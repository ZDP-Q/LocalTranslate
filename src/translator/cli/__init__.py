"""
命令行接口
使用 Typer 构建现代 CLI
"""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from translator.config import get_settings
from translator.config.languages import LanguageRegistry
from translator.core import TranslationEngine
from translator.core.models import FileFormat

app = typer.Typer(
    name="translate",
    help="AI Translation System - 基于 HY-MT1.5 的高效翻译系统",
    add_completion=False,
    rich_markup_mode="rich",
    invoke_without_command=True,
)

console = Console()


def get_direction_choices() -> list[str]:
    """获取可用的翻译方向"""
    return LanguageRegistry.get_codes()


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    text: Annotated[str | None, typer.Option("--text", "-t", help="要翻译的文本")] = None,
    input_file: Annotated[Path | None, typer.Option("--input", "-i", help="输入文件路径")] = None,
    output_file: Annotated[Path | None, typer.Option("--output", "-o", help="输出文件路径")] = None,
    direction: Annotated[
        str, typer.Option("--direction", "-d", help="翻译方向 (如 en2zh, zh2en)")
    ] = "en2zh",
    interactive: Annotated[bool, typer.Option("--interactive", "-I", help="交互式模式")] = False,
    model: Annotated[str | None, typer.Option("--model", "-m", help="模型名称或路径")] = None,
    no_bfloat16: Annotated[bool, typer.Option("--no-bfloat16", help="禁用 bfloat16 精度")] = False,
    max_tokens: Annotated[int, typer.Option("--max-tokens", help="最大生成 token 数")] = 2048,
    custom_prompt: Annotated[
        str | None, typer.Option("--prompt", "-p", help="自定义翻译提示词")
    ] = None,
    format: Annotated[str, typer.Option("--format", "-f", help="文件格式 (txt/json)")] = "txt",
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="详细输出")] = False,
):
    """
    翻译文本或文件

    支持三种模式:

    1. 单文本翻译: translate -t "Hello" -d en2zh

    2. 文件翻译: translate -i input.txt -o output.txt -d en2zh

    3. 交互式模式: translate -I -d en2zh
    """
    # 如果调用了子命令，跳过主回调逻辑
    if ctx.invoked_subcommand is not None:
        return

    # 验证输入
    if not any([text, input_file, interactive]):
        console.print("[red]错误: 请指定 --text, --input 或 --interactive[/red]")
        raise typer.Exit(1)

    if input_file and not output_file:
        console.print("[red]错误: 使用 --input 时必须指定 --output[/red]")
        raise typer.Exit(1)

    # 验证翻译方向
    if direction not in get_direction_choices() and not custom_prompt:
        console.print(f"[red]错误: 不支持的翻译方向 '{direction}'[/red]")
        console.print(f"支持的方向: {', '.join(get_direction_choices())}")
        raise typer.Exit(1)

    # 加载模型
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("正在加载模型...", total=None)

        try:
            engine = TranslationEngine(
                model_name=model, use_bfloat16=not no_bfloat16, max_new_tokens=max_tokens
            ).load()
        except Exception as e:
            console.print(f"[red]模型加载失败: {e}[/red]")
            raise typer.Exit(1)

    console.print(f"[green]✓ 模型已加载 (设备: {engine.device})[/green]\n")

    try:
        if interactive:
            _run_interactive(engine, direction, custom_prompt)
        elif text:
            _translate_text(engine, text, direction, custom_prompt, verbose)
        elif input_file:
            _translate_file(
                engine,
                input_file,
                output_file,
                direction,
                FileFormat(format),
                custom_prompt,
                verbose,
            )
    finally:
        engine.unload()


def _translate_text(
    engine: TranslationEngine, text: str, direction: str, custom_prompt: str | None, verbose: bool
):
    """翻译单个文本"""
    with console.status("翻译中..."):
        result = engine.translate_text(text, direction, custom_prompt)

    if verbose:
        table = Table(title="翻译结果")
        table.add_column("原文", style="cyan")
        table.add_column("译文", style="green")
        table.add_row(text, result)
        console.print(table)
    else:
        console.print(result)


def _translate_file(
    engine: TranslationEngine,
    input_path: Path,
    output_path: Path,
    direction: str,
    format: FileFormat,
    custom_prompt: str | None,
    verbose: bool,
):
    """翻译文件"""
    from translator.utils import FileHandler

    handler = FileHandler()
    texts = handler.read(input_path, format)

    console.print(f"[blue]读取 {len(texts)} 条文本[/blue]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("翻译中...", total=len(texts))

        def on_progress(current: int, total: int):
            progress.update(task, completed=current)

        batch_result = engine.translate_batch(texts, direction, custom_prompt, on_progress)

    # 保存结果
    translated = [r.translated_text for r in batch_result.results]
    handler.write(output_path, translated, format)

    # 显示统计
    console.print(
        Panel(
            f"[green]成功: {batch_result.successful}[/green] | "
            f"[red]失败: {batch_result.failed}[/red] | "
            f"总耗时: {batch_result.total_processing_time_ms:.0f}ms",
            title="翻译完成",
        )
    )
    console.print(f"[green]结果已保存到: {output_path}[/green]")


def _run_interactive(engine: TranslationEngine, direction: str, custom_prompt: str | None):
    """运行交互式模式"""
    lang_info = LanguageRegistry.get(direction)
    display = lang_info.display if lang_info else direction

    console.print(
        Panel(
            f"[bold]交互式翻译模式[/bold]\n"
            f"方向: {display}\n"
            f"输入 [cyan]exit[/cyan] 或 [cyan]quit[/cyan] 退出\n"
            f"输入 [cyan]swap[/cyan] 切换翻译方向",
            title="AI 翻译系统",
        )
    )

    current_direction = direction

    while True:
        try:
            text = console.input("\n[bold cyan]>[/bold cyan] ").strip()

            if not text:
                continue

            if text.lower() in ("exit", "quit", "q"):
                console.print("[yellow]再见！[/yellow]")
                break

            if text.lower() == "swap":
                new_dir = LanguageRegistry.get_swap(current_direction)
                if new_dir and LanguageRegistry.get(new_dir):
                    current_direction = new_dir
                    lang_info = LanguageRegistry.get(current_direction)
                    console.print(f"[green]已切换到: {lang_info.display}[/green]")
                else:
                    console.print("[red]无法切换方向[/red]")
                continue

            with console.status("翻译中..."):
                result = engine.translate_text(text, current_direction, custom_prompt)

            console.print(f"[green]{result}[/green]")

        except KeyboardInterrupt:
            console.print("\n[yellow]再见！[/yellow]")
            break


@app.command()
def languages():
    """显示支持的语言方向"""
    table = Table(title="支持的语言方向")
    table.add_column("代码", style="cyan")
    table.add_column("显示", style="green")
    table.add_column("描述")

    for code, direction in LanguageRegistry.get_all().items():
        table.add_row(code, direction.display, direction.description)

    console.print(table)


@app.command()
def version():
    """显示版本信息"""
    settings = get_settings()
    console.print(
        Panel(
            f"[bold]{settings.app_name}[/bold]\n"
            f"版本: {settings.version}\n"
            f"模型: {settings.model.name}",
            title="关于",
        )
    )


def main():
    """CLI 入口"""
    app()


if __name__ == "__main__":
    main()
