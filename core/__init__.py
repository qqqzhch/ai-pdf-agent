"""Core 模块"""

from .plugin_system import BasePlugin, PluginManager, PluginType
from .plugin_system.base_converter_plugin import BaseConverterPlugin
from .engine import BasePDFEngine, PyMuPDFEngine

# 优化版本
try:
    from .plugin_system.plugin_manager_optimized import OptimizedPluginManager
    from .engine.pymupdf_engine_optimized import BufferedPyMuPDFEngine
    _optimizations_available = True
except ImportError:
    _optimizations_available = False

__all__ = [
    "BasePlugin",
    "PluginManager",
    "PluginType",
    "BaseConverterPlugin",
    "BasePDFEngine",
    "PyMuPDFEngine",
]

# 优化版本（可选导入）
if _optimizations_available:
    __all__.extend([
        "OptimizedPluginManager",
        "BufferedPyMuPDFEngine",
    ])
