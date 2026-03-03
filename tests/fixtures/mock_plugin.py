"""Mock 插件用于测试"""

from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType


class MockPlugin(BasePlugin):
    """Mock 插件用于测试"""
    name = "mock"
    version = "1.0.0"
    description = "Mock plugin for testing"
    plugin_type = PluginType.READER
    author = "Test Author"
    homepage = "https://example.com.com"
    license = "MIT"
    dependencies = []
    system_dependencies = []
    
    def __init__(self):
        super().__init__()
        self.loaded = False
    
    def is_available(self) -> bool:
        """检查插件是否可用"""
        return True
    
    def execute(self, **kwargs) -> dict:
        """执行插件核心功能"""
        return {
            "status": "success",
            "data": "mock data",
            "kwargs": kwargs
        }
    
    def on_load(self) -> None:
        """插件加载时调用"""
        super().on_load()
        self.loaded = True
    
    def on_unload(self) -> None:
        """插件卸载时调用"""
        super().on_unload()
        self.loaded = False
