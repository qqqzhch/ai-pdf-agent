"""EPUB 转换插件 - 将 PDF 转换为 EPUB 格式"""

import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import fitz  # PyMuPDF

from core.plugin_system.base_converter_plugin import BaseConverterPlugin
from core.plugin_system.plugin_type import PluginType

logger = logging.getLogger(__name__)


class ToEpubPlugin(BaseConverterPlugin):
    """EPUB 转换插件 - 将 PDF 转换为 EPUB 电子书格式"""

    # 插件元数据
    name = "to_epub"
    version = "1.0.0"
    description = "将 PDF 转换为 EPUB 电子书格式，支持文本、图片和基本排版"
    plugin_type = PluginType.CONVERTER
    author = "李开发"
    homepage = ""
    license = "MIT"

    # 依赖
    dependencies = ["pymupdf>=1.23.0", "ebooklib>=0.18"]
    system_dependencies = []

    def __init__(self, pdf_engine=None):
        """
        初始化 EPUB 转换插件

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
        将 PDF 转换为 EPUB 格式

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - page: int - 指定页码（1-based）
                - page_range: Tuple[int, int] - 页面范围 (start, end)
                - pages: List[int] - 多个页码列表
                - output_path: str - 输出文件路径（必需）
                - title: str - 书籍标题（可选，默认使用 PDF 标题）
                - author: str - 作者（可选，默认使用 PDF 作者）
                - include_images: bool - 是否包含图片（默认 True）
                - chapter_pages: int - 每章页数（0=每页一章，默认 0）

        Returns:
            Dict[str, Any]: 转换结果
                {
                    "success": bool,
                    "metadata": Dict,  # 文档元数据
                    "pages": int,  # 处理的页数
                    "chapters": int,  # 章节数
                    "images": int,  # 图片数
                    "output_path": str,  # 输出文件路径
                    "error": Optional[str]  # 错误信息
                }
        """
        result = {
            "success": False,
            "metadata": {},
            "pages": 0,
            "chapters": 0,
            "images": 0,
            "output_path": "",
            "error": None,
        }

        try:
            # 验证文件
            is_valid, error_msg = self.validate(pdf_path)
            if not is_valid:
                result["error"] = error_msg
                return result

            # 获取选项
            output_path = kwargs.get("output_path")
            if not output_path:
                result["error"] = "Output path is required"
                return result

            book_title = kwargs.get("title")
            book_author = kwargs.get("author")
            include_images = kwargs.get("include_images", True)
            chapter_pages = kwargs.get("chapter_pages", 0)

            # 打开文档
            doc = self.pdf_engine.open(pdf_path)

            # 获取元数据
            metadata = self.pdf_engine.get_metadata(doc)
            result["metadata"] = metadata

            # 如果没有指定标题，使用 PDF 标题或文件名
            if not book_title:
                book_title = (
                    metadata.get("title")
                    or os.path.splitext(os.path.basename(pdf_path))[0]
                )

            # 如果没有指定作者，使用 PDF 作者
            if not book_author:
                book_author = metadata.get("author") or "Unknown"

            # 获取页数
            page_count = self.pdf_engine.get_page_count(doc)

            # 确定要处理的页面
            pages_to_process = self._determine_pages_to_process(kwargs, page_count)

            # 创建 EPUB
            try:
                from ebooklib import epub

                # 创建书籍
                book = epub.EpubBook()

                # 设置元数据
                book.set_identifier(str(uuid.uuid4()))
                book.set_title(book_title)
                book.set_language("zh")
                book.add_author(book_author)

                # 添加 PDF 元数据
                if metadata.get("subject"):
                    book.add_metadata("DC", "subject", metadata["subject"])
                if metadata.get("keywords"):
                    # keywords 可能是列表或字符串
                    keywords = metadata["keywords"]
                    if isinstance(keywords, list):
                        keywords = ", ".join([str(k) for k in keywords if k])
                    if keywords:
                        book.add_metadata("DC", "keywords", keywords)
                book.add_metadata("DC", "date", datetime.now().strftime("%Y-%m-%d"))

                # 创建章节
                chapters = []
                image_count = 0
                toc_entries = []

                # 按章节分组页面
                page_groups = self._group_pages_by_chapter(
                    pages_to_process, chapter_pages
                )

                for group_idx, page_group in enumerate(page_groups):
                    # 创建章节 HTML 内容
                    chapter_html = self._create_chapter_html(
                        doc, page_group, include_images, image_count
                    )

                    # 创建章节
                    chapter_filename = f"chapter_{group_idx + 1}.xhtml"
                    chapter = epub.EpubHtml(
                        title=f"Chapter {group_idx + 1}",
                        file_name=chapter_filename,
                        lang="zh",
                    )
                    chapter.content = chapter_html

                    # 添加到书籍
                    book.add_item(chapter)
                    chapters.append(chapter)

                    # 添加到目录
                    toc_entries.append(chapter)

                    # 统计图片（简单估算）
                    if include_images:
                        for page_num in page_group:
                            page = doc[page_num - 1]
                            image_list = page.get_images()
                            image_count += len(image_list)

                # 添加所有章节到 spine
                book.spine = ["nav"] + chapters

                # 设置目录
                book.toc = toc_entries

                # 添加默认 CSS
                css_content = self._get_default_css()
                nav_css = epub.EpubItem(
                    uid="style_nav",
                    file_name="style/nav.css",
                    media_type="text/css",
                    content=css_content,
                )
                book.add_item(nav_css)

                # 添加导航文件
                book.add_item(epub.EpubNcx())
                book.add_item(epub.EpubNav())

                # 写入 EPUB 文件
                epub.write_epub(output_path, book, {})

                result["pages"] = len(pages_to_process)
                result["chapters"] = len(chapters)
                result["images"] = image_count
                result["output_path"] = output_path
                result["success"] = True

            except ImportError:
                result["error"] = (
                    "ebooklib is required for EPUB conversion. Install with: pip install EbookLib"
                )
            except Exception as e:
                logger.error(f"Error creating EPUB: {e}", exc_info=True)
                result["error"] = f"Error creating EPUB: {str(e)}"

            # 关闭文档
            self.pdf_engine.close(doc)

        except FileNotFoundError:
            result["error"] = f"File not found: {pdf_path}"
        except Exception as e:
            logger.error(f"Error converting PDF {pdf_path} to EPUB: {e}", exc_info=True)
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

    def _group_pages_by_chapter(
        self, pages: List[int], chapter_pages: int
    ) -> List[List[int]]:
        """
        按章节分组页面

        Args:
            pages: 页码列表
            chapter_pages: 每章页数（0=每页一章）

        Returns:
            List[List[int]]: 章节列表
        """
        if chapter_pages <= 0:
            # 每页一章
            return [[p] for p in pages]
        else:
            # 按指定页数分组
            groups = []
            for i in range(0, len(pages), chapter_pages):
                groups.append(pages[i : i + chapter_pages])
            return groups

    def _create_chapter_html(
        self, doc, pages: List[int], include_images: bool, image_count: int
    ) -> str:
        """
        创建章节 HTML 内容

        Args:
            doc: PyMuPDF 文档对象
            pages: 页码列表（1-based）
            include_images: 是否包含图片
            image_count: 图片计数

        Returns:
            str: HTML 内容（仅 body 内容）
        """
        import html

        html_parts = []

        for page_num in pages:
            page = doc[page_num - 1]
            blocks = page.get_text("dict", sort=True)["blocks"]

            # 添加页面分隔符
            html_parts.append('<div class="page-break">')
            html_parts.append(f"<h4>Page {page_num}</h4>")

            # 遍历所有块
            for block in blocks:
                if block["type"] == 0:  # 文本块
                    text_html = self._convert_text_block_to_html(block)
                    html_parts.append(text_html)
                elif block["type"] == 1:  # 图片块
                    if include_images:
                        img_html = self._convert_image_block_to_html(block, page_num)
                        html_parts.append(img_html)

            html_parts.append("</div>")

        return "\n".join(html_parts)

    def _convert_text_block_to_html(self, block: Dict) -> str:
        """
        将文本块转换为 HTML

        Args:
            block: 文本块字典

        Returns:
            str: HTML 内容
        """
        import html

        if "lines" not in block:
            return ""

        html_parts = []

        for line in block["lines"]:
            if "spans" not in line:
                continue

            line_text = ""
            for span in line["spans"]:
                text = span.get("text", "").strip()
                line_text += text

            if not line_text:
                continue

            # 转义 HTML 特殊字符
            escaped_text = html.escape(line_text)

            # 判断是否为列表项
            is_list_item = line_text.lstrip().startswith(
                ("•", "-", "*", "·", "○", "●")
            ) or any(line_text.lstrip().startswith(f"{i}.") for i in range(1, 10))

            if is_list_item:
                # 列表项
                html_parts.append(f"<li>{escaped_text}</li>")
            else:
                # 普通段落
                html_parts.append(f"<p>{escaped_text}</p>")

        return "\n".join(html_parts)

    def _convert_image_block_to_html(self, block: Dict, page_num: int) -> str:
        """
        将图片块转换为 HTML

        Args:
            block: 图片块字典
            page_num: 页码

        Returns:
            str: HTML 内容
        """
        # EPUB 中我们使用占位符，因为需要实际的图片文件
        bbox = block.get("bbox", [0, 0, 0, 0])

        # 处理无效的 bbox
        try:
            if len(bbox) >= 4:
                width = int(bbox[2] - bbox[0])
                height = int(bbox[3] - bbox[1])
            else:
                width, height = 0, 0
        except (IndexError, TypeError, ValueError):
            width, height = 0, 0

        return f"<p><em>[Image from page {page_num} - {width}x{height}]</em></p>"

    def _get_default_css(self) -> str:
        """
        获取默认 CSS 样式

        Returns:
            str: CSS 内容
        """
        return """
        body {
            font-family: serif;
            line-height: 1.6;
            margin: 20px;
        }

        h4 {
            border-bottom: 1px solid #ccc;
            margin-top: 20px;
            padding-bottom: 5px;
        }

        p {
            margin-bottom: 10px;
            text-align: justify;
        }

        li {
            margin-left: 20px;
        }

        .page-break {
            page-break-after: always;
        }
        """

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
            "metadata",
            "pages",
            "chapters",
            "images",
            "output_path",
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
    from plugins.converters.to_epub import ToEpubPlugin

    plugin = ToEpubPlugin()
    result = plugin.convert(
        pdf_path="document.pdf",
        output_path="output.epub",  # 必需
        title="My Book",             # 可选：书籍标题
        author="Author Name",        # 可选：作者
        include_images=True,         # 是否包含图片
        chapter_pages=0             # 每章页数（0=每页一章）
    )

    if result["success"]:
        print("Converted {{}} pages to {{}} chapters".format(result['pages'], result['chapters']))
        print("Images: {{}}".format(result['images']))
        print("Output: {{}}".format(result['output_path']))
    else:
        print("Error: {{}}".format(result['error']))

支持的参数:
    - page: int - 指定页码（1-based）
    - page_range: Tuple[int, int] - 页面范围 (start, end)
    - pages: List[int] - 多个页码列表
    - output_path: str - 输出文件路径（必需）
    - title: str - 书籍标题（可选）
    - author: str - 作者（可选）
    - include_images: bool - 是否包含图片（默认 True）
    - chapter_pages: int - 每章页数（0=每页一章，默认 0）

注意:
    需要安装 EbookLib: pip install EbookLib
"""
