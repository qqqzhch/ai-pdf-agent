"""插件基类"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
import logging

from .plugin_type import PluginType


logger = logging.getLogger(__name__)


class BasePlugin(ABC):
    """插件基类 - 所有插件必须继承此类"""
    
    # ========== 插件元数据（必须定义） ==========
    name: str                          # 插件名称（唯一标识）
    version: str                       # 插件版本
    description: str                   # 插件描述
    plugin_type: PluginType           # 插件类型
    author: str = ""                   # 作者
    homepage: str = ""                # 主页
    license: str = "MIT"              # 许可证
    
    # ========== 插件依赖（可选） ==========
    dependencies: List[str] = []      # Python 依赖，如 ["paddleocr>=2.7", "numpy>=1.24"]
    system_dependencies: List[str] = []  # 系统依赖，如 ["tesseract", "poppler"]
    
    # ========== 配置（可选） ==========
    config_schema: Optional[Dict] = None  # 配置模式（JSON Schema）
    default_config: Optional[Dict] = None  # 默认配置
    
    def __init__(self):
        self._config = None
        self._logger = logging.getLogger(f"plugin.{self.name}")
    
    # ========== 生命周期钩子 ==========
    def on_load(self) -> None:
        """插件加载时调用"""
        self._logger.info(f"Plugin {self.name} loaded")
    
    def on_unload(self) -> None:
        """插件卸载时调用"""
        self._logger.info(f"Plugin {self.name} unloaded")
    
    def on_config_update(self, old_config: Dict, new_config: Dict) -> None:
        """配置更新时调用"""
        self._config = new_config
        self._logger.info(f"Plugin {self.name} config updated")
    
    # ========== 核心接口（必须实现） ==========
    @abstractmethod
    def is_available(self) -> bool:
        """检查插件是否可用（依赖是否满足）"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行插件核心功能"""
        pass
    
    # ========== 辅助接口（可选） ==========
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        return True
    
    def validate_output(self, result: Any) -> bool:
        """验证输出结果"""
        return True
    
    def get_help(self) -> str:
        """获取插件帮助信息"""
        return f"{self.name}: {self.description}"
    
    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """检查依赖是否满足"""
        missing = []

        # 包名映射：处理包名与导入模块名不同的情况
        # 注意：metadata 使用 PyPI 包名（如 pillow），import 使用模块名（如 PIL）
        package_name_mapping = {
            'PIL': 'pillow',  # import name -> PyPI package name
        }

        def parse_version(version_str: str):
            """解析版本字符串为元组，用于比较"""
            import re
            # 移除版本前缀（如 v, r）和非数字字符（保留数字和点）
            version_str = str(version_str).lstrip('vrVR')
            parts = re.findall(r'\d+', version_str)
            # 填充不足的部分为0
            while len(parts) < 3:
                parts.append('0')
            return tuple(int(p) for p in parts[:3])

        for dep in self.dependencies:
            # 解析依赖规范（支持版本约束，如 "pymupdf>=1.23.0"）
            dep_name = dep.split('>=')[0].split('<=')[0].split('==')[0].split('!=')[0].split('~=')[0].split('>')[0].split('<')[0].strip()

            # 使用包名映射
            package_name = package_name_mapping.get(dep_name, dep_name)

            try:
                # 首先尝试使用 importlib（Python 3.8+）
                import importlib.metadata as metadata
                try:
                    installed_version = metadata.version(package_name)
                except metadata.PackageNotFoundError:
                    # 如果映射的包名找不到，尝试原始包名
                    try:
                        installed_version = metadata.version(dep_name)
                    except metadata.PackageNotFoundError:
                        missing.append(dep)
                        continue

                # 检查版本约束
                if '>=' in dep:
                    required_version = dep.split('>=')[1].strip()
                    if parse_version(installed_version) < parse_version(required_version):
                        missing.append(dep)
                        continue
                elif '<=' in dep:
                    required = dep.split('<=')[1].strip()
                    if parse_version(installed_version) > parse_version(required):
                        missing.append(dep)
                        continue
                elif '==' in dep:
                    required = dep.split('==')[1].strip()
                    if parse_version(installed_version) != parse_version(required):
                        missing.append(dep)
                        continue
                elif '>' in dep:
                    required = dep.split('>')[1].strip()
                    if parse_version(installed_version) <= parse_version(required):
                        missing.append(dep)
                        continue
                elif '<' in dep:
                    required = dep.split('<')[1].strip()
                    if parse_version(installed_version) >= parse_version(required):
                        missing.append(dep)
                        continue

            except ImportError:
                # 降级到 pkg_resources（Python < 3.8）
                try:
                    import pkg_resources
                    try:
                        pkg_resources.require(dep)
                    except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
                        missing.append(dep)
                except ImportError:
                    # 如果 pkg_resources 也不可用，使用 importlib 检查模块是否存在
                    import importlib
                    try:
                        # 尝试导入映射的包名
                        importlib.import_module(package_name)
                    except ImportError:
                        # 尝试款导入原始包名
                        try:
                            importlib.import_module(dep_name)
                        except ImportError:
                            missing.append(dep)

        return (len(missing) == 0, missing)
    
    def get_metadata(self) -> Dict:
        """获取插件完整元数据"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "plugin_type": self.plugin_type.value,
            "author": self.author,
            "homepage": self.homepage,
            "license": self.license,
            "dependencies": self.dependencies,
            "system_dependencies": self.system_dependencies,
            "config_schema": self.config_schema,
            "default_config": self.default_config
        }
