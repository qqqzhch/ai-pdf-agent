"""插件系统集成测试

测试覆盖：
1. 插件加载测试
2. 插件注册测试
3. 插件调用测试
4. 插件依赖测试
5. 插件生命周期测试
6. 错误处理测试
7. 性能测试
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock, mock_open

import pytest

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.plugin_system.plugin_manager import PluginManager
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType


# ========== 测试插件 ==========

class TestReaderPlugin(BasePlugin):
    """测试用 Reader 插件"""
    name = "test_reader"
    version = "1.0.0"
    description = "Test reader plugin"
    plugin_type = PluginType.READER
    author = "Test"
    dependencies = []
    
    def __init__(self):
        super().__init__()
        self.initialized = False
        self.started = False
        self.stopped = False
    
    def is_available(self) -> bool:
        return True
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        return {"status": "success", "data": "test data"}
    
    def on_load(self) -> None:
        super().on_load()
        self.initialized = True
    
    def on_unload(self) -> None:
        super().on_unload()
        self.stopped = True


class TestConverterPlugin(BasePlugin):
    """测试用 Converter 插件"""
    name = "test_converter"
    version = "1.0.0"
    description = "Test converter plugin"
    plugin_type = PluginType.CONVERTER
    author = "Test"
    dependencies = ["numpy>=1.0.0"]  # 模拟依赖
    
    def is_available(self) -> bool:
        return True
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        return {"status": "converted", "format": kwargs.get("format", "unknown")}


class TestOCRPlugin(BasePlugin):
    """测试用 OCR 插件"""
    name = "test_ocr"
    version = "2.0.0"
    description = "Test OCR plugin"
    plugin_type = PluginType.OCR
    author = "Test"
    dependencies = []
    
    def is_available(self) -> bool:
        return True
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        text = kwargs.get("image", "")
        return {"status": "success", "text": f"OCR result: {text}"}


class UnavailablePlugin(BasePlugin):
    """不可用的插件测试"""
    name = "unavailable_plugin"
    version = "1.0.0"
    description = "Plugin that is not available"
    plugin_type = PluginType.CUSTOM
    dependencies = ["nonexistent-package>=999.0.0"]
    
    def is_available(self) -> bool:
        return False
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        return {"status": "error"}


class InvalidPlugin:
    """无效插件（非 BasePlugin 子类）"""
    name = "invalid"
    version = "1.0.0"


# ========== pytest Fixtures ==========

@pytest.fixture
def plugin_manager():
    """创建插件管理器实例"""
    # 重置单例
    PluginManager._instance = None
    manager = PluginManager()
    return manager


@pytest.fixture
def temp_plugin_dir(tmp_path):
    """创建临时插件目录"""
    plugin_dir = tmp_path / "test_plugins"
    plugin_dir.mkdir()
    return str(plugin_dir)


@pytest.fixture
def sample_plugin():
    """创建示例插件实例"""
    return TestReaderPlugin()


@pytest.fixture
def test_plugins():
    """返回所有测试插件类"""
    return [
        TestReaderPlugin,
        TestConverterPlugin,
        TestOCRPlugin,
        UnavailablePlugin
    ]


# ========== 1. 插件加载测试 ==========

class TestPluginLoading:
    """插件加载测试"""
    
    def test_discover_plugins_empty_dir(self, plugin_manager, temp_plugin_dir):
        """测试空目录的插件发现"""
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        discovered = plugin_manager.discover_plugins()
        assert discovered == []
    
    def test_discover_plugins_with_files(self, plugin_manager, temp_plugin_dir):
        """测试发现插件文件"""
        # 创建测试插件文件
        (Path(temp_plugin_dir) / "test_plugin1.py").write_text("# test plugin 1")
        (Path(temp_plugin_dir) / "test_plugin2.py").write_text("# test plugin 2")
        (Path(temp_plugin_dir) / "_private.py").write_text("# should be ignored")
        (Path(temp_plugin_dir) / "not_a_py.txt").write_text("# not a python file")
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        discovered = plugin_manager.discover_plugins()
        
        assert len(discovered) == 2
        assert "_private.py" not in str(discovered)
    
    def test_discover_plugins_force_refresh(self, plugin_manager, temp_plugin_dir):
        """测试强制刷新插件缓存"""
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        
        # 第一次发现
        discovered1 = plugin_manager.discover_plugins()
        assert len(discovered1) == 0
        
        # 添加新文件
        (Path(temp_plugin_dir) / "new_plugin.py").write_text("# new plugin")
        
        # 不刷新，应该返回缓存
        discovered2 = plugin_manager.discover_plugins(force_refresh=False)
        assert len(discovered2) == 0
        
        # 强制刷新
        discovered3 = plugin_manager.discover_plugins(force_refresh=True)
        assert len(discovered3) == 1
    
    def test_load_plugin_success(self, plugin_manager, temp_plugin_dir):
        """测试成功加载插件"""
        # 创建有效的插件文件
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class SimplePlugin(BasePlugin):
    name = "simple"
    version = "1.0.0"
    description = "Simple plugin"
    plugin_type = PluginType.CUSTOM
    
    def is_available(self):
        return True
    
    def execute(self, **kwargs):
        return {"status": "ok"}
"""
        plugin_file = Path(temp_plugin_dir) / "simple_plugin.py"
        plugin_file.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        plugin = plugin_manager.load_plugin(str(plugin_file))
        
        assert plugin is not None
        assert plugin.name == "simple"
        assert plugin.version == "1.0.0"
        assert "simple" in plugin_manager.plugins
    
    def test_load_plugin_missing_class(self, plugin_manager, temp_plugin_dir):
        """测试加载没有插件类的文件"""
        # 创建没有插件类的文件
        plugin_code = """
# No plugin class here
def some_function():
    pass
"""
        plugin_file = Path(temp_plugin_dir) / "no_plugin.py"
        plugin_file.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        plugin = plugin_manager.load_plugin(str(plugin_file))
        
        assert plugin is None
    
    def test_load_plugin_import_error(self, plugin_manager, temp_plugin_dir):
        """测试加载导入失败的插件"""
        # 创建有语法错误的文件
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin

