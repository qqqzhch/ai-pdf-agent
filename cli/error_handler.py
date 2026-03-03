"""AI PDF Agent CLI - 统一错误处理模块

提供统一的错误处理装饰器和友好的错误提示：
- 错误代码定义
- 错误消息本地化
- 装饰器模式的错误处理
- 友好的错误提示和解决方案
"""

import click
import sys
import logging
import traceback
from typing import Any, Callable, Dict, Optional, Type
from functools import wraps

logger = logging.getLogger(__name__)


# 错误代码定义
class ErrorCode:
    """错误代码常量"""
    SUCCESS = 0
    GENERAL_ERROR = 1
    PARAM_ERROR = 2
    FILE_NOT_FOUND = 3
    FILE_READ_ERROR = 4
    FILE_WRITE_ERROR = 5
    PDF_FORMAT_ERROR = 6
    PDF_PASSWORD_ERROR = 7
    PLUGIN_ERROR = 8
    PLUGIN_NOT_FOUND = 9
    CONFIG_ERROR = 10
    NETWORK_ERROR = 11
    PERMISSION_ERROR = 12
    MEMORY_ERROR = 13
    VALIDATION_ERROR = 14


# 错误消息模板
ERROR_MESSAGES: Dict[int, Dict[str, str]] = {
    ErrorCode.GENERAL_ERROR: {
        'zh_CN': '发生未知错误',
        'en_US': 'An unknown error occurred',
    },
    ErrorCode.PARAM_ERROR: {
        'zh_CN': '参数错误',
        'en_US': 'Invalid parameter',
    },
    ErrorCode.FILE_NOT_FOUND: {
        'zh_CN': '文件不存在',
        'en_US': 'File not found',
    },
    ErrorCode.FILE_READ_ERROR: {
        'zh_CN': '无法读取文件',
        'en_US': 'Failed to read file',
    },
    ErrorCode.FILE_WRITE_ERROR: {
        'zh_CN': '无法写入文件',
        'en_US': 'Failed to write file',
    },
    ErrorCode.PDF_FORMAT_ERROR: {
        'zh_CN': 'PDF 格式错误或文件损坏',
        'en_US': 'PDF format error or corrupted file',
    },
    ErrorCode.PDF_PASSWORD_ERROR: {
        'zh_CN': 'PDF 文件需要密码',
        'en_US': 'PDF file requires password',
    },
    ErrorCode.PLUGIN_ERROR: {
        'zh_CN': '插件错误',
        'en_US': 'Plugin error',
    },
    ErrorCode.PLUGIN_NOT_FOUND: {
        'zh_CN': '插件未找到',
        'en_US': 'Plugin not found',
    },
    ErrorCode.CONFIG_ERROR: {
        'zh_CN': '配置错误',
        'en_US': 'Configuration error',
    },
    ErrorCode.NETWORK_ERROR: {
        'zh_CN': '网络错误',
        'en_US': 'Network error',
    },
    ErrorCode.PERMISSION_ERROR: {
        'zh_CN': '权限不足',
        'en_US': 'Permission denied',
    },
    ErrorCode.MEMORY_ERROR: {
        'zh_CN': '内存不足',
        'en_US': 'Out of memory',
    },
    ErrorCode.VALIDATION_ERROR: {
        'zh_CN': '数据验证失败',
        'en_US': 'Data validation failed',
    },
}


