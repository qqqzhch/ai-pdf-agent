"""PDF 引擎抽象基类"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple


class BasePDFEngine(ABC):
    """PDF 引擎抽象基类"""
    
    name: str
    version: str
    
    @abstractmethod
    def open(self, pdf_path: str) -> Any:
        """打开 PDF 文件"""
        pass
    
    @abstractmethod
    def close(self, doc: Any) -> None:
        """关闭 PDF 文件"""
        pass
    
    @abstractmethod
    def get_page_count(self, doc: Any) -> int:
        """获取页数"""
        pass
    
    @abstractmethod
    def extract_text(self, doc: Any, page_range: Tuple[int, int] = None) -> str:
        """提取文本"""
        pass
    
    @abstractmethod
    def extract_tables(self, doc: Any, page_range: Tuple[int, int] = None) -> List[List[List[str]]]:
        """提取表格"""
        pass
    
    @abstractmethod
    def extract_images(self, doc: Any, page_range: Tuple[int, int] = None) -> List[Dict]:
        """提取图片"""
        pass
    
    @abstractmethod
    def get_metadata(self, doc: Any) -> Dict:
        """获取元数据"""
        pass
    
    @abstractmethod
    def get_structure(self, doc: Any) -> Dict:
        """获取文档结构"""
        pass
