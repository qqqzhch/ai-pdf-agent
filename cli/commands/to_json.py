"""JSON 转换命令"""

import click
import json
import logging

from plugins.converters.to_json import ToJsonPlugin

logger = logging.getLogger(__name__)


@click.command('to-json')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), required=True, help='Output JSON file')
@click.option('--page', type=int, help='Specific page to convert (1-based)')
@click.option('--page-range', type=str, help='Page range (e.g., "1-3")')
@click.option('--pages', type=str, help='Multiple pages (e.g., "1,3,5")')
@click.option('--structured', is_flag=True, default=True, help='Structured JSON format (default)')
@click.option('--include-metadata', is_flag=True, default=True, help='Include document metadata')
@click.option('--include-text', is_flag=True, default=True, help='Include text content')
@click.option('--include-tables', is_flag=True, default=True, help='Include tables')
@click.option('--include-structure', is_flag=True, default=True, help='Include document structure')
@click.pass_context
def to_json_command(ctx, input: str, output: str, page: int, page_range: str, pages: str,
                    structured: bool, include_metadata: bool, include_text: bool,
                    include_tables: bool, include_structure: bool):
    """Convert PDF to structured JSON format

    Examples:
        # Convert all pages
        ai-pdf-agent to-json input.pdf -o output.json

        # Convert specific page
        ai-pdf-agent to-json input.pdf -o output.json --page 1

        # Convert page range
        ai-pdf-agent to-json input.pdf -o output.json --page-range 1-3

        # Exclude metadata
        ai-pdf-agent to-json input.pdf -o output.json --no-include-metadata

        # Text only
        ai-pdf-agent to-json input.pdf -o output.json --no-include-tables --no-include-structure
    """
    # 解析页码参数
    kwargs = {
        'output_path': output,
        'pretty': True,  # 默认格式化输出
        'include_metadata': include_metadata,
        'include_text': include_text,
        'include_tables': include_tables,
        'include_structure': include_structure,
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
    plugin = ToJsonPlugin()

    if not plugin.is_available():
        click.echo("Error: ToJson plugin is not available. Check dependencies.", err=True)
        return

    # 执行转换
    result = plugin.convert(input, **kwargs)

    if result['success']:
        if ctx.obj.get('json_output'):
            # 在 JSON 模式下输出转换结果
            output_data = {
                'success': True,
                'input': input,
                'output': output,
                'pages': result.get('pages'),
            }
            click.echo(json.dumps(output_dataData, indent=2, ensure_ascii=False))
        else:
            click.echo(f"✓ Converted: {input} -> {output}")
            click.echo(f"  Pages: {result.get('pages')}")

            # 显示内容摘要
            if include_text and result.get('content'):
                try:
                    data = json.loads(result['content'])
                    if 'text' in data:
                        text_pages = data['text'].get('total_pages', 0)
                        click.echo(f"  Text pages: {text_pages}")
                    if 'tables' in data:
                        total_tables = data['tables'].get('total_tables', 0)
                        click.echo(f"  Tables: {total_tables}")
                except json.JSONDecodeError:
                    pass
    else:
        error_msg = result.get('error', 'Unknown error')
        if ctx.obj.get('json_output'):
            click.echo(json.dumps({'success': False, 'error': error_msg}, indent=2, ensure_ascii=False))
        else:
            click.echo(f"✗ Error: {error_msg}", err=True)