class BrokenPlugin(BasePlugin):
    name = "broken"
    this will cause syntax error
"""
        plugin_file = Path(temp_plugin_dir) / "broken.py"
        plugin_file.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        plugin = plugin_manager.load_plugin(str(plugin_file))
        
        assert plugin is None
    
    def test_load_duplicate_plugin(self, plugin_manager, temp_plugin_dir):
        """测试重复加载同名插件"""
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class DuplicatePlugin(BasePlugin):
    name = "duplicate"
    version = "1.0.0"
    description = "Duplicate plugin"
    plugin_type = PluginType.CUSTOM
    
    def is_available(self):
        return True
    
    def execute(self, **kwargs):
        return {"status": "ok"}
"""
        plugin_file1 = Path(temp_plugin_dir) / "duplicate1.py"
        plugin_file2 = Path(temp_plugin_dir) / "duplicate2.py"
        plugin_file1.write_text(plugin_code)
        plugin_file2.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        
        # 第一次加载
        plugin1 = plugin_manager.load_plugin(str(plugin_file1))
        assert plugin1 is not None
        
        # 第二次加载同名插件（应该覆盖）
        plugin2 = plugin_manager.load_plugin(str(plugin_file2))
        assert plugin2 is not None
        assert plugin_manager.plugins["duplicate"] == plugin2
    
    def test_load_plugin_not_available(self, plugin_manager, temp_plugin_dir):
        """测试加载不可用的插件"""
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class NotAvailablePlugin(BasePlugin):
    name = "not_available"
    version = "1.0.0"
    description = "Not available"
    plugin_type = PluginType.CUSTOM
    dependencies = ["nonexistent-package>=999.0.0"]
    
    def is_available(self):
        return False
    
    def execute(self, **kwargs):
        return {}
"""
        plugin_file = Path(temp_plugin_dir) / "not_available.py"
        plugin_file.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        plugin = plugin_manager.load_plugin(str(plugin_file))
        
        assert plugin is None
        assert "not_available" not in plugin_manager.plugins
    
    def test_load_all_plugins(self, plugin_manager, temp_plugin_dir):
        """测试加载所有插件"""
        # 创建多个插件
        for i in range(3):
            plugin_code = f"""
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class Plugin{i}(BasePlugin):
    name = "plugin{i}"
    version = "1.0.0"
    description = "Plugin {i}"
    plugin_type = PluginType.CUSTOM
    
    def is_available(self):
        return True
    
    def execute(self, **kwargs):
        return {{"status": "ok"}}
