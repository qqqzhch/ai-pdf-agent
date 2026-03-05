"""Markdown 转换器插件"""

import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import fitz  # PyMuPDF

from core.plugin_system.base_converter_plugin import BaseConverterPlugin
from utils.error_handler import PDFFormatError, ProcessError

logger = logging.getLogger(__name__)


class ToMarkdownPlugin(BaseConverterPlugin):
    """Markdown 起始器插件 - 将 PDF 转换为 Markdown 格式"""

    # ========== 插件元数据 ==========
    name = "to_markdown"
    version = "1.0.0"
    description = "将 PDF 内容转换为 Markdown 格式，支持标题、表格、列表和图片"
    author = "李开发"
    homepage = ""
    license = "MIT"

    # ========== 插件依赖 ==========
    dependencies = ["pymupdf>=1.24.0"]
    system_dependencies = []

    def __init__(self, pdf_engine=None):
        super().__init__(pdf_engine)
        self._heading_styles = {
            0: "#",  # 无标题风格
            1: "#",  # H1
            2: "##",  # H2
            3: "###",  # H3
            4: "####",  # H4
            5: "#####",  # H5
            6: "######",  # H6
        }

    def is_available(self) -> bool:
        """检查插件是否可用"""
        try:
            import fitz

            return True
        except ImportError:
            return False

    def validate(self, pdf_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证 PDF 文件是否可转换

        Args:
            pdf_path: PDF 文件路径

        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        if not os.path.exists(pdf_path):
            return False, f"文件不存在: {pdf_path}"

        if not pdf_path.lower().endswith(".pdf"):
            return False, "不是 PDF 文件"

        try:
            doc = fitz.open(pdf_path)
            if doc.page_count == 0:
                doc.close()
                return False, "PDF 文件为空"
            doc.close()
        except Exception as e:
            return False, f"无法打开 PDF 文件: {str(e)}"

        return True, None

    def convert(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        转换 PDF 到 Markdown

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - page: int - 指定页码（1-based）
                - page_range: Tuple[int, int] - 页面范围 (start, end)
                - pages: List[int] - 多个页码列表
                - output_path: str - 输出文件路径（可选）
                - preserve_tables: bool - 是否保留表格（默认 True）
                - preserve_images: bool - 是否保留图片（默认 True）
                - image_prefix: str - 图片文件名前缀（默认 'image_'）

        Returns:
            Dict[str, Any]: 转换结果
        """
        # 验证文件
        is_valid, error_msg = self.validate(pdf_path)
        if not is_valid:
            return {"success": False, "error": error_msg}

        try:
            # 打开 PDF 文档
            doc = fitz.open(pdf_path)

            # 获取元数据
            metadata = self._extract_metadata(doc)

            # 确定要处理的页面
            pages_to_process = self._get_pages_to_process(doc, **kwargs)

            # 获取选项
            preserve_tables = kwargs.get("preserve_tables", True)
            preserve_images = kwargs.get("preserve_images", True)
            image_prefix = kwargs.get("image_prefix", "image_")

            # 转换为 Markdown
            markdown_lines = []
            image_count = 0

            for page_num in pages_to_process:
                page = doc.load_page(page_num - 1)  # 转换为 0-based

                # 添加页面分隔符
                if len(markdown_lines) > 0:
                    markdown_lines.append("")
                    markdown_lines.append("---")
                    markdown_lines.append("")

                # 处理页面内容
                content, img_count = self._convert_page_to_markdown(
                    page,
                    page_num,
                    preserve_tables,
                    preserve_images,
                    image_prefix,
                    image_count,
                )
                image_count = img_count

                markdown_lines.append(content)

            doc.close()

            # 合并 Markdown 内容
            markdown_content = "\n".join(markdown_lines)

            # 保存到文件（如果指定）
            output_path = kwargs.get("output_path")
            if output_path:
                try:
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                except Exception as e:
                    return {"success": False, "error": f"保存文件失败: {str(e)}"}

            return {
                "success": True,
                "content": markdown_content,
                "metadata": metadata,
                "pages": len(pages_to_process),
                "output_path": output_path,
                "image_count": image_count,
            }

        except Exception as e:
            logger.error(f"转换失败: {str(e)}")
            return {"success": False, "error": f"转换失败: {str(e)}"}

    def _get_pages_to_process(self, doc: fitz.Document, **kwargs) -> List[int]:
        """获取要处理的页面列表"""
        total_pages = doc.page_count

        # 指定单个页面
        if "page" in kwargs:
            page_num = kwargs["page"]
            if 1 <= page_num <= total_pages:
                return [page_num]

        # 指定页面范围
        if "page_range" in kwargs:
            start, end = kwargs["page_range"]
            start = max(1, start)
            end = min(total_pages, end)
            return list(range(start, end + 1))

        # 指定多个页面
        if "pages" in kwargs:
            pages = kwargs["pages"]
            valid_pages = [p for p in pages if 1 <= p <= total_pages]
            return sorted(set(valid_pages))

        # 默认：所有页面
        return list(range(1, total_pages + 1))

    def _extract_metadata(self, doc: fitz.Document) -> Dict[str, Any]:
        """提取文档元数据"""
        metadata = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "keywords": doc.metadata.get("keywords", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "page_count": doc.page_count,
        }
        return metadata

    def _convert_page_to_markdown(
        self,
        page: fitz.Page,
        page_num: int,
        preserve_tables: bool,
        preserve_images: bool,
        image_prefix: str,
        image_count: int,
    ) -> Tuple[str, int]:
        """
        转换单页为 Markdown

        Returns:
            Tuple[str, int]: (Markdown 内容, 图片计数)
        """
        markdown_lines = []

        # 添加页面标题
        markdown_lines.append(f"## Page {page_num}")
        markdown_lines.append("")

        # 提取文本块
        blocks = page.get_text("dict", sort=True)["blocks"]

        for block in blocks:
            if block["type"] == 0:  # 文本块
                block_markdown = self._convert_text_block_to_markdown(block)
                if block_markdown:
                    markdown_lines.append(block_markdown)

            elif block["type"] == 1:  # 图片块
                if preserve_images:
                    img_markdown, image_count = self._convert_image_block_to_markdown(
                        block, page_num, image_prefix, image_count
                    )
                    if img_markdown:
                        markdown_lines.append(img_markdown)

        # 如果保留表格，尝试检测和转换表格
        if preserve_tables:
            tables = page.find_tables()
            if tables:
                # 移除可能被重复的表格文本
                table_markdowns = []
                for i, table in enumerate(tables):
                    table_markdown = self._convert_table_to_markdown(table)
                    if table_markdown:
                        table_markdowns.append(f"\n### Table {i + 1}\n")
                        table_markdowns.append(table_markdown)

                if table_markdowns:
                    markdown_lines.append("\n".join(table_markdowns))

        return "\n".join(markdown_lines), image_count

    def _convert_text_block_to_markdown(self, block: Dict) -> str:
        """转换文本块为 Markdown"""
        lines = []

        for line in block.get("lines", []):
            line_text = ""

            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if not text:
                    continue

                # 检测标题
                font_name = span.get("font", "")
                font_size = span.get("size", 12)
                is_bold = "Bold" in font_name or "bold" in font_name
                is_italic = "Italic" in font_name or "italic" in font_name

                # 简单标题检测：大号字体 + 居中（简化）
                # 实际应用中需要更复杂的逻辑
                if font_size >= 24:
                    # H1
                    prefix = "#"
                elif font_size >= 20:
                    # H2
                    prefix = "##"
                elif font_size >= 16:
                    # H3
                    prefix = "###"
                else:
                    prefix = ""

                # 应用格式
                formatted_text = text
                if is_italic and not prefix:
                    formatted_text = f"*{text}*"
                if is_bold and not prefix:
                    formatted_text = f"**{text}**"

                if prefix:
                    # 确保不重复添加
                    if not text.startswith(prefix):
                        formatted_text = f"{prefix} {text}"

                line_text += formatted_text + " "

            if line_text.strip():
                lines.append(line_text.strip())

        return "\n".join(lines)

    def _convert_table_to_markdown(self, table) -> str:
        """转换表格为 Markdown"""
        try:
            # 获取表格数据
            table_data = table.extract()

            if not table_data:
                return ""

            # 构建 Markdown 表格
            markdown_lines = []

            # 表头
            header = table_data[0]
            markdown_lines.append(
                "| " + " | ".join(str(cell) for cell in header) + " |"
            )

            # 分隔线
            separator = "| " + " | ".join("---" for _ in header) + " |"
            markdown_lines.append(separator)

            # 数据行
            for row in table_data[1:]:
                markdown_lines.append(
                    "| " + " | ".join(str(cell) for cell in row) + " |"
                )

            return "\n".join(markdown_lines)

        except Exception as e:
            logger.warning(f"转换表格失败: {str(e)}")
            return ""

    def _convert_image_block_to_markdown(
        self, block: Dict, page_num: int, image_prefix: str, image_count: int
    ) -> Tuple[str, int]:
        """转换图片块为 Markdown"""
        try:
            # 获取图片信息
            bbox = block.get("bbox", [0, 0, 0, 0])
            width = int(bbox[2] - bbox[0])
            height = int(bbox[3] - bbox[1])

            # 生成图片文件名
            image_filename = f"{image_prefix}{page_num}_{image_count + 1}.png"

            # Markdown 图片语法
            image_markdown = (
                f"\n"
                f"<!-- Image {image_count + 1} on page {page_num} -->\n"
                f"![Image {image_count + 1}]({image_filename})\n"
                f"*Image {image_count + 1} (width: {width}, height: {height})*\n"
            )

            return image_markdown, image_count + 1

        except Exception as e:
            logger.warning(f"转换图片失败: {str(e)}")
            return "", image_count

    def convert_text_to_markdown(self, text: str, heading_level: int = 0) -> str:
        """
        将纯文本转换为 Markdown 格式

        Args:
            text: 原始文本
            heading_level: 标题级别（0-6）

        Returns:
            str: Markdown 格式文本
        """
        # 添加标题前缀
        prefix = self._heading_styles.get(heading_level, "")
        if prefix:
            markdown = f"{prefix} {text}"
        else:
            markdown = text

        return markdown

    def convert_list_to_markdown(self, items: List[str], ordered: bool = False) -> str:
        """
        将列表转换为 Markdown 格式

        Args:
            items: 列表项
            ordered: 是否为有序列表

        Returns:
            str: Markdown 格式列表
        """
        markdown_lines = []

        for i, item in enumerate(items):
            if ordered:
                markdown_lines.append(f"{i + 1}. {item}")
            else:
                markdown_lines.append(f"- {item}")

        return "\n".join(markdown_lines)

    def get_help(self) -> str:
        """获取插件帮助信息"""
        help_text = f"""
{self.name} v{self.version} - {self.description}

用法:
  - 使用 convert() 方法转换 PDF 文件
  - 指定 output_path 保存到文件

选项:
  - preserve_tables: 保留表格（默认: True）
  - preserve_images: 保留图片（默认: True）
  - image_prefix: 图片文件名前缀（默认: 'image_'）
  - page: 指定单个页码
  - page_range: 页面范围 (start, end)
  - pages: 多个页码列表

示例:
  plugin.convert(pdf_path="test.pdf")
  plugin.convert(pdf_path="test.pdf", output_path="output.md")
  plugin.convert(pdf_path="test.pdf", page=1)
  plugin.convert(pdf_path="test.pdf", page_range=(1, 3))
"""
        return help_text
