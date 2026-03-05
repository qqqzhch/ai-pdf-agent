"""性能基准测试套件

使用 cProfile 和 timeit 进行性能基准测试
"""

import cProfile
import io
import os
import pstats
import time
import timeit
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


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

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "iterations": self.iterations,
            "total_time": self.total_time,
            "avg_time": self.avg_time,
            "min_time": self.min_time,
            "max_time": self.max_time,
            "ops_per_sec": self.ops_per_sec,
        }


class Benchmark:
    """基准测试器"""

    def __init__(self, warmup_iterations: int = 3):
        """
        Args:
            warmup_iterations: 预热迭代次数
        """
        self.warmup_iterations = warmup_iterations

    def benchmark(
        self,
        func: callable,
        iterations: int = 100,
        name: str = None,
        setup: callable = None,
    ) -> BenchmarkResult:
        """
        执行基准测试

        Args:
            func: 要测试的函数
            iterations: 迭代次数
            name: 测试名称
            setup: 每次迭代前的设置函数

        Returns:
            BenchmarkResult
        """
        name = name or func.__name__

        # 预热
        if setup:
            setup()

        for _ in range(self.warmup_iterations):
            if setup:
                setup()
            func()

        # 正式测试
        times = []

        for _ in range(iterations):
            if setup:
                setup()

            start = time.perf_counter()
            func()
            end = time.perf_counter()

            times.append(end - start)

        total_time = sum(times)
        avg_time = total_time / iterations
        min_time = min(times)
        max_time = max(times)
        ops_per_sec = 1.0 / avg_time if avg_time > 0 else 0.0

        return BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            ops_per_sec=ops_per_sec,
        )

    def compare(
        self,
        functions: List[Tuple[str, callable]],
        iterations: int = 100,
        setup: callable = None,
    ) -> List[BenchmarkResult]:
        """
        比较多个函数的性能

        Args:
            functions: (name, func) 列表
            iterations: 迭代次数
            setup: 设置函数

        Returns:
            结果列表，按平均时间排序
        """
        results = []

        for name, func in functions:
            result = self.benchmark(func, iterations, name, setup)
            results.append(result)

        # 按平均时间排序
        results.sort(key=lambda r: r.avg_time)

        return results

    def profile(
        self,
        func: callable,
        name: str = None,
        output_file: str = None,
        setup: callable = None,
    ) -> pstats.Stats:
        """
        使用 cProfile 进行性能分析

        Args:
            func: 要分析的函数
            name: 分析名称
            output_file: 输出文件
            setup: 设置函数

        Returns:
            pstats.Stats
        """
        name = name or func.__name__

        if setup:
            setup()

        profiler = cProfile.Profile()
        profiler.enable()

        func()

        profiler.disable()

        stats = pstats.Stats(profiler)
        stats.sort_stats("cumulative")

        if output_file:
            # 保存到文件
            profiler.dump_stats(output_file.replace(".txt", ".prof"))

            with open(output_file, "w") as f:
                stats.stream = f
                stats.print_stats()

        return stats


class MemoryProfiler:
    """内存分析器"""

    def __init__(self):
        try:
            import memory_profiler

            self.memory_profiler = memory_profiler
            self.available = True
        except ImportError:
            self.available = False

    def profile_memory(self, func: callable, setup: callable = None) -> Dict:
        """
        分析函数的内存使用

        Args:
            func: 要分析的函数
            setup: 设置函数

        Returns:
            内存使用统计
        """
        if not self.available:
            return {"error": "memory_profiler not installed"}

        if setup:
            setup()

        # 使用 memory_profiler 进行分析
        mem_usage = self.memory_profiler.memory_usage((func, (), {}))

        return {
            "max_memory": max(mem_usage),
            "min_memory": min(mem_usage),
            "avg_memory": sum(mem_usage) / len(mem_usage),
            "memory_usage_samples": mem_usage,
        }

    def compare_memory(
        self, functions: List[Tuple[str, callable]], setup: callable = None
    ) -> List[Dict]:
        """
        比较多个函数的内存使用

        Args:
            functions: (name, func) 列表
            setup: 设置函数

        Returns:
            内存使用结果列表
        """
        results = []

        for name, func in functions:
            mem_stats = self.profile_memory(func, setup)
            mem_stats["name"] = name
            results.append(mem_stats)

        # 按最大内存使用排序
        results.sort(key=lambda r: r.get("max_memory", 0))

        return results


