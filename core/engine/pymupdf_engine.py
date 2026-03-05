"""PyMuPDF 引擎实现"""

from typing import Any, Dict, List, Tuple

import fitz  # PyMuPDF

from .base import BasePDFEngine


class PyMuPDFEngine(BasePDFEngine):
    """PyMuPDF 引擎实现"""

    name = "pymupdf"
    version = "1.24.0"

    def open(self, pdf_path: str) -> fitz.Document:
        """打开 PDF 文件"""
        return fitz.open(pdf_path)

    def close(self, doc: fitz.Document) -> None:
        """关闭 PDF 文件"""
        doc.close()

    def get_page_count(self, doc: fitz.Document) -> int:
        """获取页数"""
        return doc.page_count

    def extract_text(
        self, doc: fitz.Document, page_range: Tuple[int, int] = None
    ) -> str:
        """提取文本 - 优化版本（策略 A：减少跨语言调用）"""
        if page_range:
            start, end = page_range
            pages = doc.pages(start, end)
        else:
            pages = doc.pages()

        # ✅ 策略 A：批量获取所有页面文本块，减少跨语言调用
        text_blocks = []
        for page in pages:
            # 使用 PyMuPDF 的批量文本提取 API
            text_blocks.extend(page.get_text("blocks"))

        # ✅ 在 Python 层面一次性处理所有文本块
        return self._process_blocks_batch(text_blocks)

    def _process_blocks_batch(self, blocks) -> str:
        """批量处理文本块，减少循环开销

        Args:
            blocks: PyMuPDF 返回的文本块列表

        Returns:
            str: 合并后的文本
        """
        # 使用列表推导式，性能更高
        # block 格式: (x0, y0, x1, y1, text, block_no, block_type)
        # 我们只需要 text (index 4)
        return "\n".join(block[4] for block in blocks if len(block) >= 5 and block[4])

    def extract_tables(
        self, doc: fitz.Document, page_range: Tuple[int, int] = None
    ) -> List[List[List[str]]]:
        """提取表格"""
        # PyMuPDF 本身不支持表格提取，需要使用 pdfplumber
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
        """提取图片"""
        images = []

        for page_num, page in enumerate(doc.pages()):
            if page_range and (page_num < page_range[0] or page_num >= page_range[1]):
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
        """获取元数据"""
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
        """获取文档结构"""
        # 简化版本：按页面提取文本和标题
        structure = {"title": doc.metadata.get("title", ""), "sections": []}

        for page_num, page in enumerate(doc.pages()):
            text = page.get_text()
            # 简单的标题识别（大字体、居中）
            # 这里只是一个简化版本
            structure["sections"].append({"page": page_num + 1, "text": text})

        return structure
