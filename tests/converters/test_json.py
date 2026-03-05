"""测试 JSON 转换器插件 (ToJsonPlugin)

测试用例覆盖：
1. 插件初始化和元数据
2. PDF 文件验证
3. 基本转换功能
4. 页码范围处理
5. 内容提取（文本、表格、元数据、结构）
6. 输出文件保存
7. 自定义 schema
8. 边界情况处理
"""

# 添加项目根目录到路径
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import tempfile
import unittest

from plugins.converters.to_json import ToJsonPlugin


class TestToJsonPluginInitialization(unittest.TestCase):
    """测试 ToJsonPlugin 初始化和元数据"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToJsonPlugin()

    def test_converter_class_exists(self):
        """测试转换器类存在"""
        self.assertIsNotNone(ToJsonPlugin)

    def test_converter_initialization(self):
        """测试转换器初始化"""
        self.assertIsNotNone(self.converter)
        self.assertEqual(self.converter.name, "to_json")
        self.assertEqual(self.converter.version, "1.0.0")
        self.assertEqual(self.converter.author, "李开发")
        self.assertEqual(self.converter.license, "MIT")

    def test_converter_metadata(self):
        """测试转换器元数据"""
        metadata = self.converter.get_metadata()

        self.assertEqual(metadata["name"], "to_json")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertEqual(
            metadata["description"],
            "将 PDF 内容转换为 JSON 格式，支持文本、表格、元数据和文档结构的转换"
        )
        self.assertEqual(metadata["plugin_type"], "converter")
        self.assertIn("pymupdf>=1.23.0", metadata["dependencies"])

    def test_converter_dependencies(self):
        """测试转换器依赖"""
        deps_ok, missing_deps = self.converter.check_dependencies()

        # PyMuPDF 应该是可用的
        self.assertTrue(deps_ok, f"Missing dependencies: {missing_deps}")

    def test_is_available(self):
        """测试转换器可用性"""
        # 如果 PyMuPDF 可用，转换器应该可用
        if self.converter.pdf_engine is not None:
            self.assertTrue(self.converter.is_available())
        else:
            self.assertFalse(self.converter.is_available())

    def test_get_help(self):
        """测试获取帮助信息"""
        help_text = self.converter.get_help()

        self.assertIsInstance(help_text, str)
        self.assertIn("to_json", help_text)
        self.assertIn("使用方法", help_text)
        self.assertIn("支持的参数", help_text)
        self.assertIn("page", help_text)
        self.assertIn("page_range", help_text)
        self.assertIn("output_path", help_text)


class TestToJsonPluginValidation(unittest.TestCase):
    """测试 ToJsonPlugin 验证功能"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToJsonPlugin()

    def test_validate_nonexistent_file(self):
        """测试验证不存在的文件"""
        is_valid, error = self.converter.validate("/nonexistent/file.pdf")
        self.assertFalse(is_valid)
        self.assertIn("not found", error.lower())

    def test_validate_non_pdf_file(self):
        """测试验证非 PDF 文件"""
        # 创建非 PDF 文件
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name
            f.write(b"This is not a PDF file")

        try:
            is_valid, error = self.converter.validate(temp_path)
            self.assertFalse(is_valid)
            self.assertIn("not a pdf", error.lower())
        finally:
            os.unlink(temp_path)

    def test_validate_unreadable_file(self):
        """测试验证不可读文件"""
        # 创建文件并移除读取权限
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name
            f.write(b"fake pdf")

        try:
            os.chmod(temp_path, 0o000)  # 移除所有权限
            is_valid, error = self.converter.validate(temp_path)
            self.assertFalse(is_valid)
            # 检查错误信息（可能是 "not readable" 或 "failed to open"）
            self.assertTrue(
                "not readable" in error.lower() or "failed to open" in error.lower() or "invalid" in error.lower()
            )
        finally:
            os.chmod(temp_path, 0o644)  # 恢复权限
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_validate_input_valid(self):
        """测试输入验证 - 有效输入"""
        self.assertTrue(self.converter.validate_input(pdf_path="test.pdf"))

    def test_validate_input_missing_pdf_path(self):
        """测试输入验证 - 缺少 pdf_path"""
        self.assertFalse(self.converter.validate_input())

    def test_validate_input_invalid_type(self):
        """测试输入验证 - 无效类型"""
        self.assertFalse(self.converter.validate_input(pdf_path=123))
        self.assertFalse(self.converter.validate_input(pdf_path=None))

    def test_validate_output_valid(self):
        """测试输出验证 - 有效输出"""
        result = {
            "success": True,
            "content": "{}",
            "metadata": {},
            "pages": 1,
            "output_path": None,
            "error": None
        }
        self.assertTrue(self.converter.validate_output(result))

    def test_validate_output_invalid(self):
        """测试输出验证 - 无效输出"""
        # 缺少字段
        invalid_result = {"success": True, "content": "{}"}
        self.assertFalse(self.converter.validate_output(invalid_result))

        # 非字典
        self.assertFalse(self.converter.validate_output("not a dict"))
        self.assertFalse(self.converter.validate_output(123))
        self.assertFalse(self.converter.validate_output(None))