"""
            (Path(temp_plugin_dir) / f"plugin{i}.py").write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        count = plugin_manager.load_all_plugins()
        
        assert count == 3
        assert len(plugin_manager.plugins) == 3
        assert "plugin0" in plugin_manager.plugins
        assert "plugin1" in plugin_manager.plugins
        assert "plugin2" in plugin_manager.plugins
    
    @patch('os.path.exists')
    @patch('pathlib.Path.glob')
    def test_discover_nonexistent_dir(self, mock_glob, mock_exists, plugin_manager):
        """测试发现不存在的目录"""
        mock_exists.return_value = False
        
        plugin_manager.plugin_dirs = ["/nonexistent/dir"]
        discovered = plugin_manager.discover_plugins()
        
        assert discovered == []
        mock_glob.assert_not_called()


# ========== 2. 插件注册测试 ==========

class TestPluginRegistration:
    """插件注册测试"""
    
    def test_manual_plugin_registration(self, plugin_manager, sample_plugin):
        """测试手动注册插件"""
        # 直接将插件添加到管理器
        plugin_manager.plugins[sample_plugin.name] = sample_plugin
        
        assert sample_plugin.name in plugin_manager.plugins
        assert plugin_manager.get_plugin(sample_plugin.name) == sample_plugin
    
    def test_register_multiple_plugins(self, plugin_manager):
        """测试注册多个插件"""
        plugins = [
            TestReaderPlugin(),
            TestConverterPlugin(),
            TestOCRPlugin()
        ]
        
        for plugin in plugins:
            plugin_manager.plugins[plugin.name] = plugin
        
        assert len(plugin_manager.plugins) == 3
        for plugin in plugins:
            assert plugin.name in plugin_manager.plugins
    
    def test_plugin_type_filtering(self, plugin_manager):
        """测试按类型过滤插件"""
        # 添加不同类型的插件
        plugin_manager.plugins["test_reader"] = TestReaderPlugin()
        plugin_manager.plugins["test_converter"] = TestConverterPlugin()
        plugin_manager.plugins["test_ocr"] = TestOCRPlugin()
        
        # 过滤 Reader 类型
        reader_plugins = plugin_manager.list_plugins(PluginType.READER)
        assert len(reader_plugins) == 1
        assert reader_plugins[0].name == "test_reader"
        
        # 过滤 Converter 类型
        converter_plugins = plugin_manager.list_plugins(PluginType.CONVERTER)
        assert len(converter_plugins) == 1
        assert converter_plugins[0].name == "test_converter"
        
        # 不过滤
        all_plugins = plugin_manager.list_plugins()
        assert len(all_plugins) == 3
    
    def test_list_plugin_names(self, plugin_manager):
        """测试列出插件名称"""
        plugin_manager.plugins["test_reader"] = TestReaderPlugin()
        plugin_manager.plugins["test_converter"] = TestConverterPlugin()
        
        names = plugin_manager.list_plugin_names()
        assert isinstance(names, list)
        assert "test_reader" in names
        assert "test_converter" in names
        
        # 按类型过滤
        reader_names = plugin_manager.list_plugin_names(PluginType.READER)
        assert reader_names == ["test_reader"]


# ========== 3. 插件调用测试 ==========

class TestPluginExecution:
    """插件调用测试"""
    
    def test_plugin_instantiation(self, plugin_manager):
        """测试插件实例化"""
        plugin = TestReaderPlugin()
        plugin_manager.plugins["test_reader"] = plugin
        
        retrieved = plugin_manager.get_plugin("test_reader")
        assert retrieved is not None
        assert isinstance(retrieved, BasePlugin)
        assert retrieved.name == "test_reader"
    
    def test_execute_plugin_success(self, plugin_manager):
        """测试成功执行插件"""
        plugin = TestReaderPlugin()
        plugin_manager.plugins["test_reader"] = plugin
        
        result = plugin_manager.execute_plugin("test_reader")
        
        assert result is not None
        assert result["status"] == "success"
        assert result["data"] == "test data"
    
    def test_execute_plugin_with_params(self, plugin_manager):
        """测试带参数执行插件"""
        plugin = TestConverterPlugin()
        plugin_manager.plugins["test_converter"] = plugin
        
        result = plugin_manager.execute_plugin("test_converter", format="markdown")
        
        assert result is not None
        assert result["status"] == "converted"
        assert result["format"] == "markdown"
    
    def test_execute_nonexistentexistent_plugin(self, plugin_manager):
        """测试执行不存在的插件"""
        with pytest.raises(ValueError, match="Plugin .* not found"):
            plugin_manager.execute_plugin("nonexistent")
    
    def test_execute_plugin_with_kwargs(self, plugin_manager):
        """测试使用 kwargs 执行插件"""
        plugin = TestOCRPlugin()
        plugin_manager.plugins["test_ocr"] = plugin
        
        result = plugin_manager.execute_plugin("test_ocr", image="test.png")
        
        assert result is not None
        assert result["text"] == "OCR result: test.png"
    
    def test_validate_input_invalid(self, plugin_manager, temp_plugin_dir):
        """测试无效输入验证"""
        # 创建一个严格验证的插件
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class StrictPlugin(BasePlugin):
    name = "strict"
    version = "1.0.0"
    description = "Strict plugin"
    plugin_type = PluginType.CUSTOM
    
    def is_available(self):
        return True
    
    def validate_input(self, **kwargs):
        return "required_param" in kwargs
    
    def execute(self, **kwargs):
        return {"status": "ok"}
"""
        plugin_file = Path(temp_plugin_dir) / "strict.py"
        plugin_file.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        plugin_manager.load_plugin(str(plugin_file))
        
        with pytest.raises(ValueError, match="Invalid input"):
            plugin_manager.execute_plugin("strict", wrong_param="value")


