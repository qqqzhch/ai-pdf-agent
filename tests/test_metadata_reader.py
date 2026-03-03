"""元数据读取插件单元测试"""

import os
import pytest
import tempfile
import fitz  # PyMuPDF

from plugins.readers.metadata_reader import MetadataReaderPlugin


class TestMetadataReaderPlugin:
    """MetadataReaderPlugin 测试类"""

    @pytest.fixture
    def plugin(self):
        """创建插件实例"""
        return MetadataReaderPlugin()

    @pytest.fixture
    def sample_pdf_path(self):
        """创建示例 PDF 文件"""
        # 创建临时 PDF 文件
        doc = fitz.open()

        # 设置元数据
        metadata = {
            "title": "Test Document",
            "author": "Test Author",
            "subject": "Test Subject",
            "keywords": "test, metadata, pdf",
            "creator": "Test Creator",
            "producer": "Test Producer",
        }
        doc.set_metadata(metadata)

        # 添加第一页
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "First Page Content", fontsize=12)
        page.insert_text(fitz.Point(50, 80), "This is the first page.", fontsize=12)

        # 添加第二页
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "Second Page Content", fontsize=12)
        page.insert_text(fitz.Point(50, 80), "This is the second page.", fontsize=12)

        # 添加第三页
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "Third Page Content", fontsize=12)
        page.insert_text(fitz.Point(50, 80), "This is the third page.", fontsize=12)

        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc.save(temp_file.name)
        doc.close()

        yield temp_file.name

        # 清理
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    @pytest.fixture
    def complex_pdf_path(self):
        """创建复杂 PDF 文件（包含图片和表格）"""
        doc = fitz.open()

        # 设置元数据
        metadata = {
            "title": "Complex Document with Images",
            "author": "Complex Author",
            "subject": "Complex Subject",
            "keywords": "complex, images, tables; multiple; keywords",
            "creator": "Complex Creator",
            "producer": "Complex Producer",
        }
        doc.set_metadata(metadata)

        # 添加包含图片的页面
        page = doc.new_page()

        # 创建简单的图片（纯色矩形）
        rect = fitz.Rect(100, 100, 200, 200)
        page.draw_rect(rect, color=(1, 0, 0), fill=(1, 0, 0))

        # 添加文本
        page.insert_text(fitz.Point(50, 50), "Page with Image", fontsize=12)
        page.insert_text(fitz.Point(50, 250), "Text below image", fontsize=10)

        # 添加多页文档
        for i in range(10):
            page = doc.new_page()
            page.insert_text(
                fitz.Point(50, 50),
                f"Page {i + 2} with lots of text content for word counting",
                fontsize=12,
            )
            # 添加更多文本
            for j in range(5):
                page.insert_text(
                    fitz.Point(50, 80 + j * 30),
                    f"Line {j + 1} on page {i + 2} with sample text.",
                    fontsize=10,
                )

        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc.save(temp_file.name)
        doc.close()

        yield temp_file.name

        # 清理
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    @pytest.fixture
    def encrypted_pdf_path(self):
        """创建加密的 PDF 文件"""
        doc = fitz.open()

        # 设置元数据
        metadata = {"title": "Encrypted Document", "author": "Test Author"}
        doc.set_metadata(metadata)

        # 添加页面
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "Encrypted Content", fontsize=12)

        # 保存到临时文件（加密）
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        owner_pwd = "owner123"
        user_pwd = "user123"
        doc.save(temp_file.name, encryption=fitz.PDF_ENCRYPT_AES_256,
                 owner_pw=owner_pwd, user_pw=user_pwd)
        doc.close()

        yield temp_file.name

        # 清理
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    # ========== 基本功能测试 ==========

    def test_plugin_is_available(self, plugin):
        """测试插件是否可用"""
        assert plugin.is_available()

    def test_plugin_metadata(self, plugin):
        """测试插件元数据"""
        assert plugin.name == "metadata_reader"
        assert plugin.version == "1.0.0"
        assert plugin.description
        assert plugin.author == "李开发"

    def test_read_metadata(self, plugin, sample_pdf_path):
        """测试读取元数据"""
        result = plugin.read(sample_pdf_path)

        assert result["success"] is True
        assert "metadata" in result
        assert "basic_metadata" in result
        assert "document_stats" in result
        assert "pdf_properties" in result

    def test_get_basic_metadata(self, plugin, sample_pdf_path):
        """测试获取基本元数据"""
        doc = plugin.pdf_engine.open(sample_pdf_path)
        metadata = plugin.get_basic_metadata(doc)

        assert "title" in metadata
        assert "author" in metadata
        assert "subject" in metadata
        assert "keywords" in metadata
        assert "created" in metadata
        assert "modified" in metadata

        assert metadata["title"] == "Test Document"
        assert metadata["author"] == "Test Author"
        assert metadata["subject"] == "Test Subject"
        assert isinstance(metadata["keywords"], list)
        assert len(metadata["keywords"]) == 3

        plugin.pdf_engine.close(doc)

    def test_get_document_stats(self, plugin, sample_pdf_path):
        """测试获取文档统计"""
        doc = plugin.pdf_engine.open(sample_pdf_path)
        stats = plugin.get_document_stats(doc)

        assert "page_count" in stats
        assert "total_words" in stats
        assert "total_chars" in stats
        assert "total_images" in stats
        assert "average_words_per_page" in stats

        assert stats["page_count"] == 3
        assert stats["total_words"] > 0
        assert stats["total_chars"] > 0
        assert stats["average_words_per_page"] > 0

        plugin.pdf_engine.close(doc)

    def test_get_pdf_properties(self, plugin, sample_pdf_path):
        """测试获取 PDF 特性"""
        doc = plugin.pdf_engine.open(sample_pdf_path)
        properties = plugin.get_pdf_properties(doc)

        assert "pdf_version" in properties
        assert "is_encrypted" in properties
        assert "is_editable" in properties
        assert "permissions" in properties

        assert properties["is_encrypted"] is False
        assert properties["is_editable"] is True

        plugin.pdf_engine.close(doc)

    def test_is_encrypted(self, plugin, sample_pdf_path):
        """测试检查加密状态"""
        doc = plugin.pdf_engine.open(sample_pdf_path)

        is_encrypted = plugin.is_encrypted(doc)
        assert is_encrypted is False

        plugin.pdf_engine.close(doc)

    def test_normalize_metadata(self, plugin):
        """测试元数据规范化"""
        metadata = {
            "title": "  Test Title  ",
            "author": "Test Author",
            "keywords": ["  keyword1  ", "keyword2", "  "],
            "empty_field": "",
            "none_field": None,
        }

        normalized = plugin.normalize_metadata(metadata)

        assert normalized["title"] == "Test Title"
        assert normalized["author"] == "Test Author"
        assert normalized["keywords"] == ["keyword1", "keyword2"]
        assert "empty_field" not in normalized
        assert "none_field" not in normalized

    # ========== 错误处理测试 ==========

    def test_file_not_found(self, plugin):
        """测试文件不存在"""
        result = plugin.read("/nonexistent/path/to/file.pdf")

        assert result["success"] is False
        assert result["error"]
        assert "not found" in result["error"].lower()

    def test_invalid_file_format(self, plugin):
        """测试无效文件格式"""
        # 创建一个非 PDF 文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
        temp_file.write(b"This is not a PDF file")
        temp_file.close()

        result = plugin.read(temp_file.name)

        assert result["success"] is False
        assert result["error"]
        assert "not a pdf" in result["error"].lower()

        # 清理
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    def test_encrypted_pdf_reject(self, plugin, encrypted_pdf_path):
        """测试加密 PDF 被拒绝"""
        result = plugin.read(encrypted_pdf_path)

        assert result["success"] is False
        assert result["error"]
        assert "encrypted" in result["error"].lower()

    # ========== 验证功能测试 ==========

    def test_validate_valid_pdf(self, plugin, sample_pdf_path):
        """测试验证有效的 PDF 文件"""
        is_valid, error_msg = plugin.validate(sample_pdf_path)

        assert is_valid is True
        assert error_msg is None

    def test_validate_nonexistent_file(self, plugin):
        """测试验证不存在的文件"""
        is_valid, error_msg = plugin.validate("/nonexistent/file.pdf")

        assert is_valid is False
        assert error_msg
        assert "not found" in error_msg.lower()

    def test_validate_non_pdf_file(self, plugin):
        """测试验证非 PDF 文件"""
        temp_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
        temp_file.write(b"Not a PDF")
        temp_file.close()

        is_valid, error_msg = plugin.validate(temp_file.name)

        assert is_valid is False
        assert error_msg
        assert "not a pdf" in error_msg.lower()

        # 清理
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    # ========== 输入输出验证测试 ==========

    def test_validate_input_valid(self, plugin, sample_pdf_path):
        """测试验证有效输入"""
        assert plugin.validate_input(pdf_path=sample_pdf_path) is True

    def test_validate_input_missing_pdf_path(self, plugin):
        """测试验证缺少 pdf_path"""
        assert plugin.validate_input() is False

    def test_validate_input_invalid_type(self, plugin):
        """测试验证无效类型"""
        assert plugin.validate_input(pdf_path=123) is False

    def test_validate_output_valid(self, plugin):
        """测试验证有效输出"""
        result = {
            "success": True,
            "metadata": {},
            "basic_metadata": {},
            "document_stats": {},
            "pdf_properties": {},
            "error": None,
        }
        assert plugin.validate_output(result) is True

    def test_validate_output_invalid(self, plugin):
        """测试验证无效输出"""
        result = {
            "success": True,
            "metadata": {},
        }
        assert plugin.validate_output(result) is False

    # ========== 复杂文档测试 ==========

    def test_complex_pdf_metadata(self, plugin, complex_pdf_path):
        """测试复杂 PDF 元数据"""
        doc = plugin.pdf_engine.open(complex_pdf_path)
        metadata = plugin.get_metadata(doc)

        assert metadata["title"] == "Complex Document with Images"
        assert metadata["author"] == "Complex Author"
        assert len(metadata["keywords"]) > 0

        plugin.pdf_engine.close(doc)

    def test_complex_pdf_stats(self, plugin, complex_pdf_path):
        """测试复杂 PDF 统计"""
        doc = plugin.pdf_engine.open(complex_pdf_path)
        stats = plugin.get_document_stats(doc)

        assert stats["page_count"] == 11  # 1 initial + 10 added
        assert stats["total_words"] > 0
        assert stats["average_words_per_page"] > 0

        plugin.pdf_engine.close(doc)

    # ========== 参数选项测试 ==========

    def test_include_stats_false(self, plugin, sample_pdf_path):
        """测试不包含文档统计"""
        result = plugin.read(sample_pdf_path, include_stats=False)

        assert result["success"] is True
        assert result["document_stats"] == {}

    def test_include_properties_false(self, plugin, sample_pdf_path):
        """测试不包含 PDF 特性"""
        result = plugin.read(sample_pdf_path, include_properties=False)

        assert result["success"] is True
        assert result["pdf_properties"] == {}

    def test_normalize_false(self, plugin, sample_pdf_path):
        """测试不规范化元数据"""
        result = plugin.read(sample_pdf_path, normalize=False)

        assert result["success"] is True
        # 元数据可能包含空字符串
        assert "metadata" in result

    # ========== 辅助方法测试 ==========

    def test_parse_keywords_comma(self, plugin):
        """测试解析逗号分隔的关键词"""
        keywords = plugin._parse_keywords("keyword1,keyword2,keyword3")
        assert keywords == ["keyword1", "keyword2", "keyword3"]

    def test_parse_keywords_semicolon(self, plugin):
        """测试解析分号分隔的关键词"""
        keywords = plugin._parse_keywords("keyword1;keyword2;keyword3")
        assert keywords == ["keyword1", "keyword2", "keyword3"]

    def test_parse_keywords_chinese(self, plugin):
        """测试解析中文分隔符"""
        keywords = plugin._parse_keywords("关键词1，关键词2；关键词3")
        assert keywords == ["关键词1", "关键词2", "关键词3"]

    def test_parse_keywords_empty(self, plugin):
        """测试解析空关键词"""
        keywords = plugin._parse_keywords("")
        assert keywords == []

    def test_parse_keywords_with_spaces(self, plugin):
        """测试解析带空格的关键词"""
        keywords = plugin._parse_keywords("  keyword1  ,  keyword2  ")
        assert keywords == ["keyword1", "keyword2"]

    def test_parse_pdf_date_valid(self, plugin):
        """测试解析有效的 PDF 日期"""
        date_str = "D:20260303191100"
        date = plugin._parse_pdf_date(date_str)

        assert date is not None
        assert "2026-03-03" in date
        assert "19:11:00" in date

    def test_parse_pdf_date_empty(self, plugin):
        """测试解析空日期"""
        date = plugin._parse_pdf_date("")
        assert date is None

    def test_parse_pdf_date_invalid(self, plugin):
        """测试解析无效日期"""
        date = plugin._parse_pdf_date("invalid")
        assert date is None

    # ========== 依赖检查测试 ==========

    def test_check_dependencies(self, plugin):
        """测试依赖检查"""
        deps_ok, missing_deps = plugin.check_dependencies()

        # PyMuPDF 应该已经安装
        assert deps_ok is True
        assert len(missing_deps) == 0

    # ========== 帮助信息测试 ==========

    def test_get_help(self, plugin):
        """测试获取帮助信息"""
        help_text = plugin.get_help()
        assert help_text
        assert plugin.name in help_text
        assert plugin.description in help_text

    def test_get_plugin_metadata(self, plugin):
        """测试获取插件元数据"""
        # 测试基础插件类的 get_metadata 方法（使用 super()）
        metadata = super(type(plugin), plugin).get_metadata()

        assert metadata["name"] == plugin.name
        assert metadata["version"] == plugin.version
        assert metadata["description"] == plugin.description
        assert metadata["plugin_type"] == plugin.plugin_type.value
        assert metadata["author"] == plugin.author

    # ========== 性能测试 ==========

    def test_large_pdf_performance(self, plugin, complex_pdf_path):
        """测试大文件处理性能"""
        import time

        start_time = time.time()
        result = plugin.read(complex_pdf_path)
        elapsed_time = time.time() - start_time

        assert result["success"] is True
        assert result["document_stats"]["page_count"] == 11
        # 应该在合理时间内完成（例如 2 秒内）
        assert elapsed_time < 2.0

    def test_metadata_extraction_performance(self, plugin, complex_pdf_path):
        """测试元数据提取性能"""
        import time

        doc = plugin.pdf_engine.open(complex_pdf_path)

        start_time = time.time()
        metadata = plugin.get_metadata(doc)
        elapsed_time = time.time() - start_time

        assert metadata["title"]
        assert metadata["page_count"] == 11
        # 元数据提取应该很快（< 0.1 秒）
        assert elapsed_time < 0.1

        plugin.pdf_engine.close(doc)

    def test_stats_extraction_performance(self, plugin, complex_pdf_path):
        """测试统计提取性能"""
        import time

        doc = plugin.pdf_engine.open(complex_pdf_path)

        start_time = time.time()
        stats = plugin.get_document_stats(doc)
        elapsed_time = time.time() - start_time

        assert stats["page_count"] == 11
        # 统计提取应该很快（< 1 秒）
        assert elapsed_time < 1.0

        plugin.pdf_engine.close(doc)

    # ========== 边界情况测试 ==========

    def test_empty_metadata_pdf(self, plugin):
        """测试没有元数据的 PDF"""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "Content", fontsize=12)

        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc.save(temp_file.name)
        doc.close()

        try:
            result = plugin.read(temp_file.name)

            assert result["success"] is True
            # 基本元数据应该有字段（即使为空或被规范化过滤掉）
            # 当 normalize=True 时，空字符串会被过滤掉
            assert isinstance(result["basic_metadata"], dict)

            # 测试不规范化时的情况
            result_no_normalize = plugin.read(temp_file.name, normalize=False)
            assert "title" in result_no_normalize["basic_metadata"]
            assert "author" in result_no_normalize["basic_metadata"]
        finally:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)

    def test_single_page_pdf(self, plugin):
        """测试单页 PDF"""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "Single Page", fontsize=12)

        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc.save(temp_file.name)
        doc.close()

        try:
            doc = plugin.pdf_engine.open(temp_file.name)
            stats = plugin.get_document_stats(doc)

            assert stats["page_count"] == 1
            assert stats["average_words_per_page"] > 0

            plugin.pdf_engine.close(doc)
        finally:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)
