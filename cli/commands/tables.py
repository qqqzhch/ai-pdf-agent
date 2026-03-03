"""表格读取命令（示例）"""

import click
import json


@click.command('tables')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='Output file')
@click.option('-p', '--pages', help='Page range (e.g., 1-5, 1,3,5)')
@click.pass_context
def tables_command(ctx, input, output, pages):
    """Extract tables from PDF"""
    # TODO: 实现表格读取功能
    # 这里只是一个示例
    
    result = {
        "input": input,
        "output": output,
        "pages": pages,
        "tables": []  # 实际实现中需要从 PDF 提取表格
    }
    
    if ctx.obj['json']:
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            click.echo(f"Tables extracted to: {output}")
        else:
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
