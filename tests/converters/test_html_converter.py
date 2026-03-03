"""测试 HTML 转换器插件 (ToHtmlConverter)"""

import pytest
import os
import tempfile
import sys

# 确保可以导入插件
sys.path.insert(0, '/root/.openclaw/workspace/ai-pdf-agent')

from plugins.converters.html_converter import ToHtmlConverter


# 共享 fixtures
@pytest.fixture
def converter():
    """创建转换器实例"""
    return ToHtmlConverter()


@pytest.fixture
def sample_pdf_path():
    """示例 PDF 文件路径"""
    return "/testfiles/simple.pdf"


@pytest.fixture
def temp_output_path():
    """临时输出文件路径"""
    fd, path = tempfile.mkstemp(suffix=".html")
    os.close(fd)
    yield path
    # 清理
    if os.path.exists(path):
        os.remove(path)


class TestToHtmlConverter:
    """测试 ToHtmlConverter 类"""

    def test_converter_inherits_from_base_plugin(self, converter):
        """测试转换器继承自 BasePlugin"""
        from core.plugin_system.base_plugin import BasePlugin
        assert isinstance(converter, BasePlugin)

    def test_converter_inherits_from_base_converter_plugin(self, converter):
        """测试转换器继承自 BaseConverterPlugin"""
        from core.plugin_system.base_converter_plugin import BaseConverterPlugin
        assert isinstance(converter, BaseConverterPlugin)

    def test_converter_metadata(self, converter):
        """测试转换器元数据"""
        assert converter.name == "to_html"
        assert converter.version == "1.0.0"
        assert converter.description
        assert "HTML" in converter.description
        assert converter.author == "李开发"
        assert converter.license == "MIT"

    def test_converter_is_available(self, converter):
        """测试转换器是否可用"""
        result = converter.is_available()
        assert isinstance(result, bool)

    def test_convert_basic(self, converter, sample_pdf_path):
        """测试基本的 PDF 转 HTML 转换"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(sample_pdf_path)

        assert result["success"] is True
        assert result["content"]
        assert result["pages"] > 0
        assert result["metadata"]
        assert result["error"] is None

        # 验证 HTML 结构
        html = result["content"]
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "<body>" in html
        assert "</body>" in html
        assert "</html>" in html

    def test_convert_with_output_path(self, converter, sample_pdf_path, temp_output_path):
        """测试转换并保存到指定路径"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(
            sample_pdf_path,
            output_path=temp_output_path
        )

        assert result["success"] is True
        assert result["output_path"] == temp_output_path
        assert os.path.exists(temp_output_path)

        # 验证文件内容
        with open(temp_output_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        assert file_content == result["content"]

    def test_convert_with_page_range(self, converter, sample_pdf_path):
        """测试转换指定页面范围"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(sample_pdf_path, page_range=(1, 2))

        assert result["success"] is True
        assert result["content"]

    def test_convert_with_single_page(self, converter, sample_pdf_path):
        """测试转换单个页面"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(sample_pdf_path, page=1)

        assert result["success"] is True
        assert result["content"]

    def test_convert_with_page_list(self, converter, sample_pdf_path):
        """测试转换指定页面列表"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(sample_pdf_path, pages=[1, 2])

        assert result["success"] is True
        assert result["content"]

    def test_convert_with_embed_images(self, converter, sample_pdf_path):
        """测试转换并嵌入图片"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(sample_pdf_path, embed_images=True)

        assert result["success"] is True
        assert result["content"]

    def test_convert_with_responsive_design(self, converter, sample_pdf_path):
        """测试使用响应式设计"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(sample_pdf_path, responsive=True)

        assert result["success"] is True
        assert result["content"]

        # 验证包含响应式 CSS
        html = result["content"]
        assert "<style>" in html
        assert "max-width" in html or "viewport" in html

    def test_convert_with_custom_css(self, converter, sample_pdf_path):
        """测试使用自定义 CSS"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        custom_css = "body { background-color: #f0f0f0; }"
        result = converter.convert(sample_pdf_path, custom_css=custom_css)

        assert result["success"] is True
        assert result["content"]

        # 验证包含自定义 CSS
        html = result["content"]
        assert "background-color: #f0f0f0" in html

    def test_convert_invalid_file(self, converter):
        """测试转换不存在的文件"""
        result = converter.convert("/nonexistent/file.pdf")

        assert result["success"] is False
        assert result["error"]
        assert "not found" in result["error"].lower()

    def test_validate_valid_pdf(self, converter, sample_pdf_path):
        """测试验证有效的 PDF"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        is_valid, error = converter.validate(sample_pdf_path)

        assert is_valid is True
        assert error is None

    def test_validate_invalid_file(self, converter):
        """测试验证不存在的文件"""
        is_valid, error = converter.validate("/nonexistent/file.pdf")

        assert is_valid is False
        assert error
        assert "not found" in error.lower()

    def test_validate_non_pdf_file(self, converter, tmp_path):
        """测试验证非 PDF 文件"""
        # 创建一个非 PDF 文件
        non_pdf_file = tmp_path / "test.txt"
        non_pdf_file.write_text("This is not a PDF")

        is_valid, error = converter.validate(str(non_pdf_file))

        assert is_valid is False
        assert error
        assert "not a pdf" in error.lower()


class TestTextConversion:
    """测试文本转 HTML 功能"""

    def test_convert_text_to_html(self, converter):
        """测试将纯文本转换为 HTML"""
        text = "Hello\nWorld\nThis is a test"

        html_content = converter.convert_text_to_html(text)

        assert "Hello" in html_content
        assert "World" in html_content
        assert "This is a test" in html_content
        assert "<br>" in html_content  # 换行符应被转换

    def test_convert_text_to_html_with_special_chars(self, converter):
        """测试转换包含特殊字符的文本"""
        text = "Hello <>&'\" World"

        html_content = converter.convert_text_to_html(text)

        # 特殊字符应被转义
        assert "&lt;" in html_content  # <
        assert "&gt;" in html_content  # >
        assert "&amp;" in html_content  # &

    def test_convert_empty_text(self, converter):
        """测试转换空文本"""
        html_content = converter.convert_text_to_html("")
        assert html_content == ""


class TestTableConversion:
    """测试表格转 HTML 功能"""

    def test_convert_table_to_html(self, converter):
        """测试将表格数据转换为 HTML 表格"""
        table_data = [
            ["Name", "Age", "City"],
            ["Alice", "25", "New York"],
            ["Bob", "30", "London"],
        ]

        html_content = converter.convert_table_to_html(table_data)

        assert "<table" in html_content
        assert "</table>" in html_content
        assert "<tr>" in html_content
        assert "</tr>" in html_content
        assert "<th>" in html_content  # 表头
        assert "</th>" in html_content
        assert "<td>" in html_content  # 单元格
        assert "</td>" in html_content
        assert "Name" in html_content
        assert "Alice" in html_content

    def test_convert_empty_table(self, converter):
        """测试转换空表格"""
        html_content = converter.convert_table_to_html([])
        assert html_content == ""

    def test_convert_table_with_none_cells(self, converter):
        """测试转换包含 None 单元格的表格"""
        table_data = [
            ["A", None, "C"],
            [None, "B", None],
        ]

        html_content = converter.convert_table_to_html(table_data)

        assert "<table" in html_content
        assert "<td>" in html_content


class TestListConversion:
    """测试列表转 HTML 功能"""

    def test_convert_ordered_list(self, converter):
        """测试转换为有序列表"""
        items = ["Item 1", "Item 2", "Item 3"]

        html_content = converter.convert_list_to_html(items, ordered=True)

        assert "<ol>" in html_content
        assert "</ol>" in html_content
        assert "<li>" in html_content
        assert "</li>" in html_content
        assert "Item 1" in html_content

    def test_convert_unordered_list(self, converter):
        """测试转换为无序列表"""
        items = ["Apple", "Banana", "Cherry"]

        html_content = converter.convert_list_to_html(items, ordered=False)

        assert "<ul>" in html_content
        assert "</ul>" in html_content
        assert "<li>" in html_content
        assert "</li>" in html_content

    def test_convert_empty_list(self, converter):
        """测试转换空列表"""
        html_content = converter.convert_list_to_html([])
        assert html_content == ""

    def test_convert_list_with_non_string_items(self, converter):
        """测试转换包含非字符串项的列表"""
        items = [123, 456, 789]

        html_content = converter.convert_list_to_html(items)

        assert "<ul>" in html_content
        assert "123" in html_content


class TestImageConversion:
    """测试图片转 HTML 功能"""

    def test_convert_images_without_embed(self, converter):
        """测试转换图片为 HTML（不嵌入）"""
        images = [
            {
                "page": 1,
                "format": "png",
                "width": 100,
                "height": 100,
                "data": b"fake_image_data",
            }
        ]

        html_content = converter.convert_images_to_html(images, embed=False)

        assert "<img" in html_content
        assert "page-1-image.png" in html_content
        assert 'width="100"' in html_content
        assert 'height="100"' in html_content

    def test_convert_images_with_embed(self, converter):
        """测试转换图片为 HTML（嵌入 base64）"""
        images = [
            {
                "page": 1,
                "format": "png",
                "width": 100,
                "height": 100,
                "data": b"fake_image_data",
            }
        ]

        html_content = converter.convert_images_to_html(images, embed=True)

        assert "<img" in html_content
        assert "data:image/png;base64," in html_content

    def test_convert_empty_images(self, converter):
        """测试转换空图片列表"""
        html_content = converter.convert_images_to_html([])
        assert html_content == ""


class TestValidationMethods:
    """测试验证方法"""

    def test_validate_input_valid(self, converter):
        """测试验证有效输入"""
        result = converter.validate_input(pdf_path="/test/simple.pdf")
        assert result is True

    def test_validate_input_missing_pdf_path(self, converter):
        """测试验证缺少 pdf_path"""
        result = converter.validate_input()
        assert result is False

    def test_validate_input_invalid_type(self, converter):
        """测试验证无效类型"""
        result = converter.validate_input(pdf_path=123)
        assert result is False

    def test_validate_output_valid(self, converter):
        """测试验证有效输出"""
        result = {
            "success": True,
            "content": "<html></html>",
            "metadata": {},
            "pages": 1,
            "output_path": None,
            "error": None,
        }
        assert converter.validate_output(result) is True

    def test_validate_output_invalid_type(self, converter):
        """测试验证无效输出类型"""
        assert converter.validate_output("not a dict") is False

    def test_validate_output_missing_keys(self, converter):
        """测试验证缺少必需键的输出"""
        result = {"success": True}
        assert converter.validate_output(result) is False


class TestPluginMetadata:
    """测试插件元数据方法"""

    def test_check_dependencies(self, converter):
        """测试检查依赖"""
        deps_ok, missing = converter.check_dependencies()
        assert isinstance(deps_ok, bool)
        assert isinstance(missing, list)

    def test_get_metadata(self, converter):
        """测试获取插件元数据"""
        metadata = converter.get_metadata()

        assert isinstance(metadata, dict)
        assert metadata["name"] == "to_html"
        assert metadata["version"] == "1.0.0"
        assert metadata["plugin_type"] == "converter"
        assert metadata["author"] == "李开发"

    def test_get_help(self, converter):
        """测试获取帮助信息"""
        help_text = converter.get_help()
        assert isinstance(help_text, str)
        assert converter.name in help_text


class TestEdgeCases:
    """测试边界情况"""

    def test_convert_with_invalid_page_range(self, converter):
        """测试使用无效的页面范围"""
        sample_pdf = "/testfiles/simple.pdf"

        if not os.path.exists(sample_pdf):
            pytest.skip(f"Sample PDF not found: {sample_pdf}")

        # 测试超出范围的页面
        result = converter.convert(sample_pdf, page_range=(999, 1000))
        assert isinstance(result, dict)

    def test_convert_images_with_missing_fields(self, converter):
        """测试转换缺少字段的图片"""
        images = [{"page": 1}]  # 缺少其他字段

        # 应该能处理而不崩溃
        html_content = converter.convert_images_to_html(images)
        assert isinstance(html_content, str)
