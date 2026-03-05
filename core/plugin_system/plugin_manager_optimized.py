"""优化的插件管理器 - 支持延迟加载和缓存"""

import hashlib
import importlib.util
import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from .base_plugin import BasePlugin
from .plugin_type import PluginType

logger = logging.getLogger(__name__)


class OptimizedPluginManager:
    """优化的插件管理器 - 单例模式，支持延迟加载和缓存"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, plugin_dirs: List[str] = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(
        self,
        plugin_dirs: List[str] = None,
        enable_cache: bool = True,
        cache_ttl: int = 3600,
    ):
        """
        初始化优化的插件管理器

        Args:
            plugin_dirs: 插件目录列表
            enable_cache: 是否启用插件缓存
            cache_ttl: 缓存过期时间（秒）
        """
        if self._initialized:
            return

        self.plugin_dirs = plugin_dirs or [
            "./plugins",
            "~/.ai-pdf/plugins",
            os.path.join(os.path.dirname(__file__), "..", "builtin_plugins"),
        ]

        # 插件状态管理
        self.plugins: Dict[str, BasePlugin] = {}  # 已加载的插件
        self.plugin_configs: Dict[str, Dict] = {}
        self.hooks: Dict[str, List[Callable]] = {}

        # 延迟加载支持
        self._discovered_plugins: List[str] = []  # 发现但未加载的插件
        self._plugin_metadata: Dict[str, Dict] = {}  # 插件元数据缓存
        self._loaded_plugin_dependencies: Set[str] = set()  # 已加载的依赖

        # 缓存支持
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl
        self.cache_dir = os.path.expanduser("~/.ai-pdf/cache/plugins")
        if self.enable_cache:
            os.makedirs(self.cache_dir, exist_ok=True)

        # 配置目录
        self.config_dir = os.path.expanduser("~/.ai-pdf/config")
        os.makedirs(self.config_dir, exist_ok=True)

        # 性能统计
        self.stats = {
            "discover_time": 0,
            "load_time": {},
            "cache_hits": 0,
            "cache_misses": 0,
        }

        self._initialized = True
        logger.info("Optimized plugin manager initialized")

    # ========== 缓存管理 ==========
    def _get_cache_key(self, plugin_path: str) -> str:
        """生成插件缓存键"""
        abs_path = os.path.abspath(plugin_path)
        mtime = os.path.getmtime(abs_path)
        key_data = f"{abs_path}:{mtime}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """从缓存加载插件元数据"""
        if not self.enable_cache:
            return None

        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        if not os.path.exists(cache_file):
            self.stats["cache_misses"] += 1
            return None

        try:
            # 检查缓存是否过期
            cache_age = time.time() - os.path.getmtime(cache_file)
            if cache_age > self.cache_ttl:
                self.stats["cache_misses"] += 1
                return None

            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.stats["cache_hits"] += 1
                logger.debug(f"Cache hit for {cache_key}")
                return data
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            self.stats["cache_misses"] += 1
            return None

    def _save_to_cache(self, cache_key: str, data: Dict):
        """保存插件元数据到缓存"""
        if not self.enable_cache:
            return

        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved to cache: {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def _clear_cache(self):
        """清空插件缓存"""
        if not self.enable_cache:
            return

        try:
            for cache_file in Path(self.cache_dir).glob("*.json"):
                cache_file.unlink()
            logger.info("Plugin cache cleared")
        except Exception as e:
            logger.warning(f"Failed to clear cache: {e}")

    # ========== 插件发现 ==========
    def discover_plugins(self, force_refresh: bool = False) -> List[str]:
        start_time = time.time()

        if self._discovered_plugins and not force_refresh:
            self.stats["discover_time"] = time.time() - start_time
            return self._discovered_plugins

        discovered = []
        for plugin_dir in self.plugin_dirs:
            plugin_dir = os.path.expanduser(plugin_dir)
            if not os.path.exists(plugin_dir):
                continue

            for py_file in Path(plugin_dir).glob("*.py"):
                if py_file.name.startswith("_"):
                    continue
                discovered.append(str(py_file))

        self._discovered_plugins = discovered
        self.stats["discover_time"] = time.time() - start_time
        logger.debug(
            f"Discovered {len(discovered)} plugins in {self.stats['discover_time']:.3f}s"
        )

        return discovered

    def get_plugin_metadata(self, plugin_path: str) -> Dict:
        """
        获取插件元数据（延迟加载，不实例化插件）

        Args:
            plugin_path: 插件文件路径

        Returns:
            插件元数据字典
        """
        # 检查内存缓存
        cache_key = self._get_cache_key(plugin_path)

        if plugin_path in self._plugin_metadata:
            return self._plugin_metadata[plugin_path]

        # 检查文件缓存
        cached_data = self._load_from_cache(cache_key)
        if cached_data:
            self._plugin_metadata[plugin_path] = cached_data
            return cached_data

        # 从文件读取
        try:
            # 轻量级解析：只读取文件头部获取元数据
            with open(plugin_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 简单提取元数据（从类定义中）
            metadata = {
                "path": plugin_path,
                "name": os.path.basename(plugin_path).replace(".py", ""),
                "version": "unknown",
                "author": "unknown",
                "description": "",
                "plugin_type": "reader",
                "dependencies": [],
            }

            # 提取版本号
            import re

            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if version_match:
                metadata["version"] = version_match.group(1)

            # 提取作者
            author_match = re.search(r'author\s*=\s*["\']([^"\']+)["\']', content)
            if author_match:
                metadata["author"] = author_match.group(1)

            # 提取描述
            doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if doc_match:
                metadata["description"] = doc_match.group(1).strip()

            self._plugin_metadata[plugin_path] = metadata
            self._save_to_cache(cache_key, metadata)

            return metadata

        except Exception as e:
            logger.error(f"Failed to read plugin metadata {plugin_path}: {e}")
            return {
                "path": plugin_path,
                "name": os.path.basename(plugin_path).replace(".py", ""),
                "error": str(e),
            }

    # ========== 插件加载 ==========
    def load_plugin(self, plugin_path: str, lazy: bool = False) -> Optional[BasePlugin]:
        """
        加载单个插件

        Args:
            plugin_path: 插件文件路径
            lazy: 是否延迟加载（只加载元数据）

        Returns:
            插件实例（如果加载成功）
        """
        start_time = time.time()

        # 如果启用延迟加载，只获取元数据
        if lazy:
            metadata = self.get_plugin_metadata(plugin_path)
            return None  # 延迟加载不返回实例

        try:
            # 动态导入插件模块
            spec = importlib.util.spec_from_file_location("plugin_module", plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 查找插件类
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BasePlugin)
                    and attr != BasePlugin
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

            # 记录加载时间
            load_time = time.time() - start_time
            self.stats["load_time"][plugin.name] = load_time

            # 注册插件
            self.plugins[plugin.name] = plugin

            logger.info(
                f"Plugin {plugin.name} v{plugin.version} loaded in {load_time:.3f}s"
            )
            return plugin

        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_path}: {e}", exc_info=True)
            return None

    def load_plugin_by_name(self, name: str) -> Optional[BasePlugin]:
        """
        按名称加载插件

        Args:
            name: 插件名称

        Returns:
            插件实例
        """
        # 检查是否已加载
        if name in self.plugins:
            return self.plugins[name]

        # 在发现的插件中查找
        for plugin_path in self.discover_plugins():
            metadata = self.get_plugin_metadata(plugin_path)
            if metadata.get("name") == name:
                return self.load_plugin(plugin_path)

        logger.warning(f"Plugin {name} not found")
        return None

    def load_all_plugins(self, lazy: bool = False) -> int:
        """
        加载所有插件

        Args:
            lazy: 是否延迟加载

        Returns:
            已加载的插件数量
        """
        discovered = self.discover_plugins()
        loaded_count = 0

        for plugin_path in discovered:
            if self.load_plugin(plugin_path, lazy=lazy):
                loaded_count += 1

        return loaded_count

    def unload_plugin(self, name: str) -> bool:
        """卸载插件"""
        if name not in self.plugins:
            logger.warning(f"Plugin {name} not found")
            return False

        try:
            plugin = self.plugins[name]
            plugin.on.unload()
            del self.plugins[name]

            # 清除元数据缓存
            if name in self._plugin_metadata:
                del self._plugin_metadata[name]

            logger.info(f"Plugin {name} unloaded")
            return True
        except Exception as e:
            logger.error(f"Failed to unload plugin {name}: {e}")
            return False

    # ========== 插件查询 ==========
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """
        获取插件实例（按需加载）

        Args:
            name: 插件名称

        Returns:
            插件实例
        """
        # 如果已加载，直接返回
        if name in self.plugins:
            return self.plugins[name]

        # 否则尝试加载
        return self.load_plugin_by_name(name)

    def list_plugins(
        self, plugin_type: PluginType = None, include_metadata: bool = False
    ) -> List[BasePlugin]:
        """
        列出所有插件

        Args:
            plugin_type: 插件类型过滤
            include_metadata: 是否包含未加载的插件元数据

        Returns:
            插件列表
        """
        plugins = list(self.plugins.values())

        if plugin_type:
            plugins = [p for p in plugins if p.plugin_type == plugin_type]

        return plugins

    def list_plugin_names(
        self, plugin_type: PluginType = None, include_all: bool = False
    ) -> List[str]:
        """
        列出所有插件名称

        Args:
            plugin_type: 插件类型过滤
            include_all: 是否包含未加载的插件

        Returns:
            插件名称列表
        """
        if include_all:
            # 返回所有发现的插件
            names = []
            for plugin_path in self.discover_plugins():
                metadata = self.get_plugin_metadata(plugin_path)
                names.append(metadata.get("name", "unknown"))
            return names
        else:
            # 只返回已加载的插件
            plugins = self.list_plugins(plugin_type)
            return [p.name for p in plugins]

    def get_all_plugin_metadata(self) -> List[Dict]:
        """获取所有插件的元数据（包括未加载的）"""
        metadata_list = []
        for plugin_path in self.discover_plugins():
            metadata = self.get_plugin_metadata(plugin_path)

            # 标记是否已加载
            metadata["loaded"] = metadata["name"] in self.plugins

            metadata_list.append(metadata)

        return metadata_list

    # ========== 插件执行 ==========
    def execute_plugin(self, name: str, **kwargs) -> Any:
        """
        执行插件（自动加载）

        Args:
            name: 插件名称
            **kwargs: 插件参数

        Returns:
            执行结果
        """
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
            raise ValueError(f"Invalid output from plugin {name}")

        return result

    # ========== 插件配置 ==========
    def load_plugin_config(self, name: str) -> Dict:
        """加载插件配置"""
        config_file = os.path.join(self.config_dir, f"{name}.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load plugin config {name}: {e}")
        return {}

    def save_plugin_config(self, name: str, config: Dict) -> bool:
        """保存插件配置"""
        config_file = os.path.join(self.config_dir, f"{name}.json")
        try:
            with open(config_file, "w", encoding="utf-8") as f:
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

    # ========== 性能统计 ==========
    def get_stats(self) -> Dict:
        """获取性能统计"""
        return {
            "discover_time": self.stats["discover_time"],
            "load_time": self.stats["load_time"],
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "loaded_plugins": len(self.plugins),
            "discovered_plugins": len(self._discovered_plugins),
            "cache_enabled": self.enable_cache,
        }

    def reset_stats(self):
        """重置性能统计"""
        self.stats = {
            "discover_time": 0,
            "load_time": {},
            "cache_hits": 0,
            "cache_misses": 0,
        }
