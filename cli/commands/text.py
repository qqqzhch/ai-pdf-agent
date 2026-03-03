"""文本读取命令（示例）"""

import click
import json


@click.command('text')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='Output file')
@click.option('-p', '--pages', help='Page range (e.g., 1-5, 1,3,5)')
@click.option('--structured', is_flag=True, help='Extract structured text')
@click.pass_context
def text_command(ctx, input, output, pages, structured):
    """Extract text from PDF"""
    # TODO: 实现文本读取功能
    # 这里只是一个示例
    
    result = {
        "input": input,
        "output": output,
        "pages": pages,
        "structured": structured,
        "text": "示例文本内容"  # 实际实现中需要从 PDF 提取
    }
    
    if ctx.obj['json']:
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        text = result['text']
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(text)
            click.echo(f"Text extracted to: {output}")
        else:
            click.echo(text)
