"""测试 EPUB 转换器插件 (ToEpubPlugin)"""

import pytest
import os
import tempfile
import sys

# 确保可以导入插件
sys.path.insert(0, '/root/.openclaw/workspace/ai-pdf-agent')

from plugins.converters.to_epub import ToEpubPlugin


class TestToEpubPlugin:
    """测试 ToEpubPlugin 类"""

    @pytest.fixture
    def converter(self):
        """创建转换器实例"""
        return ToEpubPlugin()

    @pytest.fixture
    def sample_pdf_path(self):
        """示例 PDF 文件路径"""
        return "/testfiles/simple.pdf"

    @pytest.fixture
    def temp_output_path(self):
        """临时输出文件路径"""
        fd, path = tempfile.mkstemp(suffix=".epub")
        os.close(fd)
        yield path
        # 清理
        if os.path.exists(path):
            os.remove(path)

    @pytest.fixture
    def temp_cover_path(self):
        """创建临时封面图片"""
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        # 写入一个简单的 PNG 文件头
        with open(path, "wb") as f:
            # PNG 文件签名
            f.write(b'\x89PNG\r\n\x1a\n')
            # IHDR chunk (最小有效 PNG)
            f.write(b'\x00\x00\x00\x0d')  # 长度
            f.write(b'IHDR')
            f.write(b'\x00\x00\x00\x01')  # 宽度 1
            f.write(b'\x00\x00\x00\x01')  # 高度 1
            f.write(b'\x08\x06\x00\x00\x00')  # 位深度 8, 颜色类型 6 (RGBA), 压缩方法 0, 过滤器方法 0, 交错方法 0
            f.write(b'\x1f\x15\xc4\x89')  # CRC
            # IDAT chunk (空)
            f.write(b'\x00\x00\x00\x0a')
            f.write(b'IDAT')
            f.write(b'x78\x9c\x01\x00\x00\xff\xff\x00\x00\x00\x02')
            f.write(b'\x00\x01\xb2\x8b')
            # IEND chunk
            f.write(b'\x00\x00\x00\x00')
            f.write(b'IEND')
            f.write(b'\xae\x42\x60\x82')
        yield path
        # 清理
        if os.path.exists(path):
            os.remove(path)

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
        assert converter.name == "to_epub"
        assert converter.version == "1.0.0"
        assert converter.description
        assert "EPUB" in converter.description
        assert converter.author == "李开发"
        assert converter.license == "MIT"

    def test_converter_is_available(self, converter):
        """测试转换器是否可用"""
        result = converter.is_available()
        assert isinstance(result, bool)

    def test_convert_basic(self, converter, sample_pdf_path, temp_output_path):
        """测试基本的 PDF 转 EPUB 转换"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(sample_pdf_path, output_path=temp_output_path)

        assert result["success"] is True
        assert result["pages"] > 0
        assert result["chapters"] > 0
        assert result["output_path"] == temp_output_path
        assert result["error"] is None
        assert os.path.exists(temp_output_path)

        # 验证 EPUB 文件大小（应该大于 0）
        assert os.path.getsize(temp_output_path) > 0

    def test_convert_with_title_and_author(self, converter, sample_pdf_path, temp_output_path):
        """测试转换并指定标题和作者"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            title="Test Book",
            author="Test Author"
        )

        assert result["success"] is True
        assert result["output_path"] == temp_output_path
        assert os.path.exists(temp_output_path)

    def test_convert_with_page_range(self, converter, sample_pdf_path, temp_output_path):
        """测试转换指定页面范围"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            page_range=(1, 2)
        )

        assert result["success"] is True
        assert result["output_path"] == temp_output_path
        assert os.path.exists(temp_output_path)

    def test_convert_with_single_page(self, converter, sample_pdf_path, temp_output_path):
        """测试转换单个页面"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            page=1
        )

        assert result["success"] is True
        assert result["output_path"] == temp_output_path
        assert os.path.exists(temp_output_path)

    def test_convert_with_page_list(self, converter, sample_pdf_path, temp_output_path):
        """测试转换指定页面列表"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            pages=[1, 2]
        )

        assert result["success"] is True
        assert result["output_path"] == temp_output_path
        assert os.path.exists(temp_output_path)

    def test_convert_with_include_images(self, converter, sample_pdf_path, temp_output_path):
        """测试转换并包含图片"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            include_images=True
        )

        assert result["success"] is True
        assert result["output_path"] == temp_output_path
        assert os.path.exists(temp_output_path)

    def test_convert_without_images(self, converter, sample_pdf_path, temp_output_path):
        """测试转换不包含图片"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            include_images=False
        )

        assert result["success"] is True
        assert result["output_path"] == temp_output_path
        assert os.path.exists(temp_output_path)

    def test_convert_with_chapter_pages(self, converter, sample_pdf_path, temp_output_path):
        """测试使用章节分组（每 N 页一章）"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        # 每页一章
        result1 = converter.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            chapter_pages=0
        )
        assert result1["success"] is True

        # 每 2 页一章
        result2 = converter.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            chapter_pages=2
        )
        assert result2["success"] is True

    def test_convert_with_cover_image(self, converter, sample_pdf_path, temp_output_path, temp_cover_path):
        """测试转换并添加封面图片"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            cover_path=temp_cover_path
        )

        assert result["success"] is True
        assert result["output_path"] == temp_output_path
        assert os.path.exists(temp_output_path)

    def test_convert_without_output_path(self, converter, sample_pdf_path):
        """测试转换不指定输出路径（应失败）"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(sample_pdf_path)

        assert result["success"] is False
        assert result["error"]
        assert "output path" in result["error"].lower()

    def test_convert_invalid_file(self, converter, temp_output_path):
        """测试转换不存在的文件"""
        result = converter.convert("/nonexistent/file.pdf", output_path=temp_output_path)

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
            "metadata": {},
            "pages": 1,
            "chapters": 1,
            "images": 0,
            "output_path": "/test/output.epub",
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


