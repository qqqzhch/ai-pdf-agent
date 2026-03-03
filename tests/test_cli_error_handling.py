"""测试 CLI 错误处理和配置模块

测试内容：
- 错误处理装饰器
- 错误类和错误代码
- 配置加载和验证
- 日志配置
"""

import os
import sys
import json
import logging
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cli.error_handler import (
    ErrorCode,
    AI_PDF_Error,
    ParamError,
    FileNotFoundError,
    FileReadError,
    FileWriteError,
    PDFFormatError,
    PDFPasswordError,
    PluginError,
    PluginNotFoundError,
    ConfigError,
    NetworkError,
    PermissionError,
    MemoryError,
    ValidationError,
    get_error_message,
    format_error_message,
    handle_errors,
    safe_execute,
    validate_file_exists,
    validate_pdf_file,
)

from cli.config import (
    Config,
    ConfigValidationError,
    load_config,
    create_default_config,
    DEFAULT_CONFIG,
    CONFIG_SCHEMA,
)

from cli.logger import (
    setup_logging,
    get_logger,
    get_format,
    LOG_FORMATS,
)


class TestErrorCode:
    """测试错误代码"""

    def test_error_code_values(self):
        """测试错误代码值"""
        assert ErrorCode.SUCCESS == 0
        assert ErrorCode.GENERAL_ERROR == 1
        assert ErrorCode.PARAM_ERROR == 2
        assert ErrorCode.FILE_NOT_FOUND == 3
        assert ErrorCode.FILE_READ_ERROR == 4
        assert ErrorCode.FILE_WRITE_ERROR == 5
        assert ErrorCode.PDF_FORMAT_ERROR == 6
        assert ErrorCode.PDF_PASSWORD_ERROR == 7
        assert ErrorCode.PLUGIN_ERROR == 8
        assert ErrorCode.PLUGIN_NOT_FOUND == 9
        assert ErrorCode.CONFIG_ERROR == 10
        assert ErrorCode.NETWORK_ERROR == 11
        assert ErrorCode.PERMISSION_ERROR == 12
        assert ErrorCode.MEMORY_ERROR == 13
        assert ErrorCode.VALIDATION_ERROR == 14


class TestErrorClasses:
    """测试错误类"""

    def test_base_error(self):
        """测试基础错误类"""
        error = AI_PDF_Error("Test error")
        assert error.message == "Test error"
        assert error.exit_code == ErrorCode.GENERAL_ERROR
        assert "Test error" in str(error)

    def test_base_error_with_exit_code(self):
        """测试带退出代码的基础错误类"""
        error = AI_PDF_Error("Test error", exit_code=5)
        assert error.exit_code == 5

    def test_base_error_with_details(self):
        """测试带详细信息的基础错误类"""
        error = AI_PDF_Error("Test error", details="Additional details")
        assert "Additional details" in str(error)

    def test_base_error_with_solution(self):
        """测试带解决方案的基础错误类"""
        error = AI_PDF_Error("Test error", solution="Try this solution")
        assert "Try this solution" in str(error)

    def test_error_to_dict(self):
        """测试错误转字典"""
        error = AI_PDF_Error("Test error", details="Details", solution="Solution")
        error_dict = error.to_dict()

        assert error_dict['error'] == 'AI_PDF_Error'
        assert error_dict['message'] == 'Test error'
        assert error_dict['details'] == 'Details'
        assert error_dict['solution'] == 'Solution'
        assert 'exit_code' in error_dict

    def test_param_error(self):
        """测试参数错误"""
        error = ParamError("Invalid parameter")
        assert error.exit_code == ErrorCode.PARAM_ERROR

    def test_file_not_found_error(self):
        """测试文件不存在错误"""
        error = FileNotFoundError("/path/to/file.pdf")
        assert error.exit_code == ErrorCode.FILE_NOT_FOUND
        assert "/path/to/file.pdf" in str(error)

    def test_pdf_format_error(self):
        """测试 PDF 格式错误"""
        error = PDFFormatError()
        assert error.exit_code == ErrorCode.PDF_FORMAT_ERROR

    def test_pdf_password_error(self):
        """测试 PDF 密码错误"""
        error = PDFPasswordError()
        assert error.exit_code == ErrorCode.PDF_PASSWORD_ERROR

    def test_plugin_not_found_error(self):
        """测试插件未找到错误"""
        error = PluginNotFoundError("my_plugin")
        assert error.exit_code == ErrorCode.PLUGIN_NOT_FOUND
        assert "my_plugin" in str(error)


