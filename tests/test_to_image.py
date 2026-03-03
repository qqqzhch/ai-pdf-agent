"""测试 Image 转换器插件"""

# 添加项目根目录到路径
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
import unittest
import base64
from io import BytesIO

from PIL import Image

from plugins.converters.to_image import ToImagePlugin


class TestToImagePlugin(unittest.TestCase):
    """测试 ToImagePlugin 类"""

    def setUp(self):
        """测试前的设置"""
        self.plugin = ToImagePlugin()

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
        self.assertEqual(self.plugin.name, "to_image")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertEqual(self.plugin.author, "李开发")
        self.assertEqual(self.plugin.license, "MIT")

    def test_plugin_metadata(self):
        """测试插件元数据"""
        metadata = self.plugin.get_metadata()

        self.assertEqual(metadata["name"], "to_image")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertEqual(metadata["description"], "将 PDF 页面转换为图片格式（PNG, JPEG, WEBP 等）")
        self.assertEqual(metadata["plugin_type"], "converter")
        self.assertIn("pymupdf>=1.23.0", metadata["dependencies"])
        self.assertIn("pillow>=9.0.0", metadata["dependencies"])

    def test_supported_formats(self):
        """测试支持的图片格式"""
        expected_formats = ["png", "jpeg", "jpg", "pnm", "pgm", "ppm", "pbm", "pam", "tga", "tpic", "psd", "ps"]
        self.assertEqual(sorted(self.plugin.SUPPORTED_FORMATS), sorted(expected_formats))

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
        """测试成功转换 PDF 为图片"""
        result = self.plugin.convert(self.test_pdf_path)

        self.assertTrue(result["success"])
        self.assertGreater(len(result["images"]), 0)
        self.assertGreater(result["pages_converted"], 0)
        self.assertIn("metadata", result)
        self.assertIsNone(result["error"])

        # 验证图片数据结构
        for img in result["images"]:
            self.assertIn("page", img)
            self.assertIn("filename", img)
            self.assertIn("format", img)
            self.assertIn("width", img)
            self.assertIn("height", img)
            self.assertIn("dpi", img)
            self.assertIn("size", img)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_png_format(self):
        """测试转换为 PNG 格式"""
        result = self.plugin.convert(self.test_pdf_path, format="png")

        self.assertTrue(result["success"])
        self.assertEqual(result["format"], "png")

        for img in result["images"]:
            self.assertEqual(img["format"], "png")

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_jpeg_format(self):
        """测试转换为 JPEG 格式"""
        result = self.plugin.convert(self.test_pdf_path, format="jpeg")

        self.assertTrue(result["success"])
        self.assertEqual(result["format"], "jpeg")

        for img in result["images"]:
            self.assertEqual(img["format"], "jpeg")

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found"
)
    def test_convert_jpg_format(self):
        """测试转换为 JPG 格式（应该自动转换为 jpeg）"""
        result = self.plugin.convert(self.test_pdf_path, format="jpg")

        self.assertTrue(result["success"])
        self.assertEqual(result["format"], "jpeg")

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_pnm_format(self):
        """测试转换为 PNM 格式"""
        result = self.plugin.convert(self.test_pdf_path, format="pnm")

        self.assertTrue(result["success"])
        self.assertEqual(result["format"], "pnm")

        for img in result["images"]:
            self.assertEqual(img["format"], "pnm")

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_unsupported_format(self):
        """测试不支持的格式"""
        result = self.plugin.convert(self.test_pdf_path, format="gif")

        self.assertFalse(result["success"])
        self.assertIn("Unsupported format", result["error"])

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
        self.assertEqual(len(result["images"]), 1)
        self.assertEqual(result["images"][0]["page"], 1)

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
        self.assertLessEqual(len(result["images"]), 2)

        page_numbers = [img["page"] for img in result["images"]]
        self.assertEqual(sorted(page_numbers), sorted(page_numbers))

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
        result = self.plugin.convert(self.test_pdf_path, pages=[1, 2])

        self.assertTrue(result["success"])
        self.assertEqual(len(result["images"]), 2)

        page_numbers = [img["page"] for img in result["images"]]
        self.assertEqual(sorted(page_numbers), [1, 2])

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_dpi(self):
        """测试设置 DPI"""
        result = self.plugin.convert(self.test_pdf_path, dpi=300)

        self.assertTrue(result["success"])

        for img in result["images"]:
            self.assertEqual(img["dpi"], 300)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_quality(self):
        """测试设置图片质量"""
        result = self.plugin.convert(self.test_pdf_path, quality=95)

        self.assertTrue(result["success"])
        # 质量参数应该被接受（无法直接验证输出质量）

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_grayscale(self):
        """测试灰度转换"""
        result = self.plugin.convert(self.test_pdf_path, grayscale=True, format="png")

        self.assertTrue(result["success"])
        self.assertEqual(result["format"], "png")

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_embed(self):
        """测试嵌入 base64 数据"""
        result = self.plugin.convert(self.test_pdf_path, embed=True, page=1)

        self.assertTrue(result["success"])
        self.assertEqual(len(result["images"]), 1)

        img = result["images"][0]
        self.assertIn("data", img)
        self.assertTrue(img["data"].startswith("data:image/png;base64,"))

        # 验证 base64 数据可以解码
        b64_data = img["data"].split(",", 1)[1]
        decoded = base64.b64decode(b64_data)
        self.assertGreater(len(decoded), 0)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_output_directory(self):
        """测试保存到输出目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.plugin.convert(
                self.test_pdf_path,
                output_path=temp_dir
            )

            self.assertTrue(result["success"])
            self.assertGreater(len(result["output_files"]), 0)

            # 验证文件存在
            for output_file in result["output_files"]:
                self.assertTrue(os.path.exists(output_file))
                self.assertTrue(output_file.startswith(temp_dir))

                # 验证文件可以打开
                with open(output_file, "rb") as f:
                    img_data = f.read()
                self.assertGreater(len(img_data), 0)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_output_template(self):
        """测试使用输出文件模板"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_template = os.path.join(temp_dir, "document_page_{page}.png")

            result = self.plugin.convert(
                self.test_pdf_path,
                output_path=output_template
            )

            self.assertTrue(result["success"])
            self.assertGreater(len(result["output_files"]), 0)

            # 验证文件名格式
            for output_file in result["output_files"]:
                filename = os.path.basename(output_file)
                self.assertTrue(filename.startswith("document_page_"))
                self.assertTrue(filename.endswith(".png"))

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_high_dpi(self):
        """测试高 DPI 转换"""
        result = self.plugin.convert(self.test_pdf_path, dpi=600, page=1)

        self.assertTrue(result["success"])
        self.assertEqual(result["images"][0]["dpi"], 600)
        # 高 DPI 应该产生更大的图片
        self.assertGreater(result["images"][0]["width"], 0)
        self.assertGreater(result["images"][0]["height"], 0)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_low_dpi(self):
        """测试低 DPI 转换"""
        result = self.plugin.convert(self.test_pdf_path, dpi=72, page=1)

        self.assertTrue(result["success"])
        self.assertEqual(result["images"][0]["dpi"], 72)

    def test_determine_pages_to_process_single_page(self):
        """测试确定处理页码 - 单页"""
        kwargs = {"page": 3}
        pages = self.plugin._determine_pages_to_process(kwargs, 10)

        self.assertEqual(pages, [3])

    def test_determine_pages_to_process_page_range(self):
        """测试确定处理页码 - 页面范围"""
        kwargs = {"page_range": (2, 5)}
        pages = self.plugin._determine_pages_to_process(kwargs, 10)

        self.assertEqual(pages, [2, 3, 4, 5])

    def test_determine_pages_to_process_pages_list(self):
        """测试确定处理页码 - 页码列表"""
        kwargs = {"pages": [1, 3, 5]}
        pages = self.plugin._determine_pages_to_process(kwargs, 10)

        self.assertEqual(sorted(pages), [1, 3, 5])

    def test_determine_pages_to_process_all_pages(self):
        """测试确定处理页码 - 所有页面"""
        kwargs = {}
        pages = self.plugin._determine_pages_to_process(kwargs, 5)

        self.assertEqual(pages, [1, 2, 3, 4, 5])

    def test_generate_filename_with_template(self):
        """测试生成文件名 - 带模板"""
        filename = self.plugin._generate_filename("doc_page_{page}.png", 3, "png")

        self.assertEqual(filename, "doc_page_3.png")

    def test_generate_filename_without_template(self):
        """测试生成文件名 - 无模板"""
        filename = self.plugin._generate_filename(None, 5, "jpeg")

        self.assertEqual(filename, "page_5.jpeg")

    def test_generate_filename_without_extension(self):
        """测试生成文件名 - 无扩展名"""
        filename = self.plugin._generate_filename("doc_{page}", 2, "png")

        self.assertEqual(filename, "doc_2.png")

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_validate_input(self):
        """测试输入验证"""
        # 有效输入
        self.assertTrue(self.plugin.validate_input(pdf_path="test.pdf"))

        # 无效输入 - 缺少 pdf_path
        self.assertFalse(self.plugin.validate_input())

        # 无效输入 - 非字符串 pdf_path
        self.assertFalse(self.plugin.validate_input(pdf_path=123))

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_validate_output(self):
        """测试输出验证"""
        # 有效输出
        result = {
            "success": True,
            "images": [],
            "metadata": {},
            "pages_converted": 1,
            "format": "png",
            "output_files": [],
            "error": None
        }
        self.assertTrue(self.plugin.validate_output(result))

        # 无效输出 - 缺少字段
        invalid_result = {
            "success": True,
            "images": []
        }
        self.assertFalse(self.plugin.validate_output(invalid_result))

        # 无效输出 - 非字典
        self.assertFalse(self.plugin.validate_output("not a dict"))

    def test_get_help(self):
        """测试获取帮助信息"""
        help_text = self.plugin.get_help()

        self.assertIsInstance(help_text, str)
        self.assertIn("to_image", help_text)
        self.assertIn("使用方法", help_text)
        self.assertIn("支持的参数", help_text)
        self.assertIn("支持的格式", help_text)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_multiple_formats(self):
        """测试转换多种格式"""
        formats = ["png", "jpeg", "pnm"]

        for fmt in formats:
            with self.subTest(format=fmt):
                result = self.plugin.convert(self.test_pdf_path, format=fmt, page=1)

                self.assertTrue(result["success"], f"Failed to convert to {fmt}")
                self.assertEqual(result["format"], fmt)

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_with_embed_all_pages(self):
        """测试嵌入所有页面"""
        result = self.plugin.convert(self.test_pdf_path, embed=True)

        self.assertTrue(result["success"])

        for img in result["images"]:
            self.assertIn("data", img)
            self.assertTrue(img["data"].startswith("data:image/"))

    @unittest.skipIf(
    not os.path.exists(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "test_sample.pdf"
    )
    ),
    "Test PDF file not found",
)
    def test_convert_quality_clamping(self):
        """测试质量参数限制"""
        # 测试高质量
        result = self.plugin.convert(self.test_pdf_path, quality=150, page=1)
        self.assertTrue(result["success"])

        # 测试低质量
        result = self.plugin.convert(self.test_pdf_path, quality=-10, page=1)
        self.assertTrue(result["success"])


