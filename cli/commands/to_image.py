"""Image 转换命令"""

import click
import json
import logging
import os

from plugins.converters.to_image import ToImagePlugin

logger = logging.getLogger(__name__)


@click.command('to-image')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), required=True, help='Output directory or file template (e.g., "output/" or "page_{page}.png")')
@click.option('--page', type=int, help='Specific page to convert (1-based)')
@click.option('--page-range', type=str, help='Page range (e.g., "1-3")')
@click.option('--pages', type=str, help='Multiple pages (e.g., "1,3,5")')
@click.option('--format', type=click.Choice(['png', 'jpeg', 'jpg', 'webp', 'bmp', 'tiff']), default='png', help='Output format (default: png)')
@click.option('--dpi', type=int, default=150, help='DPI for rendering (default: 150)')
@click.option('--quality', type=int, default=85, help='Image quality 1-100 (default: 85)')
@click.option('--grayscale', is_flag=True, default=False, help='Convert to grayscale')
@click.pass_context
def to_image_command(ctx, input: str, output: str, page: int, page_range: str, pages: str,
                    format: str, dpi: int, quality: int, grayscale: bool):
    """Convert PDF pages to image format

    Examples:
        # Convert all pages to PNG (output to directory)
        ai-pdf-agent to-image input.pdf -o output/

        # Convert all pages with custom template
        ai-pdf-agent to-image input.pdf -o "page_{page}.png"

        # Convert specific page
        ai-pdf-agent to-image input.pdf -o. output.png --page 1

        # Convert page range
        ai-pdf-agent to-image input.pdf -o output/ --page-range 1-3

        # Convert to format JPEG with higher DPI
        ai-pdf-agent to-image input.pdf -o output/ --format jpeg --dpi 300

        # Convert to grayscale
        ai-pdf-agent to-image input.pdf -o output/ --grayscale
    """
    # 验证 DPI 和 Quality
    if dpi < 72 or dpi > 600:
        click.echo(f"Warning: DPI {dpi} is outside recommended range (72-600)", err=True)

    if quality < 1 or quality > 100:
        click.echo(f"Error: Quality must be between 1 and 100", err=True)
        return

    # 解析页码参数
    kwargs = {
        'output_path': output,
        'format': format,
        'dpi': dpi,
        'quality': quality,
        'grayscale': grayscale,
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
    plugin = ToImagePlugin()

    if not plugin.is_available():
        click.echo("Error: ToImage plugin is not available. Check dependencies.", err=True)
        return

    # 执行转换
    result = plugin.convert(input, **kwargs)

    if result['success']:
        if ctx.obj.get('json_output'):
            output_data = {
                'success': True,
                'input': input,
                'output': output,
                'pages_converted': result.get('pages_converted'),
                'format': result.get('format'),
                'output_files': result.get('output_files', []),
            }
            click.echo(json.dumps(output_data, indent=2, ensure_ascii=False))
        else:
            click.echo(f"✓ Converted: {input} -> {output}")
            click.echo(f"  Pages: {result.get('pages_converted')}")
            click.echo(f"  Format: {result.get('format')}")
            click.echo(f"  DPI: {dpi}")

            # 显示输出文件
            output_files = result.get('output_files', [])
            if output_files:
                click.echo(f"  Output files:")
                for file in output_files[:5]:  # 只显示前 5 个
                    click.echo(f"    - {file}")
                if len(output_files) > 5:
                    click.echo(f"    ... and {len(output_files) - 5} more")
    else:
        error_msg = result.get('error', 'Unknown error')
        if ctx.obj.get('json_output'):
            click.echo(json.dumps({'success': False, 'error': error_msg}, indent=2, ensure_ascii=False))
        else:
            click.echo(f"✗ Error: {error_msg}", err=True)
