# Simple PDF Skill

## Description
简单易用的 PDF 处理工具，通过插件化架构提供灵活的 PDF 处理能力。

**最新版本：** v1.0.0
**CLI 命令：** simple-pdf
**平台支持：** Windows、Linux、macOS

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

### Windows

#### 方案 A：使用 pip 安装（推荐）

```powershell
# 使用 PowerShell
pip install simple-pdf

# 或使用 CMD
pip install simple-pdf

# 验证安装
simple-pdf --version
```

#### 方案 B：从源码安装（推荐）

```powershell
# 1. Clone 仓库
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent

# 2. 创建虚拟环境（推荐）
python -m venv venv

# 3. 激活虚拟环境（PowerShell）
.\venv\Scripts\Activate.ps1

# 或使用 CMD
venv\Scripts\activate.bat

# 4. 升级 pip
pip install --upgrade pip

# 5. 安装包
pip install -e .

# 6. 验证安装
simple-pdf --version
simple-pdf --help
```

#### 方案 C：使用安装脚本（推荐）

```powershell
# 下载并运行安装脚本
.\install.ps1

# 或使用参数
.\install.ps1 -Reinstall  # 重新安装
.\install.ps1 -Test     # 安装并测试
```

**安装脚本功能：**
- ✅ 自动检测 Python 和 pip
- ✅ 创建虚拟环境
- ✅ 安装包
- ✅ 验证安装
- ✅ 支持多镜像源（默认、清华、阿里云等）
- ✅ 彩色输出和进度显示

---

### Linux / macOS

#### 方案 A：使用 pip 安装

```bash
pip install simple-pdf
```

#### 方案 B：从源码安装

```bash
# 1. Clone 仓库
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent

# 2. 安装依赖
pip install -r requirements.txt

# 或使用可编辑模式安装（推荐）
pip install -e .

# 3. 验证安装
simple-pdf --version
```

#### 方案 C：使用虚拟环境（推荐）

```bash
# 1. Clone 仓库
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate  # Linux/macOS

# 4. 安装包
pip install -e .

# 5. 验证安装
simple-pdf --version
simple-pdf --help
```

#### 方案 D：使用安装脚本（推荐）

```bash
# 添加执行权限
chmod +x install.sh

# 运行安装脚本
./install.sh

# 或使用参数
./install.sh --reinstall  # 重新安装
./install.sh --test      # 安装并测试

# 指定镜像源
./install.sh --mirror tuna           # 使用清华大学镜像
./install.sh --mirror tsinghua       # 使用清华大学镜像（备用）
./install.sh --mirror aliyun         # 使用阿里云镜像
```

---

### Docker（跨平台）

#### 方案 A：拉取镜像

```bash
docker pull simple-pdf:latest
```

#### 方案 B：从源码构建

```bash
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent
docker build -t simple-pdf:latest .
```

---

## 🎯 Quick Start

### Windows

#### PowerShell

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

#### CMD

```cmd
simple-pdf read document.pdf -o output.txt
simple-pdf convert document.pdf --format markdown
```

---

### Linux / macOS

```bash
# 读取 PDF
simple-pdf read document.pdf -o output.txt

# 转换为 Markdown
simple-pdf convert document.pdf --format markdown -o output.md

# 转换为 JSON
simple-pdf convert document.pdf --format json -o output.json

# 转换为 HTML
simple-pdf convert document.pdf --format html -o output.html
```

---

## 📋 CLI 命令完整指南

### `simple-pdf` - 主命令

```powershell
# PowerShell / CMD
simple-pdf --version    # 显示版本信息
simple-pdf --help       # 显示帮助信息

# Linux / macOS
simple-pdf --version    # 显示版本信息
simple-pdf --help       # 显示帮助信息
```

---

### `simple-pdf read` - 读取 PDF 内容

**功能：** 从 PDF 提取文本、表格、图片、元数据或结构信息

