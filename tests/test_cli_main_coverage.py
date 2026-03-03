"""CLI 主框架覆盖率提升测试

测试边界情况和错误路径以提高覆盖率
"""

import os
import sys
import json
import logging
import tempfile
from pathlib import Path
from click.testing import CliRunner
import pytest

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cli.config import Config
from cli.logger import setup_logging, get_logger, LoggerContext, log_function_call


class TestConfigCoverage:
    """配置系统覆盖率测试"""

    def test_config_invalid_json(self):
        """测试无效的 JSON 配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{ invalid json }')
            config_path = f.name

        try:
            config = Config(config_path)
            # 配置加载失败，应该使用默认配置
            assert config['pdf_engine'] == 'pymupdf'
        finally:
            os.unlink(config_path)

    def test_config_empty_file(self):
        """测试空配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('')
            config_path = f.name

        try:
            config = Config(config_path)
            # 空文件应该使用默认配置
            assert config['pdf_engine'] == 'pymupdf'
        finally:
            os.unlink(config_path)

    def test_config_yaml_not_available(self):
        """测试 YAML 不可用时的行为"""
        # 模拟 YAML 不可用
        import cli.config
        original_available = cli.config.YAML_AVAILABLE
        cli.config.YAML_AVAILABLE = False

        try:
            yaml_data = "key: value"
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write(yaml_data)
                yaml_path = f.name

            try:
                config = Config(yaml_path)
                # YAML 不可用，应该使用默认配置
                assert config['pdf_engine'] == 'pymupdf'
            finally:
                os.unlink(yaml_path)
        finally:
            cli.config.YAML_AVAILABLE = original_available

    def test_config_env_boolean_values(self):
        """测试环境变量布尔值解析"""
        os.environ['AIPDF_BOOL_TRUE'] = 'true'
        os.environ['AIPDF_BOOL_FALSE'] = 'false'
        os.environ['AIPDF_BOOL_YES'] = 'yes'
        os.environ['AIPDF_BOOL_NO'] = 'no'
        os.environ['AIPDF_BOOL_ON'] = 'on'
        os.environ['AIPDF_BOOL_OFF'] = 'off'
        os.environ['AIPDF_BOOL_1'] = '1'
        os.environ['AIPDF_BOOL_0'] = '0'

        try:
            config = Config()

            assert config.get('bool_true') is True
            assert config.get('bool_false') is False
            assert config.get('bool_yes') is True
            assert config.get('bool_no') is False
            assert config.get('bool_on') is True
            assert config.get('bool_off') is False
            assert config.get('bool_1') is True
            assert config.get('bool_0') is False
        finally:
            for key in ['AIPDF_BOOL_TRUE', 'AIPDF_BOOL_FALSE', 'AIPDF_BOOL_YES',
                       'AIPDF_BOOL_NO', 'AIPDF_BOOL_ON', 'AIPDF_BOOL_OFF',
                       'AIPDF_BOOL_1', 'AIPDF_BOOL_0']:
                if key in os.environ:
                    del os.environ[key]

    def test_config_env_numeric_values(self):
        """测试环境变量数值解析"""
        os.environ['AIPDF_INT_VALUE'] = '42'
        os.environ['AIPDF_FLOAT_VALUE'] = '3.14'

        try:
            config = Config()

            assert config.get('int_value') == 42
            assert config.get('float_value') == 3.14
        finally:
            for key in ['AIPDF_INT_VALUE', 'AIPDF_FLOAT_VALUE']:
                if key in os.environ:
                    del os.environ[key]

    def test_config_env_double_underscore(self):
        """测试双下划线环境变量命名"""
        os.environ['AIPDF_NESTED__KEY'] = 'value'

        try:
            config = Config()
            # 双下划线应该被转换为单下划线
            assert config.get('nested__key') == 'value' or config.get('nested_key') == 'value'
        finally:
            if 'AIPDF_NESTED__KEY' in os.environ:
                del os.environ['AIPDF_NESTED__KEY']

    def test_config_save_yaml_unavailable(self):
        """测试 YAML 不可用时保存时"""
        import cli.config
        original_available = cli.config.YAML_AVAILABLE
        cli.config.YAML_AVAILABLE = False

        try:
            config = Config()

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                output_path = f.name

            try:
                success = config.save_to_file(output_path, format='yaml')
                assert success is False
            finally:
                if os.path.exists(output_path):
                    os.unlink(output_path)
        finally:
            cli.config.YAML_AVAILABLE = original_available

    def test_config_validation_invalid_engine(self):
        """测试验证无效的 PDF 引擎"""
        config = Config()
        config.set('pdf_engine', 'invalid_engine')

        # 验证应该返回 True（只警告，不失败）
        assert config.validate() is True

    def test_config_validation_invalid_format(self):
        """测试验证无效的输出格式"""
        config = Config()
        config.set('output_format', 'invalid_format')

        # 验证应该返回 True（只警告，不失败）
        assert config.validate() is True

    def test_config_repr(self):
        """测试配置的字符串表示"""
        config = Config()
        repr_str = repr(config)

        assert 'Config' in repr_str
        assert 'keys=' in repr_str

    def test_config_nested_key_set_nonexistent_parent(self):
        """测试设置嵌套键时父级不存在"""
        config = Config()

        # 设置嵌套键（父级不存在）
        config.set('parent.child.grandchild', 'value')

        # 验证可以获取
        assert config.get('parent.child.grandchild') == 'value'

    def test_config_get_nested_key_missing(self):
        """测试获取不存在的嵌套键"""
        config = Config()

        # 获取不存在的嵌套键
        value = config.get('nonexistent.nested.key', 'default')
        assert value == 'default'

    def test_config_to_dict_returns_copy(self):
        """测试 to_dict 返回副本"""
        config = Config()

        config_dict1 = config.to_dict()
        config_dict2 = config.to_dict()

        # 两次调用应该返回不同的对象
        assert config_dict1 is not config_dict2
        # 但内容相同
        assert config_dict1 == config_dict2


