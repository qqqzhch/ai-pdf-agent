# 使用示例

本文档提供了 ai-pdf-agent 的详细使用示例，帮助您快速上手并充分利用其功能。

## 目录

- [基础使用示例](#基础使用示例)
  - [读取 PDF 文本](#读取-pdf-文本)
  - [转换 PDF 格式](#转换-pdf-格式)
  - [提取 PDF 图片](#提取-pdf-图片)
  - [管理 PDF 元数据](#管理-pdf-元数据)
- [高级使用示例](#高级使用示例)
  - [页面范围处理](#页面范围处理)
  - [自定义插件配置](#自定义插件配置)
  - [错误处理](#错误处理)
- [批量处理示例](#批量处理示例)
  - [批量转换目录](#批量转换目录)
  - [批量提取信息](#批量提取信息)
  - [并行处理](#并行处理)
- [集成示例](#集成示例)
  - [与 Flask 集成](#与-flask-集成)
  - [与 FastAPI 集成](#与-fastapi-集成)
  - [与 Django 集成](#与-django-集成)
- [最佳实践](#最佳实践)
  - [性能优化建议](#性能优化建议)
  - [错误处理建议](#错误处理建议)
  - [安全建议](#安全建议)

---

## 基础使用示例

### 读取 PDF 文本

**示例 1：读取整个 PDF 文件的文本内容**

```python
from ai_pdf_agent import PDFProcessor

# 初始化处理器
processor = PDFProcessor()

# 读取 PDF 文本
text = processor.extract_text('document.pdf')

# 输出文本
print(text)
```

**预期输出：**
```
这是 PDF 文档的第一页内容。

这是 PDF 文档的第二页内容，包含更多的文本信息。
...
```

**示例 2：读取指定页面的文本**

```python
from ai_pdf_agent import PDFProcessor

processor = PDFProcessor()

# 只读取第一页
text_page1 = processor.extract_text('document.pdf', pages=[1])

# 读取第 3 到第 5 页
text_range = processor.extract_text('document.pdf', pages=[3, 4, 5])

print(f"第一页内容：\n{text_page1}")
print(f"第 3-5 页内容：\n{text_range}")
```

---

### 转换 PDF 格式

**示例 1：将 PDF 转换为 Markdown**

```python
from ai_pdf_agent import PDFConverter

converter = PDFConverter()

# 转换为 Markdown
markdown_text = converter.to_markdown('document.pdf', output='output.md')

print(f"Markdown 文件已保存到：{markdown_text}")
```

**预期输出：**
```
Markdown 文件已保存到：output.md
```

**示例 2：将 PDF 转换为纯文本**

```python
from ai_pdf_agent import PDFConverter

converter = PDFConverter()

# 转换为纯文本
text_file = converter.to_text('document.pdf', output='output.txt')

print(f"文本文件已保存到：{text_file}")
```

**示例 3：将 PDF 转换为 HTML**

```python
from ai_pdf_agent import PDFConverter

converter = PDFConverter()

# 转换为 HTML
html_file = converter.to_html('document.pdf', output='output.html')

print(f"HTML 文件已保存到：{html_file}")
```

---

### 提取 PDF 图片

**示例 1：提取所有图片**

```python
from ai_pdf_agent import PDFImageExtractor

extractor = PDFImageExtractor()

# 提取所有图片到指定目录
images = extractor.extract_all('document.pdf', output_dir='images')

print(f"共提取 {len(images)} 张图片：")
for img in images:
    print(f"  - {img}")
```

**预期输出：**
```
共提取 3 张图片：
  - images/image_0_page_1.png
  - images/image_1_page_2.png
  - images/image_2_page_3.png
```

**示例 2：提取指定页面的图片**

```python
from ai_pdf_agent import PDFImageExtractor

extractor = PDFImageExtractor()

# 只提取第 2 页的图片
images = extractor.extract_from_pages('document.pdf', pages=[2], output_dir='images')

print(f"第 2 页的图片：{images}")
```

**示例 3：获取图片信息（不提取）**

```python
from ai_pdf_agent import PDFImageExtractor

extractor = PDFImageExtractor()

# 获取图片信息
info = extractor.get_image_info('document.pdf')

print("图片信息：")
for img_info in info:
    print(f"  页面 {img_info['page']}: {img_info['width']}x{img_info['height']}")
```

---

### 管理 PDF 元数据

**示例 1：读取 PDF 元数据**

```python
from ai_pdf_agent import PDFMetadataManager

manager = PDFMetadataManager()

# 读取元数据
metadata = manager.read('document.pdf')

print("PDF 元数据：")
print(f"  标题：{metadata.get('title', 'N/A')}")
print(f"  作者：{metadata.get('author', 'N/A')}")
print(f"  主题：{metadata.get('subject', 'N/A')}")
print(f"  创建日期：{metadata.get('creation_date', 'N/A')}")
print(f"  页数：{metadata.get('page_count', 'N/A')}")
```

**预期输出：**
```
PDF 元数据：
  标题：示例文档
  作者：张三
  主题：PDF 处理示例
  创建日期：2026-03-03
  页数：10
```

**示例 2：更新 PDF 元数据**

```python
from ai_pdf_agent import PDFMetadataManager

manager = PDFMetadataManager()

# 更新元数据
new_metadata = {
    'title': '新标题',
    'author': '李四',
    'subject': '更新的主题',
    'keywords': 'PDF, 处理, 示例'
}

manager.update('document.pdf', new_metadata, output='updated_document.pdf')

print("元数据已更新，保存到：updated_document.pdf")
```

**示例 3：添加自定义元数据**

```python
from ai_pdf_agent import PDFMetadataManager

manager = PDFMetadataManager()

# 添加自定义元数据
custom_metadata = {
    'custom_field': '自定义值',
    'document_version': '1.2.3',
    'reviewer': '王五'
}

manager.add_custom('document.pdf', custom_metadata, output='custom_document.pdf')

print("自定义元数据已添加")
```

---

## 高级使用示例

### 页面范围处理

**示例 1：提取页面范围**

```python
from ai_pdf_agent import PDFProcessor

processor = PDFProcessor()

# 提取第 1-3 页
processor.extract_pages('document.pdf', pages='1-3', output='pages_1_3.pdf')

# 提取第 5, 7, 9 页
processor.extract_pages('document.pdf', pages='5,7,9', output='pages_selected.pdf')

# 提取第 10 页到最后一页
processor.extract_pages('document.pdf', pages='10-end', output='pages_to_end.pdf')

print("页面提取完成")
```

**示例 2：合并多个 PDF**

```python
from ai_pdf_agent import PDFMerger

merger = PDFMerger()

# 合并多个 PDF 文件
merger.merge(
    input_files=['doc1.pdf', 'doc2.pdf', 'doc3.pdf'],
    output='merged_document.pdf'
)

print("PDF 文件已合并")
```

**示例 3：拆分 PDF 为单页文件**

```python
from ai_pdf_agent import PDFSplitter

splitter = PDFSplitter()

# 拆分为单页文件
output_files = splitter.split_to_single_pages('document.pdf', output_dir='single_pages')

print(f"已拆分为 {len(output_files)} 个单页文件")
for file in output_files:
    print(f"  - {file}")
```

---

### 自定义插件配置

**示例 1：使用自定义 OCR 插件**

```python
from ai_pdf_agent import PDFProcessor, OCRPlugin

# 创建自定义 OCR 配置
ocr_config = {
    'language': 'chi_sim+eng',  # 简体中文 + English
    'dpi': 300,
    'preprocess': True,
    'output_format': 'text'
}

# 初始化处理器并配置插件
processor = PDFProcessor()
processor.register_plugin('ocr', OCRPlugin(ocr_config))

# 使用 OCR 提取文本
text = processor.extract_text('scanned_document.pdf', use_ocr=True)

print(text)
```

**示例 2：使用自定义文本清理插件**

```python
from ai_pdf_agent import TextCleanerPlugin

# 自定义清理规则
cleaner_config = {
    'remove_extra_spaces': True,
    'normalize_unicode': True,
    'fix_line_breaks': True,
    'custom_patterns': {
        'remove_page_numbers': r'第\s*\d+\s*页',
        'remove_headers': r'^[A-Z]{2,}-\d+'
    }
}

cleaner = TextCleanerPlugin(cleaner_config)

# 清理文本
cleaned_text = cleaner.clean(raw_text)

print(cleaned_text)
```

**示例 3：使用自定义格式转换插件**

```python
from ai_pdf_agent import FormatConverterPlugin

# 自定义转换规则
converter_config = {
    'markdown': {
        'headers': {
            'h1': '# ',
            'h2': '## ',
            'h3': '### '
        },
        'lists': {
            'bullet': '- ',
            'numbered': '1. '
        },
        'code_blocks': {
            'prefix': '```',
            'suffix': '```'
        }
    }
}

converter = FormatConverterPlugin(converter_config)

markdown_output = converter.convert_to_markdown(pdf_content)
```

---

### 错误处理

**示例 1：基本的错误处理**

```python
from ai_pdf_agent import PDFProcessor, PDFError

processor = PDFProcessor()

try:
    text = processor.extract_text('document.pdf')
    print(text)
except PDFError as e:
    print(f"PDF 处理错误：{e}")
except FileNotFoundError:
    print("文件不存在，请检查路径")
except Exception as e:
    print(f"未知错误：{e}")
```

**示例 2：详细的错误信息**

```python
from ai_pdf_agent import PDFProcessor, PDFError

processor = PDFProcessor()

try:
    text = processor.extract_text('corrupted.pdf')
except PDFError as e:
    print(f"错误类型：{e.error_type}")
    print(f"错误消息：{e.message}")
    print(f"文件路径：{e.file_path}")
    print(f"堆栈跟踪：{e.traceback}")
    
    # 根据错误类型采取不同措施
    if e.error_type == 'encryption':
        print("文件已加密，需要密码")
    elif e.error_type == 'corruption':
        print("文件已损坏，尝试修复")
```

**示例 3：使用上下文管理器**

```python
from ai_pdf_agent import PDFProcessor

with PDFProcessor() as processor:
    try:
        text = processor.extract_text('document.pdf')
        print(text)
    except Exception as e:
        print(f"处理失败：{e}")
        # 自动清理资源
```

**示例 4：批量处理的错误处理**

```python
from ai_pdf_agent import PDFProcessor
import os

processor = PDFProcessor()
failed_files = []

for filename in os.listdir('pdfs'):
    if filename.endswith('.pdf'):
        try:
            text = processor.extract_text(f'pdfs/{filename}')
            # 处理文本...
            print(f"✓ {filename} 处理成功")
        except Exception as e:
            failed_files.append((filename, str(e)))
            print(f"✗ {filename} 处理失败：{e}")

if failed_files:
    print("\n失败的文件：")
    for filename, error in failed_files:
        print(f"  - {filename}: {error}")
```

---

## 批量处理示例

### 批量转换目录

**示例 1：转换目录下所有 PDF**

```python
from ai_pdf_agent import PDFConverter
import os

converter = PDFConverter()
pdf_dir = 'input_pdfs'
output_dir = 'converted'

# 创建输出目录
os.makedirs(output_dir, exist_ok=True)

# 批量转换
for filename in os.listdir(pdf_dir):
    if filename.endswith('.pdf'):
        input_path = os.path.join(pdf_dir, filename)
        output_path = os.path.join(output_dir, filename.replace('.pdf', '.md'))
        
        try:
            converter.to_markdown(input_path, output=output_path)
            print(f"✓ 转换成功：{filename}")
        except Exception as e:
            print(f"✗ 转换失败：{filename} - {e}")

print(f"\n批量转换完成，结果保存在 {output_dir}")
```

**预期输出：**
```
✓ 转换成功：doc1.pdf
✓ 转换成功：doc2.pdf
✓ 转换成功：doc3.pdf
✗ 转换失败：corrupted.pdf - 文件已损坏

批量转换完成，结果保存在 converted
```

**示例 2：使用批处理工具**

```python
from ai_pdf_agent import BatchConverter

batch = BatchConverter()

# 配置批处理
results = batch.convert_directory(
    input_dir='input_pdfs',
    output_dir='converted',
    format='markdown',  # 'text', 'html', 'markdown'
    recursive=True,     # 包含子目录
    overwrite=False     # 不覆盖已存在的文件
)

# 查看结果
print(f"成功：{results['success_count']}")
print(f"失败：{results['failed_count']}")
print(f"跳过：{results['skipped_count']}")

if results['failed']:
    print("\n失败的文件：")
    for item in results['failed']:
        print(f"  - {item['file']}: {item['error']}")
```

---

### 批量提取信息

**示例 1：批量提取文本信息**

```python
from ai_pdf_agent import PDFProcessor, BatchExtractor
import json

processor = PDFProcessor()
batch = BatchExtractor(processor)

# 批量提取
results = batch.extract_text_from_directory(
    'input_pdfs',
    include_metadata=True,
    output_format='dict'
)

# 保存结果
with open('extracted_data.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"提取完成，共处理 {len(results)} 个文件")
```

**示例 2：批量提取并生成报告**

```python
from ai_pdf_agent import PDFProcessor, BatchExtractor
import csv

processor = PDFProcessor()
batch = BatchExtractor(processor)

# 批量提取
results = batch.extract_text_from_directory('input_pdfs')

# 生成 CSV 报告
with open('report.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['文件名', '页数', '字符数', '提取状态'])
    
    for result in results:
        writer.writerow([
            result['filename'],
            result['page_count'],
            len(result['text']),
            '成功' if result['success'] else '失败'
        ])

print("CSV 报告已生成：report.csv")
```

**示例 3：批量提取特定信息**

```python
from ai_pdf_agent import PDFProcessor
import re

processor = PDFProcessor()

# 定义提取规则
patterns = {
    'email': r'\b[\w.-]+@[\w.-]+\.\w+\b',
    'phone': r'\b\d{3,4}-?\d{7,8}\b',
    'url': r'https?://[^\s<>"]+'
}

results = []

for filename in os.listdir('pdfs'):
    if filename.endswith('.pdf'):
        text = processor.extract_text(f'pdfs/{filename}')
        
        extracted = {'filename': filename}
        for key, pattern in patterns.items():
            matches = re.findall(pattern, text)
            extracted[key] = matches
        
        results.append(extracted)

# 输出结果
import json
print(json.dumps(results, ensure_ascii=False, indent=2))
```

---

### 并行处理

**示例 1：使用多线程并行处理**

```python
from ai_pdf_agent import ParallelProcessor
import time

processor = ParallelProcessor(workers=4)  # 4 个工作线程

# 定义处理函数
def process_pdf(file_path):
    from ai_pdf_agent import PDFProcessor
    p = PDFProcessor()
    return p.extract_text(file_path)

# 并行处理
file_list = ['doc1.pdf', 'doc2.pdf', 'doc3.pdf', 'doc4.pdf']
results = processor.map(process_pdf, file_list)

print(f"处理完成，共 {len(results)} 个文件")
```

**示例 2：使用异步处理**

```python
import asyncio
from ai_pdf_agent import AsyncPDFProcessor

async def process_files_async():
    processor = AsyncPDFProcessor()
    
    tasks = []
    for filename in ['doc1.pdf', 'doc2.pdf', 'doc3.pdf']:
        task = processor.extract_text_async(filename)
        tasks.append(task)
    
    # 等待所有任务完成
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"✗ 文件 {i+1} 处理失败：{result}")
        else:
            print(f"✓ 文件 {i+1} 处理成功，提取了 {len(result)} 个字符")

# 运行异步处理
asyncio.run(process_files_async())
```

**示例 3：带进度显示的并行处理**

```python
from ai_pdf_agent import ParallelProcessor
from tqdm import tqdm

processor = ParallelProcessor(workers=4)
file_list = [f'doc{i}.pdf' for i in range(1, 21)]  # 20 个文件

# 使用进度条
with tqdm(total=len(file_list), desc="处理 PDF") as pbar:
    def process_with_progress(file_path):
        from ai_pdf_agent import PDFProcessor
        p = PDFProcessor()
        result = p.extract_text(file_path)
        pbar.update(1)
        return result
    
    results = processor.map(process_with_progress, file_list)

print(f"处理完成：{len(results)} 个文件")
```

---

## 集成示例

### 与 Flask 集成

**示例 1：基本的 Flask API**

```python
from flask import Flask, request, jsonify, send_file
from ai_pdf_agent import PDFProcessor, PDFConverter
import tempfile
import os

app = Flask(__name__)
processor = PDFProcessor()
converter = PDFConverter()

@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """
    提取 PDF 文本
    POST /api/extract-text
    Content-Type: multipart/form-data
    file: PDF 文件
    """
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        file.save(tmp.name)
        try:
            # 提取文本
            text = processor.extract_text(tmp.name)
            return jsonify({
                'success': True,
                'filename': file.filename,
                'text': text,
                'length': len(text)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        finally:
            os.unlink(tmp.name)

@app.route('/api/convert', methods=['POST'])
def convert_pdf():
    """
    转换 PDF 格式
    POST /api/convert
    Content-Type: multipart/form-data
    file: PDF 文件
    format: 转换格式 (markdown|text|html)
    """
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    format_type = request.form.get('format', 'markdown')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
        file.save(tmp_pdf.name)
        
        try:
            # 转换格式
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{format_type}') as tmp_out:
                if format_type == 'markdown':
                    converter.to_markdown(tmp_pdf.name, output=tmp_out.name)
                elif format_type == 'text':
                    converter.to_text(tmp_pdf.name, output=tmp_out.name)
                elif format_type == 'html':
                    converter.to_html(tmp_pdf.name, output=tmp_out.name)
                
                # 返回转换后的文件
                return send_file(
                    tmp_out.name,
                    as_attachment=True,
                    download_name=f"{os.path.splitext(file.filename)[0]}.{format_type}"
                )
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**运行和测试：**
```bash
# 启动服务器
python flask_app.py

# 测试提取文本
curl -X POST -F "file=@document.pdf" http://localhost:5000/api/extract-text

# 测试格式转���
curl -X POST -F "file=@document.pdf" -F "format=markdown" http://localhost:5000/api/convert
```

---

### 与 FastAPI 集成

**示例 1：FastAPI 应用**

```python
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from ai_pdf_agent import PDFProcessor, PDFConverter
import tempfile
import os
import uuid

app = FastAPI(title="PDF 处理 API", version="1.0.0")
processor = PDFProcessor()
converter = PDFConverter()

@app.post("/api/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """
    提取 PDF 文本
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")
    
    # 保存临时文件
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.write(await file.read())
    temp_file.close()
    
    try:
        text = processor.extract_text(temp_file.name)
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "text": text,
            "length": len(text)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(temp_file.name)

@app.post("/api/convert")
async def convert_pdf(
    file: UploadFile = File(...),
    format: str = Form("markdown")
):
    """
    转换 PDF 格式
    """
    if format not in ['markdown', 'text', 'html']:
        raise HTTPException(status_code=400, detail="不支持的格式")
    
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_pdf.write(await file.read())
    temp_pdf.close()
    
    output_ext = 'md' if format == 'markdown' else format
    output_filename = f"{uuid.uuid4()}.{output_ext}"
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_ext}')
    temp_output.close()
    
    try:
        if format == 'markdown':
            converter.to_markdown(temp_pdf.name, output=temp_output.name)
        elif format == 'text':
            converter.to('text, output=temp_output.name)
        elif format == 'html':
            converter.to_html(temp_pdf.name, output=temp_output.name)
        
        return FileResponse(
            temp_output.name,
            media_type='text/plain',
            filename=f"{os.path.splitext(file.filename)[0]}.{output_ext}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**运行和测试：**
```bash
# 启动服务器
uvicorn fastapi_app:app --reload

# 测试 API
curl -X POST -F "file=@document.pdf" http://localhost:8000/api/extract-text
```

---

### 与 Django 集成

**示例 1：Django 视图**

```python
# views.py
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ai_pdf_agent import PDFProcessor, PDFConverter
import tempfile
import os

processor = PDFProcessor()
converter = PDFConverter()

@csrf_exempt
@require_http_methods(["POST"])
def extract_text_view(request):
    """
    提取 PDF 文本
    POST /api/extract-text
    """
    if 'file' not in request.FILES:
        return JsonResponse({'error': '没有上传文件'}, status=400)
    
    file = request.FILES['file']
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        for chunk in file.chunks():
            tmp.write(chunk)
        tmp.close()
        
        try:
            text = processor.extract_text(tmp.name)
            return JsonResponse({
                'success': True,
                'filename': file.name,
                'text': text,
                'length': len(text)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        finally:
            os.unlink(tmp.name)

@csrf_exempt
@require_http_methods(["POST"])
def convert_pdf_view(request):
    """
    转换 PDF 格式
    POST /api/convert
    """
    if 'file' not in request.FILES:
        return JsonResponse({'error': '没有上传文件'}, status=400)
    
    file = request.FILES['file']
    format_type = request.POST.get('format', 'markdown')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
        for chunk in file.chunks():
            tmp_pdf.write(chunk)
        tmp_pdf.close()
        
        try:
            output_ext = 'md' if format_type == 'markdown' else format_type
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_ext}') as tmp_out:
                tmp_out.close()
                
                if format_type == 'markdown':
                    converter.to_markdown(tmp_pdf.name, output=tmp_out.name)
                elif: format_type == 'text':
                    converter.to_text(tmp_pdf.name, output=tmp_out.name)
                elif format_type == 'html':
                    converter.to_html(tmp_pdf.name, output=tmp_out.name)
                
                response = FileResponse(
                    open(tmp_out.name, 'rb'),
                    as_attachment=True,
                    filename=f"{os.path.splitext(file.name)[0]}.{output_ext}"
                )
                return response
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/extract-text/', views.extract_text_view),
    path('api/convert/', views.convert_pdf_view),
]
```

---

## 最佳实践

### 性能优化建议

**1. 使用缓存**

```python
from functools import lru_cache
from ai_pdf_agent import PDFProcessor

processor = PDFProcessor()

@lru_cache(maxsize=100)
def extract_text_cached(file_path):
    """带缓存的文本提取"""
    return processor.extract_text(file_path)

# 后续调用会使用缓存
text1 = extract_text_cached('document.pdf')
text2 = extract_text_cached('document.pdf')  # 从缓存读取
```

**2. 批量处理时使用并行**

```python
from ai_pdf_agent import ParallelProcessor

# 对于大量文件，使用并行处理
processor = ParallelProcessor(workers=4)  # 根据 CPU 核心数调整

def process_file(file_path):
    from ai_pdf_agent import PDFProcessor
    p = PDFProcessor()
    return p.extract_text(file_path)

results = processor.map(process_file, large_file_list)
```

**3. 及时释放资源**

```python
from ai_pdf_agent import PDFProcessor

# 使用上下文管理器
with PDFProcessor() as processor:
    text = processor.extract_text('document.pdf')
    # 资源会自动释放
```

**4. 预处理大文件**

```python
from ai_pdf_agent import PDFProcessor

processor = PDFProcessor()

# 对于大文件，分页处理
def process_large_pdf(file_path, batch_size=10):
    metadata = processor.get_metadata(file_path)
    total_pages = metadata['page_count']
    
    all_text = []
    for start in range(1, total_pages + 1, batch_size):
        end = min(start + batch_size - 1, total_pages)
        pages = list(range(start, end + 1))
        text = processor.extract_text(file_path, pages=pages)
        all_text.append(text)
    
    return ''.join(all_text)
```

---

### 错误处理建议

**1. 记录错误日志**

```python
import logging
from ai_pdf_agent import PDFProcessor, PDFError

# 配置日志
logging.basicConfig(
    filename='pdf_processor.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

processor = PDFProcessor()

try:
    text = processor.extract_text('document.pdf')
except PDFError as e:
    logging.error(f"PDF 处理失败：{e.message}", exc_info=True)
    # 用户友好的错误消息
    print(f"处理失败：{e.message}")
```

**2. 重试机制**

```python
import time
from ai_pdf_agent import PDFProcessor

def extract_with_retry(file_path, max_retries=3, delay=1):
    """带重试机制的文本提取"""
    processor = PDFProcessor()
    
    for attempt in range(max_retries):
        try:
            return processor.extract_text(file_path)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"第 {attempt + 1} 次尝试失败，{delay} 秒后重试...")
            time.sleep(delay)
            delay *= 2  # 指数退避
    
    return None

text = extract_with_retry('document.pdf')
```

**3. 验证输入**

```python
from ai_pdf_agent import PDFProcessor

def validate_and_extract(file_path):
    """验证输入后提取"""
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")
    
    # 检查文件扩展名
    if not file_path.lower().endswith('.pdf'):
        raise ValueError("只支持 PDF 文件")
    
    # 检查文件大小
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        raise ValueError("文件为空")
    if file_size > 100 * 1024 * 1024:  # 100MB
        raise ValueError("文件过大（超过 100MB）")
    
    # 提取文本
    processor = PDFProcessor()
    return processor.extract_text(file_path)
```

---

### 安全建议

**1. 验证文件类型**

```python
import magic
from ai_pdf_agent import PDFProcessor

def is_valid_pdf(file_path):
    """验证文件是否为真正的 PDF"""
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    return file_type == 'application/pdf'

# 使用验证
if is_valid_pdf('document.pdf'):
    processor = PDFProcessor()
    text = processor.extract_text('document.pdf')
else:
    print("文件不是有效的 PDF")
```

**2. 限制文件大小**

```python
import os
from ai_pdf_agent import PDFProcessor

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def extract_with_size_limit(file_path):
    """限制文件大小的提取"""
    file_size = os.path.getsize(file_path)
    
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"文件过大（{file_size} 字节），最大支持 {MAX_FILE_SIZE} 字节")
    
    processor = PDFProcessor()
    return processor.extract_text(file_path)
```

**3. 处理敏感信息**

```python
import re
from ai_pdf_agent import PDFProcessor

def redact_sensitive_info(text):
    """脱敏敏感信息"""
    # 脱敏邮箱
    text = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '[EMAIL REDACTED]', text)
    
    # 脱敏手机号
    text = re.sub(r'\b1[3-9]\d{9}\b', '[PHONE REDACTED]', text)
    
    # 脱敏身份证号
    text = re.sub(r'\b\d{17}[\dXx]\b', '[ID REDACTED]', text)
    
    return text

processor = PDFProcessor()
raw_text = processor.extract_text('document.pdf')
safe_text = redact_sensitive_info(raw_text)
```

**4. 使用临时文件**

```python
import tempfile
import os
from ai_pdf_agent import PDFProcessor

def process_safely(file_content):
    """安全地处理文件内容"""
    processor = PDFProcessor()
    
    # 使用临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    
    try:
        text = processor.extract_text(tmp_path)
        return text
    finally:
        # 确保删除临时文件
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
```

---

## 总结

本文档涵盖了 ai-pdf-agent 的主要使用场景和最佳实践。通过这些示例，您应该能够：

1. 基本使用：读取、转换、提取 PDF 内容
2. 高级功能：页面处理、自定义插件、错误处理
3. 批量处理：目录转换、信息提取、并行处理
4. 框架集成：Flask、FastAPI、Django
5. 最佳实践：性能优化、错误处理、安全建议

如有问题或需要更多帮助，请参考 [README.md](README.md) 或 [API 文档](API.md)。
