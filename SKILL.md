# AI PDF Agent Skill

## Description
AI Agent 友好的 PDF 处理工具，专为 AI Agent 设计的 CLI 工具，通过插件化架构提供灵活的 PDF 处理能力。

**最新版本：** v1.0.0（V2 团队部署版）

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

### 方案 A：从源码安装（Python 环境）

#### 1. Clone 仓库
```bash
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt

# 或者使用 setup.py 开发模式安装
pip install -e .
```

#### 3. 验证安装
```bash
# 检查版本
ai --version

# 查看帮助
ai --help
```

---

### 方案 B：使用 Docker（无需 Python 环境）

#### 1. Clone 仓库
```bash
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent
```

#### 2. 构建 Docker 镜像
```bash
docker build -t ai-pdf-agent:latest .
```

#### 3. 使用 Docker 容器
```bash
# 提取文本
docker run -v $(pwd)/data:/app/data ai-pdf-agent:latest read /app/data/document.pdf -o /app/data/output.txt

# 转换为 Markdown
docker run -v $(pwd)/data:/app/data ai-pdf-agent:latest convert /app/data/document.pdf --format markdown -o /app/data/output.md
```

---

### 方案 C：使用 Docker Compose（推荐生产环境）

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
docker-compose exec ai-pdf-agent bash

# 或者直接执行
docker-compose exec ai-pdf-agent ai read document.pdf -o output.md
```

---

## 🎯 Quick Start

### Python 环境

```bash
# 1. 提取文本
ai read document.pdf -o output.txt

# 2. 提取表格
ai read document.pdf --type tables -o tables.json

# 3. 转换为 Markdown
ai convert document.pdf --format markdown -o output.md

# 4. 转换为 JSON
ai convert document.pdf --format json -o output.json

# 5. 转换为 HTML
ai convert document.pdf --format html -o output.html
```

### Docker 环境

```bash
# 1. 提取文本
docker run -v $(pwd)/data:/app/data ai-pdf-agent:latest read /app/data/document.pdf -o /app/data/output.txt

# 2. 转换为 Markdown
docker run -v $(pwd)/data:/app/data ai-pdf-agent:latest convert /app/data/document.pdf --format markdown -o /app/data/output.md

# 3. 转换为 JSON
docker run -v $(pwd)/data:/app/data ai-pdf-agent:latest convert /app/data/document.pdf --format json -o /app/data/output.json
```

---

## 📋 CLI 命令完整指南

### `ai` - 主命令

```bash
ai --version    # 显示版本信息
ai --help       # 显示帮助信息
```

---

### `ai read` - 读取 PDF 内容

**功能：** 从 PDF 提取文本、表格、图片、元数据或结构信息

**语法：**
```bash
ai read <input.pdf> [options]
```

**选项：**
- `--type TYPE` - 提取类型（text, tables, images, metadata, structure）
- `-o, --output PATH` - 输出文件路径
- `--json` - 输出 JSON 格式（AI Agent 友好）
- `--pages START-END` - 指定页码范围（例如：1-5）
- `--image-dir PATH` - 图片输出目录（--type images 时使用）

**示例：**

```bash
# 提取文本
ai read document.pdf -o output.txt

# 提取表格（JSON 格式）
ai read document.pdf --type tables --json -o tables.json

# 提取图片
ai read document.pdf --type images --image-dir ./images

# 提取元数据
ai read document.pdf --type metadata -o metadata.json

# 提取结构信息
ai read document.pdf --type structure -o structure.json

# 提取指定页面的文本
ai read document.pdf --pages 1-10 -o pages1-10.txt
```

**输出示例（JSON 格式）：**
```json
{
  "success": true,
  "file": "document.pdf",
  "pages": 5,
  "text": "PDF document content...",
  "metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "created": "2026-03-05"
  }
}
```

---

### `ai convert` - 转换 PDF 格式

**功能：** 将 PDF 转换为其他格式（Markdown, JSON, HTML, CSV, Image, EPUB）

**语法：**
```bash
ai convert <input.pdf> --format <FORMAT> [options]
```

**选项：**
- `--format FORMAT` - 目标格式（markdown, json, html, csv, image, epub）
- `-o, --output PATH` - 输出文件路径
- `--pages START-END` - 指定页码范围
- `--image-dir PATH` - 图片输出目录

**示例：**

```bash
# 转换为 Markdown
ai convert document.pdf --format markdown -o output.md

# 转换为 JSON
ai convert document.pdf --format json -o output.json

# 转换为 HTML
ai convert document.pdf --format html -o output.html

# 转换为 CSV
ai convert document.pdf --format csv -o output.csv

# 转换为图片（每页一张图）
ai convert document.pdf --format image -o ./page_images

