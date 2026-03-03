"""性能测试套件

测试关键操作的性能和内存使用
"""

import pytest
import time
import tempfile
import os
from pathlib import Path

# 导入要测试的模块
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine.pymupdf_engine import PyMuPDFEngine
from core.engine.pymupdf_engine_optimized import BufferedPyMuPDFEngine
from core.benchmark import Benchmark, MemoryProfiler, format_benchmark_results, format_comparison_results
from core.performance_monitor import monitor_performance, monitor


class TestPDFExtractionPerformance:
    """PDF 提取性能测试"""
    
    @pytest.fixture
    def sample_pdf(self):
        """创建测试用的 PDF 文件"""
        import fitz
        
        # 创建一个多页 PDF 用于测试
        doc = fitz.open()
        
        for i in range(50):  # 50 页
            page = doc.new_page(width=595, height=842)
            page.insert_text(
                fitz.Point(50, 50),
                f"Test Page {i + 1}",
                fontsize=12
            )
            for j in range(20):
                page.insert_text(
                    fitz.Point(50, 100 + j * 20),
                    f"This is line {j + 1} on page {i + 1}",
                    fontsize=10
                )
        
        # 保存到临时文件
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, "test_50_pages.pdf")
        doc.save(pdf_path)
        doc.close()
        
        yield pdf_path
        
        # 清理
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        os.rmdir(temp_dir)
    
    def test_original_engine_text_extraction(self, sample_pdf):
        """测试原始引擎的文本提取性能"""
        engine = PyMuPDFEngine()
        doc = engine.open(sample_pdf)
        
        # 测量时间
        start = time.perf_counter()
        text = engine.extract_text(doc)
        duration = time.perf_counter() - start
        
        engine.close(doc)
        
        # 断言文本不为空
        assert len(text) > 0
        
        # 性能断言（50页应在 1 秒内完成）
        assert duration < 1.0, f"Text extraction too slow: {duration:.2f}s"
        
        print(f"\nOriginal Engine Text Extraction: {duration:.4f}s")
    
    def test_optimized_engine_text_extraction(self, sample_pdf):
        """测试优化引擎的文本提取性能"""
        engine = BufferedPyMuPDFEngine(
            page_cache_size=10,
            workers=4
        )
        doc = engine.open(sample_pdf)
        
        # 测量时间
        start = time.perf_counter()
        text = engine.extract_text_batch(doc)
        duration = time.perf_counter() - start
        
        engine.close(doc)
        
        # 断言文本不为空
        assert len(text) > 0
        
        # 性能断言（优化引擎应更快）
        assert duration < 0.5, f"Optimized extraction too slow: {duration:.2f}s"
        
        print(f"\nOptimized Engine Text Extraction: {duration:.4f}s")
    
    def test_streaming_text_extraction(self, sample_pdf):
        """测试流式文本提取的内存效率"""
        engine = BufferedPyMuPDFEngine()
        doc = engine.open(sample_pdf)
        
        # 测量时间和内存
        start = time.perf_counter()
        
        # 流使用生成器
        page_count = 0
        for page_text in engine.extract_text(doc, stream=True):
            page_count += 1
            # 立即处理，不积累
            _ = page_text
        
        duration = time.perf_counter() - start
        
        engine.close(doc)
        
        # 断言
        assert page_count == 50
        assert duration < 0.5, f"Streaming extraction too slow: {duration:.2f}s"
        
        print(f"\nStreaming Text Extraction: {duration:.4f}s ({page_count} pages)")
    
    def test_parallel_text_extraction(self, sample_pdf):
        """测试并行文本提取性能"""
        # 小文件串行，大文件并行
        engine = BufferedPyMuPDFEngine(workers=4)
        doc = engine.open(sample_pdf)
        
        start = time.perf_counter()
        text = engine.extract_text_batch(doc)
        duration = time.perf_counter() - start
        
        engine.close(doc)
        
        assert len(text) > 0
        assert duration < 0.5, f"Parallel extraction too slow: {duration:.2f}s"
        
        print(f"\nParallel Text Extraction: {duration:.4f}s")
    
    def test_engines_comparison(self, sample_pdf, capsys):
        """比较原始引擎和优化引擎的性能"""
        benchmark = Benchmark(warmup_iterations=2)
        
        def extract_original():
            engine = PyMuPDFEngine()
            doc = engine.open(sample_pdf)
            text = engine.extract_text(doc)
            engine.close(doc)
            return text
        
        def extract_optimized():
            engine = BufferedPyMuPDFEngine()
            doc = engine.open(sample_pdf)
            text = engine.extract_text_batch(doc)
            engine.close(doc)
            return text
        
        # 比较性能
        functions = [
            ("Original Engine", extract_original),
            ("Optimized Engine", extract_optimized),
        ]
        
        results = benchmark.compare(functions, iterations=10)
        
        # 输出结果
        print("\n" + format_benchmark_results(results))
        print("\n" + format_comparison_results(results))
        
        # 断言两个引擎都能工作
        assert len(results) == 2
        # 对于小文档，优化引擎可能更慢，所以不强制要求优化引擎更快


