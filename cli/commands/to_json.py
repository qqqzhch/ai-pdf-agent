"""JSON 转换命令（示例）"""

import click
import json


@click.command('to-json')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), required=True, help='Output file')
@click.option('--structured', is_flag=True, help='Structured JSON format')
@click.option('--include-metadata', is_flag=True, help='Include metadata')
@click.pass_context
def to_json_command(ctx, input, output, structured, include_metadata):
    """Convert PDF to structured JSON"""
    # TODO: 实现 JSON 转换功能
    # 这里只是一个示例
    
    result = {
        "input": input,
        "output": output,
        "structured": structured,
        "include_metadata": include_metadata,
        "data": {
            "text": "示例文本",
            "pages": []
        }
    }
    
    if ctx.obj['json']:
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        click.echo(f"Converted: {input} -> {output}")
