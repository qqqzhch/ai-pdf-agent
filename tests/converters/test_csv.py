"""测试 CSV 转换器 (ToCsvPlugin)"""

# 添加项目根目录到路径
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import csv
import tempfile
import unittest
import io
import shutil

from plugins.converters.to_csv import ToCsvPlugin


class TestToCsvPluginInitialization(unittest.TestCase):
    """测试 ToCsvPlugin 初始化"""

    def test_initialization_default(self):
        """测试默认初始化"""
        converter = ToCsvPlugin()

        self.assertEqual(converter.name, "csv_converter")
        self.assertEqual(converter.version, "1.0.0")
        self.assertEqual(converter.author, "李开发")
        self.assertEqual(converter.license, "MIT")
        self.assertIn("将 PDF 表格转换为 CSV", converter.description)

    def test_initialization_with_pdf_engine(self):
        """测试使用 PDF 引擎初始化"""
        from core.engine.pymupdf_engine import PyMuPDFEngine

        engine = PyMuPDFEngine()
        converter = ToCsvPlugin(pdf_engine=engine)

        self.assertIsNotNone(converter.pdf_engine)
        self.assertEqual(converter.pdf_engine, engine)

    def test_initialization_with_table_reader(self):
        """测试使用表格读取器初始化"""
        from plugins.readers.table_reader import TableReaderPlugin
        from core.engine.pymupdf_engine import PyMuPDFEngine

        engine = PyMuPDFEngine()
        reader = TableReaderPlugin(engine)
        converter = ToCsvPlugin(table_reader=reader)

        self.assertIsNotNone(converter.table_reader)
        self.assertEqual(converter.table_reader, reader)

    def test_plugin_metadata(self):
        """测试插件元数据"""
        converter = ToCsvPlugin()
        metadata = converter.get_metadata()

        self.assertEqual(metadata["name"], "csv_converter")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertEqual(metadata["plugin_type"], "converter")
        self.assertIn("pymupdf>=1.23.0", metadata["dependencies"])


class TestToCsvPluginValidation(unittest.TestCase):
    """测试 ToCsvPlugin 验证功能"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToCsvPlugin()

    def test_validate_nonexistent_file(self):
        """测试验证不存在的文件"""
        is_valid, error = self.converter.validate("/nonexistent/file.pdf")
        self.assertFalse(is_valid)
        self.assertIn("not found", error.lower())

    def test_validate_invalid_file(self):
        """测试验证无效文件"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name
            f.write(b"not a pdf")

        try:
            is_valid, error = self.converter.validate(temp_path)
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
            os.chmod(temp_path, 0o000)

            is_valid, error = self.converter.validate(temp_path)
            self.assertFalse(is_valid)
            self.assertTrue("not readable" in error.lower() or "failed to open" in error.lower())

        finally:
            os.chmod(temp_path, 0o644)
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_validate_input_valid(self):
        """测试输入验证 - 有效输入"""
        self.assertTrue(self.converter.validate_input(pdf_path="test.pdf"))

    def test_validate_input_missing_pdf_path(self):
        """测试输入验证 - 缺少 pdf_path"""
        self.assertFalse(self.converter.validate_input())

    def test_validate_input_invalid_pdf_path_type(self):
        """测试输入验证 - 无效的 pdf_path 类型"""
        self.assertFalse(self.converter.validate_input(pdf_path=123))

    def test_validate_input_valid_multi_table_mode(self):
        """测试输入验证 - 有效的多表格模式"""
        for mode in ["separate", "merge", "first"]:
            self.assertTrue(self.converter.validate_input(
                pdf_path="test.pdf",
                multi_table_mode=mode
            ))

    def test_validate_input_invalid_multi_table_mode(self):
        """测试输入验证 - 无效的多表格模式"""
        self.assertFalse(self.converter.validate_input(
            pdf_path="test.pdf",
            multi_table_mode="invalid"
        ))

    def test_validate_input_valid_delimiter(self):
        """测试输入验证 - 有效的分隔符"""
        for delimiter in [",", ";", "\t", "|", " "]:
            self.assertTrue(self.converter.validate_input(
                pdf_path="test.pdf",
                delimiter=delimiter
            ))

    def test_validate_input_invalid_delimiter(self):
        """测试输入验证 - 无效的分隔符"""
        self.assertFalse(self.converter.validate_input(
            pdf_path="test.pdf",
            delimiter=":"
        ))

    def test_validate_output_valid(self):
        """测试输出验证 - 有效输出"""
        result = {
            "success": True,
            "tables": [],
            "total_tables": 0,
            "files": [],
            "content": None,
            "metadata": {},
            "error": None
        }
        self.assertTrue(self.converter.validate_output(result))

    def test_validate_output_missing_fields(self):
        """测试输出验证 - 缺少字段"""
        invalid_result = {"success": True}
        self.assertFalse(self.converter.validate_output(invalid_result))

    def test_validate_output_not_dict(self):
        """测试输出验证 - 非字典"""
        self.assertFalse(self.converter.validate_output("not a dict"))