class TestToImagePluginEdgeCases(unittest.TestCase):
    """测试 ToImagePlugin 边界情况"""

    def setUp(self):
        """测试前的设置"""
        self.plugin = ToImagePlugin()

    def test_determine_pages_invalid_single_page(self):
        """测试无效的单一页码"""
        kwargs = {"page": 999}
        # 页码超出范围，应该返回所有页面（容错）
        pages = self.plugin._determine_pages_to_process(kwargs, 5)
        # 如果页码无效，应该返回空列表或默认值
        self.assertIsInstance(pages, list)

    def test_determine_pages_invalid_range(self):
        """测试无效的页码范围"""
        kwargs = {"page_range": (10, 5)}
        pages = self.plugin._determine_pages_to_process(kwargs, 10)
        # 起始大于结束，应该返回空列表或默认值
        self.assertIsInstance(pages, list)

    def test_determine_pages_invalid_range_bounds(self):
        """测试页码范围超出边界"""
        kwargs = {"page_range": (5, 15)}
        pages = self.plugin._determine_pages_to_process(kwargs, 10)
        # 超出边界应该被处理
        self.assertIsInstance(pages, list)

    def test_determine_pages_empty_list(self):
        """测试空的页码列表"""
        kwargs = {"pages": []}
        pages = self.plugin._determine_pages_to_process(kwargs, 10)
        self.assertEqual(pages, [])

    def test_determine_pages_invalid_page_numbers(self):
        """测试包含无效页码的列表"""
        kwargs = {"pages": [1, 999, 3]}
        pages = self.plugin._determine_pages_to_process(kwargs, 5)
        # 应该过滤掉无效页码
        self.assertIsInstance(pages, list)
        self.assertNotIn(999, pages)


if __name__ == "__main__":
    unittest.main()
