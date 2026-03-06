# AI PDF Agent - 智能 PDF 处理工具

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)]
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]

> 由 AI 团队自动开发的 PDF 智能处理工具

---

## 🌟 特性

- 📄 **智能读取**：自动识别 PDF 内容（文本、表格、图片、元数据）
- 🔄 **格式转换**：支持多种输出格式（Markdown、HTML、JSON、CSV、EPUB）
- 🚀 **高性能**：基于 PyMuPDF，速度和准确性优化
- 🤖 **插件化架构**：模块化设计，易于扩展
- 🐳 **容器化**：支持 Docker 部署，开箱即用
- 🔒 **隐私优先**：本地处理，无文件大小限制

---

## 🚀 安装

### 方案 A：Python 环境

#### 使用 pip 安装
```bash
pip install ai-pdf-agent
```

#### 从源码安装
```bash
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent
pip install -e .
```

#### 验证安装
```bash
ai --version
```

---

### 方案 B：Docker 环境

#### 拉取镜像
```bash
docker pull qqqzhch/ai-pdf-agent:latest
```

#### 从源码构建
```bash
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent
docker build -t ai-pdf-agent:latest .
```

---

## 🎯 使用指南

### Python 环境

#### 基本使用
```bash
# 读取 PDF（提取文本）
ai read document.pdf -o output.txt

# 读取 PDF（提取表格）
ai read document.pdf --type tables -o tables.json

# 转换为 Markdown
ai convert document.pdf --format markdown -o output.md

# 转换为 JSON
ai convert document.pdf --format json -o output.json

# 转换为 HTML
ai convert document.pdf --format html -o output.html

# 转换为 CSV
ai convert document.pdf --format csv -o output.csv

# 转换为 EPUB
ai convert document.pdf --format epub -o output.epub

# 查看版本
ai --version

# 查看帮助
ai --help
```

#### 高级选项
```bash
# 提取指定页面的文本
ai read document.pdf --pages 1-10 -o pages1-10.txt

# 提取表格（JSON 格式）
ai read document.pdf --type tables --json -o tables.json

# 提取图片
ai read document.pdf --type images --image-dir ./images

# 提取元数据
ai read document.pdf --type metadata -o metadata.json

# 提取结构信息
ai read document.pdf --type structure -o structure.json
```

---

### Docker 环境

#### 基本使用
```bash
# 读取 PDF
docker run -v $(pwd):/data ai-pdf-agent:latest read /data/document.pdf -o /data/output.txt

# 转换为 Markdown
docker run -v $(pwd):/data ai-pdf-agent:latest convert /data/document.pdf --format markdown -o /data/output.md

# 转换为 JSON
docker run -v $(pwd):/data ai-pdf-agent:latest convert /data/document.pdf --format json -o /data/output.json
```

#### 使用 Docker Compose
```bash
# 启动服务
docker-compose up -d

# 运行命令
docker-compose run ai-pdf-agent read document.pdf -o output.md

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 📋 CLI 命令说明

### `ai` - 主命令
```bash
ai --version    # 显示版本信息
ai --help       # 显示帮助信息
```

### `ai read` - 读取 PDF 内容

**功能：** 从 PDF 提取文本、表格、图片、元数据或结构信息

**语法：**
```bash
ai read <input.pdf> [options]
```

**选项：**
- `--type TYPE` - 提取类型（text, tables, images, metadata, structure）
- `-o, --output PATH` - 输出文件路径
- `--json` - 输出 JSON 格式
- `--pages START-END` - 指定页码范围
- `--image-dir PATH` - 图片输出目录

**示例：**
```bash
# 提取文本
ai read document.pdf -o output.txt

# 提取表格
ai read document.pdf --type tables --json -o tables.json

# 提取图片
ai read document.pdf --type images --image-dir ./images
```

---

### `ai convert` - 转换 PDF 格式

**功能：** 将 PDF 转换为其他格式

**语法：**
```bash
ai convert <input.pdf> --format <FORMAT> [options]
```

**选项：**
- `--format FORMAT` - 目标格式（markdown, json, html, csv, image, epub）
- `-o, --output PATH` - 输出文件路径
- `--pages START-END` - 指定页码范围

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

# 转换为 EPUB
ai convert document.pdf --format epub -o output.epub
```

---

## 🔧 开发

### 安装开发依赖

```bash
# 安装开发依赖
pip install -e .[dev]

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=ai_pdf_agent --cov-report=html

# 代码格式化
black .

# 类型检查
mypy .
```

---

## 📚 项目结构

```
ai-pdf-agent/
├── ai_pdf_agent/       # 核心包
│   ├── cli/            # CLI 工具
│   ├── core/           # 核心功能
│   ├── plugins/        # 插件系统
│   │   ├── readers/    # 读取插件
│   │   └── converters/ # 转换插件
│   └── version.py      # 版本信息
├── tests/              # 测试
├── requirements.txt    # 依赖
├── setup.py            # Python 包配置
├── Dockerfile         # Docker 镜像
├── docker-compose.yml # Docker Compose
└── README.md          # 文档
```

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 🔗 链接

- **Repository:** https://github.com/qqqzhch/ai-pdf-agent
- **Issues:** https://github.com/qqqzhch/ai-pdf-agent/issues
- **Documentation:** 详见 [SKILL.md](SKILL.md)

---

## 💡 提示

1. **性能优化：** 使用 `--pages` 选项指定页码范围，减少不必要的处理
2. **批处理：** 结合 Shell 脚本进行批量处理
3. **内存管理：** 大文件建议分页处理
4. **Docker 使用：** 确保 volume 映射正确，否则无法访问文件

---

## 🎉 版本

**当前版本：** v1.0.0

**更新内容：**
- ✅ 完整的 CLI 工具
- ✅ Docker 支持（开箱即用）
- ✅ 多格式转换支持
- ✅ 插件化架构
- ✅ 完善的文档和测试
