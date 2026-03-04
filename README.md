# AI PDF Agent

> **AI Agent 友好的 PDF 处理工具** - 基于插件系统的 CLI 工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 📖 项目介绍

**AI PDF Agent** 是一个专为 AI Agent 设计的 PDF 处理工具，通过插件化架构提供灵活的 PDF 处理能力。

### 为什么设计这个工具？

在 AI Agent 应用中，我们需要一个简单、可靠、程序化友好的 PDF 处理工具，能够：

- **轻松集成** - CLI + JSON 输出，适合 AI Agent 调用
- **灵活扩展** - 插件系统支持自定义功能
- **本地处理** - 保护隐私，无文件大小限制
- **开发者友好** - Markdown、JSON 等开发者熟悉格式

### 核心设计理念

1. **AI Agent 优先** - 所有操作都有 JSON 输出选项，便于程序解析
2. **本地处理优先** - 尽可能在本地完成处理，不依赖云服务
3. **插件化架构** - 核心功能通过插件实现，易于扩展
4. **开发者友好** - 清晰的 API、详细的文档、丰富的示例

---

## ✨ 特性说明

### 🔌 插件系统

采用灵活的插件架构，所有功能模块都通过插件实现：

- **Reader 插件** - 提取 PDF 内容（文本、表格、图片等）
- **Converter 插件** - 格式转换（Markdown、HTML、JSON、EPUB 等）
- **OCR 插件** - 文字识别（Tesseract、PaddleOCR 等）
- **RAG 插件** - 检索增强生成（向量索引、语义检索）
- **Encrypt 插件** - 密码保护（PDF 加密、解密）
- **Compress 插件** - 文件压缩（PDF 压缩、图片优化）
- **Edit 插件** - 文档编辑（添加文本、删除页面、旋转等）
- **Analyze 插件** - 文档分析（质量评估、内容分析）

### 📄 多格式支持

- **输入格式**: PDF
- **输出格式**: Text, Markdown, HTML, JSON, CSV, Image, EPUB

### 🖥️ CLI 友好

- **简洁命令** - 直观的命令行接口
- **JSON 输出** - 所有命令支持 JSON 格式输出
- **批处理支持** - 支持批量处理多个文件
- **进度显示** - 长时间操作显示进度条

### 🛡️ 隐私保护

- **本地处理** - 文件在本地处理，不上传到云端
- **无大小限制** - 无文件大小限制（仅受本地内存限制）
- **无数据收集** - 不收集任何用户数据

---

## 🚀 快速开始

### 安装

#### 方式 1: 从源码安装

```bash
# 克隆项目
git clone https://github.com/ai-agent/ai-pdf-agent.git
cd ai-pdf-agent

# 安装依赖
pip install -r requirements.txt

# 安装工具
pip install -e .
```

#### 方式 2: 直接使用（开发模式）

```bash
# 克隆项目
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent

# 安装依赖
pip install -r requirements.txt

# 安装工具
pip install -e .

# 验证安装
ai-pdf --version
```

### 验证安装

```bash
# 查看版本号
ai-pdf --version

# 查看 CLI 帮助
ai-pdf --help

# 列出所有插件
ai-pdf plugin list

# 检查插件状态
ai-pdf plugin check text_reader
```

### 基本使用

```bash
# 1. 提取 PDF 文本
ai-pdf text document.pdf -o output.txt

# 2. 提取文本并输出 JSON（AI Agent 友好）
ai-pdf text document.pdf --format json --structured -o output.json

# 3. 转换为 Markdown
ai-pdf to-markdown document.pdf -o output.md

# 4. 提取表格
ai-pdf tables document.pdf -o tables.json

# 5. 提取图片
ai-pdf images document.pdf --extract-dir ./images

# 6. 转换为图片
ai-pdf to-image document.pdf -o output.png
```

---

## 📚 命令参考

### 全局选项

| 选项 | 说明 |
|------|------|
| `-v, --version` | 显示版本号 |
| `--help` | 显示帮助信息 |

### 插件管理命令

```bash
# 列出所有插件
ai-pdf plugin list

# 查看插件详情
ai-pdf plugin info <plugin-name>

# 检查插件依赖
ai-pdf plugin check <plugin-name>
```

### PDF 阅读命令

#### 文本读取

```bash
ai-pdf text <pdf_path> [OPTIONS]
```

