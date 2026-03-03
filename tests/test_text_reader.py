"""文本读取插件单元测试"""

import os
import pytest
import tempfile
import fitz  # PyMuPDF

from plugins.readers.text_reader import TextReaderPlugin


class TestTextReaderPlugin:
    """TextReaderPlugin 测试类"""
    
    @pytest.fixture
    def plugin(self):
        """创建插件实例"""
        return TextReaderPlugin()
    
    @pytest.fixture
    def sample_pdf_path(self):
        """创建示例 PDF 文件"""
        # 创建临时 PDF 文件
        doc = fitz.open()
        
        # 添加第一页
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "First Page Content", fontsize=12)
        page.insert_text(fitz.Point(50, 80), "This is the first page of the test PDF.", fontsize=12)
        
        # 添加第二页
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "Second Page Content", fontsize=12)
        page.insert_text(fitz.Point(50, 80), "This is the second page of the test PDF.", fontsize=12)
        
        # 添加第三页
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "Third Page Content", fontsize=12)
        page.insert_text(fitz.Point(50, 80), "This is the third page of the test PDF.", fontsize=12)
        
        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc.save(temp_file.name)
        doc.close()
        
        yield temp_file.name
        
        # 清理
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
    
    @pytest.fixture
    def large_pdf_path(self):
        """创建大型 PDF 文件（用于性能测试）"""
        doc = fitz.open()
        
        # 添加 100 页
        for i in range(100):
            page = doc.new_page()
            page.insert_text(
                fitz.Point(50, 50), 
                f"Page {i + 1} Content", 
                fontsize=12
            )
            page.insert_text(
                fitz.Point(50, 80), 
                f"This is page {i + 1} of the test PDF with some additional text.",
                fontsize=12
            )
            # 添加更多文本以增加文件大小
            for j in range(5):
                page.insert_text(
                    fitz.Point(50, 110 + j * 30),
                    f"Line {j + 1} on page {i + 1} with some sample text content.",
                    fontsize=10
                )
        
        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc.save(temp_file.name)
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
        assert plugin.name == "text_reader"
        assert plugin.version == "1.0.0"
        assert plugin.description
        assert plugin.author == "李开发"
    
    def test_extract_all_text(self, plugin, sample_pdf_path):
        """测试提取所有文本"""
        result = plugin.read(sample_pdf_path)
        
        assert result["success"] is True
        assert result["content"]
        assert result["page_count"] == 3
        assert len(result["pages_extracted"]) == 3
        assert result["pages_extracted"] == [1, 2, 3]
        assert "First Page Content" in result["content"]
        assert "Second Page Content" in result["content"]
        assert "Third Page Content" in result["content"]
    
    def test_extract_single_page(self, plugin, sample_pdf_path):
        """测试提取单页文本"""
        result = plugin.read(sample_pdf_path, page=2)
        
        assert result["success"] is True
        assert result["content"]
        assert result["page_count"] == 3
        assert len(result["pages_extracted"]) == 1
        assert result["pages_extracted"] == [2]
        assert "Second Page Content" in result["content"]
        assert "First Page Content" not in result["content"]
    
    def test_extract_page_range(self, plugin, sample_pdf_path):
        """测试提取页面范围"""
        result = plugin.read(sample_pdf_path, page_range=(1, 2))
        
        assert result["success"] is True
        assert result["content"]
        assert result["page_count"] == 3
        assert len(result["pages_extracted"]) == 2
        assert result["pages_extracted"] == [1, 2]
        assert "First Page Content" in result["content"]
        assert "Second Page Content" in result["content"]
        assert "Third Page Content" not in result["content"]
    
    def test_extract_specific_pages(self, plugin, sample_pdf_path):
        """测试提取指定页列表"""
        result = plugin.read(sample_pdf_path, pages=[1, 3])
        
        assert result["success"] is True
        assert result["content"]
        assert result["page_count"] == 3
        assert len(result["pages_extracted"]) == 2
        assert result["pages_extracted"] == [1, 3]
        assert "First Page Content" in result["content"]
        assert "Third Page Content" in result["content"]
        assert "Second Page Content" not in result["content"]
    
    def test_metadata_extraction(self, plugin, sample_pdf_path):
        """测试元数据提取"""
        result = plugin.read(sample_pdf_path)
        
        assert result["success"] is True
        assert "metadata" in result
        assert isinstance(result["metadata"], dict)
        assert "page_count" in result["metadata"]
        assert result["metadata"]["page_count"] == 3
    
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
    
    def test_invalid_page_number_too_low(self, plugin, sample_pdf_path):
        """测试页码超出范围（太小）"""
        result = plugin.read(sample_pdf_path, page=0)
        
        assert result["success"] is False
        assert result["error"]
        assert "invalid page number" in result["error"].lower()
    
    def test_invalid_page_number_too_high(self, plugin, sample_pdf_path):
        """测试页码超出范围（太大）"""
        result = plugin.read(sample_pdf_path, page=100)
        
        assert result["success"] is False
        assert result["error"]
        assert "invalid page number" in result["error"].lower()
    
    def test_invalid_page_range(self, plugin, sample_pdf_path):
        """测试无效页面范围"""
        # 起始页大于结束页
        result = plugin.read(sample_pdf_path, page_range=(3, 1))
        
        assert result["success"] is False
        assert result["error"]
        assert "invalid page_range" in result["error"].lower()
    
    def test_invalid_page_range_out_of_bounds(self, plugin, sample_pdf_path):
        """测试页面范围超出边界"""
        result = plugin.read(sample_pdf_path, page_range=(1, 100))
        
        assert result["success"] is False
        assert result["error"]
        assert "invalid page_range" in result["error"].lower()
    
    def test_invalid_pages_list(self, plugin, sample_pdf_path):
        """测试无效页码列表"""
        result = plugin.read(sample_pdf_path, pages=[1, 100])
        
        assert result["success"] is False
        assert result["error"]
        assert "invalid page number" in result["error"].lower()
    
    def test_invalid_pages_type(self, plugin, sample_pdf_path):
        """测试页码列表类型错误"""
        result = plugin.read(sample_pdf_path, pages="not a list")
        
        assert result["success"] is False
        assert result["error"]
        assert "invalid pages" in result["error"].lower()
    
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
            "content": "test",
            "metadata": {},
            "page_count": 1,
            "pages_extracted": [1],
            "error": None
        }
        assert plugin.validate_output(result) is True
    
    def test_validate_output_invalid(self, plugin):
        """测试验证无效输出"""
        result = {
            "success": True,
            "content": "test"
        }
        assert plugin.validate_output(result) is False
    
    # ========== 性能测试 ==========
    
    def test_large_file_performance(self, plugin, large_pdf_path):
        """测试大文件处理性能"""
        import time
        
        start_time = time.time()
        result = plugin.read(large_pdf_path)
        elapsed_time = time.time() - start_time
        
        assert result["success"] is True
        assert result["page_count"] == 100
        # 应该在合理时间内完成（例如 5 秒内）
        assert elapsed_time < 5.0
    
    def test_large_file_page_extraction(self, plugin, large_pdf_path):
        """测试大文件分页提取性能"""
        import time
        
        start_time = time.time()
        result = plugin.read(large_pdf_path, pages=[10, 50, 90])
        elapsed_time = time.time() - start_time
        
        assert result["success"] is True
        assert len(result["pages_extracted"]) == 3
        assert elapsed_time < 1.0  # 分页提取应该很快
    
    def test_large_file_range_extraction(self, plugin, large_pdf_path):
        """测试大文件范围提取性能"""
        import time
        
        start_time = time.time()
        result = plugin.read(large_pdf_path, page_range=(20, 40))
        elapsed_time = time.time() - start_time
        
        assert result["success"] is True
        assert len(result["pages_extracted"]) == 21
        assert elapsed_time < 2.0  # 范围提取应该很快
    
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
    
    def test_get_metadata(self, plugin):
        """测试获取插件元数据"""
        metadata = plugin.get_metadata()
        
        assert metadata["name"] == plugin.name
        assert metadata["version"] == plugin.version
        assert metadata["description"] == plugin.description
        assert metadata["plugin_type"] == plugin.plugin_type.value
        assert metadata["author"] == plugin.author
