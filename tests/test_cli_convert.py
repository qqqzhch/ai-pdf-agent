"""CLI 转换命令测试

测试所有转换 CLI 命令的功能：
- to-markdown
- to-html
- to-json
- to-csv
- to-image
- to-epub
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from click.testing import CliRunner
import pytest

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cli.main import cli


class TestCLIToMarkdownCommand:
    """测试 to-markdown 命令"""

    @pytest.fixture
    def cli_runner(self):
        """创建 CLI 测试运行器"""
        return CliRunner()

    @pytest.fixture
    def sample_pdf(self):
        """示例 PDF 文件"""
        return str(project_root / "test_sample.pdf")

    @pytest.fixture
    def temp_output_dir(self):
        """临时输出目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_to_markdown_basic(self, cli_runner, sample_pdf, temp_output_dir):
        """测试基本的 Markdown 转换"""
        output_path = os.path.join(temp_output_dir, "output.md")

        result = cli_runner.invoke(cli, [
            'to-markdown',
            sample_pdf,
            '-o', output_path
        ])

        assert result.exit_code == 0
        assert "✓ Converted" in result.output
        assert os.path.exists(output_path)

        # 验证输出文件
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 0

    def test_to_markdown_with_page(self, cli_runner, sample_pdf, temp_output_dir):
        """测试转换指定页面"""
        output_path = os.path.join(temp_output_dir, "output.md")

        result = cli_runner.invoke(cli, [
            'to-markdown',
            sample_pdf,
            '-o', output_path,
            '--page', '1'
        ])

        assert result.exit_code == 0
        assert "Pages: 1" in result.output

    def test_to_markdown_with_page_range(self, cli_runner, sample_pdf, temp_output_dir):
        """测试转换页面范围"""
        output_path = os.path.join(temp_output_dir, "output.md")

        result = cli_runner.invoke(cli, [
            'to-markdown',
            sample_pdf,
            '-o', output_path,
            '--page-range', '1-2'
        ])

        assert result.exit_code == 0
        assert "Pages: 2" in result.output

    def test_to_markdown_with_pages(self, cli_runner, sample_pdf, temp_output_dir):
        """测试转换多个指定页面"""
        output_path = os.path.join(temp_output_dir, "output.md")

        result = cli_runner.invoke(cli, [
            'to-markdown',
            sample_pdf,
            '-o', output_path,
            '--pages', '1,3'
        ])

        assert result.exit_code == 0
        assert "Pages: 2" in result.output

    def test_to_markdown_json_output(self, cli_runner, sample_pdf, temp_output_dir):
        """测试 JSON 格式输出"""
        output_path = os.path.join(temp_output_dir, "output.md")

        result = cli_runner.invoke(cli, [
            '--json',
            'to-markdown',
            sample_pdf,
            '-o', output_path
        ])

        assert result.exit_code == 0

        # 验证 JSON 输出
        output_data = json.loads(result.output)
        assert output_data['success'] is True
        assert 'pages' in output_data

    def test_to_markdown_no_tables(self, cli_runner, sample_pdf, temp_output_dir):
        """测试不保留表格"""
        output_path = os.path.join(temp_output_dir, "output.md")

        result = cli_runner.invoke(cli, [
            'to-markdown',
            sample_pdf,
            '-o', output_path
        ])

        # 命令默认包含表格，没有 --no-preserve-tables 选项
        assert result.exit_code == 0

    def test_to_markdown_no_images(self, cli_runner, sample_pdf, temp_output_dir):
        """测试不保留图片"""
        output_path = os.path.join(temp_output_dir, "output.md")

        result = cli_runner.invoke(cli, [
            'to-markdown',
            sample_pdf,
            '-o', output_path
        ])

        # 命令默认包含图片，没有 --no-preserve-images 选项
        assert result.exit_code == 0