def format_benchmark_results(results: List[BenchmarkResult]) -> str:
    """格式化基准测试结果"""
    lines = []
    lines.append("=" * 80)
    lines.append("Benchmark Results")
    lines.append("=" * 80)
    lines.append("")

    # 表头
    lines.append(
        f"{'Name':<30} {'Iterations':<12} {'Avg Time':<12} {'Min Time':<12} {'Max Time':<12} {'Ops/sec':<12}"
    )
    lines.append("-" * 80)

    for result in results:
        lines.append(
            f"{result.name:<30} "
            f"{result.iterations:<12} "
            f"{result.avg_time*1000:>8.3f}ms  "
            f"{result.min_time*1000:>8.3f}ms  "
            f"{result.max_time*1000:>8.3f}ms  "
            f"{result.ops_per_sec:>8.2f}"
        )

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def format_comparison_results(results: List[BenchmarkResult]) -> str:
    """格式化比较结果"""
    lines = []
    lines.append("=" * 80)
    lines.append("Performance Comparison")
    lines.append("=" * 80)
    lines.append("")

    if not results:
        lines.append("No results")
        return "\n".join(lines)

    baseline = results[0]

    lines.append(f"Baseline: {baseline.name}")
    lines.append(f"Average Time: {baseline.avg_time*1000:.3f}ms")
    lines.append("")
    lines.append("-" * 80)

    for result in results[1:]:
        speedup = baseline.avg_time / result.avg_time
        lines.append(f"{result.name}:")
        lines.append(f"  Average Time: {result.avg_time*1000:.3f}ms")
        lines.append(f"  Speedup: {speedup:.2f}x")
        lines.append(
            f"  Improvement: {(1 - result.avg_time/baseline.avg_time)*100:.1f}%"
        )
        lines.append("")

    lines.append("=" * 80)

    return "\n".join(lines)


def format_memory_results(results: List[Dict]) -> str:
    """格式化内存分析结果"""
    lines = []
    lines.append("=" * 80)
    lines.append("Memory Usage Results")
    lines.append("=" * 80)
    lines.append("")

    for result in results:
        name = result.get("name", "Unknown")
        max_mem = result.get("max_memory", 0)
        min_mem = result.get("min_memory", 0)
        avg_mem = result.get("avg_memory", 0)

        lines.append(f"{name}:")
        lines.append(f"  Max Memory: {max_mem:.2f} MiB")
        lines.append(f"  Min Memory: {min_mem:.2f} MiB")
        lines.append(f"  Avg Memory: {avg_mem:.2f} MiB")
        lines.append("")

    lines.append("=" * 80)

    return "\n".join(lines)


# 基准测试示例
if __name__ == "__main__":
    # 示例：比较两个函数的性能
    def fast_function():
        return sum(range(1000))

    def slow_function():
        s = 0
        for i in range(1000):
            s += i
        return s

    benchmark = Benchmark()

    functions = [
        ("Fast Function", fast_function),
        ("Slow Function", slow_function),
    ]

    results = benchmark.compare(functions, iterations=1000)

    print(format_benchmark_results(results))
    print(format_comparison_results(results))

    # 内存使用分析
    mem_profiler = MemoryProfiler()
    if mem_profiler.available:
        mem_results = mem_profiler.compare_memory(functions)
        print(format_memory_results(mem_results))
