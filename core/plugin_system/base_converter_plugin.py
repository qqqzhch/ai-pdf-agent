"""转换器插件基类"""

import logging
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from .base_plugin import BasePlugin
from .plugin_type import PluginType

logger = logging.getLogger(__name__)


class BaseConverterPlugin(BasePlugin):
    """转换器插件基类 - 所有转换器插件必须继承此类"""

    plugin_type = PluginType.CONVERTER

    def __init__(self, pdf_engine=None):
        super().__init__()
        self.pdf_engine = pdf_engine

    @abstractmethod
    def convert(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        转换 PDF 到目标格式

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - page: int - 指定页码（1-based）
                - page_range: Tuple[int, int] - 页面范围 (start, end)
                - pages: List[int] - 多个页码列表
                - output_path: str - 输出文件路径（可选）

        Returns:
            Dict[str, Any]: 转换结果
                {
                    "success": bool,
                    "content": str,  # 转换后的内容
                    "metadata": Dict,  # 文档元数据
                    "pages": int,  # 处理的页数
                    "output_path": Optional[str],  # 输出文件路径（如果指定）
                    "error": Optional[str]  # 错误信息
                }
        """
        pass

    @abstractmethod
    def validate(self, pdf_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证 PDF 文件是否可转换

        Args:
            pdf_path: PDF 文件路径

        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        pass

    def execute(self, **kwargs) -> Any:
        """执行插件核心功能"""
        pdf_path = kwargs.get("pdf_path")
        if not pdf_path:
            return {"success": False, "error": "pdf_path is required"}
        return self.convert(pdf_path, **kwargs)
