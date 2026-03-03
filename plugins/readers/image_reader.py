"""图片读取插件 - 使用 PyMuPDF 提取 PDF 图片"""

import os
from typing import Dict, Optional, Any, Tuple, List, Generator
import logging
from dataclasses import dataclass
from datetime import datetime

from core.plugin_system.base_reader_plugin import BaseReaderPlugin
from core.plugin_system.plugin_type import PluginType

logger = logging.getLogger(__name__)


@dataclass
class ImageMetadata:
    """图片元数据"""
    page_number: int  # 页码（1-based）
    image_index: int  # 图片索引
    width: int  # 宽度
    height: int  # 高度
    xref: int  # 引用号
    bbox: Tuple[float, float, float, float]  # 边界框
    transform: Optional[Tuple[float, float, float, float, float, float]]  # 变换矩阵
    image_format: str  # 图片格式
    size_bytes: int  # 字节大小
    cs_name: Optional[str]  # 颜色空间名称
    n_channels: Optional[int]  # 通道数
    bpc: Optional[int]  # 每通道位数
    mask: Optional[int]  # 掩码引用
    extraction_time: str  # 提取时间


class ImageReaderPlugin(BaseReaderPlugin):
    """图片读取插件 - 提取 PDF 图片内容"""

    # 插件元数据
    name = "image_reader"
    version = "1.0.0"
    description = "使用 PyMuPDF 提取 PDF 图片，支持按页、按范围提取，返回图片元数据"
    plugin_type = PluginType.READER
    author = "李开发"
    homepage = ""
    license = "MIT"

    # 依赖
    dependencies = ["pymupdf>=1.23.0"]
    system_dependencies = []

    def __init__(self, pdf_engine=None):
        """
        初始化图片读取插件

        Args:
            pdf_engine: PDF 引擎实例（可选）
        """
        super().__init__(pdf_engine)

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

        # 检查依赖
        deps_ok, missing_deps = self.check_dependencies()
        if not deps_ok:
            logger.warning(f"Missing dependencies: {missing_deps}")
            return False

        return True

    def read(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        读取 PDF 图片内容

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - page: int: 指定页码（1-based）
                - page_range: Tuple[int, int]: 页面范围 (start, end)，1-based
                - pages: List[int]: 多个页码列表，1-based
                - extract_dir: str: 保存图片的目录
                - format: str: 保存格式（png, jpeg, ppm, pbm, pam）
                - dpi: int: 图片 DPI（默认：150）
                - include_metadata: bool: 是否包含详细元数据（默认：True）

        Returns:
            Dict[str, Any]: 结构化结果
                {
                    "success": bool,
                    "images": List[Dict],  # 图片列表
                    "count": int,  # 图片总数
                    "page_count": int,  # 总页数
                    "pages_extracted": List[int],  # 提取的页码列表
                    "metadata": Dict,  # 文档元数据
                    "extract_dir": Optional[str],  # 保存目录
                    "error": Optional[str]  # 错误信息
                }
        """
        result = {
            "success": False,
            "images": [],
            "count": 0,
            "page_count": 0,
            "pages_extracted": [],
            "metadata": {},
            "extract_dir": None,
            "error": None,
        }

        try:
            # 验证文件
            is_valid, error_msg = self.validate(pdf_path)
            if not is_valid:
                result["error"] = error_msg
                return result

            # 获取保存参数
            extract_dir = kwargs.get("extract_dir")
            image_format = kwargs.get("format", "png")
            dpi = kwargs.get("dpi", 150)
            include_metadata = kwargs.get("include_metadata", True)

            # 打开文档
            doc = self.pdf_engine.open(pdf_path)

            # 获取页数
            page_count = self.pdf_engine.get_page_count(doc)
            result["page_count"] = page_count

            # 获取元数据
            result["metadata"] = self.pdf_engine.get_metadata(doc)

            # 确定要提取的页码范围
            pages_to_extract = []

            if "page" in kwargs:
                page_num = kwargs["page"]
                if not isinstance(page_num, int) or page_num < 1 or page_num > page_count:
                    msg = f"Invalid page number: {page_num}. Must be between 1 and {page_count}"
                    result["error"] = msg
                    self.pdf_engine.close(doc)
                    return result
                pages_to_extract = [page_num]
            elif "page_range" in kwargs:
                page_range = kwargs["page_range"]
                if not isinstance(page_range, (tuple, list)) or len(page_range) != 2:
                    result["error"] = (
                        f"Invalid page_range: {page_range}. "
                        f"Must be a tuple/list of 2 integers"
                    )
                    self.pdf_engine.close(doc)
                    return result
                start, end = page_range
                if start < 1 or end > page_count or start > end:
                    msg = (
                        f"Invalid page_range: ({start}, {end}). "
                        f"Must be between 1 and {page_count}, with start <= end"
                    )
                    result["error"] = msg
                    self.pdf_engine.close(doc)
                    return result
                pages_to_extract = list(range(start, end + 1))
            elif "pages" in kwargs:
                pages = kwargs["pages"]
                if not isinstance(pages, list) or not all(
                    isinstance(p, int) for p in pages
                ):
                    result["error"] = f"Invalid pages: {pages}. Must be a list of integers"
                    self.pdf_engine.close(doc)
                    return result
                for page_num in pages:
                    if page_num < 1 or page_num > page_count:
                        msg = f"Invalid page number: {page_num}. Must be between 1 and {page_count}"
                        result["error"] = msg
                        self.pdf_engine.close(doc)
                        return result
                pages_to_extract = sorted(pages)
            else:
                pages_to_extract = list(range(1, page_count + 1))

            result["pages_extracted"] = pages_to_extract

            # 创建保存目录
            if extract_dir:
                os.makedirs(extract_dir, exist_ok=True)
                result["extract_dir"] = extract_dir

            # 提取图片
            images = []
            for page_num in pages_to_extract:
                page_images = list(self.extract_images(
                    doc,
                    page_num,
                    extract_dir=extract_dir,
                    image_format=image_format,
                    dpi=dpi,
                    include_metadata=include_metadata
                ))
                images.extend(page_images)

            # 关闭文档
            self.pdf_engine.close(doc)

            # 设置结果
            result["success"] = True
            result["images"] = images
            result["count"] = len(images)

        except FileNotFoundError:
            result["error"] = f"File not found: {pdf_path}"
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}", exc_info=True)
            result["error"] = str(e)

        return result

    def extract_images(
        self,
        doc,
        page_num: int,
        extract_dir: Optional[str] = None,
        image_format: str = "png",
        dpi: int = 150,
        include_metadata: bool = True
    ) -> Generator[Dict[str, Any], None, None]:
        """
        提取指定页面的所有图片（生成器）

        Args:
            doc: PyMuPDF 文档对象
            page_num: 页码（1-based）
            extract_dir: 保存目录（可选）
            image_format: 图片格式（png, jpeg, ppm, pbm, pam）
            dpi: 图片 DPI
            include_metadata: 是否包含详细元数据

        Yields:
            Dict[str, Any]: 图片信息
        """
        # 获取页面（0-based）
        page = doc[page_num - 1]

        # 获取页面上的所有图片
        image_list = page.get_images(full=True)

        for img_index, img_info in enumerate(image_list):
            try:
                xref = img_info[0]

                # 提取基础图片
                base_image = doc.extract_image(xref)

                if base_image is None:
                    logger.warning(f"Failed to extract image {xref} from page {page_num}")
                    continue

                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # 创建图片数据字典
                image_data = {
                    "page_number": page_num,
                    "image_index": img_index,
                    "xref": xref,
                    "format": image_ext,
                    "size_bytes": len(image_bytes),
                }

                # 包含详细元数据
                if include_metadata:
                    # 获取图片尺寸
                    try:
                        # 使用 PIL 获取图片尺寸
                        from PIL import Image
                        import io

                        pil_image = Image.open(io.BytesIO(image_bytes))
                        image_data["width"] = pil_image.width
                        image_data["height"] = pil_image.height
                        image_data["mode"] = pil_image.mode

                        # 关闭图片以释放资源
                        pil_image.close()
                    except Exception as e:
                        logger.warning(f"Failed to get image dimensions: {e}")
                        image_data["width"] = None
                        image_data["height"] = None
                        image_data["mode"] = None

                    # 添加颜色空间信息
                    if "cs" in base_image:
                        image_data["colorspace"] = base_image["cs"]
                    if "colorspace" in base_image:
                        image_data["colorspace_name"] = base_image["colorspace"]
                    if "n" in base_image:
                        image_data["n_channels"] = base_image["n"]
                    if "bpc" in base_image:
                        image_data["bpc"] = base_image["bpc"]
                    if "smask" in base_image:
                        image_data["smask"] = base_image["smask"]
                    if "xres" in base_image:
                        image_data["x_resolution"] = base_image["xres"]
                    if "yres" in base_image:
                        image_data["y_resolution"] = base_image["yres"]

                    # 添加边界框信息
                    if len(img_info) > 1:
                        image_data["bbox"] = img_info[1]
                    if len(img_info) > 2:
                        image_data["transform"] = img_info[2]

                # 保存图片到目录
                if extract_dir:
                    # 生成文件名
                    filename = f"page_{page_num}_image_{img_index + 1}.{image_format}"
                    filepath = os.path.join(extract_dir, filename)

                    # 如果需要转换格式
                    if image_format.lower() != image_ext.lower():
                        try:
                            from PIL import Image
                            import io

                            # 使用 PIL 转换格式
                            pil_image = Image.open(io.BytesIO(image_bytes))

                            # 根据格式处理
                            if image_format.lower() == "jpeg":
                                pil_image.save(filepath, "JPEG", quality=95)
                            elif image_format.lower() == "png":
                                pil_image.save(filepath, "PNG")
                            elif image_format.lower() in ["ppm", "pbm", "pam"]:
                                pil_image.save(filepath, image_format.upper())
                            else:
                                pil_image.save(filepath, image_format.upper())

                            pil_image.close()
                        except Exception as e:
                            logger.warning(
                                f"Failed to convert image format: {e}, saving as original"
                            )
                            # 保存原始格式
                            filename = f"page_{page_num}_image_{img_index + 1}.{image_ext}"
                            filepath = os.path.join(extract_dir, filename)
                            with open(filepath, "wb") as f:
                                f.write(image_bytes)
                    else:
                        # 保存原始格式
                        with open(filepath, "wb") as f:
                            f.write(image_bytes)

                    image_data["saved_path"] = filepath
                    image_data["saved_format"] = image_format

                # 添加提取时间
                image_data["extraction_time"] = datetime.now().isoformat()

                yield image_data

            except Exception as e:
                logger.error(
                    f"Error processing image {img_index} on page {page_num}: {e}",
                    exc_info=True
                )
                continue

    def extract_images_by_page_range(
        self,
        pdf_path: str,
        start_page: int,
        end_page: int,
        extract_dir: Optional[str] = None,
        image_format: str = "png",
        dpi: int = 150,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        按页码范围提取图片

        Args:
            pdf_path: PDF 文件路径
            start_page: 起始页码（1-based）
            end_page: 结束页码（1-based）
            extract_dir: 保存目录（可选）
            image_format: 图片格式
            dpi: 图片 DPI
            include_metadata: 是否包含详细元数据

        Returns:
            Dict[str, Any]: 提取结果
        """
        return self.read(
            pdf_path,
            page_range=(start_page, end_page),
            extract_dir=extract_dir,
            format=image_format,
            dpi=dpi,
            include_metadata=include_metadata
        )

    def save_images(
        self,
        images: List[Dict[str, Any]],
        output_dir: str,
        image_format: str = "png"
    ) -> Dict[str, Any]:
        """
        保存图片到指定目录

        Args:
            images: 图片列表（从 extract_images 获取）
            output_dir: 输出目录
            image_format: 图片格式

        Returns:
            Dict[str, Any]: 保存结果
        """
        result = {
            "success": False,
            "saved_count": 0,
            "failed_count": 0,
            "errors": []
        }

        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)

            saved_count = 0
            failed_count = 0

            for idx, image_data in enumerate(images):
                try:
                    # 检查是否已经保存过
                    if "saved_path" in image_data and os.path.exists(
                        image_data["saved_path"]
                    ):
                        saved_count += 1
                        continue

                    # 生成文件名
                    filename = f"image_{idx + 1}.{image_format}"
                    filepath = os.path.join(output_dir, filename)

                    # 保存图片
                    with open(filepath, "wb") as f:
                        f.write(image_data["image_bytes"])

                    saved_count += 1
                except Exception as e:
                    failed_count += 1
                    result["errors"].append({
                        "index": idx,
                        "error": str(e)
                    })
                    logger.error(f"Failed to save image {idx}: {e}")

            result["success"] = True
            result["saved_count"] = saved_count
            result["failed_count"] = failed_count

        except Exception as e:
            logger.error(f"Error saving images: {e}", exc_info=True)
            result["errors"].append({"error": str(e)})

        return result

    def get_image_metadata(self, image_bytes: bytes) -> Optional[ImageMetadata]:
        """
        获取图片元数据

        Args:
            image_bytes: 图片字节数据

        Returns:
            Optional[ImageMetadata]: 图片元数据
        """
        try:
            from PIL import Image
            import io

            pil_image = Image.open(io.BytesIO(image_bytes))

            metadata = ImageMetadata(
                page_number=0,
                image_index=0,
                width=pil_image.width,
                height=pil_image.height,
                xref=0,
                bbox=(0, 0, 0, 0),
                transform=None,
                image_format=pil_image.format or "unknown",
                size_bytes=len(image_bytes),
                cs_name=pil_image.mode,
                n_channels=len(pil_image.getbands()),
                bpc=None,
                mask=None,
                extraction_time=datetime.now().isoformat(),
            )

            pil_image.close()
            return metadata

        except Exception as e:
            logger.error(f"Failed to get image metadata: {e}", exc_info=True)
            return None

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
            "images",
            "count",
            "page_count",
            "pages_extracted",
            "metadata",
            "error",
        ]
        for key in required_keys:
            if key not in result:
                return False

        return True
