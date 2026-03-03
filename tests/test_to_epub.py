"""测试 EPUB 转换插件"""

import pytest
import os
import tempfile

# 确保可以导入插件
import sys
sys.path.insert(0, '/root/.openclaw/workspace/ai-pdf-agent')

from plugins.converters.to_epub import ToEpubPlugin


class TestToEpubPlugin:
    """测试 ToEpubPlugin"""

    @pytest.fixture
    def plugin(self):
        """创建插件实例"""
        return ToEpubPlugin()

    @pytest.fixture
    def sample_pdf_path(self):
        """示例 PDF 文件路径"""
        return "/root/.openclaw/workspace/ai-pdf-agent/test_sample.pdf"

    @pytest.fixture
    def temp_output_path(self):
        """临时输出文件路径"""
        fd, path = tempfile.mkstemp(suffix=".epub")
        os.close(fd)
        yield path
        # 清理
        if os.path.exists(path):
            os.remove(path)

    def test_plugin_metadata(self, plugin):
        """测试插件元数据"""
        assert plugin.name == "to_epub"
        assert plugin.version == "1.0.0"
        assert plugin.description
        assert plugin.author == "李开发"
        assert plugin.license == "MIT"

    def test_is_available(self, plugin):
        """测试插件是否可用"""
        result = plugin.is_available()
        assert isinstance(result, bool)

    def test_convert_success(self, plugin, sample_pdf_path, temp_output_path):
        """测试成功转换"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = plugin.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            include_images=True,
            chapter_pages=0
        )

        assert result["success"] is True
        assert result["pages"] > 0  # 应该有页面
        assert result["chapters"] > 0  # 应该有章节
        assert result["output_path"] == temp_output_path
        assert result["error"] is None

        # 检查输出文件是否存在
        assert os.path.exists(temp_output_path)

        # 检查文件大小（EPUB 文件应该有内容）
        assert os.path.getsize(temp_output_path) > 0

    def test_convert_with_page_range(self, plugin, sample_pdf_path, temp_output_path):
        """测试转换指定页面范围"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = plugin.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            page_range=(1, 1)
        )

        assert result["success"] is True
        assert result["pages"] >= 1

    def test_convert_with_single_page(self, plugin, sample_pdf_path, temp_output_path):
        """测试转换单个页面"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = plugin.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            page=1
        )

        assert result["success"] is True
        assert result["pages"] >= 1

    def test_convert_with_page_list(self, plugin, sample_pdf_path, temp_output_path):
        """测试转换指定页面列表"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = plugin.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            pages=[1, 2]
        )

        assert result["success"] is True
        assert result["pages"] >= 1

    def test_convert_with_custom_title_and_author(self, plugin, sample_pdf_path, temp_output_path):
        """测试使用自定义标题和作者"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = plugin.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            title="Test Book Title",
            author="Test Author"
        )

        assert result["success"] is True

    def test_convert_with_chapter_pages(self, plugin, sample_pdf_path, temp_output_path):
        """测试按指定页数分组章节"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = plugin.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            chapter_pages=5  # 每 5 页一章
        )

        assert result["success"] is True

    def test_convert_without_images(self, plugin, sample_pdf_path, temp_output_path):
        """测试不包含图片的转换"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = plugin.convert(
            sample_pdf_path,
            output_path=temp_output_path,
            include_images=False
        )

        assert result["success"] is True

    def test_convert_invalid_file(self, plugin, temp_output_path):
        """测试转换不存在的文件"""
        result = plugin.convert(
            "/nonexistent/file.pdf",
            output_path=temp_output_path
        )

        assert result["success"] is False
        assert result["error"]
        assert "not found" in result["error"].lower()

    def test_convert_missing_output_path(self, plugin, sample_pdf_path):
        """测试缺少输出路径"""
        if not os.path.exists(sample_pdf_path):
            pytest.skip(f"Sample PDF not found: {sample_pdf_path}")

        result = plugin.convert(sample_pdf_path)

        assert result["success"] is False
        assert result["error"]
        assert "output path" in result["error"].lower()

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
            "metadata": {},
            "pages": 1,
            "chapters": 1,
            "images": 0,
            "output_path": "test.epub",
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
        assert metadata["name"] == "to_epub"
        assert metadata["version"] == "1.0.0"
        assert metadata["plugin_type"] == "converter"
        assert metadata["author"] == "李开发"

    def test_get_help(self, plugin):
        """测试获取帮助信息"""
        help_text = plugin.get_help()
        assert isinstance(help_text, str)
        assert plugin.name in help_text

    def test_convert_text_block_to_html(self, plugin):
        """测试转换文本块为 HTML"""
        block = {
            "type": 0,
            "lines": [
                {
                    "spans": [
                        {"text": "Hello World", "size": 12}
                    ]
                }
            ]
        }

        html = plugin._convert_text_block_to_html(block)

        assert "Hello" in html or "World" in html
        assert "<p>" in html or "<li>" in html

    def test_convert_text_block_to_html_empty(self, plugin):
        """测试转换空文本块"""
        block = {"type": 0}

        html = plugin._convert_text_block_to_html(block)
        assert html == ""

    def test_convert_text_block_to_html_list_item(self, plugin):
        """测试转换列表项"""
        block = {
            "type": 0,
            "lines": [
                {
                    "spans": [
                        {"text": "• First item", "size": 12}
                    ]
                }
            ]
        }

        html = plugin._convert_text_block_to_html(block)
        assert "<li>" in html

    def test_convert_image_block_to_html(self, plugin):
        """测试转换图片块为 HTML"""
        block = {
            "type": 1,
            "bbox": [0, 0, 100, 200]
        }

        html = plugin._convert_image_block_to_html(block, 1)
        assert "[Image from page 1" in html
        assert "100x200" in html

    def test_get_default_css(self, plugin):
        """测试获取默认 CSS"""
        css = plugin._get_default_css()

        assert isinstance(css, str)
        assert "body" in css
        assert "font-family" in css
        assert "page-break" in css

    def test_determine_pages_to_process_single_page(self, plugin):
        """测试确定要处理的页面（单页）"""
        kwargs = {"page": 2}
        pages = plugin._determine_pages_to_process(kwargs, 10)

        assert pages == [2]

    def test_determine_pages_to_process_page_range(self, plugin):
        """测试确定要处理的页面（范围）"""
        kwargs = {"page_range": (3, 5)}
        pages = plugin._determine_pages_to_process(kwargs, 10)

        assert pages == [3, 4, 5]

    def test_determine_pages_to_process_page_list(self, plugin):
        """测试确定要处理的页面（列表）"""
        kwargs = {"pages": [1, 3, 5, 7]}
        pages = plugin._determine_pages_to_process(kwargs, 10)

        assert pages == [1, 3, 5, 7]

    def test_determine_pages_to_process_all_pages(self, plugin):
        """测试确定要处理的页面（全部）"""
        kwargs = {}
        pages = plugin._determine_pages_to_process(kwargs, 5)

        assert pages == [1, 2, 3, 4, 5]

    def test_group_pages_by_chapter_single_page_per_chapter(self, plugin):
        """测试按章节分组页面（每页一章）"""
        pages = [1, 2, 3, 4, 5]
        groups = plugin._group_pages_by_chapter(pages, 0)

        assert len(groups) == 5
        assert groups == [[1], [2], [3], [4], [5]]

    def test_group_pages_by_chapter_multiple_pages(self, plugin):
        """测试按章节分组页面（多页一章）"""
        pages = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        groups = plugin._group_pages_by_chapter(pages, 3)

        assert len(groups) == 4
        assert groups[0] == [1, 2, 3]
        assert groups[1] == [4, 5, 6]
        assert groups[2] == [7, 8, 9]
        assert groups[3] == [10]


class TestToEpubPluginEdgeCases:
    """测试边界情况"""

    @pytest.fixture
    def plugin(self):
        """创建插件实例"""
        return ToEpubPlugin()

    def test_convert_with_invalid_page_range(self, plugin, tmp_path):
        """测试使用无效的页面范围"""
        temp_output = tmp_path / "test.epub"
        sample_pdf = "/root/.openclaw/workspace/ai-pdf-agent/test-pdfs/simple.pdf"

        if not os.path.exists(sample_pdf):
            pytest.skip(f"Sample PDF not found: {sample_pdf}")

        # 测试超出范围的页面
        result = plugin.convert(sample_pdf, output_path=str(temp_output), page_range=(999, 1000))
        # 应该返回错误或处理边界情况
        assert isinstance(result, dict)

    def test_convert_text_block_with_special_characters(self, plugin):
        """测试转换包含特殊字符的文本块"""
        block = {
            "type": 0,
            "lines": [
                {
                    "spans": [
                        {"text": "Hello <>&'\" World", "size": 12}
                    ]
                }
            ]
        }

        html = plugin._convert_text_block_to_html(block)

        # 特殊字符应该被转义
        assert "&lt;" in html or "&gt;" in html or "&amp;" in html

    def test_convert_image_block_with_invalid_bbox(self, plugin):
        """测试转换无效边界框的图片块"""
        block = {
            "type": 1,
            "bbox": []  # 空 bbox
        }

        # 应该能处理而不崩溃
        html = plugin._convert_image_block_to_html(block, 1)
        assert isinstance(html, str)

    def test_determine_pages_to_process_invalid_page(self, plugin):
        """测试确定要处理的页面（无效页码）"""
        kwargs = {"page": 999}
        pages = plugin._determine_pages_to_process(kwargs, 10)

        # 应该返回所有页面（默认行为）
        assert pages == list(range(1, 11))

    def test_determine_pages_to_process_invalid_range(self, plugin):
        """测试确定要处理的页面（无效范围）"""
        kwargs = {"page_range": (5, 3)}  # start > end
        pages = plugin._determine_pages_to_process(kwargs, 10)

        # 应该返回所有页面（默认行为）
        assert pages == list(range(1, 11))

    def test_group_pages_by_chapter_empty_list(self, plugin):
        """测试按章节分组空页面列表"""
        pages = []
        groups = plugin._group_pages_by_chapter(pages, 5)

        assert groups == []

    def test_group_pages_by_chapter_negative_chapter_pages(self, plugin):
        """测试按章节分组（负数每章页数）"""
        pages = [1, 2, 3]
        groups = plugin._group_pages_by_chapter(pages, -1)

        # 负数应该被当作 0 处理（每页一章）
        assert len(groups) == 3

    def test_convert_with_missing_metadata(self, plugin, tmp_path):
        """测试转换没有元数据的 PDF"""
        # 这里我们使用正常的 PDF，只是测试方法不会崩溃
        sample_pdf = "/root/.openclaw/workspace/ai-pdf-agent/test-pdfs/simple.pdf"
        temp_output = tmp_path / "test.epub"

        if not os.path.exists(sample_pdf):
            pytest.skip(f"Sample PDF not found: {sample_pdf}")

        result = plugin.convert(
            sample_pdf,
            output_path=str(temp_output),
            title="Custom Title",
            author="Custom Author"
        )

        # 应该能处理并使用自定义标题和作者
        assert isinstance(result, dict)

    def test_convert_encrypted_pdf(self, plugin, tmp_path):
        """测试转换加密的 PDF（会失败）"""
        # 我们需要创建一个加密的 PDF 或模拟
        # 这里我们测试验证方法
        is_valid, error = plugin.validate("/testfiles/encrypted.pdf")

        if os.path.exists("/testfiles/encrypted.pdf"):
            assert is_valid is False
            assert "encrypted" in error.lower()
        else:
            pytest.skip("Encrypted PDF not found for testing")
