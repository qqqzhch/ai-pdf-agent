# CLI 使用示例

> AI PDF Agent 命令行实际使用演示

---

## 🚀 快速演示

### 1. 提取文本（基础）

```bash
cd /root/.openclaw/workspace/ai-pdf-agent

# 提取文本（默认文本格式）
python3 -m cli.main text examples/sample_pdfs/sample_text.pdf -o /tmp/output.txt
```

**输出：**
```
✓ Text extracted to: /tmp/output.txt
```

**查看内容：**
```bash
cat /tmp/output.txt
```

**结果：**
```
Document Title

This is a sample document

with some text content.

Features

- Feature 1

- Feature 2

- Feature 3

Table Example

Name    Age    City

Alice   25     New York

Bob     30     Los Angeles

Charlie 35     Chicago
```

---

### 2. 提取文本（JSON 格式 - AI Agent 友好）

```bash
python3 -m cli.main text examples/sample_pdfs/sample_text.pdf --format json --structured -o /tmp/output.json
```

**输出：**
```
✓ Text extracted to: /tmp/output.json
```

**查看内容：**
```bash
cat /tmp/output.json
```

**结果：**
```json
{
  "success": true,
  "input": "examples/sample_pdfs/sample_text.pdf",
  "pages_extracted": [1, 2, 3],
  "page_count": 3,
  "content": "Document Title\n\nThis is a sample document...",
  "metadata": {
    "title": "",
    "author": "",
    "page_count": 3,
    "is_encrypted": false,
    "pdf_version": "PDF 1.7"
  }
}
```

---

### 3. PDF → Markdown 转换

```bash
python3 -m cli.main to-markdown examples/sample_pdfs/sample_text.pdf -o /tmp/output.md
```

**输出：**
```
Consider using pymupdf_layout package for a greatly improved page layout analysis.
✓ Converted: examples/sample_pdfs/sample_text.pdf -> /tmp/output.md
  Pages: 3
```

**查看内容：**
```bash
cat /tmp/output.md
```

**结果：**
```markdown
## Page 1

# Document Title
This is a sample document
with some text content.

---

## Page 2

## Features
- Feature 1
- Feature 2
- Feature 3

---

## Page 3

### Table Example
Name    Age    City
Alice   25     New York
Bob     30     Los Angeles
Charlie 35     Chicago
```

---

### 4. PDF → JSON 转换

```bash
python3 -m cli.main to-json examples/sample_pdfs/sample_text.pdf -o /tmp/doc.json
```

**输出：**
```
Consider using pymupdf_layout package for a greatly improved page layout analysis.
✓ Converted: examples/sample_pdfs/sample_text.pdf -> /tmp/doc.json
  Pages: 3
  Text pages: 3
  Tables: 0
```

**查看内容：**
```bash
head -30 /tmp/doc.json
```

**结果：**
```json
{
  "document": {
    "filename": "sample_text.pdf",
    "path": "examples/sample_pdfs/sample_text.pdf",
    "page_count": 3,
    "pages_processed": [1, 2, 3]
  },
  "metadata": {
    "title": "",
    "author": "",
    "page_count": 3,
    "is_encrypted": false,
    "pdf_version": "PDF 1.7"
  },
  "structure": {
    "pages": [
      {
        "page_number": 1,
        ...
      }
    ]
  }
}
```

---

### 5. 提取图片

```bash
python3 -m cli.main images examples/sample_pdfs/sample_image.pdf --extract-dir /tmp/images
```

**输出：**
```json
{
  "success": true,
  "input": "examples/sample_pdfs/sample_image.pdf",
  "pages_extracted": [1],
  "page_count": 1,
  "count": 0,
  "images": [],
  "extract_dir": "/tmp/images"
}
```

---

## 📋 完整命令列表

### 读取命令

```bash
# 1. 提取文本（文本格式）
python3 -m cli.main text sample.pdf -o output.txt

# 2. 提取文本（JSON 格式）
python3 -m cli.main text sample.pdf --format json --structured -o output.json

# 3. 提取指定页面
python3 -m cli.main text sample.pdf --pages 1-5 -o output.txt

# 4. 提取元数据
python3 -m cli.main metadata sample.pdf -o metadata.json

# 5. 提取结构
python3 -m cli.main structure sample.pdf -o structure.json

# 6. 提取表格
python3 -m cli.main tables sample.pdf -o tables.json

# 7. 提取图片
python3 -m cli.main images sample.pdf --extract-dir ./images
```

### 转换命令

```bash
# 1. PDF → Markdown
python3 -m cli.main to-markdown sample.pdf -o output.md

# 2. PDF → HTML
python3 -m cli.main to-html sample.pdf -o output.html

# 3. PDF → JSON
python3 -m cli.main to-json sample.pdf -o output.json

# 4. PDF → CSV
python3 -m cli.main to-csv sample.pdf -o output.csv

# 5. PDF → EPUB
python3 -m cli.main to-epub sample.pdf -o output.epub

# 6. PDF → 图片
python3 -m cli.main to-image sample.pdf --output-dir ./images
```

---

## 🎯 推荐工作流

### 方案 1：基本使用（文本输出）

```bash
# 提取文本
python3 -m cli.main text document.pdf -o output.txt

# 转换为 Markdown
python3 -m cli.main to-markdown document.pdf -o output.md

# 提取表格
python3 -m cli.main tables report.pdf -o tables.json
```

### 方案 2：AI Agent 使用（JSON 输出）

```bash
# 提取文本（JSON）
python3 -m cli.main text document.pdf --format json --structured -o output.json

# 转换为 JSON
python3 -m cli.main to-json document.pdf -o full.json

# 提取元数据（JSON）
python3 -m cli.main metadata document.json
```

### 方案 3：批量处理

```bash
# 处理目录中所有 PDF
for file in documents/*.pdf; do
    python3 -m cli.main text "$file" -o "output/$(basename "$file" .pdf).txt"
done
```

---

## 💡 实用技巧

### 1. 查看帮助信息

```bash
# 查看主帮助
python3 -m cli.main --help

# 查看特定命令帮助
python3 -m cli.main text --help
python3 -m cli.main to-markdown --help
```

### 2. 指定页面范围

```bash
# 提取第 1 页
python3 -m cli.main text document.pdf --pages 1 -o page1.txt

# 提取第 1-5 页
python3 -m cli.main text document.pdf --pages 1-5 -o pages1-5.txt

# 提取第 1、3、5 页
python3 -m cli.main text document.pdf --pages 1,3,5 -o specific.txt
```

### 3. 使用管道组合

```bash
# 提取文本并搜索关键词
python3 -m cli.main text document.pdf | grep "关键词"

# 提取文本并统计行数
python3 -m cli.main text document.pdf | wc -l
```

---

## 📊 测试文件

**使用示例文件：**
```bash
cd /root/.openclaw/workspace/ai-pdf-agent
ls -la examples/sample_pdfs/
```

**可用文件：**
- `sample_text.pdf` - 纯文本文档
- `sample_table.pdf` - 包含表格的文档
- `sample_image.pdf` - 包含图片的文档
- `sample_mixed.pdf` - 混合内容
- `sample_multipage.pdf` - 多页文档（4 页）
- `sample_password.pdf` - 密码保护（密码：secret123）
- `sample_annotated.pdf` - 带注释的文档

---

**演示时间：** 2026-03-04 17:10
**CLI 模式：** python3 -m cli.main
**状态：** ✅ 所有命令工作正常