**选项:**
- `-o, --output <path>` - 输出文件路径
- `--json` - 以 JSON 格式输出
- `--page <num>` - 提取指定页（1-based）
- `--page-range <start-end>` - 提取页面范围（如 1-5）
- `--pages <nums>` - 提取多个页（如 1,3,5）

**示例:**
```bash
# 提取所有文本
ai-pdf text document.pdf -o output.txt

# 提取第 1 页
ai-pdf text document.pdf --page 1 -o page1.txt

# 提取 1-5 页
ai-pdf text document.pdf --page-range 1-5 -o pages1-5.txt

# JSON 输出
ai-pdf text document.pdf --json -o output.json
```

#### 表格读取

```bash
ai-pdf tables <pdf_path> [OPTIONS]
```

**选项:**
- `-o, --output <path>` - 输出文件路径（JSON）
- `--json` - 以 JSON 格式输出

**示例:**
```bash
ai-pdf tables document.pdf -o tables.json
```

#### 图片读取

```bash
ai-pdf images <pdf_path> [OPTIONS]
```

**选项:**
- `--extract-dir <path>` - 图片保存目录
- `--format <format>` - 保存格式（png, jpeg, ppm, pbm, pam）
- `--dpi <dpi>` - DPI 设置
- `--page <num>` - 提取指定页的图片
- `--page-range <start-end>` - 提取页面范围的图片

**示例:**
```bash
# 提取所有图片
ai-pdf images document.pdf --extract-dir ./images

# 提取第 1 页的图片
ai-pdf images document.pdf --page 1 --extract-dir ./images

# 指定格式和 DPI
ai-pdf images document.pdf --format jpeg --dpi 300 --extract-dir ./images
```

#### 元数据读取

```bash
ai-pdf metadata <pdf_path> [OPTIONS]
```

**示例:**
```bash
ai-pdf metadata document.pdf
```

#### 结构读取

```bash
ai-pdf structure <pdf_path> [OPTIONS]
```

**示例:**
```bash
ai-pdf structure document.pdfkt> output.json
```

### PDF 转换命令

#### Markdown 转换

```bash
ai-pdf to-markdown <pdf_path> [OPTIONS]
```

**选项:**
- `-o, --output <path>` - 输出 Markdown 文件路径
- `--preserve-tables/--no-preserve-tables` - 保留表格（默认: True）
- `--preserve-images/--no-preserve-images` - 保留图片（默认: True）
- `--image-prefix <prefix>` - 图片文件名前缀（默认: "image_"）
- `--page <num>` - 转换指定页（1-based）
- `--page-range <start end>` - 转换页面范围（如 1 5）
- `--json` - 以 JSON 格式输出

**示例:**
```bash
# 转换为 Markdown
ai-pdf to-markdown document.pdf -o output.md

# 转换指定页
ai-pdf to-markdown document.pdf --page 1 -o page1.md

# 转换页面范围
ai-pdf to-markdown document.pdf --page-range 1 5 -o pages1-5.md

# 不保留表格和图片
ai-pdf to-markdown document.pdf --no-preserve-tables --no-preserve-images -o text-only.md

# 自定义图片前缀
ai-pdf to-markdown document.pdf --image-prefix img_ -o output.md

# JSON 输出
ai-pdf to-markdown document.pdf -o output.md --json
```

#### HTML 转换

```bash
ai-pdf to-html <pdf_path> [OPTIONS]
```

**选项:**
- `-o, --output <path>` - 输出文件路径
- `-p, --page <num>` - 转换指定页（1-based）
- `--page-range <start-end>` - 转换页面范围（如 1,5）
- `--pages <nums>` - 转换多个页（如 1,3,5）
- `--embed-images` - 将图片嵌入 HTML 为 base64
- `--responsive` - 使用响应式设计
- `--json` - 以 JSON 格式输出

**示例:**
```bash
# 转换为 HTML
ai-pdf to-html document.pdf -o output.html

# 转换指定页
ai-pdf to-html document.pdf --page 1 -o page1.html

# 转换页面范围
ai-pdf to-html document.pdf --page-range 1,5 -o pages1-5.html

# 转换指定页列表
ai-pdf to-html document.pdf --pages 1,3,5 -o selected.html

# 嵌入图片
ai-pdf to-html document.pdf --embed-images -o output.html

# 响应式设计
ai-pdf to-html document.pdf --responsive -o output.html

# JSON 输出
ai-pdf to-html document.pdf --json -o output.json
```

