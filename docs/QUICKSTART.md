# AI PDF Agent - 5分钟快速开始指南

欢迎使用 AI PDF Agent！本指南将帮助您在5分钟内快速上手这个强大的PDF处理工具。

## 📦 安装

### 使用 pip 安装

```bash
pip install ai-pdf-agent
```

### 从源码安装

```bash
git clone https://github.com/your-org/ai-pdf-agent.git
cd ai-pdf-agent
pip install -e .
```

### 验证安装

```bash
# 检查版本
ai-pdf --version

# 查看帮助
ai-pdf --help
```

## 🚀 基本用法

### 读取PDF文本

```bash
# 读取整个PDF的文本内容
ai-pdf read document.pdf

# 读取指定页面
ai-pdf read document.pdf --pages 1,2,3

# 保存到文件
ai-pdf read document.pdf -o output.txt
```

### PDF格式转换

```bash
# PDF转文本
ai-pdf convert document.pdf --to txt -o output.txt

# PDF转Markdown
ai-pdf convert document.pdf --to md -o output.md

# PDF转HTML
ai-pdf convert document.pdf --to html -o output.html

# 批量转换
ai-pdf convert *.pdf --to txt
```

### 插件管理

```bash
# 查看已安装插件
ai-pdf plugin list

# 安装插件
ai-pdf plugin install plugin-name

# 启用插件
ai-pdf plugin enable plugin-name

# 禁用插件
ai-pdf plugin disable plugin-name
```

## 📋 常用命令示例

### 读取命令

```bash
# 读取并显示文本（限制输出行数）
ai-pdf read document.pdf --limit 100

# 读取带元数据
ai-pdf read document.pdf --metadata

# 读取并提取表格
ai-pdf read document.pdf --extract-tables

# 读取并提取图片
ai-pdf read document.pdf --extract-images --images-dir ./images
```

### 转换命令

```bash
# 高质量文本转换
ai-pdf convert document.pdf --to txt --ocr --preserve-layout -o output.txt

# Markdown转换（保留格式）
ai-pdf convert document.pdf --to md --preserve-format -o output.md

# 转换为结构化JSON
ai-pdf convert document.pdf --to json --structure -o output.json
```

### 插件命令

```bash
# 使用翻译插件
ai-pdf translate document.pdf --to zh-CN -o translated.pdf

# 使用摘要插件
ai-pdf summarize document.pdf --length short

# 使用OCR插件
ai-pdf ocr document.pdf --language en+zh -o ocr_text.txt
```

## 🔧 Python API 快速入门

### 基本使用

```python
from ai_pdf_agent import PDFReader, PDFConverter

# 读取PDF
reader = PDFReader("document.pdf")
text = reader.read()
print(text)

# 读取指定页面
pages = reader.read_pages([1, 2, 3])
for page in pages:
    print(page)
```

### PDF转换

```python
# PDF转Markdown
converter = PDFConverter("document.pdf")
markdown = converter.to_markdown()

# 保存转换结果
converter.save(markdown, "output.md")

# 批量转换
converter = PDFConverter()
for pdf in ["doc1.pdf", "doc2.pdf"]:
    markdown = converter.load(pdf).to_markdown()
    converter.save(markdown, f"{pdf}.md")
```

### 插件使用

```python
from ai_pdf_agent import PDFProcessor

# 使用插件处理PDF
processor = PDFProcessor("document.pdf")

# 启用OCR插件
processor.enable_plugin("ocr")

# 启用翻译插件
processor.enable_plugin("translate")

# 处理并保存
result = processor.process(output="processed.pdf")
```

### 错误处理

```python
from ai_pdf_agent import PDFReader, PDFError

try:
    reader = PDFReader("document.pdf")
    text = reader.read()
except PDFError as e:
    print(f"处理PDF时出错: {e}")
except FileNotFoundError:
    print("文件不存在")
except Exception as e:
    print(f"未知错误: {e}")

# 使用上下文管理器
with PDFReader("document.pdf") as reader:
    text = reader.read()
    # 自动关闭资源
```

## 📚 下一步学习

恭喜您完成了快速入门！接下来您可以：

- **[README.md](README.md)** - 查看完整项目文档
- **[COMMANDS.md](COMMANDS.md)** - 了解所有可用命令和选项
- **[EXAMPLES.md](EXAMPLES.md)** - 查看更多使用示例和场景

## 💡 提示

- 使用 `ai-pdf --help` 查看所有可用命令
- 使用 `ai-pdf <command> --help` 查看特定命令的帮助
- 遇到问题时，请查看 [故障排除指南](TROUBLESHOOTING.md)

---

**开始您的PDF处理之旅吧！** 🎉
