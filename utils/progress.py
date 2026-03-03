"""进度显示和并行处理工具"""

import time
import threading
from typing import Callable, Any, List, Optional, Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys


class ProgressTracker:
    """简单的进度跟踪器（无第三方依赖）"""
    
    def __init__(
        self, 
        total: int,
        description: str = "Processing",
        show_percentage: bool = True
    ):
        """
        初始化进度跟踪器
        
        Args:
            total: 总任务数
            description: 描述文本
            show_percentage: 是否显示百分比
        """
        self.total = total
        self.completed = 0
        self.description = description
        self.show_percentage = show_percentage
        self.start_time = time.time()
        self.last_update = 0
        self.lock = threading.Lock()
        self._update_interval = 0.1  # 100ms 更新间隔
        self._spinner_chars = ['|', '/', '-', '\\']
        self._spinner_index = 0
        
    def update(self, n: int = 1):
        """
        更新进度
        
        Args:
            n: 完成的任务数
        """
        with self.lock:
            self.completed += n
            self._spinner_index = (self._spinner_index + 1) % len(self._spinner_chars)
            
            # 限制更新频率
            now = time.time()
            if now - self.last_update < self._update_interval:
                return
            
            self.last_update = now
            self._print_progress()
    
    def _print_progress(self):
        """打印进度"""
        if self.show_percentage:
            percentage = (self.completed / self.total) * 100
            bar_length = 30
            filled = int(bar_length * self.completed / self.total)
            bar = '=' * filled + ' ' * (bar_length - filled)
            
            elapsed = time.time() - self.start_time
            if self.completed > 0:
                eta = (elapsed / self.completed) * (self.total - self.completed)
            else:
                eta = 0
            
            spinner = self._spinner_chars[self._spinner_index]
            sys.stdout.write(
                f"\r{spinner} {self.description}: [{bar}] "
                f"{self.completed}/{self.total} ({percentage:.1f}%) "
                f"ETA: {eta:.1f}s"
            )
        else:
            sys.stdout.write(f"\r{self.description}: {self.completed}/{self.total}")
        
        sys.stdout.flush()
    
    def finish(self, success: bool = True):
        """
        完成进度显示
        
        Args:
            success: 是否成功
        """
        with self.lock:
            self.completed = self.total
            self._print_progress()
            
            elapsed = time.time() - self.start_time
            
            if success:
                status = "✓ Done"
            else:
                status = "✗ Failed"
            
            sys.stdout.write(f"\r{status} - {self.description} completed in {elapsed:.2f}s\n")
            sys.stdout.flush()


def parallel_process(
    tasks: List[Any],
    process_func: Callable,
    max_workers: int = 4,
    show_progress: bool = True,
    description: str = "Processing"
) -> List[Any]:
    """
    并行处理任务
    
    Args:
        tasks: 任务列表
        process_func: 处理函数（接受任务作为参数）
        max_workers: 最大工作线程数
        show_progress: 是否显示进度
        description: 进度描述
        
    Returns:
        结果列表（按任务顺序）
    """
    if not tasks:
        return []
    
    results = {}
    progress = None
    
    if show_progress:
        progress = ProgressTracker(len(tasks), description)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = {
            executor.submit(process_func, task): task
            for task in tasks
        }
        
        # 收集结果
        for future in as_completed(futures):
            task = futures[future]
            try:
                result = future.result()
                results[task] = result
            except Exception as e:
                results[task] = e
            
            if progress:
                progress.update()
    
    if progress:
        progress.finish(success=True)
    
    # 按任务顺序返回结果
    return [results.get(task) for task in tasks]


def stream_process(
    items: Generator[Any, None, None],
    process_func: Callable,
    batch_size: int = 10,
    show_progress: bool = False
) -> Generator[Any, None, None]:
    """
    流式处理数据
    
    Args:
        items: 项目生成器
        process_func: 处理函数
        batch_size: 批处理大小
        show_progress: 是否显示进度
        
    Yields:
        处理后的项目
    """
    batch = []
    batch_count = 0
    total_processed = 0
    
    for item in items:
        batch.append(item)
        
        if len(batch) >= batch_size:
            # 批量处理
            for result in batch:
                processed = process_func(result)
                yield processed
                total_processed += 1
            
            if show_progress:
                sys.stdout.write(f"\rProcessed: {total_processed}")
                batch_count += 1
            
            batch.clear()
    
    # 处理剩余项目
    for result in batch:
        processed = process_func(result)
        yield processed
        total_processed += 1
    
    if show_progress:
        sys.stdout.write(f"\rTotal processed: {total_processed}\n")
        sys.stdout.flush()


class ProgressContext:
    """进度上下文管理器"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.description = description
        self.tracker: Optional[ProgressTracker] = None
    
    def __enter__(self):
        self.tracker = ProgressTracker(self.total, self.description)
        return self.tracker
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tracker:
            self.tracker.finish(success=(exc_type is None))
        return False


class ParallelProgress:
    """带进度显示的并行处理器"""
    
    def __init__(
        self,
        max_workers: int = 4,
        show_progress: bool = True
    ):
        self.max_workers = max_workers
        self.show_progress = show_progress
    
    def process(
        self,
        tasks: List[Any],
        process_func: Callable,
        description: str = "Processing"
    ) -> List[Any]:
        """
        并行处理任务
        
        Args:
            tasks: 任务列表
            process_func: 处理函数
            description: 进度描述
            
        Returns:
            结果列表
        """
        return parallel_process(
            tasks,
            process_func,
            self.max_workers,
            self.show_progress,
            description
        )
    
    def process_dict(
        self,
        tasks: Dict[Any, Any],
        process_func: Callable,
        description: str = "Processing"
    ) -> Dict[Any, Any]:
        """
        并行处理字典任务
        
        Args:
            tasks: 任务字典 {key: task}
            process_func: 处理函数
            description: 进度描述
            
        Returns:
            结果字典 {key: result}
        """
        keys = list(tasks.keys())
        task_list = [tasks[key] for key in keys]
        
        results = parallel_process(
            task_list,
            process_func,
            self.max_workers,
            self.show_progress,
            description
        )
        
        return {k: v for k, v in zip(keys, results)}


# 便捷函数
def parallel_map(
    func: Callable,
    items: List[Any],
    workers: int = 4,
    progress: bool = True
) -> List[Any]:
    """
    并行 map 函数
    
    Args:
        func: 映射函数
        items: 项目列表
        workers: 工作线程数
        progress: 是否显示进度
        
    Returns:
        映射结果列表
    """
    return parallel_process(
        items,
        func,
        workers,
        show_progress=progress,
        description="Mapping"
    )


def parallel_map_dict(
    func: Callable,
    items: Dict[Any, Any],
    workers: int = 4,
    progress: bool = True
) -> Dict[Any, Any]:
    """
    并行 map 字典
    
    Args:
        func: 映射函数
        items: 项目字典
        workers: 工作线程数
        progress: 是否显示进度
        
    Returns:
        映射结果字典
    """
    keys = list(items.keys())
    value_list = [items[key] for key in keys]
    
    results = parallel_map(func, value_list, workers, progress)
    
    return {k: v for k, v in zip(keys, results)}