class TestToCsvPluginConversion(unittest.TestCase):
    """测试 ToCsvPlugin 转换功能"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToCsvPlugin()
        self.test_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "test_sample.pdf"
        )

    def tearDown(self):
        """测试后的清理"""
        pass

    def test_convert_nonexistent_file(self):
        """测试转换不存在的文件"""
        result = self.converter.convert("/nonexistent/file.pdf")

        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])
        self.assertIn("not found", result["error"].lower())

    def test_convert_empty_pdf_path(self):
        """测试转换空 PDF 路径"""
        result = self.converter.convert("")

        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_convert_success(self):
        """测试成功转换"""
        result = self.converter.convert(self.test_pdf_path)

        # 检查基本结构
        self.assertIn("success", result)
        self.assertIn("tables", result)
        self.assertIn("total_tables", result)
        self.assertIn("files", result)
        self.assertIn("content", result)
        self.assertIn("metadata", result)
        self.assertIn("error", result)

        if not result["success"]:
            # 如果没有表格，应该返回错误
            self.assertIn("error", result)
            self.assertIsNotNone(result["error"])
        else:
            self.assertTrue(result["success"])
            self.assertGreaterEqual(result["total_tables"], 0)

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_convert_with_page_parameter(self):
        """测试转换指定页码"""
        result = self.converter.convert(self.test_pdf_path, page=1)

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])
        self.assertGreaterEqual(result["total_tables"], 0)

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_convert_with_page_range(self):
        """测试转换页面范围"""
        result = self.converter.convert(self.test_pdf_path, page_range=(1, 2))

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_convert_with_pages_list(self):
        """测试转换指定页码列表"""
        result = self.converter.convert(self.test_pdf_path, pages=[1])

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])


class TestToCsvPluginMultiTableModes(unittest.TestCase):
    """测试 ToCsvPlugin 多表格模式"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToCsvPlugin()
        self.test_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "test_sample.pdf"
        )

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_mode_separate_with_output_dir(self):
        """测试 separate 模式 - 每个表格一个文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.converter.convert(
                self.test_pdf_path,
                multi_table_mode="separate",
                output_dir=temp_dir,
                file_prefix="test_table"
            )

            if not result["success"]:
                if "No tables found" in result.get("error", ""):
                    self.skipTest("No tables found in PDF")
                self.fail(f"Conversion failed: {result['error']}")

            self.assertTrue(result["success"])
            self.assertGreater(len(result["files"]), 0)

            # 验证文件存在
            for file_path in result["files"]:
                self.assertTrue(os.path.exists(file_path))
                self.assertTrue(file_path.startswith(temp_dir))

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_mode_merge_with_output_path(self):
        """测试 merge 模式 - 合并所有表格"""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = f.name

        try:
            result = self.converter.convert(
                self.test_pdf_path,
                multi_table_mode="merge",
                output_path=output_path
            )

            if not result["success"]:
                if "No tables found" in result.get("error", ""):
                    self.skipTest("No tables found in PDF")
                self.fail(f"Conversion failed: {result['error']}")

            self.assertTrue(result["success"])
            self.assertIsNotNone(result["content"])
            self.assertEqual(result["files"], [output_path])

            # 验证文件存在
            self.assertTrue(os.path.exists(output_path))

            # 验证内容匹配
            with open(output_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            self.assertEqual(file_content, result["content"])

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_mode_first_with_output_path(self):
        """测试 first 模式 - 只转换第一个表格"""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = f.name

        try:
            result = self.converter.convert(
                self.test_pdf_path,
                multi_table_mode="first",
                output_path=output_path
            )

            if not result["success"]:
                if "No tables found" in result.get("error", ""):
                    self.skipTest("No tables found in PDF")
                if "No tables found" not in result.get("error", "") and result["total_tables"] > 0:
                    # 有表格但转换失败
                    self.fail(f"Conversion failed: {result['error']}")

            self.assertTrue(result["success"])
            self.assertIsNotNone(result["content"])
            self.assertEqual(result["files"], [output_path])
            self.assertEqual(len(result["tables"]), 1)

            # 验证文件存在
            self.assertTrue(os.path.exists(output_path))

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestToCsvPluginFormatting(unittest.TestCase):
    """测试 ToCsvPlugin 格式化选项"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToCsvPlugin()
        self.test_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "test_sample.pdf"
        )

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_comma_delimiter(self):
        """测试逗号分隔符"""
        result = self.converter.convert(
            self.test_pdf_path,
            multi_table_mode="merge",
            delimiter=","
        )

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])
        self.assertIsNotNone(result["content"])

        # 验证可以解析
        reader = csv.reader(io.StringIO(result["content"]), delimiter=",")
        list(reader)

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_semicolon_delimiter(self):
        """测试分号分隔符"""
        result = self.converter.convert(
            self.test_pdf_path,
            multi_table_mode="merge",
            delimiter=";"
        )

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])
        self.assertIsNotNone(result["content"])

        # 验证可以解析
        reader = csv.reader(io.StringIO(result["content"]), delimiter=";")
        list(reader)

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_tab_delimiter(self):
        """测试制制表符分隔符"""
        result = self.converter.convert(
            self.test_pdf_path,
            multi_table_mode="merge",
            delimiter="\t"
        )

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])
        self.assertIsNotNone(result["content"])

        # 验证可以解析
        reader = csv.reader(io.StringIO(result["content"]), delimiter="\t")
        list(reader)

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_pipe_delimiter(self):
        """测试管道符分隔符"""
        result = self.converter.convert(
            self.test_pdf_path,
            multi_table_mode="merge",
            delimiter="|"
        )

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])
        self.assertIsNotNone(result["content"])

        # 验证可以解析
        reader = csv.reader(io.StringIO(result["content"]), delimiter="|")
        list(reader)

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_quote_minimal(self):
        """测试最小化引号"""
        result = self.converter.convert(
            self.test_pdf_path,
            multi_table_mode="merge",
            quoting=csv.QUOTE_MINIMAL
        )

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_quote_all(self):
        """测试所有字段引号"""
        result = self.converter.convert(
            self.test_pdf_path,
            multi_table_mode="merge",
            quoting=csv.QUOTE_ALL
        )

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_quote_nonnumeric(self):
        """测试非数字引号"""
        result = self.converter.convert(
            self.test_pdf_path,
            multi_table_mode="merge",
            quoting=csv.QUOTE_NONNUMERIC
        )

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_custom_quotechar(self):
        """测试自定义引号字符"""
        result = self.converter.convert(
            self.test_pdf_path,
            multi_table_mode="merge",
            quotechar="'"
        )

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_include_header(self):
        """测试包含表头"""
        result = self.converter.convert(
            self.test_pdf_path,
            multi_table_mode="merge",
            include_header=True
        )

        if not result["success"] and "No tables found" in result.get("error", ""):
            self.skipTest("No tables found in PDF")

        self.assertTrue(result["success"])

        if result["content"]:
            # 验证可以解析
            reader = csv.reader(io.StringIO(result["content"]))
            rows = list(reader)
            if rows:
                # 第一行应该是表头
                self.assertIsInstance(rows[0], list)

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_custom_encoding(self):
        """测试自定义编码"""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = f.name

        try:
            result = self.converter.convert(
                self.test_pdf_path,
                multi_table_mode="merge",
                output_path=output_path,
                encoding="utf-8-sig"
            )

            if not result["success"] and "No tables found" in result.get("error", ""):
                self.skipTest("No tables found in PDF")

            self.assertTrue(result["success"])

            # 验证可以读取文件
            with open(output_path, "r", encoding="utf-8-sig") as f:
                f.read()

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestToCsvPluginHelperMethods(unittest.TestCase):
    """测试 ToCsvPlugin 辅助方法"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToCsvPlugin()

    def test_determine_pages_to_extract_single_page(self):
        """测试确定提取页码 - 单页"""
        pages = self.converter._determine_pages_to_extract({"page": 2}, 10)
        self.assertEqual(pages, [2])

    def test_determine_pages_to_extract_page_range(self):
        """测试确定提取页码 - 页面范围"""
        pages = self.converter._determine_pages_to_extract({"page_range": (3, 7)}, 10)
        self.assertEqual(pages, [3, 4, 5, 6, 7])

    def test_determine_pages_to_extract_pages_list(self):
        """测试确定提取页码 - 页码列表"""
        pages = self.converter._determine_pages_to_extract({"pages": [1, 3, 5]}, 10)
        self.assertEqual(pages, [1, 3, 5])

    def test_determine_pages_to_extract_all_pages(self):
        """测试确定提取页码 - 所有页面"""
        pages = self.converter._determine_pages_to_extract({}, 5)
        self.assertEqual(pages, [1, 2, 3, 4, 5])

    def test_convert_table_to_csv(self):
        """测试转换单个表格为 CSV"""
        table = {
            "page": 1,
            "rows": [
                ["Name", "Age", "City"],
                ["John", "25", "NYC"],
                ["Jane", "30", "LA"]
            ]
        }

        csv_content = self.converter._convert_table_to_csv(
            table,
            delimiter=",",
            quoting=csv.QUOTE_MINIMAL,
            quotechar='"',
            include_header=True,
            encoding="utf-8"
        )

        self.assertIsInstance(csv_content, str)
        self.assertGreater(len(csv_content), 0)

        # 验证可以解析
        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)
        self.assertEqual(len(rows), 3)

    def test_merge_tables_to_csv(self):
        """测试合并多个表格为 CSV"""
        tables = [
            {
                "page": 1,
                "rows": [
                    ["Name", "Age"],
                    ["John", "25"]
                ]
            },
            {
                "page": 2,
                "rows": [
                    ["Jane", "30"]
                ]
            }
        ]

        csv_content = self.converter._merge_tables_to_csv(
            tables,
            delimiter=",",
            quoting=csv.QUOTE_MINIMAL,
            quotechar='"',
            include_header=True,
            encoding="utf-8"
        )

        self.assertIsInstance(csv_content, str)
        self.assertGreater(len(csv_content), 0)

        # 验证可以解析
        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)
        self.assertGreater(len(rows), 0)

    def test_save_csv_file(self):
        """测试保存 CSV 文件"""
        content = "Name,Age\nJohn,25\n"

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = f.name

        try:
            self.converter._save_csv_file(content, output_path, "utf-8")

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

            self.converter._save_csv_file(content, output_path, "utf-8")

            # 验证文件和目录存在
            self.assertTrue(os.path.exists(output_path))
            self.assertTrue(os.path.exists(os.path.dirname(output_path)))

    def test_save_csv_file_custom_encoding(self):
        """测试保存 CSV 文件使用自定义编码"""
        content = "姓名,年龄\n张三,25\n"

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = f.name

        try:
            self.converter._save_csv_file(content, output_path, "utf-8-sig")

            # 验证文件存在
            self.assertTrue(os.path.exists(output_path))

            # 使用相同编码读取
            with open(output_path, "r", encoding="utf-8-sig") as f:
                file_content = f.read()

            self.assertEqual(file_content, content)

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_get_help(self):
        """测试获取帮助信息"""
        help_text = self.converter.get_help()

        self.assertIsInstance(help_text, str)
        self.assertIn("csv_converter", help_text)
        self.assertIn("使用方法", help_text)
        self.assertIn("支持的参数", help_text)
        self.assertIn("multi_table_mode", help_text)
        self.assertIn("delimiter", help_text)
        self.assertIn("quoting", help_text)


class TestToCsvPluginIntegration(unittest.TestCase):
    """测试 ToCsvPlugin 集成场景"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToCsvPlugin()
        self.test_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "test_sample.pdf"
        )

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_full_conversion_pipeline_separate_mode(self):
        """测试完整转换流程 - separate 模式"""
        # 1. 验证文件
        is_valid, error = self.converter.validate(self.test_pdf_path)
        self.assertTrue(is_valid, f"Validation failed: {error}")

        # 2. 转换文件
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.converter.convert(
                self.test_pdf_path,
                multi_table_mode="separate",
                output_dir=temp_dir,
                delimiter=",",
                include_header=True,
                file_prefix="test"
            )

            if not result["success"]:
                if "No tables found" in result.get("error", ""):
                    self.skipTest("No tables found in PDF")
                self.fail(f"Conversion failed: {result['error']}")

            # 3. 验证输出
            self.assertTrue(self.converter.validate_output(result))

            # 4. 验证文件
            self.assertGreater(len(result["files"]), 0)
            for file_path in result["files"]:
                self.assertTrue(os.path.exists(file_path))

            # 5. 验证表格信息
            if result["tables"]:
                for table_info in result["tables"]:
                    self.assertIn("table_index", table_info)
                    self.assertIn("page", table_info)
                    self.assertIn("rows", table_info)

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_full_conversion_pipeline_merge_mode(self):
        """测试完整转换流程 - merge 模式"""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = f.name

        try:
            result = self.converter.convert(
                self.test_pdf_path,
                multi_table_mode="merge",
                output_path=output_path,
                delimiter=";",
                quoting=csv.QUOTE_ALL
            )

            if not result["success"]:
                if "No tables found" in result.get("error", ""):
                    self.skipTest("No tables found in PDF")
                self.fail(f"Conversion failed: {result['error']}")

            self.assertTrue(result["success"])
            self.assertIsNotNone(result["content"])
            self.assertEqual(result["files"], [output_path])

            # 验证文件存在且内容匹配
            self.assertTrue(os.path.exists(output_path))

            with open(output_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            self.assertEqual(file_content, result["content"])

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    @unittest.skipIf(
        not os.path.exists(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "test_sample.pdf"
            )
        ),
        "Test PDF file not found"
    )
    def test_batch_conversion_with_different_formats(self):
        """测试批量转换不同格式"""
        formats = [
            (",", csv.QUOTE_MINIMAL),
            (";", csv.QUOTE_ALL),
            ("\t", csv.QUOTE_NONNUMERIC),
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            for i, (delimiter, quoting) in enumerate(formats):
                output_path = os.path.join(temp_dir, f"output_{i}.csv")

                result = self.converter.convert(
                    self.test_pdf_path,
                    multi_table_mode="merge",
                    output_path=output_path,
                    delimiter=delimiter,
                    quoting=quoting
                )

                if not result["success"]:
                    if "No tables found" in result.get("error", ""):
                        self.skipTest("No tables found in PDF")
                    continue

                self.assertTrue(result["success"])
                self.assertTrue(os.path.exists(output_path))


class TestToCsvPluginEdgeCases(unittest.TestCase):
    """测试 ToCsvPlugin 边界情况"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToCsvPlugin()

    def test_convert_invalid_delimiter_fallback(self):
        """测试无效分隔符回退到默认"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            result = self.converter.convert(temp_path, delimiter=":")
            # 应该返回结果（可能成功但没有表格，或失败）
            self.assertIsNotNone(result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_convert_table_with_empty_rows(self):
        """测试转换包含空行的表格"""
        table = {
            "page": 1,
            "rows": []
        }

        csv_content = self.converter._convert_table_to_csv(
            table,
            delimiter=",",
            quoting=csv.QUOTE_MINIMAL,
            quotechar='"',
            include_header=True,
            encoding="utf-8"
        )

        self.assertIsInstance(csv_content, str)

    def test_merge_empty_tables_list(self):
        """测试合并空表格列表"""
        csv_content = self.converter._merge_tables_to_csv(
            [],
            delimiter=",",
            quoting=csv.QUOTE_MINIMAL,
            quotechar='"',
            include_header=True,
            encoding="utf-8"
        )

        self.assertIsInstance(csv_content, str)

    def test_save_empty_content(self):
        """测试保存空内容"""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = f.name

        try:
            self.converter._save_csv_file("", output_path, "utf-8")

            self.assertTrue(os.path.exists(output_path))

            with open(output_path, "r") as f:
                content = f.read()

            self.assertEqual(content, "")

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


if __name__ == "__main__":
    unittest.main()
