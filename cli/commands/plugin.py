"""插件管理命令

提供完整的插件管理功能：
- list: 列出所有插件
- info: 显示插件详细信息
- check: 检查插件健康状态
- enable: 启用插件
- disable: 禁用插件
- reload: 重新加载所有插件
"""

import click
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

from core.plugin_system import PluginManager, PluginType
from utils.error_handler import handle_errors, AI_PDF_Error


# 禁用插件配置文件路径
DISABLED_PLUGINS_FILE = Path.home() / ".ai-pdf" / "disabled_plugins.json"


def load_disabled_plugins() -> set:
    """加载禁用插件列表"""
    if not DISABLED_PLUGINS_FILE.exists():
        return set()

    try:
        with open(DISABLED_PLUGINS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get('disabled', []))
    except Exception:
        return set()


def save_disabled_plugins(disabled: set):
    """保存禁用插件列表"""
    DISABLED_PLUGINS_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(DISABLED_PLUGINS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'disabled': list(disabled)}, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise AI_PDF_Error(f"Failed to save disabled plugins: {e}")


def is_plugin_disabled(name: str) -> bool:
    """检查插件是否被禁用"""
    disabled = load_disabled_plugins()
    return name in disabled


@click.group('plugin')
@click.pass_context
def plugin_group(ctx):
    """插件管理命令

    管理和操作 AI PDF Agent 的插件系统。

    使用示例:

        # 列出所有插件
        ai-pdf-agent plugin list

        # 查看插件详细信息
        ai-pdf-agent plugin info text_reader

        # 检查插件健康状态
        ai-pdf-agent plugin check

        # 启用插件
        ai-pdf-agent plugin enable text_reader

        # 禁用插件
        ai-pdf-agent plugin disable text_reader

        # 重新加载所有插件
        ai-pdf-agent plugin reload
    """
    pass


@plugin_group.command('list')
@click.option('--type', 'plugin_type', help='按插件类型过滤 (reader, converter, ocr, etc.)')
@click.option('--all', 'show_all', is_flag=True, help='显示所有插件（包括禁用的）')
@click.option('--json', 'json_output', is_flag=True, help='JSON 格式输出')
@click.pass_obj
@handle_errors
def plugin_list(ctx, plugin_type: Optional[str], show_all: bool, json_output: bool):
    """列出所有插件

    显示当前系统中所有可用插件的信息，包括插件名称、版本、类型和描述。

    使用 --type 选项可以按插件类型过滤：
        reader     - 阅读器插件（文本、表格、图片等）
        converter  - 转换器插件（Markdown、HTML、JSON 等）
        ocr        - OCR 插件（文字识别）
        rag        - RAG 插件（检索增强生成）
        encrypt    - 加密插件
        compress   - 压缩插件
        edit       - 编辑插件
        analyze    - 分析插件
        custom     - 自定义插件

    使用 --all 选项显示所有插件（包括已禁用的插件）。
    """
    # 获取插件管理器
    manager = ctx.plugin_manager
    if manager is None:
        manager = PluginManager()
        manager.load_all_plugins()

    # 加载禁用插件列表
    disabled_plugins = load_disabled_plugins()

    # 获取所有插件
    plugins = manager.list_plugins()

    # 按类型过滤
    if plugin_type:
        try:
            plugin_type_enum = PluginType(plugin_type)
            plugins = [p for p in plugins if p.plugin_type == plugin_type_enum]
        except ValueError:
            raise AI_PDF_Error(f"Invalid plugin type: {plugin_type}")

    # 准备输出数据
    plugin_data = []
    for p in plugins:
        is_disabled = p.name in disabled_plugins
        if is_disabled and not show_all:
            continue

        plugin_info = {
            'name': p.name,
            'version': p.version,
            'description': p.description,
            'plugin_type': p.plugin_type.value,
            'enabled': not is_disabled,
        }
        plugin_data.append(plugin_info)

    # 按名称排序
    plugin_data.sort(key=lambda x: x['name'])

    # 输出
    if json_output:
        click.echo(json.dumps(plugin_data, indent=2, ensure_ascii=False))
    else:
        if not plugin_data:
            click.echo("No plugins found.")
            return

        # 计算列宽
        name_width = max(len(p['name']) for p in plugin_data)
        name_width = max(name_width, 20)
        version_width = 10
        type_width = 12
        status_width = 8

        # 打印表头
        header = f"{'Name':<{name_width}} {'Version':<{version_width}} {'Type':<{type_width}} {'Status':<{status_width}} Description"
        click.echo(header)
        click.echo("-" * len(header))

        # 打印插件信息
        for p in plugin_data:
            status = "✓" if p['enabled'] else "✗"
            click.echo(f"{p['name']:<{name_width}} {p['version']:<{version_width}} {p['plugin_type']:<{type_width}} {status:<{status_width}} {p['description']}")