class TestGetErrorMessage:
    """测试获取错误消息"""

    def test_get_error_message_en(self):
        """测试获取英文错误消息"""
        msg = get_error_message(ErrorCode.FILE_NOT_FOUND, 'en_US')
        assert 'File not found' in msg

    def test_get_error_message_zh(self):
        """测试获取中文错误消息"""
        msg = get_error_message(ErrorCode.FILE_NOT_FOUND, 'zh_CN')
        assert '文件不存在' in msg

    def test_get_error_message_default(self):
        """测试获取默认错误消息"""
        msg = get_error_message(999, 'en_US')
        assert 'unknown error' in msg.lower()


class TestFormatErrorMessage:
    """测试格式化错误消息"""

    def test_format_ai_pdf_error(self):
        """测试格式化 AI_PDF_Error"""
        error = AI_PDF_Error("Test error")
        msg = format_error_message(error, verbose=False, json_output=False)
        assert "Test error" in msg

    def test_format_ai_pdf_error_json(self):
        """测试 JSON 格式化 AI_PDF_Error"""
        error = AI_PDF_Error("Test error", exit_code=2)
        msg = format_error_message(error, verbose=False, json_output=True)

        data = json.loads(msg)
        assert data['message'] == 'Test error'
        assert data['exit_code'] == 2

    def test_format_generic_exception(self):
        """测试格式化通用异常"""
        error = ValueError("Invalid value")
        msg = format_error_message(error, verbose=False, json_output=False)
        assert "Invalid value" in msg


class TestSafeExecute:
    """测试安全执行"""

    def test_safe_execute_success(self):
        """测试安全执行成功"""
        result = safe_execute(lambda: 42)
        assert result == 42

    def test_safe_execute_failure_with_default(self):
        """测试安全执行失败返回默认值"""
        result = safe_execute(lambda: 1 / 0, default=None)
        assert result is None

    def test_safe_execute_failure_with_handler(self):
        """测试安全执行失败调用处理器"""
        def handler(e):
            return f"Error: {e}"

        result = safe_execute(lambda: 1 / 0, error_handler=handler)
        assert "Error" in result


class TestValidateFile:
    """测试文件验证"""

    def test_validate_file_exists(self):
        """测试验证存在的文件"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            result = validate_file_exists(temp_path)
            assert result == temp_path
        finally:
            os.unlink(temp_path)

    def test_validate_file_not_exists(self):
        """测试验证不存在的文件"""
        with pytest.raises(FileNotFoundError):
            validate_file_exists("/nonexistent/file.txt")

    def test_validate_pdf_file(self):
        """测试验证 PDF 文件"""
        # 创建临时 PDF 文件（写入一些内容）
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False, mode='wb') as f:
            f.write(b'%PDF-1.4\n')
            temp_path = f.name

        try:
            result = validate_pdf_file(temp_path)
            assert result == temp_path
        finally:
            os.unlink(temp_path)

    def test_validate_pdf_file_wrong_extension(self):
        """测试验证非 PDF 文件"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ValidationError):
                validate_pdf_file(temp_path)
        finally:
            os.unlink(temp_path)


