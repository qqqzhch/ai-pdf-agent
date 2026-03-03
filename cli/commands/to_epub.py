"""EPUB 转换命令"""

import click
import json
import logging

from plugins.converters.to_epub import ToEpubPlugin

logger = logging.getLogger(__name__)


@click.command('to-epub')
@click.argument('input', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), required=True, help='Output EPUB file')
@click.option('--page', type=int, help='Specific page to convert (1-based)')
@click.option('--page-range', type=str, help='Page range (e.g., "1-3")')
@click.option('--pages', type=str, help='Multiple pages (e.g., "1,3,5")')
@click.option('--title', type=str, help='Book title (default: PDF title or filename)')
@click.option('--author', type=str, help='Book author (default: PDF author)')
@click.option('--include-images/--no-include-images', default=True, help='Include images in EPUB (default: True)')
@click.option('--chapter-pages', type=int, default=0, help='Pages per chapter (0 = one chapter per page, default: 0)')
@click.pass_context
def to_epub_command(ctx, input: str, output: str, page: int, page_range: str, pages: str,
                    title: str, author: str, include_images: bool, chapter_pages: int):
    """Convert PDF to EPUB ebook format

    Examples:
        # Convert all pages
    ai-pdf-agent to-epub input.pdf -o output.epub

        # Convert specific page
    ai-pdf-agent to-epub input.pdf -o output.epub --page 1

        # Convert page range
    ai-pdf-agent to-epub input.pdf -o output.epub --page-range 1-10

        # Set title and author
    ai-pdf-agent to-epub input.pdf -o output.epub --title "My Book" --author "John Doe"

        # Group pages into chapters (5 pages per chapter)
    ai-pdf-agent to-epub input.pdf -o output.epub --chapter-pages 5

        # Exclude images
    ai-pdf-agent to-epub input.pdf -o output.epub --no-include-images
    """
    # 验证 chapter_pages
    if chapter_pages < 0:
        click.echo("Error: chapter-pages must be >= 0", err=True)
        return

    # 解析页码参数
    kwargs = {
        'output_path': output,
        'include_images': include_images,
        'chapter_pages': chapter_pages,
    }

    if title:
        kwargs['title'] = title

    if author:
        kwargs['author'] = author

    if page is not None:
        kwargs['page'] = page
    elif page_range:
        try:
            start, end = map(int, page_range.split('-'))
            kwargs['page_range'] = (start, end)
        except ValueError:
            click.echo(f"Error: Invalid page range format: {page_range}. Use 'start-end' (e.g., '1-3')", err=True)
            return
    elif pages:
        try:
            kwargs['pages'] = [int(p.strip()) for p in pages.split(',')]
        except ValueError:
            click.echo(f"Error: Invalid pages format: {pages}. Use comma-separated numbers (e.g., '1,3,5')", err=True)
            return

    # 创建转换器插件
    plugin = ToEpubPlugin()

    if not plugin.is_available():
        click.echo("Error: ToEpub plugin is not available. Check dependencies.", err=True)
        return

    # 执行转换
    result = plugin.convert(input, **kwargs)

    if result['success']:
        if ctx.obj.get('json_output'):
            output_data = {
                'success': True,
                'input': input,
                'output': output,
                'pages': result.get('pages'),
                'chapters': result.get('chapters'),
                'images': result.get('images'),
            }
            click.echo(json.dumps(output_data, indent=2, ensure_ascii=False))
        else:
            click.echo(f"✓ Converted: {input} -> {output}")
            click.echo(f"  Pages: {result.get('pages')}")
            click.echo(f"  Chapters: {result.get('chapters')}")
            click.echo(f"  Images: {result.get('images')}")
    else:
        error_msg = result.get('error', 'Unknown error')
        if ctx.obj.get('json_output'):
            click.echo(json.dumps({'success': False, 'error': error_msg}, indent=2, ensure_ascii=False))
        else:
            click.echo(f"✗ Error: {error_msg}", err=True)