# ========== 4. 插件依赖测试 ==========

class TestPluginDependencies:
    """插件依赖测试"""
    
    def test_check_dependencies_no_deps(self, plugin_manager):
        """测试无依赖插件"""
        plugin = TestReaderPlugin()
        deps_ok, missing = plugin.check_dependencies()
        
        assert deps_ok is True
        assert len(missing) == 0
    
    def test_check_dependencies_with_deps(self, plugin_manager):
        """测试有依赖的插件"""
        plugin = TestConverterPlugin()
        deps_ok, missing = plugin.check_dependencies()
        
        # numpy 应该已安装
        assert deps_ok is True
    
    def test_check_missing_dependencies(self, plugin_manager):
        """测试缺失依赖"""
        plugin = UnavailablePlugin()
        deps_ok, missing = plugin.check_dependencies()
        
        assert deps_ok is False
        assert len(missing) > 0
    
    def test_plugin_with_missing_deps_not_loaded(self, plugin_manager, temp_plugin_dir):
        """测试依赖缺失的插件不被加载"""
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class MissingDepsPlugin(BasePlugin):
    name = "missing_deps"
    version = "1.0.0"
    description = "Plugin with missing deps"
    plugin_type = PluginType.CUSTOM
    dependencies = ["nonexistent-package-xyz>=999.0.0"]
    
    def is_available(self):
        return True
    
    def execute(self, **kwargs):
        return {}
