"""CSV 转换命令"""

import click
import json
import logging

from plugins.converters.to_csv import ToCsvPlugin

logger = logging.getLogger(__name__)


@click.command('to-csv')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), required=True, help='Output CSV file')
@click.option('--page', type=int, help='Specific page to extract tables from (1-based)')
@click.option('--page-range', type=str, help='Page range (e.g., "1-3")')
@click.option('--pages', type=str, help='Multiple pages (e.g., "1,3,5")')
@click.option('--table-index', type=int, default=0, help='Table index to convert (0-based, default: 0)')
@click.option('--merge-tables', is_flag=True, default=False, help='Merge all tables into one CSV')
@click.option('--header/--no-header', default=True, help='Include table header (default: True)')
@click.option('--delimiter', type=str, default=',', help='CSV delimiter (default: ",")')
@click.pass_context
def to_csv_command(ctx, input: str, output: str, page: int, page_range: str, pages: str,
                    table_index: int, merge_tables: bool, header: bool, delimiter: str):
    """Convert PDF tables to CSV format

    Examples:
        # Convert first table from all pages
        ai-pdf-agent to-csv input.pdf -o output.csv

        # Convert from specific page
        ai-pdf-agent to-csv input.pdf -o output.csv --page 1

        # Convert second table
        ai-pdf-agent to-csv input.pdf -o output.csv --table-index 1

        # Merge all tables
        ai-pdf-agent to-csv input.pdf -o output.csv --merge-tables

        # Use tab delimiter
        ai-pdf-agent to-csv input.pdf -o output.csv --delimiter '\t'

        # No header
        ai-pdf-agent to-csv input.pdf -o output.csv --no-header
    """
    # 解析页码参数
    kwargs = {
        'output_path': output,
        'table_index': table_index,
        'merge_tables': merge_tables,
        'header': header,
        'delimiter': delimiter,
    }

    if page is not None:
        kwargs['page'] = page
    elif page_range:
        try:
            start, end = map(int, page_range.split('-'))
            kwargs['page_range'] = (start, end)
        except ValueError:
            click.echo(f"Error: Invalid page range format: {page_range}. Use 'start-end' (e.g., '1-3')", err=True)
            return
    elif pages:
        try:
            kwargs['pages'] = [int(p.strip()) for p in pages.split(',')]
        except ValueError:
            click.echo(f"Error: Invalid pages format: {pages}. Use comma-separated numbers (e.g., '1,3,5')", err=True)
            return

    # 创建转换器插件
    plugin = ToCsvPlugin()

    if not plugin.is_available():
        click.echo("Error: ToCsv plugin is not available. Check dependencies.", err=True)
        return

    # 执行转换
    result = plugin.convert(input, **kwargs)

    if result['success']:
        if ctx.obj.get('json_output'):
            output_data = {
                'success': True,
                'input': input,
                'output': output,
                'tables_found': result.get('tables_found'),
                'tables_converted': result.get('tables_converted'),
            }
            click.echo(json.dumps(output_data, indent=2, ensure_ascii=False))
        else:
            click.echo(f"✓ Converted: {input} -> {output}")
            click.echo(f"  Tables found: {result.get('tables_found')}")
            click.echo(f"  Tables converted: {result.get('tables_converted')}")
    else:
        error_msg = result.get('error', 'Unknown error')
        if ctx.obj.get('json_output'):
            click.echo(json.dumps({'success': False, 'error': error_msg}, indent=2, ensure_ascii=False))
        else:
            click.echo(f"✗ Error: {error_msg}", err=True)
