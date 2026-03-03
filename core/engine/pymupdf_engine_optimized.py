"""优化的 PyMuPDF 引擎实现 - 支持缓冲和流式处理"""

import fitz  # PyMuPDF
import io
from typing import Dict, List, Tuple, Any, Generator, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import threading

from .base import BasePDFEngine

logger = logging.getLogger(__name__)


class BufferedPyMuPDFEngine(BasePDFEngine):
    """缓冲和流式处理的 PyMuPDF 引擎实现"""
    
    name = "pymupdf_buffered"
    version = "2.0.0"
    
    # 页面缓存大小（页数）
    DEFAULT_PAGE_CACHE_SIZE = 10
    # 默认线程池大小
    DEFAULT_WORKERS = 4
    
    def __init__(
        self, 
        page_cache_size: int = DEFAULT_PAGE_CACHE_SIZE,
        workers: int = DEFAULT_WORKERS
    ):
        """
        初始化优化的引擎
        
        Args:
            page_cache_size: 页面缓存大小
            workers: 并行处理的线程数
        """
        self.page_cache_size = page_cache_size
        self.workers = workers
        self._page_cache: Dict[int, Dict] = {}
        self._cache_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=workers)
        
    def open(self, pdf_path: str) -> fitz.Document:
        """打开 PDF 文件并预加载元数据"""
        doc = fitz.open(pdf_path)
        logger.debug(f"Opened PDF: {pdf_path} ({doc.page_count} pages)")
        return doc
    
    def close(self, doc: fitz.Document) -> None:
        """关闭 PDF 文件并清理缓存"""
        self._page_cache.clear()
        doc.close()
        logger.debug("PDF document closed and cache cleared")
    
    def get_page_count(self, doc: fitz.Document) -> int:
        """获取页数"""
        return doc.page_count
    
    def _cache_page(self, doc: fitz.Document, page_num: int) -> Dict:
        """
        缓存页面内容
        
        Args:
            doc: PDF 文档
            page_num: 页码（0-based）
            
        Returns:
            页面内容字典
        """
        with self._cache_lock:
            # 如果缓存已满，删除最旧的页面
            if len(self._page_cache) >= self.page_cache_size:
                oldest_key = min(self._page_cache.keys())
                del self._page_cache[oldest_key]
            
            # 获取页面并缓存
            page = doc[page_num]
            page_data = {
                'text': page.get_text(),
                'page_num': page_num,
            }
            self._page_cache[page_num] = page_data
            return page_data
    
    def _get_cached_page(self, doc: fitz.Document, page_num: int) -> Optional[Dict]:
        """
        从缓存获取页面，如果不存在则加载
        
        Args:
            doc: PDF 文档
            page_num: 页码（0-based）
            
        Returns:
            页面内容字典
        """
        with self._cache_lock:
            if page_num in self._page_cache:
                logger.debug(f"Page {page_num} cache hit")
                return self._page_cache[page_num]
        
        return self._cache_page(doc, page_num)
    
    def extract_text(
        self, 
        doc: fitz.Document, 
        page_range: Tuple[int, int] = None,
        stream: bool = True
    ) -> Generator[str, None, None]:
        """
        提取文本（支持流式处理）
        
        Args:
            doc: PDF 文档
            page_range: 页面范围 (start, end)，None 表示全部
            stream: 是否使用流式生成器
            
        Yields:
            每页的文本（流式模式）或一次性返回所有文本
        """
        if page_range:
            start, end = page_range
            page_nums = range(start, min(end, doc.page_count))
        else:
            page_nums = range(doc.page_count)
        
        def extract_page_text(page_num: int) -> Tuple[int, str]:
            """提取单页文本"""
            page_data = self._get_cached_page(doc, page_num)
            return page_num, page_data['text']
        
        if stream:
            # 流式模式：逐页生成
            for page_num in page_nums:
                _, text = extract_page_text(page_num)
                yield text
        else:
            # 批量模式：并行处理
            futures = {}
            for page_num in page_nums:
                future = self._executor.submit(extract_page_text, page_num)
                futures[future] = page_num
            
            # 按顺序收集结果
            results = {}
            for future in as_completed(futures):
                page_num, text = future.result()
                results[page_num] = text
            
            for page_num in sorted(results.keys()):
                yield results[page_num]
    
    def extract_text_batch(
        self, 
        doc: fitz.Document, 
        page_range: Tuple[int, int] = None
    ) -> str:
        """
        批量提取文本（一次性返回）
        
        Args:
            doc: PDF 文档
            page_range: 页面范围
            
        Returns:
            所有文本
        """
        return ''.join(self.extract_text(doc, page_range, stream=False))
    
    def extract_tables(
        self, 
        doc: fitz.Document, 
        page_range: Tuple[int, int] = None,
        parallel: bool = True
    ) -> List[List[List[str]]]:
        """
        提取表格（支持并行处理）
        
        Args:
            doc: PDF 文档
            page_range: 页面范围
            parallel: 是否并行处理
            
        Returns:
            表格列表
        """
        import pdfplumber
        
        tables = []
        
        def extract_page_tables(pdf_path: str, page_num: int) -> Tuple[int, List]:
            """提取单页表格"""
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    if page_num >= len(pdf.pages):
                        return page_num, []
                    
                    table = pdf.pages[page_num].extract_table()
                    return page_num, [table] if table else []
            except Exception as e:
                logger.error(f"Error extracting tables from page {page_num}: {e}")
                return page_num, []
        
        if page_range:
            start, end = page_range
            page_nums = range(start, min(end, doc.page_count))
        else:
            page_nums = range(doc.page_count)
        
        if parallel and len(page_nums) > 1:
            # 并行处理
            futures = {}
            for page_num in page_nums:
                future = self._executor.submit(extract_page_tables, doc.name, page_num)
                futures[future] = page_num
            
            results = {}
            for future in as_completed(futures):
                page_num, page_tables = future.result()
                results[page_num] = page_tables
            
            # 按顺序合并结果
            for page_num in sorted(results.keys()):
                tables.extend(results[page_num])
        else:
            # 串行处理
            for page_num in page_nums:
                _, page_tables = extract_page_tables(doc.name, page_num)
                tables.extend(page_tables)
        
        return tables
    
    def extract_images(
        self, 
        doc: fitz.Document, 
        page_range: Tuple[int, int] = None,
        parallel: bool = True
    ) -> List[Dict]:
        """
        提取图片（支持并行处理）
        
        Args:
            doc: PDF 文档
            page_range: 页面范围
            parallel: 是否并行处理
            
        Returns:
            图片列表
        """
        images = []
        
        def extract_page_images(doc: fitz.Document, page_num: int) -> List[Dict]:
            """提取单页图片"""
            page_images = []
            page = doc[page_num]
            
            for img_index, img in enumerate(page.get_images()):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]
                
                page_images.append({
                    "page": page_num + 1,
                    "image_index": img_index,
                    "xref": xref,
                    "width": base_image["width"],
                    "height": base_image["height"],
                    "data": image_data,
                    "format": base_image["ext"]
                })
            
            return page_images
        
        if page_range:
            start, end = page_range
            page_nums = range(start, min(end, doc.page_count))
        else:
            page_nums = range(doc.page_count)
        
        if parallel and len(page_nums) > 1:
            # 并行处理
            futures = {}
            for page_num in page_nums:
                future = self._executor.submit(extract_page_images, doc, page_num)
                futures[future] = page_num
            
            results = {}
            for future in as_completed(futures):
                page_num = futures[future]
                try:
                    page_images = future.result()
                    results[page_num] = page_images
                except Exception as e:
                    logger.error(f"Error extracting images from page {page_num}: {e}")
                    results[page_num] = []
            
            # 按顺序合并结果
            for page_num in sorted(results.keys()):
                images.extend(results[page_num])
        else:
            # 串行处理
            for page_num in page_nums:
                page_images = extract_page_images(doc, page_num)
                images.extend(page_images)
        
        return images
    
    def get_metadata(self, doc: fitz.Document) -> Dict:
        """获取元数据（优化的快速读取）"""
        metadata = doc.metadata
        
        # Handle pdf_version attribute which may not exist in all versions
        pdf_version = ""
        try:
            pdf_version = str(doc.pdf_version)
        except AttributeError:
            pdf_version = metadata.get("format", "")
        
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", "").split(",") if metadata.get("keywords") else [],
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "created": metadata.get("creationDate", ""),
            "modified": metadata.get("modDate", ""),
            "page_count": doc.page_count,
            "is_encrypted": doc.is_encrypted,
            "pdf_version": pdf_version,
        }
    
    def get_structure(
        self, 
        doc: fitz.Document, 
        page_range: Tuple[int, int] = None
    ) -> Dict:
        """
        获取文档结构（使用流式处理）
        
        Args:
            doc: PDF 文档
            page_range: 页面范围
            
        Returns:
            文档结构字典
        """
        structure = {
            "title": doc.metadata.get("title", ""),
            "sections": []
        }
        
        for text in self.extract_text(doc, page_range, stream=True):
            structure["sections"].append({
                "text": text
            })
        
        return structure
    
    def __del__(self):
        """清理线程池"""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)


# 保持向后兼容的别名
PyMuPDFEngineOptimized = BufferedPyMuPDFEngine
