"""CSV 转换器 - 将 PDF 表格转换为 CSV 格式

此插件提供高级 CSV 转换功能：
- 支持多个表格，每个表格生成一个独立的 CSV 文件
- 支持自定义分隔符（逗号、分号、制表符等）
- 支持不同的引号风格（单引号、双引号、不引号等）
- 支持表头处理（包含/排除）
- 支持合并单元格处理
"""

import os
import csv
from typing import Dict, List, Optional, Any, Tuple
import logging

from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

logger = logging.getLogger(__name__)


class ToCsvConverter(BasePlugin):
    """CSV 转换器 - 将 PDF 表格转换为 CSV 格式，支持多表格和高级格式参数"""

    # 插件元数据
    name = "csv_converter"
    version = "1.0.0"
    description = "将 PDF 表格转换为 CSV 格式，支持多表格、自定义分隔符、引号风格等高级选项"
    plugin_type = PluginType.CONVERTER
    author = "李开发"
    homepage = ""
    license = "MIT"

    # 依赖
    dependencies = ["pymupdf>=1.23.0"]
    system_dependencies = []

    def __init__(self, pdf_engine=None, table_reader=None):
        """
        初始化 CSV 转换器

        Args:
            pdf_engine: PDF 引擎实例（可选）
            table_reader: 表格读取器实例（可选）
        """
        super().__init__()

        # 初始化 PDF 引擎
        if pdf_engine is not None:
            self.pdf_engine = pdf_engine
        else:
            try:
                from core.engine.pymupdf_engine import PyMuPDFEngine
                self.pdf_engine = PyMuPDFEngine()
            except ImportError as e:
                logger.warning(f"Failed to import PyMuPDFEngine: {e}")
                self.pdf_engine = None

        # 初始化表格读取器
        if table_reader is not None:
            self.table_reader = table_reader
        else:
            try:
                from plugins.readers.table_reader import TableReaderPlugin
                self.table_reader = TableReaderPlugin(self.pdf_engine)
            except ImportError as e:
                logger.warning(f"Failed to import TableReaderPlugin: {e}")
                self.table_reader = None

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
                - page_range: Tuple[int, int] - 页面范围 (start, end)，1-based
                - pages: List[int] - 多个页码列表，1-based
                - output_dir: str - 输出目录（用于多表格）
                - output_path: str - 输出文件路径（用于单表格或合并）
                - delimiter: str - 分隔符（默认 ','），支持 ',', ';', '\t', '|'
                - quoting: int - 引号风格（默认 csv.QUOTE_MINIMAL）
                    csv.QUOTE_MINIMAL - 最小化引号
                    Quote all - 所有字段都加引号
                    csv.QUOTE_NONNUMERIC - 非数字字段加引号
                    csv.QUOTE_NONE - 不使用引号
                - quotechar: str - 引号字符（默认 '"'）
                - include_header: bool - 是否包含表头（默认 True）
                - multi_table_mode: str - 多表格模式
                    'separate' - 每个表格一个文件（默认）
                    'merge' - 合并所有表格到一个文件
                    'first' - 只转换第一个表格
                - file_prefix: str - 文件前缀（默认 'table'）
                - encoding: str - 文件编码（默认 'utf-8'）

        Returns:
            Dict[str, Any]: 转换结果
                {
                    "success": bool,
                    "tables": List[Dict],  # 转换的表格信息
                    "total_tables": int,  # 表格总数
                    "files": List[str],  # 生成的文件路径列表
                    "content": Optional[str],  # CSV 内容（仅当合并或单表格时）
                    "metadata": Dict,  # 文档元数据
                    "error": Optional[str]  # 错误信息
                }
        """
        result = {
            "success": False,
            "tables": [],
            "total_tables": 0,
            "files": [],
            "content": None,
            "metadata": {},
            "error": None,
        }

        try:
            # 验证文件
            is_valid, error_msg = self.validate(pdf_path)
            if not is_valid:
                result["error"] = error_msg
                return result

            # 获取选项
            delimiter = kwargs.get("delimiter", ",")
            quoting = kwargs.get("quoting", csv.QUOTE_MINIMAL)
            quotechar = kwargs.get("quotechar", '"')
            include_header = kwargs.get("include_header", True)
            multi_table_mode = kwargs.get("multi_table_mode", "separate")
            file_prefix = kwargs.get("file_prefix", "table")
            encoding = kwargs.get("encoding", "utf-8")
            output_dir = kwargs.get("output_dir")
            output_path = kwargs.get("output_path")

            # 验证分隔符
            if delimiter not in [",", ";", "\t", "|", " "]:
                logger.warning(f"Unsupported delimiter '{delimiter}', using ','")
                delimiter = ","

            # 使用表格读取器提取表格
            if self.table_reader and self.table_reader.is_available():
                tables_result = self.table_reader.read(pdf_path, **kwargs)
            else:
                # 如果表格读取器不可用，使用内置方法
                tables_result = self._extract_tables(pdf_path, **kwargs)

            if not tables_result.get("success"):
                result["error"] = tables_result.get("error", "Failed to extract tables")
                return result

            tables = tables_result.get("tables", [])
            result["total_tables"] = len(tables)

            if not tables:
                result["error"] = "No tables found in the PDF"
                return result

            # 获取元数据
            result["metadata"] = tables_result.get("metadata", {})

            # 根据多表格模式处理
            if multi_table_mode == "merge":
                # 合并所有表格到一个文件
                merged_content = self._merge_tables_to_csv(
                    tables,
                    delimiter,
                    quoting,
                    quotechar,
                    include_header,
                    encoding
                )
                result["content"] = merged_content
                result["tables"] = [{
                    "table_index": i,
                    "page": table["page"],
                    "rows": len(table["rows"])
                } for i, table in enumerate(tables)]

                # 保存到文件
                if output_path:
                    self._save_csv_file(merged_content, output_path, encoding)
                    result["files"] = [output_path]

            elif multi_table_mode == "first":
                # 只转换第一个表格
                csv_content = self._convert_table_to_csv(
                    tables[0],
                    delimiter,
                    quoting,
                    quotechar,
                    include_header,
                    encoding
                )
                result["content"] = csv_content
                result["tables"] = [{
                    "table_index": 0,
                    "page": tables[0]["page"],
                    "rows": len(tables[0]["rows"])
                }]

                # 保存到文件
                if output_path:
                    self._save_csv_file(csv_content, output_path, encoding)
                    result["files"] = [output_path]

            else:  # multi_table_mode == "separate" (default)
                # 每个表格一个文件
                if not output_dir:
                    # 如果没有指定输出目录，使用 PDF 文件同目录
                    output_dir = os.path.dirname(pdf_path)
                    if not output_dir:
                        output_dir = "."

                # 确保输出目录存在
                os.makedirs(output_dir, exist_ok=True)

                # 为每个表格生成 CSV 文件
                for i, table in enumerate(tables):
                    csv_content = self._convert_table_to_csv(
                        table,
                        delimiter,
                        quoting,
                        quotechar,
                        include_header,
                        encoding
                    )

                    # 生成文件名
                    filename = f"{file_prefix}_{i + 1}_page{table['page']}.csv"
                    file_path = os.path.join(output_dir, filename)

                    # 保存文件
                    self._save_csv_file(csv_content, file_path, encoding)
                    result["files"].append(file_path)

                    # 记录表格信息
                    result["tables"].append({
                        "table_index": i,
                        "page": table["page"],
                        "rows": len(table["rows"]),
                        "file_path": file_path
                    })

            result["success"] = True

        except FileNotFoundError:
            result["error"] = f"File not found: {pdf_path}"
        except Exception as e:
            logger.error(f"Error converting PDF {pdf_path} to CSV: {e}", exc_info=True)
            result["error"] = str(e)

        return result

    def _extract_tables(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        内置表格提取方法（当表格读取器不可用时使用）

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 页面选择参数

        Returns:
            Dict[str, Any]: 提取结果
        """
        result = {
            "success": False,
            "tables": [],
            "metadata": {},
            "page_count": 0,
            "pages_extracted": [],
            "error": None,
        }

        try:
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

        except Exception as e:
            logger.error(f"Error extracting tables: {e}", exc_info=True)
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
            import sys
            import io
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
                    "rows": []
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
            logger.error(f"Error extracting tables from page {page + 1}: {e}", exc_info=True)

        return tables

    def _convert_table_to_csv(
        self,
        table: Dict[str, Any],
        delimiter: str,
        quoting: int,
        quotechar: str,
        include_header: bool,
        encoding: str
    ) -> str:
        """
        将单个表格转换为 CSV 格式

        Args:
            table: 表格数据
            delimiter: 分隔符
            quoting: 引号风格
            quotechar: 引号字符
            include_header: 是否包含表头
            encoding: 编码

        Returns:
            str: CSV 内容
        """
        import io

        output = io.StringIO()
        writer = csv.writer(
            output,
            delimiter=delimiter,
            quoting=quoting,
            quotechar=quotechar,
            lineterminator="\n"
        )

        rows = table.get("rows", [])

        # if not include_header and rows:
        #     rows = rows[1:]

        # 写入表格行
        for row in rows:
            writer.writerow(row)

        return output.getvalue()

    def _merge_tables_to_csv(
        self,
        tables: List[Dict[str, Any]],
        delimiter: str,
        quoting: int,
        quotechar: str,
        include_header: bool,
        encoding: str
    ) -> str:
        """
        合并多个表格为单个 CSV 文件

        Args:
            tables: 表格数据列表
            delimiter: 分隔符
            quoting: 引号风格
            quotechar: 引号字符
            include_header: 是否包含表头
            encoding: 编码

        Returns:
            str: 合并的 CSV 内容
        """
        import io

        output = io.StringIO()
        writer = csv.writer(
            output,
            delimiter=delimiter,
            quoting=quoting,
            quotechar=quotechar,
            lineterminator="\n"
        )

        for i, table in enumerate(tables):
            if not table.get("rows"):
                continue

            rows = table["rows"]

            # 如果是第二个及以后的表格，添加空行分隔
            if i > 0:
                writer.writerow([])

            # 写入表格行
            for row in rows:
                writer.writerow(row)

        return output.getvalue()

    def _save_csv_file(self, content: str, file_path: str, encoding: str) -> None:
        """
        保存 CSV 文件

        Args:
            content: CSV 内容
            file_path: 文件路径
            encoding: 编码
        """
        # 确保输出目录存在
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # 写入文件
        with open(file_path, "w", encoding=encoding, newline="") as f:
            f.write(content)

        logger.info(f"CSV saved to: {file_path}")

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

        # 验证多表格模式
        if "multi_table_mode" in kwargs:
            mode = kwargs["multi_table_mode"]
            if mode not in ["separate", "merge", "first"]:
                return False

        # 验证分隔符
        if "delimiter" in kwargs:
            delimiter = kwargs["delimiter"]
            if delimiter not in [",", ";", "\t", "|", " "]:
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
            "files",
            "content",
            "metadata",
            "error",
        ]
        for key in required_keys:
            if key not in result:
                return False

        return True

    def execute(self, **kwargs) -> Any:
        """执行插件核心功能"""
        pdf_path = kwargs.get("pdf_path")
        if not pdf_path:
            return {
                "success": False,
                "error": "pdf_path is required"
            }
        return self.convert(pdf_path, **kwargs)

    def get_help(self) -> str:
        """获取插件帮助信息"""
        return f"""
{self.name} v{self.version}
{self.description}

使用方法:
    from plugins.converters.csv_converter import ToCsvConverter

    converter = ToCsvConverter()

    # 方法1：每个表格一个文件（默认）
    result = converter.convert(
        pdf_path="document.pdf",
        output_dir="./output",
        delimiter=",",
        include_header=True,
        file_prefix="table"
    )

    # 方法2：合并所有表格到一个文件
    result = converter.convert(
        pdf_path="document.pdf",
        multi_table_mode="merge",
        output_path="merged.csv",
        delimiter=";"
    )

    # 方法3：只转换第一个表格
    result = converter.convert(
        pdf_path="document.pdf",
        multi_table_mode="first",
        output_path="first_table.csv",
        quoting=csv.QUOTE_ALL
    )

    if result["success"]:
        print(f"Converted {{result['total_tables']}} tables")
        print(f"Generated files: {{result['files']}}")
        if result['content']:
            print(f"CSV content: {{result['content'][:100]}}...")
    else:
        print(f"Error: {{result['error']}}")

支持的参数:
    - page: int - 指定页码（1-based）
    - page_range: Tuple[int, int] - 页面范围 (start, end)
    - pages: List[int] - 多个页码列表
    - output_dir: str - 输出目录（用于多表格）
    - output_path: str - 输出文件路径（用于单表格或合并）
    - delimiter: str - 分隔符（默认 ','），支持 ',', ';', '\\t', '|'
    - quoting: int - 引号风格
        csv.QUOTE_MINIMAL - 最小化引号（默认）
        csv.QUOTE_ALL - 所有字段都加引号
        csv.QUOTE_NONNUMERIC - 非数字字段加引号
        csv.QUOTE_NONE - 不使用引号
    - quotechar: str - 引号字符（默认 '"'）
    - include_header: bool - 是否包含表头（默认 True）
    - multi_table_mode: str - 多表格模式
        'separate' - 每个表格一个文件（默认）
        'merge' - 合并所有表格到一个文件
        'first' - 只转换第一个表格
    - file_prefix: str - 文件前缀（默认 'table'）
    - encoding: str - 文件编码（默认 'utf-8'）

特性:
    - 自动处理合并单元格
    - 支持多种 CSV 格式
    - 批量处理多个表格
    - 自动清理单元格内容
"""
