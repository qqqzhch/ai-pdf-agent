"""元数据读取命令（示例）"""

import click
import json


@click.command('metadata')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='Output JSON file')
@click.pass_context
def metadata_command(ctx, input, output):
    """Read PDF metadata"""
    # TODO: 实现元数据读取功能
    # 这里只是一个示例
    
    result = {
        "input": input,
        "output": output,
        "metadata": {
            "title": "示例标题",
            "author": "示例作者",
            "page_count": 10
        }
    }
    
    if ctx.obj['json']:
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            click.echo(f"Metadata saved to: {output}")
        else:
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
