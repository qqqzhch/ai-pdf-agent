"""表格读取命令

使用 table_reader 插件提取 PDF 表格内容
"""

import click
import json
import logging

logger = logging.getLogger(__name__)


@click.command('tables')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(),
              help='Output file path (save to file)')
@click.option('-p', '--pages',
              help='Page range (e.g., 1-5, 1,3,5)')
@click.option('-f', '--format', 'output_format',
              type=click.Choice(['json', 'csv', 'list'],
              case_sensitive=False),
              default='json', help='Output format (default: json)')
@click.option('--csv-output', type=click.Path(),
              help='Separate CSV output file (when format=json)')
@click.pass_obj
def tables_command(ctx, input, output, pages, output_format, csv_output):
    """Extract tables from PDF

    Extract table data from PDF files with page range and format options.

    Examples:
        ai-pdf-agent tables document.pdf
        ai-pdf-agent tables document.pdf -p 1-3
        ai-pdf-agent tables document.csv --format csv
        ai-pdf-agent tables document.pdf -p 2 -o tables.json
    """
    from plugins.readers.table_reader import TableReaderPlugin

    # 创建插件实例
    plugin = TableReaderPlugin()

    if not plugin.is_available():
        raise click.ClickException(
            "Error: Table reader plugin is not available"
        )

    # 解析页码范围
    kwargs = {}
    if pages:
        parsed = parse_page_range(pages)
        if parsed is None:
            raise click.ClickException(
                f"Error: Invalid page range format: {pages}"
            )
        kwargs.update(parsed)

    # 设置输出格式
    kwargs['output_format'] = output_format

    # 读取表格
    result = plugin.read(input, **kwargs)

    if not result["success"]:
        raise click.ClickException(f"Error: {result['error']}")

    # 准备输出数据
    output_data = {
        "success": True,
        "input": input,
        "pages_extracted": result["pages_extracted"],
        "page_count": result["page_count"],
        "total_tables": result["total_tables"],
        "tables": result["tables"],
    }

    # 输出结果
    if output_format.lower() == 'json':
        output_str = json.dumps(output_data, indent=2, ensure_ascii=False)

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(output_str)
            click.echo(f"✓ Tables extracted to: {output}")
        else:
            click.echo(output_str)

        # 同时输出 CSV
        if csv_output and 'csv' in result:
            with open(csv_output, 'w', encoding='utf-8') as f:
                f.write(result['csv'])
            click.echo(f"✓ CSV saved to: {csv_output}")

    elif output_format.lower() == 'csv':
        output_str = result.get('csv', '')

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(output_str)
            click.echo(f"✓ CSV saved to: {output}")
        else:
            click.echo(output_str)

    elif output_format.lower() == 'list':
        output_str = json.dumps(output_data, indent=2, ensure_ascii=False)

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(output_str)
            click.echo(f"✓ Tables list saved to: {output}")
        else:
            click.echo(output_str)

    # 显示摘要信息（仅在保存到文件时）
    if output and output_format.lower() == 'json':
        click.echo(f"Summary: {result['total_tables']} tables found on {len(result['pages_extracted'])} page(s)")

    return 0


def parse_page_range(pages: str):
    """解析页码范围字符串（与 text.py 共享逻辑）"""
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
