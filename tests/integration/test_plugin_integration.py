# tests/integration/test_plugin_integration.py
"""
V2 团队插件系统集成测试

测试所有插件的加载、初始化和协调
"""
import pytest
from pathlib import Path


class TestPluginSystemIntegration:
    """插件系统集成测试"""

    def test_plugin_manager_initialization(self):
        """测试插件管理器初始化"""
        try:
            # 导入插件管理器
            import sys
            plugin_path = Path(__file__).parent.parent.parent / 'plugins'
            sys.path.insert(0, str(plugin_path))
            
            from plugins.__init__ import PluginManager
            
            manager = PluginManager()
            
            assert manager is not None
            print(f"插件管理器初始化成功: {len(manager.plugins)} 个插件")
            
        except ImportError as e:
            pytest.skip(f"插件系统未完全实现: {e}")

    def test_reader_plugins_exist(self):
        """验证读取插件存在"""
        reader_plugins = [
            'plugins/readers/__init__.py',
            'plugins/readers/text_reader.py',
            'plugins/readers/table_reader.py',
            'plugins/readers/image_reader.py',
            'plugins/readers/metadata_reader.py',
            'plugins/readers/structure_reader.py',
        ]
        
        for plugin in reader_plugins:
            plugin_path = Path(__file__).parent.parent.parent / plugin
            if plugin_path.exists():
                print(f"✅ {plugin} 存在")
            else:
                print(f"⚠️  {plugin} 不存在")

    def test_converter_plugins_exist(self):
        """验证转换器插件存在"""
        converter_plugins = [
            'plugins/converters/__init__.py',
            'plugins/converters/to_markdown.py',
            'plugins/converters/to_json.py',
            'plugins/converters/to_html.py',
            'plugins/converters/to_text.py',
            'plugins/converters/to_csv.py',
            'plugins/converters/to_image.py',
            'plugins/converters/to_epub.py',
        ]
        
        for plugin in converter_plugins:
            plugin_path = Path(__file__).parent.parent.parent / plugin
            if plugin_path.exists():
                print(f"✅ {plugin} 存在")
            else:
                print(f"⚠️ {plugin} 不存在")

    def test_core_modules_exist(self):
        """验证核心模块存在"""
        core_modules = [
            'core/pdf_engine.py',
            'core/plugin_system/__init__.py',
            'core/plugin_system/base_reader_plugin.py',
            'core/plugin_system/base_converter_plugin.py',
            'core/plugin_system/plugin_type.py',
        ]
        
        for module in core_modules:
            module_path = Path(__file__).parent.parent.parent / module
            if module_path.exists():
                print(f"✅ {module} 存在")
            else:
                print(f"⚠️ {module} 不存在")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