**语法：**
```powershell
# Windows (PowerShell / CMD)
simple-pdf read <pdf-path> [-o output]

# Linux / macOS
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
```powershell
# Windows (PowerShell / CMD)
simple-pdf convert <pdf-path> --format <format> [-o output]

# Linux / macOS
simple-pdf convert <pdf-path> --format <format> [-o output]
```

**选项：**
- `pdf-path` - PDF 文件路径（必需）
- `--format, -f FORMAT` - 目标格式（必需：markdown, html, json, text）
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

### 跨平台支持
- **Windows**: 支持 PowerShell 和 CMD
- **Linux**: 支持 Bash 和 Zsh
- **macOS**: 支持 Bash 和 Zsh
- **Docker**: 跨平台容器化部署

---

## � Installation Scripts

### Windows (install.ps1)

**功能：**
- ✅ 自动检测 Python 和 pip
- ✅ 创建虚拟环境
- ✅ 支持多镜像源（默认、清华、阿里云等）
- ✅ 自动镜像切换（默认失败时切换清华）
- ✅ 彩色输出和进度显示

**使用方法：**
```powershell
# 基本安装
.\install.ps1

# 重新安装
.\install.ps1 -Reinstall

# 安装并测试
.\install.ps1 -Test

# 使用清华大学镜像
.\install.ps1 -PipMirror tuna

# 查看帮助
.\install.ps1 -Help

# 使用自定义镜像
.\install.ps1 -PipIndex https://pypi.mirrors.china.edu/simple
```

**支持的镜像源：**
- `default` - PyPI 官方镜像
- `tuna` - 清华大学镜像（https://pypi.tuna.tsinghua.edu.cn/simple）
- `aliyun` - 阿里云镜像（https://mirrors.aliyun.com/pypi/simple）
- `pypi` - PyPI 官方镜像（备用）

---

### Linux/macOS (install.sh)

**功能：**
- ✅ 自动检测 Python 和 pip
- ✅ 创建虚拟环境
- ✅ 支持多镜像源（默认、清华、阿里云等）
- ✅ 环境变量支持（PIP_INDEX_URL）
- ✅ 彩色输出和进度显示

**使用方法：**
```bash
# 添加执行权限
chmod +x install.sh

# 基本安装
./install.sh

# 重新安装
./install.sh --reinstall

# 安装并测试
./install.sh --test

# 指定镜像源
./install.sh --mirror tuna        # 清华大学镜像
./install.sh --mirror aliyun       # 阿里云镜像
./install.sh --mirror tsinghua    # 清华大学镜像（备用）

# 指定自定义镜像 URL
./install.sh --mirror-index https://pypi.mirrors.china.edu/simple

# 查看帮助
./install.sh --help
```

**支持的镜像源：**
- `default` - PyPI 官方镜像
- `tuna` - 清华大学镜像
- `tsinghua` - 清华大学镜像（备用）
- `aliyun` - 阿里云镜像
- `ustc` - 中科大镜像
- `chima` - 中国科大镜像
- `pypi` - PyPI 官方镜像（备用）

---

## � Troubleshooting

### 常见问题

#### Q1: 命令不存在？

**Windows:**
```powershell
# 检查是否在虚拟环境中
where simple-pdf

# 或使用模块直接运行
python -m ai_pdf_agent.cli.cli --version

# 查找安装位置
Get-ChildItem $HOME -Recurse -ErrorAction SilentlyContinue -Include simple-pdf.exe
```

**Linux/macOS:**
```bash
# 检查是否在虚拟环境中
which simple-pdf

# 或使用模块直接运行
python3 -m ai_pdf_agent.cli.cli --version

# 查找安装位置
find ~/.local -name "simple-pdf" 2>/dev/null
```

#### Q2: pip 默认源无法访问？

**Windows:**
```powershell
# 使用安装脚本（自动切换到清华镜像）
.\install.ps1 -PipMirror tuna

