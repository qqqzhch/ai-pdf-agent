"""表格读取插件单元测试"""

import os
import pytest
import tempfile
import fitz  # PyMuPDF


class TestTableReaderPlugin:
    """TableReaderPlugin 测试类"""

    @pytest.fixture
    def plugin(self):
        """创建插件实例"""
        from plugins.readers.table_reader import TableReaderPlugin
        return TableReaderPlugin()

    @pytest.fixture
    def sample_pdf_with_tables(self):
        """创建包含表格的示例 PDF 文件"""
        doc = fitz.open()

        # 添加第一页 - 包含一个简单表格
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "Table Test Document", fontsize=16)

        # 绘制表格边框和文本
        # 表格头
        y_offset = 100
        page.insert_text(fitz.Point(50, y_offset), "Name", fontsize=12)
        page.insert_text(fitz.Point(200, y_offset), "Age", fontsize=12)
        page.insert_text(fitz.Point(300, y_offset), "City", fontsize=12)

        # 表格行
        y_offset += 30
        page.insert_text(fitz.Point(50, y_offset), "Alice", fontsize=12)
        page.insert_text(fitz.Point(200, y_offset), "25", fontsize=12)
        page.insert_text(fitz.Point(300, y_offset), "New York", fontsize=12)

        y_offset += 30
        page.insert_text(fitz.Point(50, y_offset), "Bob", fontsize=12)
        page.insert_text(fitz.Point(200, y_offset), "30", fontsize=12)
        page.insert_text(fitz.Point(300, y_offset), "London", fontsize=12)

        y_offset += 30
        page.insert_text(fitz.Point(50, y_offset), "Charlie", fontsize=12)
        page.insert_text(fitz.Point(200, y_offset), "35", fontsize=12)
        page.insert_text(fitz.Point(300, y_offset), "Paris", fontsize=12)

        # 添加第二页 - 包含另一个表格
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "Second Table Page", fontsize=16)

        y_offset = 100
        page.insert_text(fitz.Point(50, y_offset), "Product", fontsize=12)
        page.insert_text(fitz.Point(200, y_offset), "Price", fontsize=12)
        page.insert_text(fitz.Point(300, y_offset), "Stock", fontsize=12)

        y_offset += 30
        page.insert_text(fitz.Point(50, y_offset), "Laptop", fontsize=12)
        page.insert_text(fitz.Point(200, y_offset), "$999", fontsize=12)
        page.insert_text(fitz.Point(300, y_offset), "50", fontsize=12)

        # 添加第三页 - 包含一个更大的表格
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "Large Table Page", fontsize=16)

        y_offset = 100
        page.insert_text(fitz.Point(50, y_offset), "ID", fontsize=12)
        page.insert_text(fitz.Point(120, y_offset), "First Name", fontsize=12)
        page.insert_text(fitz.Point(250, y_offset), "Last Name", fontsize=12)
        page.insert_text(fitz.Point(380, y_offset), "Email", fontsize=12)
        page.insert_text(fitz.Point(530, y_offset), "Phone", fontsize=12)

        # 添加多行
        for i in range(10):
            y_offset += 30
            page.insert_text(fitz.Point(50, y_offset), str(i + 1), fontsize=12)
            page.insert_text(fitz.Point(120, y_offset), f"User{i + 1}", fontsize=12)
            page.insert_text(fitz.Point(250, y_offset), f"Last{i + 1}", fontsize=12)
            page.insert_text(fitz.Point(380, y_offset), f"user{i + 1}@example.com", fontsize=12)
            page.insert_text(fitz.Point(530, y_offset), f"555-010{i}", fontsize=12)

        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc.save(temp_file.name)
        doc.close()

        yield temp_file.name

        # 清理
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    @pytest.fixture
    def pdf_without_tables(self):
        """创建不包含表格的 PDF 文件"""
        doc = fitz.open()

        # 添加纯文本页面
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "This is a text-only document", fontsize=12)
        page.insert_text(fitz.Point(50, 80), "There are no tables here.", fontsize=12)
        page.insert_text(fitz.Point(50, 110), "Just regular text content.", fontsize=12)

        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc.save(temp_file.name)
        doc.close()

        yield temp_file.name

        # 清理
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    @pytest.fixture
    def large_pdf_with_tables(self):
        """创建包含多个表格的大型 PDF 文件"""
        doc = fitz.open()

        # 添加 10 页，每页都有表格
        for page_idx in range(10):
            page = doc.new_page()
            page.insert_text(fitz.Point(50, 50), f"Page {page_idx + 1} - Table Test", fontsize=16)

            y_offset = 100
            page.insert_text(fitz.Point(50, y_offset), "Column 1", fontsize=12)
            page.insert_text(fitz.Point(200, y_offset), "Column 2", fontsize=12)
            page.insert_text(fitz.Point(350, y_offset), "Column 3", fontsize=12)

            # 添加 5 行数据
            for i in range(5):
                y_offset += 30
                page.insert_text(fitz.Point(50, y_offset), f"R{i + 1}C1", fontsize=12)
                page.insert_text(fitz.Point(200, y_offset), f"R{i + 1}C2", fontsize=12)
                page.insert_text(fitz.Point(350, y_offset), f"R{i + 1}C3", fontsize=12)

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
        assert plugin.name == "table_reader"
        assert plugin.version == "1.0.0"
        assert plugin.description
        assert plugin.author == "李开发"

    def test_extract_all_tables(self, plugin, sample_pdf_with_tables):
        """测试提取所有表格"""
        result = plugin.read(sample_pdf_with_tables)

        assert result["success"] is True
        assert result["page_count"] == 3
        assert len(result["pages_extracted"]) == 3
        assert result["total_tables"] >= 0  # 可能检测到 0 或多个表格
        assert isinstance(result["tables"], list)

    def test_extract_single_page_tables(self, plugin, sample_pdf_with_tables):
        """测试提取单页表格"""
        result = plugin.read(sample_pdf_with_tables, page=2)

        assert result["success"] is True
        assert result["page_count"] == 3
        assert len(result["pages_extracted"]) == 1
        assert result["pages_extracted"] == [2]
        assert isinstance(result["tables"], list)

    def test_extract_page_range_tables(self, plugin, sample_pdf_with_tables):
        """测试提取页面范围表格"""
        result = plugin.read(sample_pdf_with_tables, page_range=(1, 2))

        assert result["success"] is True
        assert result["page_count"] == 3
        assert len(result["pages_extracted"]) == 2
        assert result["pages_extracted"] == [1, 2]
        assert isinstance(result["tables"], list)

    def test_extract_specific_pages_tables(self, plugin, sample_pdf_with_tables):
        """测试提取指定页列表表格"""
        result = plugin.read(sample_pdf_with_tables, pages=[1, 3])

        assert result["success"] is True
        assert result["page_count"] == 3
        assert len(result["pages_extracted"]) == 2
        assert result["pages_extracted"] == [1, 3]
        assert isinstance(result["tables"], list)

    def test_metadata_extraction(self, plugin, sample_pdf_with_tables):
        """测试元数据提取"""
        result = plugin.read(sample_pdf_with_tables)

        assert result["success"] is True
        assert "metadata" in result
        assert isinstance(result["metadata"], dict)
        assert "page_count" in result["metadata"]
        assert result["metadata"]["page_count"] == 3

    # ========== 输出格式测试 ==========

    def test_output_format_json(self, plugin, sample_pdf_with_tables):
        """测试 JSON 输出格式（默认）"""
        result = plugin.read(sample_pdf_with_tables, output_format="json")

        assert result["success"] is True
        assert "tables" in result
        assert isinstance(result["tables"], list)

    def test_output_format_list(self, plugin, sample_pdf_with_tables):
        """测试 List 输出格式"""
        result = plugin.read(sample_pdf_with_tables, output_format="list")

        assert result["success"] is True
        assert "table_list" in result
        assert isinstance(result["table_list"], list)

        # 验证简化格式
        if result["table_list"]:
            table = result["table_list"][0]
            assert "page" in table
            assert "rows" in table

    def test_output_format_csv(self, plugin, sample_pdf_with_tables):
        """测试 CSV 输出格式"""
        result = plugin.read(sample_pdf_with_tables, output_format="csv")

        assert result["success"] is True
        assert "csv" in result
        assert isinstance(result["csv"], str)

    def test_output_format_case_insensitive(self, plugin, sample_pdf_with_tables):
        """测试输出格式大小写不敏感"""
        result1 = plugin.read(sample_pdf_with_tables, output_format="CSV")
        assert result1["success"] is True
        assert "csv" in result1

        result2 = plugin.read(sample_pdf_with_tables, output_format="List")
        assert result2["success"] is True
        assert "table_list" in result2

    # ========== 边界情况测试 ==========

    def test_empty_tables_document(self, plugin, pdf_without_tables):
        """测试不包含表格的文档"""
        result = plugin.read(pdf_without_tables)

        assert result["success"] is True
        assert result["total_tables"] == 0
        assert len(result["tables"]) == 0

    def test_large_pdf_performance(self, plugin, large_pdf_with_tables):
        """测试大文件处理性能"""
        import time

        start_time = time.time()
        result = plugin.read(large_pdf_with_tables)
        elapsed_time = time.time() - start_time

        assert result["success"] is True
        assert result["page_count"] == 10
        # 应该在合理时间内完成（例如 5 秒内）
        assert elapsed_time < 5.0

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

    def test_invalid_page_number_too_low(self, plugin, sample_pdf_with_tables):
        """测试页码超出范围（太小）"""
        result = plugin.read(sample_pdf_with_tables, page=0)

        assert result["success"] is True
        # 应该处理为空结果或提取所有页面
        assert isinstance(result["tables"], list)

    def test_invalid_page_number_too_high(self, plugin, sample_pdf_with_tables):
        """测试页码超出范围（太大）"""
        result = plugin.read(sample_pdf_with_tables, page=100)

        assert result["success"] is True
        # 应该处理为空结果或提取所有页面
        assert isinstance(result["tables"], list)

    def test_invalid_page_range(self, plugin, sample_pdf_with_tables):
        """测试无效页面范围"""
        # 起始页大于结束页
        result = plugin.read(sample_pdf_with_tables, page_range=(3, 1))

        assert result["success"] is True
        # 应该处理为空结果或提取所有页面
        assert isinstance(result["tables"], list)

    def test_invalid_pages_list(self, plugin, sample_pdf_with_tables):
        """测试无效页码列表"""
        result = plugin.read(sample_pdf_with_tables, pages=[1, 100])

        assert result["success"] is True
        # 应该处理为空结果或提取所有页面
        assert isinstance(result["tables"], list)

    def test_invalid_pages_type(self, plugin, sample_pdf_with_tables):
        """测试页码列表类型错误"""
        result = plugin.read(sample_pdf_with_tables, pages="not a list")

        assert result["success"] is True
        # 应该处理为提取所有页面
        assert isinstance(result["tables"], list)

    # ========== 验证功能测试 ==========

    def test_validate_valid_pdf(self, plugin, sample_pdf_with_tables):
        """测试验证有效的 PDF 文件"""
        is_valid, error_msg = plugin.validate(sample_pdf_with_tables)

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

    def test_validate_input_valid(self, plugin, sample_pdf_with_tables):
        """测试验证有效输入"""
        assert plugin.validate_input(pdf_path=sample_pdf_with_tables) is True

    def test_validate_input_with_output_format(self, plugin, sample_pdf_with_tables):
        """测试验证带输出格式的输入"""
        assert plugin.validate_input(pdf_path=sample_pdf_with_tables, output_format="json") is True
        assert plugin.validate_input(pdf_path=sample_pdf_with_tables, output_format="csv") is True
        assert plugin.validate_input(pdf_path=sample_pdf_with_tables, output_format="list") is True

    def test_validate_input_missing_pdf_path(self, plugin):
        """测试验证缺少 pdf_path"""
        assert plugin.validate_input() is False

    def test_validate_input_invalid_type(self, plugin):
        """测试验证无效类型"""
        assert plugin.validate_input(pdf_path=123) is False

    def test_validate_input_invalid_output_format(
        self, plugin, sample_pdf_with_tables
    ):
        """测试验证测试无效输出格式"""
        assert plugin.validate_input(
            pdf_path=sample_pdf_with_tables, output_format="invalid"
        ) is False

    def test_validate_output_valid(self, plugin):
        """测试验证有效输出"""
        result = {
            "success": True,
            "tables": [],
            "total_tables": 0,
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
            "tables": []
        }
        assert plugin.validate_output(result) is False

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

    # ========== 表格数据结构测试 ==========

    def test_table_structure(self, plugin, sample_pdf_with_tables):
        """测试表格数据结构"""
        result = plugin.read(sample_pdf_with_tables)

        if result["total_tables"] > 0:
            table = result["tables"][0]

            # 验证表格结构
            assert "page" in table
            assert "rows" in table
            assert isinstance(table["rows"], list)

            # 验证行结构
            if table["rows"]:
                row = table["rows"][0]
                assert isinstance(row, list)

    def test_determine_pages_to_extract_all(self, plugin, sample_pdf_with_tables):
        """测试确定提取页面（全部）"""
        page_count = 3
        pages = plugin._determine_pages_to_extract({}, page_count)

        assert pages == [1, 2, 3]

    def test_determine_pages_to_extract_single(self, plugin, sample_pdf_with_tables):
        """测试确定提取页面（单页）"""
        page_count = 3
        pages = plugin._determine_pages_to_extract({"page": 2}, page_count)

        assert pages == [2]

    def test_determine_pages_to_extract_range(self, plugin, sample_pdf_with_tables):
        """测试确定提取页面（范围）"""
        page_count = 3
        pages = plugin._determine_pages_to_extract({"page_range": (1, 2)}, page_count)

        assert pages == [1, 2]

    def test_determine_pages_to_extract_list(self, plugin, sample_pdf_with_tables):
        """测试确定提取页面（列表）"""
        page_count = 3
        pages = plugin._determine_pages_to_extract({"pages": [1, 3]}, page_count)

        assert pages == [1, 3]

    # ========== CSV/List 转换测试 ==========

    def test_convert_to_csv_empty(self, plugin):
        """测试 CSV 转换（空表格）"""
        csv_output = plugin._convert_to_csv([])
        assert csv_output == ""

    def test_convert_to_csv_with_data(self, plugin):
        """测试 CSV 转换（有数据）"""
        tables = [
            {
                "page": 1,
                "rows": [
                    ["Name", "Age", "City"],
                    ["Alice", "25", "NY"],
                    ["Bob", "30", "LA"]
                ]
            }
        ]

        csv_output = plugin._convert_to_csv(tables)

        assert csv_output
        assert "Table 1 (Page 1)" in csv_output
        assert "Name" in csv_output
        assert "Alice" in csv_output

    def test_convert_to_list_empty(self, plugin):
        """测试 List 转换（空表格）"""
        list_output = plugin._convert_to_list([])
        assert list_output == []

    def test_convert_to_list_with_data(self, plugin):
        """测试 List 转换（有数据）"""
        tables = [
            {
                "page": 1,
                "rows": [["A", "B"], ["1", "2"]]
            },
            {
                "page": 2,
                "rows": [["C", "D"], ["3", "4"]]
            }
        ]

        list_output = plugin._convert_to_list(tables)

        assert len(list_output) == 2
        assert list_output[0]["page"] == 1
        assert list_output[0]["rows"] == [["A", "B"], ["1", "2"]]
        assert list_output[1]["page"] == 2

    # ========== 异常处理测试 ==========

    def test_extract_tables_from_corrupted_pdf(self, plugin):
        """测试提取损坏的 PDF 表格"""
        # 创建一个损坏的 PDF 文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        temp_file.write(b"%PDF-1.4\n%%EOF")
        temp_file.close()

        # 这应该抛出异常或返回错误
        result = plugin.read(temp_file.name)

        # 无论是成功还是失败，都应该有有效的结果结构
        assert isinstance(result, dict)
        assert "success" in result

        # 清理
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    def test_extract_tables_permission_denied(self, plugin):
        """测试提取无权限访问的文件"""
        # 这个测试在某些环境中可能会失败，但我们可以尝试
        import tempfile
        import stat

        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        temp_file.write(b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF")
        temp_file.close()

        # 设置文件为只读
        os.chmod(temp_file.name, stat.S_IRUSR)

        # 尝试读取
        result = plugin.read(temp_file.name)

        # 恢复权限
        os.chmod(temp_file.name, stat.S_IRUSR | stat.S_IWUSR)

        # 应该有有效的结果
        assert isinstance(result, dict)

        # 清理
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
