#!/usr/bin/env python3
"""
AI PDF Agent - CLI 主入口
"""

import click

@click.group()
@click.version_option(version="1.0.0", prog_name="ai-pdf")
def cli():
    """AI PDF Agent - 智能 PDF 处理工具

    使用方法：
      ai-pdf read <pdf-path> [-o output]
      ai-pdf convert <pdf-path> --format <format>
    """
    pass


@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
def read(pdf_path, output):
    """读取 PDF 内容并提取信息"""
    click.echo(f"读取 PDF: {pdf_path}")
    # TODO: 实现读取逻辑
    if output:
        click.echo(f"输出到: {output}")


@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['markdown', 'html', 'json', 'text']), required=True, help='输出格式')
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
def convert(pdf_path, format, output):
    """转换 PDF 到指定格式"""
    click.echo(f"转换 PDF: {pdf_path} -> {format}")
    # TODO: 实现转换逻辑
    if output:
        click.echo(f"输出到: {output}")


if __name__ == '__main__':
    cli()
