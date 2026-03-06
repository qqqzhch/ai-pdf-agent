# Simple PDF Skill

## Description
简单易用的 PDF 处理工具，通过插件化架构提供灵活的 PDF 处理能力。

**最新版本：** v1.0.0
**CLI 命令：** simple-pdf

---

## Use Cases
Use this skill when:
- User asks to extract text, tables, images from PDF documents
- User wants to convert PDF to Markdown, JSON, HTML, CSV formats
- User needs to analyze PDF metadata or structure
- User requests PDF content extraction for AI Agent processing
- User mentions "PDF", "document", "pdf tool", "document processing"

---

## 🚀 Installation

### 方案 A：Python 环境（推荐）

#### 1. Clone 仓库
```bash
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent
```

#### 2. 安装依赖
```bash
# 使用可编辑模式安装（推荐）
pip install -e .

# 或从 requirements.txt 安装
pip install -r requirements.txt
```

#### 3. 验证安装
```bash
# 检查版本
simple-pdf --version

# 查看帮助
simple-pdf --help

# 找到命令
which simple-pdf
```

#### 4. 如果命令找不到

```bash
# 方法 1：使用虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate
pip install -e .
simple-pdf --version

# 方法 2：检查 PATH
echo $PATH | grep -i local

# 方法 3：直接使用模块
python3 -m ai_pdf_agent.cli.cli --version
```

---

### 方案 B：Docker 环境（无需 Python）

#### 1. Clone 仓库
```bash
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent
```

#### 2. 构建 Docker 镜像
```bash
docker build -t simple-pdf:latest .
```

#### 3. 使用 Docker 容器
```bash
# 提取文本
docker run -v $(pwd)/data:/app/data simple-pdf:latest read /app/data/document.pdf -o /app/data/output.txt

# 转换为 Markdown
docker run -v $(pwd)/data:/app/data simple-pdf:latest convert /app/data/document.pdf --format markdown -o /app/data/output.md
```

---

### 方案 C：Docker Compose（推荐生产环境）

#### 1. Clone 仓库
```bash
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent
```

#### 2. 启动服务
```bash
docker-compose up -d
```

#### 3. 使用服务
```bash
# 进入容器
docker-compose exec simple-pdf bash

# 或者直接执行
docker-compose exec simple-pdf simple-pdf read document.pdf -o output.md
```

---

## 🎯 Quick Start

### Python 环境

```bash
# 1. 提取文本
simple-pdf read document.pdf -o output.txt

# 2. 转换为 Markdown
simple-pdf convert document.pdf --format markdown -o output.md

# 3. 转换为 JSON
simple-pdf convert document.pdf --format json -o output.json

# 4. 转换为 HTML
simple-pdf convert document.pdf --format html -o output.html
```

### Docker 环境

```bash
# 1. 提取文本
docker run -v $(pwd)/data:/app/data simple-pdf:latest read /app/data/document.pdf -o /app/data/output.txt

# 2. 转换为 Markdown
docker run -v $(pwd)/data:/app/data simple-pdf:latest convert /app/data/document.pdf --format markdown -o /app/data/output.md

# 3. 转换为 JSON
docker run -v $(pwd)/data:/app/data simple-pdf:latest convert /app/data/document.pdf --format json -o /app/data/output.json
```

---

## 📋 CLI 命令完整指南

### `simple-pdf` - 主命令

```bash
simple-pdf --version    # 显示版本信息
simple-pdf --help       # 显示帮助信息
```

---

### `simple-pdf read` - 读取 PDF 内容

**功能：** 从 PDF 提取文本、表格、图片、元数据或结构信息

**语法：**
```bash
simple-pdf read <pdf-path> [-o output]
```

**选项：**
- `pdf-path` - PDF 文件路径（必需）
- `-o, --output PATH` - 输出文件路径（可选）

**示例：**

```bash
# 提取文本
simple-pdf read document.pdf -o output.txt

# 提取表格
simple-pdf read document.pdf -o tables.json

# 提取图片
simple-pdf read document.pdf -o images.json

# 提取元数据
simple-pdf read document.pdf -o metadata.json

# 提取结构信息
simple-pdf read document.pdf -o structure.json
```

**输出示例：**
```
读取 PDF: document.pdf
输出到: output.txt
```

---

### `simple-pdf convert` - 转换 PDF 格式

**功能：** 将 PDF 转换为其他格式（Markdown, JSON, HTML, Text）

**语法：**
```bash
simple-pdf convert <pdf-path> --format <format> [-o output]
```

**选项：**
**pdf-path` - PDF 文件路径（必需）
- `--format, -f FORMAT` - 目标格式（必需：markdown, html, json, text）
- `-o, --output PATH` - 输出文件路径（可选）

**示例：**

```bash
# 转换为 Markdown
simple-pdf convert document.pdf --format markdown -o output.md

# 转换为 JSON
simple-pdf convert document.pdf --format json -o output.json

# 转换为 HTML
simple-pdf convert document.pdf --format html -o output.html

