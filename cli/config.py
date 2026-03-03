"""AI PDF Agent CLI - 配置管理模块

提供统一的配置管理功能，支持：
- YAML/JSON 配置文件加载
- 环境变量覆盖
- 默认配置
- 配置验证
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger(__name__)


# 默认配置
DEFAULT_CONFIG = {
    'pdf_engine': 'pymupdf',
    'output_format': 'markdown',
    'include_images': True,
    'include_tables': True,
    'image_format': 'png',
    'image_dpi': 150,
    'output_encoding': 'utf-8',
    'chunk_size': 1000,
    'overlap': 100,
    'log_level': 'INFO',
    'log_file': None,
    'log_format': 'standard',
}


# 配置验证 schema
CONFIG_SCHEMA = {
    'pdf_engine': {
        'type': str,
        'required': True,
        'choices': ['pymupdf', 'pdfplumber', 'pypdf'],
        'default': 'pymupdf',
    },
    'output_format': {
        'type': str,
        'required': True,
        'choices': ['markdown', 'html', 'json', 'text', 'csv'],
        'default': 'markdown',
    },
    'include_images': {
        'type': bool,
        'required': False,
        'default': True,
    },
    'include_tables': {
        'type': bool,
        'required': False,
        'default': True,
    },
    'image_format': {
        'type': str,
        'required': False,
        'choices': ['png', 'jpeg', 'jpg', 'webp'],
        'default': 'png',
    },
    'image_dpi': {
        'type': int,
        'required': False,
        'min': 72,
        'max': 600,
        'default': 150,
    },
    'output_encoding': {
        'type': str,
        'required': False,
        'default': 'utf-8',
    },
    'chunk_size': {
        'type': int,
        'required': False,
        'min': 100,
        'max': 10000,
        'default': 1000,
    },
    'overlap': {
        'type': int,
        'required': False,
        'min': 0,
        'max': 1000,
        'default': 100,
    },
    'log_level': {
        'type': str,
        'required': False,
        'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        'default': 'INFO',
    },
    'log_file': {
        'type': (str, type(None)),
        'required': False,
        'default': None,
    },
    'log_format': {
        'type': str,
        'required': False,
        'choices': ['minimal', 'simple', 'standard', 'detailed', 'full'],
        'default': 'standard',
    },
}


class ConfigError(Exception):
    """配置错误基类"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ConfigValidationError(ConfigError):
    """配置验证错误"""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Config validation error in '{field}': {message}")