class TestToJsonPluginConversion(unittest.TestCase):
    """测试 ToJsonPlugin 基本转换功能"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToJsonPlugin()

        # 创建测试 PDF 文件路径
        self.test_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "test_sample.pdf"
        )

    def test_convert_nonexistent_file(self):
        """测试转换不存在的文件"""
        result = self.converter.convert("/nonexistent/file.pdf")

        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])
        self.assertIn("not found", result["error"].lower())

    def test_convert_empty_path(self):
        """测试转换空路径"""
        result = self.converter.convert("")

        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])

    def test_convert_success_with_test_pdf(self):
        """测试成功转换 PDF 为 JSON"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path)

        self.assertTrue(result["success"])
        self.assertGreater(len(result["content"]), 0)
        self.assertGreater(result["pages"], 0)
        self.assertIn("metadata", result)
        self.assertIsNone(result["error"])

    def test_convert_result_structure(self):
        """测试转换结果结构"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path)

        self.assertTrue(result["success"])
        self.assertIn("success", result)
        self.assertIn("content", result)
        self.assertIn("metadata", result)
        self.assertIn("pages", result)
        self.assertIn("output_path", result)
        self.assertIn("error", result)

    def test_convert_json_validity(self):
        """测试转换结果为有效 JSON"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path)

        if result["success"]:
            try:
                json_data = json.loads(result["content"])
                self.assertIsInstance(json_data, dict)
            except json.JSONDecodeError as e:
                self.fail(f"Failed to parse JSON: {e}")

    def test_convert_json_structure(self):
        """测试 JSON 数据结构"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path)

        if result["success"]:
            json_data = json.loads(result["content"])

            # 验证必需字段
            self.assertIn("document", json_data)
            self.assertIn("metadata", json_data)
            self.assertIn("text", json_data)
            self.assertIn("tables", json_data)
            self.assertIn("structure", json_data)

            # 验证 document 字段
            self.assertIn("filename", json_data["document"])
            self.assertIn("path", json_data["document"])
            self.assertIn("page_count", json_data["document"])
            self.assertIn("pages_processed", json_data["document"])


class TestToJsonPluginPageSelection(unittest.TestCase):
    """测试 ToJsonPlugin 页码选择功能"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToJsonPlugin()
        self.test_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "test_sample.pdf"
        )

    def test_convert_single_page(self):
        """测试转换单页"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, page=1)

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])
        self.assertEqual(json_data["document"]["pages_processed"], [1])

    def test_convert_page_range(self):
        """测试转换页码范围"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, page_range=(1, 3))

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])
        self.assertEqual(json_data["document"]["pages_processed"], [1, 2, 3])

    def test_convert_pages_list(self):
        """测试转换指定页码列表"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, pages=[1, 3])

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])
        self.assertEqual(json_data["document"]["pages_processed"], [1, 3])

    def test_convert_all_pages(self):
        """测试转换所有页面（默认）"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path)

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])

        result_metadata = self.converter.get_metadata()
        # 处理的页码应该从 1 开始递增
        expected_pages = list(range(1, json_data["document"]["page_count"] + 1))
        self.assertEqual(json_data["document"]["pages_processed"], expected_pages)

    def test_convert_invalid_page_number(self):
        """测试无效页码"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        # 超出范围的页码
        result = self.converter.convert(self.test_pdf_path, page=99999)
        # 应该成功但处理所有页面（或失败，取决于实现）
        if result["success"]:
            json_data = json.loads(result["content"])
            # 应该回退到处理所有页面
            self.assertGreater(len(json_data["document"]["pages_processed"]), 0)

    def test_convert_invalid_page_range(self):
        """测试无效页码范围"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        # 起始大于结束
        result = self.converter.convert(self.test_pdf_path, page_range=(10, 5))
        # 应该失败或回退到处理所有页面
        if result["success"]:
            json_data = json.loads(result["content"])
            self.assertGreater(len(json_data["document"]["pages_processed"]), 0)

    def test_convert_empty_pages_list(self):
        """测试空页码列表"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, pages=[])
        # 空页码列表应该回退到处理所有页面
        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])
        self.assertGreater(len(json_data["document"]["pages_processed"]), 0)


class TestToJsonPluginContentExtraction(unittest.TestCase):
    """测试 ToJsonPlugin 内容提取功能"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToJsonPlugin()
        self.test_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "test_sample.pdf"
        )

    def test_extract_text(self):
        """测试文本提取"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, include_text=True)

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])

        self.assertIn("text", json_data)
        self.assertIn("total_pages", json_data["text"])
        self.assertIn("pages", json_data["text"])

        # 验证每个页面的文本结构
        for page in json_data["text"]["pages"]:
            self.assertIn("page_number", page)
            self.assertIn("full_text", page)
            self.assertIn("blocks", page)
            self.assertIn("char_count", page)

    def test_extract_tables(self):
        """测试表格提取"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, include_tables=True)

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])

        self.assertIn("tables", json_data)
        self.assertIn("total_tables", json_data["tables"])
        self.assertIn("pages", json_data["tables"])

        # 验证每个页面的表格结构
        for page in json_data["tables"]["pages"]:
            self.assertIn("page_number", page)
            self.assertIn("tables", page)
            self.assertIn("table_count", page)

    def test_extract_metadata(self):
        """测试元数据提取"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, include_metadata=True)

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])

        self.assertIn("metadata", json_data)

        # 验证元数据结构
        metadata = json_data["metadata"]
        self.assertIn("title", metadata)
        self.assertIn("author", metadata)
        self.assertIn("subject", metadata)
        self.assertIn("keywords", metadata)
        self.assertIn("created", metadata)
        self.assertIn("modified", metadata)

    def test_extract_structure(self):
        """测试文档结构提取"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, include_structure=True)

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])

        self.assertIn("structure", json_data)
        self.assertIn("pages", json_data["structure"])

        # 验证每个页面的结构信息
        for page in json_data["structure"]["pages"]:
            self.assertIn("page_number", page)
            self.assertIn("width", page)
            self.assertIn("height", page)
            self.assertIn("rotation", page)
            self.assertIn("text_blocks", page)
            self.assertIn("image_blocks", page)
            self.assertIn("drawing_blocks", page)

    def test_exclude_text(self):
        """测试排除文本内容"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, include_text=False)

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])
        self.assertNotIn("text", json_data)

    def test_exclude_tables(self):
        """测试排除表格"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, include_tables=False)

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])
        self.assertNotIn("tables", json_data)

    def test_exclude_metadata(self):
        """测试排除元数据"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, include_metadata=False)

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])
        self.assertNotIn("metadata", json_data)

    def test_exclude_structure(self):
        """测试排除文档结构"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, include_structure=False)

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])
        self.assertNotIn("structure", json_data)

    def test_text_blocks_structure(self):
        """测试文本块结构"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, include_text=True)

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])

        # 检查文本块结构
        for for_page in json_data["text"]["pages"]:
            for block in for_page.get("blocks", []):
                self.assertIn("text", block)
                self.assertIn("bbox", block)
                self.assertIn("line_no", block)

    def test_table_structure(self):
        """测试表格数据结构"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, include_tables=True)

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])

        # 检查表格结构
        for page in json_data["tables"]["pages"]:
            for table in page.get("tables", []):
                self.assertIn("bbox", table)
                self.assertIn("header", table)
                self.assertIn("rows", table)
                self.assertIn("row_count", table)
                self.assertIn("col_count", table)


