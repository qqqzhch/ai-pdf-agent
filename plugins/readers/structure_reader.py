"""结构读取插件 - 分析 PDF 文档结构"""

import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import fitz  # PyMuPDF

from core.plugin_system.base_reader_plugin import BaseReaderPlugin
from core.plugin_system.plugin_type import PluginType

logger = logging.getLogger(__name__)


class StructureReaderPlugin(BaseReaderPlugin):
    """结构读取插件 - 分析 PDF 文档结构，提取大纲、页面层次和逻辑结构"""

    name = "structure_reader"
    version = "1.0.0"
    description = (
        "分析 PDF 文档结构，提取大纲、页面层次和逻辑结构（标题、段落、列表等）"
    )
    plugin_type = PluginType.READER
    author = "李开发"
    homepage = ""
    license = "MIT"

    dependencies = ["pymupdf>=1.23.0"]
    system_dependencies = []

    TITLE_FONT_SIZE_THRESHOLD = 14.0
    HEADING_FONT_SIZE_THRESHOLD = 12.0

    def __init__(self, pdf_engine=None):
        super().__init__(pdf_engine)

        if self.pdf_engine is None:
            try:
                from core.engine.pymupdf_engine import PyMuPDFEngine

                self.pdf_engine = PyMuPDFEngine()
            except ImportError as e:
                logger.warning(f"Failed to import PyMuPDFEngine: {e}")
                self.pdf_engine = None

    def is_available(self) -> bool:
        if self.pdf_engine is None:
            return False

        deps_ok, missing_deps = self.check_dependencies()
        if not deps_ok:
            logger.warning(f"Missing dependencies: {missing_deps}")
            return False

        return True

    def read(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        result = {
            "success": False,
            "outline": [],
            "page_structure": [],
            "logical_structure": [],
            "blocks": [],
            "metadata": {},
            "page_count": 0,
            "pages_analyzed": [],
            "error": None,
        }

        include_outline = kwargs.get("include_outline", True)
        include_page_structure = kwargs.get("include_page_structure", True)
        include_logical_structure = kwargs.get("include_logical_structure", True)
        include_blocks = kwargs.get("include_blocks", True)

        try:
            is_valid, error_msg = self.validate(pdf_path)
            if not is_valid:
                result["error"] = error_msg
                return result

            doc = fitz.open(pdf_path)
            page_count = len(doc)
            result["page_count"] = page_count
            result["metadata"] = self.pdf_engine.get_metadata(doc)

            pages_to_analyze = self._get_pages_to_analyze(kwargs, page_count)
            result["pages_analyzed"] = pages_to_analyze

            if include_outline:
                result["outline"] = self.get_outline(doc)

            if include_page_structure:
                result["page_structure"] = self.get_page_structure(
                    doc, pages_to_analyze
                )

            if include_blocks:
                result["blocks"] = self.analyze_blocks(doc, pages_to_analyze)

            if include_logical_structure:
                result["logical_structure"] = self.detect_logical_structure(
                    doc, pages_to_analyze, result["blocks"]
                )

            doc.close()
            result["success"] = True

        except FileNotFoundError:
            result["error"] = f"File not found: {pdf_path}"
        except Exception as e:
            logger.error(f"Error reading PDF structure {pdf_path}: {e}", exc_info=True)
            result["error"] = str(e)

        return result

    def get_outline(self, doc: fitz.Document) -> List[Dict[str, Any]]:
        outline = []

        try:
            toc = doc.get_toc()
            outline = self._build_outline_tree(toc)
        except Exception as e:
            logger.error(f"Error getting outline: {e}", exc_info=True)

        return outline

    def _build_outline_tree(self, toc: List[Tuple]) -> List[Dict[str, Any]]:
        if not toc:
            return []

        tree = []
        stack = []

        for item in toc:
            if len(item) == 3:
                level, title, page = item
                dest = None
            elif len(item) >= 4:
                level, title, page, dest = item[:4]
            else:
                continue

            node = {
                "level": level,
                "title": title.strip(),
                "page": page,
                "dest": dest,
                "children": [],
            }

            while stack and stack[-1][0] >= level:
                stack.pop()

            if not stack:
                tree.append(node)
            else:
                stack[-1][1].append(node)

            stack.append((level, node["children"]))

        return tree

    def get_page_structure(
        self, doc: fitz.Document, pages: List[int]
    ) -> List[Dict[str, Any]]:
        page_structure = []

        for page_num in pages:
            page = doc[page_num - 1]

            rect = page.rect
            width = rect.width
            height = rect.height
            rotation = page.rotation

            blocks = page.get_text("blocks")
            text_blocks = 0
            image_blocks = 0
            drawing_blocks = 0
            font_sizes = []

            for block in blocks:
                block_type = block[6]
                if block_type == 0:
                    text_blocks += 1
                elif block_type == 1:
                    image_blocks += 1
                elif block_type == 2:
                    drawing_blocks += 1

            try:
                text_dict = page.get_text("dict")
                for block in text_dict.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                font_size = span.get("size", 0)
                                if font_size > 0:
                                    font_sizes.append(font_size)
            except Exception as e:
                logger.debug(f"Error extracting font sizes: {e}")

            median_font_size = 0
            if font_sizes:
                font_sizes.sort()
                n = len(font_sizes)
                median_font_size = (
                    font_sizes[n // 2]
                    if n % 2 == 1
                    else (font_sizes[n // 2 - 1] + font_sizes[n // 2]) / 2
                )

            has_header = False
            has_footer = False

            try:
                top_region = fitz.Rect(0, 0, width, height * 0.15)
                bottom_region = fitz.Rect(0, height * 0.85, width, height)

                header_text = page.get_text("text", clip=top_region).strip()
                footer_text = page.get_text("text", clip=bottom_region).strip()

                has_header = len(header_text) > 10
                has_footer = len(footer_text) > 10
            except Exception as e:
                logger.debug(f"Error detecting header/footer: {e}")

            page_structure.append(
                {
                    "page": page_num,
                    "width": width,
                    "height": height,
                    "rotation": rotation,
                    "text_blocks": text_blocks,
                    "image_blocks": image_blocks,
                    "drawing_blocks": drawing_blocks,
                    "median_font_size": round(median_font_size, 2),
                    "has_header": has_header,
                    "has_footer": has_footer,
                }
            )

        return page_structure

    def analyze_blocks(
        self, doc: fitz.Document, pages: List[int]
    ) -> List[Dict[str, Any]]:
        blocks = []

        for page_num in pages:
            page = doc[page_num - 1]
            raw_blocks = page.get_text("blocks")

            for block in raw_blocks:
                x0, y0, x1, y1 = block[:4]
                text = block[4]
                block_type = block[6]

                block_info = {
                    "page": page_num,
                    "type": self._get_block_type_name(block_type),
                    "x0": round(x0, 2),
                    "y0": round(y0, 2),
                    "x1": round(x1, 2),
                    "y1": round(y1, 2),
                    "width": round(x1 - x0, 2),
                    "height": round(y1 - y0, 2),
                    "content": text.strip() if text else None,
                    "metadata": {
                        "block_type": block_type,
                        "bbox": (
                            round(x0, 2),
                            round(y0, 2),
                            round(x1, 2),
                            round(y1, 2),
                        ),
                    },
                }

                if block_type == 0:
                    block_info["metadata"]["font_info"] = self._extract_font_info(
                        page, x0, y0, x1, y1
                    )

                blocks.append(block_info)

        return blocks

    def _get_block_type_name(self, block_type: int) -> str:
        type_map = {0: "text", 1: "image", 2: "drawing"}
        return type_map.get(block_type, "unknown")

    def _extract_font_info(
        self, page: fitz.Page, x0: float, y0: float, x1: float, y1: float
    ) -> List[Dict[str, Any]]:
        font_info = []

        try:
            text_dict = page.get_text("dict", clip=(x0, y0, x1, y1))

            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            font_info.append(
                                {
                                    "font": span.get("font", ""),
                                    "size": round(span.get("size", 0), 2),
                                    "color": span.get("color", (0, 0, 0)),
                                    "flags": span.get("flags", 0),
                                }
                            )
        except Exception as e:
            logger.debug(f"Error extracting font info: {e}")

        return font_info

    def detect_logical_structure(
        self, doc: fitz.Document, pages: List[int] = None, blocks: List = None
    ) -> List[Dict[str, Any]]:
        if blocks is None:
            blocks = self.analyze_blocks(doc, pages)

        logical_structure = []

        for page_num in pages:
            page_blocks = [b for b in blocks if b["page"] == page_num]
            page = doc[page_num - 1]

            page_structure = self.get_page_structure(doc, [page_num])
            median_font_size = (
                page_structure[0]["median_font_size"] if page_structure else 12.0
            )

            for block in page_blocks:
                if block["type"] != "text":
                    logical_structure.append(
                        {
                            "page": page_num,
                            "type": block["type"].lower(),
                            "level": 0,
                            "content": block["content"],
                            "position": {
                                "x0": block["x0"],
                                "y0": block["y0"],
                                "x1": block["x1"],
                                "y1": block["y1"],
                            },
                            "metadata": block["metadata"],
                        }
                    )
                    continue

                text = block["content"]
                if not text:
                    continue

                font_info = block["metadata"].get("font_info", [])
                font_size = font_info[0]["size"] if font_info else median_font_size

                structure_type, level = self._classify_text_block(
                    text, font_size, median_font_size
                )

                logical_structure.append(
                    {
                        "page": page_num,
                        "type": structure_type,
                        "level": level,
                        "content": text,
                        "position": {
                            "x0": block["x0"],
                            "y0": block["y0"],
                            "x1": block["x1"],
                            "y1": block["y1"],
                        },
                        "metadata": {"font_size": font_size, "font_info": font_info},
                    }
                )

        return logical_structure

    def _classify_text_block(
        self, text: str, font_size: float, median_font_size: float
    ) -> Tuple[str, int]:
        text = text.strip()

        if not text:
            return "empty", 0

        list_patterns = {
            r"^\s*[•●○]\s+": "list",
            r"^\s*[-–—]\s+": "list",
            r"^\s*\d+\.\s+": "list",
            r"^\s*[a-zA-Z]\.\s+": "list",
            r"^\s*\(\d+\)\s+": "list",
        }

        for pattern, item_type in list_patterns.items():
            if re.match(pattern, text):
                return item_type, 0

        if font_size > self.TITLE_FONT_SIZE_THRESHOLD:
            if font_size > self.TITLE_FONT_SIZE_THRESHOLD + 4:
                return "title", 1
            else:
                return "heading", 2

        if text.isupper() and len(text) < 100:
            return "heading", 2

        numbered_patterns = [
            r"^\d+\.\s+",
            r"^\d+\.\d+\s+",
            r"^\d+\.\d+\.\d+\s+",
            r"^第[一二三四五六七八九十百千]+[章节篇]\s+",
            r"^Chapter\s+\d+",
            r"^Section\s+\d+",
        ]

        for pattern in numbered_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return "heading", 2

        if font_size > median_font_size and len(text) < 100:
            return "heading", 3

        return "paragraph", 0

    def get_structure_tree(self, pdf_path: str) -> Dict[str, Any]:
        result = self.read(pdf_path)

        if not result["success"]:
            return {"success": False, "error": result["error"]}

        tree = {
            "success": True,
            "metadata": result["metadata"],
            "outline": result["outline"],
            "structure": result["logical_structure"],
            "statistics": self._calculate_structure_statistics(result),
        }

        return tree

    def _calculate_structure_statistics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        stats = {
            "total_pages": result["page_count"],
            "outline_items": self._count_outline_items(result["outline"]),
            "structure_types": {},
        }

        for item in result["logical_structure"]:
            item_type = item["type"]
            if item_type not in stats["structure_types"]:
                stats["structure_types"][item_type] = 0
            stats["structure_types"][item_type] += 1

        return stats

    def _count_outline_items(self, outline: List[Dict[str, Any]]) -> int:
        count = len(outline)
        for item in outline:
            count += self._count_outline_items(item.get("children", []))
        return count

    def _get_pages_to_analyze(
        self, kwargs: Dict[str, Any], page_count: int
    ) -> List[int]:
        if "page" in kwargs:
            page_num = kwargs["page"]
            if 1 <= page_num <= page_count:
                return [page_num]
            else:
                logger.warning(f"Invalid page number: {page_num}")
                return list(range(1, page_count + 1))

        elif "page_range" in kwargs:
            page_range = kwargs["page_range"]
            if isinstance(page_range, (tuple, list)) and len(page_range) == 2:
                start, end = page_range
                if 1 <= start <= end <= page_count:
                    return list(range(start, end + 1))
                else:
                    logger.warning(f"Invalid page_range: {page_range}")
                    return list(range(1, page_count + 1))
            else:
                logger.warning(f"Invalid page_range format: {page_range}")
                return list(range(1, page_count + 1))

        elif "pages" in kwargs:
            pages = kwargs["pages"]
            if isinstance(pages, list) and all(isinstance(p, int) for p in pages):
                valid_pages = [p for p in pages if 1 <= p <= page_count]
                return sorted(valid_pages)
            else:
                logger.warning(f"Invalid pages format: {pages}")
                return list(range(1, page_count + 1))

        return list(range(1, page_count + 1))

    def validate(self, pdf_path: str) -> Tuple[bool, Optional[str]]:
        if not os.path.exists(pdf_path):
            return False, f"File not found: {pdf_path}"

        if not os.path.isfile(pdf_path):
            return False, f"Path is not a file: {pdf_path}"

        if not pdf_path.lower().endswith(".pdf"):
            return False, f"File is not a PDF: {pdf_path}"

        if not os.access(pdf_path, os.R_OK):
            return False, f"File is not readable: {pdf_path}"

        try:
            doc = fitz.open(pdf_path)

            if doc.is_encrypted:
                doc.close()
                return False, "PDF is encrypted and requires password"

            page_count = len(doc)
            if page_count <= 0:
                doc.close()
                return False, "PDF has no pages"

            doc.close()

        except Exception as e:
            logger.error(f"Error validating PDF {pdf_path}: {e}", exc_info=True)
            return False, f"Invalid PDF file: {str(e)}"

        return True, None

    def validate_input(self, **kwargs) -> bool:
        if "pdf_path" not in kwargs:
            return False

        pdf_path = kwargs["pdf_path"]
        if not isinstance(pdf_path, str):
            return False

        return True

    def validate_output(self, result: Any) -> bool:
        if not isinstance(result, dict):
            return False

        required_keys = [
            "success",
            "outline",
            "page_structure",
            "logical_structure",
            "blocks",
            "metadata",
            "page_count",
            "pages_analyzed",
            "error",
        ]
        for key in required_keys:
            if key not in result:
                return False

        return True