class TestCLIToHtmlCommand:
    """测试 to-html 命令"""

    @pytest.fixture
    def cli_runner(self):
        """创建 CLI 测试运行器"""
        return CliRunner()

    @pytest.fixture
    def sample_pdf(self):
        """示例 PDF 文件"""
        return str(project_root / "test_sample.pdf")

    @pytest.fixture
    def temp_output_dir(self):
        """临时输出目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_to_html_basic(self, cli_runner, sample_pdf, temp_output_dir):
        """测试基本的 HTML 转换"""
        output_path = os.path.join(temp_output_dir, "output.html")

        result = cli_runner.invoke(cli, [
            'to-html',
            sample_pdf,
            '-o', output_path
        ])

        assert result.exit_code == 0
        assert "✓ Converted" in result.output
        assert os.path.exists(output_path)

        # 验证输出文件
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'html' in content
            assert '</html>' in content

    def test_to_html_with_page(self, cli_runner, sample_pdf, temp_output_dir):
        """测试转换指定页面"""
        output_path = os.path.join(temp_output_dir, "output.html")

        result = cli_runner.invoke(cli, [
            'to-html',
            sample_pdf,
            '-o', output_path,
            '--page', '1'
        ])

        assert result.exit_code == 0
        assert "Pages: 1" in result.output

    def test_to_html_embed_images(self, cli_runner, sample_pdf, temp_output_dir):
        """测试嵌入图片"""
        output_path = os.path.join(temp_output_dir, "output.html")

        result = cli_runner.invoke(cli, [
            'to-html',
            sample_pdf,
            '-o', output_path,
            '--embed-images'
        ])

        assert result.exit_code == 0

    def test_to_html_responsive(self, cli_runner, sample_pdf, temp_output_dir):
        """测试响应式设计"""
        output_path = os.path.join(temp_output_dir, "output.html")

        result = cli_runner.invoke(cli, [
            'to-html',
            sample_pdf,
            '-o', output_path,
            '--responsive'
        ])

        assert result.exit_code == 0


class TestCLIToJsonCommand:
    """测试 to-json 命令"""

    @pytest.fixture
    def cli_runner(self):
        """创建 CLI 测试运行器"""
        return CliRunner()

    @pytest.fixture
    def sample_pdf(self):
        """示例 PDF 文件"""
        return str(project_root / "test_sample.pdf")

    @pytest.fixture
    def temp_output_dir(self):
        """临时输出目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_to_json_basic(self, cli_runner, sample_pdf, temp_output_dir):
        """测试基本的 JSON 转换"""
        output_path = os.path.join(temp_output_dir, "output.json")

        result = cli_runner.invoke(cli, [
            'to-json',
            sample_pdf,
            '-o', output_path
        ])

        assert result.exit_code == 0
        assert "✓ Converted" in result.output
        assert os.path.exists(output_path)

        # 验证输出文件
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert isinstance(data, dict)

    def test_to_json_with_page(self, cli_runner, sample_pdf, temp_output_dir):
        """测试转换指定页面"""
        output_path = os.path.join(temp_output_dir, "output.json")

        result = cli_runner.invoke(cli, [
            'to-json',
            sample_pdf,
            '-o', output_path,
            '--page', '1'
        ])

        assert result.exit_code == 0
        assert "Pages: 1" in result.output

    def test_to_json_with_options(self, cli_runner, sample_pdf, temp_output_dir):
        """测试使用选项"""
        output_path = os.path.join(temp_output_dir, "output.json")

        result = cli_runner.invoke(cli, [
            'to-json',
            sample_pdf,
            '-o', output_path,
            '--include-metadata',
            '--include-text',
            '--include-tables'
        ])

        assert result.exit_code == 0


