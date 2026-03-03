"""CSV 转换命令（示例）"""

import click
import json
import csv


@click.command('to-csv')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), required=True, help='Output file')
@click.option('--table-index', type=int, default=0, help='Table index (0 for first table)')
@click.pass_context
def to_csv_command(ctx, input, output, table_index):
    """Convert PDF tables to CSV"""
    # TODO: 实现 CSV 转换功能
    # 这里只是一个示例
    
    result = {
        "input": input,
        "output": output,
        "table_index": table_index
    }
    
    if ctx.obj['json']:
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # 示例 CSV 内容
        csv_content = [
            ["列1", "列2", "列3"],
            ["数据1", "数据2", "数据3"],
            ["数据4", "数据5", "数据6"]
        ]
        
        with open(output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(csv_content)
        
        click.echo(f"Converted: {input} -> {output}")
