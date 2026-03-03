"""图片读取命令

使用 image_reader 插件提取 PDF 图片
"""

import click
import json
import logging

logger = logging.getLogger(__name__)


@click.command('images')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='Output JSON file with image metadata')
@click.option('--extract-dir', type=click.Path(), help='Directory to extract images')
@click.option('-p', '--pages', help='Page range (e.g., 1-5, 1,3,5)')
@click.option('-f', '--format', 'image_format',
              type=click.Choice(['png', 'jpeg', 'ppm', 'pbm', 'pam'],
                               case_sensitive=False),
              default='png', help='Image extraction format (default: png)')
@click.option('--dpi', type=int, default=150, help='Image DPI (default: 150)')
@click.option('--metadata-only', is_flag=True, help='Only extract metadata, do not save images')
@click.pass_obj
def images_command(ctx, input, output, extract_dir, pages, image_format, dpi, metadata_only):
    """Extract images from PDF

    Extract images from PDF files with page range, format, and output options.

    Examples:
        ai-pdf-agent images document.pdf
        ai-pdf-agent images document.pdf -p 1-3 --extract-dir ./images
        ai-pdf-agent images document.pdf --format jpeg --dpi 300
        ai-pdf-agent images document.pdf --metadata-only -o metadata.json
    """
    from plugins.readers.image_reader import ImageReaderPlugin

    # 创建插件实例
    plugin = ImageReaderPlugin()

    if not plugin.is_available():
        raise click.ClickException("Error: Image reader plugin is not available")

    # 解析页码范围
    kwargs = {}
    if (pages):
        parsed = parse_page_range(pages)
        if parsed is None:
            raise click.ClickException(f"Error: Invalid page range format: {pages}")
        kwargs.update(parsed)

    # 设置保存目录
    if extract_dir and not metadata_only:
        kwargs['extract_dir'] = extract_dir

    # 设置图片格式
    kwargs['format'] = image_format
    kwargs['dpi'] = dpi

    # 读取图片
    result = plugin.read(input, **kwargs)

    if not result["success"]:
        raise click.ClickException(f"Error: {result['error']}")

    # 准备输出数据
    output_data = {
        "success": True,
        "input": input,
        "pages_extracted": result["pages_extracted"],
        "page_count": result["page_count"],
        "count": result["count"],
        "images": result["images"],
    }

    # 添加保存目录信息
    if result.get("extract_dir"):
        output_data["extract_dir"] = result["extract_dir"]

    # 输出结果
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        click.echo(f"✓ Image metadata saved to: {output}")
    else:
        click.echo(json.dumps(output_data, indent=2, ensure_ascii=False))

    # 显示摘要信息（仅在保存到文件时）
    if output:
        click.echo(f"Summary: {result['count']} images found on {len(result['pages_extracted'])} page(s)")
        if extract_dir and not metadata_only:
            saved_count = sum(1 for img in result["images"] if "saved_path" in img)
            click.echo(f"✓ {saved_count} images saved to: {extract_dir}")

    return 0


def parse_page_range(pages: str):
    """解析页码范围字符串"""
    try:
        # 单页
        if '-' not in pages and ',' not in pages:
            page_num = int(pages.strip())
            if page_num < 1:
                return None
            return {"page": page_num}

        # 范围 "1-5"
        if '-' in pages and ',' not in pages:
            parts = pages.split('-')
            if len(parts) == 2:
                start = int(parts[0].strip())
                end = int(parts[1].strip())
                if start < 1 or end < 1 or start > end:
                    return None
                return {"page_range": (start, end)}

        # 多页 "1,3,5"
        if ',' in pages and '-' not in pages:
            page_list = [int(p.strip()) for p in pages.split(',')]
            if any(p < 1 for p in page_list):
                return None
            return {"pages": page_list}

        # 混合 "1-3,5,7-9"
        if ',' in pages and '-' in pages:
            page_list = []
            parts = pages.split(',')

            for part in parts:
                part = part.strip()
                if '-' in part:
                    range_parts = part.split('-')
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