class TestTextConversion:
    """测试文本转 EPUB 功能"""

    @pytest.fixture
    def converter(self):
        """创建转换器实例"""
        return ToEpubPlugin()

    @pytest.fixture
    def temp_output_path(self):
        """临时输出文件路径"""
        fd, path = tempfile.mkstemp(suffix=".epub")
        os.close(fd)
        yield path
        # 清理
        if os.path.exists(path):
            os.remove(path)

    def test_convert_text_to_epub(self, converter, temp_output_path):
        """测试将纯文本转换为 EPUB"""
        text = "Hello World\n\nThis is a test.\n\nSecond paragraph."

        result = converter.convert_text_to_epub(
            text,
            output_path=temp_output_path,
            title="Test Document",
            author="Test Author"
        )

        assert result["success"] is True
        assert result["pages"] == 1
        assert result["chapters"] == 1
        assert result["output_path"] == temp_output_path
        assert os.path.exists(temp_output_path)
        assert os.path.getsize(temp_output_path) > 0

    def test_convert_empty_text(self, converter, temp_output_path):
        """测试转换空文本"""
        result = converter.convert_text_to_epub("", temp_output_path)

        # 即使是空文本，也应该创建有效的 EPUB
        assert isinstance(result, dict)
        assert "success" in result

    def test_convert_text_with_special_chars(self, converter, temp_output_path):
        """测试转换包含特殊字符的文本"""
        text = "Hello <>&'\" World\n\n特殊字符测试"

        result = converter.convert_text_to_epub(text, temp_output_path)

        assert result["success"] is True
        assert os.path.exists(temp_output_path)

    def test_convert_text_long_paragraphs(self, converter, temp_output_path):
        """测试转换长段落"""
        text = "Paragraph 1" * 100 + "\n\n" + "Paragraph 2" * 100

        result = converter.convert_text_to_epub(text, temp_output_path)

        assert result["success"] is True
        assert os.path.exists(temp_output_path)

    def test_convert_text_without_title_author(self, converter, temp_output_path):
        """测试转换文本不指定标题和作者"""
        text = "Test content"

        result = converter.convert_text_to_epub(text, temp_output_path)

        assert result["success"] is True
        assert os.path.exists(temp_output_path)