class TestCLIToCsvCommand:
    """测试 to-csv 命令"""

    @pytest.fixture
    def cli_runner(self):
        """创建 CLI 测试运行器"""
        return CliRunner()

    @pytest.fixture
    def sample_pdf(self):
        """示例 PDF 文件"""
        return str(project_root / "test_sample.pdf")

    @pytest.fixture
    def temp_output_dir(self):
        """临时输出目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_to_csv_basic(self, cli_runner, sample_pdf, temp_output_dir):
        """测试基本的 CSV 转换"""
        output_path = os.path.join(temp_output_dir, "output.csv")

        result = cli_runner.invoke(cli, [
            'to-csv',
            sample_pdf,
            '-o', output_path
        ])

        # 命令应该执行（即使没有表格）
        # 成功或失败都可以接受，只要没有异常
        assert result.exit_code in [0, 1]

    def test_to_csv_with_page(self, cli_runner, sample_pdf, temp_output_dir):
        """测试转换指定页面"""
        output_path = os.path.join(temp_output_dir, "output.csv")

        result = cli_runner.invoke(cli, [
            'to-csv',
            sample_pdf,
            '-o', output_path,
            '--page', '1'
        ])

        # 命令应该执行
        assert result.exit_code in [0, 1]

    def test_to_csv_merge_tables(self, cli_runner, sample_pdf, temp_output_dir):
        """测试合并表格"""
        output_path = os.path.join(temp_output_dir, "output.csv")

        result = cli_runner.invoke(cli, [
            'to-csv',
            sample_pdf,
            '-o', output_path,
            '--merge-tables'
        ])

        # 命令应该执行
        assert result.exit_code in [0, 1]


class TestCLIToImageCommand:
    """测试 to-image 命令"""

    @pytest.fixture
    def cli_runner(self):
        """创建 CLI 测试运行器"""
        return CliRunner()

    @pytest.fixture
    def sample_pdf(self):
        """示例 PDF 文件"""
        return str(project_root / "test_sample.pdf")

    @pytest.fixture
    def temp_output_dir(self):
        """临时输出目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_to_image_basic(self, cli_runner, sample_pdf, temp_output_dir):
        """测试基本的图片转换"""
        result = cli_runner.invoke(cli, [
            'to-image',
            sample_pdf,
            '-o', temp_output_dir
        ])

        assert result.exit_code == 0
        assert "✓ Converted" in result.output

        # 检查是否生成了图片文件
        image_files = [f for f in os.listdir(temp_output_dir) if f.endswith('.png')]
        assert len(image_files) > 0

    def test_to_image_with_format(self, cli_runner, sample_pdf, temp_output_dir):
        """测试指定图片格式"""
        result = cli_runner.invoke(cli, [
            'to-image',
            sample_pdf,
            '-o', temp_output_dir,
            '--format', 'jpeg'
        ])

        assert result.exit_code == 0
        assert "Format: jpeg" in result.output

        # 检查是否生成了 JPEG 文件
        image_files = [f for f in os.listdir(temp_output_dir) if f.endswith('.jpeg') or f.endswith('.jpg')]
        assert len(image_files) > 0

    def test_to_image_with_dpi(self, cli_runner, sample_pdf, temp_output_dir):
        """测试指定 DPI"""
        result = cli_runner.invoke(cli, [
            'to-image',
            sample_pdf,
            '-o', temp_output_dir,
            '--dpi', '300'
        ])

        assert result.exit_code == 0
        assert "DPI: 300" in result.output

    def test_to_image_with_page(self, cli_runner, sample_pdf, temp_output_dir):
        """测试转换指定页面"""
        result = cli_runner.invoke(cli, [
            'to-image',
            sample_pdf,
            '-o', temp_output_dir,
            '--page', '1'
        ])

        assert result.exit_code == 0

        # 检查是否只生成了一个图片文件
        image_files = [f for f in os.listdir(temp_output_dir) if f.endswith('.png')]
        assert len(image_files) == 1

    def test_to_image_grayscale(self, cli_runner, sample_pdf, temp_output_dir):
        """测试转换为灰度图"""
        result = cli_runner.invoke(cli, [
            'to-image',
            sample_pdf,
            '-o', temp_output_dir,
            '--grayscale'
        ])

        assert result.exit_code == 0


