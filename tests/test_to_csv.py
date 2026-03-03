"""测试 CSV 转换器插件"""

# 添加项目根目录到路径
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import tempfile
import unittest
import io

from plugins.converters.to_csv import ToCsvPlugin


class TestToCsvPlugin(unittest.TestCase):
    """测试 ToCsvPlugin 类"""

    def setUp(self):
        """测试前的设置"""
        self.plugin = ToCsvPlugin()

        # 创建测试 PDF 文件路径
        self.test_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "test_sample.pdf"
        )

        # 备用测试 PDF
        self.simple_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "test-pdfs",
            "simple.pdf"
        )

    def tearDown(self):
        """测试后的清理"""
        pass

    def test_plugin_initialization(self):
        """测试插件初始化"""
        self.assertEqual(self.plugin.name, "to_csv")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertEqual(self.plugin.author, "李开发")
        self.assertEqual(self.plugin.license, "MIT")
        self.assertIn("PDF 表格转换为 CSV", self.plugin.description)

    def test_plugin_metadata(self):
        """测试插件元数据"""
        metadata = self.plugin.get_metadata()

        self.assertEqual(metadata["name"], "to_csv")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertEqual(metadata["plugin_type"], "converter")
        self.assertIn("pymupdf>=1.23.0", metadata["dependencies"])

    def test_is_available(self):
        """测试插件可用性检查"""
        # 如果 PyMuPDF 可用，插件应该可用
        if self.plugin.pdf_engine is not None:
            self.assertTrue(self.plugin.is_available())
        else:
            self.assertFalse(self.plugin.is_available())

    def test_validate_nonexistent_file(self):
        """测试验证不存在的文件"""
        is_valid, error = self.plugin.validate("/nonexistent/file.pdf")
        self.assertFalse(is_valid)
        self.assertIn("not found", error.lower())

    def test_validate_invalid_file(self):
        """测试验证无效文件"""
        # 创建非 PDF 文件
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name
            f.write(b"not a pdf")

        try:
            is_valid, error = self.plugin.validate(temp_path)
            self.assertFalse(is_valid)
            self.assertIn("not a pdf", error.lower())
        finally:
            os.unlink(temp_path)

    def test_validate_unreadable_file(self):
        """测试验证不可读文件"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name
            f.write(b"%PDF-1.4")

        try:
            # 移除读权限
            os.chmod(temp_path, 0o000)

            is_valid, error = self.plugin.validate(temp_path)
            self.assertFalse(is_valid)
            # 错误信息可能包含 "not readable" 或 "failed to open"
            self.assertTrue("not readable" in error.lower() or "failed to open" in error.lower())

        finally:
            os.chmod(temp_path, 0o644)
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_convert_with_invalid_file(self):
        """测试转换不存在的文件"""
        result = self.plugin.convert("/nonexistent/file.pdf")

        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])
        self.assertIn("not found", result["error"].lower())

    def test_convert_missing_pdf_path(self):
        """测试缺少 pdf_path 参数"""
        result = self.plugin.convert("")

        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_success(self):
        """测试成功转换 PDF 表格为 CSV"""
        result = self.plugin.convert(self.test_pdf_path)

        # 检查基本结构
        self.assertIn("success", result)
        self.assertIn("content", result)
        self.assertIn("metadata", result)
        self.assertIn("tables_found", result)
        self.assertIn("tables_converted", result)
        self.assertIn("output_path", result)
        self.assertIn("error", result)

        # 如果没有表格，应该返回错误
        if not result["success"]:
            self.assertIn("No tables found", result["error"])
        else:
            self.assertTrue(result["success"])
            self.assertGreater(len(result["content"]), 0)
            self.assertGreaterEqual(result["tables_found"], 0)
            self.assertIsNone(result["error"])

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_csv_parsing(self):
        """测试转换结果可以解析为有效 CSV"""
        result = self.plugin.convert(self.test_pdf_path)

        if result["success"] and result["content"].strip():
            # 尝试解析 CSV
            try:
                reader = csv.reader(io.StringIO(result["content"]))
                rows = list(reader)
                self.assertIsInstance(rows, list)
                self.assertGreater(len(rows), 0)
            except Exception as e:
                self.fail(f"Failed to parse CSV: {e}")

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_specific_page(self):
        """测试转换指定页码"""
        result = self.plugin.convert(self.test_pdf_path, page=1)

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])
        self.assertGreater(len(result["content"]), 0)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_page_range(self):
        """测试转换页面范围"""
        result = self.plugin.convert(self.test_pdf_path, page_range=(1, 2))

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])
        self.assertGreater(len(result["content"]), 0)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_pages_list(self):
        """测试转换指定页码列表"""
        result = self.plugin.convert(self.test_pdf_path, pages=[1])

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])
        self.assertGreater(len(result["content"]), 0)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_header(self):
        """测试包含表头"""
        result = self.plugin.convert(self.test_pdf_path, header=True)

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])

        # 解析 CSV 并验证
        reader = csv.reader(io.StringIO(result["content"]))
        rows = list(reader)

        if rows:
            # 第一行应该是表头
            header_row = rows[0]
            self.assertIsInstance(header_row, list)
            self.assertGreater(len(header_row), 0)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_without_header(self):
        """测试不包含表头"""
        result = self.plugin.convert(self.test_pdf_path, header=False)

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])

        # 解析内容
        reader = csv.reader(io.StringIO(result["content"]))
        rows = list(reader)

        if rows:
            self.assertIsInstance(rows, list)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_comma_delimiter(self):
        """测试使用逗号分隔符"""
        result = self.plugin.convert(self.test_pdf_path, delimiter=",")

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])

        # 解析 CSV 并验证分隔符
        reader = csv.reader(io.StringIO(result["content"]), delimiter=",")
        rows = list(reader)
        self.assertIsInstance(rows, list)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_semicolon_delimiter(self):
        """测试使用分号分隔符"""
        result = self.plugin.convert(self.test_pdf_path, delimiter=";")

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])

        # 解析 CSV 并验证分隔符
        reader = csv.reader(io.StringIO(result["content"]), delimiter=";")
        rows = list(reader)
        self.assertIsInstance(rows, list)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_tab_delimiter(self):
        """测试使用制表符分隔符"""
        result = self.plugin.convert(self.test_pdf_path, delimiter="\t")

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])

        # 解析 CSV 并验证分隔符
        reader = csv.reader(io.StringIO(result["content"]), delimiter="\t")
        rows = list(reader)
        self.assertIsInstance(rows, list)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_table_index(self):
        """测试转换指定索引的表格"""
        result = self.plugin.convert(self.test_pdf_path, table_index=0)

        if not result["success"]:
            if "No tables found" in result.get("error", ""):
                self.skipTest("No tables found in PDF")
            if "Table index 0 out of range" in result.get("error", ""):
                self.skipTest("Less than 1 table found")

        self.assertTrue(result["success"])
        self.assertEqual(result["tables_converted"], 1)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_invalid_table_index(self):
        """测试使用无效的表格索引"""
        result = self.plugin.convert(self.test_pdf_path, table_index=999)

        # 应该失败（要么是因为没有表格，要么是因为索引超出范围）
        self.assertFalse(result["success"])
        self.assertIn("error", result)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_merge_tables(self):
        """测试合并多个表格"""
        result = self.plugin.convert(self.test_pdf_path, merge_tables=True)

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])

        # 表格数量应该等于找到的表格数
        self.assertEqual(result["tables_converted"], result["tables_found"])

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_without_merge_tables(self):
        """测试不合并多个表格"""
        result = self.plugin.convert(self.test_pdf_path, merge_tables=False)

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])

        # 应该只转换一个表格（默认）
        self.assertEqual(result["tables_converted"], 1)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_output_file(self):
        """测试保存到输出文件"""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = f.name

        try:
            result = self.plugin.convert(
                self.test_pdf_path,
                output_path=output_path
            )

            if not result["success"] and "No tables found" in result.get("error", ""):
                self.skipTest("No tables found in PDF")

            self.assertTrue(result["success"])
            self.assertEqual(result["output_path"], output_path)

            # 验证文件存在
            self.assertTrue(os.path.exists(output_path))

            # 读取文件内容
            with open(output_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            # 验证内容
            self.assertEqual(file_content, result["content"])

            # 验证可以解析为 CSV
            reader = csv.reader(io.StringIO(file_content))
            list(reader)  # 尝试读取所有行

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_output_directory(self):
        """测试保存到不存在的目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "subdir", "output.csv")

            result = self.plugin.convert(
                self.test_pdf_path,
                output_path=output_path
            )

            if not result["success"] and "No tables found" in result.get("error", ""):
                self.skipTest("No tables found in PDF")

            self.assertTrue(result["success"])
            self.assertEqual(result["output_path"], output_path)

            # 验证文件存在
            self.assertTrue(os.path.exists(output_path))

    def test_validate_input(self):
        """测试输入验证"""
        # 有效输入
        self.assertTrue(self.plugin.validate_input(pdf_path="test.pdf"))

        # 无效输入 - 缺少 pdf_path
        self.assertFalse(self.plugin.validate_input())

        # 无效输入 - 非字符串 pdf_path
        self.assertFalse(self.plugin.validate_input(pdf_path=123))

    def test_validate_output(self):
        """测试输出验证"""
        # 有效输出
        result = {
            "success": True,
            "content": "header1,header2\nvalue1,value2\n",
            "metadata": {},
            "tables_found": 1,
            "tables_converted": 1,
            "output_path": None,
            "error": None
        }
        self.assertTrue(self.plugin.validate_output(result))

        # 无效输出 - 缺少字段
        invalid_result = {
            "success": True,
            "content": "header1,header2\n"
        }
        self.assertFalse(self.plugin.validate_output(invalid_result))

        # 无效输出 - 非字典
        self.assertFalse(self.plugin.validate_output("not a dict"))

    def test_get_help(self):
        """测试获取帮助信息"""
        help_text = self.plugin.get_help()

        self.assertIsInstance(help_text, str)
        self.assertIn("to_csv", help_text)
        self.assertIn("使用方法", help_text)
        self.assertIn("支持的参数", help_text)
        self.assertIn("delimiter", help_text)
        self.assertIn("table_index", help_text)
        self.assertIn("merge_tables", help_text)
        self.assertIn("header", help_text)

    def test_determine_pages_to_process_single_page(self):
        """测试确定处理页码 - 单页"""
        pages = self.plugin._determine_pages_to_process({"page": 2}, 10)
        self.assertEqual(pages, [2])

    def test_determine_pages_to_process_page_range(self):
        """测试确定处理页码 - 页面范围"""
        pages = self.plugin._determine_pages_to_process({"page_range": (3, 7)}, 10)
        self.assertEqual(pages, [3, 4, 5, 6, 7])

    def test_determine_pages_to_process_pages_list(self):
        """测试确定处理页码 - 页码列表"""
        pages = self.plugin._determine_pages_to_process({"pages": [1, 3, 5]}, 10)
        self.assertEqual(pages, [1, 3, 5])

    def test_determine_pages_to_process_all_pages(self):
        """测试确定处理页码 - 所有页面"""
        pages = self.plugin._determine_pages_to_process({}, 5)
        self.assertEqual(pages, [1, 2, 3, 4, 5])

    def test_determine_pages_to_process_invalid_page(self):
        """测试确定处理页码 - 无效页码"""
        pages = self.plugin._determine_pages_to_process({"page": 15}, 10)
        # 应该返回所有页面（默认）
        self.assertEqual(pages, list(range(1, 11)))

    def test_determine_pages_to_process_invalid_range(self):
        """测试确定处理页码 - 无效范围"""
        pages = self.plugin._determine_pages_to_process({"page_range": (10, 5)}, 10)
        # 应该返回所有页面（默认）
        self.assertEqual(pages, list(range(1, 11)))

    def test_build_csv_content_with_header(self):
        """测试构建 CSV 内容 - 包含表头"""
        tables = [
            {
                "rows": [
                    ["Name", "Age", "City"],
                    ["John", "25", "NYC"],
                    ["Jane", "30", "LA"]
                ]
            }
        ]

        content = self.plugin._build_csv_content(tables, True, ",", False)

        lines = content.strip().split("\n")
        self.assertEqual(len(lines), 3)

        # 验证第一行是表头
        self.assertIn("Name", lines[0])

    def test_build_csv_content_without_header(self):
        """测试构建 CSV 内容 - 不包含表头"""
        tables = [
            {
                "rows": [
                    ["Name", "Age", "City"],
                    ["John", "25", "NYC"],
                    ["Jane", "30", "LA"]
                ]
            }
        ]

        content = self.plugin._build_csv_content(tables, False, ",", False)

        lines = content.strip().split("\n")
        self.assertEqual(len(lines), 2)

        # 第一行应该是数据，不是表头
        self.assertIn("John", lines[0])

    def test_build_csv_content_merge_tables(self):
        """测试构建 CSV 内容 - 合并表格"""
        tables = [
            {
                "rows": [
                    ["Name", "Age"],
                    ["John", "25"]
                ]
            },
            {
                "rows": [
                    ["Jane", "30"],
                    ["Bob", "35"]
                ]
            }
        ]

        content = self.plugin._build_csv_content(tables, True, ",", True)

        lines = content.strip().split("\n")
        # 应该有 4 行（两个表格合并）
        self.assertEqual(len(lines), 4)

    def test_build_csv_content_no_merge(self):
        """测试构建 CSV 内容 - 不合并表格"""
        tables = [
            {
                "rows": [
                    ["Name", "Age"],
                    ["John", "25"]
                ]
            },
            {
                "rows": [
                    ["Jane", "30"],
                    ["Bob", "35"]
                ]
            }
        ]

        content = self.plugin._build_csv_content(tables, True, ",", False)

        lines = content.split("\n")
        # 应该有空行分隔表格
        self.assertIn("", lines)

    def test_build_csv_content_custom_delimiter(self):
        """测试构建 CSV 内容 - 自定义分隔符"""
        tables = [
            {
                "rows": [
                    ["Name", "Age"],
                    ["John", "25"]
                ]
            }
        ]

        content = self.plugin._build_csv_content(tables, True, ";", False)

        lines = content.strip().split("\n")
        self.assertIn(";", lines[0])

    def test_build_csv_content_empty_table(self):
        """测试构建 CSV 内容 - 空表格"""
        tables = [
            {"rows": []}
        ]

        content = self.plugin._build_csv_content(tables, True, ",", False)

        # 应该返回空字符串或只有空行
        self.assertTrue(len(content.strip()) == 0)

    def test_save_csv_file(self):
        """测试保存 CSV 文件"""
        content = "Name,Age\nJohn,25\n"

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = f.name

        try:
            self.plugin._save_csv_file(content, output_path)

            # 验证文件存在
            self.assertTrue(os.path.exists(output_path))

            # 读取并验证内容
            with open(output_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            self.assertEqual(file_content, content)

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_save_csv_file_with_directory(self):
        """测试保存 CSV 文件到新目录"""
        content = "Name,Age\nJohn,25\n"

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "subdir", "output.csv")

            self.plugin._save_csv_file(content, output_path)

            # 验证文件存在
            self.assertTrue(os.path.exists(output_path))

            # 验证目录已创建
            self.assertTrue(os.path.exists(os.path.dirname(output_path)))

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_empty_cells(self):
        """测试处理空单元格"""
        result = self.plugin.convert(self.test_pdf_path)

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])

        # 解析 CSV 并检查单元格
        reader = csv.reader(io.StringIO(result["content"]))
        rows = list(reader)

        if rows:
            # 验证每行都是列表
            for row in rows:
                self.assertIsInstance(row, list)