class TestHelperMethods:
    """测试辅助方法"""

    @pytest.fixture
    def converter(self):
        """创建转换器实例"""
        return ToEpubPlugin()

    def test_determine_pages_to_process_all(self, converter):
        """测试确定要处理的所有页面"""
        pages = converter._determine_pages_to_process({}, 5)
        assert pages == [1, 2, 3, 4, 5]

    def test_determine_pages_to_process_single(self, converter):
        """测试确定要处理的单个页面"""
        pages = converter._determine_pages_to_process({"page": 3}, 10)
        assert pages == [3]

    def test_determine_pages_to_process_range(self, converter):
        """测试确定要处理的页面范围"""
        pages = converter._determine_pages_to_process({"page_range": (2, 5)}, 10)
        assert pages == [2, 3, 4, 5]

    def test_determine_pages_to_process_list(self, converter):
        """测试确定要处理的页面列表"""
        pages = converter._determine_pages_to_process({"pages": [1, 3, 5]}, 10)
        assert pages == [1, 3, 5]

    def test_determine_pages_to_process_invalid(self, converter):
        """测试确定要处理的页面（无效参数）"""
        # 无效参数应返回所有页面
        pages = converter._determine_pages_to_process({"page": 999}, 10)
        assert pages == list(range(1, 11))

    def test_group_pages_by_chapter_zero(self, converter):
        """测试按章节分组页面（每页一章）"""
        pages = [1, 2, 3, 4, 5]
        groups = converter._group_pages_by_chapter(pages, 0)
        assert groups == [[1], [2], [3], [4], [5]]

    def test_group_pages_by_chapter_two(self, converter):
        """测试按章节分组页面（每2页一章）"""
        pages = [1, 2, 3, 4, 5, 6]
        groups = converter._group_pages_by_chapter(pages, 2)
        assert groups == [[1, 2], [3, 4], [5, 6]]

    def test_group_pages_by_chapter_negative(self, converter):
        """测试按章节分组页面（负数，应每页一章）"""
        pages = [1, 2, 3]
        groups = converter._group_pages_by_chapter(pages, -1)
        assert groups == [[1], [2], [3]]

    def test_convert_text_block_to_html(self) -> None:
        """测试将文本块转换为 HTML"""
        converter = ToEpubPlugin()

        # 创建一个模拟的文本块
        block = {
            "lines": [
                {
                    "spans": [
                        {
                            "text": "This is a test paragraph",
                            "size": 12
                        }
                    ]
                },
                {
                    "spans": [
                        {
                            "text": "• List item 1",
                            "size": 12
                        }
                    ]
                },
                {
                    "spans": [
                        {
                            "text": "1. Numbered item",
                            "size": 12
                        }
                    ]
                }
            ]
        }

        html_content = converter._convert_text_block_to_html(block)

        assert "This is a test paragraph" in html_content
        assert "<p>" in html_content
        assert "<li>" in html_content
        assert "List item 1" in html_content
        assert "Numbered item" in html_content

    def test_convert_empty_text_block(self, converter):
        """测试转换空文本块"""
        block = {}
        html_content = converter._convert_text_block_to_html(block)
        assert html_content == ""

    def test_convert_image_block_to_html(self, converter):
        """测试将图片块转换为 HTML"""
        block = {
            "bbox": [0, 0, 100, 200]
        }

        html_content = converter._convert_image_block_to_html(block, 5)

        assert "image-placeholder" in html_content
        assert "Image from page 5" in html_content
        assert "100x200" in html_content

    def test_convert_image_block_invalid_bbox(self, converter):
        """测试转换无效 bbox 的图片块"""
        block = {"bbox": []}

        html_content = converter._convert_image_block_to_html(block, 1)

        assert isinstance(html_content, str)
        assert "image-placeholder" in html_content

    def test_get_default_css(self, converter):
        """测试获取默认 CSS"""
        css = converter._get_default_css()

        assert isinstance(css, str)
        assert "body {" in css
        assert "font-family" in css
        assert "page-break" in css

    def test_text_to_html_paragraphs(self, converter):
        """测试将文本转换为 HTML 段落"""
        text = "First paragraph\n\nSecond paragraph\n\nThird paragraph"

        html_content = converter._text_to_html_paragraphs(text)

        assert "<p>First paragraph</p>" in html_content
        assert "<p>Second paragraph</p>" in html_content
        assert "<p>Third paragraph</p>" in html_content

    def test_text_to_html_paragraphs_with_linebreaks(self, converter):
        """测试将文本转换为 HTML 段落（包含换行符）"""
        text = "Line 1\nLine 2\nLine 3"

        html_content = converter._text_to_html_paragraphs(text)

        assert "Line 1" in html_content
        assert "<br/>" in html_content or "<br>" in html_content


