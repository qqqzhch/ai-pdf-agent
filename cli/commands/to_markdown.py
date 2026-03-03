"""Markdown 转换命令（示例）"""

import click
import json


@click.command('to-markdown')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), required=True, help='Output file')
@click.option('--preserve-tables', is_flag=True, help='Preserve tables')
@click.option('--preserve-code', is_flag=True, help='Preserve code blocks')
@click.pass_context
def to_markdown_command(ctx, input, output, preserve_tables, preserve_code):
    """Convert PDF to Markdown"""
    # TODO: 实现 Markdown 转换功能
    # 这里只是一个示例
    
    result = {
        "input": input,
        "output": output,
        "preserve_tables": preserve_tables,
        "preserve_code": preserve_code
    }
    
    if ctx.obj['json']:
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        markdown_content = "# 示例 Markdown 内容\n\n这里是从 PDF 转换的内容。"
        
        with open(output, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        click.echo(f"Converted: {input} -> {output}")