#### JSON 转换

```bash
ai-pdf to-json <pdf_path> [OPTIONS]
```

**示例:**
```bash
ai-pdf to-json document.pdf -o output.json
```

#### CSV 转换

```bash
ai-pdf to-csv <pdf_path> [OPTIONS]
```

**示例:**
```bash
ai-pdf to-csv document.pdf -o output.csv
```

#### 图片转换

```bash
ai-pdf to-image <pdf_path> [OPTIONS]
```

**选项:**
- `-o, --output <path>` - 输出文件路径（目录或文件模板）
- `--format <format>` - 图片格式（png, jpeg, pnm, pgm, ppm, pbm, pam, tga, tpic, psd, ps）
- `--dpi <dpi>` - DPI 设置（默认 150）
- `--quality <quality>` - 图片质量（1-100，默认 85）
- `--grayscale` - 转换为灰度图
- `--embed` - 嵌入为 base64 数据
- `--page <num>` - 转换指定页（1-based）
- `--page-range <start end>` - 转换页面范围（如 1 5）
- `--pages <nums>` - 转换多个页（如 1,3,5）
- `--json` - 以 JSON 格式输出

**示例:**
```bash
# 转换为 PNG（所有页面）
ai-pdf to-image document.pdf -o output.png

# 转换为 JPEG，设置 DPI
ai-pdf to-image document.pdf --format jpeg --dpi 300 -o output.jpg

# 转换指定页
ai-pdf to-image document.pdf --page 1 -o page1.png

# 转换页面范围
ai-pdf to-image document.pdf --page-range 1 5 -o pages.png

# 转换指定页列表
ai-pdf to-image document.pdf --pages 1,3,5 -o selected.png

# 保存到目录
ai-pdf to-image document.pdf -o ./images/

# 使用文件名模板
ai-pdf to-image document.pdf -o ./output/doc_page_{page}.png

# 高 DPI 转换
ai-pdf to-image document.pdf --dpi 600 -o high_res.png

# 灰度转换
ai-pdf to-image document.pdf --grayscale -o gray.png

# 嵌入 base64（JSON 输出）
ai-pdf to-image document.pdf --embed --json -o result.json
```

#### EPUB 转换

```bash
ai-pdf to-epub <pdf_path> [OPTIONS]
```

**示例:**
```bash
ai-pdf to-epub document.pdf -o output.epub
```

---

## 💻 示例代码

### Python API 调用

#### 1. 文本读取

```python
from plugins.readers.text_reader import TextReaderPlugin

# 创建插件实例
plugin = TextReaderPlugin()

# 检查插件是否可用
if plugin.is_available():
    # 读取所有文本
    result = plugin.read("document.pdf")
    print(result['content'])

    # 读取指定页
    result = plugin.read("document.pdf", page=1)
    print(result['content'])

    # 读取页面范围
    result = plugin.read("document.pdf", page_range=(1, 5))
    print(result['content'])
else:
    print("Plugin not available")
```

#### 2. 表格读取

```python
from plugins.readers.table_reader import TableReaderPlugin

plugin = TableReaderPlugin()

if plugin.is_available():
    result = plugin.read("document.pdf")
    
    for table in result['tables']:
        print(f"页码: {table['page_number']}")
        print(f"表格: {table['data']}")
```

#### 3. 图片读取

```python
from plugins.readers.image_reader import ImageReaderPlugin

plugin = ImageReaderPlugin()

if plugin.is_available():
    # 提取所有图片
    result = plugin.read("document.pdf", extract_dir="./images")
    print(f"提取了 {result['count']} 张图片")
    
    # 提取指定页的图片
    result = plugin.read("document.pdf", page=1, extract_dir="./images")
    
    for image in result['images']:
        print(f"页码: {image['page_number']}")
        print(f"格式: {image['format']}")
        print(f"保存路径: {image['saved_path']}")
```

#### 4. JSON 转换

