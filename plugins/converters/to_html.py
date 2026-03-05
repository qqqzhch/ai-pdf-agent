"""HTML 转换插件 - 使用 PyMuPDF 将 PDF 转换为 HTML"""

import base64
import html
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from core.plugin_system.base_converter_plugin import BaseConverterPlugin
from core.plugin_system.plugin_type import PluginType

logger = logging.getLogger(__name__)


class ToHtmlPlugin(BaseConverterPlugin):
    """HTML 转换插件 - 将 PDF 内容转换为 HTML 格式"""

    # 插件元数据
    name = "to_html"
    version = "1.0.0"
    description = "将 PDF 内容转换为 HTML 格式，支持文本、标题、表格、列表和图片"
    plugin_type = PluginType.CONVERTER
    author = "李开发"
    homepage = ""
    license = "MIT"

    # 依赖
    dependencies = ["pymupdf>=1.23.0"]
    system_dependencies = []

    def __init__(self, pdf_engine=None):
        """
        初始化 HTML 转换插件

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
        将 PDF 转换为 HTML

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - page: int - 指定页码（1-based）
                - page_range: Tuple[int, int] - 页面范围 (start, end)
                - pages: List[int] - 多个页码列表
                - output_path: str - 输出文件路径（可选）
                - embed_images: bool - 是否将图片嵌入 HTML（默认 False）
                - responsive: bool - 是否使用响应式设计（默认 False）

        Returns:
            Dict[str, Any]: 转换结果
                {
                    "success": bool,
                    "content": str,  # HTML 内容
                    "metadata": Dict,  # 文档元数据
                    "pages": int,  # 处理的页数
                    "output_path": Optional[str],  # 输出文件路径
                    "error": Optional[str]  # 错误信息
                }
        """
        result = {
            "success": False,
            "content": "",
            "metadata": {},
            "pages": 0,
            "output_path": None,
            "error": None,
        }

        try:
            # 验证文件
            is_valid, error_msg = self.validate(pdf_path)
            if not is_valid:
                result["error"] = error_msg
                return result

            # 获取选项
            embed_images = kwargs.get("embed_images", False)
            responsive = kwargs.get("responsive", False)
            output_path = kwargs.get("output_path")

            # 打开文档
            doc = self.pdf_engine.open(pdf_path)

            # 获取元数据
            result["metadata"] = self.pdf_engine.get_metadata(doc)

            # 获取页数
            page_count = self.pdf_engine.get_page_count(doc)

            # 确定要转换的页面
            pages_to_convert = self._determine_pages_to_convert(kwargs, page_count)
            result["pages"] = len(pages_to_convert)

            # 构建 HTML
            html_content = self._build_html_document(
                doc, pages_to_convert, embed_images, responsive
            )

            # 关闭文档
            self.pdf_engine.close(doc)

            # 设置结果
            result["success"] = True
            result["content"] = html_content

            # 如果指定了输出路径，保存文件
            if output_path:
                self._save_html_file(html_content, output_path)
                result["output_path"] = output_path

        except FileNotFoundError:
            result["error"] = f"File not found: {pdf_path}"
        except Exception as e:
            logger.error(f"Error converting PDF {pdf_path} to HTML: {e}", exc_info=True)
            result["error"] = str(e)
        except Exception as e:
            logger.error(f"Error converting PDF {pdf_path} to HTML: {e}", exc_info=True)
            result["error"] = str(e)

        return result

    def _determine_pages_to_convert(self, kwargs: Dict, page_count: int) -> List[int]:
        """
        确定要转换的页码列表

        Args:
            kwargs: 输入参数
            page_count: 总页数

        Returns:
            List[int]: 页码列表（1-based）
        """
        # 情况1：转换指定页
        if "page" in kwargs:
            page_num = kwargs["page"]
            if isinstance(page_num, int) and 1 <= page_num <= page_count:
                return [page_num]

        # 情况2：转换页面范围
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

        # 情况3：转换指定页列表
        elif "pages" in kwargs:
            pages = kwargs["pages"]
            if isinstance(pages, list) and all(isinstance(p, int) for p in pages):
                if all(1 <= p <= page_count for p in pages):
                    return sorted(pages)

        # 情况4：转换所有页面（默认）
        return list(range(1, page_count + 1))

    def _build_html_document(
        self,
        doc,
        pages: List[int],
        embed_images: bool,
        responsive: bool,
    ) -> str:
        """
        构建 HTML 文档

        Args:
            doc: PyMuPDF 文档对象
            pages: 要转换的页码列表（1-based）
            embed_images: 是否嵌入图片
            responsive: 是否响应式设计

        Returns:
            str: HTML 文档
        """
        # HTML 头部
        html_parts = []
        html_parts.append("<!DOCTYPE html>")
        html_parts.append('<html lang="zh-CN">')
        html_parts.append("<head>")
        html_parts.append('    <meta charset="UTF-8">')
        html_parts.append(
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
        )

        # 标题
        title = doc.metadata.get("title", "PDF 文档")
        if not title:
            title = "PDF 文档"
        html_parts.append(f"    <title>{html.escape(title)}</title>")

        # 响应式样式
        if responsive:
            html_parts.append("    <style>")
            html_parts.append(
                "        body { max-width: 1200px; margin: 0 auto; padding: 20px; "
                "font-family: Arial, sans-serif; line-height: 1.6; }"
            )
            html_parts.append(
                "        table { width: 100%; border-collapse: collapse; margin: 10px 0; }"
            )
            html_parts.append(
                "        table, th, td { border: 1px solid #ddd; padding: 8px; }"
            )
            html_parts.append("        th { background-color: #f2f2f2; }")
            html_parts.append("        img { max-width: 100%; height: auto; }")
            html_parts.append(
                "        pre { white-space: pre-wrap; word-wrap: break-word; }"
            )
            html_parts.append("    </style>")

        html_parts.append("</head>")
        html_parts.append("<body>")

        # 转换每个页面
        for page_num in pages:
            page_html = self._convert_page_to_html(doc, page_num - 1, embed_images)
            html_parts.append(page_html)

        # HTML 尾部
        html_parts.append("</body>")
        html_parts.append("</html>")

        return "\n".join(html_parts)

    def _convert_page_to_html(self, doc, page_num: int, embed_images: bool) -> str:
        """
        将单个页面转换为 HTML

        Args:
            doc: PyMuPDF 文档对象
            page_num: 页码（0-based）
            embed_images: 是否嵌入图片

        Returns:
            str: HTML 内容
        """
        try:
            page = doc[page_num]
            blocks = page.get_text("dict", sort=True)["blocks"]

            html_parts = []
            html_parts.append(f'<div class="page" id="page-{page_num + 1}">')
            html_parts.append("    <hr>")
            html_parts.append(f"    <h4>第 {page_num + 1} 页</h4>")

            # 遍历所有块
            for block in blocks:
                if block["type"] == 0:  # 文本块
                    text_html = self._convert_text_block_to_html(block)
                    html_parts.append(text_html)
                elif block["type"] == 1:  # 图片块
                    image_html = self._convert_image_block_to_html(
                        doc, page_num, block, embed_images
                    )
                    html_parts.append(image_html)

            html_parts.append("</div>")

            return "\n".join(html_parts)

        except Exception as e:
            logger.error(
                f"Error converting page {page_num + 1} to HTML: {e}", exc_info=True
            )
            return f'<div class="page-error">Error converting page {page_num + 1}: {html.escape(str(e))}</div>'

    def _convert_text_block_to_html(self, block: Dict) -> str:
        """
        将文本块转换为 HTML

        Args:
            block: 文本块字典

        Returns:
            str: HTML 内容
        """
        if "lines" not in block:
            return ""

        html_parts = []

        # 获取字体大小用于判断标题
        font_size = None
        if "lines" in block and len(block["lines"]) > 0:
            if "spans" in block["lines"][0] and len(block["lines"][0]["spans"]) > 0:
                font_size = block["lines"][0]["spans"][0].get("size", 12)

        # 判断是否为标题（字体大小较大）
        is_heading = font_size and font_size >= 18

        for line in block["lines"]:
            if "spans" not in line:
                continue

            line_text = ""
            for span in line["spans"]:
                text = span.get("text", "").strip()
                line_text += text

            if not line_text:
                continue

            # 判断是否为列表项
            is_list_item = line_text.lstrip().startswith(
                ("•", "-", "*", "·", "○", "●")
            ) or any(line_text.lstrip().startswith(f"{i}.") for i in range(1, 10))

            if is_heading:
                # 根据字体大小确定标题级别
                if font_size >= 28:
                    tag = "h1"
                elif font_size >= 24:
                    tag = "h2"
                elif font_size >= 20:
                    tag = "h3"
                else:
                    tag = "h4"
                html_parts.append(f"    <{tag}>{html.escape(line_text)}</{tag}>")
            elif is_list_item:
                # 判断是有序列表还是无序列表
                if any(line_text.lstrip().startswith(f"{i}.") for i in range(1, 10)):
                    # 有序列表
                    item_text = line_text.split(".", 1)[1].strip()
                    html_parts.append(f"    <li>{html.escape(item_text)}</li>")
                else:
                    # 无序列表
                    item_text = line_text.lstrip()
                    item_text = (
                        item_text[1:].strip()
                        if item_text[0] in ["•", "-", "*", "·"]
                        else item_text
                    )
                    html_parts.append(f"    <li>{html.escape(item_text)}</li>")
            else:
                # 普通段落
                html_parts.append(f"    <p>{html.escape(line_text)}</p>")

        return "\n".join(html_parts)

    def _convert_image_block_to_html(
        self, doc, page_num: int, block: Dict, embed_images: bool
    ) -> str:
        """
        将图片块转换为 HTML

        Args:
            doc: PyMuPDF 文档对象
            page_num: 页码（0-based）
            block: 图片块字典
            embed_images: 是否嵌入图片

        Returns:
            str: HTML 内容
        """
        try:
            if "image" not in block:
                return ""

            xref = block["image"]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]
            image_format = base_image["ext"]

            if embed_images:
                # 嵌入图片为 base64
                b64_data = base64.b64encode(image_data).decode("utf-8")
                img_src = f"data:image/{image_format};base64,{b64_data}"
            else:
                # 使用占位符
                img_src = f"page-{page_num + 1}-image-{xref}.{image_format}"

            width = base_image.get("width", "auto")
            height = base_image.get("height", "auto")

            return (
                f'    <img src="{html.escape(img_src)}" '
                f'alt="Image from page {page_num + 1}" '
                f'width="{width}" height="{height}" />'
            )

        except Exception as e:
            logger.error(f"Error converting image block to HTML: {e}", exc_info=True)
            return f'    <div class="image-error">Error loading image: {html.escape(str(e))}</div>'

    def convert_text_to_html(self, text: str) -> str:
        """
        将纯文本转换为 HTML

        Args:
            text: 纯文本

        Returns:
            str: HTML 内容
        """
        # 转义 HTML 特殊字符
        escaped_text = html.escape(text)

        # 将换行符转换为 <br>
        html_text = escaped_text.replace("\n", "<br>")

        return html_text

    def convert_table_to_html(self, table_data: List[List[str]]) -> str:
        """
        将表格数据转换为 HTML 表格

        Args:
            table_data: 表格数据（二维列表）

        Returns:
            str: HTML 表格
        """
        if not table_data or not isinstance(table_data, list):
            return ""

        html_parts = []
        html_parts.append('<table border="1" cellpadding="5" cellspacing="0">')

        for row_index, row in enumerate(table_data):
            html_parts.append("    <tr>")

            for cell in row:
                cell_text = str(cell) if cell is not None else ""

                # 第一行作为表头
                if row_index == 0:
                    html_parts.append(f"        <th>{html.escape(cell_text)}</th>")
                else:
                    html_parts.append(f"        <td>{html.escape(cell_text)}</td>")

            html_parts.append("    </tr>")

        html_parts.append("</table>")

        return "\n".join(html_parts)

    def convert_list_to_html(self, items: List[str], ordered: bool = False) -> str:
        """
        将列表转换为 HTML 列表

        Args:
            items: 列表项
            ordered: 是否为有序列表

        Returns:
            str: HTML 列表
        """
        if not items or not isinstance(items, list):
            return ""

        tag = "ol" if ordered else "ul"

        html_parts = []
        html_parts.append(f"<{tag}>")

        for item in items:
            html_parts.append(f"    <li>{html.escape(str(item))}</li>")

        html_parts.append(f"</{tag}>")

        return "\n".join(html_parts)

    def convert_images_to_html(self, images: List[Dict], embed: bool = False) -> str:
        """
        将图片列表转换为 HTML

        Args:
            images: 图片列表
            embed: 是否嵌入图片

        Returns:
            str: HTML 内容
        """
        if not images or not isinstance(images, list):
            return ""

        html_parts = []

        for img_dict in images:
            page = img_dict.get("page", 1)
            img_format = img_dict.get("format", "png")
            width = img_dict.get("width", "auto")
            height = img_dict.get("height", "auto")
            img_data = img_dict.get("data")

            if embed and img_data:
                # 嵌入图片为 base64
                b64_data = base64.b64encode(img_data).decode("utf-8")
                img_src = f"data:image/{img_format};base64,{b64_data}"
            else:
                # 使用占位符
                img_src = f"page-{page}-image.{img_format}"

            html_parts.append(
                f'<img src="{html.escape(img_src)}" alt="Image from page {page}" width="{width}" height="{height}" />'
            )

        return "\n".join(html_parts)

    def _save_html_file(self, content: str, output_path: str) -> None:
        """
        保存 HTML 文件

        Args:
            content: HTML 内容
            output_path: 输出文件路径
        """
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # 写入文件
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"HTML saved to: {output_path}")

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
            "content",
            "metadata",
            "pages",
            "output_path",
            "error",
        ]
        for key in required_keys:
            if key not in result:
                return False

        return True