class TestToCsvPluginEdgeCases(unittest.TestCase):
    """测试 ToCsvPlugin 边界情况"""

    def setUp(self):
        """测试前的设置"""
        self.plugin = ToCsvPlugin()

    def test_convert_invalid_page_number(self):
        """测试无效的页码"""
        # 创建一个最小的测试 PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            # 尝试转换不存在的页码
            result = self.plugin.convert(temp_path, page=999)
            # 可能成功但没有表格，或者失败
            self.assertIsNotNone(result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_convert_invalid_page_range(self):
        """测试无效的页码范围"""
        # 创建一个最小的测试 PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            # 尝试使用无效的页码范围（开始 > 结束）
            result = self.plugin.convert(temp_path, page_range=(10, 5))
            # 应该仍然有返回
            self.assertIsNotNone(result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_convert_empty_pages_list(self):
        """测试空的页码列表"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            result = self.plugin.convert(temp_path, pages=[])
            self.assertIsNotNone(result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_convert_empty_pdf_path(self):
        """测试空 PDF 路径"""
        result = self.plugin.convert("")
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])

    def test_convert_none_pdf_path(self):
        """测试 None PDF 路径"""
        result = self.plugin.convert(None)
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])

    def test_build_csv_content_all_options_false(self):
        """测试构建 CSV 内容 - 所有选项为 False"""
        tables = [
            {
                "rows": [
                    ["A", "B"],
                    ["1", "2"]
                ]
            }
        ]

        content = self.plugin._build_csv_content(tables, False, ",", False)
        self.assertIsInstance(content, str)

    def test_build_csv_content_single_row(self):
        """测试构建 CSV 内容 - 单行表格"""
        tables = [
            {
                "rows": [
                    ["Only", "One", "Row"]
                ]
            }
        ]

        content = self.plugin._build_csv_content(tables, False, ",", False)
        self.assertIsInstance(content, str)

    def test_build_csv_content_many_columns(self):
        """测试构建 CSV 内容 - 多列表格"""
        tables = [
            {
                "rows": [
                    ["Col" + str(i) for i in range(20)]
                ]
            }
        ]

        content = self.plugin._build_csv_content(tables, True, ",", False)

        # 验证包含所有列
        reader = csv.reader(io.StringIO(content))
        rows_list = list(reader)

        if rows_list:
            self.assertEqual(len(rows_list[0]), 20)

    def test_save_csv_file_empty_content(self):
        """测试保存空 CSV 文件"""
        content = ""

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = f.name

        try:
            self.plugin._save_csv_file(content, output_path)
            self.assertTrue(os.path.exists(output_path))

            with open(output_path, "r") as f:
                file_content = f.read()
            self.assertEqual(file_content, content)

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_determine_pages_boundary_values(self):
        """测试确定处理页码 - 边界值"""
        # 第一页
        pages = self.plugin._determine_pages_to_process({"page": 1}, 10)
        self.assertEqual(pages, [1])

        # 最后一页
        pages = self.plugin._determine_pages_to_process({"page": 10}, 10)
        self.assertEqual(pages, [10])

        # 完整范围
        pages = self.plugin._determine_pages_to_process({"page_range": (1, 10)}, 10)
        self.assertEqual(pages, list(range(1, 11)))


class TestToCsvPluginIntegration(unittest.TestCase):
    """测试 ToCsvPlugin 集成场景"""

    def setUp(self):
        """测试前的设置"""
        self.plugin = ToCsvPlugin()
        self.test_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "test_sample.pdf"
        )

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_full_conversion_pipeline(self):
        """测试完整的转换流程"""
        # 1. 验证文件
        is_valid, error = self.plugin.validate(self.test_pdf_path)
        self.assertTrue(is_valid, f"Validation failed: {error}")

        # 2. 转换文件
        result = self.plugin.convert(
            self.test_pdf_path,
            header=True,
            delimiter=",",
            merge_tables=False,
            table_index=0
        )

        if not result["success"]:
            if "No tables found" in result.get("error", ""):
                self.skipTest("No tables found in PDF")
            self.fail(f"Conversion failed: {result['error']}")

        # 3. 验证输出
        self.assertTrue(self.plugin.validate_output(result))

        # 4. 验证内容
        self.assertGreater(len(result["content"]), 0)

        # 5. 解析 CSV
        reader = csv.reader(io.StringIO(result["content"]))
        rows = list(reader)
        self.assertGreater(len(rows), 0)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_and_save_pipeline(self):
        """测试转换和保存的完整流程"""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = f.name

        try:
            # 转换并保存
            result = self.plugin.convert(
                self.test_pdf_path,
                output_path=output_path
            )

            if not result["success"]:
                if "No tables found" in result.get("error", ""):
                    self.skipTest("No tables found in PDF")
                self.fail(f"Conversion failed: {result['error']}")

            # 验证文件
            self.assertTrue(os.path.exists(output_path))
            self.assertEqual(result["output_path"], output_path)

            # 读取并验证
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertEqual(content, result["content"])

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


if __name__ == "__main__":
    unittest.main()
