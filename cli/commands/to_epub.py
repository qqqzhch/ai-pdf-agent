"""EPUB 转换命令（示例）"""

import click
import json


@click.command('to-epub')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), required=True, help='Output EPUB file')
@click.option('--title', help='EPUB title')
@click.option('--author', help='EPUB author')
@click.pass_context
def to_epub_command(ctx, input, output, title, author):
    """Convert PDF to EPUB"""
    # TODO: 实现 EPUB 转换功能
    # 这里只是一个示例
    
    result = {
        "input": input,
        "output": output,
        "title": title,
        "author": author
    }
    
    if ctx.obj['json']:
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        click.echo(f"Converted: {input} -> {output}")