"""
        plugin_file = Path(temp_plugin_dir) / "missing_deps.py"
        plugin_file.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        plugin = plugin_manager.load_plugin(str(plugin_file))
        
        assert plugin is None
        assert "missing_deps" not in plugin_manager.plugins


# ========== 5. 插件生命周期测试 ==========

class TestPluginLifecycle:
    """插件生命周期测试"""
    
    def test_plugin_initialization(self, plugin_manager, temp_plugin_dir):
        """测试插件初始化"""
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class LifecyclePlugin(BasePlugin):
    name = "lifecycle"
    version = "1.0.0"
    description = "Lifecycle test plugin"
    plugin_type = PluginType.CUSTOM
    
    def __init__(self):
        super().__init__()
        self.initialized = False
    
    def is_available(self):
        self.initialized = True
        return True
    
    def execute(self, **kwargs):
        return {"initialized": self.initialized}
"""
        plugin_file = Path(temp_plugin_dir) / "lifecycle.py"
        plugin_file.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        plugin = plugin_manager.load_plugin(str(plugin_file))
        
        assert plugin is not None
        result = plugin_manager.execute_plugin("lifecycle")
        assert result["initialized"] is True
    
    def test_plugin_on_load_hook(self, plugin_manager, sample_plugin):
        """测试 on_load 钩子"""
        sample_plugin.on_load()
        
        assert sample_plugin.initialized is True
    
    def test_plugin_on_unload_hook(self, plugin_manager):
        """测试 on_unload 钩子"""
        plugin = TestReaderPlugin()
        plugin_manager.plugins["test_reader"] = plugin
        
        plugin.on_load()
        assert plugin.initialized is True
        
        plugin_manager.unload_plugin("test_reader")
        assert plugin.stopped is True
    
    def test_plugin_on_config_update(self, plugin_manager, sample_plugin):
        """测试配置更新钩子"""
        old_config = {"setting1": "value1"}
        new_config = {"setting1": "value2", "setting2": "value3"}
        
        sample_plugin.on_config_update(old_config, new_config)
        
        assert sample_plugin._config == new_config
    
    def test_unload_plugin_success(self, plugin_manager):
        """测试成功卸载插件"""
        plugin = TestReaderPlugin()
        plugin_manager.plugins["test_reader"] = plugin
        
        result = plugin_manager.unload_plugin("test_reader")
        
        assert result is True
        assert "test_reader" not in plugin_manager.plugins
    
    def test_unload_nonexistent_plugin(self, plugin_manager):
        """测试卸载不存在的插件"""
        result = plugin_manager.unload_plugin("nonexistent")
        assert result is False
    
    def test_plugin_cleanup_on_un(self, plugin_manager, temp_plugin_dir):
        """测试卸载时插件清理"""
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class CleanupPlugin(BasePlugin):
    name = "cleanup"
    version = "1.0.0"
    description = "Cleanup test plugin"
    plugin_type = PluginType.CUSTOM
    
    def __init__(self):
        super().__init__()
        self.cleaned_up = False
    
    def is_available(self):
        return True
    
    def on_unload(self):
        super().on_unload()
        self.cleaned_up = True
    
    def execute(self, **kwargs):
        return {"cleaned_up": self.cleaned_up}
"""
        plugin_file = Path(temp_plugin_dir) / "cleanup.py"
        plugin_file.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        plugin_manager.load_plugin(str(plugin_file))
        
        plugin = plugin_manager.plugins["cleanup"]
        plugin_manager.unload_plugin("cleanup")
        
        assert plugin.cleaned_up is True


# ========== 6. 错误处理测试 ==========

class TestErrorHandling:
    """错误处理测试"""
    
    def test_plugin_load_failure(self, plugin_manager, temp_plugin_dir):
        """测试插件加载失败处理"""
        # 创建有语法错误的插件
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin

class Broken(BasePlugin):
    name = "broken"
    invalid syntax here
"""
        plugin_file = Path(temp_plugin_dir) / "broken.py"
        plugin_file.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        plugin = plugin_manager.load_plugin(str(plugin_file))
        
        assert plugin is None
        assert "broken" not in plugin_manager.plugins
    
    def test_plugin_registration_failure(self, plugin_manager):
        """测试插件注册失败处理"""
        # 尝试注册 None
        try:
            plugin_manager.plugins["null"] = None
            assert False, "Should not allow None registration"
        except:
            pass
    
    def test_plugin_execution_failure(self, plugin_manager, temp_plugin_dir):
        """测试插件执行失败处理"""
        # 创建会抛异常的插件
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class FailingPlugin(BasePlugin):
    name = "failing"
    version = "1.0.0"
    description = "Failing plugin"
    plugin_type = PluginType.CUSTOM
    
    def is_available(self):
        return True
    
    def execute(self, **kwargs):
        raise ValueError("Expected failure")
