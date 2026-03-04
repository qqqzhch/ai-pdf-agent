# AI PDF Agent - 完整使用指南

> AI Agent 叟友的 PDF 处理工具 - 安装、使用和命令参考

---

## 📦 安装指南

### 前置要求

- Python 3.8+
- pip (Python 包管理器)

### 快速安装

#### 方式 1：开发模式（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 验证安装
python -m cli.main --help
```

#### 方式 2：全局安装

```bash
# 1. 克隆项目
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent

# 2. 安装到系统
pip install -e .

# 3. 验证安装
ai-pdf --help
```

---

## 🚀 快速开始

### 验证安装

```bash
python -m cli.main --help
```

**预期输出：**
```
Usage: cli.main [OPTIONS] COMMAND [ARGS]...

  AI Agent 友好的 PDF 处理工具

Options:
  -v, --version  显示版本号
  --help         显示帮助信息

Commands:
  text          提取 PDF 文本
  tables        提取 PDF 表格
  images        提取 PDF 图片
  metadata      提取 PDF 元数据
  structure     提取 PDF 结构
  to-markdown   转换为 Markdown
  to-html       转换为 HTML
  to-json       转换为 JSON
  to-csv        转换为 CSV
  to-image      转换为图片
  to-epub       转换为 EPUB
  plugin        插件管理
```

---

## 📖 使用示例

### 1. 提取文本

**基本用法：**
```bash
python -m cli.main text sample.pdf -o output.txt.txt
```

**指定页面：**
```bash
# 提取第 1 页
python -m cli.main text sample.pdf --page 1 -o page1.txt

# 提取第 1-5 页
python -m cli.main text sample.pdf --pages 1-5 -o pages1-5.txt

# 提取第 1、3、5 页
python -m cli.main text sample.pdf --pages 1,3,5 -o specific.txt
```

**JSON 输出（AI Agent 友好）：**
```bash
python -m cli.main text sample.pdf --json -o output.json
```

**输出示例：**
```json
{
  "success": true,
  "file": "sample.pdf",
  "pages": 5,
  "text": "这是 PDF 文档的文本内容...",
  "metadata": {
    "title": "示例文档",
    "author": "AI PDF Agent",
    "pages": 5
  }
}
```

---

### 2. 提取表格

**提取所有表格：**
```bash
python -m cli.main tables report.pdf -o tables.json
```

**输出示例：**
```json
{
  "success": true,
  "file": "report.pdf",
  "tables": [
    {
      "page": 1,
      "rows": [
        ["姓名", "年龄", "城市"],
        ["张三", "25", "北京"],
        ["李四", "30", "上海"]
      ]
    }
  ]
}
```

**导出为 CSV：**
```bash
python -m cli.main tables report.pdf --csv -o tables.csv
```

---

### 3. 提取图片

**提取所有图片：**
```bash
python -m cli.main images document.pdf --extract-dir ./images
```

**输出：**
```
images/page1_img1.png
images/page1_img2.png
images/page2_img1.png
```

**指定格式：**
```bash
# 提取为 JPEG
python -m cli.main images document.pdf --format jpeg --extract-dir ./images

# 提取为 PNG
python -m cli.main images document.pdf --format png --extract-dir ./images
```

---

### 4. 格式转换

#### PDF → Markdown

```bash
python -m cli.main to-markdown document.pdf -o document.md
```

#### PDF → HTML

```bash
python -m cli.main to-html document.pdf -o document.html
```

#### PDF → JSON

```bash
python -m cli.main to-json document.pdf -o document.json
```

#### PDF → CSV（表格）

```bash
python -m cli.main to-csv report.pdf -o tables.csv
```

#### PDF → EPUB（电子书）

```bash
python -m cli.main to-epub book.pdf -o book.epub
```

#### PDF → 图片（页面转图片）

```bash
# 将所有页面转为图片
python -m cli.main to-image document.pdf --output-dir ./images

# 指定分辨率
python -m cli.main to-image document.pdf --dpi 300 --output-dir ./images

# 指定格式
python -m cli.main to-image document.pdf --format png --output-dir ./images
```

---

### 5. 提取元数据

```bash
python -m cli.main metadata document.json
```

**输出示例：**
```json
{
  "success": true,
  "file": "document.pdf",
  "metadata": {
    "title": "文档标题",
    "author": "作者",
    "subject": "主题",
    "keywords": "关键词",
    "creator": "创建工具",
    "producer": "PDF 生成器",
    "created": "2026-03-03T10:00:00Z",
    "modified": "2026-03-04T15:00:00Z",
    "pages": 10,
    "size": "1.2 MB"
  }
}
```

---

### 6. 提取结构（目录、书签）

```bash
python -m cli.main structure document.json
```

**输出示例：**
```json
{
  "success": true,
  "file": "document.pdf",
  "structure": {
    "toc": [
      {
        "level": 1,
        "title": "第一章",
        "page": 1
      },
      {
        "level": 2,
        "title": "1.1 节标题",
        "page": 2
      }
    ],
    "bookmarks": [
      {
        "title": "重要标记",
        "page": 5
      }
    ]
  }
}
```

---

### 7. OCR 文字识别

```bash
# 使用 Tesseract OCR
python -m cli.main ocr scanned.pdf --engine tesseract -o output.txt