class TestLoggerCoverage:
    """日志系统覆盖率测试"""

    def test_logger_with_colorama_unavailable(self):
        """测试 colorama 不可用时的行为"""
        import cli.logger
        original_available = cli.logger.COLORAMA_AVAILABLE
        cli.logger.COLORAMA_AVAILABLE = False

        try:
            # 应该仍然能设置日志
            logger = setup_logging(level='INFO')
            assert logger is not None
        finally:
            cli.logger.COLORAMA_AVAILABLE = original_available

    def test_logger_colored_formatter(self):
        """测试彩色格式化器"""
        from cli.logger import ColoredFormatter

        formatter = ColoredFormatter(fmt='%(message)s', use_colors=True)

        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        assert 'Test message' in formatted

    def test_logger_structured_formatter(self):
        """测试结构化格式化器"""
        from cli.logger import StructuredFormatter

        formatter = StructuredFormatter()

        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        # 验证是 JSON 格式
        data = json.loads(formatted)
        assert data['message'] == 'Test message'
        assert data['level'] == 'INFO'
        assert data['logger'] == 'test'

    def test_logger_structured_formatter_with_exception(self):
        """测试带异常的结构化格式化器"""
        from cli.logger import StructuredFormatter

        formatter = StructuredFormatter()

        try:
            raise ValueError("Test exception")
        except Exception:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name='test',
            level=logging.ERROR,
            pathname='test.py',
            lineno=1,
            msg='Error message',
            args=(),
            exc_info=exc_info,
        )

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert 'exception' in data
        assert 'Test exception' in data['exception']

    def test_logger_structured_formatter_with_extra(self):
        """测试带额外字段的结构化格式化器"""
        from cli.logger import StructuredFormatter

        formatter = StructuredFormatter()

        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None,
        )
        record.extra = {'custom_field': 'custom_value'}

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert 'extra' in data
        assert data['extra']['custom_field'] == 'custom_value'

    def test_logger_level_string(self):
        """测试使用字符串设置日志级别"""
        logger = setup_logging(level='WARNING')

        assert logger.level == logging.WARNING

    def test_logger_context_manager_level(self):
        """测试日志上下文管理器 - 级别"""
        logger = get_logger('test')
        original_level = logger.level

        with LoggerContext(logger, level=logging.DEBUG):
            assert logger.level == logging.DEBUG

        # 恢复原始级别
        assert logger.level == original_level

    def test_logger_context_manager_handler(self):
        """测试日志上下文管理器 - 处理器"""
        logger = get_logger('test')
        original_handlers = logger.handlers[:]

        new_handler = logging.StreamHandler()

        with LoggerContext(logger, handler=new_handler):
            # 应该只有新处理器
            assert new_handler in logger.handlers
            assert len(logger.handlers) == 1

        # 恢复原始处理器
        assert logger.handlers == original_handlers

    def test_log_function_call_decorator(self):
        """测试函数调用装饰器"""
        @log_function_call
        def add(a, b):
            return a + b

        result = add(2, 3)
        assert result == 5

    def test_log_function_call_decorator_exception(self):
        """测试函数调用装饰器 - 异常情况"""
        @log_function_call
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

    def test_get_format(self):
        """测试获取日志格式"""
        from cli.logger import get_format

        minimal_format = get_format('minimal')
        assert '%(message)s' in minimal_format

        unknown_format = get_format('unknown')
        assert '%(asctime)s' in unknown_format  # 应该返回标准格式

    def test_setup_logging_json_output(self):
        """测试 JSON 格式输出"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / 'test.log'

            logger = setup_logging(
                level='DEBUG',
                log_file=str(log_file),
                json_output=True,
            )

            test_logger = get_logger('test_json')
            test_logger.info('JSON message')

            # 读取日志文件
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否包含预期的内容
            assert 'JSON message' in content
            assert 'test_json' in content
            assert 'INFO' in content

    def test_setup_logging_without_color(self):
        """测试不使用颜色"""
        logger = setup_logging(
            level='INFO',
            use_colors=False,
        )

        assert logger is not None
