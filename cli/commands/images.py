"""图片读取命令（示例）"""

import click
import json


@click.command('images')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='Output JSON file')
@click.option('--extract-dir', type=click.Path(), help='Directory to extract images')
@click.option('-p', '--pages', help='Page range (e.g., 1-5, 1,3,5)')
@click.pass_context
def images_command(ctx, input, output, extract_dir, pages):
    """Extract images from PDF"""
    # TODO: 实现图片读取功能
    # 这里只是一个示例
    
    result = {
        "input": input,
        "output": output,
        "extract_dir": extract_dir,
        "pages": pages,
        "images": []  # 实际实现中需要从 PDF 提取图片
    }
    
    if ctx.obj['json']:
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            click.echo(f"Images extracted to: {output}")
        else:
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
