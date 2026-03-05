"""元数据读取插件 - 使用 PyMuPDF 提取 PDF 元数据"""

import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.plugin_system.base_reader_plugin import BaseReaderPlugin
from core.plugin_system.plugin_type import PluginType

logger = logging.getLogger(__name__)


class MetadataReaderPlugin(BaseReaderPlugin):
    """元数据读取插件 - 提取 PDF 元数据和文档统计信息"""

    # 插件元数据
    name = "metadata_reader"
    version = "1.0.0"
    description = "使用 PyMuPDF 提取 PDF 元数据、文档统计和 PDF 特性信息"
    plugin_type = PluginType.READER
    author = "李开发"
    homepage = ""
    license = "MIT"

    # 依赖
    dependencies = ["pymupdf>=1.23.0"]
    system_dependencies = []

    def __init__(self, pdf_engine=None):
        """
        初始化元数据读取插件

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
        读取 PDF 元数据

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - include_stats: bool - 是否包含文档统计信息（默认 True）
                - include_properties: bool - 是否包含 PDF 特性信息（默认 True）
                - normalize: bool - 是否规范化元数据（默认 True）

        Returns:
            Dict[str, Any]: 结构化结果
                {
                    "success": bool,
                    "metadata": Dict,  # 完整元数据
                    "basic_metadata": Dict,  # 基本元数据
                    "document_stats": Dict,  # 文档统计（可选）
                    "pdf_properties": Dict,  # PDF 特性（可选）
                    "error": Optional[str]  # 错误信息
                }
        """
        result = {
            "success": False,
            "metadata": {},
            "basic_metadata": {},
            "document_stats": {},
            "pdf_properties": {},
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

            # 获取完整元数据
            metadata = self.get_metadata(doc, **kwargs)
            result["metadata"] = metadata

            # 获取基本元数据
            basic_metadata = self.get_basic_metadata(doc, **kwargs)
            result["basic_metadata"] = basic_metadata

            # 获取文档统计（可选）
            if kwargs.get("include_stats", True):
                stats = self.get_document_stats(doc)
                result["document_stats"] = stats

            # 获取 PDF 特性（可选）
            if kwargs.get("include_properties", True):
                properties = self.get_pdf_properties(doc)
                result["pdf_properties"] = properties

            # 规范化元数据（可选）
            if kwargs.get("normalize", True):
                result["metadata"] = self.normalize_metadata(result["metadata"])
                result["basic_metadata"] = self.normalize_metadata(
                    result["basic_metadata"]
                )

            # 关闭文档
            self.pdf_engine.close(doc)

            # 设置结果
            result["success"] = True

        except FileNotFoundError:
            result["error"] = f"File not found: {pdf_path}"
        except Exception as e:
            logger.error(f"Error reading PDF metadata {pdf_path}: {e}", exc_info=True)
            result["error"] = str(e)

        return result

    def get_metadata(self, doc, **kwargs) -> Dict[str, Any]:
        """
        获取完整的元数据

        Args:
            doc: PDF 文档对象
            **kwargs: 额外参数

        Returns:
            Dict[str, Any]: 完整元数据
        """
        try:
            raw_metadata = doc.metadata

            # 基本元数据
            metadata = {
                "title": raw_metadata.get("title", "").strip(),
                "author": raw_metadata.get("author", "").strip(),
                "subject": raw_metadata.get("subject", "").strip(),
                "keywords": self._parse_keywords(raw_metadata.get("keywords", "")),
                "creator": raw_metadata.get("creator", "").strip(),
                "producer": raw_metadata.get("producer", "").strip(),
                "created": self._parse_pdf_date(raw_metadata.get("creationDate", "")),
                "modified": self._parse_pdf_date(raw_metadata.get("modDate", "")),
            }

            # PDF 版本
            try:
                metadata["pdf_version"] = str(doc.pdf_version)
            except AttributeError:
                metadata["pdf_version"] = raw_metadata.get("format", "").strip()

            # 页数
            metadata["page_count"] = doc.page_count

            # 加密状态
            metadata["is_encrypted"] = doc.is_encrypted

            # 文件信息
            try:
                metadata["file_size"] = os.path.getsize(doc.name)
            except (AttributeError, OSError):
                metadata["file_size"] = 0

            return metadata

        except Exception as e:
            logger.error(f"Error getting metadata: {e}", exc_info=True)
            return {}

    def get_basic_metadata(self, doc, **kwargs) -> Dict[str, Any]:
        """
        获取基本元数据（标题、作者、主题、关键词、创建日期等）

        Args:
            doc: PDF 文档对象
            **kwargs: 额外参数

        Returns:
            Dict[str, Any]: 基本元数据
        """
        try:
            raw_metadata = doc.metadata

            return {
                "title": raw_metadata.get("title", "").strip(),
                "author": raw_metadata.get("author", "").strip(),
                "subject": raw_metadata.get("subject", "").strip(),
                "keywords": self._parse_keywords(raw_metadata.get("keywords", "")),
                "created": self._parse_pdf_date(raw_metadata.get("creationDate", "")),
                "modified": self._parse_pdf_date(raw_metadata.get("modDate", "")),
            }

        except Exception as e:
            logger.error(f"Error getting basic metadata: {e}", exc_info=True)
            return {}

    def get_document_stats(self, doc) -> Dict[str, Any]:
        """
        获取文档统计信息（页数、字数、图片数量等）

        Args:
            doc: PDF 文档对象

        Returns:
            Dict[str, Any]: 文档统计
        """
        try:
            stats = {
                "page_count": doc.page_count,
                "total_words": 0,
                "total_chars": 0,
                "total_images": 0,
                "total_tables": 0,
                "average_words_per_page": 0.0,
            }

            # 统计每页的文本和图片
            for page in doc.pages():
                # 统计文本
                text = page.get_text()
                words = re.findall(r"\b\w+\b", text)
                stats["total_words"] += len(words)
                stats["total_chars"] += len(text)

                # 统计图片
                images = page.get_images()
                stats["total_images"] += len(images)

                # 统计表格（简化版本）
                try:
                    tables = page.find_tables()
                    stats["total_tables"] += len(tables)
                except Exception:
                    pass

            # 计算平均每页字数
            if stats["page_count"] > 0:
                stats["average_words_per_page"] = (
                    stats["total_words"] / stats["page_count"]
                )

            return stats

        except Exception as e:
            logger.error(f"Error getting document stats: {e}", exc_info=True)
            return {}

    def get_pdf_properties(self, doc) -> Dict[str, Any]:
        """
        获取 PDF 特性信息（版本、加密状态、是否可编辑等）

        Args:
            doc: PDF 文档对象

        Returns:
            Dict[str, Any]: PDF 特性
        """
        try:
            properties = {}

            # PDF 版本
            try:
                properties["pdf_version"] = str(doc.pdf_version)
            except AttributeError:
                try:
                    properties["pdf_version"] = doc.metadata.get("format", "").strip()
                except Exception:
                    properties["pdf_version"] = "Unknown"

            # 加密状态
            properties["is_encrypted"] = doc.is_encrypted

            # 是否可编辑（简化判断）
            properties["is_editable"] = not doc.is_encrypted

            # 是否为表单
            try:
                properties["is_form"] = doc.needs_appearance()
            except Exception:
                properties["is_form"] = False

            # 权限信息
            try:
                permissions = doc.permissions
                properties["permissions"] = {
                    "can_print": bool(permissions & 0x0004),
                    "can_modify": bool(permissions & 0x0008),
                    "can_copy": bool(permissions & 0x0010),
                    "can_annotate": bool(permissions & 0x0020),
                    "can_fill_forms": bool(permissions & 0x0100),
                }
            except Exception:
                properties["permissions"] = {}

            # 页面尺寸信息
            try:
                if doc.page_count > 0:
                    first_page = doc[0]
                    rect = first_page.rect
                    properties["page_size"] = {
                        "width": rect.width,
                        "height": rect.height,
                        "unit": "point",
                    }
            except Exception:
                properties["page_size"] = {}

            return properties

        except Exception as e:
            logger.error(f"Error getting PDF properties: {e}", exc_info=True)
            return {}

    def is_encrypted(self, doc) -> bool:
        """
        检查 PDF 是否加密

        Args:
            doc: PDF 文档对象

        Returns:
            bool: 是否加密
        """
        try:
            return doc.is_encrypted
        except Exception as e:
            logger.error(f"Error checking encryption status: {e}", exc_info=True)
            return False

    def normalize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        规范化元数据

        Args:
            metadata: 原始元数据

        Returns:
            Dict[str, Any]: 规范化后的元数据
        """
        try:
            normalized = {}

            for key, value in metadata.items():
                # 跳过 None 值
                if value is None:
                    continue

                # 规范化字符串
                if isinstance(value, str):
                    stripped = value.strip()
                    # 跳过空字符串
                    if stripped:
                        normalized[key] = stripped
                # 规范化列表
                elif isinstance(value, list):
                    normalized_list = [
                        v.strip() if isinstance(v, str) else v
                        for v in value
                        if v and (not isinstance(v, str) or v.strip())
                    ]
                    # 跳过空列表
                    if normalized_list:
                        normalized[key] = normalized_list
                # 规范化字典
                elif isinstance(value, dict):
                    normalized_dict = self.normalize_metadata(value)
                    # 跳过空字典
                    if normalized_dict:
                        normalized[key] = normalized_dict
                else:
                    normalized[key] = value

            return normalized

        except Exception as e:
            logger.error(f"Error normalizing metadata: {e}", exc_info=True)
            return metadata

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

        # 尝试打开 PDF 文件验证验证
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
            "basic_metadata",
            "document_stats",
            "pdf_properties",
            "error",
        ]
        for key in required_keys:
            if key not in result:
                return False

        return True

    def _parse_keywords(self, keywords_str: str) -> List[str]:
        """
        解析关键词字符串

        Args:
            keywords_str: 关键词字符串（逗号、分号分隔）

        Returns:
            List[str]: 关键词列表
        """
        if not keywords_str:
            return []

        # 将所有分隔符统一为逗号
        separators = [",", ";", "，", "；", "\n"]
        normalized_str = keywords_str

        for sep in separators:
            if sep != ",":
                normalized_str = normalized_str.replace(sep, ",")

        # 分割并去除空格和空值
        keywords = normalized_str.split(",")
        return [k.strip() for k in keywords if k.strip()]

    def _parse_pdf_date(self, date_str: str) -> Optional[str]:
        """
        解析 PDF 日期字符串

        Args:
            date_str: PDF 日期字符串（格式：D:YYYYMMDDHHmmSS）

        Returns:
            Optional[str]: ISO 8601 格式的日期字符串，如果解析失败返回 None
        """
        if not date_str:
            return None

        try:
            # PDF 日期格式：D:YYYYMMDDHHmmSS
            if date_str.startswith("D:"):
                date_str = date_str[2:]

            # 提取日期时间部分
            # 格式：YYYYMMDDHHmmSS
            if len(date_str) >= 14:
                year = int(date_str[0:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                hour = int(date_str[8:10])
                minute = int(date_str[10:12])
                second = int(date_str[12:14])

                # 转换为 datetime 对象
                dt = datetime(year, month, day, hour, minute, second)

                # 转换为 ISO 8601 格式
                return dt.isoformat()

            return None

        except (ValueError, IndexError) as e:
            logger.debug(f"Failed to parse PDF date '{date_str}': {e}")
            return None
