"""Image 转换命令（示例）"""

import click
import json


@click.command('to-image')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), required=True, help='Output file pattern (e.g., page-{page}.png)')
@click.option('--dpi', type=int, default=150, help='DPI for output images')
@click.option('-p', '--pages', help='Page range (e.g., 1-5, 1,3,5)')
@click.option('--format', default='png', help='Output format (png, jpeg)')
@click.pass_context
def to_image_command(ctx, input, output, dpi, pages, format):
    """Convert PDF pages to images"""
    # TODO: 实现 Image 转换功能
    # 这里只是一个示例
    
    result = {
        "input": input,
        "output": output,
        "dpi": dpi,
        "pages": pages,
        "format": format
    }
    
    if ctx.obj['json']:
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        click.echo(f"Converted: {input} -> {output}")
        click.echo(f"DPI: {dpi}, Format: {format}")