class TestToJsonPluginOutputOptions(unittest.TestCase):
    """测试 ToJsonPlugin 输出选项"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToJsonPlugin()
        self.test_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "test_sample.pdf"
        )

    def test_pretty_json(self):
        """测试格式化 JSON"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, pretty=True)

        self.assertTrue(result["success"])
        self.assertIn("\n", result["content"])
        self.assertIn("  ", result["content"])

    def test_compact_json(self):
        """测试紧凑 JSON"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, pretty=False)

        self.assertTrue(result["success"])
        self.assertNotIn("\n", result["content"])

    def test_save_to_file(self):
        """测试保存到文件"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            output_path = f.name

        try:
            result = self.converter.convert(
                self.test_pdf_path,
                output_path=output_path
            )

            self.assertTrue(result["success"])
            self.assertEqual(result["output_path"], output_path)
            self.assertTrue(os.path.exists(output_path))

            # 读取并验证文件内容
            with open(output_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            self.assertEqual(file_content, result["content"])
            json.loads(file_content)  # 验证是有效 JSON

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_save_to_file_pretty(self):
        """测试保存格式化 JSON 到文件"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            output_path = f.name

        try:
            result = self.converter.convert(
                self.test_pdf_path,
                output_path=output_path,
                pretty=True
            )

            self.assertTrue(result["success"])
            self.assertTrue(os.path.exists(output_path))

            with open(output_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            self.assertIn("\n", file_content)
            self.assertIn("  ", file_content)

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_save_to_nonexistent_directory(self):
        """测试保存到不存在的目录"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        output_path = "/nonexistent/directory/output.json"
        result = self.converter.convert(
            self.test_pdf_path,
            output_path=output_path
        )

        # 应该失败
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error"])


class TestToJsonPluginCustomSchema(unittest.TestCase):
    """测试 ToJsonPlugin 自定义 schema 功能"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToJsonPlugin()
        self.test_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "test_sample.pdf"
        )

    def test_apply_schema_include_fields(self):
        """测试使用自定义 schema - 包含字段"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        schema = {
            "include_fields": ["document", "text"],
            "exclude_fields": []
        }

        result = self.converter.convert(self.test_pdf_path, schema=schema)

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])

        self.assertIn("document", json_data)
        self.assertIn("text", json_data)
        self.assertNotIn("metadata", json_data)
        self.assertNotIn("tables", json_data)
        self.assertNotIn("structure", json_data)

    def test_apply_schema_exclude_fields(self):
        """测试使用自定义 schema - 排除字段"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(
            self.test_pdf_path,
            include_tables=True,
            include_structure=True
        )

        # 先获取所有字段
        json_data = json.loads(result["content"])
        original_keys = set(json_data.keys())

        # 使用 exclude_fields
        schema = {
            "exclude_fields": ["tables", "structure"]
        }

        result = self.converter.convert(
            self.test_pdf_path,
            schema=schema,
            include_tables=True,
            include_structure=True
        )

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])

        self.assertNotIn("tables", json_data)
        self.assertNotIn("structure", json_data)
        self.assertIn("document", json_data)
        self.assertIn("text", json_data)

    def test_apply_empty_schema(self):
        """测试应用空 schema"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(self.test_pdf_path, schema=None)

        self.assertTrue(result["success"])
        json_data = json.loads(result["content"])

        # 应该包含所有默认字段
        self.assertIn("document", json_data)
        self.assertIn("metadata", json_data)
        self.assertIn("text", json_data)
        self.assertIn("tables", json_data)
        self.assertIn("structure", json_data)

    def test_build_json_schema(self):
        """测试构建 JSON schema"""
        schema = self.converter.build_json_schema()

        self.assertIsInstance(schema, dict)
        self.assertIn("$schema", schema)
        self.assertIn("title", schema)
        self.assertIn("type", schema)
        self.assertIn("properties", schema)
        self.assertEqual(schema["type"], "object")

        # 验证必需字段
        self.assertIn("document", schema["properties"])

    def test_convert_metadata_to_json(self):
        """测试元数据转换为 JSON"""
        metadata = {
            "title": "Test Document",
            "author": "Test Author",
            "subject": None,
            "keywords": ["tag1", "tag2"],
            "created_date": "2024-01-01",
            "page_count": 10
        }

        result = self.converter.convert_metadata_to_json(metadata)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["title"], "Test Document")
        self.assertEqual(result["author"], "Test Author")
        self.assertIsNone(result["subject"])
        self.assertIsInstance(result["keywords"], list)


