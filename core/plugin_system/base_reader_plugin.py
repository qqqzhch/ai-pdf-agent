"""读取器插件基类"""

from abc import abstractmethod
from typing import Dict, List, Optional, Any, Tuple
import logging

from .base_plugin import BasePlugin
from .plugin_type import PluginType


logger = logging.getLogger(__name__)


class BaseReaderPlugin(BasePlugin):
    """读取器插件基类 - 所有读取器插件必须继承此类"""
    
    plugin_type = PluginType.READER
    
    def __init__(self, pdf_engine=None):
        super().__init__()
        self.pdf_engine = pdf_engine
    
    @abstractmethod
    def read(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        读取 PDF 内容
        
        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - page: int - 指定页码（1-based）
                - page_range: Tuple[int, int] - 页面范围 (start, end)
                - pages: List[int] - 多个页码列表
        
        Returns:
            Dict[str, Any]: 结构化数据
                {
                    "success": bool,
                    "content": str,  # 提取的内容
                    "metadata": Dict,  # 文档元数据
                    "pages": int,  # 总页数
                    "error": Optional[str]  # 错误信息
                }
        """
        pass
    
    @abstractmethod
    def validate(self, pdf_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证 PDF 文件
        
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
            return {
                "success": False,
                "error": "pdf_path is required"
            }
        return self.read(pdf_path, **kwargs)
