"""插件管理命令"""

import click
import json

from core.plugin_system import PluginManager, PluginType


@click.group('plugin')
@click.pass_context
def plugin_group(ctx):
    """Plugin management commands"""
    pass


@plugin_group.command('list')
@click.option('--type', help='Filter by plugin type')
@click.pass_context
def plugin_list(ctx, type):
    """List all plugins"""
    manager = PluginManager()
    manager.load_all_plugins()
    
    plugins = manager.list_plugins()
    if type:
        plugin_type = PluginType(type)
        plugins = [p for p in plugins if p.plugin_type == plugin_type]
    
    if ctx.obj['json']:
        output = [
            {
                'name': p.name,
                'version': p.version,
                'description': p.description,
                'plugin_type': p.plugin_type.value
            }
            for p in plugins
        ]
        click.echo(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        click.echo(f"{'Name':<25} {'Version':<10} {'Type':<15} {'Description'}")
        click.echo("-" * 80)
        for p in plugins:
            click.echo(f"{p.name:<25} {p.version:<10} {p.plugin_type.value:<15} {p.description}")


@plugin_group.command('info')
@click.argument('name')
@click.pass_context
def plugin_info(ctx, name):
    """Show plugin information"""
    manager = PluginManager()
    manager.load_all_plugins()
    
    info = manager.get_plugin_info(name)
    if not info:
        click.echo(f"Plugin {name} not found", err=True)
        raise SystemExit(1)
    
    if ctx.obj['json']:
        click.echo(json.dumps(info, indent=2, ensure_ascii=False))
    else:
        click.echo(f"Plugin: {info['name']}")
        click.echo(f"Version: {info['version']}")
        click.echo(f"Description: {info['description']}")
        click.echo(f"Type: {info['plugin_type']}")
        click.echo(f"Author: {info.get('author', 'N/A')}")
        click.echo(f"Homepage: {info.get('homepage', 'N/A')}")
        click.echo(f"License: {info.get('license', 'N/A')}")
        click.echo(f"Dependencies: {', '.join(info['dependencies']) or 'None'}")
        click.echo(f"System Dependencies: {', '.join(info['system_dependencies']) or 'None'}")
        click.echo(f"Loaded: {info['loaded']}")
        click.echo(f"Dependencies OK: {info['dependencies_ok']}")


@plugin_group.command('check')
@click.argument('name')
@click.pass_context
def plugin_check(ctx, name):
    """Check plugin dependencies"""
    manager = PluginManager()
    manager.load_all_plugins()
    
    plugin = manager.get_plugin(name)
    if not plugin:
        click.echo(f"Plugin {name} not found", err=True)
        raise SystemExit(1)
    
    deps_ok, missing_deps = plugin.check_dependencies()
    
    if ctx.obj['json']:
        output = {
            'name': name,
            'dependencies_ok': deps_ok,
            'missing_dependencies': missing_deps
        }
        click.echo(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        if deps_ok:
            click.echo(f"✅ Plugin {name} dependencies satisfied")
        else:
            click.echo(f"❌ Plugin {name} missing dependencies: {', '.join(missing_deps)}")


@plugin_group.command('enable')
@click.argument('name')
@click.pass_context
def plugin_enable(ctx, name):
    """Enable a plugin"""
    # 简化实现，后续可以添加禁用/启用机制
    manager = PluginManager()
    manager.load_all_plugins()
    
    plugin = manager.get_plugin(name)
    if not plugin:
        click.echo(f"Plugin {name} not found", err=True)
        raise SystemExit(1)
    
    click.echo(f"Plugin {name} enabled")


@plugin_group.command('disable')
@click.argument('name')
@click.pass_context
def plugin_disable(ctx, name):
    """Disable a plugin"""
    # 简化实现，后续可以添加禁用/启用机制
    manager = PluginManager()
    
    success = manager.unload_plugin(name)
    if success:
        click.echo(f"Plugin {name} disabled")
    else:
        click.echo(f"Failed to disable plugin {name}", err=True)
        raise SystemExit(1)


@plugin_group.command('reload')
@click.argument('name')
@click.pass_context
def plugin_reload(ctx, name):
    """Reload a plugin"""
    manager = PluginManager()
    
    # 先卸载
    manager.unload_plugin(name)
    
    # 重新发现并加载
    discovered = manager.discover_plugins(force_refresh=True)
    for plugin_path in discovered:
        if name in plugin_path:
            plugin = manager.load_plugin(plugin_path)
            if plugin:
                click.echo(f"Plugin {name} reloaded")
                return
    
    click.echo(f"Failed to reload plugin {name}", err=True)
    raise SystemExit(1)
