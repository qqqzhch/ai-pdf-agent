# AI-PDF-Agent 性能优化使用指南

## 快速开始

### 使用优化的 PDF 引擎

```python
from core.engine.pymupdf_engine_optimized import BufferedPyMuPDFEngine

# 创建优化的引擎
engine = BufferedPyMuPDFEngine(
    page_cache_size=20,  # 缓存 20 页
    workers=4            # 4 个工作线程
)

# 打开 PDF
doc = engine.open("document.pdf")

# 流式提取文本（内存高效）
for page_text in engine.extract_text(doc, stream=True):
    # 处理每页文本
    process_page(page_text)

# 或批量提取所有文本
text = engine.extract_text_batch(doc)

# 关闭 PDF
engine.close(doc)
```

### 使用优化的插件管理器

```python
from core.plugin_system.plugin_manager_optimized import OptimizedPluginManager

# 创建优化的插件管理器
manager = OptimizedPluginManager(
    enable_cache=True,  # 启用缓存
    cache_ttl=3600      # 缓存 1 小时
)

# 发现插件（延迟加载，只获取元数据）
plugins = manager.discover_plugins()

# 按需加载插件
plugin = manager.get_plugin("my_plugin")
if plugin:
    result = plugin.execute(**kwargs)

# 查看性能统计
stats = manager.get_stats()
print(f"Cache hits: {stats['cache_hits']}")
print(f"Cache misses: {stats['cache_misses']}")
```

### 使用并行处理

```python
from utils.progress import parallel_process

def process_page(page_data):
    """处理单页数据"""
    # 你的处理逻辑
    return result

# 准备任务列表
tasks = [page1, page2, page3, ...]

# 并行处理
results = parallel_process(
    tasks=tasks,
    process_func=process_page,
    max_workers=4,
    show_progress=True,
    description="Processing pages"
)
```

## 实际应用示例

### 示例 1：流式处理大型 PDF

```python
import fitz
from core.engine.pymupdf_engine_optimized import BufferedPyMuPDFEngine

def analyze_large_pdf(pdf_path):
    """
    流式分析大型 PDF 文件
    
    适用于：100+ 页的 PDF，内存受限环境
    """
    engine = BufferedPyMuPDFEngine(
        page_cache_size=10,
        workers=4
    )
    
    doc = engine.open(pdf_path)
    total_pages = engine.get_page_count(doc)
    
    print(f"Analyzing {total_pages} pages...")
    
    page_count = 0
    total_text_length = 0
    
    # 流式处理，内存占用恒定
    for page_text in engine.extract_text(doc, stream=True):
        page_count += 1
        total_text_length += len(page_text)
        
        # 可以在这里做实时分析
        # analyze_page(page_text)
        
        # 打印进度
        if page_count % 10 == 0:
            print(f"Processed {page_count}/{total_pages} pages")
    
    engine.close(doc)
    
    print(f"Done! Analyzed {page_count} pages, {total_text_length} characters")
    return page_count, total_text_length

# 使用
analyze_large_pdf("large_document.pdf")
```

### 示例 2：并行提取多个 PDF 的信息

```python
import os
from core.engine.pymupdf_engine_optimized import BufferedPyMuPDFEngine
from utils.progress import parallel_process

def extract_pdf_metadata(pdf_path):
    """提取单个 PDF 的元数据"""
    engine = BufferedPyMuPDFEngine()
    doc = engine.open(pdf_path)
    metadata = engine.get_metadata(doc)
    engine.close(doc)
    return {
        'path': pdf_path,
        'filename': os.path.basename(pdf_path),
        'title': metadata.get('title', ''),
        'pages': metadata.get('page_count', 0),
    }

def batch_extract_metadata(directory):
    """
    批量提取目录中所有 PDF 的元数据
    
    使用并行处理加速
    """
    # 查找所有 PDF 文件
    pdf_files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith('.pdf')
    ]
    
    print(f"Found {len(pdf_files)} PDF files")
    
    # 并行处理
    results = parallel_process(
        tasks=pdf_files,
        process_func=extract_pdf_metadata,
        max_workers=4,
        show_progress=True,
        description="Extracting metadata"
    )
    
    return results

# 使用
metadata_list = batch_extract_metadata("/path/to/pdfs")
for meta in metadata_list:
    print(f"{meta['filename']}: {meta['pages']} pages")
```

### 示例 3：带进度的批量转换

```python
import os
from core.engine.pymupdf_engine_optimized import BufferedPyMuPDFEngine
from utils.progress import ProgressTracker, parallel_map

def convert_pdf_to_text(pdf_path, output_dir):
    """将 PDF 转换为文本"""
    engine = BufferedPyMuPDFEngine()
    doc = engine.open(pdf_path)
    
    # 提取文本
    text = engine.extract_text_batch(doc)
    engine.close(doc)
    
    # 保存文本
    output_path = os.path.join(
        output_dir,
        os.path.basename(pdf_path).replace('.pdf', '.txt')
    )
    
    with with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return output_path

def batch_convert_pdfs(input_dir, output_dir):
    """批量转换 PDF 为文本"""
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找所有 PDF
    pdf_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith('.pdf')
    ]
    
    print(f"Converting {len(pdf_files)} PDF files...")
    
    # 使用进度条
    with ProgressTracker(len(pdf_files), "Converting PDFs") as progress:
        for pdf_path in pdf_files:
            convert_pdf_to_text(pdf_path, output_dir)
            progress.update()
    
    print(f"Done! Converted {len(pdf_files)} files to {output_dir}")

# 使用
batch_convert_pdfs("input_pdfs", "output_texts")
```

### 示例 4：插件按需加载

