"""CLI 命令测试 - 测试 5 个 PDF 读取命令

测试命令:
- text: 读取 PDF 文本
- tables: 读取 PDF 表格
- images: 读取 PDF 图片
- metadata: 读取 PDF 元数据
- structure: 读取 PDF 结构
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from click.testing import CliRunner
import pytest
import fitz  # PyMuPDF

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cli.main import cli


# ========== Fixtures ==========

@pytest.fixture
def cli_runner():
    """CLI runner fixture"""
    runner = CliRunner()
    return runner


@pytest.fixture
def sample_pdf():
    """创建测试 PDF 文件（包含文本）"""
    doc = fitz.open()

    # 添加第一页
    page = doc.new_page()
    page.insert_text(fitz.Point(50, 50), "Introduction", fontsize=16)
    page.insert_text(fitz.Point(50, 80), "This is the first page of the test PDF.", fontsize=12)
    page.insert_text(fitz.Point(50, 110), "It contains sample text content.", fontsize=12)

    # 添加第二页
    page = doc.new_page()
    page.insert_text(fitz.Point(50, 50), "Chapter 1", fontsize=14)
    page.insert_text(fitz.Point(50, 80), "This is the second page.", fontsize=12)
    page.insert_text(fitz.Point(50, 110), "More sample text here.", fontsize=12)

    # 添加第三页
    page = doc.new_page()
    page.insert_text(fitz.Point(50, 50), "Conclusion", fontsize=16)
    page.insert_text(fitz.Point(50, 80), "This is the third and final page.", fontsize=12)

    # 保存到临时文件
    temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    doc.save(temp_file.name)
    doc.close()

    yield temp_file.name

    # 清理
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)


@pytest.fixture
def multi_page_pdf():
    """创建多页 PDF（用于页码范围测试）"""
    doc = fitz.open()

    # 添加 10 页
    for i in range(1, 11):
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), f"Page {i}", fontsize=14)
        page.insert_text(fitz.Point(50, 80), f"This is page {i} of the document.", fontsize=12)

    # 保存到临时文件
    temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    doc.save(temp_file.name)
    doc.close()

    yield temp_file.name

    # 清理
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)


# ========== Text Command Tests ==========

class TestTextCommand:
    """测试 text 命令"""

    def test_text_extract_all_pages(self, cli_runner, sample_pdf):
        """测试提取所有页面的文本"""
        result = cli_runner.invoke(cli, ['text', sample_pdf])

        assert result.exit_code == 0
        assert "Introduction" in result.output
        assert "Chapter 1" in result.output
        assert "Conclusion" in result.output

    def test_text_single_page(self, cli_runner, sample_pdf):
        """测试提取单页文本"""
        result = cli_runner.invoke(cli, ['text', sample_pdf, '-p', '2'])

        assert result.exit_code == 0
        assert "Chapter 1" in result.output
        assert "Introduction" not in result.output
        assert "Conclusion" not in result.output

    def test_text_page_range(self, cli_runner, sample_pdf):
        """测试提取页面范围"""
        result = cli_runner.invoke(cli, ['text', sample_pdf, '-p', '1-2'])

        assert result.exit_code == 0
        assert "Introduction" in result.output
        assert "Chapter 1" in result.output
        assert "Conclusion" not in result.output

    def test_text_multiple_pages(self, cli_runner, multi_page_pdf):
        """测试提取指定多页"""
        result = cli_runner.invoke(cli, ['text', multi_page_pdf, '-p', '1,3,5'])

        assert result.exit_code == 0
        assert "Page 1" in result.output
        assert "Page 3" in result.output
        assert "Page 5" in result.output
        assert "Page 2" not in result.output

    def test_text_mixed_page_range(self, cli_runner, multi_page_pdf):
        """测试混合页码范围 (1-3,5,7-9)"""
        result = cli_runner.invoke(cli, ['text', multi_page_pdf, '-p', '1-3,5,7-9'])

        assert result.exit_code == 0
        assert "Page 1" in result.output
        assert "Page 2" in result.output
        assert "Page 3" in result.output
        assert "Page 5" in result.output
        assert "Page 7" in result.output
        assert "Page 9" in result.output
        assert "Page 4" not in result.output
        assert "Page 6" not in result.output

    def test_text_json_format(self, cli_runner, sample_pdf):
        """测试 JSON 格式输出"""
        result = cli_runner.invoke(cli, ['text', sample_pdf, '--format', 'json'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert "content" in data
        assert "pages_extracted" in data
        assert "page_count" in data

    def test_text_json_with_structured(self, cli_runner, sample_pdf):
        """测试 JSON 格式 + structured 选项"""
        result = cli_runner.invoke(cli, ['text', sample_pdf, '--format', 'json', '--structured'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert "metadata" in data

    def test_text_save_to_file(self, cli_runner, sample_pdf, tmp_path):
        """测试保存到文件"""
        output_file = tmp_path / "output.txt"
        result = cli_runner.invoke(cli, ['text', sample_pdf, '-o', str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        assert "extracted to" in result.output.lower()

    def test_text_invalid_page_format(self, cli_runner, sample_pdf):
        """测试无效页码格式"""
        result = cli_runner.invoke(cli, ['text', sample_pdf, '-p', 'invalid'])

        # 命令应该失败
        assert result.exit_code != 0

    def test_text_invalid_page_number(self, cli_runner, sample_pdf):
        """测试无效页码（超出范围）"""
        result = cli_runner.invoke(cli, ['text', sample_pdf, '-p', '100'])

        # 命令应该失败
        assert result.exit_code != 0

    def test_text_help(self, cli_runner):
        """测试命令帮助"""
        result = cli_runner.invoke(cli, ['text', '--help'])

        assert result.exit_code == 0
        assert 'text' in result.output.lower()
        assert 'extract' in result.output.lower()


# ========== Tables Command Tests ==========

class TestTablesCommand:
    """测试 tables 命令"""

    def test_tables_extract(self, cli_runner, sample_pdf):
        """测试提取表格（可能没有表格）"""
        result = cli_runner.invoke(cli, ['tables', sample_pdf])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert "tables" in data
        assert "total_tables" in data

    def test_tables_json_format(self, cli_runner, sample_pdf):
        """测试 JSON 格式输出"""
        result = cli_runner.invoke(cli, ['tables', sample_pdf, '--format', 'json'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data["tables"], list)

    def test_tables_csv_format(self, cli_runner, sample_pdf):
        """测试 CSV 格式输出"""
        result = cli_runner.invoke(cli, ['tables', sample_pdf, '--format', 'csv'])

        assert result.exit_code == 0
        # CSV 格式输出应该是纯文本
        assert isinstance(result.output, str)

    def test_tables_list_format(self, cli_runner, sample_pdf):
        """测试 list 格式输出"""
        result = cli_runner.invoke(cli, ['tables', sample_pdf, '--format', 'list'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tables" in data

    def test_tables_with_page_range(self, cli_runner, sample_pdf):
        """测试指定页面范围"""
        result = cli_runner.invoke(cli, ['tables', sample_pdf, '-p', '1-2'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True

    def test_tables_save_to_file(self, cli_runner, sample_pdf, tmp_path):
        """测试保存到文件"""
        output_file = tmp_path / "tables.json"
        result = cli_runner.invoke(cli, ['tables', sample_pdf, '-o', str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()

    def test_tables_csv_output(self, cli_runner, sample_pdf, tmp_path):
        """测试 CSV 输出文件"""
        output_file = tmp_path / "tables.json"
        csv_file = tmp_path / "tables.csv"

        result = cli_runner.invoke(cli, ['tables', sample_pdf, '-o', str(output_file), '--csv-output', str(csv_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        # CSV 文件只有在有表格时才会创建

    def test_tables_help(self, cli_runner):
        """测试命令帮助"""
        result = cli_runner.invoke(cli, ['tables', '--help'])

        assert result.exit_code == 0
        assert 'tables' in result.output.lower()
        assert 'extract' in result.output.lower()


# ========== Images Command Tests ==========

class TestImagesCommand:
    """测试 images 命令"""

    def test_images_extract(self, cli_runner, sample_pdf):
        """测试提取图片（可能没有图片）"""
        result = cli_runner.invoke(cli, ['images', sample_pdf])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert "images" in data
        assert "count" in data

    def test_images_metadata_only(self, cli_runner, sample_pdf):
        """测试仅提取元数据"""
        result = cli_runner.invoke(cli, ['images', sample_pdf, '--metadata-only'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True

    def test_images_with_page_range(self, cli_runner, sample_pdf):
        """测试指定页面范围"""
        result = cli_runner.invoke(cli, ['images', sample_pdf, '-p', '1-2'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert len(data["pages_extracted"]) == 2

    def test_images_format_jpeg(self, cli_runner, sample_pdf):
        """测试 JPEG 格式"""
        result = cli_runner.invoke(cli, ['images', sample_pdf, '--format', 'jpeg'])

        assert result.exit_code == 0

    def test_images_format_png(self, cli_runner, sample_pdf):
        """测试 PNG 格式"""
        result = cli_runner.invoke(cli, ['images', sample_pdf, '--format', 'png'])

        assert result.exit_code == 0

    def test_images_with_dpi(self, cli_runner, sample_pdf):
        """测试指定 DPI"""
        result = cli_runner.invoke(cli, ['images', sample_pdf, '--dpi', '300'])

        assert result.exit_code == 0

    def test_images_save_metadata(self, cli_runner, sample_pdf, tmp_path):
        """测试保存元数据到文件"""
        output_file = tmp_path / "images.json"
        result = cli_runner.invoke(cli, ['images', sample_pdf, '-o', str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert "images" in data

    def test_images_extract_to_directory(self, cli_runner, sample_pdf, tmp_path):
        """测试提取图片到目录"""
        extract_dir = tmp_path / "extracted_images"
        result = cli_runner.invoke(cli, ['images', sample_pdf, '--extract-dir', str(extract_dir)])

        assert result.exit_code == 0
        # 如果没有图片，目录可能不存在或为空

    def test_images_help(self, cli_runner):
        """测试命令帮助"""
        result = cli_runner.invoke(cli, ['images', '--help'])

        assert result.exit_code == 0
        assert 'images' in result.output.lower()
        assert 'extract' in result.output.lower()


# ========== Metadata Command Tests ==========

class TestMetadataCommand:
    """测试 metadata 命令"""

    def test_metadata_basic(self, cli_runner, sample_pdf):
        """测试基本元数据提取"""
        result = cli_runner.invoke(cli, ['metadata', sample_pdf])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert "basic_metadata" in data

    def test_metadata_full(self, cli_runner, sample_pdf):
        """测试完整元数据（包含统计和属性）"""
        result = cli_runner.invoke(cli, ['metadata', sample_pdf, '--full'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert "document_stats" in data
        assert "pdf_properties" in data
        assert "metadata" in data

    def test_metadata_stats_only(self, cli_runner, sample_pdf):
        """测试仅包含统计信息"""
        result = cli_runner.invoke(cli, ['metadata', sample_pdf, '--stats'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert "document_stats" in data

    def test_metadata_properties_only(self, cli_runner, sample_pdf):
        """测试仅包含 PDF 特性"""
        result = cli_runner.invoke(cli, ['metadata', sample_pdf, '--properties'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert "pdf_properties" in data

    def test_metadata_raw(self, cli_runner, sample_pdf):
        """测试原始元数据（不规范化）"""
        result = cli_runner.invoke(cli, ['metadata', sample_pdf, '--raw'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True

    def test_metadata_save_to_file(self, cli_runner, sample_pdf, tmp_path):
        """测试保存到文件"""
        output_file = tmp_path / "metadata.json"
        result = cli_runner.invoke(cli, ['metadata', sample_pdf, '-o', str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert "basic_metadata" in data

    def test_metadata_displays_summary(self, cli_runner, sample_pdf):
        """测试显示摘要信息"""
        result = cli_runner.invoke(cli, ['metadata', sample_pdf])

        assert result.exit_code == 0
        # 应该包含摘要信息（如果不保存到文件）

    def test_metadata_help(self, cli_runner):
        """测试命令帮助"""
        result = cli_runner.invoke(cli, ['metadata', '--help'])

        assert result.exit_code == 0
        assert 'metadata' in result.output.lower()
        assert 'read' in result.output.lower()


# ========== Structure Command Tests ==========

class TestStructureCommand:
    """测试 structure 命令"""

    def test_structure_basic(self, cli_runner, sample_pdf):
        """测试基本结构提取"""
        result = cli_runner.invoke(cli, ['structure', sample_pdf])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert "page_structure" in data or "blocks" in data or "logical_structure" in data

    def test_structure_outline_only(self, cli_runner, sample_pdf):
        """测试仅提取大纲"""
        result = cli_runner.invoke(cli, ['structure', sample_pdf, '--outline-only'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert "outline" in data

    def test_structure_blocks_only(self, cli_runner, sample_pdf):
        """测试仅提取块"""
        result = cli_runner.invoke(cli, ['structure', sample_pdf, '--blocks-only'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert "blocks" in data

    def test_structure_logical_only(self, cli_runner, sample_pdf):
        """测试仅提取逻辑结构"""
        result = cli_runner.invoke(cli, ['structure', sample_pdf, '--logical-only'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert "logical_structure" in data

    def test_structure_tree(self, cli_runner, sample_pdf):
        """测试树形结构输出"""
        result = cli_runner.invoke(cli, ['structure', sample_pdf, '--tree'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True

    def test_structure_with_page_range(self, cli_runner, sample_pdf):
        """测试指定页面范围"""
        result = cli_runner.invoke(cli, ['structure', sample_pdf, '-p', '1-2'])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert len(data["pages_analyzed"]) == 2

    def test_structure_save_to_file(self, cli_runner, sample_pdf, tmp_path):
        """测试保存到文件"""
        output_file = tmp_path / "structure.json"
        result = cli_runner.invoke(cli, ['structure', sample_pdf, '-o', str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data["success"] is True

    def test_structure_shows_summary(self, cli_runner, sample_pdf):
        """测试显示摘要信息"""
        result = cli_runner.invoke(cli, ['structure', sample_pdf])

        assert result.exit_code == 0
        # 应该显示分析页面数等信息

    def test_structure_help(self, cli_runner):
        """测试命令帮助"""
        result = cli_runner.invoke(cli, ['structure', '--help'])

        assert result.exit_code == 0
        assert 'structure' in result.output.lower()
        assert 'extract' in result.output.lower()


# ========== Page Range Parser Tests ==========

class TestPageRangeParser:
    """测试页码范围解析器"""

    def test_single_page(self):
        """测试单页格式"""
        from cli.commands.text import parse_page_range

        result = parse_page_range("1")
        assert result == {"page": 1}

    def test_page_range(self):
        """测试范围格式"""
        from cli.commands.text import parse_page_range

        result = parse_page_range("1-5")
        assert result == {"page_range": (1, 5)}

    def test_multiple_pages(self):
        """测试多页格式"""
        from cli.commands.text import parse_page_range

        result = parse_page_range("1,3,5")
        assert result == {"pages": [1, 3, 5]}

    def test_mixed_range(self):
        """测试混合格式"""
        from cli.commands.text import parse_page_range

        result = parse_page_range("1-3,5,7-9")
        expected_pages = [1, 2, 3, 5, 7, 8, 9]
        assert result == {"pages": expected_pages}

    def test_invalid_format(self):
        """测试无效格式"""
        from cli.commands.text import parse_page_range

        result = parse_page_range("invalid")
        assert result is None

    def test_zero_page(self):
        """测试页码为 0（无效）"""
        from cli.commands.text import parse_page_range

        result = parse_page_range("0")
        assert result is None

    def test_negative_page(self):
        """测试负页码（无效）"""
        from cli.commands.text import parse_page_range

        result = parse_page_range("-1")
        assert result is None


# ========== Integration Tests ==========

class TestCLICommandsIntegration:
    """CLI 命令集成测试"""

    def test_all_commands_on_same_file(self, cli_runner, sample_pdf):
        """测试所有命令在同一个文件上运行"""
        # text 命令
        result = cli_runner.invoke(cli, ['text', sample_pdf])
        assert result.exit_code == 0

        # tables 命令
        result = cli_runner.invoke(cli, ['tables', sample_pdf])
        assert result.exit_code == 0

        # images 命令
        result = cli_runner.invoke(cli, ['images', sample_pdf])
        assert result.exit_code == 0

        # metadata 命令
        result = cli_runner.invoke(cli, ['metadata', sample_pdf])
        assert result.exit_code == 0

        # structure 命令
        result = cli_runner.invoke(cli, ['structure', sample_pdf])
        assert result.exit_code == 0

    def test_commands_with_page_ranges(self, cli_runner, multi_page_pdf):
        """测试所有命令使用页码范围"""
        page_range = "1-3,5,7-9"

        # text
        result = cli_runner.invoke(cli, ['text', multi_page_pdf, '-p', page_range])
        assert result.exit_code == 0

        # tables
        result = cli_runner.invoke(cli, ['tables', multi_page_pdf, '-p', page_range])
        assert result.exit_code == 0

        # images
        result = cli_runner.invoke(cli, ['images', multi_page_pdf, '-p', page_range])
        assert result.exit_code == 0

        # structure
        result = cli_runner.invoke(cli, ['structure', multi_page_pdf, '-p', page_range])
        assert result.exit_code == 0

    def test_commands_with_json_output(self, cli_runner, sample_pdf):
        """测试所有命令使用 JSON 输出"""
        # text
        result = cli_runner.invoke(cli, ['text', sample_pdf, '--format', 'json'])
        assert result.exit_code == 0
        json.loads(result.output)  # 验证是有效 JSON

        # tables
        result = cli_runner.invoke(cli, ['tables', sample_pdf, '--format', 'json'])
        assert result.exit_code == 0
        json.loads(result.output)

        # images
        result = cli_runner.invoke(cli, ['images', sample_pdf])
        assert result.exit_code == 0
        json.loads(result.output)

        # metadata
        result = cli_runner.invoke(cli, ['metadata', sample_pdf])
        assert result.exit_code == 0
        json.loads(result.output)

        # structure
        result = cli_runner.invoke(cli, ['structure', sample_pdf])
        assert result.exit_code == 0
        json.loads(result.output)


# ========== Error Handling Tests ==========

class TestCLICommandErrorHandling:
    """CLI 命令错误处理测试"""

    def test_text_nonexistent_file(self, cli_runner):
        """测试文件不存在"""
        result = cli_runner.invoke(cli, ['text', '/nonexistent/file.pdf'])
        assert result.exit_code != 0

    def test_tables_nonexistent_file(self, cli_runner):
        """测试文件不存在"""
        result = cli_runner.invoke(cli, ['tables', '/nonexistent/file.pdf'])
        assert result.exit_code != 0

    def test_images_nonexistent_file(self, cli_runner):
        """测试文件不存在"""
        result = cli_runner.invoke(cli, ['images', '/nonexistent/file.pdf'])
        assert result.exit_code != 0

    def test_metadata_nonexistent_file(self, cli_runner):
        """测试文件不存在"""
        result = cli_runner.invoke(cli, ['metadata', '/nonexistent/file.pdf'])
        assert result.exit_code != 0

    def test_structure_nonexistent_file(self, cli_runner):
        """测试文件不存在"""
        result = cli_runner.invoke(cli, ['structure', '/nonexistent/file.pdf'])
        assert result.exit_code != 0


# ========== Run Tests ==========

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
