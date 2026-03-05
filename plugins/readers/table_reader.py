"""表格读取插件 - 使用 PyMuPDF 提取 PDF 表格"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from core.plugin_system.base_reader_plugin import BaseReaderPlugin
from core.plugin_system.plugin_type import PluginType

logger = logging.getLogger(__name__)


class TableReaderPlugin(BaseReaderPlugin):
    """表格读取插件 - 提取 PDF 表格内容"""

    # 插件元数据
    name = "table_reader"
    version = "1.0.0"
    description = (
        "使用 PyMuPDF 提取 PDF 表格内容，支持按页、按范围提取，返回结构化表格数据"
    )
    plugin_type = PluginType.READER
    author = "李开发"
    homepage = ""
    license = "MIT"

    # 依赖
    dependencies = ["pymupdf>=1.23.0"]
    system_dependencies = []

    def __init__(self, pdf_engine=None):
        """
        初始化表格读取插件

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
        读取 PDF 表格内容

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - page: int - 指定页码（1-based）
                - page_range: Tuple[int, int] - 页面范围 (start, end)，1-based
                - pages: List[int] - 多个页码列表，1-based
                - output_format: str - 输出格式 (json | csv | list)，默认 json

        Returns:
            Dict[str, Any]: 结构化结果
                {
                    "success": bool,
                    "tables": List[Dict],  # 提取的表格列表
                    "total_tables": int,  # 表格总数
                    "metadata": Dict,  # 文档元数据
                    "page_count": int,  # 总页数
                    "pages_extracted": List[int],  # 提取的页码列表
                    "error": Optional[str]  # 错误信息
                }
        """
        result = {
            "success": False,
            "tables": [],
            "total_tables": 0,
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

            # 确定要提取的页面
            pages_to_extract = self._determine_pages_to_extract(kwargs, page_count)
            result["pages_extracted"] = pages_to_extract

            # 提取表格
            tables = []
            for page_num in pages_to_extract:
                page_tables = self._extract_tables_from_page(doc, page_num - 1)
                for table_data in page_tables:
                    table_data["page"] = page_num
                    tables.append(table_data)

            # 关闭文档
            self.pdf_engine.close(doc)

            # 设置结果
            result["success"] = True
            result["tables"] = tables
            result["total_tables"] = len(tables)

            # 根据输出格式转换
            output_format = kwargs.get("output_format", "json").lower()
            if output_format == "csv":
                result["csv"] = self._convert_to_csv(tables)
            elif output_format == "list":
                result["table_list"] = self._convert_to_list(tables)

        except FileNotFoundError:
            result["error"] = f"File not found: {pdf_path}"
        except Exception as e:
            logger.error(
                f"Error reading tables from PDF {pdf_path}: {e}", exc_info=True
            )
            result["error"] = str(e)

        return result

    def _determine_pages_to_extract(self, kwargs: Dict, page_count: int) -> List[int]:
        """
        确定要提取的页码列表

        Args:
            kwargs: 输入参数
            page_count: 总页数

        Returns:
            List[int]: 页码列表（1-based）
        """
        # 情况1：提取指定页
        if "page" in kwargs:
            page_num = kwargs["page"]
            if isinstance(page_num, int) and 1 <= page_num <= page_count:
                return [page_num]

        # 情况2：提取页面范围
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

        # 情况3：提取指定页列表
        elif "pages" in kwargs:
            pages = kwargs["pages"]
            if isinstance(pages, list) and all(isinstance(p, int) for p in pages):
                # 验证所有页码都在范围内
                if all(1 <= p <= page_count for p in pages):
                    return sorted(pages)

        # 情况4：提取所有页面（默认）
        return list(range(1, page_count + 1))

    def _extract_tables_from_page(self, doc, page: int) -> List[Dict[str, Any]]:
        """
        从单个页面提取表格

        Args:
            doc: PyMuPDF 文档对象
            page: 页码（0-based）

        Returns:
            List[Dict]: 表格数据列表
        """
        tables = []

        try:
            # 获取页面
            page_obj = doc[page]

            # 使用 PyMuPDF 的 find_tables 方法
            # Suppress the "pymupdf_layout" warning by redirecting stdout temporarily
            import io
            import sys

            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                # 查找表格
                tabs = page_obj.find_tables()
            finally:
                sys.stdout = old_stdout

            if not tabs.tables:
                return []

            # 遍历所有表格
            for tab in tabs:
                # 提取表格数据
                table_data = {
                    "bbox": tab.bbox,  # 表格边界框
                    "header": tab.header,  # 表头行索引
                    "rows": [],
                }

                # 提取所有行
                for row in tab.extract():
                    # 处理合并单元格：PyMuPDF 会将合并单元格重复或填充
                    # 这里我们只保留文本内容
                    cleaned_row = []
                    for cell in row:
                        if cell is None:
                            cleaned_row.append("")
                        else:
                            # 清理文本（去除多余空格）
                            cell_text = str(cell).strip()
                            cleaned_row.append(cell_text)
                    table_data["rows"].append(cleaned_row)

                # 只添加非空表格
                if table_data["rows"]:
                    tables.append(table_data)

        except Exception as e:
            logger.error(
                f"Error extracting tables from page {page + 1}: {e}", exc_info=True
            )

        return tables

    def _convert_to_csv(self, tables: List[Dict]) -> str:
        """
        将表格转换为 CSV 格式

        Args:
            tables: 表格列表

        Returns:
            str: CSV 格式字符串
        """
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # 为每个表格添加分隔符和页码信息
        for i, table in enumerate(tables):
            if i > 0:
                writer.writerow([])  # 空行分隔

            writer.writerow([f"Table {i + 1} (Page {table['page']})"])
            writer.writerow([])

            # 写入表格行
            for row in table["rows"]:
                writer.writerow(row)

        return output.getvalue()

    def _convert_to_list(self, tables: List[Dict]) -> List[Dict[str, Any]]:
        """
        将表格转换为简化列表格式

        Args:
            tables: 表格列表

        Returns:
            List[Dict]: 简化的表格列表
        """
        return [{"page": table["page"], "rows": table["rows"]} for table in tables]

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

        # 验证 output_format（如果提供）
        if "output_format" in kwargs:
            output_format = kwargs["output_format"].lower()
            if output_format not in ["json", "csv", "list"]:
                return False

        return True

    def validate_output(self, result: Any) -> bool:
        """验证输出结果"""
        if not isinstance(result, dict):
            return False

        required_keys = [
            "success",
            "tables",
            "total_tables",
            "metadata",
            "page_count",
            "pages_extracted",
            "error",
        ]
        for key in required_keys:
            if key not in result:
                return False

        return True
