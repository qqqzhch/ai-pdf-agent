"""CLI 主入口"""

import click
import json
import logging

fromsys import stderr

from utils.error_handler import handle_errors, AI_PDF_Error


logger = logging.getLogger(__name__)

# 全局上下文设置
CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help'],
    'max_content_width': 120,
}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--json', is_flag=True, help='Output in JSON format')
@click.option('--quiet', is_flag=True, help='Quiet mode')
@click.option('--verbose', is_flag=True, help='Verbose output')
@click.option('--config', type=click.Path(), help='Config file path')
@click.version_option(version='0.1.0')
@click.pass_context
@handle_errors
def cli(ctx, json, quiet, verbose, config):
    """AI PDF Agent - Plugin-based PDF processing tool
    
    A CLI tool designed for AI Agents to process PDF files with a plugin system.
    """
    ctx.ensure_object(dict)
    ctx.obj['json'] = json
    ctx.obj['quiet'] = quiet
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config
    
    # 设置日志级别
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')


# 导入子命令
from commands import plugin
from commands import text, tables, images, metadata, structure
from commands import to_markdown, to_html, to_json, to_csv, to_image, to_epub

# 注册子命令
cli.add_command(plugin.plugin_group)
cli.add_command(text.text_command)
cli.add_command(tables.tables_command)
cli.add_command(images.images_command)
cli.add_command(metadata.metadata_command)
cli.add_command(structure.structure_command)
cli.add_command(to_markdown.to_markdown_command)
cli.add_command(to_html.to_html_command)
cli.add_command(to_json.to_json_command)
cli.add_command(to_csv.to_csv_command)
cli.add_command(to_image.to_image_command)
cli.add_command(to_epub.to_epub_command)


if __name__ == '__main__':
    cli()