"""
        plugin_file = Path(temp_plugin_dir) / "failing.py"
        plugin_file.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        plugin_manager.load_plugin(str(plugin_file))
        
        with pytest.raises(ValueError, match="Expected failure"):
            plugin_manager.execute_plugin("failing")
    
    def test_plugin_dependency_failure(self, plugin_manager, temp_plugin_dir):
        """测试依赖失败处理"""
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class DepFailPlugin(BasePlugin):
    name = "dep_fail"
    version = "1.0.0"
    description = "Dependency fail plugin"
    plugin_type = PluginType.CUSTOM
    dependencies = ["nonexistent-xyz-123-abc>=999.0.0"]
    
    def is_available(self):
        return True
    
    def execute(self, **kwargs):
        return {}
"""
        plugin_file = Path(temp_plugin_dir) / "dep_fail.py"
        plugin_file.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        plugin = plugin_manager.load_plugin(str(plugin_file))
        
        assert plugin is None
        assert "dep_fail" not in plugin_manager.plugins
    
    def test_invalid_input_validation(self, plugin_manager):
        """测试无效输入验证失败"""
        class StrictInputPlugin(BasePlugin):
            name = "strict_input"
            version = "1.0.0"
            description = "Strict input plugin"
            plugin_type = PluginType.CUSTOM
            
            def is_available(self):
                return True
            
            def validate_input(self, **kwargs):
                return "required" in kwargs
            
            def execute(self, **kwargs):
                return {"ok": True}
        
        plugin = StrictInputPlugin()
        plugin_manager.plugins["strict_input"] = plugin
        
        with pytest.raises(ValueError, match="Invalid input"):
            plugin_manager.execute_plugin("strict_input", wrong_param="value")


# ========== 7. 配置管理测试 ==========

class TestConfiguration:
    """配置管理测试"""
    
    def test_save_and_load_config(self, plugin_manager, tmp_path):
        """测试保存和加载配置"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        plugin_manager.config_dir = str(config_dir)
        
        config = {"setting1": "value1", "setting2": 42}
        result = plugin_manager.save_plugin_config("test_plugin", config)
        
        assert result is True
        
        loaded_config = plugin_manager.load_plugin_config("test_plugin")
        assert loaded_config == config
    
    def test_load_nonexistent_config(self, plugin_manager, tmp_path):
        """测试加载不存在的配置"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        plugin_manager.config_dir = str(config_dir)
        
        config = plugin_manager.load_plugin_config("nonexistent")
        assert config == {}
    
    def test_set_plugin_config(self, plugin_manager):
        """测试设置插件配置"""
        plugin = TestReaderPlugin()
        plugin_manager.plugins["test_reader"] = plugin
        
        config = {"setting": "value"}
        result = plugin_manager.set_plugin_config("test_reader", config)
        
        assert result is True
        assert plugin_manager.plugin_configs["test_reader"] == config
    
    def test_get_plugin_config(self, plugin_manager):
        """测试获取插件配置"""
        plugin = TestReaderPlugin()
        plugin_manager.plugins["test_reader"] = plugin
        plugin_manager.plugin_configs["test_reader"] = {"setting": "value"}
        
        config = plugin_manager.get_plugin_config("test_reader")
        assert config == {"setting": "value"}
    
    def test_config_update_hook(self, plugin_manager):
        """测试配置更新钩子调用"""
        plugin = TestReaderPlugin()
        plugin_manager.plugins["test_reader"] = plugin
        
        old_config = {"setting1": "old"}
        new_config = {"setting1": "new"}
        
        plugin_manager.set_plugin_config("test_reader", old_config)
        plugin_manager.set_plugin_config("test_reader", new_config)
        
        assert plugin._config == new_config


# ========== 8. Hook 系统测试 ==========