class AI_PDF_Error(Exception):
    """基础错误类

    所有自定义错误都应该继承此类

    Attributes:
        message: 错误消息
        exit_code: 退出代码
        details: 详细信息
        solution: 解决方案建议
    """

    exit_code: int = ErrorCode.GENERAL_ERROR

    def __init__(
        self,
        message: str,
        exit_code: Optional[int] = None,
        details: Optional[str] = None,
        solution: Optional[str] = None,
    ):
        """初始化错误

        Args:
            message: 错误消息
            exit_code: 退出代码（可选，默认使用类定义的 exit_code）
            details: 详细信息（可选）
            solution: 解决方案建议（可选）
        """
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code if exit_code is not None else self.exit_code
        self.details = details
        self.solution = solution

    def __str__(self) -> str:
        """字符串表示"""
        msg = self.message
        if self.details:
            msg += f"\n  Details: {self.details}"
        if self.solution:
            msg += f"\n  💡 Solution: {self.solution}"
        return msg

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于 JSON 输出）

        Returns:
            包含错误信息的字典
        """
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'exit_code': self.exit_code,
            'details': self.details,
            'solution': self.solution,
        }


class ParamError(AI_PDF_Error):
    """参数错误"""
    exit_code = ErrorCode.PARAM_ERROR


class FileNotFoundError(AI_PDF_Error):
    """文件不存在错误"""
    exit_code = ErrorCode.FILE_NOT_FOUND

    def __init__(self, file_path: str):
        """初始化错误

        Args:
            file_path: 文件路径
        """
        super().__init__(
            message=f"File not found: {file_path}",
            solution=f"Please check if the file path is correct: {file_path}"
        )


class FileReadError(AI_PDF_Error):
    """文件读取错误"""
    exit_code = ErrorCode.FILE_READ_ERROR


class FileWriteError(AI_PDF_Error):
    """文件写入错误"""
    exit_code = ErrorCode.FILE_WRITE_ERROR


class PDFFormatError(AI_PDF_Error):
    """PDF 格式错误"""
    exit_code = ErrorCode.PDF_FORMAT_ERROR

    def __init__(self, message: str = "Invalid PDF format or corrupted file"):
        """初始化错误

        Args:
            message: 错误消息
        """
        super().__init__(
            message=message,
            solution="Please ensure the file is a valid PDF document"
        )


class PDFPasswordError(AI_PDF_Error):
    """PDF 密码错误"""
    exit_code = ErrorCode.PDF_PASSWORD_ERROR

    def __init__(self):
        """初始化错误"""
        super().__init__(
            message="PDF file is password-protected",
            solution="Please provide the password using --password option"
        )


class PluginError(AI_PDF_Error):
    """插件错误"""
    exit_code = ErrorCode.PLUGIN_ERROR


class PluginNotFoundError(AI_PDF_Error):
    """插件未找到错误"""
    exit_code = ErrorCode.PLUGIN_NOT_FOUND

    def __init__(self, plugin_name: str):
        """初始化错误

        Args:
            plugin_name: 插件名称
        """
        super().__init__(
            message=f"Plugin not found: {plugin_name}",
            solution=f"Please check if the plugin '{plugin_name}' is installed and available"
        )


class ConfigError(AI_PDF_Error):
    """配置错误"""
    exit_code = ErrorCode.CONFIG_ERROR


class NetworkError(AI_PDF_Error):
    """网络错误"""
    exit_code = ErrorCode.NETWORK_ERROR


class PermissionError(AI_PDF_Error):
    """权限错误"""
    exit_code = ErrorCode.PERMISSION_ERROR

    def __init__(self, resource: str = "resource"):
        """初始化错误

        Args:
            resource: 资源描述
        """
        super().__init__(
            message=f"Permission denied: {resource}",
            solution="Please check file permissions or run with appropriate privileges"
        )


class MemoryError(AI_PDF_Error):
    """内存错误"""
    exit_code = ErrorCode.MEMORY_ERROR

    def __init__(self):
        """初始化错误"""
        super().__init__(
            message="Out of memory",
            solution="Try processing smaller files or increase available memory"
        )


class ValidationError(AI_PDF_Error):
    """验证错误"""
    exit_code = ErrorCode.VALIDATION_ERROR


def get_error_message(code: int, locale: str = 'en_US') -> str:
    """获取错误消息

    Args:
        code: 错误代码
        locale: 语言环境

    Returns:
        错误消息
    """
    if code in ERROR_MESSAGES:
        return ERROR_MESSAGES[code].get(locale, ERROR_MESSAGES[code]['en_US'])
    return ERROR_MESSAGES[ErrorCode.GENERAL_ERROR][locale]


def format_error_message(
    error: Exception,
    verbose: bool = False,
    json_output: bool = False
) -> str:
    """格式化错误消息

    Args:
        error: 异常对象
        verbose: 是否显示详细信息
        json_output: 是否 JSON 格式输出

    Returns:
        格式化后的错误消息
    """
    if json_output:
        import json
        if isinstance(error, AI_PDF_Error):
            error_dict = error.to_dict()
        else:
            error_dict = {
                'error': error.__class__.__name__,
                'message': str(error),
            }

        if verbose:
            error_dict['traceback'] = traceback.format_exc()

        return json.dumps(error_dict, indent=2, ensure_ascii=False)

    # 普通文本格式
    if isinstance(error, AI_PDF_Error):
        return str(error)
    else:
        return f"Error: {error}"


def handle_errors(
    exit_on_error: bool = True,
    show_traceback: bool = False,
):
    """错误处理装饰器

    捕获和处理异常，提供友好的错误提示

    Args:
        exit_on_error: 发生错误时是否退出
        show_traceback: 是否显示完整的错误堆栈

    Usage:
        @handle_errors()
        def my_command():
            ...

        @handle_errors(exit_on_error=False)
        def my_function():
            ...

    Returns:
        装饰器函数
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 获取 Click 上下文
            ctx = None
            try:
                ctx = click.get_current_context()
            except RuntimeError:
                pass

            # 获取 verbose 和 json_output 设置
            verbose = False
            json_output = False
            quiet = False

            if ctx is not None and hasattr(ctx, 'obj') and ctx.obj is not None:
                verbose = getattr(ctx.obj, 'debug', False)
                json_output = getattr(ctx.obj, 'json_output', False)
                quiet = getattr(ctx.obj, 'quiet', False)

            try:
                # 调用原始函数
                return f(*args, **kwargs)

            except click.ClickException:
                # Click 异常直接抛出
                raise

            except KeyboardInterrupt:
                # 键盘中断
                if not quiet:
                    click.echo("\n⚠️  Operation cancelled by user", err=True)
                if exit_on_error:
                    sys.exit(130)
                raise

            except AI_PDF_Error as e:
                # 自定义错误
                logger.error(f"AI_PDF_Error: {e.message}")

                if quiet:
                    raise click.ClickException(e.message)

                error_msg = format_error_message(e, verbose, json_output)

                if json_output:
                    click.echo(error_msg, err=True)
                else:
                    # 使用红色显示错误
                    click.echo(f"\n❌ {error_msg}\n", err=True)

                    # 在详细模式下显示堆栈
                    if show_traceback or verbose:
                        click.echo("\nStack trace:", err=True)
                        click.echo(traceback.format_exc(), err=True)

                if exit_on_error:
                    sys.exit(e.exit_code)
                else:
                    raise SystemExit(e.exit_code)

            except Exception as e:
                # 其他未捕获的异常
                logger.exception(f"Uncaught exception: {e}")

                if quiet:
                    raise click.ClickException(str(e))

                error_msg = format_error_message(e, verbose, json_output)

                if json_output:
                    click.echo(error_msg, err=True)
                else:
                    click.echo(f"\n❌ {error_msg}\n", err=True)

                    # 在详细模式下显示堆栈
                    if show_traceback or verbose:
                        click.echo("\nStack trace:", err=True)
                        click.echo(traceback.format_exc(), err=True)
                    else:
                        click.echo(
                            "\n💡 Run with --debug or --verbose for more details",
                            err=True
                        )

                if exit_on_error:
                    sys.exit(ErrorCode.GENERAL_ERROR)
                else:
                    raise SystemExit(ErrorCode.GENERAL_ERROR)

        return wrapper

    return decorator


