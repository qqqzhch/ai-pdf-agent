"""性能监控模块

提供性能指标收集、记录和报告功能
"""

import functools
import json
import logging
import os
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """性能指标数据类"""

    name: str
    category: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None

    def finish(self, success: bool = True, error: Optional[str] = None):
        """结束计时"""
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error = error

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "category": self.category,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "metadata": self.metadata,
            "success": self.success,
            "error": self.error,
        }


class PerformanceMonitor:
    """性能监控器 - 单例模式"""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.metrics: List[PerformanceMetric] = []
        self.metrics_lock = Lock()
        self.category_stats: Dict[str, Dict] = defaultdict(
            lambda: {
                "count": 0,
                "total_duration": 0.0,
                "min_duration": float("inf"),
                "max_duration": 0.0,
                "success_count": 0,
                "error_count": 0,
            }
        )
        self.enabled = True
        self.log_to_file = False
        self.log_file_path = None
        self._initialized = True

    def enable(self):
        """启用性能监控"""
        self.enabled = True
        logger.info("Performance monitoring enabled")

    def disable(self):
        """禁用性能监控"""
        self.enabled = False
        logger.info("Performance monitoring disabled")

    def enable_file_logging(self, log_file: str = None):
        """启用文件日志"""
        self.log_to_file = True
        if log_file:
            self.log_file_path = log_file
        else:
            log_dir = os.path.expanduser("~/.ai-pdf/logs/performance")
            os.makedirs(log_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file_path = os.path.join(log_dir, f"perf_{timestamp}.log")

        logger.info(f"Performance logging to file: {self.log_file_path}")

    def start_metric(
        self, name: str, category: str = "default", metadata: Dict[str, Any] = None
    ) -> PerformanceMetric:
        """开始一个性能指标"""
        if not self.enabled:
            return None

        metric = PerformanceMetric(
            name=name,
            category=category,
            start_time=time.perf_counter(),
            metadata=metadata or {},
        )

        return metric

    def end_metric(
        self,
        metric: PerformanceMetric,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """结束一个性能指标"""
        if not self.enabled or metric is None:
            return

        metric.finish(success, error)

        with self.metrics_lock:
            self.metrics.append(metric)

        # 更新统计信息
        stats = self.category_stats[metric.category]
        stats["count"] += 1
        stats["total_duration"] += metric.duration
        stats["min_duration"] = min(stats["min_duration"], metric.duration)
        stats["max_duration"] = max(stats["max_duration"], metric.duration)

        if metric.success:
            stats["success_count"] += 1
        else:
            stats["error_count"] += 1

        # 记录到文件
        if self.log_to_file:
            self._log_to_file(metric)

    def _log_to_file(self, metric: PerformanceMetric):
        """记录指标到文件"""
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                timestamp = datetime.now().isoformat()
                log_entry = {"timestamp": timestamp, **metric.to_dict()}
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write performance log: {e}")

    def get_metrics(
        self, category: str = None, name: str = None, limit: int = None
    ) -> List[PerformanceMetric]:
        """获取指标"""
        with self.metrics_lock:
            filtered = self.metrics

            if category:
                filtered = [m for m in filtered if m.category == category]

            if name:
                filtered = [m for m in filtered if m.name == name]

            # 返回最近的指标
            filtered = filtered[-limit:] if limit else filtered

            return filtered

    def get_stats(self, category: str = None) -> Dict:
        """获取统计信息"""
        if category:
            stats = self.category_stats.get(category, {})
            if stats and stats["count"] > 0:
                stats["avg_duration"] = stats["total_duration"] / stats["count"]
                stats["success_rate"] = stats["success_count"] / stats["count"]
            return stats
        else:
            result = {}
            for cat, stats in self.category_stats.items():
                if stats["count"] > 0:
                    stats_copy = dict(stats)
                    stats_copy["avg_duration"] = (
                        stats["total_duration"] / stats["count"]
                    )
                    stats_copy["success_rate"] = stats["success_count"] / stats["count"]
                    result[cat] = stats_copy
            return result

    def clear(self):
        """清空所有指标"""
        with self.metrics_lock:
            self.metrics.clear()
        self.category_stats.clear()
        logger.info("Performance metrics cleared")

    def generate_report(self, output_file: str = None) -> str:
        """生成性能报告"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("AI-PDF-Agent Performance Report")
        report_lines.append(f"Generated: {datetime.now().isoformat()}")
        report_lines.append("=" * 80)
        report_lines.append("")

        # 总体统计
        with self.metrics_lock:
            total_metrics = len(self.metrics)
            total_duration = sum(m.duration for m in self.metrics if m.duration)

        report_lines.append(f"Total Metrics: {total_metrics}")
        report_lines.append(f"Total Duration: {total_duration:.4f}s")
        report_lines.append("")

        # 分类统计
        report_lines.append("-" * 80)
        report_lines.append("Category Statistics")
        report_lines.append("-" * 80)

        stats = self.get_stats()
        for category, cat_stats in sorted(stats.items()):
            report_lines.append(f"\n{category}:")
            report_lines.append(f"  Count: {cat_stats['count']}")
            report_lines.append(f"  Total Duration: {cat_stats['total_duration']:.4f}s")
            report_lines.append(f"  Avg Duration: {cat_stats['avg_duration']:.4f}s")
            report_lines.append(f"  Min Duration: {cat_stats['min_duration']:.4f}s")
            report_lines.append(f"  Max Duration: {cat_stats['max_duration']:.4f}s")
            report_lines.append(f"  Success Rate: {cat_stats['success_rate']:.2%}")
            report_lines.append(f"  Success: {cat_stats['success_count']}")
            report_lines.append(f"  Errors: {cat_stats['error_count']}")

        report_lines.append("")
        report_lines.append("=" * 80)

        report = "\n".join(report_lines)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"Performance report saved to: {output_file}")

        return report

    def export_metrics(self, output_file: str, format: str = "json"):
        """导出指标到文件"""
        with self.metrics_lock:
            data = [m.to_dict() for m in self.metrics]

        if format == "json":
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        elif format == "csv":
            import csv

            with open(output_file, "w", newline="", encoding="utf-8") as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Metrics exported to: {output_file}")


def monitor_performance(
    name: str = None, category: str = "default", log_on_error: bool = True
):
    """性能监控装饰器

    Args:
        name: 操作名称，如果为 None 则使用函数名
        category: 指标类别
        log_on_error: 是否在错误时记录日志

    Example:
        @monitor_performance(category="pdf_operations")
        def extract_text(pdf_path):
            # ... implementation
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            metric_name = name or func.__name__

            metric = monitor.start_metric(metric_name, category)

            try:
                result = func(*args, **kwargs)
                monitor.end_metric(metric, success=True)
                return result
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                monitor.end_metric(metric, success=False, error=error_msg)

                if log_on_error:
                    logger.error(f"Error in {metric_name}: {error_msg}")

                raise

        return wrapper

    return decorator


def profile_function(output_file: str = None):
    """函数性能分析装饰器（使用 cProfile）

    Args:
        output_file: 分析结果输出文件

    Example:
        @profile_function("profile_extract_text.txt")
        def extract_text(pdf_path):
            # ... implementation
            pass
    """
    import cProfile
    import io
    import pstats

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()

            result = func(*args, **kwargs)

            profiler.disable()

            # 输出结果
            if output_file:
                profiler.dump_stats(output_file.replace(".txt", ".prof"))

                # 生成可读报告
                with open(output_file, "w") as f:
                    stats = pstats.Stats(profiler, stream=f)
                    stats.sort_stats("cumulative")
                    stats.print_stats()
            else:
                stats = pstats.Stats(profiler)
                stats.sort_stats("cumulative")
                stats.print_stats()

            return result

        return wrapper

    return decorator


# 全局实例
monitor = PerformanceMonitor()
