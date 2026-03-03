"""测试用例示例"""

import pytest
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType


class MockPlugin(BasePlugin):
    """Mock 插件用于测试"""
    name =ser"mock"
    version = "1.0.0"
    description = "Mock plugin for testing"
    plugin_type = PluginType.READER
    
    def is_available(self) -> bool:
        """检查插件是否可用"""
        return True
    
    def execute(self, **kwargs) -> dict:
        """执行插件核心功能"""
        return {
            "status": "success",
            "data": "mock data"
        }


class TestBasePlugin:
    """测试插件基类"""
    
    def test_plugin_metadata(self):
        """测试插件元数据"""
        plugin = MockPlugin()
        assert plugin.name == "mock"
        assert plugin.version == "1.0.0"
        assert plugin.description == "Mock plugin for testing"
        assert plugin.plugin_type == PluginType.READER
    
    def test_lifecycle_hooks(self):
        """测试生命周期钩子"""
        plugin = MockPlugin()
        plugin.on_load()  # 应该被调用
        plugin.on_unload()  # 应该被调用
    
    def test_dependency_check(self):
        """测试依赖检查"""
        plugin = MockPlugin()
        deps_ok, missing = plugin.check_dependencies()
        assert isinstance(deps_ok, bool)
        assert isinstance(missing, list)
    
    def test_validate_input(self):
        """测试输入验证"""
        plugin = MockPlugin()
        result = plugin.validate_input(param1="value1")
        assert result is True
    
    def test_validate_output(self):
        """测试输出验证"""
        plugin = MockPlugin()
        result = plugin.validate_output({"key": "value"})
        assert result is True
    
    def test_get_metadata(self):
        """测试获取元数据"""
        plugin = MockPlugin()
        metadata = plugin.get_metadata()
        assert isinstance(metadata, dict)
        assert "name" in metadata
        assert "version" in metadata
        assert "description" in metadata
        assert "plugin_type" in metadata
    
    def test_is_available(self):
        """测试插件可用性"""
        plugin = MockPlugin()
        assert plugin.is_available() is True
    
    def test_execute(self):
        """测试插件执行"""
        plugin = MockPlugin()
        result = plugin.execute()
        assert isinstance(result, dict)
        assert result["status"] == "success"
