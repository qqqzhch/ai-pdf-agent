# 安装和部署指南

> AI PDF Agent 完整的安装、配置和使用说明

---

## 📦 安装方式

### 前置要求

- Python 3.8 或更高版本
- pip (Python 包管理器)
- 网络连接（用于下载依赖）

---

### 方式 1：从 PyPI 安装（推荐）

```bash
# 安装到系统
pip install ai-pdf-agent

# 或使用 pip3
pip3 install ai-pdf-agent
```

**验证安装：**
```bash
ai-pdf --version
ai-pdf --help
```

---

### 方式 2：从源码安装

```bash
# 1. 克隆项目
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent

# 2. 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 3. 安装到系统
pip install -e .

# 4. 验证安装
ai-pdf --version
ai-pdf --help
```

---

### 方式 3：开发模式（仅开发使用）

```bash
# 1. 克隆项目
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 使用 Python 直接运行
python3 -m cli.main --help
```

---

## 🚀 安装后使用

### 全局命令方式（推荐）

安装完成后，可以使用全局命令：

```bash
# 查看帮助
ai-pdf --help

# 查看版本
ai-pdf --version

# 查看所有命令
ai-pdf --help
```

---

### 常用命令示例

#### 1. 提取文本

```bash
# 提取整个文档的文本
ai-pdf text document.pdf -o output.txt

# 指定页面范围
ai-pdf text document.pdf --pages 1-5 -o output.txt

# 指定特定页面
ai-pdf text document.pdf --pages 1,3,5 -o output.txt
```

#### 2. 转换格式

```bash
# PDF → Markdown
ai-pdf to-markdown document.pdf -o output.md

# PDF → HTML
ai-pdf to-html document.pdf -o output.html

# PDF → JSON
ai-pdf to-json document.pdf -o output.json

# PDF → CSV（表格）
ai-pdf to-csv report.pdf -o tables.csv

# PDF → EPUB（电子书）
ai-pdf to-epub book.pdf -o book.epub

# PDF → 图片
ai-pdf to-image document.pdf --output-dir ./images
```

#### 3. 提取内容

```bash
# 提取表格
ai-pdf tables report.pdf -o tables.json

# 提取图片
ai-pdf images document.pdf --extract-dir ./images

# 提取元数据
ai-pdf metadata document.pdf -o metadata.json

# 提取结构（目录、书签）
ai-pdf structure document.pdf -o structure.json
```

#### 4. 插件管理

```bash
# 列出所有插件
ai-pdf plugin list

# 查看插件信息
ai-pdf plugin info text_reader

# 检查插件依赖
ai-pdf plugin check text_reader
```

---

## 🔧 配置选项

### 查看命令帮助

每个命令都有详细的帮助信息：

```bash
# 查看主帮助
ai-pdf --help

# 查看特定命令帮助
ai-pdf text --help
ai-pdf to-markdown --help
ai-pdf plugin --help
```

### 常用选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `-o, --output` | 输出文件路径 | `-o output.txt` |
| `--pages` | 页面范围 | `--pages 1-5` |
| `--format` | 输出格式 | `--format json` |
| `--extract-dir` | 提取目录 | `--extract-dir ./images` |
| `--structured` | 结构化输出 | `--structured` |

---

## 📊 完整命令列表

### 读取命令

```bash
ai-pdf text <pdf_path> [OPTIONS]          # 提取文本
ai-pdf tables <pdf_path> [OPTIONS]        # 提取表格
ai-pdf images <pdf_path> [OPTIONS]        # 提取图片
ai-pdf metadata <pdf_path> [OPTIONS]      # 提取元数据
ai-pdf structure <pdf_path> [OPTIONS]     # 提取结构
```

### 转换命令

```bash
ai-pdf to-markdown <pdf_path> [OPTIONS]  # PDF → Markdown
ai-pdf to-html <pdf_path> [OPTIONS]     # PDF → HTML
ai-pdf to-json <pdf_path> [OPTIONS]      # PDF → JSON
ai-pdf to-c-csv <pdf_path> [OPTIONS]     # PDF → CSV
ai-pdf to-image <pdf_path> [OPTIONS]     # PDF → 图片
ai-pdf to-epub <pdf_path> [OPTIONS]      # PDF → EPUB
```

### 管理命令

```bash
ai-pdf plugin [COMMAND] [OPTIONS]        # 插件管理
```

---

## 🌐 部署到生产环境

### 使用 Docker 部署

**创建 Dockerfile：**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 安装工具
RUN pip install -e .

# 设置工作目录
WORKDIR /data

# 默认命令
CMD ["ai-pdf", "--help"]
```

**构建和运行：**
```bash
# 构建镜像
docker build -t ai-pdf-agent .

# 运行容器
docker run -v $(pwd)/data:/data ai-pdf-agent ai-pdf text /data/document.pdf -o /data/output.txt
```

---

### 使用 systemd 部署（Linux）

**创建服务文件：**
```ini
[Unit]
Description=AI PDF Agent Service
After=network.target

[Service]
Type=simple
User=pdfagent
WorkingDirectory=/opt/ai-pdf-agent
ExecStart=/usr/local/bin/ai-pdf --help
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**启用服务：**
```bash
# 复制服务文件
sudo cp ai-pdf-agent.service /etc/systemd/system/

# 重载 systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable ai-pdf-agent

# 启动服务
sudo systemctl start ai-pdf-agent
```

---

## 🔍 故障排除

### 问题 1：命令未找到

**错误：**
```
bash: ai-pdf: command not found
```

**解决方案：**
```bash
# 确保已安装
pip list | grep ai-pdf-agent

# 使用完整路径
~/.local/bin/ai-pdf --help

# 或重新安装
pip install --user ai-pdf-agent
```

---

### 问题 2：权限错误

**错误：**
```
Permission denied: 'output.txt'
```

**解决方案：**
```bash
# 检查输出目录权限
ls -ra

# 使用有写权限的目录
ai-pdf text document.pdf -o /tmp/output.txt
```

---

### 问题 3：依赖冲突

**错误：**
```
ERROR: pip's dependency resolver does not currently take into account...
```

**解决方案：**
```bash
# 使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📚 更多文档

- **快速开始：** [QUICKSTART.md](QUICKSTART.md)
- **命令参考：** [COMMANDS.md](COMMANDS.md)
- **使用示例：** [CLI_EXAMPLES.md](CLI_EXAMPLES.md)
- **插件开发：** [PLUGIN_DEV.md](PLUGIN_DEV.md)

---

## 🤝 获取帮助

- **GitHub：** https://github.com/qqqzhch/ai-pdf-agent
- **Issues：** https://github.com/qqqzhch/ai-pdf-agent/issues
- **文档：** https://docs.ai-pdf-agent.com

---

**生成时间：** 2026-03-04 17:40
**项目版本：** v0.1.0