@plugin_group.command('info')
@click.argument('name')
@click.option('--json', 'json_output', is_flag=True, help='JSON 格式输出')
@click.pass_obj
@handle_errors
def plugin_info(ctx, name: str, json_output: bool):
    """显示插件详细信息

    显示指定插件的完整信息，包括：
        - 基本信息（名称、版本、描述、类型）
        - 作者和许可证
        - 依赖项（Python 依赖和系统依赖）
        - 配置信息
        - 健康状态

    使用示例:
        ai-pdf-agent plugin info text_reader
    """
    # 获取插件管理器
    manager = ctx.plugin_manager
    if manager is None:
        manager = PluginManager()
        manager.load_all_plugins()

    # 获取插件
    plugin = manager.get_plugin(name)
    if not plugin:
        raise AI_PDF_Error(f"Plugin '{name}' not found")

    # 检查是否禁用
    is_disabled = is_plugin_disabled(name)

    # 检查依赖
    deps_ok, missing_deps = plugin.check_dependencies()

    # 检查可用性
    is_available = plugin.is_available()

    # 获取插件元数据
    metadata = plugin.get_metadata()

    # 获取插件配置
    config = manager.get_plugin_config(name) or {}

    # 准备输出数据
    info = {
        'name': metadata['name'],
        'version': metadata['version'],
        'description': metadata['description'],
        'plugin_type': metadata['plugin_type'],
        'author': metadata.get('author', 'N/A'),
        'homepage': metadata.get('homepage', 'N/A'),
        'license': metadata.get('license', 'N/A'),
        'python_dependencies': metadata['dependencies'],
        'system_dependencies': metadata['system_dependencies'],
        'enabled': not is_disabled,
        'available': is_available,
        'dependencies_ok': deps_ok,
        'missing_dependencies': missing_deps,
        'config': config,
    }

    # 输出
    if json_output:
        click.echo(json.dumps(info, indent=2, ensure_ascii=False))
    else:
        click.echo(f"插件信息: {name}")
        click.echo("=" * 60)
        click.echo(f"名称: {info['name']}")
        click.echo(f"版本: {info['version']}")
        click.echo(f"描述: {info['description']}")
        click.echo(f"类型: {info['plugin_type']}")
        click.echo(f"作者: {info['author']}")
        click.echo(f"主页: {info['homepage']}")
        click.echo(f"许可证: {info['license']}")
        click.echo()
        click.echo("状态:")
        click.echo(f"  启用状态: {'✓ 已启用' if info['enabled'] else '✗ 已禁用'}")
        click.echo(f"  可用状态: {'✓ 可用' if info['available'] else '✗ 不可用'}")
        click.echo(f"  依赖状态: {'✓ 满足' if info['dependencies_ok'] else '✗ 缺失'}")
        click.echo()
        click.echo("依赖项:")
        click.echo(f"  Python 依赖: {', '.join(info['python_dependencies']) if info['python_dependencies'] else '无'}")
        click.echo(f"  系统依赖: {', '.join(info['system_dependencies']) if info['system_dependencies'] else '无'}")

        if info['missing_dependencies']:
            click.echo(f"  ⚠ 缺失依赖: {', '.join(info['missing_dependencies'])}")


