"""HTML 转换命令"""

import click
import json
import logging

from plugins.converters.to_html import ToHtmlPlugin

logger = logging.getLogger(__name__)


@click.command('to-html')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), required=True, help='Output HTML file')
@click.option('--page', type=int, help='Specific page to convert (1-based)')
@click.option('--page-range', type=str, help='Page range (e.g., "1-3")')
@click.option('--pages', type=str, help='Multiple pages (e.g., "1,3,5")')
@click.option('--embed-images', is_flag=True, default=False, help='Embed images as base64 in HTML')
@click.option('--responsive', is_flag=True, default=False, help='Use responsive CSS design')
@click.pass_context
def to_html_command(ctx, input, output, page, page_range, pages, embed_images, responsive):
    """Convert PDF to HTML format

    Examples:
        # Convert all pages
        ai-pdf-agent to-html input.pdf -o output.html

        # Convert specific page
        ai-pdf-agent to-html input.pdf -o output.html --page 1

        # Convert page range
        ai-pdf-agent to-html input.pdf -o output.html --page-range 1-3

        # With embedded images
        ai-pdf-agent to-html input.pdf -o output.html --embed-images

        # With responsive design
        ai-pdf-agent to-html input.pdf -o output.html --responsive
    """
    # 解析页码参数
    kwargs = {
        'output_path': output,
        'embed_images': embed_images,
        'responsive': responsive,
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
    plugin = ToHtmlPlugin()

    if not plugin.is_available():
        click.echo("Error: ToHtml plugin is not available. Check dependencies.", err=True)
        return

    # 执行转换
    result = plugin.convert(input, **kwargs)

    if result['success']:
        if ctx.obj.get('json_output'):
            output_data = {
                'success': True,
                'input': input,
                'output': output,
                'pages': result.get('pages'),
                'metadata': result.get('metadata', {})
            }
            click.echo(json.dumps(output_data, indent=2, ensure_ascii=False))
        else:
            click.echo(f"✓ Converted: {input} -> {output}")
            click.echo(f"  Pages: {result.get('pages')}")
    else:
        error_msg = result.get('error', 'Unknown error')
        if ctx.obj.get('json_output'):
            click.echo(json.dumps({'success': False, 'error': error_msg}, indent=2, ensure_ascii=False))
        else:
            click.echo(f"✗ Error: {error_msg}", err=True)