```python
from plugins.converters.to_json import ToJsonPlugin

plugin = ToJsonPlugin()

if plugin.is_available():
    # 转换为 JSON（包含所有内容）
    result = plugin.convert("document.pdf")
    print(f"Success: {result['success']}")
    print(f"Pages: {result['pages']}")

    # 转换并保存到文件
    result = plugin.convert("document.pdf", output_path="output.json")

    # 只转换指定页
    result = plugin.convert("document.pdf", page=1)
    import json
    data = json.loads(result['content'])

    # 转换页面范围
    result = plugin.convert("document.pdf", page_range=(1, 5))

    # 只包含文本（不包含表格、元数据等）
    result = plugin.convert(
        "document.pdf",
        include_text=True,
        include_tables=False,
        include_metadata=False,
        include_structure=False
    )

    # 使用自定义 schema 过滤字段
    schema = {
        "include_fields": ["document", "text"]
    }
    result = plugin.convert("document.pdf", schema=schema)

    # 紧凑格式（无缩进）
    result = plugin.convert("document.pdf", pretty=False)
```

#### 5. HTML 转换

```python
from plugins.converters.to_html import ToHtmlPlugin

plugin = = ToHtmlPlugin()

if plugin.is_available():
    # 转换为 HTML
    result = plugin.convert("document.pdf", output_path="output.html")
    print(f"Success: {result['success']}")
    print(f"Pages: {result['pages']}")

    # 转换指定页
    result = plugin.convert("document.pdf", page=1)
    html_content = result['content']

    # 转换页面范围
    result = plugin.convert("document.pdf", page_range=(1, 5))

    # 嵌入图片
    result = plugin.convert("document.pdf", embed_images=True)

    # 响应式设计
    result = plugin.convert("document.pdf", responsive=True)

    # 使用辅助方法
    text_html = plugin.convert_text_to_html("Hello\nWorld")
    table_html = plugin.convert_table_to_html([["A", "B"], ["1", "2"]])
    list_html = plugin.convert_list_to_html(["Item 1", "Item 2"], ordered=True)
```

#### 6. Image 转换

```python
from plugins.converters.to_image import ToImagePlugin

plugin = ToImagePlugin()

if plugin.is_available():
    # 转换所有页面为 PNG
    result = plugin.convert("document.pdf")
    print(f"Success: {result['success']}")
    print(f"Pages converted: {result['pages_converted']}")
    print(f"Format: {result['format']}")

    # 访问图片信息
    for img in result['images']:
        print(f"  Page {img['page']}: {img['filename']} ({img['width']}x{img['height']})")

    # 转换指定页
    result = plugin.convert("document.pdf", page=1)
    print(f"Image: {result['images'][0]['filename']}")

    # 转换页面范围
    result = plugin.convert("document.pdf", page_range=(1, 3))

    # 转换指定页列表
    result = plugin.convert("document.pdf", pages=[1, 3, 5])

    # 设置 DPI（默认 150）
    result = plugin.convert("document.pdf", dpi=300)

    # 设置图片质量（1-100）
    result = plugin.convert("document.pdf", quality=95)

    # 转换为灰度图
    result = plugin.convert("document.pdf", grayscale=True)

    # 嵌入 base64 数据
    result = plugin.convert("document.pdf", embed=True, page=1)
    img_data = result['images'][0]['data']  # data:image/png;base64,...

    # 保存到目录
    result = plugin.convert("document.pdf", output_path="./images")

    # 使用文件名模板
    result = plugin.convert(
        "document.pdf",
        output_path="./output/doc_page_{page}.png"
    )

    # 转换为 JPEG 格式
    result = plugin.convert("document.pdf", format="jpeg")
```

#### 7. EPUB 转换

```python
from plugins.converters.to_epub import ToEpubPlugin

plugin = ToEpubPlugin()

if plugin.is_available():
    # 转换 PDF 为 EPUB
    result = plugin.convert("document.pdf", output_path="output.epub")
    print(f"Success: {result['success']}")
    print(f"Pages: {result['pages']}")
    print(f"Chapters: {result['chapters']}")
    print(f"Images: {result['images']}")

    # 自定义标题和作者
    result = plugin.convert(
        "document.pdf",
        output_path="book.epub",
        title="My Book Title",
        author="Author Name"
    )

    # 设置章节分组（每 5 页一章）
    result = plugin.convert(
        "document.pdf",
        output_path="chapters.epub",
        chapter_pages=5
    )

    # 不包含图片
    result = plugin.convert(
        "document.pdf",
        output_path="text_only.epub",
        include_images=False
    )

    # 转换指定页面范围
    result = plugin.convert(
        "document.pdf",
        output_path="partial.epub",
        page_range=(1, 10)
    )

    # 转换指定页面列表
    result = plugin.convert(
        "document.pdf",
        output_path="selected.epub",
        pages=[1, 3, 5, 7]
    )
```

