"""Markdown 转换命令"""

import json
import logging
from pathlib import Path

import click

from plugins.converters.to_markdown import ToMarkdownPlugin

logger = logging.getLogger(__name__)


@click.command("to-markdown")
@click.argument("input", type=click.Path(exists=True))
@click.option(
    "-o", "--output", type=click.Path(), required=True, help="Output Markdown file"
)
@click.option("--page", type=int, help="Specific page to convert (1-based)")
@click.option("--page-range", type=str, help='Page range (e.g., "1-3")')
@click.option("--pages", type=str, help='Multiple pages (e.g., "1,3,5")')
@click.option(
    "--preserve-tables", is_flag=True, default=True, help="Preserve tables in Markdown"
)
@click.option(
    "--preserve-images", is_flag=True, default=True, help="Preserve images in Markdown"
)
@click.option(
    "--image-prefix", type=str, default="image_", help="Image filename prefix"
)
@click.pass_context
def to_markdown_command(
    ctx,
    input,
    output,
    page,
    page_range,
    pages,
    preserve_tables,
    preserve_images,
    image_prefix,
):
    """Convert PDF to Markdown format

    Examples:
        # Convert all pages
        ai-pdf-agent to-markdown input.pdf -o output.md

        # Convert specific page
        ai-pdf-agent to-markdown input.pdf -o output.md --page 1

        # Convert page range
        ai-pdf-agent to-markdown input.pdf -o output.md --page-range 1-3

        # Convert multiple pages
        ai-pdf-agent to-markdown input.pdf -o output.md --pages 1,3,5

        # Without tables or images
        ai-pdf-agent to-markdown input.pdf -o output.md --no-preserve-tables --no-preserve-images
    """
    # 解析页码参数
    kwargs = {
        "output_path": output,
        "preserve_tables": preserve_tables,
        "preserve_images": preserve_images,
        "image_prefix": image_prefix,
    }

    if page is not None:
        kwargs["page"] = page
    elif page_range:
        try:
            start, end = map(int, page_range.split("-"))
            kwargs["page_range"] = (start, end)
        except ValueError:
            click.echo(
                f"Error: Invalid page range format: {page_range}. Use 'start-end' (e.g., '1-3')",
                err=True,
            )
            return
    elif pages:
        try:
            kwargs["pages"] = [int(p.strip()) for p in pages.split(",")]
        except ValueError:
            click.echo(
                f"Error: Invalid pages format: {pages}. Use comma-separated numbers (e.g., '1,3,5')",
                err=True,
            )
            return

    # 创建转换器插件
    plugin = ToMarkdownPlugin()

    if not plugin.is_available():
        click.echo(
            "Error: ToMarkdown plugin is not available. Check dependencies.", err=True
        )
        return

    # 执行转换
    result = plugin.convert(input, **kwargs)

    if result["success"]:
        if ctx.obj.get("json_output"):
            output_data = {
                "success": True,
                "input": input,
                "output": output,
                "pages": result.get("pages"),
                "image_count": result.get("image_count", 0),
                "metadata": result.get("metadata", {}),
            }
            click.echo(json.dumps(output_data, indent=2, ensure_ascii=False))
        else:
            click.echo(f"✓ Converted: {input} -> {output}")
            click.echo(f"  Pages: {result.get('pages')}")
            if result.get("image_count", 0) > 0:
                click.echo(f"  Images: {result.get('image_count')}")
    else:
        error_msg = result.get("error", "Unknown error")
        if ctx.obj.get("json_output"):
            click.echo(
                json.dumps(
                    {"success": False, "error": error_msg}, indent=2, ensure_ascii=False
                )
            )
        else:
            click.echo(f"✗ Error: {error_msg}", err=True)