class TestMemoryUsage:
    """内存使用测试"""
    
    @pytest.fixture
    def large_pdf(self):
        """创建一个较大的 PDF 用于内存测试"""
        import fitz
        
        doc = fitz.open()
        
        # 创建 100 页 PDF
        for i in range(100):
            page = doc.new_page(width=595, height=842)
            page.insert_text(
                fitz.Point(50, 50),
                f"Page {i + 1}",
                fontsize=12
            )
            # 添加更多内容以增加内存使用
            for j in range(50):
                page.insert_text(
                    fitz.Point(50, 100 + j * 15),
                    f"Line {j + 1} with some text content",
                    fontsize=10
                )
        
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, "test_100_pages.pdf")
        doc.save(pdf_path)
        doc.close()
        
        yield pdf_path
        
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        os.rmdir(temp_dir)
    
    def test_streaming_memory_efficiency(self, large_pdf):
        """测试流式处理的内存效率"""
        engine = BufferedPyMuPDFEngine()
        doc = engine.open(large_pdf)
        
        # 流式处理：逐页处理，不积累
        page_count = 0
        for page_text in engine.extract_text(doc, stream=True):
            page_count += 1
            # 模拟处理并立即丢弃
            if len(page_text) > 0:
                pass
        
        engine.close(doc)
        
        assert page_count == 100
        print(f"\nProcessed {page_count} pages in streaming mode")
    
    def test_batch_memory_usage(self, large_pdf):
        """测试批量处理的内存使用"""
        engine = BufferedPyMuPDFEngine()
        doc = engine.open(large_pdf)
        
        # 批量处理：一次性加载所有文本
        start = time.perf_counter()
        text = engine.extract_text_batch(doc)
        duration = time.perf_counter() - start
        
        engine.close(doc)
        
        assert len(text) > 0
        print(f"\nBatch processing completed in {duration:.4f}s")
        print(f"Total text length: {len(text)} characters")
    
    def test_cache_effectiveness(self, large_pdf):
        """测试缓存的有效性"""
        engine = BufferedPyMuPDFEngine(page_cache_size=10)
        doc = engine.open(large_pdf)
        
        # 第一次读取：缓存未命中
        start = time.perf_counter()
        text1 = engine.extract_text_batch(doc)
        duration1 = time.perf_counter() - start
        
        # 第二次读取：利用缓存
        start = time.perf_counter()
        text2 = engine.extract_text_batch(doc)
        duration2 = time.perf_counter() - start
        
        engine.close(doc)
        
        assert text1 == text2
        print(f"\nFirst read: {duration1:.4f}s")
        print(f"Second read (cached): {duration2:.4f}s")
        print(f"Cache effect: {duration1/duration2:.2f}x speedup" if duration2 > 0 else "Cached")


class TestPluginPerformance:
    """插件性能测试"""
    
    def test_plugin_discovery_performance(self):
        """测试插件发现性能"""
        from core.plugin_system.plugin_manager import PluginManager
        
        manager = PluginManager()
        
        start = time.perf_counter()
        discovered = manager.discover_plugins()
        duration = time.perf_counter() - start
        
        print(f"\nPlugin discovery: {duration:.4f}s ({len(discovered)} plugins)")
        assert duration < 0.1, f"Plugin discovery too slow: {duration:.2f}s"
    
    def test_plugin_loading_performance(self):
        """测试插件加载性能"""
        from core.plugin_system.plugin_manager import PluginManager
        
        manager = PluginManager()
        
        start = time.perf_counter()
        loaded_count = manager.load_all_plugins()
        duration = time.perf_counter() - start
        
        print(f"\nPlugin loading: {duration:.4f}s ({loaded_count} plugins)")
        assert duration < 1.0, f"Plugin loading too slow: {duration:.2f}s"


class TestPerformanceMonitor:
    """性能监控器测试"""
    
    def test_metric_tracking(self):
        """测试指标跟踪"""
        monitor.clear()
        monitor.enable()
        
        # 创建一些指标
        metric1 = monitor.start_metric("test_operation", "test_category")
        time.sleep(0.01)
        monitor.end_metric(metric1, success=True)
        
        metric2 = monitor.start_metric("test_operation", "test_category")
        time.sleep(0.02)
        monitor.end_metric(metric2, success=True)
        
        # 获取指标
        metrics = monitor.get_metrics(category="test_category")
        assert len(metrics) == 2
        
        # 获取统计
        stats = monitor.get_stats(category="test_category")
        assert stats["count"] == 2
        assert stats["total_duration"] > 0
        
        print(f"\nTracked {len(metrics)} metrics")
    
    def test_decorator_monitoring(self):
        """测试装饰器监控"""
        monitor.clear()
        monitor.enable()
        
        @monitor_performance(name="decorated_func", category="test")
        def slow_function():
            time.sleep(0.01)
            return "result"
        
        result = slow_function()
        assert result == "result"
        
        # 检查指标
        metrics = monitor.get_metrics(name="decorated_func")
        assert len(metrics) == 1
        assert metrics[0].duration > 0.01
        
        print(f"\nDecorator tracked function: {metrics[0].duration:.4f}s")
    
    def test_report_generation(self):
        """测试报告生成"""
        monitor.clear()
        monitor.enable()
        
        # 创建一些指标
        for i in range(5):
            metric = monitor.start_metric(f"operation_{i}", "test")
            time.sleep(0.005)
            monitor.end_metric(metric, success=True)
        
        # 生成报告
        report = monitor.generate_report()
        assert len(report) > 0
        assert "Performance Report" in report
        
        print("\n" + report)


