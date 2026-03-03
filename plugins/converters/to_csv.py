"""CSV 转换插件 - 将 PDF 表格转换为 CSV 格式"""

import os
import csv
from typing import Dict, List, Optional, Any, Tuple
import logging

import fitz  # PyMuPDF

from core.plugin_system.base_converter_plugin import BaseConverterPlugin
from core.plugin_system.plugin_type import PluginType

logger = logging.getLogger(__name__)


class ToCsvPlugin(BaseConverterPlugin):
    """CSV 转换插件 - 将 PDF 表格转换为 CSV 格式"""

    # 插件元数据
    name = "to_csv"
    version = "1.0.0"
    description = "将 PDF 表格转换为 CSV 格式，支持单个表格或合并多个表格"
    plugin_type = PluginType.CONVERTER
    author = "李开发"
    homepage = ""
    license = "MIT"

    # 依赖
    dependencies = ["pymupdf>=1.23.0"]
    system_dependencies = []

    def __init__(self, pdf_engine=None):
        """
        初始化 CSV 转换插件

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
        将 PDF 表格转换为 CSV 格式

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - page: int - 指定页码（1-based）
                - page_range: Tuple[int, int] - 页面范围 (start, end)
                - pages: List[int] - 多个页码列表
                - output_path: str - 输出文件路径（可选）
                - table_index: int - 表格索引（0-based，默认 0）
                - merge_tables: bool - 是否合并多个表格（默认 False）
                - header: bool - 是否包含表头（默认 True）
                - delimiter: str - 分隔符（默认 ','）

        Returns:
            Dict[str, Any]: 转换结果
                {
                    "success": bool,
                    "content": str,  # CSV 内容
                    "metadata": Dict,  # 文档元数据
                    "tables_found": int,  # 找到的表格数
                    "tables_converted": int,  # 转换的表格数
                    "output_path": Optional[str],  # 输出文件路径
                    "error": Optional[str]  # 错误信息
                }
        """
        result = {
            "success": False,
            "content": "",
            "metadata": {},
            "tables_found": 0,
            "tables_converted": 0,
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
            table_index = kwargs.get("table_index", 0)
            merge_tables = kwargs.get("merge_tables", False)
            include_header = kwargs.get("header", True)
            delimiter = kwargs.get("delimiter", ",")
            output_path = kwargs.get("output_path")

            # 打开文档
            doc = self.pdf_engine.open(pdf_path)

            # 获取元数据
            result["metadata"] = self.pdf_engine.get_metadata(doc)

            # 获取页数
            page_count = self.pdf_engine.get_page_count(doc)

            # 确定要处理的页面
            pages_to_process = self._determine_pages_to_process(kwargs, page_count)

            # 提取表格
            all_tables = []

            for page_num in pages_to_process:
                page = doc[page_num - 1]
                tables = page.find_tables()

                for table in tables:
                    table_data = {
                        "page": page_num,
                        "bbox": table.bbox,
                        "rows": []
                    }

                    # 提取表格数据
                    extracted = table.extract()
                    for row in extracted:
                        cleaned_row = []
                        for cell in row:
                            if cell is None:
                                cleaned_row.append("")
                            else:
                                cell_text = str(cell).strip()
                                cleaned_row.append(cell_text)
                        table_data["rows"].append(cleaned_row)

                    all_tables.append(table_data)

            result["tables_found"] = len(all_tables)

            # 检查是否有表格
            if not all_tables:
                self.pdf_engine.close(doc)
                result["error"] = "No tables found in the specified pages"
                return result

            # 选择要转换的表格
            if merge_tables:
                # 合并所有表格
                tables_to_convert = all_tables
            else:
                # 只转换指定索引的表格
                if table_index >= len(all_tables):
                    self.pdf_engine.close(doc)
                    result["error"] = (
                        f"Table index {table_index} out of range "
                        f"(found {len(all_tables)} tables)"
                    )
                    return result
                tables_to_convert = [all_tables[table_index]]

            # 构建 CSV 内容
            csv_content = self._build_csv_content(tables_to_convert, include_header, delimiter, merge_tables)
            result["content"] = csv_content
            result["tables_converted"] = len(tables_to_convert)

            # 关闭文档
            self.pdf_engine.close(doc)

            # 保存到文件（如果指定）
            if output_path:
                self._save_csv_file(csv_content, output_path)
                result["output_path"] = output_path

            result["success"] = True

        except FileNotFoundError:
            result["error"] = f"File not found: {pdf_path}"
        except Exception as e:
            logger.error(f"Error converting PDF {pdf_path} to CSV: {e}", exc_info=True)
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

    def _build_csv_content(
        self,
        tables: List[Dict],
        include_header: bool,
        delimiter: str,
        merge: bool
    ) -> str:
        """
        构建 CSV 内容

        Args:
            tables: 表格数据列表
            include_header: 是否包含表头
            delimiter: 分隔符
            merge: 是否合并表格

        Returns:
            str: CSV 内容
        """
        import io

        output = io.StringIO()
        writer = csv.writer(output, delimiter=delimiter)

        for i, table in enumerate(tables):
            if not table["rows"]:
                continue

            rows = table["rows"]

            # 如果不包含表头，移除第一行
            if not include_header and rows:
                rows = rows[1:]

            # 写入表格行
            for row in rows:
                writer.writerow(row)

            # 如果不合并且不是最后一个表格，添加空行分隔
            if not merge and i < len(tables) - 1:
                writer.writerow([])

        return output.getvalue()

    def _save_csv_file(self, content: str, output_path: str) -> None:
        """
        保存 CSV 文件

        Args:
            content: CSV 内容
            output_path: 输出文件路径
        """
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # 写入文件
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            f.write(content)

        logger.info(f"CSV saved to: {output_path}")

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
            return False, f"File not not found: {pdf_path}"

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
            "tables_found",
            "tables_converted",
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
    from plugins:Converters.to_csv import ToCsvPlugin

    plugin = ToCsvPlugin()
    result = plugin.convert(
        pdf_path="document.pdf",
        table_index=0,        # 转换第一个表格
        merge_tables=False,   # 不合并多个表格
        header=True,          # 包含表头
        delimiter=",",        # 使用逗号分隔
        output_path="output.csv"  # 可选：保存到文件
    )

    if result["success"]:
        csv_content = result["content"]
        # 可以访问: result['tables_found'], result['tables_converted']
    else:
        # 可以访问: result['error']
        pass

支持的参数:
    - page: int - 指定页码（1-based）
    - page_range: Tuple[int, int] - 页面范围 (start, end)
    - pages: List[int] - 多个页码列表
    - output_path: str - 输出文件路径
    - table_index: int - 表格索引（0-based，默认 0）
    - merge_tables: bool - 是否合并多个表格（默认 False）
    - header: bool - 是否包含表头（默认 True）
    - delimiter: str - 分隔符（默认 ','）
"""
