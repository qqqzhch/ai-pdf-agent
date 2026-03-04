# 示例 PDF 文件

本目录包含 7 个示例 PDF 文件，用于测试和演示 AI PDF Agent 的各种功能。

## 文件列表

### 1. sample_text.pdf
**类型：** 纯文本 PDF
**大小：** 3.0 KB
**用途：** 测试文本提取功能

### 2. sample_table.pdf
**类型：** 表格 PDF
**大小：** 3.7 KB
**用途：** 测试表格提取功能

### 3. sample_image.pdf
**类型：** 图片 PDF
**大小：** 1.3 KB
**用途：** 测试图片提取功能

### 4. sample_mixed.pdf
**类型：** 混合内容（文本 + 表格）
**大小：** 1.6 KB
**用途：** 测试混合内容提取

### 5. sample_multipage.pdf
**类型：** 多页 PDF（4 页）
**大小：** 2.4 KB
**用途：** 测试多页文档处理

### 6. sample_password.pdf
**类型：** 密码保护 PDF
**大小：** 947 B
**密码：** secret123
**用途：** 测试密码保护文档处理

### 7. sample_annotated.pdf
**类型：** 带注释 PDF
**大小：** 1.5 KB
**用途：** 测试注释提取功能

## 使用示例

### 文本提取
```bash
python3 -m ai_pdf_agent.main examples/sample_pdfs/sample_text.pdf --extract text
```

### 表格提取
```bash
python3 -m ai_pdf_agent.main examples/sample_pdfs/sample_table.pdf --extract tables
```

### 图片提取
```bash
python3 -m ai_pdf_agent.main examples/sample_pdfs/sample_image.pdf --extract images
```

### 批量处理
```bash
python3 -m ai_pdf_agent.main examples/sample_pdfs/ --batch --output output/
```

## 文件来源

这些文件是从之前的性能测试中使用的真实 PDF 文件复制而来，并通过 PyMuPDF 生成额外示例。

**原始来源：**
- `/tmp/test_sample.pdf` → `sample_text.pdf`
- `/tmp/test_table.pdf` → `sample_table.pdf`
- `/tmp/test_images.pdf` → `sample_image.pdf`

**新生成：**
- `sample_mixed.pdf` - 使用 Python + fitz 生成
- `sample_multipage.pdf` - 使用 Python + fitz 生成
- `sample_password.pdf` - 使用 Python + fitz 生成
- `sample_annotated.pdf` - 使用 Python + fitz 生成

## 验证

所有文件都已通过 PyMuPDF 验证，可以正常打开和读取。

```python
import fitz

for pdf in [
    'sample_text.pdf',
    'sample_table.pdf',
    'sample_image.pdf',
    'sample_mixed.pdf',
    'sample_multipage.pdf',
    'sample_password.pdf',
    'sample_annotated.pdf',
]:
    doc = fitz.open(pdf)
    print(f'{pdf}: {doc.page_count} pages')
    doc.close()
```

---

**生成日期：** 2026-03-04
**版本：** P1.4 完成
**状态：** ✅ 所有文件可用