# 转换为 Text
simple-pdf convert document.pdf --format text -o output.txt
```

**输出示例：**
```
转换 PDF: document.pdf -> markdown
输出到: output.md
```

---

## 🌟 Features

### 核心功能
- **Plugin System**: 模块化架构，易于扩展
- **Multi-format Support**: PDF → Markdown, JSON, HTML, Text
- **Content Extraction**: 文本、表格、图片、元数据、结构
- **Simple to Use**: 简单易用的命令行接口
- **Local Processing**: 隐私优先，无文件大小限制

### 性能优化
- **高性能 PDF 引擎**: 基于 PyMuPDF，快速可靠
- **批量处理**: 支持批量处理多个文件
- **内存优化**: 流式处理，减少内存占用

---

## 🧪 Testing

### Python 环境

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=ai_pdf_agent --cov-report=html

# 运行特定测试文件
pytest tests/test_text_reader.py
```

### Docker 环境

```bash
# 进入测试容器
docker run -it simple-pdf:latest bash

# 在容器内运行测试
pytest

# 或者直接运行测试
docker run simple-pdf:latest pytest
```

---

## 📚 Documentation

### 项目文档
- **README.md**: 完整项目文档
- **QUICKSTART.md**: 5 分钟快速入门
- **COMMANDS.md**: 命令参考手册
- **EXAMPLES.md**: 使用示例
- **PLUGIN.md**: 插件开发指南

---

## 🔧 Advanced Usage

### 批量处理

```bash
# 批量提取文本
for file in *.pdf; do
    simple-pdf read "$file" -o "${file%.pdf}.txt"
done
```

### 与 AI Agent 集成

```python
import subprocess

# 提取 PDF 文本
result = subprocess.run(
    ['simple-pdf', 'read', 'document.pdf', '-o', 'output.txt'],
    capture_output=True,
    text=True
)

# 转换为 Markdown
result = subprocess.run(
    ['simple-pdf', 'convert', 'document.pdf', '--format', 'markdown', '-o', 'output.md'],
    capture_output=True,
    text=True
)
```

---

## 🎓 Examples

### 示例 1：技术手册转换为 Markdown

```bash
# 读取 Nginx 安全配置指南
simple-pdf read "Nginx 安全配置指南技术手册.pdf" -o nginx-guide.txt

# 转换为 Markdown（保留格式）
simple-pdf convert "Nginx 安全配置指南技术手册.pdf" --format markdown -o nginx-guide.md
```

### 示例 2：提取表格数据

```bash
# 从财务报表提取表格
simple-pdf read "financial-report.pdf" -o tables.json

# 转换为 JSON 格式
simple-pdf convert "financial-report.pdf" --format json -o tables.json
```

### 示例 3：批量转换

```bash
# 转换目录下所有 PDF 为 Markdown
for pdf in reports/*.pdf; do
    simple-pdf convert "$pdf" --format markdown -o "markdown/$(basename "$pdf" .pdf).md"
done
```

---

## 📦 Package Structure

```
ai-pdf-agent/
├── ai_pdf_agent/          # 包根目录
│   ├── __init__.py        # 包初始化
│   ├── cli/              # CLI 模块
│   │   ├── __init__.py
│   │   └── cli.py       # CLI 主入口
│   ├── core/             # 核心模块
│   │   ├── __init__.py
│   │   ├── pdf_engine.py # PDF 引擎
│   │   └── ...
│   ├── plugins/          # 插件目录
│   │   ├── __init__.py
│   │   ├── readers/      # 读取插件
│   │   └── converters/   # 转换插件
│   └── version.py        # 版本信息
├── tests/                # 测试目录
├── setup.py              # Python 包配置
├── requirements.txt      # Python 依赖
├── Dockerfile            # Docker 镜像
├── docker-compose.yml    # Docker Compose
├── install.sh            # 自动安装脚本
├── diagnose.sh           # 诊断脚本
└── README.md             # 项目文档
```

---

## 🤝 Contributing

欢迎贡献代码！请遵循以下步骤：

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 License

MIT License - 详见 LICENSE 文件

---

## 🔗 Links

- **Repository:** https://github.com/qqqzhch/ai-pdf-agent
- **Issues:** https://github.com/qqqzhch/ai-pdf-agent/issues
- **Releases:** https://github.com/qqqzhch/ai-pdf-agent/releases

---

## 💡 Tips

1. **安装方法：** 推荐使用虚拟环境安装
2. **性能优化：** 分页处理大文件
3. **批处理：** 结合 Shell 脚本进行批量处理
4. **内存管理：** 大文件建议分页处理
5. **AI 集成：** 使用 `-o` 输出到文件，便于 AI Agent 解析
6. **Docker 使用：** 确保 volume 映射正确，否则无法访问文件

---

## 🎉 Version

**当前版本：** v1.0.0

**更新内容：**
- ✅ 完整的 CLI 工具（命令：simple-pdf）
- ✅ 虚拟环境支持
- ✅ Docker 支持（开箱即用）
- ✅ 多格式转换支持
- ✅ 插件化架构
- ✅ 完善的文档和测试

---

**需要帮助？** 查看 [GitHub Issues](https://github.com/qqqzhch/ai-pdf-agent/issues) 或创建新 Issue。