def safe_execute(
    func: Callable,
    default: Any = None,
    error_handler: Optional[Callable[[Exception], Any]] = None,
) -> Any:
    """安全执行函数

    捕获异常并返回默认值或调用错误处理器

    Args:
        func: 要执行的函数
        default: 默认返回值
        error_handler: 错误处理器函数

    Returns:
        函数结果或默认值

    Usage:
        result = safe_execute(lambda: risky_operation(), default=None)

        def handle_error(e):
            logger.error(f"Error: {e}")
            return None

        result = safe_execute(risky_operation, error_handler=handle_error)
    """
    try:
        return func()
    except Exception as e:
        logger.error(f"Error in safe_execute: {e}")
        if error_handler:
            return error_handler(e)
        return default


def validate_file_exists(file_path: str) -> str:
    """验证文件是否存在

    Args:
        file_path: 文件路径

    Returns:
        文件路径

    Raises:
        FileNotFoundError: 文件不存在
    """
    import os
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)
    return file_path


def validate_pdf_file(file_path: str) -> str:
    """验证 PDF 文件

    Args:
        file_path: 文件路径

    Returns:
        文件路径

    Raises:
        FileNotFoundError: 文件不存在
        ValidationError: 不是 PDF 文件
    """
    import os
    from pathlib import Path

    file_path = validate_file_exists(file_path)

    # 检查文件扩展名
    path = Path(file_path)
    if path.suffix.lower() not in ['.pdf']:
        raise ValidationError(
            message=f"Not a PDF file: {file_path}",
            solution="Please provide a valid PDF file with .pdf extension"
        )

    # 检查文件大小（防止处理过大文件）
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        raise PDFFormatError("PDF file is empty")

    return file_path
