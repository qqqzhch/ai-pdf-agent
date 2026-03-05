"""优化版 PyMuPDF 引擎实现 - 阶段 1"""

import time
from contextlib import contextmanager
from typing import Any, Dict, List, Tuple

import fitz  # PyMuPDF

from .base import BasePDFEngine


class OptimizedPyMuPDFEngine(BasePDFEngine):
    """优化版 PyMuPDF 引擎实现 - 阶段 1（策略 A：减少跨语言调用）

    优化策略：
    1. 批量获取页面文本块，减少 Python-C 跨界调用
    2. 在 Python 层面一次性处理所有文本块
    3. 使用列表推导式，减少循环开销

    预期提升：10-30%（对于大文档）
    """

    name = "pymupdf_optimized"
    version = "1.24.0-optimized"

    @contextmanager
    def _timer(self, operation_name: str):
        """性能计时上下文管理器"""
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = (time.perf_counter() - start) * 1000  # 转换为毫秒
            if hasattr(self, "_performance_stats"):
                self._performance_stats[operation_name] = elapsed

    def open(self, pdf_path: str) -> fitz.Document:
        """打开 PDF 文件"""
        with self._timer("open"):
            doc = fitz.open(pdf_path)
            return doc

    def close(self, doc: fitz.Document) -> None:
        """关闭 PDF 文件"""
        with self._timer("close"):
            doc.close()

    def get_page_count(self, doc: fitz.Document) -> int:
        """获取页数"""
        with self._timer("get_page_count"):
            return doc.page_count

    def extract_text(
        self, doc: fitz.Document, page_range: Tuple[int, int] = None
    ) -> str:
        """提取文本 - 优化版本（策略 A：减少跨语言调用）

        优化说明：
        1. 使用 page.get_text("blocks") 批量 API，减少 Python-C 跨界调用
        2. 在 Python 层面一次性处理所有文本块
        3. 使用列表推导式，减少循环开销

        Args:
            doc: PyMuPDF 文档对象
            page_range: 可选的页面范围 (start, end)

        Returns:
            str: 提取的文本
        """
        with self._timer("extract_text"):
            if page_range:
                start, end = page_range
                pages = list(doc.pages(start, end))
            else:
                pages = list(doc.pages())

            # ✅ 策略 A：批量获取所有页面文本块，减少跨语言调用
            text_blocks = []
            for page in pages:
                # 使用 PyMuPDF 的批量文本提取 API
                # 这比多次调用 page.get_text("text") 更高效
                text_blocks.extend(page.get_text("blocks"))

            # ✅ 在 Python 层面一次性处理所有文本块
            return self._process_blocks_batch(text_blocks)

    def _process_blocks_batch(self, blocks) -> str:
        """批量处理文本块，减少循环开销

        优化说明：
        1. 使用列表推导式，比 for 循环更快
        2. 一次性过滤和提取，减少中间步骤

        Args:
            blocks: PyMuPDF 返回的文本块列表
            block 格式: (x0, y0, x1, y1, text, block_no, block_type)

        Returns:
            str: 合并后的文本
        """
        # 使用列表推导式，性能更高
        # block 格式: (x0, y0, x1, y1, text, block_no, block_type)
        # 我们只需要 text (index 4)
        # 只包含非空文本块
        return "\n".join(block[4] for block in blocks if len(block) >= 5 and block[4])

    def extract_tables(
        self, doc: fitz.Document, page_range: Tuple[int, int] = None
    ) -> List[List[List[str]]]:
        """提取表格（未优化，保持原实现）"""
        with self._timer("extract_tables"):
            import pdfplumber

            tables = []
            with pdfplumber.open(doc.name) as pdf:
                for i, page in enumerate(pdf.pages):
                    if page_range and (i < page_range[0] or i >= page_range[1]):
                        continue

                    table = page.extract_table()
                    if table:
                        tables.append(table)

            return tables

    def extract_images(
        self, doc: fitz.Document, page_range: Tuple[int, int] = None
    ) -> List[Dict]:
        """提取图片（未优化，保持原实现）"""
        with self._timer("extract_images"):
            images = []

            for page_num, page in enumerate(doc.pages()):
                if page_range and (
                    page_num < page_range[0] or page_num >= page_range[1]
                ):
                    continue

                for img_index, img in enumerate(page.get_images()):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_data = base_image["image"]

                    images.append(
                        {
                            "page": page_num + 1,
                            "image_index": img_index,
                            "xref": xref,
                            "width": base_image["width"],
                            "height": base_image["height"],
                            "data": image_data,
                            "format": base_image["ext"],
                        }
                    )

            return images

    def get_metadata(self, doc: fitz.Document) -> Dict:
        """获取元数据（未优化，保持原实现）"""
        with self._timer("get_metadata"):
            metadata = doc.metadata

            # Handle pdf_version attribute which may not exist in all versions
            pdf_version = ""
            try:
                pdf_version = str(doc.pdf_version)
            except AttributeError:
                # Fallback: try to get from metadata
                pdf_version = metadata.get("format", "")

            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "keywords": metadata.get("keywords", "").split(","),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "created": metadata.get("creationDate", ""),
                "modified": metadata.get("modDate", ""),
                "page_count": doc.page_count,
                "is_encrypted": doc.is_encrypted,
                "pdf_version": pdf_version,
            }

    def get_structure(self, doc: fitz.Document) -> Dict:
        """获取文档结构（未优化，保持原实现）"""
        with self._timer("get_structure"):
            # 简化版本：按页面提取文本和标题
            structure = {"title": doc.metadata.get("title", ""), "sections": []}

            for page_num, page in enumerate(doc.pages()):
                text = page.get_text()
                # 简单的标题识别（大字体、居中）
                # 这里只是一个简化版本
                structure["sections"].append({"page": page_num + 1, "text": text})

            return structure

    def get_performance_stats(self) -> Dict:
        """获取性能统计数据

        Returns:
            Dict: 各操作的性能统计（毫秒）
        """
        if not hasattr(self, "_performance_stats"):
            return {}

        return {
            "engine": self.name,
            "version": self.version,
            "stats": self._performance_stats.copy(),
        }

    def reset_performance_stats(self):
        """重置性能统计数据"""
        self._performance_stats = {}