class TestToJsonPluginEdgeCases(unittest.TestCase):
    """测试 ToJsonPlugin 边界情况"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToJsonPlugin()

    def test_empty_pdf_file(self):
        """测试空 PDF 文件"""
        # 创建空文件
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            result = self.converter.convert(temp_path)
            self.assertFalse(result["success"])
            self.assertIsNotNone(result["error"])
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_corrupted_pdf_file(self):
        """测试损坏的 PDF 文件"""
        # 创建损坏的 PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name
            f.write(b"This is not a valid PDF file content")

        try:
            result = self.converter.convert(temp_path)
            self.assertFalse(result["success"])
            self.assertIsNotNone(result["error"])
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_very_long_filename(self):
        """测试非常长的文件名"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            result = self.converter.convert(temp_path)
            # 文件应该可以处理，即使内容无效
            self.assertIsNotNone(result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_unicode_filename(self):
        """测试 Unicode 文件名"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            suffix="测试.pdf",
            delete=False,
            prefix="中文"
        ) as f:
            temp_path = f.name

        try:
            result = self.converter.convert(temp_path)
            # 文件应该可以处理，即使内容无效
            self.assertIsNotNone(result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_special_characters_in_path(self):
        """测试路径中的特殊字符"""
        # 创建临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = os.path.join(tmpdir, "test file.pdf")

            # 创建文件
            with open(temp_path, "w") as f:
                f.write("")

            try:
                result = self.converter.convert(temp_path)
                self.assertIsNotNone(result)
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)


class TestToJsonPluginIntegration(unittest.TestCase):
    """测试 ToJsonPlugin 集成测试"""

    def setUp(self):
        """测试前的设置"""
        self.converter = ToJsonPlugin()
        self.test_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "test_sample.pdf"
        )

    def test_full_conversion_workflow(self):
        """测试完整转换工作流"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            output_path = f.name

        try:
            # 执行完整转换
            result = self.converter.convert(
                self.test_pdf_path,
                page_range=(1, 2),
                include_text=True,
                include_tables=True,
                include_metadata=True,
                include_structure=True,
                pretty=True,
                output_path=output_path
            )

            # 验证结果
            self.assertTrue(result["success"])
            self.assertGreater(len(result["content"]), 0)
            self.assertEqual(result["pages"], 2)  # 处理了 2 页
            self.assertEqual(result["output_path"], output_path)
            self.assertIsNone(result["error"])

            # 验证文件
            self.assertTrue(os.path.exists(output_path))

            # 验证 JSON 内容
            with open(output_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            self.assertIn("document", json_data)
            self.assertIn("metadata", json_data)
            self.assertIn("text", json_data)
            self.assertIn("tables", json_data)
            self.assertIn("structure", json_data)

            # 验证只处理了指定页面
            self.assertEqual(json_data["document"]["pages_processed"], [1, 2])

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_minimal_conversion(self):
        """测试最小转换（只提取文本）"""
        if not os.path.exists(self.test_pdf_path):
            self.skipTest(f"Test PDF file not found: {self.test_pdf_path}")

        result = self.converter.convert(
            self.test_pdf_path,
            include_text=True,
            include_tables=False,
            include_metadata=False,
            include_structure=False,
            pretty=False
        )

        self.assertTrue(result["success"])

        json_data = json.loads(result["content"])

        self.assertIn("document", json_data)
        self.assertIn("text", json_data)
        self.assertNotIn("metadata", json_data)
        self.assertNotIn("tables", json_data)
        self.assertNotIn("structure", json_data)


if __name__ == "__main__":
    # 运行所有测试
    unittest.main(verbosity=2)
