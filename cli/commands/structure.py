"""结构读取命令

使用 structure_reader 插件分析 PDF 文档结构
"""

import json
import logging

import click

logger = logging.getLogger(__name__)


@click.command("structure")
@click.argument("input", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="Output JSON file path")
@click.option("-p", "--pages", help="Page range (e.g., 1-5, 1,3,5)")
@click.option("--outline-only", is_flag=True, help="Extract outline (TOC) only")
@click.option("--blocks-only", is_flag=True, help="Extract blocks only")
@click.option("--logical-only", is_flag=True, help="Extract logical structure only")
@click.option("--tree", is_flag=True, help="Output as structure tree (simplified view)")
@click.pass_obj
def structure_command(
    ctx, input, output, pages, outline_only, blocks_only, logical_only, tree
):
    """Extract document structure from PDF

    Analyze PDF document structure including outline (TOC), page structure,
    blocks, and logical structure (headings, paragraphs, lists, etc.).

    Examples:
        ai-pdf-agent structure document.pdf
        ai-pdf-agent structure document.pdf -p 1-5
        ai-pdf-agent structure document.pdf --outline-only
        ai-pdf-agent structure document.pdf --tree
    """
    from plugins.readers.structure_reader import StructureReaderPlugin

    # 创建插件实例
    plugin = StructureReaderPlugin()

    if not plugin.is_available():
        raise click.ClickException("Error: Structure reader plugin is not available")

    # 解析页码范围
    kwargs = {}
    if pages:
        parsed = parse_page_range(pages)
        if parsed is None:
            raise click.ClickException(f"Error: Invalid page range format: {pages}")
        kwargs.update(parsed)

    # 设置要提取的内容
    if outline_only:
        kwargs["include_outline"] = True
        kwargs["include_page_structure"] = False
        kwargs["include_logical_structure"] = False
        kwargs["include_blocks"] = False
    elif blocks_only:
        kwargs["include_outline"] = False
        kwargs["include_page_structure"] = False
        kwargs["include_logical_structure"] = False
        kwargs["include_blocks"] = True
    elif logical_only:
        kwargs["include_outline"] = False
        kwargs["include_page_structure"] = False
        kwargs["include_logical_structure"] = True
        kwargs["include_blocks"] = False
    else:
        # 默认：提取所有
        kwargs["include_outline"] = True
        kwargs["include_page_structure"] = True
        kwargs["include_logical_structure"] = True
        kwargs["include_blocks"] = True

    # 读取结构
    if tree:
        result = {"success": False, "error": None}
        try:
            structure_tree = plugin.get_structure_tree(input)
            if structure_tree.get("success"):
                result["success"] = True
                result["structure"] = structure_tree
            else:
                result["error"] = structure_tree.get("error", "Unknown error")
        except Exception as e:
            result["error"] = str(e)
    else:
        result = plugin.read(input, **kwargs)

    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1

    # 准备输出数据
    if tree:
        output_data = {
            "success": True,
            "input": input,
        }
        output_data.update(result.get("structure", {}))
    else:
        output_data = {
            "success": True,
            "input": input,
            "pages_analyzed": result["pages_analyzed"],
            "page_count": result["page_count"],
        }

        if outline_only or not blocks_only and not logical_only:
            output_data["outline"] = result.get("outline", [])

        if blocks_only or not outline_only and not logical_only:
            output_data["blocks"] = result.get("blocks", [])

        if logical_only or not outline_only and not blocks_only:
            output_data["logical_structure"] = result.get("logical_structure", [])

        if not outline_only and not blocks_only and not logical_only:
            output_data["page_structure"] = result.get("page_structure", [])
            output_data["metadata"] = result.get("metadata", {})

    # 输出结果
    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        click.echo(f"✓ Structure saved to: {output}")
    else:
        click.echo(json.dumps(output_data, indent=2, ensure_ascii=False))

    # 显示摘要信息（仅在保存到文件时）
    if output:
        click.echo(f"Summary: Analyzed {len(result['pages_analyzed'])} page(s)")

        if "outline" in output_data:
            click.echo(f"Outline items: {_count_outline_items(output_data['outline'])}")

        if "logical_structure" in output_data:
            # 统计结构类型
            type_counts = {}
            for item in output_data["logical_structure"]:
                item_type = item.get("type", "unknown")
                type_counts[item_type] = type_counts.get(item_type, 0) + 1

            if type_counts:
                click.echo(
                    f"Structure types: {', '.join(f'{k}: {v}' for k, v in type_counts.items())}"
                )

    return 0


def parse_page_range(pages: str):
    """解析页码范围字符串"""
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
                    range_parts = part.split("-")
                    if len(range_parts) == 2:
                        start = int(range_parts[0].strip())
                        end = int(range_parts[1].strip())
                        page_list.extend(range(start, end + 1))
                else:
                    page_list.append(int(part))

            if any(p < 1 for p in page_list):
                return None

            page_list = sorted(list(set(page_list)))
            return {"pages": page_list}

        return None

    except (ValueError, AttributeError):
        return None


def _count_outline_items(outline):
    """递归统计大纲项目数量"""
    count = len(outline)
    for item in outline:
        count += _count_outline_items(item.get("children", []))
    return count
