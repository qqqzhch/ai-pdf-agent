"""元数据读取命令

使用 metadata_reader 插件提取 PDF 元数据和文档统计
"""

import click
import json
import logging

logger = logging.getLogger(__name__)


@click.command('metadata')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='Output JSON file path')
@click.option('--full', is_flag=True, help='Include all metadata (stats and properties)')
@click.option('--raw', is_flag=True, help='Show raw metadata without normalization')
@click.option('--stats', is_flag=True, help='Include document statistics')
@click.option('--properties', is_flag=True, help='Include PDF properties')
@click.pass_obj
def metadata_command(ctx, input, output, full, raw, stats, properties):
    """Read PDF metadata

    Extract metadata, document statistics, and PDF properties from PDF files.

    Examples:
        ai-pdf-agent metadata document.pdf
        ai-pdf-agent metadata document.pdf --full
        ai-pdf-agent metadata document.pdf --stats --properties -o info.json
    """
    from plugins.readers.metadata_reader import MetadataReaderPlugin

    # 创建插件实例
    plugin = MetadataReaderPlugin()

    if not plugin.is_available():
        raise click.ClickException(
            "Error: Metadata reader plugin is not available"
        )

    # 设置读取选项
    kwargs = {}

    if full:
        kwargs['include_stats'] = True
        kwargs['include_properties'] = True
    else:
        kwargs['include_stats'] = stats
        kwargs['include_properties'] = properties

    kwargs['normalize'] = not raw

    # 读取元数据
    result = plugin.read(input, **kwargs)

    if not result["success"]:
        raise click.ClickException(f"Error: {result['error']}")

    # 准备输出数据
    output_data = {
        "success": True,
        "input": input,
    }

    # 添加基本元数据
    output_data["basic_metadata"] = result.get("basic_metadata", {})

    # 添加完整元数据
    if full or raw:
        output_data["metadata"] = result.get("metadata", {})

    # 添加统计信息
    if full or stats:
        output_data["document_stats"] = result.get("document_stats", {})

    # 添加 PDF 特性
    if full or properties:
        output_data["pdf_properties"] = result.get("pdf_properties", {})

    # 输出结果
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        click.echo(f"✓ Metadata saved to: {output}")
    else:
        click.echo(json.dumps(output_data, indent=2, ensure_ascii=False))

    # 显示摘要信息（仅在保存到文件时）
    if output:
        basic = result.get("basic_metadata", {})
        if basic.get("title"):
            click.echo(f"Title: {basic['title']}")
        if basic.get("author"):
            click.echo(f"Author: {basic['author']}")
        if basic.get("subject"):
            click.echo(f"Subject: {basic['subject']}")
        if basic.get("keywords"):
            kw = basic['keywords']
            if isinstance(kw, list):
                kw_str = ', '.join(kw)
            else:
                kw_str = kw
            click.echo(f"Keywords: {kw_str}")

        if full or stats:
            doc_stats = result.get("document_stats", {})
            if doc_stats.get("page_count"):
                click.echo(f"Pages: {doc_stats['page_count']}")

    return 0