#### 8. 使用 CLI 子进程调用

```python
import subprocess
import json

# 提取文本（JSON 输出）
result = subprocess.run(
    ["ai-pdf", "text", "document.pdf", "--json"],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)
print(data['content'])

# 转换为 Markdown
subprocess.run(
    ["ai-pdf", "to-markdown", "document.pdf", "-o", "output.md"],
    check=True
)
```

### Shell 脚本示例

#### 批量处理文档

```bash
#!/bin/bash

# 批量转换为 Markdown
for file in documents/*.pdf; do
    output="output/$(basename "$file" .pdf).md"
    ai-pdf to-markdown "$file" -o "$output"
    echo "Converted: $file -> $output"
done
```

#### 提取所有文本

```bash
#!/bin/bash

# 提取所有 PDF 文本的文本
find . -name "*.pdf" -exec ai-pdf text {} -o {}.txt \;
```

#### 提取所有图片

```bash
#!/bin/bash

# 为每个 PDF 创建图片目录并提取图片
for file in documents/*.pdf; do
    dir="images/$(basename "$file" .pdf)"
    mkdir -p "$dir"
    ai-pdf images "$file" --extract-dir "$dir"
    echo "Extracted images: $file -> $dir"
done
```

---

## 🏗️ 架构说明

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                        CLI 层                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  text    │  │ tables   │  │  images  │  ...       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
│       │             │              │                   │
│       └──────────────┴──────────────┘                   │
│                      │                                 │
└──────────────────────┼─────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────┐
│                     插件系统层                          │
│  ┌──────────────────────────────────────────────┐      │
│  │            Plugin Manager                    │      │
│  │  - 插件注册/发现                              │      │
│  │  - 依赖检查                                  │           │
│  │  - 生命周期管理                              │      │
│  └──────────────────────────────────────────────┘      │
│                       │                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  Reader      │  │  Converter   │  │  OCR        │ │
│  │  插件池      │  │  插件池      │  │  插件池     │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
└─────────┼──────────────────┼──────────────────┼────────┘
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼────────┐
│                      核心引擎层                         │
│  ┌──────────────────────────────────────────────┐    │
│  │          PyMuPDF Engine                       │    │
│  │  - PDF 打开/关闭                              │    │
│  │  - 页面操作                                  │    │
│  │  - 文本/图片提取                             │    │
│  │  - 元数据获取                                │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

### 目录结构

```
ai-pdf-agent/
├── ai/                      # 包包初始化
├── cli/                     # CLI 命令
│   ├── __init__.py
│   ├── main.py             # 主入口
│   └── commands/           # 命令实现
│       ├── text.py
│       ├── tables.py
│       ├── images.py
│       ├── metadata.py
│       ├── structure.py
│       ├── to_markdown.py
│       ├── to_html.py
│       ├── to_json.py
│       ├── to_csv.py
│       ├── to_image.py
│       ├── to_epub.py
│       └── plugin.py
├── core/                    # 核心逻辑
│   ├── __init__.py
│   ├── engine/             # PDF 引擎
│   │   ├── __init__.py
│   │   ├── base.py         # 引擎基类
│   │   └── pymupdf_engine.py  # PyMuPDF 实现
│   ├── plugin_system/      # 插件系统
│   │   ├── __init__.py
│   │   ├── plugin_type.py  # 插件类型枚举
│   │   ├── plugin_manager.py  # 插件管理器
│   │   ├── base_plugin.py  # 插件基类
│   │   └── base_reader_plugin.py  # 阅读器基类
│   ├── readers/            # 核心阅读器
│   └── converters/         # 核心转换器
├── plugins/                 # 用户插件
│   ├── __init__.py
│   └── readers/            # 阅读器插件
│       ├── __init__.py
│       ├── text_reader.py
│       ├── table_reader.py
│       └── image_reader.py
├── utils/                   # 工具类
│   └── error_handler.py
├── tests/                   # 测试
│   ├── fixtures/           # 测试固件
│   └── ...
├── docs/                    # 文档
├── test-pdfs/              # 测试 PDF 文件
├── requirements.txt        # 依赖
├── setup.py               # 安装脚本
├── pytest.ini             # pytest 配置
└── README.md              # 项目说明
```

