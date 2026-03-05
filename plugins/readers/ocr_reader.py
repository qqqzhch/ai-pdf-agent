"""
OCR 文本提取插件 - 使用 Tesseract 或 PaddleOCR 从 PDF 图片中提取文本

功能：
1. 从 PDF 中提取所有图片
2. 使用 OCR 识别图片中的文本
3. 保留文本位置和坐标信息
4. 支持多种 OCR 引擎（Tesseract/PaddleOCR）
5. 支持置信度阈值过滤
6. 支持多语言（中文 + 英文）

作者：李开发
版本：1.0.0
"""

import io
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from core.plugin_system.base_reader_plugin import BaseReaderPlugin
from core.plugin_system.plugin_type import PluginType

logger = logging.getLogger(__name__)


class OCRReaderPlugin(BaseReaderPlugin):
    """
    OCR 文本提取插件

    使用 Tesseract 或 PaddleOCR 从 PDF 图片中提取文本。
    """

    # 插件元数据
    name = "ocr_reader"
    version = "1.0.0"
    description = "使用 Tesseract 或 PaddleOCR 从 PDF 图片中提取文本"
    plugin_type = PluginType.READER
    author = "李开发"
    homepage = ""
    license = "MIT"

    # 依赖（标记为可选，实际使用时检查）
    dependencies = []
    system_dependencies = []

    def __init__(self, pdf_engine=None):
        """
        初始化 OCR 读取插件

        Args:
            pdf_engine: PDF 引擎实例（可选）
        """
        super().__init__(pdf_engine)

        # OCR 引擎配置
        self.ocr_engine = None
        self.ocr_engine_name = None
        self.language = "chi_sim+eng"
        self.confidence_threshold = 0.6

        # 如果没有传入引擎，则创建默认的 PyMuPDF 引擎
        if self.pdf_engine is None:
            try:
                from core.engine.pymupdf_engine import PyMuPDFEngine

                self.pdf_engine = PyMuPDFEngine()
            except ImportError as e:
                logger.warning(f"Failed to import PyMuPDFEngine: {e}")
                self.pdf_engine = None

    def is_available(self) -> bool:
        """检查插件是否可用"""
        if self.pdf_engine is None:
            return False

        # 检查 OCR 引擎是否可用
        if self.ocr_engine is None:
            # 尝试初始化 OCR 引擎
            try:
                self._init_ocr_engine("tesseract")
            except Exception:
                try:
                    self._init_ocr_engine("paddleocr")
                except Exception:
                    logger.warning("No OCR engine available")
                    return False

        return True

    def _init_ocr_engine(self, engine_name: str):
        """
        初始化 OCR 引擎

        Args:
            engine_name: OCR 引擎名称 ("tesseract" 或 "paddleocr")

        Raises:
            ImportError: 如果引擎不可用
            ValueError: 如果引擎名称无效
        """
        if engine_name == "tesseract":
            try:
                import pytesseract

                # 检查 tesseract 是否安装
                pytesseract.get_tesseract_version()
                self.ocr_engine = pytesseract
                self.ocr_engine_name = "tesseract"
                logger.info("Tesseract OCR engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Tesseract: {e}")
                raise ImportError(
                    "Tesseract not installed. Install with: "
                    "pip install pytesseract && sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim"
                )
        elif engine_name == "paddleocr":
            try:
                from paddleocr import PaddleOCR

                self.ocr_engine = PaddleOCR(use_angle_cls=True, lang="ch")
                self.ocr_engine_name = "paddleocr"
                logger.info("PaddleOCR engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize PaddleOCR: {e}")
                raise ImportError(
                    "PaddleOCR not installed. Install with: pip install paddleocr"
                )
        else:
            raise ValueError(f"Unsupported OCR engine: {engine_name}")

    def _set_engine(self, engine_name: str):
        """
        设置 OCR 引擎

        Args:
            engine_name: OCR 引擎名称

        Raises:
            ValueError: 如果引擎名称无效
        """
        if self.ocr_engine_name == engine_name:
            return

        self._init_ocr_engine(engine_name)

    def _extract_images_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        从 PDF 中提取所有图片

        Args:
            pdf_path: PDF 文件路径

        Returns:
            List[Dict[str, Any]]: 图片列表
                {
                    "page_num": int,
                    "image_index": int,
                    "bbox": Tuple[float, float, float, float],  # (x0, y0, x1, y1)
                    "data": bytes  # 图片数据
                }
        """
        import fitz

        doc = fitz.open(pdf_path)
        images = []

        for page_num, page in enumerate(doc, start=1):
            image_list = page.get_images(full=True)

            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                base_image = page.parent.extract_image(xref)

                if base_image:
                    image_bytes = base_image["image"]

                    # 获取图片位置信息
                    image_rects = page.get_image_rects(xref)
                    bbox = image_rects[0] if image_rects else (0, 0, 0, 0)

                    images.append(
                        {
                            "page_num": page_num,
                            "image_index": img_index,
                            "bbox": bbox,
                            "data": image_bytes,
                        }
                    )

        doc.close()
        return images

    def _ocr_with_tesseract(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        使用 Tesseract 进行 OCR 识别

        Args:
            image_bytes: 图片数据

        Returns:
            List[Dict[str, Any]]: OCR 结果列表
        """
        import pytesseract
        from PIL import Image

        image = Image.open(io.BytesIO(image_bytes))

        try:
            # 使用 image_to_data 获取位置信息
            data = pytesseract.image_to_data(
                image, lang=self.language, output_type=pytesseract.Output.DICT
            )

            blocks = []
            for i, text in enumerate(data["text"]):
                if text.strip():  # 忽略空文本
                    confidence = data["conf"][i] / 100.0

                    if confidence >= self.confidence_threshold:
                        blocks.append(
                            {
                                "text": text,
                                "bbox": (
                                    data["left"][i],
                                    data["top"][i],
                                    data["left"][i] + data["width"][i],
                                    data["top"][i] + data["height"][i],
                                ),
                                "confidence": confidence,
                            }
                        )

            return blocks
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            raise

    def _ocr_with_paddleocr(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        使用 PaddleOCR 进行 OCR 识别

        Args:
            image_bytes: 图片数据

        Returns:
            List[Dict[str, Any]]: OCR 结果列表
        """
        from PIL import Image

        image = Image.open(io.BytesIO(image_bytes))

        try:
            # PaddleOCR 需要 RGB 模式
            if image.mode != "RGB":
                image = image.convert("RGB")

            # 执行 OCR
            result = self.ocr_engine.ocr(image, cls=True)

            blocks = []
            if result and result[0]:
                for line in result[0]:
                    box = line[0]  # 坐标框
                    text_info = line[1]  # 文本信息
                    text = text_info[0]
                    confidence = text_info[1]

                    if confidence >= self.confidence_threshold:
                        # 转换坐标
                        x_coords = [point[0] for point in box]
                        y_coords = [point[1] for point in box]

                        blocks.append(
                            {
                                "text": text,
                                "bbox": (
                                    min(x_coords),
                                    min(y_coords),
                                    max(x_coords),
                                    max(y_coords),
                                ),
                                "confidence": confidence,
                            }
                        )

            return blocks
        except Exception as e:
            logger.error(f"PaddleOCR OCR failed: {e}")
            raise

    def read(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        从 PDF 中提取 OCR 文本

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - engine: str - OCR 引擎（"tesseract" 或 "paddleocr"）
                - language: str - OCR 语言（仅 Tesseract，默认："chi_sim+eng"）
                - confidence_threshold: float - 置信度阈值（0-1，默认：0.6）
                - page: int - 指定页码（1-based）
                - page_range: Tuple[int, int] - 页面范围 (start, end)，1-based
                - pages: List[int] - 多个页码列表，1-based

        Returns:
            Dict[str, Any]: 结构化结果
                {
                    "success": bool,
                    "content": List[Dict],  # OCR 文本块列表
                    "metadata": Dict,  # 文档元数据
                    "page_count": int,  # 总页数
                    "pages_processed": List[int],  # 处理的页码列表
                    "image_count": int,  # 提取的图片数量
                    "text_block_count": int,  # 文本块数量
                    "engine": str,  # 使用的 OCR 引擎
                    "error": Optional[str]  # 错误信息
                }
        """
        result = {
            "success": False,
            "content": [],
            "metadata": {},
            "page_count": 0,
            "pages_processed": [],
            "image_count": 0,
            "text_block_count": 0,
            "engine": None,
            "error": None,
        }

        try:
            # 验证文件
            is_valid, error_msg = self.validate(pdf_path)
            if not is_valid:
                result["error"] = error_msg
                return result

            # 获取文档信息（用于页面验证）
            doc = self.pdf_engine.open(pdf_path)
            page_count = self.pdf_engine.get_page_count(doc)
            result["page_count"] = page_count
            result["metadata"] = self.pdf_engine.get_metadata(doc)
            self.pdf_engine.close(doc)

            # 验证页面参数（在初始化 OCR 引擎之前）
            if "page" in kwargs:
                page_num = kwargs["page"]
                if (
                    not isinstance(page_num, int)
                    or page_num < 1
                    or page_num > page_count
                ):
                    result["error"] = (
                        f"Invalid page number: {page_num}. "
                        f"Must be between 1 and {page_count}"
                    )
                    return result
            elif "page_range" in kwargs:
                page_range = kwargs["page_range"]
                if not isinstance(page_range, (tuple, list)) or len(page_range) != 2:
                    result["error"] = (
                        f"Invalid page_range: {page_range}. Must be a tuple/list of 2 integers"
                    )
                    return result
                start, end = page_range
                if start < 1 or end > page_count or start > end:
                    result["error"] = (
                        f"Invalid page_range: ({start}, {end}). "
                        f"Must be between 1 and {page_count}, with start <= end"
                    )
                    return result
            elif "pages" in kwargs:
                pages = kwargs["pages"]
                if not isinstance(pages, list) or not all(
                    isinstance(p, int) for p in pages
                ):
                    result["error"] = (
                        f"Invalid pages: {pages}. Must be a list of integers"
                    )
                    return result
                if not all(1 <= p <= page_count for p in pages):
                    result["error"] = (
                        f"Invalid page numbers. Must be between 1 and {page_count}"
                    )
                    return result

            # 处理额外参数
            engine = kwargs.get("engine", "tesseract")
            language = kwargs.get("language", "chi_sim+eng")
            confidence_threshold = kwargs.get("confidence_threshold", 0.6)

            # 设置语言和置信度阈值
            self.language = language
            self.confidence_threshold = confidence_threshold

            # 提取图片
            images = self._extract_images_from_pdf(pdf_path)
            result["image_count"] = len(images)

            # 如果没有图片，直接返回成功（不需要初始化 OCR 引擎）
            if not images:
                logger.info(f"No images found in {pdf_path}")
                result["success"] = True
                result["engine"] = engine
                return result

            # 初始化或切换 OCR 引擎（只在有图片时才初始化）
            try:
                self._set_engine(engine)
            except Exception as e:
                result["error"] = f"Failed to initialize OCR engine: {str(e)}"
                return result

            result["engine"] = engine

            # 过滤图片（根据页面参数）
            page_filter = None
            if "page" in kwargs:
                page_num = kwargs["page"]
                if page_num < 1 or page_num > result["page_count"]:
                    result["error"] = (
                        f"Invalid page number: {page_num}. "
                        f"Must be between 1 and {result['page_count']}"
                    )
                    return result
                page_filter = {page_num}
            elif "page_range" in kwargs:
                start, end = kwargs["page_range"]
                if start < 1 or end > result["page_count"] or start > end:
                    result["error"] = (
                        f"Invalid page_range: ({start}, {end}). "
                        f"Must be between 1 and {result['page_count']}, with start <= end"
                    )
                    return result
                page_filter = set(range(start, end + 1))
            elif "pages" in kwargs:
                pages = kwargs["pages"]
                if not all(1 <= p <= result["page_count"] for p in pages):
                    result["error"] = (
                        f"Invalid page numbers. Must be between 1 and {result['page_count']}"
                    )
                    return result
                page_filter = set(pages)

            # 执行 OCR
            content = []
            pages_processed = set()

            for img_info in images:
                page_num = img_info["page_num"]

                # 应用页面过滤
                if page_filter is not None and page_num not in page_filter:
                    continue

                pages_processed.add(page_num)

                try:
                    # 执行 OCR
                    if engine == "tesseract":
                        ocr_blocks = self._ocr_with_tesseract(img_info["data"])
                    elif engine == "paddleocr":
                        ocr_blocks = self._ocr_with_paddleocr(img_info["data"])
                    else:
                        result["error"] = f"Unsupported OCR engine: {engine}"
                        return result

                    # 合并位置信息
                    page_bbox = img_info["bbox"]
                    for block in ocr_blocks:
                        local_bbox = block["bbox"]
                        # 调整全局坐标
                        block["bbox"] = (
                            page_bbox[0] + local_bbox[0],
                            page_bbox[1] + local_bbox[1],
                            page_bbox[0] + local_bbox[2],
                            page_bbox[1] + local_bbox[3],
                        )
                        # 添加额外信息
                        block["page_num"] = page_num
                        block["engine"] = engine

                    content.extend(ocr_blocks)
                    logger.info(
                        f"Page {page_num}, image {img_info['image_index']}: "
                        f"extracted {len(ocr_blocks)} text blocks"
                    )

                except Exception as e:
                    logger.error(
                        f"Page {page_num}, image {img_info['image_index']} OCR failed: {e}"
                    )
                    continue

            result["success"] = True
            result["content"] = content
            result["pages_processed"] = sorted(pages_processed)
            result["text_block_count"] = len(content)

        except FileNotFoundError:
            result["error"] = f"File not found: {pdf_path}"
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}", exc_info=True)
            result["error"] = str(e)

        return result

    def validate(self, pdf_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证 PDF 文件

        Args:
            pdf_path: PDF 文件路径

        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            return False, f"File not found: {pdf_path}"

        # 检查文件是否为普通文件
        if not os.path.isfile(pdf_path):
            return False, f"Path is not a file: {pdf_path}"

        # 检查文件扩展名
        if not pdf_path.lower().endswith(".pdf"):
            return False, f"File is not a PDF: {pdf_path}"

        # 检查文件是否可读
        if not os.access(pdf_path, os.R_OK):
            return False, f"File is not readable: {pdf_path}"

        # 尝试打开 PDF 文件验证格式
        try:
            if self.pdf_engine is None:
                return False, "PDF engine not available"

            doc = self.pdf_engine.open(pdf_path)

            # 检查是否为有效的 PDF
            if doc.is_encrypted:
                self.pdf_engine.close(doc)
                return False, "PDF is encrypted and requires password"

            # 获取页数验证
            page_count = self.pdf_engine.get_page_count(doc)
            if page_count <= 0:
                self.pdf_engine.close(doc)
                return False, "PDF has no pages"

            self.pdf_engine.close(doc)

        except Exception as e:
            logger.error(f"Error validating PDF {pdf_path}: {e}", exc_info=True)
            return False, f"Invalid PDF file: {str(e)}"

        return True, None

    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        if "pdf_path" not in kwargs:
            return False

        pdf_path = kwargs["pdf_path"]
        if not isinstance(pdf_path, str):
            return False

        return True

    def validate_output(self, result: Any) -> bool:
        """验证输出结果"""
        if not isinstance(result, dict):
            return False

        required_keys = [
            "success",
            "content",
            "metadata",
            "page_count",
            "pages_processed",
            "image_count",
            "text_block_count",
            "engine",
            "error",
        ]
        for key in required_keys:
            if key not in result:
                return False

        return True

    def get_help(self) -> str:
        """获取插件帮助信息"""
        return """
OCR 文本提取插件帮助
====================

功能：
  使用 Tesseract 或 PaddleOCR 从 PDF 图片中提取文本，保留位置和坐标信息。

用法示例：
  # 使用 Tesseract OCR（默认）
  plugin = OCRReaderPlugin()
  result = plugin.read("document.pdf", engine="tesseract")

  # 使用 PaddleOCR
  result = plugin.read("document.pdf", engine="paddleocr")

  # 设置语言（仅 Tesseract）
  result = plugin.read("document.pdf", engine="tesseract", language="chi_sim+eng")

  # 设置置信度阈值
  result = plugin.read("document.pdf", confidence_threshold=0.8)

  # 提取指定页面
  result = plugin.read("document.pdf", page=1)

  # 提取页面范围
  result = plugin.read("document.pdf", page_range=(1, 5))

  # 提取指定页列表
  result = plugin.read("document.pdf", pages=[1, 3, 5])

配置参数：
  pdf_path: str - PDF 文件路径（必需）
  engine: str - OCR 引擎（"tesseract" 或 "paddleocr"，默认："tesseract"）
  language: str - OCR 语言（仅 Tesseract，默认："chi_sim+eng"）
  confidence_threshold: float - 置信度阈值（0-1，默认：0.6）
  page: int - 指定页码（1-based）
  page_range: Tuple[int, int] - 页面范围 (start, end)，1-based
  pages: List[int] - 多个页码列表，1-based

返回格式：
  {
    "success": bool,
    "content": [
      {
        "text": "识别的文本",
        "bbox": (x0, y0, x1, y1),
        "page_num": 1,
        "confidence": 0.95,
        "engine": "tesseract"
      },
      ...
    ],
    "metadata": {...},  # 文档元数据
    "page_count": int,  # 总页数
    "pages_processed": [1, 2, ...],  # 处理的页码列表
    "image_count": int,  # 提取的图片数量
    "text_block_count": int,  # 文本块数量
    "engine": "tesseract",  # 使用的 OCR 引擎
    "error": None
  }

依赖安装：
  # Tesseract OCR
  pip install pytesseract
  sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

  # PaddleOCR
  pip install paddleocr

注意事项：
  - OCR 是 CPU 密集型操作，处理大文件可能需要较长时间
  - 置信度阈值可以过滤低质量的识别结果
  - Tesseract 支持更多语言配置
  - PaddleOCR 对中文识别效果更好，但首次运行会下载模型文件
"""