class Config:
    """配置管理类

    支持从多个来源加载和合并配置：
    1. 默认配置
    2. 配置文件（JSON/YAML）
    3. 环境变量

    优先级：环境变量 > 配置文件 > 默认配置
    """

    def __init__(self, config_path: Optional[str] = None):
        """初始化配置

        Args:
            config_path: 配置文件路径（可选）
        """
        self._config: Dict[str, Any] = {}
        self._config_path: Optional[str] = None
        self._validation_errors: List[ConfigValidationError] = []

        # 加载默认配置
        self._load_default_config()

        # 加载配置文件
        if config_path is not None:
            self.load_from_file(config_path)

        # 加载环境变量
        self._load_from_env()

        # 填充默认值
        self._fill_defaults()

    def _load_default_config(self):
        """加载默认配置"""
        self._config.update(DEFAULT_CONFIG)
        logger.debug("Loaded default configuration")

    def load_from_file(self, config_path: Union[str, Path]) -> bool:
        """从文件加载配置

        Args:
            config_path: 配置文件路径（JSON 或 YAML）

        Returns:
            bool: 是否成功加载
        """
        config_path = Path(config_path)

        if not config_path.exists():
            logger.error(f"Config file not found: {config_path}")
            raise FileNotFoundError(f"Config file not found: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix in ['.yaml', '.yml']:
                    if not YAML_AVAILABLE:
                        logger.warning("PyYAML not installed, cannot load YAML config")
                        raise ImportError("PyYAML is required to load YAML config files")
                    config_data = yaml.safe_load(f)
                else:
                    # 默认尝试 JSON
                    config_data = json.load(f)

            if config_data and isinstance(config_data, dict):
                self._config.update(config_data)
                self._config_path = str(config_path)
                logger.info(f"Loaded config from: {config_path}")
                return True
            else:
                logger.error(f"Invalid config format in: {config_path}")
                raise ValueError("Invalid config format: must be a dictionary")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file {config_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading config file {config_path}: {e}")
            raise

    def _load_from_env(self):
        """从环境变量加载配置

        环境变量命名规则：AIPDF_<CONFIG_KEY>
        例如：AIPDF_PDF_ENGINE, AIPDF_OUTPUT_FORMAT
        """
        env_prefix = 'AIPDF_'

        for key in os.environ:
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()

                # 转换为 Python 命名风格
                config_key = config_key.replace('__', '_')

                # 尝试解析值
                value = self._parse_env_value(os.environ[key])

                self._config[config_key] = value
                logger.debug(f"Loaded config from env: {config_key}={value}")

    def _parse_env_value(self, value: str) -> Any:
        """解析环境变量值

        Args:
            value: 环境变量字符串值

        Returns:
            解析后的值（bool, int, float, str）
        """
        # 布尔值
        if value.lower() in ['true', 'yes', '1', 'on']:
            return True
        elif value.lower() in ['false', 'no', '0', 'off']:
            return False

        # 整数
        try:
            return int(value)
        except ValueError:
            pass

        # 浮点数
        try:
            return float(value)
        except ValueError:
            pass

        # 字符串
        return value

    def _fill_defaults(self):
        """填充默认值"""
        for field_name, schema in CONFIG_SCHEMA.items():
            if field_name not in self._config:
                if 'default' in schema:
                    self._config[field_name] = schema['default']

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项

        Args:
            key: 配置键（支持嵌套，如 'output.format'）
            default: 默认值

        Returns:
            配置值
        """
        # 支持嵌套键
        if '.' in key:
            keys = key.split('.')
            value = self._config

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default

            return value
        else:
            return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置项

        Args:
            key: 配置键（支持嵌套，如 'output.format'）
            value: 配置值
        """
        if '.' in key:
            keys = key.split('.')
            config = self._config

            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]

            config[keys[-1]] = value
        else:
            self._config[key] = value

    def update(self, config: Dict[str, Any]):
        """更新多个配置项

        Args:
            config: 配置字典
        """
        self._config.update(config)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典

        Returns:
            配置字典
        """
        return self._config.copy()

    def save_to_file(self, output_path: Union[str, Path], format: str = 'json') -> bool:
        """保存配置到文件

        Args:
            output_path: 输出文件路径
            format: 文件格式（json 或 yaml）

        Returns:
            bool: 是否成功保存
        """
        output_path = Path(output_path)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if format == 'yaml':
                    if not YAML_AVAILABLE:
                        logger.error("PyYAML not installed, cannot save YAML config")
                        raise ImportError("PyYAML is required to save YAML config files")
                    yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(self._config, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved config to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving config to {output_path}: {e}")
            raise

    def validate(self, raise_on_error: bool = False) -> bool:
        """验证配置

        Args:
            raise_on_error: 遇到错误时是否抛出异常

        Returns:
            bool: 是否验证通过

        Raises:
            ConfigValidationError: 配置验证失败（当 raise_on_error=True 时）
        """
        self._validation_errors.clear()
        all_valid = True

        for field_name, schema in CONFIG_SCHEMA.items():
            # 检查必需字段
            if schema.get('required', False) and field_name not in self._config:
                error = ConfigValidationError(field_name, "Required field is missing")
                self._validation_errors.append(error)
                all_valid = False
                continue

            # 如果字段不存在且非必需，跳过
            if field_name not in self._config:
                continue

            value = self._config[field_name]

            # 类型检查
            field_type = schema.get('type')
            if field_type:
                if isinstance(field_type, tuple):
                    # 支持多种类型
                    if not isinstance(value, field_type):
                        error = ConfigValidationError(
                            field_name,
                            f"Expected type {field_type}, got {type(value).__name__}"
                        )
                        self._validation_errors.append(error)
                        all_valid = False
                elif not isinstance(value, field_type):
                    error = ConfigValidationError(
                        field_name,
                        f"Expected type {field_type.__name__}, got {type(value).__name__}"
                    )
                    self._validation_errors.append(error)
                    all_valid = False

            # 选择值检查
            if 'choices' in schema and value not in schema['choices']:
                error = ConfigValidationError(
                    field_name,
                    f"Invalid choice '{value}'. Valid options: {schema['choices']}"
                )
                self._validation_errors.append(error)
                all_valid = False

            # 数值范围检查
            if isinstance(value, (int, float)):
                if 'min' in schema and value < schema['min']:
                    error = ConfigValidationError(
                        field_name,
                        f"Value {value} is less than minimum {schema['min']}"
                    )
                    self._validation_errors.append(error)
                    all_valid = False

                if 'max' in schema and value > schema['max']:
                    error = ConfigValidationError(
                        field_name,
                        f"Value {value} is greater than maximum {schema['max']}"
                    )
                    self._validation_errors.append(error)
                    all_valid = False

        # 记录验证错误
        if self._validation_errors:
            for error in self._validation_errors:
                logger.warning(str(error))
            if raise_on_error:
                raise self._validation_errors[0]

        return all_valid

    def get_validation_errors(self) -> List[ConfigValidationError]:
        """获取验证错误列表

        Returns:
            验证错误列表
        """
        return self._validation_errors.copy()

    def __repr__(self) -> str:
        """字符串表示"""
        return f"Config(path={self._config_path}, keys={len(self._config)})"

    def __getitem__(self, key: str) -> Any:
        """支持字典式访问"""
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        """支持字典式设置"""
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        """支持 in 操作符"""
        return key in self._config


def load_config(config_path: Optional[str] = None, validate: bool = True) -> Config:
    """加载配置的便捷函数

    Args:
        config_path: 配置文件路径（可选）
        validate: 是否验证配置

    Returns:
        Config: 配置对象
    """
    config = Config(config_path)

    if validate:
        config.validate(raise_on_error=False)

    return config


def create_default_config(output_path: Union[str, Path], format: str = 'json') -> bool:
    """创建默认配置文件

    Args:
        output_path: 输出文件路径
        format: 文件格式（json 或 yaml）

    Returns:
        bool: 是否成功创建
    """
    config = Config()
    return config.save_to_file(output_path, format)