### 插件类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `READER` | 阅读器插件 | 文本、表格、图片读取 |
| `CONVERTER` | 转换器插件 | Markdown、HTML、EPUB 转换 |
| `OCR` | OCR 插件 | Tesseract、PaddleOCR |
| `RAG` | RAG 插件 | 向量索引、语义检索 |
| `ENCRYPT` | 加密插件 | PDF 加密、解密 |
| `COMPRESS` | 压缩插件 | PDF 压缩、图片优化 |
| `EDIT` | 编辑插件 | 添加文本、删除页面 |
| `ANALYZE` | 分析插件 | 质量评估、内容分析 |
| `CUSTOM` | 自定义插件 | 用户自定义功能 |

---

## 🛠️ 开发指南

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/ai-agent/ai-pdf-agent.git
cd ai-pdf-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -r requirements.txt
pip install -e .
```

### 如何开发插件

#### 1. 创建插件类

所有插件必须继承自对应的基类：

```python
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class MyPlugin(BasePlugin):
    # 插件元数据（必填）
    name = "my_plugin"
    version = "1.0.0"
    description = "插件描述"
    plugin_type = PluginType.READER  # 或其他类型
    author = "作者名"
    homepage = ""
    license = "MIT"

    # 依赖（可选）
    dependencies = ["package-name>=1.0.0"]
    system_dependencies = ["system-package"]

    def is_available(self) -> bool:
        """检查插件是否可用"""
        # 检查依赖、权限等
        return True

    def read(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """读取/处理 PDF"""
        # 实现具体逻辑
        return {
            "success": True,
            "data": ...
        }
```

#### 2. Reader 插件示例

```python
from core.plugin_system.base_reader_plugin import BaseReaderPlugin
from core.plugin_system.plugin_type import PluginType

class MyReaderPlugin(BaseReaderPlugin):
    name = "my_reader"
    version = "1.0.0"
    description = "我的阅读器插件"
    plugin_type = PluginType.READER

    def __init__(self, pdf_engine=None):
        super().__init__(pdf_engine)
        # 初始化逻辑

    def read(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        读取 PDF

        Returns:
            {
                "success": bool,
                "content": Any,
                "metadata": Dict,
                "error": Optional[str]
            }
        """
        result = {
            "success": False,
            "content": None,
            "metadata": {},
            "error": None
        }

        try:
            # 实现读取逻辑
            doc = self.pdf_engine.open(pdf_path)
            # ... 处理逻辑
            self.pdf_engine.close(doc)

            result["success"] = True
            result["content"] = content
        except Exception as e:
            result["error"] = str(e)

        return result

    def validate(self, pdf_path: str) -> Tuple[bool, Optional[str]]:
        """验证 PDF 文件"""
        # 实现验证逻辑
        return True, None
```

#### 3. Converter 插件示例

```python
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class MyConverterPlugin(BasePlugin):
    name = "my_converter"
    version = "1.0.0"
    description = "我的转换器插件"
    plugin_type = PluginType.CONVERTER

    def convert(self, pdf_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
        """
        转换 PDF

        Returns:
            {
                "success": bool,
                "output_path": str,
                "error": Optional[str]
            }
        """
        result = {
            "success": False,
            "output_path": output_path,
            "error": None
        }

        try:
            # 实现转换逻辑
            # ...
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)

        return result
```

#### 4. 注册插件

将插件放在 `plugins/` 目录下，插件管理器会自动发现：

```bash
# 阅读器插件
plugins/readers/my_reader.py

# 转换器插件
plugins/converters/my_converter.py
```

#### 5. 测试插件

```python
import pytest
from plugins.readers.my_reader import MyReaderPlugin

def test_my_reader():
    plugin = MyReaderPlugin()
    assert plugin.is_available()

    result = plugin.read("test.pdf")
    assert result["success"]
    assert result["content"] is not None
```

### 代码规范

```bash
# 格式化代码
black .

# 代码检查
flake8 .

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

### Git 提交规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式（不影响逻辑）
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. **Fork 项目**
   ```bash
   git clone https://github.com/your-username/ai-pdf-agent.git
   ```

2. **创建特性分支**
   ```bash
   git checkout -b feature/your-feature
   ```

3. **提交更改**
   ```bash
   git commit -m "feat: add your feature"
   ```

4. **推送到分支**
   ```bash
   git push origin feature/your-feature
   ```

5. **创建 Pull Request**

### 贡献类型

- 🐛 **Bug 修复** - 修复已知问题
- ✨ **新功能** - 添加新特性
- 📝 **文档改进** - 改进文档
- 🎨 **代码优化** - 性能优化
- 🧪 **测试覆盖** - 增加测试
- 🔧 **工具链** - 改进构建工具

### 代码审查

- 所有 PR 都需要经过代码审查
- 确保通过所有测试
- 遵循代码规范
- 更新相关文档

### 行为准则

- 尊重所有贡献者
- 使用清晰的语言
- 提供建设性反馈
- 保持开放心态

---

## 📄 许可证说明

本项目采用 **MIT License** 开源许可证。

```
MIT License

Copyright (c) 2024 AI PDF Agent Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR (IN CONNECTION WITH THE SOFTWARE THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 依赖库许可证

本项目使用以下依赖库，请遵守各自的许可证：

- **PyMuPDF** - AGPL-3.0
- **pdfplumber** - MIT
- **Pillow** - PIL License
- **pdf2image** - MIT
- **ebooklib** - AGPL-3.0
- **Click** - BSD-3-Clause

---

## 📞 联系方式

- **GitHub**: https://github.com/ai-agent/ai-pdf-agent
- **Issues**: https://github.com/ai-agent/ai-pdf-agent/issues
- **Discussions**: (待添加)

---

## 🙏 致谢

感谢以下项目和贡献者：

- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - 强大的 PDF 处理库
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF 表格提取
- [Click](https://github.com/pallets/click) - 优雅的 CLI 框架

---

## 📊 项目状态

- [x] 基础架构
- [x] 插件系统
- [x] 文本读取
- [x] 表格读取
- [x] 图片读取
- [x] 元数据读取
- [x] Markdown 转换
- [x] HTML 转换
- [x] JSON 转换
- [x] CSV 转换
- [x] Image 转换
- [x] EPUB 转换
- [ ] OCR 支持（计划中）
- [ ] RAG 支持（计划中）
- [ ] 加密支持（计划中）
- [ ] 压缩支持（计划中）
- [ ] 编辑功能（计划中）
- [ ] 完整测试覆盖（进行中）
- [ ] 性能优化（持续）

---

## ⚡ 性能优化

### 优化引擎

项目提供了优化的 PDF 引擎实现，显著提升处理性能：

```python
from core.engine.pymupdf_engine_optimized import BufferedPyMuPDFEngine

# 创建优化引擎
engine = BufferedPyMuPDFEngine(
    page_cache_size=20,  # 缓存 20 页
    workers=4            # 4 个工作线程
)

doc = engine.open("document.pdf")

# 流式处理（内存高效）
for page_text in engine.extract_text(doc, stream=True):
    process_page(page_text)

# 批量处理（并行）
text = engine.extract_text_batch(doc)

engine.close(doc)
```

### 性能特性

1. **页面缓存** - LRU 风格缓存，避免重复读取
2. **流式处理** - 生成器模式，逐页返回，内存高效
3. **并行处理** - 线程池并行处理，提升速度
4. **性能监控** - 内置性能指标收集和报告

### 性能提升

- **50 页 PDF**: 约 2-3x 加速
- **100 页 PDF**: 约 3-4x 加速
- **500+ 页 PDF**: 约 4-5x 加速

详细性能报告请参见 [PERFORMANCE.md](PERFORMANCE.md)。

### 性能监控

```python
from core.performance_monitor import monitor, monitor_performance

# 启用性能监控
monitor.enable()
monitor.enable_file_logging("performance.log")

# 使用装饰器监控函数
@monitor_performance(category="pdf_operations")
def process_pdf(pdf_path):
    # ... 处理逻辑
    pass

# 生成性能报告
report = monitor.generate_report("performance_report.txt")
print(report)
```

### 运行性能测试

```bash
# 运行性能测试
pytest tests/test_performance.py -v -s

# 运行综合性能测试
pytest tests/test_performance.py::TestComprehensivePerformance -v -s --slow
```

---

### 元数据读取插件 (Metadata Reader)

元数据读取插件 (`metadata_reader`) 提供了完整的 PDF 元数据提取功能：

```bash
# 提取元数据
ai-pdf metadata input.pdf -o metadata.json
```

**Python API 使用示例:**

```python
from plugins.readers.metadata_reader import MetadataReaderPlugin

plugin = MetadataReaderPlugin()

# 提取所有元数据
result = plugin.read("input.pdf")

# 访问完整元数据
print(f"标题: {result['metadata']['title']}")
print(f"作者: {result['metadata']['author']}")
print(f"页数: {result['metadata']['page_count']}")
print(f"PDF 版本: {result['metadata']['pdf_version']}")

# 访问基本元数据
print(f"基本元数据: {result['basic_metadata']}")

# 访问文档统计
stats = result['document_stats']
print(f"总字数: {stats['total_words']}")
print(f"总字符数: {stats['total_chars']}")
print(f"总图片数: {stats['total_images']}")
print(f"平均每页字数: {stats['average_words_per_page']:.2f}")

# 访问 PDF 特性
props = result['pdf_properties']
print(f"PDF 版本: {props['pdf_version']}")
print(f"是否加密: {props['is_encrypted']}")
print(f"是否可编辑: {props['is_editable']}")

# 权限信息
if 'permissions' in props:
    perms = props['permissions']
    print(f"可打印: {perms['can_print']}")
    print(f"可修改: {perms['can_modify']}")
    print(f"可复制: {perms['can_copy']}")

# 自定义选项
# 不包含文档统计
result = plugin.read("input.pdf", include_stats=False)

# 不包含 PDF 特性
result = plugin.read("input.pdf", include_properties=False)

# 不规范化元数据（保留空值）
result = plugin.read("input.pdf", normalize=False)
```

### 结构读取插件 (Structure Reader)

结构读取插件 (`structure_reader`) 提供了 PDF 文档结构分析功能，可以提取大纲、页面层次和逻辑结构：

```bash
# 提取文档结构
ai-pdf structure input.pdf -o structure.json
```

**Python API 使用示例:**

```python
from plugins.readers.structure_reader import StructureReaderPlugin

plugin = StructureReaderPlugin()

# 提取所有结构
result = plugin.read("input.pdf")

# 访问文档大纲
print(f"大纲项数: {len(result['outline'])}")
for item in result['outline']:
    print(f"  - {item['title']} (页 {item['page']}, 级别 {item['level']})")
    # 递归打印子节点
    for child in item['children']:
        print(f"    - {child['title']} (页 {child['page']}, 级别 {child['level']})")

# 访问页面结构
for page_struct in result['page_structure']:
    print(f"页 {page_struct['page']}:")
    print(f"  - 尺寸: {page_struct['width']:.0f} x {page_struct['height']:.0f}")
    print(f"  - 文本块: {page_struct['text_blocks']}")
    print(f"  - 图片块: {page_struct['image_blocks']}")
    print(f"  - 中位字体大小: {page_struct['median_font_size']}")
    print(f"  - 有页眉: {page_struct['has_header']}")
    print(f"  - 有页脚: {page_struct['has_footer']}")

# 访问逻辑结构
for item in result['logical_structure']:
    print(f"页 {item['page']}: [{item['type']}] {item['content'][:50]}...")

# 统计逻辑结构类型
from collections import Counter
structure_types = Counter(item['type'] for item in result['logical_structure'])
print(f"结构类型统计: {structure_types}")

# 获取完整文档树
tree = plugin.get_structure_tree("input.pdf")
print(f"文档树统计: {tree['statistics']}")

# 自定义选项
# 只提取大纲（不分析页面结构）
result = plugin.read("input.pdf", include_page_structure=False, include_logical_structure=False)

# 只提取指定页的结构
result = plugin.read("input.pdf", page=1)

# 提取页面范围的结构
result = plugin.read("input.pdf", page_range=(1, 5))

# 提取指定页列表的结构
result = plugin.read("input.pdf", pages=[1, 3, 5])
```

**返回数据结构说明:**

- **outline**: 文档大纲（目录）树结构，包含层级、标题、页码和子节点
- **page_structure**: 页面物理结构，包含尺寸、旋转角度、块数量、字体大小、页眉页脚检测
- **logical_structure**: 逻辑结构，包含类型（title/heading/paragraph/list/image）、层级、内容和位置
- **blocks**: 所有块信息（文本、图片、绘图），包含精确的位置坐标和元数据

**Made with ❤️ for AI Agents**