# 使用 PaddleOCR
python -m cli.main ocr scanned.pdf --engine paddleocr -o output.txt

# 混合模式（自动选择）
python -m cli.main ocr scanned.pdf --engine auto -o output.txt
```

---

## 🔧 高级功能

### 批量处理

```bash
# 处理目录中的所有 PDF
python -m cli.main batch ./documents --output-dir ./output --format markdown

# 指定输出格式
python -m cli.main batch ./documents --output-dir ./output --format json

# 只处理匹配的文件
python -m cli.main batch ./documents --pattern "report_*.pdf" --output-dir ./output
```

---

## 📚 命令参考

### 读取命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `text` | 提取文本 | `python -m cli.main text file.pdf -o output.txt` |
| `tables` | 提取表格 | `python -m cli.main tables file.pdf -o tables.json` |
| `images` | 提取图片 | `python -m cli.main images file.pdf --extract-dir ./images` |
| `metadata` | 提取元数据 | `python -m cli.main metadata file.json` |
| `structure` | 提取结构 | `python -m cli.main structure file.json` |
| `ocr` | OCR 识别 | `python -m cli.main ocr file.pdf -o output.txt` |

### 转换命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `to-markdown` | PDF → Markdown | `python -m cli.main to-markdown file.pdf -o output.md` |
| `to-html` | PDF → HTML | `python -m cli.main to-html file.pdf -o output.html` |
| `to-json` | PDF → JSON | `python -m cli.main to-json file.pdf -o output.json` |
| `to-csv` | PDF → CSV | `python -m cli.main to-csv file.pdf -o output.csv` |
| `to-epub` | PDF → EPUB | `python -m cli.main to-epub file.pdf -o output.epub` |
| `to-image` | PDF → 图片 | `python -m cli.main to-image file.pdf --output-dir ./images` |

---

## 🎯 功能模块

### ✅ 已实现功能

#### 核心模块
- ✅ 插件系统（发现、加载、管理）
- ✅ PDF 引擎（PyMuPDF）
- ✅ 性能监控（基准测试、内存分析）

#### 读取器插件（6 个）
- ✅ 文本读取器
- ✅ 表格读取器
- ✅ 图片读取器
- ✅ 元数据读取器
- ✅ 结构读取器
- ✅ OCR 文字识别器

#### 转换器插件（6 个）
- ✅ Markdown 转换器
- ✅ HTML 转换器
- ✅ JSON 转换器
- ✅ CSV 转换器
- ✅ Image 转换器
- ✅ EPUB 转换器

#### CLI 命令（12 个）
- ✅ 读取命令（5 个）
- ✅ 转换命令（6 个）
- ✅ 管理命令（1 个）

#### P1 优先级任务（100% 完成）
- ✅ P1.1 OCR 文本提取插件
- ✅ P1.2 Word 转换器插件
- ✅ P1.3 批量处理命令
- ✅ P1.4 示例 PDF 文件

---

## 📁 示例文件

**路径：** `examples/sample_pdfs/`

| 文件 | 类型 | 说明 |
|------|------|------|
| `sample_text.pdf` | 纯文本 | 基础文本提取测试 |
| `sample_table.pdf` | 表格 | 表格提取测试 |
| `sample_image.pdf` | 图片 | 图片提取测试 |
| `sample_mixed.pdf` | 混合 | 文本 + 表格混合内容 |
| `sample_multipage.pdf` | 多页 | 4 页文档测试 |
| `sample_password.pdf` | 密码保护 | 密码：secret123 |
| `sample_annotated.pdf` | 注释 | 带高亮注释的文档 |

---

## 🔍 测试覆盖

**总测试数：** 1101 个
**通过率：** 100%

运行测试：
```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_plugins/
pytest tests/test_cli/

# 查看测试覆盖率
pytest tests/ --cov=ai_pdf_agent --cov-report=html
```

---

## 📊 项目统计

- **核心模块：** 3 个
- **读取器插件：** 6 个
- **转换器插件：** 6 个
- **CLI 命令：** 12 个
- **示例文件：** 7 个
- **测试用例：** 1101 个
- **文档文件：** 5 个

---

## 🤝 贡献指南

欢迎贡献代码！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License

---

## 📞 联系方式

- **GitHub：** https://github.com/qqqzhch/ai-pdf-agent
- **文档：** https://docs.ai-pdf-agent.com
- **问题反馈：** https://github.com/qqqzhch/ai-pdf-agent/issues

---

**生成时间：** 2026-03-04 16:55
**项目版本：** v1.0
**状态：** 🟢 稳定
