"""测试 JSON 转换器插件"""

# 添加项目根目录到路径
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import tempfile
import unittest

from plugins.converters.to_json import ToJsonPlugin


class TestToJsonPlugin(unittest.TestCase):
    """测试 ToJsonPlugin 类"""

    def setUp(self):
        """测试前的设置"""
        self.plugin = ToJsonPlugin()

        # 创建测试 PDF 文件路径
        self.test_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "test_sample.pdf"
        )

    def tearDown(self):
        """测试后的清理"""
        pass

    def test_plugin_initialization(self):
        """测试插件初始化"""
        self.assertEqual(self.plugin.name, "to_json")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertEqual(self.plugin.author, "李开发")
        self.assertEqual(self.plugin.license, "MIT")

    def test_plugin_metadata(self):
        """测试插件元数据"""
        metadata = self.plugin.get_metadata()

        self.assertEqual(metadata["name"], "to_json")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertEqual(metadata["description"], "将 PDF 内容转换为 JSON 格式，支持文本、表格、元数据和文档结构的转换")
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
        """测试成功转换 PDF 为 JSON"""
        result = self.plugin.convert(self.test_pdf_path)

        self.assertTrue(result["success"])
        self.assertGreater(len(result["content"]), 0)
        self.assertGreater(result["pages"], 0)
        self.assertIn("metadata", result)
        self.assertIsNone(result["error"])

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_json_parsing(self):
        """测试转换结果可以解析为有效 JSON"""
        result = self.plugin.convert(self.test_pdf_path)

        if result["success"]:
            # 尝试解析 JSON
            try:
                json_data = json.loads(result["content"])
                self.assertIsInstance(json_data, dict)
                self.assertIn("document", json_data)
                self.assertIn("metadata", json_data)
                self.assertIn("text", json_data)
                self.assertIn("tables", json_data)
                self.assertIn("structure", json_data)
            except json.JSONDecodeError as e:
                self.fail(f"Failed to parse JSON: {e}")

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

        self.assertTrue(result["success"])

        # 解析 JSON 并验证
        json_data = json.loads(result["content"])
        self.assertEqual(json_data["document"]["pages_processed"], [1])

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

        self.assertTrue(result["success"])

        # 解析 JSON 并验证
        json_data = json.loads(result["content"])
        self.assertEqual(json_data["document"]["pages_processed"], [1, 2])

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
        result = self.plugin.convert(self.test_pdf_path, pages=[1, 3])

        self.assertTrue(result["success"])

        # 解析 JSON 并验证
        json_data = json.loads(result["content"])
        self.assertEqual(json_data["document"]["pages_processed"], [1, 3])

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_exclude_text(self):
        """测试排除文本内容"""
        result = self.plugin.convert(self.test_pdf_path, include_text=False)

        self.assertTrue(result["success"])

        # 解析 JSON 并验证
        json_data = json.loads(result["content"])
        self.assertNotIn("text", json_data)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_exclude_tables(self):
        """测试排除表格"""
        result = self.plugin.convert(self.test_pdf_path, include_tables=False)

        self.assertTrue(result["success"])

        # 解析 JSON 并验证
        json_data = json.loads(result["content"])
        self.assertNotIn("tables", json_data)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_exclude_metadata(self):
        """测试排除元数据"""
        result = self.plugin.convert(self.test_pdf_path, include_metadata=False)

        self.assertTrue(result["success"])

        # 解析 JSON 并验证
        json_data = json.loads(result["content"])
        self.assertNotIn("metadata", json_data)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_exclude_structure(self):
        """测试排除文档结构"""
        result = self.plugin.convert(self.test_pdf_path, include_structure=False)

        self.assertTrue(result["success"])

        # 解析 JSON 并验证
        json_data = json.loads(result["content"])
        self.assertNotIn("structure", json_data)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_pretty_json(self):
        """测试格式化 JSON"""
        result = self.plugin.convert(self.test_pdf_path, pretty=True)

        self.assertTrue(result["success"])

        # 检查 JSON 是否有缩进
        self.assertIn("\n", result["content"])
        self.assertIn("  ", result["content"])

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_compact_json(self):
        """测试紧凑 JSON"""
        result = self.plugin.convert(self.test_pdf_path, pretty=False)

        self.assertTrue(result["success"])

        # 检查 JSON 是否紧凑
        self.assertNotIn("\n", result["content"])

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
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            output_path = f.name

        try:
            result = self.plugin.convert(
                self.test_pdf_path,
                output_path=output_path
            )

            self.assertTrue(result["success"])
            self.assertEqual(result["output_path"], output_path)

            # 验证文件存在
            self.assertTrue(os.path.exists(output_path))

            # 读取文件内容
            with open(output_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            # 验证内容
            self.assertEqual(file_content, result["content"])

            # 验证可以解析
            json.loads(file_content)

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
    def test_convert_with_custom_schema(self):
        """测试使用自定义 schema"""
        schema = {
            "include_fields": ["document", "text"],
            "exclude_fields": []
        }

        result = self.plugin.convert(self.test_pdf_path, schema=schema)

        self.assertTrue(result["success"])

        # 解析 JSON 并验证
        json_data = json.loads(result["content"])

        # 只应该包含指定字段
        self.assertIn("document", json_data)
        self.assertIn("text", json_data)
        self.assertNotIn("metadata", json_data)
        self.assertNotIn("tables", json_data)
        self.assertNotIn("structure", json_data)

    def test_build_json_schema(self):
        """测试构建 JSON schema"""
        schema = self.plugin.build_json_schema()

        self.assertIsInstance(schema, dict)
        self.assertIn("$schema", schema)
        self.assertIn("title", schema)
        self.assertIn("type", schema)
        self.assertIn("properties", schema)
        self.assertEqual(schema["type"], "object")

        # 验证必需字段
        self.assertIn("document", schema["properties"])

    def test_apply_custom_schema_include(self):
        """测试应用自定义 schema - 包含字段"""
        data = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }

        schema = {
            "include_fields": ["field1", "field3"]
        }

        result = self.plugin.apply_custom_schema(data, schema)

        self.assertIn("field1", result)
        self.assertIn("field3", result)
        self.assertNotIn("field2", result)

    def test_apply_custom_schema_exclude(self):
        """测试应用自定义 schema - 排除字段"""
        data = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }

        schema = {
            "exclude_fields": ["field2"]
        }

        result = self.plugin.apply_custom_schema(data, schema)

        self.assertIn("field1", result)
        self.assertIn("field3", result)
        self.assertNotIn("field2", result)

    def test_apply_custom_schema_empty(self):
        """测试应用空 schema"""
        data = {
            "field1": "value1",
            "field2": "value2"
        }

        result = self.plugin.apply_custom_schema(data, None)

        # 应该返回原始数据
        self.assertEqual(result, data)

    def test_convert_metadata_to_json(self):
        """测试元数据转换"""
        metadata = {
            "title": "Test Document",
            "author": "Test Author",
            "subject": None,
            "keywords": ["tag1", "tag2"],
            "created_date": "2024-01-01"
        }

        result = self.plugin.convert_metadata_to_json(metadata)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["title"], "Test Document")
        self.assertEqual(result["author"], "Test Author")
        self.assertIsNone(result["subject"])
        self.assertIsInstance(result["keywords"], list)

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
            "content": "{}",
            "metadata": {},
            "pages": 1,
            "output_path": None,
            "error": None
        }
        self.assertTrue(self.plugin.validate_output(result))

        # 无效输出 - 缺少字段
        invalid_result = {
            "success": True,
            "content": "{}"
        }
        self.assertFalse(self.plugin.validate_output(invalid_result))

        # 无效输出 - 非字典
        self.assertFalse(self.plugin.validate_output("not a dict"))

    def test_get_help(self):
        """测试获取帮助信息"""
        help_text = self.plugin.get_help()

        self.assertIsInstance(help_text, str)
        self.assertIn("to_json", help_text)
        self.assertIn("使用方法", help_text)
        self.assertIn("支持的参数", help_text)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_document_structure(self):
        """测试文档结构信息"""
        result = self.plugin.convert(self.test_pdf_path, include_structure=True)

        self.assertTrue(result["success"])

        json_data = json.loads(result["content"])
        self.assertIn("structure", json_data)
        self.assertIn("pages", json_data["structure"])

        # 验证每个页面都有结构信息
        for page in json_data["structure"]["pages"]:
            self.assertIn("page_number", page)
            self.assertIn("width", page)
            self.assertIn("height", page)
            self.assertIn("rotation", page)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_text_blocks(self):
        """测试文本块提取"""
        result = self.plugin.convert(self.test_pdf_path, include_text=True)

        self.assertTrue(result["success"])

        json_data = json.loads(result["content"])
        self.assertIn("text", json_data)
        self.assertIn("pages", json_data["text"])

        # 验证每个页面都有文本信息
        for page in json_data["text"]["pages"]:
            self.assertIn("page_number", page)
            self.assertIn("full_text", page)
            self.assertIn("blocks", page)
            self.assertIn("char_count", page)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_table_structure(self):
        """测试表格结构"""
        result = self.plugin.convert(self.test_pdf_path, include_tables=True)

        self.assertTrue(result["success"])

        json_data = json.loads(result["content"])
        self.assertIn("tables", json_data)
        self.assertIn("total_tables", json_data["tables"])
        self.assertIn("pages", json_data["tables"])

        # 验证表格结构
        for page in json_data["tables"]["pages"]:
            self.assertIn("page_number", page)
            self.assertIn("tables", page)
            self.assertIn("table_count", page)


class TestToJsonPluginEdgeCases(unittest.TestCase):
    """测试 ToJsonPlugin 边界情况"""

    def setUp(self):
        """测试前的设置"""
        self.plugin = ToJsonPlugin()

    def test_convert_invalid_page_number(self):
        """测试无效的页码"""
        # 创建一个最小的测试 PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            # 尝试转换不存在的页码
            result = self.plugin.convert(temp_path, page=999)
            # 应该失败或返回错误
            self.assertFalse(result.get("success", True))
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_convert_invalid_page_range(self):
        """测试无效的页码范围"""
        # 创建一个最小的测试 PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            # 尝试使用无效的页码范围
            result = self.plugin.convert(temp_path, page_range=(10, 5))
            # 应该失败
            self.assertFalse(result.get("success", True))
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_convert_empty_pages_list(self):
        """测试空的页码列表"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            result = self.plugin.convert(temp_path, pages=[])
            # 应该返回错误
            self.assertFalse(result.get("success", True))
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