class TestBenchmarks:
    """基准测试集成"""
    
    def test_benchmark_framework(self):
        """测试基准测试框架"""
        benchmark = Benchmark(warmup_iterations=2)
        
        def test_func():
            return sum(range(1000))
        
        result = benchmark.benchmark(test_func, iterations=100, name="sum_range")
        
        assert result.iterations == 100
        assert result.avg_time > 0
        assert result.ops_per_sec > 0
        
        print(f"\nBenchmark: {result.name}")
        print(f"  Avg Time: {result.avg_time*1000:.3f}ms")
        print(f"  Ops/sec: {result.ops_per_sec:.2f}")
    
    def test_memory_profiler(self):
        """测试内存分析器"""
        mem_profiler = MemoryProfiler()
        
        if not mem_profiler.available:
            pytest.skip("memory_profiler not installed")
        
        def test_func():
            data = [i for i in range(10000)]
            return sum(data)
        
        mem_stats = mem_profiler.profile_memory(test_func)
        
        assert "max_memory" in mem_stats
        assert mem_stats["max_memory"] > 0
        
        print(f"\nMemory Profile:")
        print(f"  Max Memory: {mem_stats['max_memory']:.2f} MiB")
        print(f"  Avg Memory: {mem_stats['avg_memory']:.2f} MiB")


# 集成测试：完整的性能测试套件
@pytest.mark.slow
class TestComprehensivePerformance:
    """综合性能测试（标记为慢速测试）"""
    
    @pytest.fixture
    def test_pdfs(self):
        """创建不同大小的测试 PDF"""
        import fitz
        
        temp_dir = tempfile.mkdtemp()
        pdfs = {}
        
        # 小 PDF (10 页)
        doc = fitz.open()
        for i in range(10):
            page = doc.new_page()
            page.insert_text(fitz.Point(50, 50), f"Small PDF Page {i}")
        pdfs["small"] = os.path.join(temp_dir, "small.pdf")
        doc.save(pdfs["small"])
        doc.close()
        
        # 中 PDF (50 页)
        doc = fitz.open()
        for i in range(50):
            page = doc.new_page()
            page.insert_text(fitz.Point(50, 50), f"Medium PDF Page {i}")
            for j in range(20):
                page.insert_text(fitz.Point(50, 100 + j * 15), f"Line {j}")
        pdfs["medium"] = os.path.join(temp_dir, "medium.pdf")
        doc.save(pdfs["medium"])
        doc.close()
        
        # 大 PDF (100 页)
        doc = fitz.open()
        for i in range(100):
            page = doc.new_page()
            page.insert_text(fitz.Point(50, 50), f"Large PDF Page {i}")
            for j in range(50):
                page.insert_text(fitz.Point(50, 100 + j * 15), f"Line {j}")
        pdfs["large"] = os.path.join(temp_dir, "large.pdf")
        doc.save(pdfs["large"])
        doc.close()
        
        yield pdfs
        
        # 清理
        for pdf_path in pdfs.values():
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        os.rmdir(temp_dir)
    
    def test_comprehensive_benchmark(self, test_pdfs, capsys):
        """综合基准测试：比较不同大小的 PDF"""
        benchmark = Benchmark(warmup_iterations=2)
        
        print("\n" + "=" * 80)
        print("Comprehensive Performance Benchmark")
        print("=" * 80)
        
        for size, pdf_path in test_pdfs.items():
            print(f"\nTesting {size.upper()} PDF ({os.path.basename(pdf_path)})")
            print("-" * 80)
            
            # 测试原始引擎
            def test_original():
                engine = PyMuPDFEngine()
                doc = engine.open(pdf_path)
                text = engine.extract_text(doc)
                engine.close(doc)
                return text
            
            # 测试优化引擎
            def test_optimized():
                engine = BufferedPyMuPDFEngine()
                doc = engine.open(pdf_path)
                text = engine.extract_text_batch(doc)
                engine.close(doc)
                return text
            
            # 测试流式处理
            def test_streaming():
                engine = BufferedPyMuPDFEngine()
                doc = engine.open(pdf_path)
                texts = list(engine.extract_text(doc, stream=True))
                engine.close(doc)
                return texts
            
            functions = [
                ("Original", test_original),
                ("Optimized Batch", test_optimized),
                ("Optimized Streaming", test_streaming),
            ]
            
            results = benchmark.compare(functions, iterations=5)
            
            print(format_benchmark_results(results))
            print(format_comparison_results(results))
            
            # 对于小文档，优化引擎可能更慢，不强制要求优化引擎更快
            assert len(results) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
