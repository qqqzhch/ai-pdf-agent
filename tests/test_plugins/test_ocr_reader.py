"""
OCR 文本提取插件单元测试

测试 OCR 插件的各种场景：
1. 基本功能测试
2. 图片提取测试
3. OCR 文本提取测试
4. 置信度测试
5. 多引擎测试
6. 空 PDF 处理测试
7. 错误处理测试
"""

import os
import pytest
import tempfile
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import io

from plugins.readers.ocr_reader import OCRReaderPlugin


class TestOCRReaderPlugin:
    """OCRReaderPlugin 测试类"""

    @pytest.fixture
    def plugin(self):
        """创建插件实例"""
        return OCRReaderPlugin()

    @pytest.fixture
    def sample_pdf_with_image(self):
        """创建包含图片的测试 PDF"""
        # 创建 PDF 文档
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)  # A4 尺寸

        # 创建测试图片（带有文字）
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 390, 290], outline='black', width=2)
        draw.text((50, 50), "测试文本", fill='black')
        draw.text((50, 100), "Test Text", fill='black')
        draw.text((50, 150), "Sample Text", fill='black')

        # 保存为字节
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()

        # 插入图片到 PDF
        rect = fitz.Rect(50, 50, 450, 350)
        page.insert_image(rect, stream=img_bytes)

        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc.save(temp_file.name)
        doc.close()

        yield temp_file.name

        # 清理
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    @pytest.fixture
    def empty_pdf(self):
        """创建空 PDF 文件（无图片）"""
        doc = fitz.open()
        page = doc.new_page()  # 添加一个空页
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc.save(temp_file.name)
        doc.close()

        yield temp_file.name

        # 清理
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    @pytest.fixture
    def pdf_with_multiple_images(self):
        """创建包含多张图片的 PDF"""
        doc = fitz.open()

        # 第一页：图片 1
        page = doc.new_page()
        img1 = Image.new('RGB', (300, 200), color='white')
        draw1 = ImageDraw.Draw(img1)
        draw1.text((50, 50), "Image 1 Text", fill='black')
        img1_bytes = io.BytesIO()
        img1.save(img1_bytes, format='PNG')
        rect1 = fitz.Rect(50, 50, 350, 250)
        page.insert_image(rect1, stream=img1_bytes.getvalue())

        # 第二页：图片 2
        page = doc.new_page()
        img2 = Image.new('RGB', (300, 200), color='white')
        draw2 = ImageDraw.Draw(img2)
        draw2.text((50, 50), "Image 2 Text", fill='black')
        img2_bytes = io.BytesIO()
        img2.save(img2_bytes, format='PNG')
        rect2 = fitz.Rect(50, 50, 350, 250)
        page.insert_image(rect2, stream=img2_bytes.getvalue())

        # 第三页：图片 3
        page = doc.new_page()
        img3 = Image.new('RGB', (300, 200), color='white')
        draw3 = ImageDraw.Draw(img3)
        draw3.text((50, 50), "Image 3 Text", fill='black')
        img3_bytes = io.BytesIO()
        img3.save(img3_bytes, format='PNG')
        rect3 = fitz.Rect(50, 50, 350, 250)
        page.insert_image(rect3, stream=img3_bytes.getvalue())

        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc.save(temp_file.name)
        doc.close()

        yield temp_file.name

        # 清理
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    # ========== 基本功能测试 ==========

    def test_plugin_import(self):
        """测试插件可以正常导入"""
        from plugins.readers.ocr_reader import OCRReaderPlugin
        assert OCRReaderPlugin is not None

    def test_plugin_metadata(self, plugin):
        """测试插件元数据"""
        assert plugin.name == "ocr_reader"
        assert plugin.version == "1.0.0"
        assert plugin.description
        assert "OCR" in plugin.description
        assert plugin.author == "李开发"

    def test_plugin_type(self, plugin):
        """测试插件类型"""
        from core.plugin_system.plugin_type import PluginType
        assert plugin.plugin_type == PluginType.READER

    def test_get_help(self, plugin):
        """测试获取帮助信息"""
        help_text = plugin.get_help()
        assert isinstance(help_text, str)
        assert len(help_text) > 0
        assert "OCR" in help_text
        assert "Tesseract" in help_text
        assert "PaddleOCR" in help_text

    # ========== 验证功能测试 ==========

    def test_validate_valid_pdf(self, plugin, sample_pdf_with_image):
        """测试验证有效的 PDF 文件"""
        is_valid, error_msg = plugin.validate(sample_pdf_with_image)
        assert is_valid is True
        assert error_msg is None

    def test_validate_nonexistent_file(file, plugin):
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

    def test_validate_input_valid(self, plugin, sample_pdf_with_image):
        """测试验证有效输入"""
        assert plugin.validate_input(pdf_path=sample_pdf_with_image) is True

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
            "content": [],
            "metadata": {},
            "page_count": 1,
            "pages_processed": [],
            "image_count": 0,
            "text_block_count": 0,
            "engine": "tesseract",
            "error": None
        }
        assert plugin.validate_output(result) is True

    def test_validate_output_invalid(self, plugin):
        """测试验证无效输出"""
        result = {
            "success": True,
            "content": []
        }
        assert plugin.validate_output(result) is False

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

    def test_empty_pdf_handling(self, plugin, empty_pdf):
        """测试空 PDF 处理"""
        result = plugin.read(empty_pdf)

        # 空 PDF 应该成功处理，但没有图片
        assert result["success"] is True
        assert result["image_count"] == 0
        assert result["text_block_count"] == 0
        assert len(result["content"]) == 0
        assert result["error"] is None

    def test_invalid_page_number_too_low(self, plugin, sample_pdf_with_image):
        """测试页码超出范围（太小）"""
        result = plugin.read(sample_pdf_with_image, page=0)

        assert result["success"] is False
        assert result["error"]
        assert "invalid page number" in result["error"].lower()

    def test_invalid_page_number_too_high(self, plugin, sample_pdf_with_image):
        """测试页码超出范围（太大）"""
        result = plugin.read(sample_pdf_with_image, page=100)

        assert result["success"] is False
        assert result["error"]
        assert "invalid page number" in result["error"].lower()

    def test_invalid_page_range(self, plugin, sample_pdf_with_image):
        """测试无效页面范围"""
        # 起始页大于结束页
        result = plugin.read(sample_pdf_with_image, page_range=(3, 1))

        assert result["success"] is False
        assert result["error"]
        assert "invalid page_range" in result["error"].lower()

    def test_invalid_page_range_out_of_bounds(self, plugin, sample_pdf_with_image):
        """测试页面范围超出边界"""
        result = plugin.read(sample_pdf_with_image, page_range=(1, 100))

        assert result["success"] is False
        assert result["error"]
        assert "invalid page_range" in result["error"].lower()

    def test_invalid_pages_list(self, plugin, sample_pdf_with_image):
        """测试无效页码列表"""
        result = plugin.read(sample_pdf_with_image, pages=[1, 100])

        assert result["success"] is False
        assert result["error"]
        assert "invalid page numbers" in result["error"].lower()

    # ========== OCR 引擎测试 ==========

    @pytest.mark.skipif(
        not os.path.exists("/usr/bin/tesseract"),
        reason="Tesseract 未安装"
    )
    def test_ocr_with_tesseract(self, plugin, sample_pdf_with_image):
        """测试 Tesseract OCR 提取"""
        result = plugin.read(sample_pdf_with_image, engine="tesseract")

        assert result["success"] is True
        assert result["engine"] == "tesseract"
        assert result["image_count"] > 0
        assert isinstance(result["content"], list)

        # 验证每个文本块的结构
        for block in result["content"]:
            assert "text" in block
            assert "bbox" in block
            assert "page_num" in block
            assert "confidence" in block
            assert "engine" in block

            assert isinstance(block["text"], str)
            assert isinstance(block["bbox"], tuple)
            assert len(block["bbox"]) == 4
            assert isinstance(block["page_num"], int)
            assert 0 <= block["confidence"] <= 1
            assert block["engine"] == "tesseract"

    @pytest.mark.skipif(
        not os.path.exists("/usr/bin/tesseract"),
        reason="Tesseract 未安装"
    )
    def test_confidence_threshold_filtering(self, plugin, sample_pdf_with_image):
        """测试置信度阈值过滤"""
        # 使用高置信度阈值
        result = plugin.read(
            sample_pdf_with_image,
            engine="tesseract",
            confidence_threshold=0.9
        )

        assert result["success"] is True

        # 验证置信度阈值
        for block in result["content"]:
            assert block["confidence"] >= 0.9

    @pytest.mark.skipif(
        not os.path.exists("/usr/bin/tesseract"),
        reason="Tesseract 未安装"
    )
    def test_multiple_pages_ocr(self, plugin, pdf_with_multiple_images):
        """测试多页 PDF OCR 提取"""
        result = plugin.read(pdf_with_multiple_images, engine="tesseract")

        assert result["success"] is True
        assert result["page_count"] == 3
        assert result["image_count"] == 3
        assert len(result["pages_processed"]) == 3

        # 验证所有页面都被处理
        assert set(result["pages_processed"]) == {1, 2, 3}

    @pytest.mark.skipif(
        not os.path.exists("/usr/bin/tesseract"),
        reason="Tesseract 未安装"
    )
    def test_single_page_extraction(self, plugin, pdf_with_multiple_images):
        """测试提取单页 OCR"""
        result = plugin.read(pdf_with_multiple_images, engine="tesseract", page=2)

        assert result["success"] is True
        assert result["page_count"] == 3
        assert len(result["pages_processed"]) == 1
        assert result["pages_processed"] == [2]

    @pytest.mark.skipif(
        not os.path.exists("/usr/bin/tesseract"),
        reason="Tesseract 未安装"
    )
    def test_page_range_extraction(self, plugin, pdf_with_multiple_images):
        """测试提取页面范围 OCR"""
        result = plugin.read(
            pdf_with_multiple_images,
            engine="tesseract",
            page_range=(1, 2)
        )

        assert result["success"] is True
        assert result["page_count"] == 3
        assert len(result["pages_processed"]) == 2
        assert set(result["pages_processed"]) == {1, 2}

    @pytest.mark.skipif(
        not os.path.exists("/usr/bin/tesseract"),
        reason="Tesseract 未安装"
    )
    def test_specific_pages_extraction(self, plugin, pdf_with_multiple_images):
        """测试提取指定页列表 OCR"""
        result = plugin.read(
            pdf_with_multiple_images,
            engine="tesseract",
            pages=[1, 3]
        )

        assert result["success"] is True
        assert result["page_count"] == 3
        assert len(result["pages_processed"]) == 2
        assert set(result["pages_processed"]) == {1, 3}

    @pytest.mark.skipif(
        not os.path.exists("/usr/bin/tesseract"),
        reason="Tesseract 未安装"
    )
    def test_metadata_extraction(self, plugin, sample_pdf_with_image):
        """测试元数据提取"""
        result = plugin.read(sample_pdf_with_image, engine="tesseract")

        assert result["success"] is True
        assert "metadata" in result
        assert isinstance(result["metadata"], dict)

    # ========== PaddleOCR 测试 ==========

    @pytest.mark.skip(reason="PaddleOCR 测试需要安装，运行时间长")
    def test_ocr_with_paddleocr(self, plugin, sample_pdf_with_image):
        """测试 PaddleOCR 提取"""
        result = plugin.read(sample_pdf_with_image, engine="paddleocr")

        assert result["success"] is True
        assert result["engine"] == "paddleocr"
        assert result["image_count"] > 0
        assert isinstance(result["content"], list)

        # 验证每个文本块的结构
        for block in result["content"]:
            assert "text" in block
            assert "bbox" in block
            assert "page_num" in block
            assert "confidence" in block
            assert "engine" in block
            assert block["engine"] == "paddleocr"

    # ========== 边界情况测试 ==========

    @pytest.mark.skipif(
        not os.path.exists("/usr/bin/tesseract"),
        reason="Tesseract 未安装"
    )
    def test_pdf_without_images(self, plugin, empty_pdf):
        """测试没有图片的 PDF"""
        result = plugin.read(empty_pdf, engine="tesseract")

        assert result["success"] is True
        assert result["image_count"] == 0
        assert result["text_block_count"] == 0
        assert len(result["content"]) == 0

    # ========== 执行接口测试 ==========

    @pytest.mark.skipif(
        not os.path.exists("/usr/bin/tesseract"),
        reason="Tesseract 未安装"
    )
    def test_execute_interface(self, plugin, sample_pdf_with_image):
        """测试 execute 接口"""
        result = plugin.execute(
            pdf_path=sample_pdf_with_image,
            engine="tesseract"
        )

        assert result["success"] is True
        assert result["engine"] == "tesseract"

    def test_execute_missing_pdf_path(self, plugin):
        """测试 execute 接口缺少 pdf_path"""
        result = plugin.execute()

        assert result["success"] is False
        assert result["error"]
        assert "pdf_path" in result["error"].lower()

    # ========== 坐标信息测试 ==========

    @pytest.mark.skipif(
        not os.path.exists("/usr/bin/tesseract"),
        reason="Tesseract 未安装"
    )
    def test_bbox_coordinates(self, plugin, sample_pdf_with_image):
        """测试边界框坐标信息"""
        result = plugin.read(sample_pdf_with_image, engine="tesseract")

        assert result["success"] is True

        for block in result["content"]:
            bbox = block["bbox"]
            x0, y0, x1, y1 = bbox

            # 验证坐标是有效的
            assert x0 >= 0 and y0 >= 0
            assert x1 > x0
            assert y1 > y0

            # 验证坐标范围合理（A4 页面大小约 595x842）
            assert x1 < 1000
            assert y1 < 1500

    # ========== 语言设置测试 ==========

    @pytest.mark.skipif(
        not os.path.exists("/usr/bin/tesseract"),
        reason="Tesseract 未安装"
    )
    def test_language_setting(self, plugin, sample_pdf_with_image):
        """测试语言设置"""
        # 测试英文
        result = plugin.read(
            sample_pdf_with_image,
            engine="tesseract",
            language="eng"
        )

        assert result["success"] is True
        assert result["engine"] == "tesseract"

        # 测试中英文
        result = plugin.read(
            sample_pdf_with_image,
            engine="tesseract",
            language="chi_sim+eng"
        )

        assert result["success"] is True
