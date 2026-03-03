"""测试 HTML 转换插件"""

import pytest
import os
import tempfile

# 确保可以导入插件
import sys
sys.path.insert(0, '/root/.openclaw/workspace/ai-pdf-agent')

from plugins.converters.to_html import ToHtmlPlugin


class TestToHtmlPlugin:
    """测试 ToHtmlPlugin"""

    @pytest.fixture
    def plugin(self):
        """创建插件实例"""
        return ToHtmlPlugin()

    @pytest.fixture
    def sample_pdf_path(self):
        """示例 PDF 文件路径"""
        return "/testfiles/simple.pdf"

    @pytest.fixture
    def temp_output_path(self):
        """临时输出文件路径"""
        fd, path = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        yield path
        # 清理
        if os.path.exists(path):
            os.remove(path)

    def test_plugin_metadata(self, plugin):
        """测试插件元数据"""
        assert plugin.name == "to_html"
        assert plugin.version == "1.0.0"
        assert plugin.description
        assert plugin.author == "李开发"
        assert plugin.license == "MIT"

    def test_is_available(self, plugin):
        """测试插件是否可用"""
        # 需要检查依赖是否安装
        result = plugin.is_available()
        # 这里我们只测试方法存在，具体结果取决于环境
        assert isinstance(result, bool)

    def test_convert_success(self, plugin, sample_pdf_path, temp_output_path):
        """测试成功转换"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = plugin.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            embed_images=False,
            responsive=True
        )

        assert result["success"] is True
        assert result["content"]  # HTML 内容不应为空
        assert result["pages"] > 0  # 应该有页面
        assert result["metadata"]  # 应该有元数据
        assert result["output_path"] == temp_output_path

        # 检查输出文件是否存在
        assert os.path.exists(temp_output_path)

        # 检查 HTML 内容格式
        html_content = result["content"]
        assert "<!DOCTYPE html>" in html_content
        assert "<html" in html_content
        assert "</html>" in html_content
        assert "<body>" in html_content
        assert "</body>" in html_content

    def test_convert_with_page_range(self, plugin, sample_pdf_path):
        """测试转换指定页面范围"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = plugin.convert(sample_pdf_path, page_range=(1, 1))

        assert result["success"] is True
        assert result["pages"] >= 1

    def test_convert_with_single_page(self, plugin, sample_pdf_path):
        """测试转换单个页面"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = plugin.convert(sample_pdf_path, page=1)

        assert result["success"] is True
        assert result["content"]

    def test_convert_with_page_list(self, plugin, sample_pdf_path):
        """测试转换指定页面列表"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = plugin.convert(sample_pdf_path, pages=[1, 2])

        assert result["success"] is True
        assert result["content"]

    def test_convert_with_embed_images(self, plugin, sample_pdf_path):
        """测试嵌入图片"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = plugin.convert(sample_pdf_path, embed_images=True)

        assert result["success"] is True
        assert result["content"]

    def test_convert_invalid_file(self, plugin):
        """测试转换不存在的文件"""
        result = plugin.convert("/nonexistent/file.pdf")

        assert result["success"] is False
        assert result["error"]
        assert "not found" in result["error"].lower()

    def test_validate_valid_pdf(self, plugin, sample_pdf_path):
        """测试验证有效的 PDF"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        is_valid, error = plugin.validate(sample_pdf_path)

        assert is_valid is True
        assert error is None

    def test_validate_invalid_file(self, plugin):
        """测试验证不存在的文件"""
        is_valid, error = plugin.validate("/nonexistent/file.pdf")

        assert is_valid is False
        assert error
        assert "not found" in error.lower()

    def test_validate_non_pdf_file(self, plugin, tmp_path):
        """测试验证非 PDF 文件"""
        # 创建一个非 PDF 文件
        non_pdf_file = tmp_path / "test.txt"
        non_pdf_file.write_text("This is not a PDF")

        is_valid, error = plugin.validate(str(non_pdf_file))

        assert is_valid is False
        assert error
        assert "not a pdf" in error.lower()

    def test_convert_text_to_html(self, plugin):
        """测试将文本转换为 HTML"""
        text = "Hello\nWorld\nThis is a test"

        html_content = plugin.convert_text_to_html(text)

        assert "Hello" in html_content
        assert "World" in html_content
        assert "This is a test" in html_content
        assert "<br>" in html_content  # 换行符应被转换

    def test_convert_text_to_html_with_special_chars(self, plugin):
        """测试转换包含特殊字符的文本"""
        text = "Hello <>&'\" World"

        html_content = plugin.convert_text_to_html(text)

        # 特殊字符应被转义
        assert "&lt;" in html_content  # <
        assert "&gt;" in html_content  # >
        assert "&amp;" in html_content  # &
        assert "&apos;" in html_content or "&#x27;" in html_content  # '
        assert "&quot;" in html_content  # "

    def test_convert_table_to_html(self, plugin):
        """测试将表格转换为 HTML"""
        table_data = [
            ["Name", "Age", "City"],
            ["Alice", "25", "New York"],
            ["Bob", "30", "London"],
        ]

        html_content = plugin.convert_table_to_html(table_data)

        assert "<table" in html_content
        assert "</table>" in html_content
        assert "<tr>" in html_content
        assert "</tr>" in html_content
        assert "<th>" in html_content
        assert "</th>" in html_content
        assert "<td>" in html_content
        assert "</td>" in html_content
        assert "Name" in html_content
        assert "Alice" in html_content
        assert "Bob" in html_content

    def test_convert_table_to_html_empty(self, plugin):
        """测试转换空表格"""
        html_content = plugin.convert_table_to_html([])
        assert html_content == ""

    def test_convert_list_to_html_ordered(self, plugin):
        """测试转换为有序列表"""
        items = ["Item 1", "Item 2", "Item 3"]

        html_content = plugin.convert_list_to_html(items, ordered=True)

        assert "<ol>" in html_content
        assert "</ol>" in html_content
        assert "<li>" in html_content
        assert "</li>" in html_content
        assert "Item 1" in html_content
        assert "Item 2" in html_content
        assert "Item 3" in html_content

    def test_convert_list_to_html_unordered(self, plugin):
        """测试转换为无序列表"""
        items = ["Apple", "Banana", "Cherry"]

        html_content = plugin.convert_list_to_html(items, ordered=False)

        assert "<ul>" in html_content
        assert "</ul>" in html_content
        assert "<li>" in html_content
        assert "</li>" in html_content
        assert "Apple" in html_content
        assert "Banana" in html_content
        assert "Cherry" in html_content

    def test_convert_list_to_html_empty(self, plugin):
        """测试转换空列表"""
        html_content = plugin.convert_list_to_html([])
        assert html_content == ""

    def test_convert_images_to_html_without_embed(self, plugin):
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

        html_content = plugin.convert_images_to_html(images, embed=False)

        assert "<img" in html_content
        assert "page-1-image.png" in html_content
        assert 'width="100"' in html_content
        assert 'height="100"' in html_content

    def test_convert_images_to_html_with_embed(self, plugin):
        """测试转换图片为 HTML（嵌入）"""
        images = [
            {
                "page": 1,
                "format": "png",
                "width": 100,
                "height": 100,
                "data": b"fake_image_data",
            }
        ]

        html_content = plugin.convert_images_to_html(images, embed=True)

        assert "<img" in html_content
        assert "data:image/png;base64," in html_content

    def test_convert_images_to_html_empty(self, plugin):
        """测试转换空图片列表"""
        html_content = plugin.convert_images_to_html([])
        assert html_content == ""

    def test_validate_input_valid(self, plugin, sample_pdf_path):
        """测试验证有效输入"""
        result = plugin.validate_input(pdf_path=sample_pdf_path)
        assert result is True

    def test_validate_input_missing_pdf_path(self, plugin):
        """测试验证缺少 pdf_path"""
        result = plugin.validate_input()
        assert result is False

    def test_validate_input_invalid_type(self, plugin):
        """测试验证无效类型"""
        result = plugin.validate_input(pdf_path=123)
        assert result is False

    def test_validate_output_valid(self, plugin):
        """测试验证有效输出"""
        result = {
            "success": True,
            "content": "<html></html>",
            "metadata": {},
            "pages": 1,
            "output_path": None,
            "error": None,
        }
        assert plugin.validate_output(result) is True

    def test_validate_output_invalid_type(self, plugin):
        """测试验证无效输出类型"""
        assert plugin.validate_output("not a dict") is False

    def test_validate_output_missing_keys(self, plugin):
        """测试验证缺少必需键的输出"""
        result = {"success": True}
        assert plugin.validate_output(result) is False

    def test_check_dependencies(self, plugin):
        """测试检查依赖"""
        deps_ok, missing = plugin.check_dependencies()
        assert isinstance(deps_ok, bool)
        assert isinstance(missing, list)

    def test_get_metadata(self, plugin):
        """测试获取插件元数据"""
        metadata = plugin.get_metadata()

        assert isinstance(metadata, dict)
        assert metadata["name"] == "to_html"
        assert metadata["version"] == "1.0.0"
        assert metadata["plugin_type"] == "converter"
        assert metadata["author"] == "李开发"

    def test_get_help(self, plugin):
        """测试获取帮助信息"""
        help_text = plugin.get_help()
        assert isinstance(help_text, str)
        assert plugin.name in help_text