# 手动设置镜像
$env:PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"
pip install simple-pdf
```

**Linux/macOS:**
```bash
# 使用安装脚本（自动切换到清华镜像）
./install.sh --mirror tuna

# 手动设置镜像
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
pip install simple-pdf
```

#### Q3: 需要激活虚拟环境？

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

---

## � Advanced Usage

### 批量处理

**Windows:**
```powershell
# 批量提取文本
Get-ChildItem . -Filter *.pdf | ForEach-Object {
    simple-pdf read $_.FullName -o "$($_.BaseName).txt"
}
```

**Linux/macOS:**
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

**Windows:**
```powershell
# 读取 Nginx 安全配置指南
simple-pdf read "Nginx 安全配置指南技术手册.pdf" -o nginx-guide.txt

# 转换为 Markdown（保留格式）
simple-pdf convert "Nginx 安全配置指南技术手册.pdf" --format markdown -o nginx-guide.md
```

**Linux/macOS:**
```bash
# 读取 Nginx 安全配置指南
simple-pdf read "Nginx 安全配置指南技术手册.pdf" -o nginx-guide.txt

# 转换为 Markdown（保留格式）
simple-pdf convert "Nginx 安全配置指南技术手册.pdf" --format markdown -o nginx-guide.md
```

### 示例 2：提取表格数据

**Windows:**
```powershell
# 从财务报表提取表格
simple-pdf read "financial-report.pdf" -o tables.json

# 转换为 JSON 格式
simple-pdf convert "financial-report.pdf" --format json -o tables.json
```

**Linux/macOS:**
```bash
# 从财务报表提取表格
simple-pdf read "financial-report.pdf" -o tables.json

# 转换为 JSON 格式
simple-pdf convert "financial-report.pdf" --format json -o tables.json
```

### 示例 3：批量转换

**Windows:**
```powershell
# 转换目录下所有 PDF 为 Markdown
Get-ChildItem reports -Filter *.pdf | ForEach-Object {
    $mdName = "$($_.BaseName).md"
    simple-pdf convert $_.FullName --format markdown -o $mdName
}
```

**Linux/macOS:**
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
│   │   └── ...
│   ├── plugins/          # 插件目录
│   │   ├── __init__.py
│   │   ├── readers/      # 读取插件
│   │   │   └── ...
│   │   └── converters/   # 转换插件
│   └── version.py        # 版本信息
├── tests/                # 测试目录
├── install.ps1            # Windows 安装脚本（PowerShell）
├── install.sh              # Linux/macOS 安装脚本（Bash）
├── simple-pdf.sh           # 快速启动脚本（Linux/macOS）
├── simple-pdf.bat          # 快速启动脚本（Windows）
├── requirements.txt        # Python 依赖
├── setup.py                # Python 包配置
├── Dockerfile               # Docker 镜像
├── docker-compose.yml         # Docker Compose
└── README.md              # 项目文档
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

1. **跨平台：** 推荐使用安装脚本自动处理平台差异
2. **镜像源：** 默认源无法访问时，使用清华或阿里云镜像
3. **虚拟环境：** 推荐使用虚拟环境隔离项目依赖
4. **批处理：** 结合 Shell 脚本进行批量处理
5. **内存管理：** 大文件建议分页处理
6. **AI 集成：** 使用 `-o` 输出到文件，便于 AI Agent 解析

---

## 🎉 Version

**当前版本：** v1.0.0

**更新内容：**
- ✅ 完整的 CLI 工具（命令：simple-pdf）
- ✅ 跨平台支持（Windows、Linux、macOS）
- ✅ 安装脚本（PowerShell + Bash）
- ✅ 多镜像源支持（默认、清华、阿里云）
- ✅ 自动镜像切换功能
- ✅ Docker 支持（开箱即用）
- ✅ 多格式转换支持
- ✅ 插件化架构
- ✅ 完善的文档和测试

---

**需要帮助？** 查看 [GitHub Issues](https://github.com/qqqzhch/ai-pdf-agent/issues) 或创建新 Issue。