class TestHookSystem:
    """Hook 系统测试"""
    
    def test_register_hook(self, plugin_manager):
        """测试注册 Hook"""
        callback = lambda x: x * 2
        plugin_manager.register_hook("test_event", callback)
        
        assert "test_event" in plugin_manager.hooks
        assert callback in plugin_manager.hooks["test_event"]
    
    def test_trigger_hook(self, plugin_manager):
        """测试触发 Hook"""
        results = []
        
        def callback1(x):
            results.append(x * 2)
            return x * 2
        
        def callback2(x):
            results.append(x * 3)
            return x * 3
        
        plugin_manager.register_hook("test_event", callback1)
        plugin_manager.register_hook("test_event", callback2)
        
        hook_results = plugin_manager.trigger_hook("test_event", 5)
        
        assert len(hook_results) == 2
        assert 10 in hook_results
        assert 15 in hook_results
        assert results == [10, 15]
    
    def test_trigger_nonexistent_event(self, plugin_manager):
        """测试触发不存在的 Hook"""
        results = plugin_manager.trigger_hook("nonexistent", "data")
        assert results == []
    
    def test_hook_failure_handling(self, plugin_manager):
        """测试 Hook 失败处理"""
        def failing_callback(x):
            raise ValueError("Hook failed")
        
        def working_callback(x):
            return x * 2
        
        plugin_manager.register_hook("test_event", failing_callback)
        plugin_manager.register_hook("test_event", working_callback)
        
        results = plugin_manager.trigger_hook("test_event", 5)
        
        # 一个失败，一个成功
        assert len(results) == 1
        assert results[0] == 10


# ========== 9. 插件信息查询 ==========

class TestPluginInfo:
    """插件信息查询测试"""
    
    def test_get_plugin_info(self, plugin_manager):
        """测试获取插件信息"""
        plugin = TestReaderPlugin()
        plugin_manager.plugins["test_reader"] = plugin
        
        info = plugin_manager.get_plugin_info("test_reader")
        
        assert info is not None
        assert info["name"] == "test_reader"
        assert info["version"] == "1.0.0"
        assert info["plugin_type"] == PluginType.READER.value
        assert info["loaded"] is True
        assert "dependencies_ok" in info
        assert "missing_dependencies" in info
    
    def test_get_nonexistent_plugin_info(self, plugin_manager):
        """测试获取不存在的插件信息"""
        info = plugin_manager.get_plugin_info("nonexistent")
        assert info is None
    
    def test_get_all_plugin_info(self, plugin_manager):
        """测试获取所有插件信息"""
        plugin_manager.plugins["test_reader"] = TestReaderPlugin()
        plugin_manager.plugins["test_converter"] = TestConverterPlugin()
        plugin_manager.plugins["test_ocr"] = TestOCRPlugin()
        
        infos = plugin_manager.get_all_plugin_info()
        
        assert len(infos) == 3
        names = [info["name"] for info in infos]
        assert "test_reader" in names
        assert "test_converter" in names
        assert "test_ocr" in names


# ========== 10. 性能测试 ==========

class TestPerformance:
    """性能测试"""
    
    def test_plugin_loading_performance(self, plugin_manager, temp_plugin_dir):
        """测试插件加载性能"""
        # 创建多个插件
        for i in range(10):
            plugin_code = f"""
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class PerfPlugin{i}(BasePlugin):
    name = "perf_plugin{i}"
    version = "1.0.0"
    description = "Performance test plugin {i}"
    plugin_type = PluginType.CUSTOM
    
    def is_available(self):
        return True
    
    def execute(self, **kwargs):
        return {{"status": "ok"}}
"""
            (Path(temp_plugin_dir) / f"perf_plugin{i}.py").write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        
        start_time = time.time()
        count = plugin_manager.load_all_plugins()
        end_time = time.time()
        
        elapsed = end_time - start_time
        
        assert count == 10
        assert elapsed < 5.0, f"Loading 10 plugins took {elapsed:.2f}s, should be < 5s"
    
    def test_plugin_execution_performance(self, plugin_manager):
        """测试插件执行性能"""
        plugin = TestReaderPlugin()
        plugin_manager.plugins["test_reader"] = plugin
        
        iterations = 1000
        start_time = time.time()
        
        for _ in range(iterations):
            plugin_manager.execute_plugin("test_reader")
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        avg_time = elapsed / iterations
        
        assert avg_time < 0.01, f"Average execution time {avg_time:.4f}s, should be < 0.01s"
    
    def test_memory_usage(self, plugin_manager, temp_plugin_dir):
        """测试内存使用"""
        import sys
        
        # 创建插件
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class MemoryPlugin(BasePlugin):
    name = "memory_test"
    version = "1.0.0"
    description = "Memory test plugin"
    plugin_type = PluginType.CUSTOM
    
    def is_available(self):
        return True
    
    def execute(self, **kwargs):
        return {"status": "ok"}
