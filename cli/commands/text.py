"""文本读取命令

使用 text_reader 插件提取 PDF 文本内容
"""

import json
import logging
from typing import Optional

import click

from cli.error_handler import (AI_PDF_Error, PluginNotFoundError,
                               handle_errors, validate_pdf_file)

logger = logging.getLogger(__name__)


@click.command("text")
@click.argument("input", type=click.Path(exists=False))
@click.option(
    "-o", "--output", type=click.Path(), help="Output file path (save text to file)"
)
@click.option("-p", "--pages", help="Page range (e.g., 1-5, 1,3,5, or single page)")
@click.option(
    "-f",
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "markdown"], case_sensitive=False),
    default="text",
    help="Output format (default: text)",
)
@click.option(
    "--structured", is_flag=True, help="Return structured output with metadata"
)
@click.pass_obj
@handle_errors()
def text_command(ctx, input, output, pages, output_format, structured):
    """Extract text from PDF

    Extract text content from PDF files with page range and format options.

    Examples:
        ai-pdf-agent text document.pdf
        ai-pdf-agent text document.pdf -p 1-5
        ai-pdf-agent text document.pdf -p 1,3,5 -o output.txt
        ai-pdf-agent text document.pdf --format json --structured
    """
    from plugins.readers.text_reader import TextReaderPlugin

    # 验证 PDF 文件
    validate_pdf_file(input)

    # 创建插件实例
    plugin = TextReaderPlugin()

    if not plugin.is_available():
        raise PluginNotFoundError("text_reader")

    # 解析页码范围
    kwargs = {}
    if pages:
        parsed = parse_page_range(pages)
        if parsed is None:
            raise AI_PDF_Error(
                message=f"Invalid page range format: {pages}",
                details="Supported formats: '1', '1-5', '1,3,5', '1-3,5,7-9'",
                solution="Check the page range format",
            )
        kwargs.update(parsed)

    # 读取文本
    result = plugin.read(input, **kwargs)

    if not result["success"]:
        raise AI_PDF_Error(
            message=f"Failed to extract text from {input}",
            details=result.get("error", "Unknown error"),
        )

    # 准备输出
    if output_format.lower() == "json" or structured:
        # JSON 格式输出
        output_data = {
            "success": True,
            "input": input,
            "pages_extracted": result["pages_extracted"],
            "page_count": result["page_count"],
            "content": result["content"],
        }

        if structured:
            output_data["metadata"] = result.get("metadata", {})

        output_str = json.dumps(output_data, indent=2, ensure_ascii=False)
    else:
        # 纯文本格式
        output_str = result["content"]

    # 输出结果
    if output:
        try:
            with open(output, "w", encoding="utf-8") as f:
                f.write(output_str)
            if not ctx.json_output:
                click.echo(f"✓ Text extracted to: {output}")
        except Exception as e:
            raise AI_PDF_Error(
                message=f"Failed to write to output file: {output}", details=str(e)
            )
    else:
        click.echo(output_str)

    return 0


def parse_page_range(pages: str) -> Optional[dict]:
    """
    解析页码范围字符串

    支持格式:
        - 单页: "1"
        - 范围: "1-5"
        - 多页: "1,3,5"
        - 混合: "1-3,5,7-9"

    Args:
        pages: 页码范围字符串

    Returns:
        Optional[dict]: 解析后的 kwargs，格式为 {"page": int}, {"page_range": (start, end)}, 或 {"pages": list}
    """
    try:
        # 单页
        if "-" not in pages and "," not in pages:
            page_num = int(pages.strip())
            if page_num < 1:
                return None
            return {"page": page_num}

        # 范围 "1-5"
        if "-" in pages and "," not in pages:
            parts = pages.split("-")
            if len(parts) == 2:
                start = int(parts[0].strip())
                end = int(parts[1].strip())
                if start < 1 or end < 1 or start > end:
                    return None
                return {"page_range": (start, end)}

        # 多页 "1,3,5"
        if "," in pages and "-" not in pages:
            page_list = [int(p.strip()) for p in pages.split(",")]
            if any(p < 1 for p in page_list):
                return None
            return {"pages": page_list}

        # 混合 "1-3,5,7-9"
        if "," in pages and "-" in pages:
            page_list = []
            parts = pages.split(",")

            for part in parts:
                part = part.strip()
                if "-" in part:
                    # 处理范围
                    range_parts = part.split("-")
                    if len(range_parts) == 2:
                        start = int(range_parts[0].strip())
                        end = int(range_parts[1].strip())
                        page_list.extend(range(start, end + 1))
                else:
                    # 处理单页
                    page_list.append(int(part))

            if any(p < 1 for p in page_list):
                return None

            # 去重并排序
            page_list = sorted(list(set(page_list)))
            return {"pages": page_list}

        return None

    except (ValueError, AttributeError):
        return None
