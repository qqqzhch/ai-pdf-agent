"""性能基准测试"""

import time
import os
import tempfile
from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    ops_per_sec: float
    
    def __str__(self):
        return (
            f"{self.name}:\n"
            f"  Iterations: {self.iterations}\n"
            f"  Total time: {self.total_time:.4f}s\n"
            f"  Avg time: {self.avg_time:.4f}s\n"
            f"  Min time: {self.min_time:.4f}s\n"
            f"  Max time: {self.max_time:.4f}s\n"
            f"  Ops/sec: {self.ops_per_sec:.2f}\n"
        )


class Benchmark:
    """基准测试工具"""
    
    def __init__(self, warmup_iterations: int = 3):
        """
        初始化基准测试
        
        Args:
            warmup_iterations: 预热迭代次数
        """
        self.warmup_iterations = warmup_iterations
        self.results: List[BenchmarkResult] = []
    
    def run(
        self,
        func: Callable,
        name: str = None,
        iterations: int = 100,
        *args,
        **kwargs
    ) -> BenchmarkResult:
        """
        运行基准测试
        
        Args:
            func: 要测试的函数
            name: 测试名称
            iterations: 迭代次数
            *args, **kwargs: 函数参数
            
        Returns:
            基准测试结果
        """
        name = name or func.__name__
        
        # 预热
        print(f"Warming up {name}...")
        for _ in range(self.warmup_iterations):
            func(*args, **kwargs)
        
        # 实际测试
        print(f"Benchmarking {name} ({iterations} iterations)...")
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            times.append(end - start)
        
        total_time = sum(times)
        avg_time = total_time / len(times)
        min_time = min(times)
        max_time = max(times)
        ops_per_sec = iterations / total_time if total_time > 0 else 0
        
        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            ops_per_sec=ops_per_sec
        )
        
        self.results.append(result)
        return result
    
    def compare(self, func1: Callable, func2: Callable, name1: str = None, name2: str = None, iterations: int = 100) -> Tuple[BenchmarkResult, BenchmarkResult, float]:
        """
        比较两个函数的性能
        
        Args:
            func1: 第一个函数
            func2: 第二个函数
            name1: 第一个函数名称
            name2: 第二个函数名称
            iterations: 迭代次数
            
        Returns:
            (结果1, 结果2, 速度提升倍数)
        """
        name1 = name1 or func1.__name__
        name2 = name2 or func2.__name__
        
        result1 = self.run(func1, name1, iterations)
        result2 = self.run(func2, name2, iterations)
        
        speedup = result1.avg_time / result2.avg_time if result2.avg_time > 0 else 0
        
        print(f"\nComparison:")
        print(f"  {name1}: {result1.avg_time:.4f}s avg")
        print(f"  {name2}: {result2.avg_time:.4f}s avg")
        print(f"  Speedup: {speedup:.2f}x")
        
        return result1, result2, speedup
    
    def print_summary(self):
        """打印所有结果的摘要"""
        print("\n" + "=" * 50)
        print("BENCHMARK SUMMARY")
        print("=" * 50)
        
        for result in self.results:
            print(result)
    
    def get_results(self) -> List[BenchmarkResult]:
        """获取所有结果"""
        return self.results.copy()


