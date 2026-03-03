# AI PDF Agent

> **AI Agent 友好的 PDF 处理工具** - 基于插件系统的 CLI 工具

## 简介

AI PDF Agent 是一个专为 AI Agent 设计的 PDF 处理工具，核心特性：

- ✅ **AI Agent 友好** - CLI + JSON 输出，程序化调用
- ✅ **插件化架构** - 所有功能通过插件扩展，生态开放
- ✅ **本地处理优先** - 隐私保护，无文件大小限制
- ✅ **开发者优先** - Markdown、JSON 等开发者友好格式

## 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/ai-agent/ai-pdf-agent.git
cd ai-pdf-agent

# 安装依赖
pip install -r requirements.txt

# 安装工具（可选）
pip install -e .
```

### 基本使用

```bash
# 查看帮助
ai-pdf --help

# 插件管理
ai-pdf plugin list
ai-pdf plugin info to-markdown

# 读取 PDF 文本
ai-pdf text document.pdf -o output.txt

# 转换为 Markdown
ai-pdf to-markdown document.pdf -o output.md

# JSON 输出（AI Agent 友好）
ai-pdf text document.pdf --json -o output.json
```

## 主要功能

### PDF 阅读器

```bash
# 文本读取
ai-pdf text input.pdf -o output.txt

# 表格读取
ai-pdf tables input.pdf -o tables.json

# 图片读取
ai-pdf images input.pdf -o images.json --extract-dir ./images

# 元数据读取
ai-pdf metadata input.pdf -o metadata.json

# 结构读取
ai-pdf structure input.pdf -o structure.json
```

### PDF 转换器

```bash
# Markdown 转换
ai-pdf to-markdown input.pdf -o output.md

# HTML 转换
ai-pdf to-html input.pdf -o output.html

# JSON 转换
ai-pdf to-json input.pdf -o output.json

# CSV 转换
ai-pdf to-csv input.pdf -o output.csv

# Image 转换
ai-pdf to-image input.pdf -o output.png

# EPUB 转换
ai-pdf to-epub input.pdf -o output.epub
```

### 插件管理

```bash
# 列出所有插件
ai-pdf plugin list

# 查看插件详情
ai-pdf plugin info <plugin-name>

# 检查插件依赖
ai-pdf plugin check <plugin-name>

# 启用/禁用插件
ai-pdf plugin enable <plugin-name>
ai-pdf plugin disable <plugin-name>

# 重载插件
ai-pdf plugin reload <plugin-name>
```

## AI Agent 集成示例

### Python 调用

```python
import subprocess
import json

# 提取文本
result = subprocess.run(
    ["["ai-pdf", "text", "document.pdf", "--json"],
    capture_output=True,
    text=True
)
data = json.loads(result.stdout)
print(data['text'])

# 转换为 Markdown
result = subprocess.run(
    ["ai-pdf", "to-markdown", "document.pdf", "-o", "output.md"],
    capture_output=True,
    text=True
)
```

### Shell 脚本

```bash
#!/bin/bash

# 批量处理文档
for file in documents/*.pdf; do
    ai-pdf text "$file" -o "output/$(basename $file .pdf).txt"
done
```

## 项目结构

```
ai-pdf-agent/
├── cli/                    # CLI 命令
├── core/                   # 核心逻辑
│   ├── plugin_system/      # 插件系统
│   ├── engine/             # PDF 引擎
│   ├── readers/            # 阅读器
│   └── converters/         # 转换器
├── plugins/                # 用户自定义插件
├── utils/                  # 工具类
├── tests/                  # 测试
└── docs/                   # 文档
```

## 开发

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html
```

### 代码格式化

```bash
# 格式化代码
black .

# 代码检查
flake8 .
```

## 许可证

MIT License

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 联系方式

- GitHub: https://github.com/ai-agent/ai-pdf-agent
- Issues: https://github.com/ai-agent/ai-pdf-agent/issues
