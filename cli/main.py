"""AI PDF Agent CLI - 主入口模块

这个模块实现了基于 Click 的命令行界面框架，支持：
- 全局选项 (--verbose, --debug, --config)
- 上下文传递
- 插件加载和初始化
- 子命令注册
"""

import sys
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

import click

from core.plugin_system import PluginManager, PluginType
from cli.error_handler import handle_errors
from cli.config import Config, ConfigError
from cli.logger import setup_logging, get_logger

logger = get_logger(__name__)

# 全局上下文设置
CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help'],
    'max_content_width': 120,
    'ignore_unknown_options': True,
    'allow_extra_args': True,
}


class CLIContext:
    """CLI 上下文类

    用于在命令之间传递共享状态和配置
    """

    def __init__(
        self,
        verbose: bool = False,
        debug: bool = False,
        quiet: bool = False,
        json_output: bool = False,
        config_path: Optional[str] = None,
    ):
        self.verbose = verbose
        self.debug = debug
        self.quiet = quiet
        self.json_output = json_output
        self.config_path = config_path

        # 配置对象
        self.config: Optional[Config] = None

        # 插件管理器
        self.plugin_manager: Optional[PluginManager] = None

        # PDF 引擎实例
        self.pdf_engine = None

        # 设置日志
        self._setup_logging()

        # 加载配置
        self._load_config()

        # 初始化插件系统
        self._init_plugin_system()

    def _setup_logging(self):
        """设置日志级别和格式"""
        # 从配置获取日志设置（配置加载后）
        log_level = 'DEBUG' if self.debug else ('INFO' if self.verbose else 'WARNING')
        log_format = 'detailed' if self.debug else ('standard' if self.verbose else 'minimal')

        # 设置日志
        setup_logging(
            level=log_level,
            verbose=self.verbose,
            debug=self.debug,
            quiet=self.quiet,
            json_output=self.json_output,
            use_colors=not self.json_output,
        )

    def _load_config(self):
        """加载配置文件"""
        try:
            self.config = Config(self.config_path)

            # 验证配置
            if not self.config.validate(raise_on_error=False):
                errors = self.config.get_validation_errors()
                if errors and self.debug:
                    logger.warning(f"Config validation errors: {len(errors)}")
                    for error in errors:
                        logger.warning(f"  - {error}")

            # 从配置更新日志设置
            if self.config:
                log_level = self.config.get('log_level', 'INFO')
                log_file = self.config.get('log_file')
                log_format = self.config.get('log_format', 'standard')

                # 重新设置日志（如果配置中有日志设置）
                if log_file or log_format != 'standard':
                    setup_logging(
                        level=log_level,
                        verbose=self.verbose,
                        debug=self.debug,
                        quiet=self.quiet,
                        log_file=log_file,
                        json_output=self.json_output,
                        use_colors=not self.json_output,
                    )

            logger.info(f"Config loaded successfully")

        except FileNotFoundError as e:
            if self.config_path:
                logger.warning(f"Config file not found: {self.config_path}")
            # 使用默认配置
            self.config = Config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            # 使用默认配置
            self.config = Config()

    def _init_plugin_system(self):
        """初始化插件系统"""
        try:
            # 创建插件管理器
            self.plugin_manager = PluginManager()

            # 自动发现并加载插件
            plugin_dir = Path(__file__).parent.parent / 'plugins'
            if plugin_dir.exists():
                # 使用 PluginManager 的方法
                loaded_count = self.plugin_manager.load_all_plugins()
                logger.info(f"Loaded {loaded_count} plugins")

            # 获取已加载的插件信息
            plugins = self.plugin_manager.list_plugin_names()
            if self.verbose:
                logger.info(f"Available plugins: {plugins}")

        except Exception as e:
            logger.error(f"Error initializing plugin system: {e}")
            self.plugin_manager = None

    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        if self.config:
            return self.config.get(key, default)
        return default

    def set_config(self, key: str, value: Any):
        """设置配置项"""
        if self.config:
            self.config.set(key, value)

    def get_plugin(self, plugin_name: str):
        """获取指定插件"""
        if self.plugin_manager is None:
            return None
        return self.plugin_manager.get_plugin(plugin_name)

    def get_plugins_by_type(self, plugin_type: PluginType):
        """获取指定类型的所有插件"""
        if self.plugin_manager is None:
            return []
        # PluginManager 的 list_plugins 返回 list, not dict
        plugins = self.plugin_manager.list_plugins(plugin_type)
        return plugins

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项（兼容字典式访问）"""
        # 支持访问 CLIContext 属性
        if hasattr(self, key):
            return getattr(self, key)
        # 否则从配置字典获取
        return self.get_config(key, default)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--verbose', '-v', is_flag=True, help='详细输出模式')
@click.option('--debug', '-d', is_flag=True, help='调试模式（显示详细日志）')
@click.option('--quiet', '-q', is_flag=True, help='静默模式（只显示错误）')
@click.option('--json', is_flag=True, help='JSON 格式输出')
@click.option('--config', '-c', type=click.Path(exists=False), help='配置文件路径')
@click.version_option(version='0.1.0', prog_name='ai-pdf-agent')
@click.pass_context
@handle_errors()
def cli(ctx, verbose, debug, quiet, json, config):
    """AI PDF Agent - 基于插件的 PDF 处理工具

    一个为 AI Agent 设计的 PDF 处理命令行工具，通过插件系统提供灵活的
    PDF 内容提取、分析和转换功能。

    全局选项:
        -v, --verbose    详细输出模式
        -d, --debug      调试模式（显示详细日志）
        -q, --quiet      静默模式（只显示错误）
        --json           JSON 格式输出
        -c, --config     配置文件路径

    使用示例:

        # 提取 PDF 文本
        ai-pdf-agent text input.pdf

        # 提取 PDF 表格
        ai-pdf-agent tables input.pdf

        # 提取 PDF 图片
        ai-pdf-agent images input.pdf

        # 转换为 Markdown
        ai-pdf-agent to-markdown input.pdf -o output.md

        # 显示插件列表
        ai-pdf-agent plugin list

        # 使用配置文件
        ai-pdf-agent -c config.json text input.pdf

        # 使用详细模式
        ai-pdf-agent --verbose text input.pdf
    """
    # 创建 CLI 上下文
    ctx.obj = CLIContext(
        verbose=verbose,
        debug=debug,
        quiet=quiet,
        json_output=json,
        config_path=config,
    )


def register_commands():
    """注册所有子命令"""
    from cli.commands import plugin
    from cli.commands import text, tables, images, metadata, structure
    from cli.commands import to_markdown, to_html, to_json, to_csv, to_image, to_epub

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


# 延迟加载子命令（避免循环导入）
def _lazy_load_commands():
    """延迟加载子命令"""
    if not cli.commands:
        register_commands()


# 重写 invoke 方法以支持延迟加载
original_invoke = cli.invoke


def _invoke(self, *args, **kwargs):
    """重写 invoke 方法以支持延迟加载"""
    _lazy_load_commands()
    return original_invoke(*args, **kwargs)


cli.invoke = _invoke.__get__(cli, cli.__class__)


if __name__ == '__main__':
    # 确保工作目录正确
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # 运行 CLI
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n操作已取消", err=True)
        sys.exit(130)
    except Exception as e:
        if '--debug' in sys.argv or '-d' in sys.argv:
            logger.exception("未捕获的异常")
        else:
            click.echo(f"错误: {e}", err=True)
        sys.exit(1)
