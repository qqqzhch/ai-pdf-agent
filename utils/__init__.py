"""工具模块"""

from .error_handler import AI_PDF_Error, ParamError, FileNotFoundError, PDFFormatError, ProcessError, PermissionError, PluginError, handle_errors

__all__ = [
    "AI_PDF_Error",
    "ParamError",
    "FileNotFoundError",
    "PDFFormatError",
    "ProcessError",
    "PermissionError",
    "PluginError",
    "handle_errors",
]
