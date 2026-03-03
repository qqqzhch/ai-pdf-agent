"""性能分析测试"""

import cProfile
import pstats
import io
import time
import os
from typing import Callable
from contextlib import contextmanager


@contextmanager
def profile_context(name: str = "Profile", output_file: str = None):
    """
    性能分析上下文管理器
    
    Args:
        name: 分析名称
        output_file: 输出文件路径（可选）
    """
    pr = cProfile.Profile()
    pr.enable()
    
    try:
        yield pr
    finally:
        pr.disable()
        
        # 输出统计
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # 打印前 20 个函数
        
        print(f"\n{'='*60}")
        print(f"PROFILE: {name}")
        print(f"{'='*60}")
        print(s.getvalue())
        
        # 保存到文件
        if output_file:
            with open(output_file, 'w') as f:
                ps.print_stats()
            print(f"\nProfile saved to: {output_file}")


def profile_function(
    func: Callable,
    *args,
    name: str = None,
    output_file: str = None,
    **kwargs
):
    """
    分析单个函数的性能
    
    Args:
        func: 要分析的函数
        *args: 函数参数
        name: 分析名称
        output_file: 输出文件路径
        **kwargs: 函数关键字参数
        
    Returns:
        函数返回值
    """
    name = name or func.__name__
    
    with profile_context(name, output_file):
        return func(*args, **kwargs)


def compare_functions(
    funcs: list[tuple[Callable, str]],
    iterations: int = 10
):
    """
    比较多个函数的性能
    
    Args:
        funcs: 函数列表，每个元素是 (函数, 名称)
        iterations: 迭代次数
    """
    print(f"\n{'='*60}")
    print(f"FUNCTION COMPARISON ({iterations} iterations)")
    print(f"{'='*60}")
    
    results = []
    
    for func, name in funcs:
        times = []
        
        # 预热
        for _ in range(3):
            func()
        
        # 测试
        for _ in range(iterations):
            start = time.perf_counter()
            result = func()
            end = time.perf_counter()
            times.append(end - start)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        results.append({
            'name': name,
            'avg': avg_time,
            'min': min_time,
            'max': max_time,
            'ops_per_sec': iterations / sum(times)
        })
    
    # 打印结果
    print(f"\n{'Name':<30} {'Avg (s)':<12} {'Min (s)':<12} {'Max (s)':<12} {'Ops/sec':<12}")
    print("-" * 80)
    
    for r in results:
        print(f"{r['name']:<30} {r['avg']:<12.4f} {r['min']:<12.4f} {r['max']:<12.4f} {r['ops_per_sec']:<12.2f}")
    
    # 打印相对性能
    if len(results) > 1:
        baseline = results[0]['avg']
        print(f"\nRelative performance (baseline: {results[0]['name']}):")
        for r in results:
            if r == results[0]:
                print(f"  {r['name']}: 1.00x (baseline)")
            else:
                speedup = baseline / r['avg']
                print(f"  {r['name']}: {speedup:.2f}x")


def profile_memory(func: Callable, *args, **kwargs):
    """
    分析内存使用（需要 memory_profiler）
    
    Args:
        func: 要分析的函数
        *args, **kwargs: 函数参数
    """
    try:
        from memory_profiler import profile as memory_profile
        
        @memory_profile
        def wrapper():
            return func(*args, **kwargs)
        
        return wrapper()
        
    except ImportError:
        print("memory_profiler not installed. Install with: pip install memory-profiler")
        print("Running without memory profiling...")
        return func(*args, **kwargs)


# 测试用例
def test_pdf_text_extraction_profile():
    """测试 PDF 文本提取性能"""
    try:
        from benchmarks import create_test_pdf
        from core.engine.pymupdf_engine_optimized import BufferedPyMuPDFEngine
    except ImportError:
        print("Error: Could not import required modules")
        return
    
    # 创建测试 PDF
    pdf_path = create_test_pdf(num_pages=50, text_per_page=1000)
    
    print(f"Test PDF: {pdf_path}")
    
    def extract_text():
        engine = BufferedPyMuPDFEngine()
        doc = engine.open(pdf_path)
        text = ''.join(engine.extract_text(doc, stream=True))
        engine.close(doc)
        return text
    
    # 性能分析
    profile_function(
        extract_text,
        name="PDF Text Extraction (50 pages)",
        output_file="profile_pdf_extraction.txt"
    )
    
    # 清理
    os.remove(pdf_path)


def test_plugin_discovery_profile():
    """测试插件发现性能"""
    try:
        from core.plugin_system.plugin_manager_optimized import OptimizedPluginManager
    except ImportError:
        print("Error: Could not import required modules")
        return
    
    def discover_plugins():
        manager = OptimizedPluginManager.__new__(OptimizedPluginManager)
        manager._initialized = False
        manager.__init__(enable_cache=True)
        return manager.discover_plugins()
    
    # 性能分析
    profile_function(
        discover_plugins,
        name="Plugin Discovery",
        output_file="profile_plugin_discovery.txt"
    )


def test_parallel_processing_profile():
    """测试并行处理性能"""
    from utils.progress import parallel_process
    
    def dummy_task(n):
        import time
        time.sleep(0.01)
        return n * 2
    
    def parallel_task():
        tasks = list(range(100))
        return parallel_process(tasks, dummy_task, max_workers=4, show_progress=False)
    
    # 性能分析
    profile_function(
        parallel_task,
        name="Parallel Processing (100 tasks)",
        output_file="profile_parallel_processing.txt"
    )


def run_all_profiles():
    """运行所有性能分析"""
    print("=" * 60)
    print("AI-PDF-AGENT PERFORMANCE PROFILING")
    print("=" * 60)
    
    test_pdf_text_extraction_profile()
    test_plugin_discovery_profile()
    test_parallel_processing_profile()
    
    print("\n" + "=" * 60)
    print("PROFILING COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    run_all_profiles()