class TestToHtmlPluginEdgeCases:
    """测试边界情况"""

    @pytest.fixture
    def plugin(self):
        """创建插件实例"""
        return ToHtmlPlugin()

    def test_convert_with_invalid_page_range(self, plugin, tmp_path):
        """测试使用无效的页面范围"""
        # 创建一个临时 PDF 文件（如果需要）
        # 这里使用假设存在的 PDF
        sample_pdf = "/testfiles/simple.pdf"

        if not os.path.exists(sample_pdf):
            pytest.skip(f"Sample PDF not found: {sample_pdf}")

        # 测试超出范围的页面
        result = plugin.convert(sample_pdf, page_range=(999, 1000))
        # 应该返回错误或处理边界情况
        assert isinstance(result, dict)

    def test_convert_text_with_empty_string(self, plugin):
        """测试转换空字符串"""
        html_content = plugin.convert_text_to_html("")
        assert html_content == ""

    def test_convert_table_with_none_cells(self, plugin):
        """测试转换包含 None 单元格的表格"""
        table_data = [
            ["A", None, "C"],
            [None, "B", None],
        ]

        html_content = plugin.convert_table_to_html(table_data)

        assert "<table" in html_content
        assert "<td>" in html_content

    def test_convert_list_with_non_string_items(self, plugin):
        """测试转换包含非字符串项的列表"""
        items = [123, 456, 789]

        html_content = plugin.convert_list_to_html(items)

        assert "<ul>" in html_content
        assert "123" in html_content
        assert "456" in html_content

    def test_convert_images_with_missing_fields(self, plugin):
        """测试转换缺少字段的图片"""
        images = [{"page": 1}]  # 缺少其他字段

        # 应该能处理而不崩溃
        html_content = plugin.convert_images_to_html(images)
        assert isinstance(html_content, str)