# 转换为 EPUB
ai convert document.pdf --format epub -o output.epub
```

---

## 🌟 Features

### 核心功能
- **Plugin System**: 模块化架构，易于扩展
- **Multi-format Support**: PDF → Markdown, JSON, HTML, CSV, EPUB
- **Content Extraction**: 文本、表格、图片、元数据、结构
- **AI Agent Friendly**: JSON 输出，便于程序化访问
- **Local Processing**: 隐私优先，无文件大小限制

### V2 团队特性（v1.0.0 新增）
- **100% 自动化**: 自动任务拆分、估算、分配
- **完美依赖管理**: 智能依赖检查和并行执行
- **30 分钟监控**: 自动状态检查和异常报告
- **技能集成**: task-planning, task-estimation, team-communication-protocols
- **Docker 支持**: 开箱即用，无需 Python 环境
- **Git Hooks**: 自动测试和文档更新

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

# 运行特定测试函数
pytest tests/test_text_reader.py::test_extract_text
```

### Docker 环境

```bash
# 进入测试容器
docker run -it ai-pdf-agent:latest bash

# 在容器内运行测试
pytest

# 或者直接运行测试
docker run ai-pdf-agent:latest pytest
```

---

## 📚 Documentation

### 项目文档
- **README.md**: 完整项目文档
- **QUICKSTART.md**: 5 分钟快速入门
- **COMMANDS.md**: 命令参考手册
- **EXAMPLES.md**: 使用示例
- **PLUGIN_DEV.md**: 插件开发指南

### V2 团队文档
- **TEAM_V2.md**: V2 团队设计文档
- **TEAM_V2_SUMMARY.md**: V2 团队实施总结
- **DEPLOYMENT_PLAN.md**: 部署方案
- **DEPLOYMENT_COMPLETE.md**: 部署完成总结

---

## 🔧 Advanced Usage

### 批量处理

```bash
# 批量提取文本
for file in *.pdf; do
    ai read "$file" -o "${file%.pdf}.txt"
done
```

### 与 AI Agent 集成

```python
import subprocess
import json

# 提取 PDF 文本（JSON 格式）
result = subprocess.run(
    ['ai', 'read', 'document.pdf', '--json'],
    capture_output=True,
    text=True
)

# 解析 JSON 输出
data = json.loads(result.stdout)

# 使用 AI Agent 处理文本
print(data['text'])
print(data['metadata'])
```

### V2 团队监控

```bash
# 启动 V2 团队监控
python3 v2_team_monitor.py

# 查看团队状态
cat TEAM_STATE_V2.json

# 查看报告历史
cat team_reports_v2.json
```

---

## 🎓 Examples

### 示例 1：技术手册转换为 Markdown

```bash
# 读取 Nginx 安全配置指南
ai read "Nginx 安全配置指南技术手册.pdf" -o nginx-guide.txt

# 转换为 Markdown（保留格式）
ai convert "Nginx 安全配置指南技术手册.pdf" --format markdown -o nginx-guide.md
```

### 示例 2：提取表格数据

```bash
# 从财务报表提取表格
ai read "financial-report.pdf" --type tables --json -o tables.json

# 转换为 CSV（便于 Excel 导入）
ai convert "financial-report.pdf" --format csv -o tables.csv
```

### 示例 3：批量转换

```bash
# 转换目录下所有 PDF 为 Markdown
for pdf in reports/*.pdf; do
    ai convert "$pdf" --format markdown -o "markdown/$(basename "$pdf" .pdf).md"
done
```

---

## 📦 Package Structure

```
ai-pdf-agent/
├── ai_pdf_agent/          # 包根目录
│   ├── cli/              # CLI 模块
│   │   ├── __init__.py
│   │   └── main.py      # CLI 主入口
│   ├── core/             # 核心模块
│   │   ├── pdf_engine.py # PDF 引擎
│   │   └── plugin_manager.py # 插件管理器
│   ├── plugins/          # 插件目录
│   │   ├── readers/      # 读取插件
│   │   └── converters/   # 转换插件
│   └── version.py        # 版本信息
├── tests/                # 测试目录
├── setup.py              # Python 包配置
├── requirements.txt      # Python 依赖
├── Dockerfile            # Docker 镜像
├── docker-compose.yml    # Docker Compose
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

1. **性能优化：** 使用 `--pages` 选项指定页码范围，减少不必要的处理
2. **批处理：** 结合 Shell 脚本或 Python 进行批量处理
3. **内存管理：** 大文件建议分页处理
4. **AI 集成：** 使用 `--json` 输出格式，便于 AI Agent 解析
5. **Docker 使用：** 确保 volume 映射正确，否则无法访问文件

---

## 🎉 Version

**当前版本：** v1.0.0

**更新内容：**
- ✅ V2 团队系统（100% 自动化）
- ✅ Docker 支持（开箱即用）
- ✅ CLI 工具完整实现
- ✅ 30 分钟自动监控
- ✅ 完善的文档和测试

---

**需要帮助？** 查看 [GitHub Issues](https://github.com/qqqzhch/ai-pdf-agent/issues) 或创建新 Issue。