```python
from core.plugin_system.plugin_manager_optimized import OptimizedPluginManager

class DocumentProcessor:
    """文档处理器 - 按需加载插件"""
    
    def __init__(self):
        # 创建优化的插件管理器
        self.plugin_manager = OptimizedPluginManager(
            enable_cache=True,
            cache_ttl=3600
        )
        
        # 发现插件（不加载）
        self.plugin_manager.discover_plugins()
    
    def process_with_plugin(self, pdf_path, plugin_name, **kwargs):
        """
        使用指定插件处理 PDF
        
        插件只在使用时加载
        """
        # 按需加载插件
        plugin = self.plugin_manager.get_plugin(plugin_name)
        
        if not plugin:
            raise ValueError(f"Plugin {plugin_name} not found")
        
        # 执行插件
        result = plugin.execute(pdf_path=pdf_path, **kwargs)
        
        return result
    
    def list_available_plugins(self):
        """列出所有可用插件（仅元）"""
        return self.plugin_manager.list_plugin_names(include_all=True)

# 使用
processor = DocumentProcessor()

# 列出插件
print("Available plugins:", processor.list_available_plugins())

# 使用插件处理文档
result = processor.process_with_plugin(
    "document.pdf",
    "text_reader",
    include_metadata=True
)
```

## 性能调优建议

### 1. PDF 引擎配置

**小型 PDF（< 20 页）：**
```python
engine = BufferedPyMuPDFEngine(
    page_cache_size=5,   # 小缓存
    workers=2             # 少线程
)
```

**中型 PDF（20-100 页）：**
```python
engine = BufferedPyMuPDFEngine(
    page_cache_size=10,  # 中等缓存
    workers=4             # 4 线程
)
```

**大型 PDF（> 100 页）：**
```python
import os
engine = BufferedPyMuPDFEngine(
    page_cache_size=50,     # 大缓存
    workers=os.cpu_count()  # 所有核心
)
```

### 2. 并行处理配置

**CPU 密集型任务：**
```python
workers = max(1, os.cpu_count() - 1)  # 保留一个核心
```

**I/O 密集型任务：**
```python
workers = min(16, os.cpu_count() * 2)  # 可以用更多线程
```

**混合任务：**
```python
workers = os.cpu_count()  # 平衡
```

### 3. 内存优化

**流式处理（推荐用于大文件）：**
```python
for text in engine.extract_text(doc, stream=True):
    process(text)
```

**批量处理（适合小文件）：**
```python
text = engine.extract_text_batch(doc)
process(text)
```

**页面分块处理：**
```python
def process_in_chunks(doc, chunk_size=50):
    page_count = doc.page_count
    
    for start in range(0, page_count, chunk_size):
        end = min(start + chunk_size, page_count)
        text = engine.extract_text_batch(doc, page_range=(start, end))
        process(text)
```

## 性能监控

### 监控插件管理器

```python
# 获取统计信息
stats = manager.get_stats()

print(f"Discovered: {stats['discovered_plugins']} plugins")
print(f"Loaded: {stats['loaded_plugins']} plugins")
print(f"Cache hits: {stats['cache_hits']}")
print(f"Cache misses: {stats['cache_misses']}")
print(f"Discovery time: {stats['discover_time']:.3f}s")
print(f"Load times:")
for plugin, time in stats['load_time'].items():
    print(f"  {plugin}: {time:.3f}s")
```

### 监控缓存效果

```python
# 第一次加载（缓存未命中）
plugin1 = manager.get_plugin("plugin1")

# 第二次加载（缓存命中）
plugin2 = manager.get_plugin("plugin1")

# 查看缓存统计
stats = manager.get_stats()
print(f"Cache hit ratio: {stats['cache_hits'] / (stats['cache_hits'] + stats['cache_misses']):.2%}")
```

## 故障排除

### 问题 1：内存占用过高

**原因：**
- 页面缓存设置过大
- 使用批量处理而非流式处理
- 并行线程过多

**解决方案：**
```python
# 减少缓存
engine = BufferedPyMuPDFEngine(page_cache_size=5)

# 使用流式处理
for text in engine.extract_text(doc, stream=True):
    process(text)

# 减少线程数
engine = BufferedPyMuPDFEngine(workers=2)
```

### 问题 2：CPU 利用率低

**原因：**
- 线程数设置过少
- GIL 限制（Python 特性）

**解决方案：**
```python
import os
# 增加线程数
engine = BufferedPyMuPDFEngine(workers=os.cpu_count())

# 对于 I/O 密集型任务，可以使用更多线程
engine = BufferedPyMuPDFEngine(workers=16)
```

### 问题 3：插件加载慢

**原因：**
- 插件缓存未启用
- 依赖检查耗时

**解决方案：**
```python
# 启用缓存
manager = OptimizedPluginManager(
    enable_cache=True,
    cache_ttl=7200  # 增加缓存时间
)

# 延迟加载
manager.discover_plugins()  # 只发现元数据
plugin = manager.get_plugin("plugin_name")  # 按需加载
```

## 最佳实践

1. **使用流式处理大文件** - 避免一次性加载所有内容
2. **启用插件缓存** - 显著减少启动时间
3. **合理配置线程数** - 根据 CPU 核心数和任务类型
4. **监控性能统计** - 及时发现瓶颈
5. **按需加载插件** - 只加载需要的插件
6. **选择合适的缓存大小** - 平衡内存和性能
7. **使用并行处理** - 加速批量操作
8. **定期清理缓存** - 避免缓存膨胀

## 更多资源

- 完整性能报告：[PERFORMANCE.md](../PERFORMANCE.md)
- 性能测试：[tests/performance/](../tests/performance/)
- API 文档：[docs/API.md](API.md)

---

**版本：** 2.0.0
**更新日期：** 2026-03-03
