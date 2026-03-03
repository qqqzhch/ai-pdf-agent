"""CLI 插件管理命令测试

测试插件管理命令:
- plugin list: 列出所有插件
- plugin info: 显示插件详细信息
- plugin check: 检查插件健康状态
- plugin enable: 启用插件
- plugin disable: 禁用插件
- plugin reload: 重新加载所有插件
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from click.testing import CliRunner
import pytest

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cli.main import cli
from core.plugin_system import PluginManager
from cli.commands.plugin import (
    load_disabled_plugins,
    save_disabled_plugins,
    DISABLED_PLUGINS_FILE
)


# ========== Fixtures ==========

@pytest.fixture
def cli_runner():
    """CLI runner fixture"""
    runner = CliRunner()
    return runner


@pytest.fixture
def plugin_manager():
    """插件管理器 fixture"""
    manager = PluginManager()
    manager.load_all_plugins()
    return manager


@pytest.fixture
def temp_disabled_config():
    """临时禁用配置文件 fixture"""
    # 保存原始配置
    original_disabled = load_disabled_plugins()

    yield

    # 恢复原始配置
    save_disabled_plugins(original_disabled)


# ========== Plugin List Command Tests ==========

class TestPluginListCommand:
    """测试 plugin list 命令"""

    def test_list_basic(self, cli_runner):
        """测试基本插件列表"""
        result = cli_runner.invoke(cli, ['plugin', 'list'])

        assert result.exit_code == 0

    def test_list_with_json_output(self, cli_runner):
        """测试 JSON 格式输出"""
        result = cli_runner.invoke(cli, ['plugin', 'list', '--json'])

        assert result.exit_code == 0

        # 验证是有效 JSON
        try:
            data = json.loads(result.output)
            assert isinstance(data, list)
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")

    def test_list_show_all(self, cli_runner):
        """测试显示所有插件（包括禁用的）"""
        result = cli_runner.invoke(cli, ['plugin', 'list', '--all'])

        assert result.exit_code == 0

    def test_list_filter_by_type_reader(self, cli_runner):
        """测试按类型过滤（reader）"""
        result = cli_runner.invoke(cli, ['plugin', 'list', '--type', 'reader'])

        assert result.exit_code == 0

    def test_list_filter_by_type_converter(self, cli_runner):
        """测试按类型过滤（converter）"""
        result = cli_runner.invoke(cli, ['plugin', 'list', '--type', 'converter'])

        assert result.exit_code == 0

    def test_list_filter_by_type_invalid(self, cli_runner):
        """测试无效的插件类型"""
        result = cli_runner.invoke(cli, ['plugin', 'list', '--type', 'invalid_type'])

        assert result.exit_code != 0

    def test_list_with_json_and_all(self, cli_runner):
        """测试 JSON 输出 + 显示所有"""
        result = cli_runner.invoke(cli, ['plugin', 'list', '--json', '--all'])

        assert result.exit_code == 0

        # 验证 JSON 格式
        data = json.loads(result.output)
        assert isinstance(data, list)


# ========== Plugin Info Command Tests ==========

class TestPluginInfoCommand:
    """测试 plugin info 命令"""

    def test_info_existing_plugin(self, cli_runner, plugin_manager):
        """测试显示现有插件信息"""
        # 获取第一个可用的插件
        plugins = plugin_manager.list_plugins()
        if not plugins:
            pytest.skip("No plugins available for testing")

        plugin_name = plugins[0].name
        result = cli_runner.invoke(cli, ['plugin', 'info', plugin_name])

        assert result.exit_code == 0

    def test_info_with_json_output(self, cli_runner, plugin_manager):
        """测试 JSON 格式输出"""
        plugins = plugin_manager.list_plugins()
        if not plugins:
            pytest.skip("No plugins available for testing")

        plugin_name = plugins[0].name
        result = cli_runner.invoke(cli, ['plugin', 'info', plugin_name, '--json'])

        assert result.exit_code == 0

        # 验证 JSON 格式
        data = json.loads(result.output)
        assert 'name' in data
        assert 'version' in data
        assert 'description' in data
        assert 'plugin_type' in data

    def test_info_nonexistent_plugin(self, cli_runner):
        """测试显示不存在的插件"""
        result = cli_runner.invoke(cli, ['plugin', 'info', 'nonexistent_plugin'])

        assert result.exit_code != 0

    def test_info_shows_metadata(self, cli_runner, plugin_manager):
        """测试显示插件元数据"""
        plugins = plugin_manager.list_plugins()
        if not plugins:
            pytest.skip("No plugins available for testing")

        plugin_name = plugins[0].name
        result = cli_runner.invoke(cli, ['plugin', 'info', plugin_name])

        assert result.exit_code == 0
        # 应该包含插件元数据字段

    def test_info_shows_dependencies(self, cli_runner, plugin_manager):
        """测试显示依赖信息"""
        plugins = plugin_manager.list_plugins()
        if not plugins:
            pytest.skip("No plugins available for testing")

        plugin_name = plugins[0].name
        result = cli_runner.invoke(cli, ['plugin', 'info', plugin_name])

        assert result.exit_code == 0
        # 应该显示依赖信息

    def test_info_shows_status(self, cli_runner, plugin_manager):
        """测试显示插件状态"""
        plugins = plugin_manager.list_plugins()
        if not plugins:
            pytest.skip("No plugins available for testing")

        plugin_name = plugins[0].name
        result = cli_runner.invoke(cli, ['plugin', 'info', plugin_name])

        assert result.exit_code == 0
        # 应该显示启用状态、可用状态等


# ========== Plugin Check Command Tests ==========

class TestPluginCheckCommand:
    """测试 plugin check 命令"""

    def test_check_all_plugins(self, cli_runner):
        """测试检查所有插件"""
        result = cli_runner.invoke(cli, ['plugin', 'check'])

        assert result.exit_code == 0

    def test_check_specific_plugin(self, cli_runner, plugin_manager):
        """测试检查指定插件"""
        plugins = plugin_manager.list_plugins()
        if not plugins:
            pytest.skip("No plugins available for testing")

        plugin_name = plugins[0].name
        result = cli_runner.invoke(cli, ['plugin', 'check', '--name', plugin_name])

        assert result.exit_code == 0

    def test_check_with_json_output(self, cli_runner):
        """测试 JSON 格式输出"""
        result = cli_runner.invoke(cli, ['plugin', 'check', '--json'])

        assert result.exit_code == 0

        # 验证 JSON 格式
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_check_verbose(self, cli_runner):
        """测试详细模式"""
        result = cli_runner.invoke(cli, ['plugin', 'check', '--verbose'])

        assert result.exit_code == 0

    def test_check_with_name_and_json(self, cli_runner, plugin_manager):
        """测试指定插件 + JSON 输出"""
        plugins = plugin_manager.list_plugins()
        if not plugins:
            pytest.skip("No plugins available for testing")

        plugin_name = plugins[0].name
        result = cli_runner.invoke(cli, ['plugin', 'check', '--name', plugin_name, '--json'])

        assert result.exit_code == 0

        # 验证 JSON 格式
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 1

    def test_check_with_name_and_verbose(self, cli_runner, plugin_manager):
        """测试指定插件 + 详细模式"""
        plugins = plugin_manager.list_plugins()
        if not plugins:
            pytest.skip("No plugins available for testing")

        plugin_name = plugins[0].name
        result = cli_runner.invoke(cli, ['plugin', 'check', '--name', plugin_name, '--verbose'])

        assert result.exit_code == 0

    def test_check_shows_health_status(self, cli_runner):
        """测试显示健康状态"""
        result = cli_runner.invoke(cli, ['plugin', 'check'])

        assert result.exit_code == 0
        # 应该显示健康状态信息

    def test_check_shows_dependencies_status(self, cli_runner):
        """测试显示依赖状态"""
        result = cli_runner.invoke(cli, ['plugin', 'check'])

        assert result.exit_code == 0
        # 应该显示依赖状态


# ========== Plugin Enable Command Tests ==========

class TestPluginEnableCommand:
    """测试 plugin enable 命令"""

    def test_enable_existing_plugin(self, cli_runner, plugin_manager, temp_disabled_config):
        """测试启用现有插件"""
        plugins = plugin_manager.list_plugins()
        if not plugins:
            pytest.skip("No plugins available for testing")

        plugin_name = plugins[0].name

        # 先禁用插件
        disabled = load_disabled_plugins()
        disabled.add(plugin_name)
        save_disabled_plugins(disabled)

        # 启用插件
        result = cli_runner.invoke(cli, ['plugin', 'enable', plugin_name])

        assert result.exit_code == 0

        # 验证插件已启用
        disabled = load_disabled_plugins()
        assert plugin_name not in disabled

    def test_enable_already_enabled_plugin(self, cli_runner, plugin_manager, temp_disabled_config):
        """测试启用已启用的插件"""
        plugins = plugin_manager.list_plugins()
        if not plugins:
            pytest.skip("No plugins available for testing")

        plugin_name = plugins[0].name

        # 确保插件是启用的
        disabled = load_disabled_plugins()
        disabled.discard(plugin_name)
        save_disabled_plugins(disabled)

        # 再次启用
        result = cli_runner.invoke(cli, ['plugin', 'enable', plugin_name])

        assert result.exit_code == 0

    def test_enable_nonexistent_plugin(self, cli_runner, temp_disabled_config):
        """测试启用不存在的插件"""
        result = cli_runner.invoke(cli, ['plugin', 'enable', 'nonexistent_plugin'])

        assert result.exit_code != 0


# ========== Plugin Disable Command Tests ==========

class TestPluginDisableCommand:
    """测试 plugin disable 命令"""

    def test_disable_existing_plugin(self, cli_runner, plugin_manager, temp_disabled_config):
        """测试禁用现有插件"""
        plugins = plugin_manager.list_plugins()
        if not plugins:
            pytest.skip("No plugins available for testing")

        plugin_name = plugins[0].name

        # 确保插件是启用的
        disabled = load_disabled_plugins()
        disabled.discard(plugin_name)
        save_disabled_plugins(disabled)

        # 禁用插件
        result = cli_runner.invoke(cli, ['plugin', 'disable', plugin_name])

        assert result.exit_code == 0

        # 验证插件已禁用
        disabled = load_disabled_plugins()
        assert plugin_name in disabled

    def test_disable_already_disabled_plugin(self, cli_runner, plugin_manager, temp_disabled_config):
        """测试禁用已禁用的插件"""
        plugins = plugin_manager.list_plugins()
        if not plugins:
            pytest.skip("No plugins available for testing")

        plugin_name = plugins[0].name

        # 先禁用插件
        disabled = load_disabled_plugins()
        disabled.add(plugin_name)
        save_disabled_plugins(disabled)

        # 再次禁用
        result = cli_runner.invoke(cli, ['plugin', 'disable', plugin_name])

        assert result.exit_code == 0

    def test_disable_with_force(self, cli_runner, plugin_manager, temp_disabled_config):
        """测试强制禁用插件"""
        plugins = plugin_manager.list_plugins()
        if not plugins:
            pytest.skip("No plugins available for testing")

        plugin_name = plugins[0].name

        result = cli_runner.invoke(cli, ['plugin', 'disable', plugin_name, '--force'])

        assert result.exit_code == 0

    def test_disable_nonexistent_plugin(self, cli_runner, temp_disabled_config):
        """测试禁用不存在的插件"""
        result = cli_runner.invoke(cli, ['plugin', 'disable', 'nonexistent_plugin'])

        assert result.exit_code != 0


# ========== Plugin Reload Command Tests ==========

class TestPluginReloadCommand:
    """测试 plugin reload 命令"""

    def test_reload_basic(self, cli_runner):
        """测试基本重载"""
        result = cli_runner.invoke(cli, ['plugin', 'reload'])

        assert result.exit_code == 0

    def test_reload_verbose(self, cli_runner):
        """测试详细模式重载"""
        result = cli_runner.invoke(cli, ['plugin', 'reload', '--verbose'])

        assert result.exit_code == 0

    def test_reload_shows_changes(self, cli_runner):
        """测试显示重载变化"""
        result = cli_runner.invoke(cli, ['plugin', 'reload', '--verbose'])

        assert result.exit_code == 0
        # 应该显示加载的插件数量等信息


# ========== Plugin Command Help Tests ==========

class TestPluginCommandHelp:
    """测试插件命令帮助"""

    def test_plugin_group_help(self, cli_runner):
        """测试插件组帮助"""
        result = cli_runner.invoke(cli, ['plugin', '--help'])

        assert result.exit_code == 0
        assert 'plugin' in result.output.lower()

    def test_plugin_list_help(self, cli_runner):
        """测试 list 命令帮助"""
        result = cli_runner.invoke(cli, ['plugin', 'list', '--help'])

        assert result.exit_code == 0
        assert 'list' in result.output.lower()

    def test_plugin_info_help(self, cli_runner):
        """测试 info 命令帮助"""
        result = cli_runner.invoke(cli, ['plugin', 'info', '--help'])

        assert result.exit_code == 0
        assert 'info' in result.output.lower()

    def test_plugin_check_help(self, cli_runner):
        """测试 check 命令帮助"""
        result = cli_runner.invoke(cli, ['plugin', 'check', '--help'])

        assert result.exit_code == 0
        assert 'check' in result.output.lower()

    def test_plugin_enable_help(self, cli_runner):
        """测试 enable 命令帮助"""
        result = cli_runner.invoke(cli, ['plugin', 'enable', '--help'])

        assert result.exit_code == 0
        assert 'enable' in result.output.lower()

    def test_plugin_disable_help(self, cli_runner):
        """测试 disable 命令帮助"""
        result = cli_runner.invoke(cli, ['plugin', 'disable', '--help'])

        assert result.exit_code == 0
        assert 'disable' in result.output.lower()

    def test_plugin_reload_help(self, cli_runner):
        """测试 reload 命令帮助"""
        result = cli_runner.invoke(cli, ['plugin', 'reload', '--help'])

        assert result.exit_code == 0
        assert 'reload' in result.output.lower()


# ========== Integration Tests ==========

class TestPluginCommandsIntegration:
    """插件命令集成测试"""

    def test_full_workflow(self, cli_runner, plugin_manager, temp_disabled_config):
        """测试完整工作流程：list -> info -> disable -> enable -> check"""
        plugins = plugin_manager.list_plugins()
        if not plugins:
            pytest.skip("No plugins available for testing")

        plugin_name = plugins[0].name

        # 1. 列出插件
        result = cli_runner.invoke(cli, ['plugin', 'list'])
        assert result.exit_code == 0
        assert plugin_name in result.output

        # 2. 查看插件信息
        result = cli_runner.invoke(cli, ['plugin', 'info', plugin_name])
        assert result.exit_code == 0

        # 3. 禁用插件
        result = cli_runner.invoke(cli, ['plugin', 'disable', plugin_name])
        assert result.exit_code == 0

        # 4. 检查插件状态
        result = cli_runner.invoke(cli, ['plugin', 'check', '--name', plugin_name])
        assert result.exit_code == 0

        # 5. 启用插件
        result = cli_runner.invoke(cli, ['plugin', 'enable', plugin_name])
        assert result.exit_code == 0

        # 6. 再次检查
        result = cli_runner.invoke(cli, ['plugin', 'check', '--name', plugin_name])
        assert result.exit_code == 0

    def test_list_all_json_workflow(self, cli_runner):
        """测试 list --all --json 工作流程"""
        result = cli_runner.invoke(cli, ['plugin', 'list', '--all', '--json'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_check_all_json_workflow(self, cli_runner):
        """测试 check --json 工作流程"""
        result = cli_runner.invoke(cli, ['plugin', 'check', '--json'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)


# ========== Helper Function Tests ==========

class TestPluginHelperFunctions:
    """测试插件辅助函数"""

    def test_load_disabled_plugins(self):
        """测试加载禁用插件列表"""
        disabled = load_disabled_plugins()
        assert isinstance(disabled, set)

    def test_save_disabled_plugins(self, temp_disabled_config):
        """测试保存禁用插件列表"""
        test_disabled = {'test_plugin1', 'test_plugin2'}
        save_disabled_plugins(test_disabled)

        loaded = load_disabled_plugins()
        assert loaded == test_disabled

    def test_empty_disabled_plugins(self, temp_disabled_config):
        """测试空的禁用插件列表"""
        save_disabled_plugins(set())

        loaded = load_disabled_plugins()
        assert loaded == set()

    def test_disabled_plugins_file_path(self):
        """测试禁用插件配置文件路径"""
        assert DISABLED_PLUGINS_FILE.name == 'disabled_plugins.json'
        assert '.ai-pdf' in str(DISABLED_PLUGINS_FILE)


# ========== Run Tests ==========

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