def create_test_pdf(num_pages: int = 10, text_per_page: int = 1000) -> str:
    """
    创建测试用 PDF 文件
    
    Args:
        num_pages: 页数
        text_per_page: 每页文本字数
        
    Returns:
        PDF 文件路径
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF (fitz) is required for creating test PDFs")
    
    doc = fitz.new()
    font = fitz.Font("helv")
    
    for page_num in range(num_pages):
        page = doc.new_page(width=595, height=842)  # A4 size
        
        # 添加文本
        text = f"Page {page_num + 1}\n\n"
        text += "This is test content for performance benchmarking.\n" * (text_per_page // 50)
        
        point = fitz.Point(50, 50)
        page.insert_text(point, text, fontname=font.name, fontsize=12)
        page.insert_text(fitz.Point(50, 700), f"Page {page_num + 1} of {num_pages}", fontname=font.name, fontsize=14)
    
    # 保存到临时文件
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, f"test_pdf_{num_pages}pages.pdf")
    doc.save(pdf_path)
    doc.close()
    
    return pdf_path


def benchmark_pdf_reading():
    """PDF 读取性能测试"""
    print("\n" + "=" * 50)
    print("PDF READING BENCHMARK")
    print("=" * 50)
    
    # 创建测试 PDF
    print("Creating test PDF (20 pages)...")
    pdf_path = create_test_pdf(num_pages=20, text_per_page=1000)
    print(f"Test PDF created: {pdf_path}")
    
    try:
        import fitz
        from core.engine.pymupdf_engine import PyMuPDFEngine
        from core.engine.pymupdf_engine_optimized import BufferedPyMuPDFEngine
    except ImportError:
        print("Warning: Could not import engines for benchmarking")
        return
    
    benchmark = Benchmark()
    
    # 测试原始引擎
    print("\nTesting original PyMuPDFEngine...")
    original_engine = PyMuPDFEngine()
    
    def test_original():
        doc = original_engine.open(pdf_path)
        text = original_engine.extract_text(doc)
        original_engine.close(doc)
        return text
    
    result_original = benchmark.run(test_original, "Original Engine", iterations=50)
    
    # 测试优化引擎
    print("\nTesting optimized BufferedPyMuPDFEngine...")
    optimized_engine = BufferedPyMuPDFEngine()
    
    def test_optimized():
        doc = optimized_engine.open(pdf_path)
        text = optimized_engine.extract_text_batch(doc)
        optimized_engine.close(doc)
        return text
    
    result_optimized = benchmark.run(test_optimized, "Optimized Engine", iterations=50)
    
    # 比较
    speedup = result_original.avg_time / result_optimized.avg_time
    print(f"\n{result_original}")
    print(f"{result_optimized}")
    print(f"Optimization speedup: {speedup:.2f}x")
    
    # 清理
    os.remove(pdf_path)
    print(f"\nTest PDF cleaned up: {pdf_path}")


def benchmark_plugin_loading():
    """插件加载性能测试"""
    print("\n" + "=" * 50)
    print("PLUGIN LOADING BENCHMARK")
    print("=" * 50)
    
    try:
        from core.plugin_system.plugin_manager import PluginManager
        from core.plugin_system.plugin_manager_optimized import OptimizedPluginManager
    except ImportError:
        print("Warning: Could not import plugin managers for benchmarking")
        return
    
    benchmark = Benchmark()
    
    # 测试原始插件管理器
    def test_original():
        # 重新创建实例以避免单例
        import importlib
        importlib.reload(__import__('core.plugin_system.plugin_manager', fromlist=['PluginManager']))
        manager = PluginManager.__new__(PluginManager)
        manager._initialized = False
        manager.__init__()
        return manager.discover_plugins()
    
    result_original = benchmark.run(test_original, "Original PluginManager", iterations=20)
    
    # 测试优化插件管理器
    def test_optimized():
        import importlib
        importlib.reload(__import__('core.core.plugin_system.plugin_manager_optimized', fromlist=['OptimizedPluginManager']))
        manager = OptimizedPluginManager.__new__(OptimizedPluginManager)
        manager._initialized = False
        manager.__init__(enable_cache=True)
        return manager.discover_plugins()
    
    result_optimized = benchmark.run(test_optimized, "Optimized PluginManager", iterations=20)
    
    # 比较
    speedup = result_original.avg_time / result_optimized.avg_time
    print(f"\n{result_original}")
    print(f"{result_optimized}")
    print(f"Optimization speedup: {speedup:.2f}x")


def benchmark_parallel_processing():
    """并行处理性能测试"""
    print("\n" + "=" * 50)
    print("PARALLEL PROCESSING BENCHMARK")
    print("=" * 50)
    
    from utils.progress import parallel_process
    
    def dummy_task(n):
        """模拟耗时任务"""
        time.sleep(0.01)
        return n * 2
    
    tasks = list(range(100))
    
    # 测试串行处理
    def test_serial():
        return [dummy_task(task) for task in tasks]
    
    # 测试并行处理
    def test_parallel():
        return parallel_process(tasks, dummy_task, max_workers=4, show_progress=False)
    
    benchmark = Benchmark()
    
    result_serial = benchmark.run(test_serial, "Serial Processing", iterations=20)
    result_parallel = benchmark.run(test_parallel, "Parallel Processing", iterations=20)
    
    speedup = result_serial.avg_time / result_parallel.avg_time
    print(f"\n{result_serial}")
    print(f"{result_parallel}")
    print(f"Parallel speedup: {speedup:.2f}x")


def run_all_benchmarks():
    """运行所有基准测试"""
    print("=" * 60)
    print("AI-PDF-AGENT PERFORMANCE BENCHMARKS")
    print("=" * 60)
    
    benchmark_pdf_reading()
    benchmark_plugin_loading()
    benchmark_parallel_processing()
    
    print("\n" + "=" * 60)
    print("BENCHMARKS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    run_all_benchmarks()