class TestConfig:
    """测试配置管理"""

    def test_config_default(self):
        """测试默认配置"""
        config = Config()

        assert config.get('pdf_engine') == 'pymupdf'
        assert config.get('output_format') == 'markdown'
        assert config.get('include_images') is True

    def test_config_dict_access(self):
        """测试字典式访问"""
        config = Config()

        assert config['pdf_engine'] == 'pymupdf'
        assert config.get('pdf_engine') == 'pymupdf'
        assert 'pdf_engine' in config

    def test_config_set(self):
        """测试设置配置"""
        config = Config()
        config.set('pdf_engine', 'pdfplumber')

        assert config.get('pdf_engine') == 'pdfplumber'

    def test_config_dict_set(self):
        """测试字典式设置"""
        config = Config()
        config['pdf_engine'] = 'pdfplumber'

        assert config['pdf_engine'] == 'pdfplumber'

    def test_config_update(self):
        """测试更新配置"""
        config = Config()
        config.update({'pdf_engine': 'pdfplumber', 'output_format': 'json'})

        assert config.get('pdf_engine') == 'pdfplumber'
        assert config.get('output_format') == 'json'

    def test_config_to_dict(self):
        """测试转换为字典"""
        config = Config()
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert 'pdf_engine' in config_dict

    def test_config_load_json(self):
        """测试加载 JSON 配置文件"""
        config_data = {
            'pdf_engine': 'pdfplumber',
            'output_format': 'json',
            'image_dpi': 300,
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            config = Config(temp_path)
            assert config.get('pdf_engine') == 'pdfplumber'
            assert config.get('output_format') == 'json'
            assert config.get('image_dpi') == 300
        finally:
            os.unlink(temp_path)

    def test_config_save_json(self):
        """测试保存 JSON 配置文件"""
        config = Config()
        config.set('pdf_engine', 'pdfplumber')

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            config.save_to_file(temp_path, format='json')

            # 验证保存的文件
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)

            assert saved_data['pdf_engine'] == 'pdfplumber'
        finally:
            os.unlink(temp_path)

    def test_config_env_override(self):
        """测试环境变量覆盖"""
        # 设置环境变量
        os.environ['AIPDF_PDF_ENGINE'] = 'pdfplumber'
        os.environ['AIPDF_IMAGE_DPI'] = '300'
        os.environ['AIPDF_INCLUDE_IMAGES'] = 'false'

        try:
            config = Config()
            assert config.get('pdf_engine') == 'pdfplumber'
            assert config.get('image_dpi') == 300
            assert config.get('include_images') is False
        finally:
            # 清除环境变量
            del os.environ['AIPDF_PDF_ENGINE']
            del os.environ['AIPDF_IMAGE_DPI']
            del os.environ['AIPDF_INCLUDE_IMAGES']

    def test_config_validate_success(self):
        """测试配置验证成功"""
        config = Config()
        assert config.validate() is True

    def test_config_validate_invalid_choice(self):
        """测试配置验证失败 - 无效选择"""
        config = Config()
        config.set('pdf_engine', 'invalid_engine')

        assert config.validate() is False
        errors = config.get_validation_errors()
        assert len(errors) > 0

    def test_config_validate_out_of_range(self):
        """测试配置验证失败 - 超出范围"""
        config = Config()
        config.set('image_dpi', 1000)  # 超过最大值 600

        assert config.validate() is False
        errors = config.get_validation_errors()
        assert len(errors) > 0

    def test_config_validate_raise_error(self):
        """测试配置验证抛出异常"""
        config = Config()
        config.set('pdf_engine', 'invalid_engine')

        with pytest.raises(ConfigValidationError):
            config.validate(raise_on_error=True)


class TestLoadConfig:
    """测试加载配置函数"""

    def test_load_config_default(self):
        """测试加载默认配置"""
        config = load_config()
        assert config.get('pdf_engine') == 'pymupdf'


class TestCreateDefaultConfig:
    """测试创建默认配置文件"""

    def test_create_default_config_json(self):
        """测试创建默认 JSON 配置文件"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            result = create_default_config(temp_path, format='json')
            assert result is True

            # 验证文件内容
            with open(temp_path, 'r') as f:
                data = json.load(f)
            assert 'pdf_engine' in data
        finally:
            os.unlink(temp_path)


class TestLogger:
    """测试日志系统"""

    def test_get_format(self):
        """测试获取日志格式"""
        assert get_format('minimal') == LOG_FORMATS['minimal']
        assert get_format('standard') == LOG_FORMATS['standard']
        assert get_format('unknown') == LOG_FORMATS['standard']

    def test_get_logger(self):
        """测试获取日志记录器"""
        logger = get_logger('test')
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test'

    def test_setup_logging(self):
        """测试设置日志"""
        root_logger = setup_logging(level='INFO')
        assert isinstance(root_logger, logging.Logger)


class TestHandleErrorsDecorator:
    """测试错误处理装饰器"""

    def test_handle_errors_success(self):
        """测试错误处理装饰器 - 成功"""
        @handle_errors(exit_on_error=False)
        def test_func():
            return "success"

        result = test_func()
        assert result == "success"

    def test_handle_errors_with_ai_pdf_error(self):
        """测试错误处理装饰器 - AI_PDF_Error"""
        @handle_errors(exit_on_error=False, show_traceback=False)
        def test_func():
            raise AI_PDF_Error("Test error")

        # 当 exit_on_error=False 时，装饰器会抛出 SystemExit
        with pytest.raises(SystemExit) as exc_info:
            test_func()
        assert exc_info.value.code == ErrorCode.GENERAL_ERROR

    def test_handle_errors_with_generic_error(self):
        """测试错误处理装饰器 - 通用错误"""
        @handle_errors(exit_on_error=False, show_traceback=False)
        def test_func():
            raise ValueError("Invalid value")

        # 当 exit_on_error=False 时，装饰器会抛出 SystemExit
        with pytest.raises(SystemExit) as exc_info:
            test_func()
        assert exc_info.value.code == ErrorCode.GENERAL_ERROR


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
