# Simple PDF - 简单易用的 PDF 处理工具

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)]
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]

> 简单、快速、易用的 PDF 处理工具（跨平台支持）

---

## 🌟 特性

- 📄 **简单读取**：一键提取 PDF 内容（文本、表格、图片、元数据）
- 🔄 **格式转换**：支持多种输出格式（Markdown、HTML、JSON、Text）
- 🚀 **高性能**：基于 PyMuPDF，速度和准确性优化
- 🤖 **插件化架构**：模块化设计，易于扩展
- 🐳 **容器化**：支持 Docker 部署，开箱即用
- 🔒 **隐私优先**：本地处理，无文件大小限制
- 🌐 **跨平台**：支持 Windows、Linux、macOS

---

## 🚀 安装

### Windows

#### 使用 pip 安装（推荐）
```powershell
# 打开 PowerShell 或 CMD
pip install simple-pdf
```

#### 从源码安装
```powershell
# 1. Clone 仓库
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent

# 2. 创建虚拟环境（推荐）
python -m venv venv

# 3. 激活虚拟环境
.\venv\Scripts\activate

# 4. 安装包
pip install -e .

# 5. 验证安装
simple-pdf --version
```

#### 使用虚拟环境
```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（PowerShell）
.\venv\Scripts\Activate.ps1

# 激活虚拟环境（CMD）
venv\Scripts\activate.bat

# 安装包
pip install -e .

# 使用命令
simple-pdf --version
```

---

### Linux / macOS

#### 使用 pip 安装
```bash
pip install simple-pdf
```

#### 从源码安装
```bash
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent

# 创建虚拟环境（推荐）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux
source venv/bin/activate  # macOS

# 安装包
pip install -e .

# 验证安装
simple-pdf --version
```

---

### Docker（跨平台）

#### 拉取镜像
```bash
docker pull simple-pdf:latest
```

#### 从源码构建
```bash
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent
docker build -t simple-pdf:latest .
```

---

## 🎯 使用指南

### Windows

#### 基本使用
```powershell
# 读取 PDF
simple-pdf read document.pdf -o output.txt

# 转换 PDF
simple-pdf convert document.pdf --format markdown

# 查看版本
simple-pdf --version

# 查看帮助
simple-pdf --help
```

#### 高级用法
```powershell
# 读取并输出到文件
simple-pdf read document.pdf -o output.txt

# 转换为 Markdown
simple-pdf convert document.pdf --format markdown -o output.md

# 转换为 JSON
simple-pdf convert document.pdf --format json -o output.json

# 转换为 HTML
simple-pdf convert document.pdf --format html -o output.html

# 转换为 Text
simple-pdf convert document.pdf --format text -o output.txt
```

---

### Linux / macOS

#### 基本使用
```bash
# 读取 PDF
simple-pdf read document.pdf -o output.txt

# 转换 PDF
simple-pdf convert document.pdf --format markdown

# 查看版本
simple-pdf --version

# 查看帮助
simple-pdf --help
```

#### 高级用法
```bash
# 读取并输出到文件
simple-pdf read document.pdf -o output.txt

# 转换为 Markdown
simple-pdf convert document.pdf --format markdown -o output.md

# 转换为 JSON
simple-pdf convert document.pdf --format json -o output.json

# 转换为 HTML
simple-pdf convert document.pdf --format html -o output.html

# 转换为 Text
simple-pdf convert document.pdf --format text -o output.txt
```

---

### Docker（跨平台）

#### 基本使用
```bash
# 读取 PDF
docker run -v $(pwd):/data simple-pdf:latest read /data/document.pdf -o /data/output.txt

# 转换 PDF
docker run -v $(pwd):/data simple-pdf:latest convert /data/document.pdf --format markdown -o /data/output.md

# 使用 docker-compose
docker-compose run simple-pdf read document.pdf
```

#### 使用 Docker Compose
```bash
# 启动服务
docker-compose up -d

# 运行命令
docker-compose run simple-pdf read document.pdf -o output.md

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 📋 CLI 命令说明

### `simple-pdf` - 主命令
```powershell
simple-pdf --version    # 显示版本信息
simple-pdf --help       # 显示帮助信息
```

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
```powershell
# 提取文本
simple-pdf read document.pdf -o output.txt

# 提取表格
simple-pdf read document.pdf -o tables.json

# 提取图片
simple-pdf read document.pdf -o images.json

