"""文本读取插件 - 使用 PyMuPDF 提取 PDF 文本"""

import logging
import os
from typing import Any, Dict, Optional, Tuple

from core.plugin_system.base_reader_plugin import BaseReaderPlugin
from core.plugin_system.plugin_type import PluginType

logger = logging.getLogger(__name__)


class TextReaderPlugin(BaseReaderPlugin):
    """文本读取插件 - 提取 PDF 文本内容"""

    # 插件元数据
    name = "text_reader"
    version = "1.0.0"
    description = "使用 PyMuPDF 提取 PDF 文本内容，支持按页、按范围提取"
    plugin_type = PluginType.READER
    author = "李开发"
    homepage = ""
    license = "MIT"

    # 依赖
    dependencies = ["pymupdf>=1.23.0"]
    system_dependencies = []

    def __init__(self, pdf_engine=None):
        """
        初始化文本读取插件

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
        读取 PDF 文本内容

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - page: int - 指定页码（1-based）
                - page_range: Tuple[int, int] - 页面范围 (start, end)，1-based
                - pages: List[int] - 多个页码列表，1-based

        Returns:
            Dict[str, Any]: 结构化结果
                {
                    "success": bool,
                    "content": str,  # 提取的文本
                    "metadata": Dict,  # 文档元数据
                    "page_count": int,  # 总页数
                    "pages_extracted": List[int],  # 提取的页码列表
                    "error": Optional[str]  # 错误信息
                }
        """
        result = {
            "success": False,
            "content": "",
            "metadata": {},
            "page_count": 0,
            "pages_extracted": [],
            "error": None,
        }

        try:
            # 验证文件
            is_valid, error_msg = self.validate(pdf_path)
            if not is_valid:
                result["error"] = error_msg
                return result

            # 打开文档
            doc = self.pdf_engine.open(pdf_path)

            # 获取页数
            page_count = self.pdf_engine.get_page_count(doc)
            result["page_count"] = page_count

            # 获取元数据
            result["metadata"] = self.pdf_engine.get_metadata(doc)

            # 提取文本
            text = ""
            pages_extracted = []

            # 情况1：提取指定页
            if "page" in kwargs:
                page_num = kwargs["page"]
                if (
                    not isinstance(page_num, int)
                    or page_num < 1
                    or page_num > page_count
                ):
                    result["error"] = (
                        f"Invalid page number: {page_num}. Must be between 1 and {page_count}"
                    )
                    self.pdf_engine.close(doc)
                    return result

                # PyMuPDF 使用 0-based 索引
                page_range = (page_num - 1, page_num)
                text = self.pdf_engine.extract_text(doc, page_range)
                pages_extracted = [page_num]

            # 情况2：提取页面范围
            elif "page_range" in kwargs:
                page_range = kwargs["page_range"]
                if not isinstance(page_range, (tuple, list)) or len(page_range) != 2:
                    result["error"] = (
                        f"Invalid page_range: {page_range}. Must be a tuple/list of 2 integers"
                    )
                    self.pdf_engine.close(doc)
                    return result

                start, end = page_range
                if start < 1 or end > page_count or start > end:
                    result["error"] = (
                        f"Invalid page_range: ({start}, {end}). Must be between 1 and {page_count}, with start <= end"
                    )
                    self.pdf_engine.close(doc)
                    return result

                # 转换为 0-based 索引
                page_range_0based = (start - 1, end)
                text = self.pdf_engine.extract_text(doc, page_range_0based)
                pages_extracted = list(range(start, end + 1))

            # 情况3：提取指定页列表
            elif "pages" in kwargs:
                pages = kwargs["pages"]
                if not isinstance(pages, list) or not all(
                    isinstance(p, int) for p in pages
                ):
                    result["error"] = (
                        f"Invalid pages: {pages}. Must be a list of integers"
                    )
                    self.pdf_engine.close(doc)
                    return result

                for page_num in pages:
                    if page_num < 1 or page_num > page_count:
                        result["error"] = (
                            f"Invalid page number: {page_num}. Must be between 1 and {page_count}"
                        )
                        self.pdf_engine.close(doc)
                        return result

                # 按页提取并合并
                for page_num in sorted(pages):
                    page_range_0based = (page_num - 1, page_num)
                    text += self.pdf_engine.extract_text(doc, page_range_0based)
                    pages_extracted.append(page_num)

            # 情况4：提取所有文本（默认）
            else:
                text = self.pdf_engine.extract_text(doc)
                pages_extracted = list(range(1, page_count + 1))

            # 关闭文档
            self.pdf_engine.close(doc)

            # 设置结果
            result["success"] = True
            result["content"] = text
            result["pages_extracted"] = pages_extracted

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
            "pages_extracted",
            "error",
        ]
        for key in required_keys:
            if key not in result:
                return False

        return True