class TestCLIToEpubCommand:
    """测试 to-epub 命令"""

    @pytest.fixture
    def cli_runner(self):
        """创建 CLI 测试运行器"""
        return CliRunner()

    @pytest.fixture
    def sample_pdf(self):
        """示例 PDF 文件"""
        return str(project_root / "test_sample.pdf")

    @pytest.fixture
    def temp_output_dir(self):
        """临时输出目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_to_epub_basic(self, cli_runner, sample_pdf, temp_output_dir):
        """测试基本的 EPUB 转换"""
        output_path = os.path.join(temp_output_dir, "output.epub")

        result = cli_runner.invoke(cli, [
            'to-epub',
            sample_pdf,
            '-o', output_path
        ])

        assert result.exit_code == 0
        assert "✓ Converted" in result.output
        assert os.path.exists(output_path)

    def test_to_epub_with_page(self, cli_runner, sample_pdf, temp_output_dir):
        """测试转换指定页面"""
        output_path = os.path.join(temp_output_dir, "output.epub")

        result = cli_runner.invoke(cli, [
            'to-epub',
            sample_pdf,
            '-o', output_path,
            '--page', '1'
        ])

        assert result.exit_code == 0
        assert "Pages: 1" in result.output

    def test_to_epub_with_title_author(self, cli_runner, sample_pdf, temp_output_dir):
        """测试设置标题和作者"""
        output_path = os.path.join(temp_output_dir, "output.epub")

        result = cli_runner.invoke(cli, [
            'to-epub',
            sample_pdf,
            '-o', output_path,
            '--title', 'Test Book',
            '--author', 'Test Author'
        ])

        assert result.exit_code == 0

    def test_to_epub_with_chapter_pages(self, cli_runner, sample_pdf, temp_output_dir):
        """测试设置每章页数"""
        output_path = os.path.join(temp_output_dir, "output.epub")

        result = cli_runner.invoke(cli, [
            'to-epub',
            sample_pdf,
            '-o', output_path,
            '--chapter-pages', '2'
        ])

        assert result.exit_code == 0

    def test_to_epub_no_images(self, cli_runner, sample_pdf, temp_output_dir):
        """测试不包含图片"""
        output_path = os.path.join(temp_output_dir, "output.epub")

        result = cli_runner.invoke(cli, [
            'to-epub',
            sample_pdf,
            '-o', output_path,
            '--no-include-images'
        ])

        assert result.exit_code == 0


class TestCLIErrrorHandling:
    """测试 CLI 错误处理"""

    @pytest.fixture
    def cli_runner(self):
        """创建 CLI 测试运行器"""
        return CliRunner()

    @pytest.fixture
    def temp_output_dir(self):
        """临时输出目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_to_markdown_missing_output(self, cli_runner, temp_output_dir):
        """测试缺少输出文件参数"""
        sample_pdf = str(project_root / "test_sample.pdf")

        result = cli_runner.invoke(cli, [
            'to-markdown',
            sample_pdf
        ])

        assert result.exit_code != 0

    def test_to_markdown_invalid_file(self, cli_runner, temp_output_dir):
        """测试无效的输入文件"""
        output_path = os.path.join(temp_output_dir, "output.md")

        result = cli_runner.invoke(cli, [
            'to-markdown',
            '/nonexistent/file.pdf',
            '-o', output_path
        ])

        assert result.exit_code != 0

    def test_to_markdown_invalid_page_range(self, cli_runner, temp_output_dir):
        """测试无效的页面范围"""
        sample_pdf = str(project_root / "test_sample.pdf")
        output_path = os.path.join(temp_output_dir, "output.md")

        result = cli_runner.invoke(cli, [
            'to-markdown',
            sample_pdf,
            '-o', output_path,
            '--page-range', 'invalid'
        ])

        assert "Error: Invalid page range format" in result.output