# 提取元数据
simple-pdf read document.pdf -o metadata.json
```

### `simple-pdf convert` - 转换 PDF 格式

**功能：** 将 PDF 转换为其他格式（Markdown, JSON, HTML, Text）

**语法：**
```bash
simple-pdf convert <pdf-path> --format <format> [-o output]
```

**选项：**
- `pdf-path` - PDF 文件路径（必需）
- `--format, -f` FORMAT - 目标格式（必需：markdown, html, json, text）
- `-o, --output PATH` - 输出文件路径（可选）

**示例：**
```powershell
# 转换为 Markdown
simple-pdf convert document.pdf --format markdown -o output.md

# 转换为 JSON
simple-pdf convert document.pdf --format json -o output.json

# 转换为 HTML
simple-pdf convert document.pdf --format html -o output.html

# 转换为 Text
simple-pdf convert document.pdf --format text -o output.txt
```

---

## 🔧 开发

### 安装开发依赖

#### Windows
```powershell
pip install -e .[dev]
```

#### Linux / macOS
```bash
pip install -e .[dev]
```

### 运行测试

#### Windows
```powershell
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=ai_pdf_agent --cov-report=html

# 运行特定测试文件
pytest tests/test_text_reader.py
```

#### Linux / macOS
```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=ai_pdf_agent --cov-report=html

# 运行特定测试文件
pytest tests/test_text_reader.py
```

### 代码格式化和类型检查

```bash
# 代码格式化
black .

# 类型检查
mypy .
```

---

## 📂 项目结构

```
ai-pdf-agent/
├── ai_pdf_agent/       # 核心包
│   ├── __init__.py
│   ├── cli/            # CLI 工具
│   │   ├── __init__.py
│   │   └── cli.py       # CLI 主入口
│   ├── core/           # 核心功能
│   │   ├── __init__.py
│   │   └── ...
│   ├── plugins/        # 插件系统
│   │   ├── __init__.py
│   │   ├── readers/    # 读取插件
│   │   └── converters/ # 转换插件
│   └── version.py      # 版本信息
├── tests/              # 测试
├── install.sh          # 自动安装脚本（Linux/macOS）
├── install.ps1         # 自动安装脚本（Windows）
├── diagnose.sh         # 诊断脚本（Linux/macOS）
├── diagnose.ps1        # 诊断脚本（Windows）
├── simple-pdf.sh       # 快速启动脚本（Linux/macOS）
├── simple-pdf.bat      # 快速启动脚本（Windows）
├── requirements.txt    # 依赖
├── setup.py            # Python 包配置
├── Dockerfile         # Docker 镜像
├── docker-compose.yml # Docker Compose
└── README.md          # 文档
```

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

1. **虚拟环境：** 推荐使用虚拟环境安装
2. **Windows 用户：** 使用 PowerShell 或 CMD 运行命令
3. **路径分隔符：** Windows 使用 `\`，Linux/macOS 使用 `/`
4. **性能优化：** 分页处理大文件
5. **批处理：** 结合 Shell 脚本进行批量处理
6. **内存管理：** 大文件建议分页处理
7. **Docker 使用：** 确保 volume 映射正确，否则无法访问文件

---

## 🌐 跨平台说明

### Windows 路径
```powershell
# 虚拟环境路径
.\venv\Scripts\activate.ps1  # PowerShell
venv\Scripts\activate.bat   # CMD

# 文件路径（使用 `\`）
C:\Users\YourName\Documents\document.pdf
```

### Linux / macOS 路径
```bash
# 虚拟环境路径
source venv/bin/activate

# 文件路径（使用 `/`）
/home/username/Documents/document.pdf
```

### Docker 卷映射
```bash
# Windows
docker run -v C:\Users\YourName\Documents:/data simple-pdf:latest read /data/document.pdf

# Linux / macOS
docker run -v $(pwd):/data simple-pdf:latest read /data/document.pdf
```

---

## 🎉 版本

**当前版本：** v1.0.0

**更新内容：**
- ✅ 完整的 CLI 工具（命令：simple-pdf）
- ✅ 跨平台支持（Windows、Linux、macOS）
- ✅ 虚拟环境支持（Windows、Linux/macOS）
- ✅ Docker 支持（开箱即用）
- ✅ 多格式转换支持
- ✅ 插件化架构
- ✅ 完善的文档和测试

---

## 🔓 平台特定说明

### Windows 安装脚本

**install.ps1** - Windows 自动安装脚本
```powershell
# 右键点击运行
.\install.ps1

# 或使用 PowerShell
powershell -ExecutionPolicy Bypass -File install.ps1
```

### Linux/macOS 安装脚本

**install.sh** - Linux/macOS 自动安装脚本
```bash
# 添加执行权限
chmod +x install.sh

# 运行
./install.sh
```

---

**需要帮助？** 查看 [GitHub Issues](https://github.com/qqqzhch/ai-pdf-agent/issues) 或创建新 Issue。
