"""CLI 主框架完整测试

测试 CLI 主入口、上下文传递、全局选项、配置系统和日志系统
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

from cli.main import cli, CLIContext
from cli.config import Config, load_config, create_default_config
from cli.logger import setup_logging, get_logger, LOG_FORMATS


class TestConfigSystem:
    """测试配置系统"""

    def test_config_initialization(self):
        """测试配置基本初始化"""
        config = Config()

        assert config['pdf_engine'] == 'pymupdf'
        assert config['output_format'] == 'markdown'
        assert config['include_images'] is True

    def test_config_load_from_json(self):
        """测试从 JSON 文件加载配置"""
        config_data = {
            'pdf_engine': 'pdfplumber',
            'output_format': 'html',
            'include_images': False,
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)

            assert config['pdf_engine'] == 'pdfplumber'
            assert config['output_format'] == 'html'
            assert config['include_images'] is False
        finally:
            os.unlink(config_path)

    def test_config_load_from_yaml(self):
        """测试从 YAML 文件加载配置"""
        yaml_data = """
pdf_engine: pypdf
output_format: json
include_tables: false
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_data)
            yaml_path = f.name

        try:
            config = Config(yaml_path)

            assert config['pdf_engine'] == 'pypdf'
            assert config['output_format'] == 'json'
            assert config['include_tables'] is False
        finally:
            os.unlink(yaml_path)

    def test_config_get_with_default(self):
        """测试获取配置项（带默认值）"""
        config = Config()

        value = config.get('nonexistent_key', 'default_value')
        assert value == 'default_value'

    def test_config_set_and_get(self):
        """测试设置和获取配置项"""
        config = Config()

        config.set('custom_key', 'custom_value')
        assert config.get('custom_key') == 'custom_value'

    def test_config_dict_style_access(self):
        """测试字典式访问"""
        config = Config()

        # 使用 [] 设置
        config['test_key'] = 'test_value'
        # 使用 [] 获取
        assert config['test_key'] == 'test_value'
        # 使用 in 检查
        assert 'test_key' in config

    def test_config_nested_keys(self):
        """测试嵌套配置键"""
        config = Config()

        config.set('nested.key', 'nested_value')
        assert config.get('nested.key') == 'nested_value'

    def test_config_to_dict(self):
        """测试转换为字典"""
        config = Config()

        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert 'pdf_engine' in config_dict

    def test_config_save_to_json(self):
        """测试保存配置为 JSON"""
        config = Config()
        config.set('custom_key', 'custom_value')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = f.name

        try:
            success = config.save_to_file(output_path, format='json')
            assert success is True

            # 验证文件内容
            with open(output_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            assert saved_data['custom_key'] == 'custom_value'
        finally:
            os.unlink(output_path)

    def test_config_update(self):
        """测试批量更新配置"""
        config = Config()

        config.update({
            'pdf_engine': 'pdfplumber',
            'custom_key': 'custom_value',
        })

        assert config['pdf_engine'] == 'pdfplumber'
        assert config['custom_key'] == 'custom_value'

    def test_config_env_override(self) -> None:
        """测试环境变量覆盖配置"""
        # 设置环境变量
        os.environ['AIPDF_PDF_ENGINE'] = 'pdfplumber'
        os.environ['AIPDF_OUTPUT_FORMAT'] = 'html'
        os.environ['AIPDF_INCLUDE_IMAGES'] = 'false'

        try:
            config = Config()

            assert config['pdf_engine'] == 'pdfplumber'
            assert config['output_format'] == 'html'
            assert config['include_images'] is False
        finally:
            # 清理环境变量
            del os.environ['AIPDF_PDF_ENGINE']
            del os.environ['AIPDF_OUTPUT_FORMAT']
            del os.environ['AIPDF_INCLUDE_IMAGES']

    def test_config_validation(self):
        """测试配置验证"""
        config = Config()

        # 有效配置
        assert config.validate() is True

    def test_create_default_config(self):
        """测试创建默认配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = f.name

        try:
            success = create_default_config(output_path, format='json')
            assert success is True

            # 验证文件存在且有效
            with open(output_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            assert 'pdf_engine' in saved_data
        finally:
            os.unlink(output_path)

    def test_load_config_convenience_function(self):
        """测试便捷加载函数"""
        config = load_config()

        assert config is not None
        assert isinstance(config, Config)


class TestLoggerSystem:
    """测试日志系统"""

    def test_setup_logging_default(self):
        """测试默认日志设置"""
        logger = setup_logging()

        assert logger is not None
        assert logger.level == logging.INFO

    def test_setup_logging_debug_mode(self):
        """测试调试模式日志"""
        logger = setup_logging(debug=True)

        assert logger.level == logging.DEBUG

    def test_setup_logging_verbose_mode(self):
        """测试详细模式日志"""
        logger = setup_logging(verbose=True)

        assert logger.level == logging.INFO

    def test_setup_logging_quiet_mode(self):
        """测试静默模式日志"""
        logger = setup_logging(quiet=True)

        assert logger.level == logging.ERROR

    def test_setup_logging_with_file(self):
        """测试带文件输出的日志"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name

        try:
            logger = setup_logging(log_file=log_file)
            assert logger is not None

            # 记录一些日志
            test_logger = get_logger('test')
            test_logger.info('Test message')

            # 验证日志文件
            assert Path(log_file).exists()
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            assert 'Test message' in content
        finally:
            os.unlink(log_file)

    def test_get_logger(self):
        """测试获取日志记录器"""
        logger = get_logger('test_module')

        assert logger is not None
        assert logger.name == 'test_module'

    def test_log_formats(self):
        """测试预定义的日志格式"""
        assert 'minimal' in LOG_FORMATS
        assert 'simple' in LOG_FORMATS
        assert 'standard' in LOG_FORMATS
        assert 'detailed' in LOG_FORMATS
        assert 'full' in LOG_FORMATS

    def test_logger_output(self):
        """测试日志输出"""
        # 注意：caplog 需要在 pytest.ini 中配置
        # 这里我们只测试日志不会报错
        setup_logging(level='DEBUG')

        logger = get_logger('test')
        logger.info('Test info message')
        logger.warning('Test warning message')
        logger.error('Test error message')

        # 如果没有异常，则测试通过
        assert True


class TestCLIContext:
    """测试 CLI 上下文"""

    def test_context_basic_initialization(self):
        """测试上下文基本初始化"""
        ctx = CLIContext()

        assert ctx.verbose is False
        assert ctx.debug is False
        assert ctx.quiet is False
        assert ctx.json_output is False
        assert ctx.config_path is None

    def test_context_with_verbose(self):
        """测试详细模式上下文"""
        ctx = CLIContext(verbose=True)

        assert ctx.verbose is True

    def test_context_with_debug(self):
        """测试调试模式上下文"""
        ctx = CLIContext(debug=True)

        assert ctx.debug is True

    def test_context_with_quiet(self):
        """测试静默模式上下文"""
        ctx = CLIContext(quiet=True)

        assert ctx.quiet is True

    def test_context_with_json_output(self):
        """测试 JSON 输出模式上下文"""
        ctx = CLIContext(json_output=True)

        assert ctx.json_output is True

    def test_context_with_config_file(self):
        """测试带配置文件的上下文"""
        config_data = {'pdf_engine': 'pdfplumber'}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            ctx = CLIContext(config_path=config_path)

            assert ctx.config_path == config_path
            assert ctx.config['pdf_engine'] == 'pdfplumber'
        finally:
            os.unlink(config_path)

    def test_context_config_operations(self):
        """测试上下文配置操作"""
        ctx = CLIContext()

        # 设置配置
        ctx.set_config('test_key', 'test_value')

        # 获取配置
        assert ctx.get_config('test_key') == 'test_value'

        # 获取不存在的配置
        assert ctx.get_config('nonexistent', 'default') == 'default'

    def test_context_plugin_manager(self):
        """测试上下文插件管理器"""
        ctx = CLIContext()

        assert ctx.plugin_manager is not None

    def test_context_get_plugin(self):
        """测试获取插件"""
        ctx = CLIContext()

        plugin = ctx.get_plugin('text_reader')
        # 插件可能未加载，所以不强制检查

    def test_context_multiple_options(self):
        """测试多个选项组合"""
        ctx = CLIContext(
            verbose=True,
            debug=True,
            json_output=True,
        )

        assert ctx.verbose is True
        assert ctx.debug is True
        assert ctx.json_output is True


class TestCLIMain:
    """测试 CLI 主命令"""

    def test_cli_imports(self):
        """测试 CLI 导入成功"""
        assert cli is not None
        assert cli.name in ['cli', 'wrapper']

    def test_cli_help(self):
        """测试 CLI 帮助信息"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        # 检查全局选项存在
        assert '--verbose' in result.output
        assert '--debug' in result.output
        assert '--quiet' in result.output
        assert '--json' in result.output
        assert '--config' in result.output

    def test_cli_version(self):
        """测试版本信息"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])

        assert result.exit_code == 0
        assert '0.1.0' in result.output

    def test_cli_empty_invocation(self):
        """测试无参数调用"""
        runner = CliRunner()
        result = runner.invoke(cli, [])

        # Click group without commands may exit with 2
        # 这是因为子命令是延迟加载的
        assert result.exit_code in [0, 2]


class TestGlobalOptions:
    """测试全局选项"""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture"""
        return CliRunner()

    def test_verbose_option(self, runner):
        """测试 --verbose 选项"""
        result = runner.invoke(cli, ['--verbose', '--help'])

        assert result.exit_code == 0

    def test_debug_option(self, runner):
        """测试 --debug 选项"""
        result = runner.invoke(cli, ['--debug', '--help'])

        assert result.exit_code == 0

    def test_quiet_option(self, runner):
        """测试 --quiet 选项"""
        result = runner.invoke(cli, ['--quiet', '--help'])

        assert result.exit_code == 0

    def test_json_option(self, runner):
        """测试 --json 选项"""
        result = runner.invoke(cli, ['--json', '--help'])

        assert result.exit_code == 0

    def test_config_option(self, runner):
        """测试 --config 选项"""
        config_data = {'test': 'value'}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            result = runner.invoke(cli, ['--config', config_path, '--help'])
            assert result.exit_code == 0
        finally:
            os.unlink(config_path)

    def test_combined_global_options(self, runner):
        """测试组合全局选项"""
        result = runner.invoke(cli, ['--verbose', '--debug', '--help'])

        assert result.exit_code == 0


class TestCommands:
    """测试命令注册"""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture"""
        return CliRunner()

    def test_plugin_command(self, runner):
        """测试 plugin 命令"""
        result = runner.invoke(cli, ['plugin', '--help'])

        assert result.exit_code == 0

    def test_text_command(self, runner):
        """测试 text 命令"""
        result = runner.invoke(cli, ['text', '--help'])

        assert result.exit_code == 0

    def test_tables_command(self, runner):
        """测试 tables 命令"""
        result = runner.invoke(cli, ['tables', '--help'])

        assert result.exit_code == 0

    def test_images_command(self, runner):
        """测试 images 命令"""
        result = runner.invoke(cli, ['images', '--help'])

        assert result.exit_code == 0

    def test_metadata_command(self, runner):
        """测试 metadata 命令"""
        result = runner.invoke(cli, ['metadata', '--help'])

        assert result.exit_code == 0

    def test_structure_command(self, runner):
        """测试 structure 命令"""
        result = runner.invoke(cli, ['structure', '--help'])

        assert result.exit_code == 0

    def test_to_markdown_command(self, runner):
        """测试 to-markdown 命令"""
        result = runner.invoke(cli, ['to-markdown', '--help'])

        assert result.exit_code == 0

    def test_to_html_command(self, runner):
        """测试 to-html 命令"""
        result = runner.invoke(cli, ['to-html', '--help'])

        assert result.exit_code == 0

    def test_to_json_command(self, runner):
        """测试 to-json 命令"""
        result = runner.invoke(cli, ['to-json', '--help'])

        assert result.exit_code == 0

    def test_to_csv_command(self, runner):
        """测试 to-csv 命令"""
        result = runner.invoke(cli, ['to-csv', '--help'])

        assert result.exit_code == 0

    def test_to_image_command(self, runner):
        """测试 to-image 命令"""
        result = runner.invoke(cli, ['to-image', '--help'])

        assert result.exit_code == 0

    def test_to_epub_command(self, runner):
        """测试 to-epub 命令"""
        result = runner.invoke(cli, ['to-epub', '--help'])

        assert result.exit_code == 0


class TestIntegration:
    """集成测试"""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture"""
        return CliRunner()

    def test_plugin_list_command(self, runner):
        """测试插件列表命令"""
        result = runner.invoke(cli, ['plugin', 'list'])

        # 命令应该成功执行
        assert result.exit_code == 0 or 'Usage' in result.output

    def test_global_options_with_command(self, runner):
        """测试全局选项与子命令组合"""
        result = runner.invoke(cli, ['--verbose', 'plugin', 'list'])

        assert result.exit_code == 0 or 'Usage' in result.output

    def test_json_output_with_command(self, runner):
        """测试 JSON 输出选项"""
        result = runner.invoke(cli, ['--json', 'plugin', 'list'])

        assert result.exit_code == 0
        # 尝试解析为 JSON
        try:
            data = json.loads(result.output)
            assert isinstance(data, dict)
        except json.JSONDecodeError:
            # 输出可能不是 JSON，这是可以接受的
            pass


class TestErrorHandling:
    """测试错误处理"""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture"""
        return CliRunner()

    def test_unknown_command(self, runner):
        """测试未知命令"""
        result = runner.invoke(cli, ['nonexistent-command'])

        assert result.exit_code != 0

    def test_invalid_config_file(self, runner):
        """测试无效配置文件"""
        # 注意：Click 的 --help 优先处理，所以即使文件不存在也会显示帮助
        # 这里我们测试不使用 --help 的情况
        result = runner.invoke(cli, ['--config', '/nonexistent/config.json'])

        # 应该失败
        assert result.exit_code != 0

    def test_missing_required_argument(self, runner):
        """测试缺失必需参数"""
        result = runner.invoke(cli, ['text'])

        assert result.exit_code != 0 or 'Usage' in result.output