class TestPluginMetadata:
    """测试插件元数据方法"""

    @pytest.fixture
    def converter(self):
        """创建转换器实例"""
        return ToEpubPlugin()

    def test_check_dependencies(self, converter):
        """测试检查依赖"""
        deps_ok, missing = converter.check_dependencies()
        assert isinstance(deps_ok, bool)
        assert isinstance(missing, list)

    def test_get_metadata(self, converter):
        """测试获取插件元数据"""
        metadata = converter.get_metadata()

        assert isinstance(metadata, dict)
        assert metadata["name"] == "to_epub"
        assert metadata["version"] == "1.0.0"
        assert metadata["plugin_type"] == "converter"
        assert metadata["author"] == "李开发"

    def test_get_help(self, converter):
        """测试获取帮助信息"""
        help_text = converter.get_help()
        assert isinstance(help_text, str)
        assert converter.name in help_text
        assert "output_path" in help_text


class TestEdgeCases:
    """测试边界情况"""

    @pytest.fixture
    def converter(self):
        """创建转换器实例"""
        return ToEpubPlugin()

    @pytest.fixture
    def temp_output_path(self):
        """临时输出文件路径"""
        fd, path = tempfile.mkstemp(suffix=".epub")
        os.close(fd)
        yield path
        # 清理
        if os.path.exists(path):
            os.remove(path)

    def test_convert_with_invalid_page_range(self, converter, temp_output_path):
        """测试使用无效的页面范围"""
        sample_pdf = "/testfiles/simple.pdf"

        if not os.path.exists(sample_pdf):
            pytest.skip(f"Sample PDF not found: {sample_pdf}")

        # 测试超出范围的页面
        result = converter.convert(sample_pdf, output_path=temp_output_path, page_range=(999, 1000))
        # 应该能处理而不崩溃
        assert isinstance(result, dict)

    def test_convert_with_empty_page_list(self, converter, temp_output_path):
        """测试使用空的页面列表"""
        sample_pdf = "/testfiles/simple.pdf"

        if not os.path.exists(sample_pdf):
            pytest.skip(f"Sample PDF not found: {sample_pdf}")

        result = converter.convert(sample_pdf, output_path=temp_output_path, pages=[])
        # 应该能处理而不崩溃
        assert isinstance(result, dict)

    def test_convert_nonexistent_cover(self, converter, sample_pdf_path, temp_output_path):
        """测试使用不存在的封面图片"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = converter.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            cover_path="/nonexistent/cover.jpg"
        )

        # 即使封面不存在，转换也应该成功
        assert isinstance(result, dict)


# 测试完成
__all__ = ["ToEpubPlugin"]
