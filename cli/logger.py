"""AI PDF Agent CLI - 日志管理模块

提供统一的日志管理功能，支持：
- 彩色日志输出
- 日志级别控制
- 结构化日志
- 多种输出格式
"""

import logging
import sys
from typing import Optional

try:
    from colorama import Fore, Style, init

    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

    # 定义颜色代码作为后备
    class Fore:
        BLACK = ""
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        MAGENTA = ""
        CYAN = ""
        WHITE = ""
        RESET = ""

    class Style:
        BRIGHT = ""
        DIM = ""
        RESET_ALL = ""


# 日志级别颜色映射
LOG_COLORS = {
    logging.DEBUG: Fore.CYAN,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.RED + Style.BRIGHT,
}


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器

    为不同级别的日志添加颜色，提升可读性
    """

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = "%",
        use_colors: bool = True,
    ):
        """初始化格式化器

        Args:
            fmt: 日志格式字符串
            datefmt: 日期格式字符串
            style: 格式风格
            use_colors: 是否使用颜色
        """
        super().__init__(fmt, datefmt, style)
        self.use_colors = use_colors and COLORAMA_AVAILABLE

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录

        Args:
            record: 日志记录

        Returns:
            str: 格式化后的日志字符串
        """
        # 添加颜色
        if self.use_colors:
            level_color = LOG_COLORS.get(record.levelno, Fore.WHITE)
            record.levelname = f"{level_color}{record.levelname}{Style.RESET_ALL}"

        # 格式化消息
        message = super().format(record)

        return message


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器

    输出 JSON 格式的日志，便于日志分析工具处理
    """

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = "%",
    ):
        """初始化格式化器"""
        super().__init__(fmt, datefmt, style)
        self.datefmt = datefmt or "%Y-%m-%d %H:%M:%S"

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为 JSON

        Args:
            record: 日志记录

        Returns:
            str: JSON 格式的日志字符串
        """
        import json

        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    level: str = "INFO",
    verbose: bool = False,
    debug: bool = False,
    quiet: bool = False,
    log_file: Optional[str] = None,
    json_output: bool = False,
    use_colors: bool = True,
) -> logging.Logger:
    """设置日志系统

    Args:
        level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        verbose: 详细模式（INFO 级别）
        debug: 调试模式（DEBUG 级别）
        quiet: 静默模式（ERROR 级别）
        log_file: 日志文件路径（可选）
        json_output: JSON 格式输出
        use_colors: 是否使用彩色输出

    Returns:
        logging.Logger: 根日志记录器
    """
    # 确定日志级别
    if debug:
        log_level = logging.DEBUG
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    elif verbose:
        log_level = logging.INFO
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    elif quiet:
        log_level = logging.ERROR
        format_str = "%(levelname)s: %(message)s"
    else:
        log_level = getattr(logging, level.upper(), logging.INFO)
        format_str = "%(message)s"

    # 初始化 colorama
    if use_colors and COLORAMA_AVAILABLE:
        init(autoreset=True)

    # 获取根日志记录器
    root_logger = logging.getLogger()

    # 清除现有的处理器
    root_logger.handlers.clear()

    # 设置日志级别
    root_logger.setLevel(log_level)

    # 控制台处理器
    if not quiet:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        if json_output:
            console_formatter = StructuredFormatter()
        else:
            console_formatter = ColoredFormatter(
                fmt=format_str,
                datefmt="%Y-%m-%d %H:%M:%S",
                use_colors=use_colors,
            )

        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # 错误处理器（stderr）
    if quiet or log_level >= logging.WARNING:
        error_handler = logging.StreamHandler(sys.stderr)
        error_handler.setLevel(max(log_level, logging.WARNING))

        if json_output:
            error_formatter = StructuredFormatter()
        else:
            error_formatter = ColoredFormatter(
                fmt="%(levelname)s: %(message)s",
                use_colors=use_colors,
            )

        error_handler.setFormatter(error_formatter)
        root_logger.addHandler(error_handler)

    # 文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别

        file_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器
    """
    return logging.getLogger(name)


class LoggerContext:
    """日志上下文管理器

    用于临时修改日志级别或配置
    """

    def __init__(
        self,
        logger: logging.Logger,
        level: Optional[int] = None,
        handler: Optional[logging.Handler] = None,
    ):
        """初始化上下文管理器

        Args:
            logger: 日志记录器
            level: 临时日志级别
            handler: 临时日志处理器
        """
        self.logger = logger
        self.level = level
        self.handler = handler
        self._original_level = None
        self._original_handlers = []

    def __enter__(self):
        """进入上下文"""
        # 保存原始级别
        self._original_level = self.logger.level

        # 保存原始处理器
        self._original_handlers = self.logger.handlers[:]

        # 设置临时级别
        if self.level is not None:
            self.logger.setLevel(self.level)

        # 设置临时处理器
        if self.handler is not None:
            self.logger.handlers.clear()
            self.logger.addHandler(self.handler)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        # 恢复原始级别
        if self._original_level is not None:
            self.logger.setLevel(self._original_level)

        # 恢复原始处理器
        self.logger.handlers.clear()
        self.logger.handlers.extend(self._original_handlers)

        return False


def log_function_call(func):
    """函数调用日志装饰器

    自动记录函数调用和返回值

    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            return arg1 + arg2
    """
    logger = logging.getLogger(func.__module__)

    def wrapper(*args, **kwargs):
        """包装函数"""
        func_name = f"{func.__module__}.{func.__name__}"

        logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func_name} returned successfully")
            return result
        except Exception as e:
            logger.error(f"{func_name} failed with error: {e}", exc_info=True)
            raise

    return wrapper


# 预定义的常用日志格式
LOG_FORMATS = {
    "minimal": "%(message)s",
    "simple": "%(levelname)s: %(message)s",
    "standard": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "detailed": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    "full": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d)d - %(funcName)s() - %(message)s",
}


def get_format(name: str = "standard") -> str:
    """获取预定义的日志格式

    Args:
        name: 格式名称（minimal, simple, standard, detailed, full）

    Returns:
        str: 格式字符串
    """
    return LOG_FORMATS.get(name, LOG_FORMATS["standard"])
