"""Image 转换插件 - 将 PDF 页面转换为图片"""

import os
from typing import Dict, List, Optional, Any, Tuple
import logging
from io import BytesIO
import base64

import fitz  # PyMuPDF
from PIL import Image

from core.plugin_system.base_converter_plugin import BaseConverterPlugin
from core.plugin_system.plugin_type import PluginType

logger = logging.getLogger(__name__)


class ToImagePlugin(BaseConverterPlugin):
    """Image 转换插件 - 将 PDF 页面转换为图片格式"""

    # 插件元数据
    name = "to_image"
    version = "1.0.0"
    description = "将 PDF 页面转换为图片格式（PNG, JPEG, WEBP 等）"
    plugin_type = PluginType.CONVERTER
    author = "李开发"
    homepage = ""
    license = "MIT"

    # 依赖
    dependencies = ["pymupdf>=1.23.0", "pillow>=9.0.0"]
    system_dependencies = []

    # 支持的图片格式（PyMuPDF 原生支持的格式）
    SUPPORTED_FORMATS = ["png", "jpeg", "jpg", "pnm", "pgm", "ppm", "pbm", "pam", "tga", "tpic", "psd", "ps"]

    def __init__(self, pdf_engine=None):
        """
        初始化 Image 转换插件

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

    def convert(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        将 PDF 页面转换为图片

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - page: int - 指定页码（1-based）
                - page_range: Tuple[int, int] - 页面范围 (start, end)
                - pages: List[int] - 多个页码列表
                - output_path: str - 输出文件路径（可选，可以是目录或模板）
                - format: str - 输出格式（png, jpeg, webp，默认 png）
                - dpi: int - DPI（默认 150）
                - quality: int - 图片质量（1-100，默认 85）
                - grayscale: bool - 是否灰度图（默认 False）
                - embed: bool - 是否嵌入为 base64（默认 False）

        Returns:
            Dict[str, Any]: 转换结果
                {
                    "success": bool,
                    "images": List[Dict],  # 图片数据列表
                    "metadata": Dict,  # 文档元数据
                    "pages_converted": int,  # 转换的页数
                    "format": str,  # 输出格式
                    "output_files": List[str],  # 输出文件路径列表
                    "error": Optional[str]  # 错误信息
                }
        """
        result = {
            "success": False,
            "images": [],
            "metadata": {},
            "pages_converted": 0,
            "format": "png",
            "output_files": [],
            "error": None,
        }

        try:
            # 验证文件
            is_valid, error_msg = self.validate(pdf_path)
            if not is_valid:
                result["error"] = error_msg
                return result

            # 获取选项
            image_format = kwargs.get("format", "png").lower()
            if image_format == "jpg":
                image_format = "jpeg"

            if image_format not in self.SUPPORTED_FORMATS:
                result["error"] = f"Unsupported format: {image_format}. Supported: {', '.join(self.SUPPORTED_FORMATS)}"
                return result

            dpi = kwargs.get("dpi", dpi if 'dpi' in locals() else 150)
            quality = kwargs.get("quality", 85)
            grayscale = kwargs.get("grayscale", False)
            embed = kwargs.get("embed", False)
            output_path = kwargs.get("output_path")

            # 限制 quality 范围
            quality = max(1, min(100, quality))

            # 打开文档
            doc = self.pdf_engine.open(pdf_path)

            # 获取元数据
            result["metadata"] = self.pdf_engine.get_metadata(doc)

            # 获取页数
            page_count = self.pdf_engine.get_page_count(doc)

            # 确定要处理的页面
            pages_to_process = self._determine_pages_to_process(kwargs, page_count)

            # 转换缩放因子
            zoom = dpi / 72.0

            # 确定输出目录
            output_dir = None
            output_template = None

            if output_path:
                if os.path.isdir(output_path) or output_path.endswith("/") or output_path.endswith("\\"):
                    # 输出到目录
                    output_dir = output_path
                    output_template = "page_{page}.{format}"
                else:
                    # 输出到文件（模板）
                    if os.path.dirname(output_path):
                        output_dir = os.path.dirname(output_path)
                    output_template = os.path.basename(output_path)

            # 创建输出目录（如果需要）
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            # 转换每个页面
            for page_num in pages_to_process:
                try:
                    page = doc[page_num - 1]

                    # 渲染页面为图片
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, alpha=(image_format == "png"))

                    # 转换为字节
                    img_bytes = pix.tobytes(output=image_format)

                    # 应用灰度（如果需要）
                    if grayscale:
                        img = Image.open(BytesIO(img_bytes))
                        img = img.convert("L")
                        output = BytesIO()
                        img.save(output, format=image_format, quality=quality if image_format == "jpeg" else None)
                        img_bytes = output.getvalue()

                    # 生成文件名
                    filename = self._generate_filename(output_template, page_num, image_format)
                    if output_dir:
                        full_path = os.path.join(output_dir, filename)
                    else:
                        full_path = filename

                    # 保存图片（如果指定输出路径）
                    if output_path:
                        with open(full_path, "wb") as f:
                            f.write(img_bytes)
                        result["output_files"].append(full_path)

                    # 添加到结果
                    image_data = {
                        "page": page_num,
                        "filename": filename,
                        "format": image_format,
                        "width": pix.width,
                        "height": pix.height,
                        "dpi": dpi,
                        "size": len(img_bytes),
                    }

                    # 如果需要嵌入 base64
                    if embed:
                        b64_data = base64.b64encode(img_bytes).decode("utf-8")
                        image_data["data"] = f"data:image/{image_format};base64,{b64_data}"

                    result["images"].append(image_data)

                except Exception as e:
                    logger.error(f"Error converting page {page_num}: {e}")
                    result["images"].append({
                        "page": page_num,
                        "error": str(e)
                    })

            # 关闭文档
            self.pdf_engine.close(doc)

            result["pages_converted"] = len(pages_to_process)
            result["format"] = image_format
            result["success"] = True

        except FileNotFoundError:
            result["error"] = f"File not found: {pdf_path}"
        except Exception as e:
            logger.error(f"Error converting PDF {pdf_path} to image: {e}", exc_info=True)
            result["error"] = str(e)

        return result

    def _determine_pages_to_process(self, kwargs: Dict, page_count: int) -> List[int]:
        """
        确定要处理的页码列表

        Args:
            kwargs: 输入参数
            page_count: 总页数

        Returns:
            List[int]: 页码列表（1-based）
        """
        # 情况1：处理指定页
        if "page" in kwargs:
            page_num = kwargs["page"]
            if isinstance(page_num, int) and 1 <= page_num <= page_count:
                return [page_num]

        # 情况2：处理页面范围
        elif "page_range" in kwargs:
            page_range = kwargs["page_range"]
            if isinstance(page_range, (tuple, list)) and len(page_range) == 2:
                start, end = page_range
                if (
                    isinstance(start, int)
                    and isinstance(end, int)
                    and 1 <= start <= page_count
                    and 1 <= end <= page_count
                    and start <= end
                ):
                    return list(range(start, end + 1))

        # 情况3：处理指定页列表
        elif "pages" in kwargs:
            pages = kwargs["pages"]
            if isinstance(pages, list) and all(isinstance(p, int) for p in pages):
                if all(1 <= p <= page_count for p in pages):
                    return sorted(pages)

        # 情况4：处理所有页面（默认）
        return list(range(1, page_count + 1))

    def _generate_filename(self, template: str, page_num: int, format: str) -> str:
        """
        生成文件名

        Args:
            template: 文件名模板
            page_num: 页码
            format: 图片格式

        Returns:
            str: 文件名
        """
        if not template:
            return f"page_{page_num}.{format}"

        # 替换占位符
        filename = template.replace("{page}", str(page_num))
        filename = filename.replace("{format}", format)

        # 如果没有扩展名，添加扩展名
        if not filename.endswith(f".{format}"):
            filename = f"{filename}.{format}"

        return filename

    def validate(self, pdf_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证 PDF 文件是否可转换

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
            "metadata",
            "pages_converted",
            "format",
            "output_files",
            "error",
        ]
        for key in required_keys:
            if key not in result:
                return False

        return True

    def get_help(self) -> str:
        """获取插件帮助信息"""
        return f"""
{self.name} v{self.version}
{self.description}

使用方法:
    from plugins.converters.to_image import ToImagePlugin

    plugin = ToImagePlugin()
    result = plugin.convert(
        pdf_path="document.pdf",
        format="png",          # 输出格式（png, jpeg）
        dpi=150,              # DPI
        quality=85,           # 图片质量（1-100）
        grayscale=False,      # 是否灰度图
        embed=False,          # 是否嵌入为 base64
        output_path="output/"  # 输出目录或文件模板
    )

    if result["success"]:
        print(f"Converted {{result['pages_converted']}} pages")
        print(f"Output files: {{result['output_files']}}")
        for img in result["images"]:
            print(f"  Page {{img['page']}}: {{img['filename']}} ({{img['width']}}x{{img['height']}})")
    else:
        print(f"Error: {{result['error']}}")

支持的参数:
    - page: int - 指定页码（1-based）
    - page_range: Tuple[int, int] - 页面范围 (start, end)
    - pages: List[int] - 多个页码列表
    - output_path: str - 输出目录或文件模板（如 "page_{{page}}.png"）
    - format: str - 输出格式（png, jpeg, pnm, pgm, ppm, pbm, pam, tga, tpic, psd, ps）
    - dpi: int - DPI（默认 150）
    - quality: int - 图片质量（1-100，默认 85）
    - grayscale: bool - 是否灰度图（默认 False）
    - embed: bool - 是否嵌入为 base64（默认 False）

支持的格式:
    {', '.join(self.SUPPORTED_FORMATS)}
"""
