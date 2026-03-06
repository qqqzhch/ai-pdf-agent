# AI PDF Agent - 部署方案

> **目标：** 通过源码部署
> **要求：** 有 Python 环境的 Agent 可以直接用，没有 Python 环境的 Agent 用 Docker
> **版本：** V2.0
> **创建日期：** 2026-03-06

---

## 🎯 部署目标

### 核心需求

1. **源码部署**
   - ✅ 不增加新功能
   - ✅ 通过 Git 源码部署
   - ✅ 支持 pip 安装

2. **环境适配**
   - ✅ 有 Python 环境：直接使用
   - ✅ 无 Python 环境：使用 Docker
   - ✅ CLI 工具可用

3. **多平台支持**
   - ✅ Linux
   - ✅ macOS
   - ✅ Windows

---

## 📦 部署组件

### 1. 核心 Python 包

**文件结构：**
```
ai-pdf-agent/
├── setup.py              # 安装配置
├── setup.cfg             # 元数据
├── pyproject.toml         # 现代 Python 项目配置
├── ai_pdf_agent/          # 包目录
│   ├── __init__.py
│   ├── core/              # 核心功能
│   ├── cli/               # CLI 工具
│   ├── api/               # API 接口
│   └── version.py          # 版本信息
├── requirements.txt        # 依赖
├── requirements-dev.txt    # 开发依赖
└── README.md              # 文档
```

### 2. Docker 镜像

**Dockerfile：**
```dockerfile
# 多阶段构建
FROM python:3.11-slim as base

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    build-essential \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 复制应用代码
WORKDIR /app
COPY . /app/

# 安装应用
RUN pip install -e .

# 创建非 root 用户
RUN useradd -m -u 1000 aiuser && \\
    chown -R aiuser:aiuser /app
USER aiuser

# 暴露端口（如果需要）
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import ai_pdf_agent; print('OK')" || exit 1

# 默认命令
CMD ["ai-pdf-agent", "--help"]
```

**docker-compose.yml：**
```yaml
version: '3.8'

services:
  ai-pdf-agent:
    build: .
    container_name: ai-pdf-agent
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - PYTHONUNBUFFERED=1
      - AI_PDF_LOG_LEVEL=INFO
    ports:
      - "8000:8000"  # API 端口
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import ai_pdf_agent; print('OK')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
```

### 3. CLI 工具

**入口点：** `ai` 命令

```python
# ai_pdf_agent/cli/main.py
import click

@click.group()
def cli():
    """AI PDF Agent - 智能 PDF 处理工具"""
    pass

@cli.command()
def read(pdf_path, output=None):
    """读取 PDF 内容"""
    # 实现

@cli.command()
def convert(pdf_path, format):
    """转换 PDF 格式"""
    # 实现

@cli.command()
def version():
    """显示版本"""
    click.echo("AI PDF Agent v1.0.0")
```

---

## 🔧 部署步骤

### 方案 A：有 Python 环境

**步骤 1：克隆源码**
```bash
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent
```

**步骤 2：创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  on Windows: venv\\Scripts\\activate
```

**步骤 3：安装依赖**
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

**步骤 4：验证安装**
```bash
ai-pdf-agent --version
ai-pdf-agent --help
```

**步骤 5：运行测试**
```bash
pytest tests/
```

---

### 方案 B：使用 Docker

**步骤 1：克隆源码**
```bash
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent
```

**步骤 2：构建 Docker 镜像**
```bash
docker build -t ai-pdf-agent:latest .
```

**步骤 3：运行容器**
```bash
# 基本运行
docker run --rm ai-pdf-agent:latest --version

# 使用 docker-compose
docker-compose up -d

# 挂载卷
docker run -v $(pwd)/data:/app/data ai-pdf-agent:latest read input.pdf -o output.md
```

**步骤 4：进入容器**
```bash
docker exec -it ai-pdf-agent bash
```

---

## 📝 需要创建的文件

### 1. setup.py

```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-pdf-agent",
    version="1.0.0",
    author="AI Team",
    description="AI PDF Agent - 智能 PDF 处理工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qqqzhch/ai-pdf-agent",
    packages=find_packages(exclude=["tests*", "docs*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pymupdf>=1.23.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ai=ai_pdf_agent.cli.main:cli",
        ],
    },
)
```

### 2. requirements.txt

```
click>=8.0.0
pymupdf>=1.23.0
pydantic>=2.0.0
requests>=2.28.0
```

### 3. pyproject.toml

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ai-pdf-agent"
version = "1.0.0"
description = "AI PDF Agent - 智能 PDF 处理工具"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
keywords = ["pdf", "ai", "document", "converter"]
authors = [
    {name = "AI Team", email = "team@example.com"}
]

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Software Development",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

dependencies = [
    "click>=8.0.0",
    "pymupdf>=1.23.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/qqqzhch/ai-pdf-agent"
Documentation = "https://github.com/qqqzhch/ai-pdf-agent#readme"
Repository = "https://github.com/qqqzhch/ai-pdf-agent.git"

[project.scripts]
ai = "ai_pdf_agent.cli.main:cli"

[tool.setuptools]
packages = ["ai_pdf_agent"]
```

---

## 🚀 部署检查清单

### Python 环境部署

- [ ] Python 3.8+ 已安装
- [ ] 虚拟环境已创建
- [ ] 依赖已安装
- [ ] 包已安装（pip install -e .）
- [ ] CLI 命令可用（ai --version）
- [ ] 测试通过
- [ ] 文档可访问

### Docker 部署

- [ ] Docker 已安装
- [ ] Docker 镜像已构建
- [ ] 容器可以运行
- [ ] 卷挂载正常
- [ ] 环境变量配置正确
- [ ] 健康检查通过
- [ ] CLI 命令可用

---

## 📊 使用示例

### Python 环境

```bash
# 读取 PDF
ai read input.pdf -o output.md

# 转换 PDF
ai convert input.pdf --format markdown

# 查看版本
ai --version

# 查看帮助
ai --help
```

### Docker 环境

```bash
# 读取 PDF
docker run -v $(pwd):/data ai-pdf-agent:latest read /data/input.pdf -o /data/output.md

# 转换 PDF
docker run -v $(pwd):/data ai-pdf-agent:latest convert /data/input.pdf --format markdown

# 交互式运行
docker run -it -v $(pwd):/data ai-pdf-agent:latest bash

# 使用 docker-compose
docker-compose run ai-pdf-agent read input.pdf -o output.md
```

---

## 🔧 实施优先级

### P0 - 必须（立即实施）
1. 创建 `setup.py`
2. 创建 `requirements.txt`
3. 创建 `pyproject.toml`
4. 创建 `Dockerfile`
5. 创建 `docker-compose.yml`
6. 创建 CLI 入口点

### P1 - 重要（尽快实施）
1. 添加版本信息
2. 创建 README.md
3. 添加安装文档
4. 添加使用示例

### P2 - 可选（后续优化）
1. 添加 CI/CD 配置
2. 添加测试套件
3. 添加性能监控
4. 添加日志配置

---

## 🎓 总结

### 部署方案特点

✅ **源码部署**
- 通过 pip 安装
- 支持 Python 3.8+
- 跨平台支持

✅ **环境适配**
- 有 Python：直接使用
- 无 Python：Docker 部署
- CLI 工具可用

✅ **零依赖**
- 仅依赖 Python 标准库
- 第三方依赖最小化
- 易于安装和维护

---

**创建日期：** 2026-03-06
**版本：** V2.0
**状态：** 方案设计完成