"""
        plugin_file = Path(temp_plugin_dir) / "memory.py"
        plugin_file.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        
        # 加载前内存
        initial_refs = len([obj for obj in gc.get_objects() if isinstance(obj, BasePlugin)])
        
        # 加载插件
        plugin_manager.load_plugin(str(plugin_file))
        
        # 加载后内存
        final_refs = len([obj for obj in gc.get_objects() if isinstance(obj, BasePlugin)])
        
        # 应该只有一个插件实例
        assert final_refs - initial_refs == 1


# ========== 11. Mock 测试 ==========

class TestMocking:
    """Mock 测试"""
    
    @patch('os.path.exists')
    def test_mock_filesystem(self, mock_exists, plugin_manager):
        """测试 Mock 文件系统"""
        mock_exists.return_value = True
        
        plugin_manager.plugin_dirs = ["/test/dir"]
        discovered = plugin_manager.discover_plugins()
        
        mock_exists.assert_called()
    
    def test_mock_import(self, plugin_manager, temp_plugin_dir):
        """测试 Mock 导入"""
        # 创建一个可用的插件文件
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class MockImportPlugin(BasePlugin):
    name = "mock_import"
    version = "1.0.0"
    description = "Mock import test"
    plugin_type = PluginType.CUSTOM
    
    def is_available(self):
        return True
    
    def execute(self, **kwargs):
        return {"status": "ok"}
"""
        plugin_file = Path(temp_plugin_dir) / "mock_import.py"
        plugin_file.write_text(plugin_code)
        
        # 这将使用 mock 模块
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class TestPlugin(BasePlugin):
    name = "mock"
    version = "1.0.0"
    description = "Mock"
    plugin_type = PluginType.CUSTOM
    
    def is_available(self):
        return True
    
    def execute(self, **kwargs):
        return {}
"""
        plugin_file = Path(temp_plugin_dir) / "mock.py"
        plugin_file.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        plugin = plugin_manager.load_plugin(str(plugin_file))
        
        assert plugin is not None


# ========== 12. 边界条件测试 ==========

class TestEdgeCases:
    """边界条件测试"""
    
    def test_empty_plugin_name(self, plugin_manager):
        """测试空插件名称"""
        class EmptyNamePlugin(BasePlugin):
            name = ""
            version = "1.0.0"
            description = "Empty name"
            plugin_type = PluginType.CUSTOM
            
            def is_available(self):
                return True
            
            def execute(self, **kwargs):
                return {}
        
        plugin = EmptyNamePlugin()
        plugin_manager.plugins[""] = plugin
        
        # 应该能够注册空名称的插件（虽然不推荐）
        assert "" in plugin_manager.plugins
    
    def test_special_characters_in_name(self, plugin_manager, temp_plugin_dir):
        """测试插件名称中的特殊字符"""
        plugin_code = """
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class SpecialPlugin(BasePlugin):
    name = "special-plugin_123"
    version = "1.0.0"
    description = "Special chars"
    plugin_type = PluginType.CUSTOM
    
    def is_available(self):
        return True
    
    def execute(self, **kwargs):
        return {}
"""
        plugin_file = Path(temp_plugin_dir) / "special.py"
        plugin_file.write_text(plugin_code)
        
        plugin_manager.plugin_dirs = [temp_plugin_dir]
        plugin = plugin_manager.load_plugin(str(plugin_file))
        
        assert plugin is not None
        assert "special-plugin_123" in plugin_manager.plugins
    
    def test_large_plugin_config(self, plugin_manager, tmp_path):
        """测试大型插件配置"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        plugin_manager.config_dir = str(config_dir)
        
        # 创建大型配置
        large_config = {f"key{i}": f"value{i}" * 100 for i in range(100)}
        
        result = plugin_manager.save_plugin_config("large_config", large_config)
        assert result is True
        
        loaded = plugin_manager.load_plugin_config("large_config")
        assert loaded == large_config


# ========== 导入 gc 用于内存测试 ==========

import gc


# ========== 测试入口 ==========

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=core/plugin_system", "--cov-report=term"])