@plugin_group.command('check')
@click.option('--name', 'plugin_name', help='检查指定插件（不指定则检查所有插件）')
@click.option('--json', 'json_output', is_flag=True, help='JSON 格式输出')
@click.option('--verbose', '-v', is_flag=True, help='显示详细信息')
@click.pass_obj
@handle_errors
def plugin_check(ctx, plugin_name: Optional[str], json_output: bool, verbose: bool):
    """检查插件健康状态

    检查插件的依赖项是否满足，以及插件是否可用。

    不指定插件名称时，检查所有插件的健康状态。

    使用示例:
        ai-pdf-agent plugin check
        ai-pdf-agent plugin check --name text_reader
        ai-pdf-agent plugin check -v
    """
    # 获取插件管理器
    manager = ctx.plugin_manager
    if manager is None:
        manager = PluginManager()
        manager.load_all_plugins()

    # 获取插件列表
    if plugin_name:
        plugins = [manager.get_plugin(plugin_name)]
        if not plugins[0]:
            raise AI_PDF_Error(f"Plugin '{plugin_name}' not found")
    else:
        plugins = manager.list_plugins()

    # 加载禁用插件列表
    disabled_plugins = load_disabled_plugins()

    # 检查所有插件
    results = []
    all_ok = True

    for plugin in plugins:
        if plugin is None:
            continue

        # 检查依赖
        deps_ok, missing_deps = plugin.check_dependencies()

        # 检查可用性
        is_available = plugin.is_available()

        # 检查是否禁用
        is_disabled = plugin.name in disabled_plugins

        # 总体健康状态
        is_healthy = deps_ok and is_available

        result = {
            'name': plugin.name,
            'healthy': is_healthy,
            'enabled': not is_disabled,
            'available': is_available,
            'dependencies_ok': deps_ok,
            'missing_dependencies': missing_deps,
            'version': plugin.version,
            'plugin_type': plugin.plugin_type.value,
        }
        results.append(result)

        if not is_healthy:
            all_ok = False

    # 按名称排序
    results.sort(key=lambda x: x['name'])

    # 输出
    if json_output:
        click.echo(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        if not results:
            click.echo("No plugins found.")
            return

        # 计算列宽
        name_width = max(len(r['name']) for r in results)
        name_width = max(name_width, 20)

        if verbose:
            # 详细模式
            click.echo("插件健康状态检查")
            click.echo("=" * 80)

            for r in results:
                status_icon = "✓" if r['healthy'] else "✗"
                enabled_icon = "✓" if r['enabled'] else "✗"
                available_icon = "✓" if r['available'] else "✗"
                deps_icon = "✓" if r['dependencies_ok'] else "✗"

                click.echo(f"\n{status_icon} {r['name']} (v{r['version']})")
                click.echo(f"  类型: {r['plugin_type']}")
                click.echo(f"  启用: {enabled_icon}")
                click.echo(f"  可用: {available_icon}")
                click.echo(f"  依赖: {deps_icon}")

                if r['missing_dependencies']:
                    click.echo(f"  缺失: {', '.join(r['missing_dependencies'])}")
        else:
            # 简洁模式
            header = f"{'Plugin':<{name_width}} {'Type':<12} {'Status':<10} {'Enabled':<8} {'Deps':<6}"
            click.echo(header)
            click.echo("-" * len(header))

            for r in results:
                status = "✓ OK" if r['healthy'] else "✗ FAIL"
                enabled = "✓" if r['enabled'] else "✗"
                deps = "✓" if r['dependencies_ok'] else "✗"

                click.echo(f"{r['name']:<{name_width}} {r['plugin_type']:<12} {status:<10} {enabled:<8} {deps:<6}")

        # 总体状态
        click.echo()
        if all_ok:
            click.echo("✓ 所有插件健康状态正常")
        else:
            click.echo("✗ 部分插件存在问题，请检查详细输出")


@plugin_group.command('enable')
@click.argument('name')
@click.pass_obj
@handle_errors
def plugin_enable(ctx, name: str):
    """启用插件

    启用指定的插件。插件启用后会在系统加载时被自动加载。

    使用示例:
        ai-pdf-agent plugin enable text_reader
    """
    # 获取插件管理器
    manager = ctx.plugin_manager
    if manager is None:
        manager = PluginManager()
        manager.load_all_plugins()

    # 检查插件是否存在
    plugin = manager.get_plugin(name)
    if not plugin:
        raise AI_PDF_Error(f"Plugin '{name}' not found")

    # 加载禁用插件列表
    disabled = load_disabled_plugins()

    # 检查是否已经启用
    if name not in disabled:
        click.echo(f"✓ Plugin '{name}' is already enabled")
        return

    # 从禁用列表中移除
    disabled.remove(name)
    save_disabled_plugins(disabled)

    click.echo(f"✓ Plugin '{name}' has been enabled")


@plugin_group.command('disable')
@click.argument('name')
@click.option('--force', is_flag=True, help='强制禁用（即使插件正在使用）')
@click.pass_obj
@handle_errors
def plugin_disable(ctx, name: str, force: bool):
    """禁用插件

    禁用指定的插件。禁用后，插件不会被加载和使用。

    使用 --force 选项可以强制禁用插件（即使插件当前正在使用）。

    使用示例:
        ai-pdf-agent plugin disable text_reader
        ai-pdf-agent plugin disable text_reader --force
    """
    # 获取插件管理器
    manager = ctx.plugin_manager
    if manager is None:
        manager = PluginManager()
        manager.load_all_plugins()

    # 检查插件是否存在
    plugin = manager.get_plugin(name)
    if not plugin:
        raise AI_PDF_Error(f"Plugin '{name}' not found")

    # 加载禁用插件列表
    disabled = load_disabled_plugins()

    # 检查是否已经禁用
    if name in disabled:
        click.echo(f"✓ Plugin '{name}' is already disabled")
        return

    # TODO: 检查插件是否正在使用（需要实现引用计数机制）
    if not force:
        # 暂时跳过使用检查
        pass

    # 添加到禁用列表
    disabled.add(name)
    save_disabled_plugins(disabled)

    click.echo(f"✓ Plugin '{name}' has been disabled")


@plugin_group.command('reload')
@click.option('--verbose', '-v', is_flag=True, help='显示详细信息')
@click.pass_obj
@handle_errors
def plugin_reload(ctx, verbose: bool):
    """重新加载所有插件

    重新发现和加载所有插件。这会：
        1. 卸载当前加载的所有插件
        2. 重新发现插件目录中的所有插件
        3. 加载所有未被禁用的插件

    使用示例:
        ai-pdf-agent plugin reload
        ai-pdf-agent plugin reload -v
    """
    # 获取插件管理器
    manager = ctx.plugin_manager
    if manager is None:
        manager = PluginManager()

    # 记录当前加载的插件
    old_plugins = set(manager.list_plugin_names())

    if verbose:
        click.echo(f"当前加载的插件 ({len(old_plugins)}):")
        for name in sorted(old_plugins):
            click.echo(f"  - {name}")
        click.echo()

    # 卸载所有插件
    unload_count = 0
    for name in list(old_plugins):
        if manager.unload_plugin(name):
            unload_count += 1

    if verbose:
        click.echo(f"已卸载 {unload_count} 个插件")
        click.echo()

    # 重新发现插件
    manager.discover_plugins(force_refresh=True)

    # 加载所有插件（跳过禁用的）
    disabled_plugins = load_disabled_plugins()
    load_count = 0

    for plugin_path in manager.discover_plugins():
        # 从文件名提取插件名
        plugin_name = Path(plugin_path).stem

        # 跳过禁用的插件
        if plugin_name in disabled_plugins:
            if verbose:
                click.echo(f"⊗ 跳过禁用的插件: {plugin_name}")
            continue

        # 加载插件
        plugin = manager.load_plugin(plugin_path)
        if plugin:
            load_count += 1
            if verbose:
                click.echo(f"✓ 加载插件: {plugin.name} v{plugin.version}")
        else:
            if verbose:
                click.echo(f"✗ 加载失败: {plugin_name}")

    # 记录新加载的插件
    new_plugins = set(manager.list_plugin_names())

    if verbose:
        click.echo()
        click.echo(f"成功加载 {load_count} 个插件")
        click.echo()

        # 显示变化
        added = new_plugins - old_plugins
        removed = old_plugins - new_plugins

        if added:
            click.echo("新增插件:")
            for name in sorted(added):
                click.echo(f"  + {name}")

        if removed:
            click.echo("移除插件:")
            for name in sorted(removed):
                click.echo(f"  - {name}")

        if not added and not removed:
            click.echo("插件列表无变化")

    click.echo(f"✓ 插件重新加载完成 ({load_count} 个插件已加载)")
