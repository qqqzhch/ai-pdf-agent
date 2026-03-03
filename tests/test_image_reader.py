"""图片读取插件单元测试"""

import os
import pytest
import tempfile
import fitz  # PyMuPDF
import base64

from plugins.readers.image_reader import ImageReaderPlugin


class TestImageReaderPlugin:
    """ImageReaderPlugin 测试类"""

    @pytest.fixture
    def plugin(self):
        """创建插件实例"""
        return ImageReaderPlugin()

    @pytest.fixture
    def sample_pdf_with_images_path(self):
        """创建包含图片的示例 PDF 文件"""
        # 创建临时 PDF 文件
        doc = fitz.open()

        # 添加第一页 - 带有图片
        page1 = doc.new_page()
        page1.insert_text(fitz.Point(50, 50), "Page 1 with Image", fontsize=12)

        # 创建一个简单的图片（红色方块）
        import io
        from PIL import Image

        # 创建一个 100x100 的红色图片
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # 插入图片到第一页
        page1.insert_image(
            fitz.Rect(100, 100, 200, 200),
            stream=img_bytes.read()
        )

        # 添加第二页 - 带有另一个图片
        page2 = doc.new_page()
        page2.insert_text(fitz.Point(50, 50), "Page 2 with Image", fontsize=12)

        # 创建一个蓝色图片
        img2 = Image.new("RGB", (150, 150), color="blue")
        img2_bytes = io.BytesIO()
        img2.save(img2_bytes, format="PNG")
        img2_bytes.seek(0)

        # 插入图片到第二页
        page2.insert_image(
            fitz.Rect(100, 100, 250, 250),
            stream=img2_bytes.read()
        )

        # 添加第三页 - 带有第三个图片（JPEG 格式）
        page3 = doc.new_page()
        page3.insert_text(fitz.Point(50, 50), "Page 3 with JPEG Image", fontsize=12)

        # 创建一个绿色 JPEG 图片
        img3 = Image.new("RGB", (200, 200), color="green")
        img3_bytes = io.BytesIO()
        img3.save(img3_bytes, format="JPEG")
        img3_bytes.seek(0)

        # 插入图片到第三页
        page3.insert_image(
            fitz.Rect(100, 100, 300, 300),
            stream=img3_bytes.read()
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
    def pdf_without_images_path(self):
        """创建不包含图片的 PDF 文件"""
        doc = fitz.open()

        # 添加三页纯文本
        for i in range(3):
            page = doc.new_page()
            page.insert_text(
                fitz.Point(50, 50),
                f"Page {i + 1} - Text Only",
                fontsize=12
            )
            page.insert_text(
                fitz.Point(50, 80),
                "This page contains only text, no images.",
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

    @pytest.fixture
    def temp_extract_dir(self):
        """创建临时提取目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir

        # 清理
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    # ========== 基本功能测试 ==========

    def test_plugin_is_available(self, plugin):
        """测试插件是否可用"""
        assert plugin.is_available()

    def test_plugin_metadata(self, plugin):
        """测试插件元数据"""
        assert plugin.name == "image_reader"
        assert plugin.version == "1.0.0"
        assert plugin.description
        assert plugin.author == "李开发"

    def test_extract_all_images(self, plugin, sample_pdf_with_images_path):
        """测试提取所有图片"""
        result = plugin.read(sample_pdf_with_images_path)

        assert result["success"] is True
        assert result["count"] >= 3  # 至少 3 张图片
        assert result["page_count"] == 3
        assert len(result["pages_extracted"]) == 3
        assert result["pages_extracted"] == [1, 2, 3]
        assert len(result["images"]) >= 3

    def test_extract_images_from_single_page(self, plugin, sample_pdf_with_images_path):
        """测试提取单页图片"""
        result = plugin.read(sample_pdf_with_images_path, page=1)

        assert result["success"] is True
        assert result["page_count"] == 3
        assert len(result["pages_extracted"]) == 1
        assert result["pages_extracted"] == [1]
        # 第一页至少应该有一张图片
        assert result["count"] >= 1

    def test_extract_images_by_page_range(self, plugin, sample_pdf_with_images_path):
        """测试按页码范围提取图片"""
        result = plugin.read(sample_pdf_with_images_path, page_range=(1, 2))

        assert result["success"] is True
        assert result["page_count"] == 3
        assert len(result["pages_extracted"]) == 2
        assert result["pages_extracted"] == [1, 2]
        # 前两页至少应该有两张图片
        assert result["count"] >= 2

    def test_extract_images_from_specific_pages(self, plugin, sample_pdf_with_images_path):
        """测试从指定页提取图片"""
        result = plugin.read(sample_pdf_with_images_path, pages=[1, 3])

        assert result["success"] is True
        assert result["page_count"] == 3
        assert len(result["pages_extracted"]) == 2
        assert result["pages_extracted"] == [1, 3]

    def test_extract_images_from_pdf_without_images(self, plugin, pdf_without_images_path):
        """测试从没有图片的 PDF 提取"""
        result = plugin.read(pdf_without_images_path)

        assert result["success"] is True
        assert result["count"] == 0
        assert len(result["images"]) == 0

    # ========== 图片保存测试 ==========

    def test_save_images_to_directory(self, plugin, sample_pdf_with_images_path, temp_extract_dir):
        """测试保存图片到目录"""
        result = plugin.read(
            sample_pdf_with_images_path,
            extract_dir=temp_extract_dir,
            format="png"
        )

        assert result["success"] is True
        assert result["count"] >= 3
        assert result["extract_dir"] == temp_extract_dir

        # 检查文件是否被保存
        saved_files = [
            f for f in os.listdir(temp_extract_dir)
            if f.endswith(".png")
        ]
        assert len(saved_files) >= 3

    def test_save_images_as_jpeg(self, plugin, sample_pdf_with_images_path, temp_extract_dir):
        """测试保存为 JPEG 格式"""
        result = plugin.read(
            sample_pdf_with_images_path,
            extract_dir=temp_extract_dir,
            format="jpeg"
        )

        assert result["success"] is True
        assert result["count"] >= 3

        # 检查 JPEG 文件
        saved_files = [
            f for f in os.listdir(temp_extract_dir)
            if f.endswith(".jpeg") or f.endswith(".jpg")
        ]
        assert len(saved_files) >= 3

    def test_save_images_with_custom_dpi(self, plugin, sample_pdf_with_images_path, temp_extract_dir):
        """测试使用自定义 DPI 保存图片"""
        result = plugin.read(
            sample_pdf_with_images_path,
            extract_dir=temp_extract_dir,
            format="png",
            dpi=300
        )

        assert result["success"] is True
        assert result["count"] >= 3

        # 验证图片已保存
        saved_files = os.listdir(temp_extract_dir)
        assert len(saved_files) >= 3

    # ========== 元数据测试 ==========

    def test_image_metadata(self, plugin, sample_pdf_with_images_path):
        """测试图片元数据"""
        result = plugin.read(
            sample_pdf_with_images_path,
            include_metadata=True
        )

        assert result["success"] is True
        assert result["count"] >= 3

        # 检查第一张图片的元数据
        first_image = result["images"][0]
        assert "page_number" in first_image
        assert "image_index" in first_image
        assert "xref" in first_image
        assert "format" in first_image
        assert "size_bytes" in first_image
        assert "extraction_time" in first_image

    def test_image_metadata_disabled(self, plugin, sample_pdf_with_images_path):
        """测试禁用图片元数据"""
        result = plugin.read(
            sample_pdf_with_images_path,
            include_metadata=False
        )

        assert result["success"] is True
        assert result["count"] >= 3

        # 检查元数据被禁用
        first_image = result["images"][0]
        assert "page_number" in first_image
        assert "format" in first_image
        # 宽度和高度等详细信息可能不存在
        assert "width" not in first_image or first_image.get("width") is None

    def test_document_metadata(self, plugin, sample_pdf_with_images_path):
        """测试文档元数据"""
        result = plugin.read(sample_pdf_with_images_path)

        assert result["success"] is True
        assert "metadata" in result
        assert isinstance(result["metadata"], dict)
        assert "page_count" in result["metadata"]

    # ========== 错误处理测试 ==========

    def test_file_not_found(self, plugin):
        """测试文件不存在"""
        result = plugin.read("/nonexistent/path/to/file.pdf")

        assert result["success"] is False
        assert result["error"]
        assert "not found" in result["error"].lower()

    def test_invalid_file_format(self, plugin):
        """测试无效文件格式"""
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

    def test_invalid_page_number_too_low(self, plugin, sample_pdf_with_images_path):
        """测试页码超出范围（太小）"""
        result = plugin.read(sample_pdf_with_images_path, page=0)

        assert result["success"] is False
        assert result["error"]
        assert "invalid page number" in result["error"].lower()

    def test_invalid_page_number_too_high(self, plugin, sample_pdf_with_images_path):
        """测试页码超出范围（太大）"""
        result = plugin.read(sample_pdf_with_images_path, page=100)

        assert result["success"] is False
        assert result["error"]
        assert "invalid page number" in result["error"].lower()

    def test_invalid_page_range(self, plugin, sample_pdf_with_images_path):
        """测试无效页面范围"""
        result = plugin.read(sample_pdf_with_images_path, page_range=(3, 1))

        assert result["success"] is False
        assert result["error"]
        assert "invalid page_range" in result["error"].lower()

    def test_invalid_page_range_out_of_bounds(self, plugin, sample_pdf_with_images_path):
        """测试页面范围超出边界"""
        result = plugin.read(sample_pdf_with_images_path, page_range=(1, 100))

        assert result["success"] is False
        assert result["error"]
        assert "invalid page_range" in result["error"].lower()

    def test_invalid_pages_list(self, plugin, sample_pdf_with_images_path):
        """测试无效页码列表"""
        result = plugin.read(sample_pdf_with_images_path, pages=[1, 100])

        assert result["success"] is False
        assert result["error"]
        assert "invalid page number" in result["error"].lower()

    def test_invalid_pages_type(self, plugin, sample_pdf_with_images_path):
        """测试页码列表类型错误"""
        result = plugin.read(sample_pdf_with_images_path, pages="not a list")

        assert result["success"] is False
        assert result["error"]
        assert "invalid pages" in result["error"].lower()

    # ========== 验证功能测试 ==========

    def test_validate_valid_pdf(self, plugin, sample_pdf_with_images_path):
        """测试验证有效的 PDF 文件"""
        is_valid, error_msg = plugin.validate(sample_pdf_with_images_path)

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

    def test_validate_input_valid(self, plugin, sample_pdf_with_images_path):
        """测试验证有效输入"""
        assert plugin.validate_input(pdf_path=sample_pdf_with_images_path) is True

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
            "images": [],
            "count": 0,
            "page_count": 1,
            "pages_extracted": [1],
            "metadata": {},
            "extract_dir": None,
            "error": None
        }
        assert plugin.validate_output(result) is True

    def test_validate_output_invalid(self, plugin):
        """测试验证无效输出"""
        result = {
            "success": True,
            "images": []
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

    # ========== 性能测试 ==========

    def test_large_pdf_performance(self, plugin):
        """测试大文件处理性能"""
        import time

        # 创建一个包含多张图片的大 PDF
        doc = fitz.open()
        for i in range(10):
            page = doc.new_page()
            page.insert_text(fitz.Point(50, 50), f"Page {i + 1}", fontsize=12)

            # 添加一张图片
            from PIL import Image
            import io

            img = Image.new("RGB", (100, 100), color="red")
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            page.insert_image(
                fitz.Rect(100, 100, 200, 200),
                stream=img_bytes.read()
            )

        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc.save(temp_file.name)
        doc.close()

        try:
            start_time = time.time()
            result = plugin.read(temp_file.name)
            elapsed_time = time.time() - start_time

            assert result["success"] is True
            assert result["count"] >= 10
            # 应该在合理时间内完成
            assert elapsed_time < 10.0
        finally:
            # 清理
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)

    # ========== 图片元数据方法测试 ==========

    def test_get_image_metadata(self, plugin):
        """测试获取图片元数据"""
        # 创建一个简单的 PNG 图片
        from PIL import Image
        import io

        img = Image.new("RGB", (100, 100), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        metadata = plugin.get_image_metadata(img_bytes.read())

        assert metadata is not None
        assert metadata.width == 100
        assert metadata.height == 100
        assert metadata.size_bytes > 0
        assert metadata.image_format == "PNG"

    def test_get_image_metadata_invalid(self, plugin):
        """测试获取无效图片元数据"""
        metadata = plugin.get_image_metadata(b"invalid image data")
        assert metadata is None

    # ========== 格式转换测试 ==========

    def test_image_format_conversion(self, plugin, sample_pdf_with_images_path, temp_extract_dir):
        """测试图片格式转换"""
        # 先保存为 PNG
        result_png = plugin.read(
            sample_pdf_with_images_path,
            extract_dir=temp_extract_dir,
            format="png"
        )

        assert result_png["success"] is True

        # 清理目录
        import shutil
        for f in os.listdir(temp_extract_dir):
            os.remove(os.path.join(temp_extract_dir, f))

        # 再保存为 JPEG
        result_jpeg = plugin.read(
            sample_pdf_with_images_path,
            extract_dir=temp_extract_dir,
            format="jpeg"
        )

        assert result_jpeg["success"] is True

        # 检查两种格式的文件都存在
        png_files = [f for f in os.listdir(temp_extract_dir) if f.endswith('.png')]
        jpeg_files = [f for f in os.listdir(temp_extract_dir) if f.endswith('.jpeg')]

        # 至少应该有 JPEG 文件
        assert len(jpeg_files) >= 3
