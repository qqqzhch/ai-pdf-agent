"""JSON 转换器插件 - 将 PDF 内容转换为 JSON 格式"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from core.plugin_system.base_converter_plugin import BaseConverterPlugin
from core.plugin_system.plugin_type import PluginType

logger = logging.getLogger(__name__)


class ToJsonPlugin(BaseConverterPlugin):
    """JSON 转换器插件 - 将 PDF 内容转换为结构化 JSON 格式"""

    # 插件元数据
    name = "to_json"
    version = "1.0.0"
    description = "将 PDF 内容转换为 JSON 格式，支持文本、表格、元数据和文档结构的转换"
    plugin_type = PluginType.CONVERTER
    author = "李开发"
    homepage = ""
    license = "MIT"

    # 依赖
    dependencies = ["pymupdf>=1.23.0"]
    system_dependencies = []

    def __init__(self, pdf_engine=None):
        """
        初始化 JSON 转换器插件

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
        将 PDF 转换为 JSON 格式

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - page: int - 指定页码（1-based）
                - page_range: Tuple[int, int] - 页面范围 (start, end)，1-based
                - pages: List[int] - 多个页码列表，1-based
                - output_path: str - 输出文件路径（可选）
                - include_text: bool - 是否包含文本内容（默认 True）
                - include_tables: bool - 是否包含表格（默认 True）
                - include_metadata: bool - 是否包含元数据（默认 True）
                - include_structure: bool - 是否包含文档结构（默认 True）
                - pretty: bool - 是否格式化 JSON（默认 True）
                - schema: Dict - 自定义 JSON schema（可选）

        Returns:
            Dict[str, Any]: 转换结果
                {
                    "success": bool,
                    "content": str,  # JSON 字符串
                    "metadata": Dict,  # 文档元数据
                    "pages": int,  # 处理的页数
                    "output_path": Optional[str],  # 输出文件路径（如果指定）
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

            # 打开文档
            doc = self.pdf_engine.open(pdf_path)

            # 获取页数
            page_count = self.pdf_engine.get_page_count(doc)

            # 获取元数据
            metadata = self.pdf_engine.get_metadata(doc)
            result["metadata"] = metadata

            # 确定要处理的页面
            pages_to_process = self._determine_pages_to_process(kwargs, page_count)

            # 设置实际处理的页数
            result["pages"] = len(pages_to_process)

            # 获取转换选项
            include_text = kwargs.get("include_text", True)
            include_tables = kwargs.get("include_tables", True)
            include_metadata = kwargs.get("include_metadata", True)
            include_structure = kwargs.get("include_structure", True)
            pretty = kwargs.get("pretty", True)
            custom_schema = kwargs.get("schema")

            # 构建 JSON 数据结构
            json_data = {}

            # 添加文档信息
            json_data["document"] = {
                "filename": os.path.basename(pdf_path),
                "path": pdf_path,
                "page_count": page_count,
                "pages_processed": pages_to_process,
            }

            # 添加元数据
            if include_metadata:
                json_data["metadata"] = self.convert_metadata_to_json(metadata)

            # 添加文档结构
            if include_structure:
                json_data["structure"] = self.convert_structure_to_json(
                    doc, pages_to_process
                )

            # 添加文本内容
            if include_text:
                json_data["text"] = self.convert_text_to_json(doc, pages_to_process)

            # 添加表格
            if include_tables:
                json_data["tables"] = self.convert_table_to_json(doc, pages_to_process)

            # 关闭文档
            self.pdf_engine.close(doc)

            # 应用自定义 schema（如果提供）
            if custom_schema:
                json_data = self.apply_custom_schema(json_data, custom_schema)

            # 序列化为 JSON 字符串
            if pretty:
                result["content"] = json.dumps(json_data, indent=2, ensure_ascii=False)
            else:
                result["content"] = json.dumps(json_data, ensure_ascii=False)

            # 保存到文件（如果指定）
            output_path = kwargs.get("output_path")
            if output_path:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result["content"])
                result["output_path"] = output_path

            result["success"] = True

        except FileNotFoundError:
            result["error"] = f"File not found: {pdf_path}"
        except Exception as e:
            logger.error(f"Error converting PDF {pdf_path} to JSON: {e}", exc_info=True)
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
            if (
                isinstance(pages, list)
                and pages
                and all(isinstance(p, int) for p in pages)
            ):
                # 验证所有页码都在范围内
                if all(1 <= p <= page_count for p in pages):
                    return sorted(pages)

        # 情况4：处理所有页面（默认）
        return list(range(1, page_count + 1))

    def convert_text_to_json(self, doc, pages: List[int]) -> Dict[str, Any]:
        """
        将 PDF 文本内容转换为 JSON 格式

        Args:
            doc: PyMuPDF 文档对象
            pages: 要处理的页码列表（1-based-based）

        Returns:
            Dict[str, Any]: 文本 JSON 数据
        """
        text_data = {"total_pages": len(pages), "pages": []}

        for page_num in pages:
            try:
                # 获取页面
                page_obj = doc[page_num - 1]

                # 提取文本
                text = page_obj.get_text()

                # 按块提取文本（保留结构）
                blocks = page_obj.get_text("blocks")
                blocks_data = []

                for block in blocks:
                    if block[6] == 0:  # 0 表示文本块
                        block_text = block[4]
                        if block_text.strip():
                            blocks_data.append(
                                {
                                    "text": block_text.strip(),
                                    "bbox": block[:4],  # 边界框
                                    "line_no": block[5],  # 行号
                                }
                            )

                # 添加页面数据
                text_data["pages"].append(
                    {
                        "page_number": page_num,
                        "full_text": text,
                        "blocks": blocks_data,
                        "char_count": len(text),
                    }
                )

            except Exception as e:
                logger.error(
                    f"Error extracting text from page {page_num}: {e}", exc_info=True
                )
                text_data["pages"].append({"page_number": page_num, "error": str(e)})

        return text_data

    def convert_table_to_json(self, doc, pages: List[int]) -> Dict[str, Any]:
        """
        将 PDF 表格转换为 JSON 数组

        Args:
            doc: PyMuPDF 文档对象
            pages: 要处理的页码列表（1-based）

        Returns:
            Dict[str, Any]: 表格 JSON 数据
        """
        table_data = {"total_tables": 0, "pages": []}

        for page_num in pages:
            try:
                # 获取页面
                page_obj = doc[page_num - 1]

                # 查找表格
                tabs = page_obj.find_tables()

                page_tables = []

                if tabs.tables:
                    for tab in tabs:
                        # 提取表格数据
                        table_obj = {
                            "bbox": tab.bbox,
                            "header": tab.header,
                            "rows": [],
                            "row_count": 0,
                            "col_count": 0,
                        }

                        # 提取所有行
                        for row in tab.extract():
                            cleaned_row = []
                            for cell in row:
                                if cell is None:
                                    cleaned_row.append("")
                                else:
                                    cell_text = str(cell).strip()
                                    cleaned_row.append(cell_text)
                            table_obj["rows"].append(cleaned_row)

                        # 设置行列数
                        if table_obj["rows"]:
                            table_obj["row_count"] = len(table_obj["rows"])
                            table_obj["col_count"] = max(
                                len(row) for row in table_obj["rows"]
                            )

                        page_tables.append(table_obj)

                # 添加页面数据
                table_data["pages"].append(
                    {
                        "page_number": page_num,
                        "tables": page_tables,
                        "table_count": len(page_tables),
                    }
                )

                table_data["total_tables"] += len(page_tables)

            except Exception as e:
                logger.error(
                    f"Error extracting tables from page {page_num}: {e}", exc_info=True
                )
                table_data["pages"].append({"page_number": page_num, "error": str(e)})

        return table_data

    def convert_metadata_to_json(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        将文档元数据转换为 JSON 格式

        Args:
            metadata: 文档元数据字典

        Returns:
            Dict[str, Any]: 元数据 JSON
        """
        # 清理元数据，确保所有值都是 JSON 序列化的
        clean_metadata = {}

        for key, value in metadata.items():
            if value is None:
                clean_metadata[key] = None
            elif isinstance(value, str):
                clean_metadata[key] = value
            elif isinstance(value, (int, float, bool)):
                clean_metadata[key] = value
            elif isinstance(value, (list, tuple)):
                clean_metadata[key] = [str(item) for item in value]
            else:
                # 转换为字符串
                clean_metadata[key] = str(value)

        return clean_metadata

    def convert_structure_to_json(self, doc, pages: List[int]) -> Dict[str, Any]:
        """
        将文档结构信息转换为 JSON 格式

        Args:
            doc: PyMuPDF 文档对象
            pages: 要处理的页码列表（1-based）

        Returns:
            Dict[str, Any]: 结构信息 JSON
        """
        structure_data = {"pages": []}

        for page_num in pages:
            try:
                # 获取页面
                page_obj = doc[page_num - 1]

                # 获取页面尺寸
                rect = page_obj.rect
                page_info = {
                    "page_number": page_num,
                    "width": rect.width,
                    "height": rect.height,
                    "rotation": page_obj.rotation,
                    "text_blocks": 0,
                    "image_blocks": 0,
                    "drawing_blocks": 0,
                }

                # 统计块类型
                blocks = page_obj.get_text("blocks")
                for block in blocks:
                    if block[6] == 0:  # 文本
                        page_info["text_blocks"] += 1
                    elif block[6] == 1:  # 图片
                        page_info["image_blocks"] += 1
                    elif block[6] == 2:  # 绘图
                        page_info["drawing_blocks"] += 1

                structure_data["pages"].append(page_info)

            except Exception as e:
                logger.error(
                    f"Error extracting structure from page {page_num}: {e}",
                    exc_info=True,
                )
                structure_data["pages"].append(
                    {"page_number": page_num, "error": str(e)}
                )

        return structure_data

    def build_json_schema(self) -> Dict[str, Any]:
        """
        构建默认 JSON Schema

        Returns:
            Dict[str, Any]: JSON Schema 定义
        """
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "PDF Document JSON",
            "description": "JSON representation of a PDF document",
            "type": "object",
            "properties": {
                "document": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"},
                        "path": {"type": "string"},
                        "page_count": {"type": "integer"},
                        "pages_processed": {
                            "type": "array",
                            "items": {"type": "integer"},
                        },
                    },
                    "required": ["filename", "page_count"],
                },
                "metadata": {"type": "object", "description": "Document metadata"},
                "text": {
                    "type": "object",
                    "properties": {
                        "total_pages": {"type": "integer"},
                        "pages": {"type": "array"},
                    },
                },
                "tables": {
                    "type": "object",
                    "properties": {
                        "total_tables": {"type": "integer"},
                        "pages": {"type": "array"},
                    },
                },
                "structure": {
                    "type": "object",
                    "properties": {"pages": {"type": "array"}},
                },
            },
            "required": ["document"],
        }

        return schema

    def apply_custom_schema(
        self, data: Dict[str, Any], schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        应用自定义 JSON Schema 过滤数据

        Args:
            data: 原始数据
            schema: 自定义 schema 定义

        Returns:
            Dict[str, Any]: 过滤后的数据
        """
        if not schema:
            return data

        result = {}

        # 如果 schema 指定了包含的字段
        if "include_fields" in schema:
            include_fields = schema["include_fields"]
            for field in include_fields:
                if field in data:
                    result[field] = data[field]
        else:
            # 如果没有指定包含字段，复制所有数据
            result = data.copy()

        # 如果 schema 指定了排除的字段
        if "exclude_fields" in schema:
            exclude_fields = schema["exclude_fields"]
            for field in exclude_fields:
                if field in result:
                    del result[field]

        return result

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
            "pages",
            "output_path",
            "error",
        ]
        for key in required_keys:
            if key not in result:
                return False

        return True

    def get_help(self) -> str:
        """获取插件帮助信息"""
        name = self.name
        version = self.version
        description = self.description

        return f"""
{name} v{version}
{description}

使用方法:
    from plugins.converters.to_json import ToJsonPlugin

    plugin = ToJsonPlugin()
    result = plugin.convert(
        pdf_path="document.pdf",
        include_text=True,      # 包含文本内容
        include_tables=True,    # 包含表格
        include_metadata=True,  # 包含元数据
        include_structure=True, # 包含文档结构
        pretty=True,            # 格式化 JSON
        output_path="output.json"  # 可选：保存到文件
    )

    if result["success"]:
        json_str = result["content"]
        # 使用 JSON 数据
        import json
        data = json.loads(json_str)
    else:
        error_msg = result.get('error', 'Unknown error')
        print(f"Error: {{error_msg}}")

支持的参数:
    - page: int - 指定页码（1-based）
    - page_range: Tuple[int, int] - 页面范围 (start, end)
    - pages: List[int] - 多个页码列表
    - output_path: str - 输出文件路径
    - include_text: bool - 是否包含文本（默认 True）
    - include_tables: bool - 是否包含表格（默认 True）
    - include_metadata: - 是否包含元数据（默认 True）
    - include_structure: bool - 是否包含结构（默认 True）
    - pretty: bool - 是否格式化 JSON（默认 True）
    - schema: Dict - 自定义 schema（过滤字段）
"""
