"""插件管理器"""

import importlib.util
import os
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import logging

from .base_plugin import BasePlugin
from .plugin_type import PluginType


logger = logging.getLogger(__name__)


class PluginManager:
    """插件管理器 - 单例模式"""
    _instance = None
    
    def __new__(cls, plugin_dirs: List[str] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, plugin_dirs: List[str] = None):
        if self._initialized:
            return
        
        self.plugin_dirs = plugin_dirs or [
            "./plugins",
            "~/.ai-pdf/plugins",
            os.path.join(os.path.dirname(__file__), "..", "builtin_plugins")
        ]
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_configs: Dict[str, Dict] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.config_dir = os.path.expanduser("~/.ai-pdf/config")
        os.makedirs(self.config_dir, exist_ok=True)
        self._initialized = True
    
    # ========== 插件发现和加载 ==========
    def discover_plugins(self, force_refresh: bool = False) -> List[str]:
        """发现所有可用插件"""
        if hasattr(self, '_plugin_cache') and not force_refresh:
            return self._plugin_cache
        
        discovered = []
        for plugin_dir in self.plugin_dirs:
            plugin_dir = os.path.expanduser(plugin_dir)
            if not os.path.exists(plugin_dir):
                continue
            
            for py_file in Path(plugin_dir).glob("*.py"):
                if py_file.name.startswith("_"):
                    continue
                discovered.append(str(py_file))
        
        self._plugin_cache = discovered
        return discovered
    
    def load_plugin(self, plugin_path: str) -> Optional[BasePlugin]:
        """加载单个插件"""
        try:
            # 动态导入插件模块
            spec = importlib.util.spec_from_file_location(
                "plugin_module", 
                plugin_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找插件类
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type) and 
                    issubclass(attr, BasePlugin) and 
                    attr != BasePlugin
                ):
                    plugin_class = attr
                    break
            
            if not plugin_class:
                logger.error(f"Plugin class not found in {plugin_path}")
                return None
            
            # 实例化插件
            plugin = plugin_class()
            
            # 检查插件是否可用
            if not plugin.is_available():
                logger.warning(f"Plugin {plugin.name} is not available")
                return None
            
            # 检查依赖
            deps_ok, missing_deps = plugin.check_dependencies()
            if not deps_ok:
                logger.warning(
                    f"Plugin {plugin.name} missing dependencies: {missing_deps}"
                )
                return None
            
            # 调用生命周期钩子
            plugin.on_load()
            
            # 注册插件
            self.plugins[plugin.name] = plugin
            
            logger.info(f"Plugin {plugin.name} v{plugin.version} loaded from {plugin_path}")
            return plugin
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_path}: {e}", exc_info=True)
            return None
    
    def load_all_plugins(self) -> int:
        """加载所有插件"""
        discovered = self.discover_plugins()
        loaded_count = 0
        for plugin_path in discovered:
            if self.load_plugin(plugin_path):
                loaded_count += 1
        return loaded_count
    
    def unload_plugin(self, name: str) -> bool:
        """卸载插件"""
        if name not in self.plugins:
            logger.warning(f"Plugin {name} not found")
            return False
        
        try:
            plugin = self.plugins[name]
            plugin.on_unload()
            del self.plugins[name]
            logger.info(f"Plugin {name} unloaded")
            return True
        except Exception as e:
            logger.error(f"Failed to unload plugin {name}: {e}")
            return False
    
    # ========== 插件查询 ==========
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """获取插件实例"""
        return self.plugins.get(name)
    
    def list_plugins(self, plugin_type: PluginType = None) -> List[BasePlugin]:
        """列出所有插件"""
        plugins = list(self.plugins.values())
        if plugin_type:
            plugins = [p for p in plugins if p.plugin_type == plugin_type]
        return plugins
    
    def list_plugin_names(self, plugin_type: PluginType = None) -> List[str]:
        """列出所有插件名称"""
        plugins = self.list_plugins(plugin_type)
        return [p.name for p in plugins]
    
    # ========== 插件执行 ==========
    def execute_plugin(self, name: str, **kwargs) -> Any:
        """执行插件"""
        plugin = self.get_plugin(name)
        if not plugin:
            raise ValueError(f"Plugin {name} not found")
        
        # 验证输入
        if not plugin.validate_input(**kwargs):
            raise ValueError(f"Invalid input for plugin {name}")
        
        # 执行插件
        result = plugin.execute(**kwargs)
        
        # 验证输出
        if not plugin.validate_output(result):
            return ValueError(f"Invalid output from plugin {name}")
        
        return result
    
    # ========== 插件配置 ==========
    def load_plugin_config(self, name: str) -> Dict:
        """加载插件配置"""
        config_file = os.path.join(self.config_dir, f"{name}.json")
        if os.path.exists(config_file):
            import json
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load plugin config {name}: {e}")
        return {}
    
    def save_plugin_config(self, name: str, config: Dict) -> bool:
        """保存插件配置"""
        config_file = os.path.join(self.config_dir, f"{name}.json")
        try:
            import json
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save plugin config {name}: {e}")
            return False
    
    def get_plugin_config(self, name: str) -> Optional[Dict]:
        """获取插件配置"""
        return self.plugin_configs.get(name)
    
    def set_plugin_config(self, name: str, config: Dict) -> bool:
        """设置插件配置"""
        if name not in self.plugins:
            return False
        
        old_config = self.plugin_configs.get(name, {})
        self.plugin_configs[name] = config
        
        # 调用配置更新钩子
        plugin = self.plugins[name]
        plugin.on_config_update(old_config, config)
        
        return True
    
    # ========== Hook 系统 ==========
    def register_hook(self, event: str, callback: Callable) -> None:
        """注册 Hook"""
        if event not in self.hooks:
            self.hooks[event] = []
        self.hooks[event].append(callback)
    
    def trigger_hook(self, event: str, *args, **kwargs) -> List[Any]:
        """触发 Hook"""
        if event not in self.hooks:
            return []
        
        results = []
        for callback in self.hooks[event]:
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Hook {event} failed: {e}")
        
        return results
    
    # ========== 插件信息 ==========
    def get_plugin_info(self, name: str) -> Optional[Dict]:
        """获取插件信息"""
        plugin = self.get_plugin(name)
        if not plugin:
            return None
        
        info = plugin.get_metadata()
        info["loaded"] = True
        info["config"] = self.plugin_configs.get(name, {})
        
        # 检查依赖
        deps_ok, missing_deps = plugin.check_dependencies()
        info["dependencies_ok"] = deps_ok
        info["missing_dependencies"] = missing_deps
        
        return info
    
    def get_all_plugin_info(self) -> List[Dict]:
        """获取所有插件信息"""
        return [
            self.get_plugin_info(name) 
            for name in self.plugins.keys()
        ]
