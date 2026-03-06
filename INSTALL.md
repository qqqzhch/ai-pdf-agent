# AI PDF Agent - 安装指南

> **版本：** 1.0.0
> **支持平台：** Linux, macOS, Windows
> **Python 版本：** 3.8+

---

## 📋 安装前要求

### 方案 A：Python 环境安装

**要求：**
- Python 3.8+
- pip（Python 包管理器）
- git（可选，用于克隆源码）

### 方案 B：Docker 部署

**要求：**
- Docker 20.10+
- Docker Compose 1.29+（可选）

---

## 🚀 安装方法

### 方法 1：使用 pip 安装（推荐）

```bash
# 安装 AI PDF Agent
pip install ai-pdf-agent

# 验证安装
ai --version
```

### 方法 2：从源码安装

```bash
# 克隆源码
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent

# 安装
pip install -e .

# 验证安装
ai --version
```

### 方法 3：使用 Docker

```bash
# 拉取镜像
docker pull qqqzhch/ai-pdf-agent:latest

# 验证安装
docker run --rm qqqzhch/ai-pdf-agent:latest --version
```

---

## 🔧 验证安装

### Python 环境

```bash
# 查看版本
ai --version

# 查看帮助
ai --help

# 测试读取功能
ai read /path/to/document.pdf
```

### Docker 环境

```bash
# 测试运行
docker run -v $(pwd):/app/data qqqzhch/ai-pdf-agent:latest read /app/data/document.pdf

# 使用 docker-compose
docker-compose run ai-pdf-agent read /app/data/document.pdf
```

---

## 📝 使用示例

### 读取 PDF

```bash
# Python 环境
ai read document.pdf

# 输出到文件
ai read document.pdf -o output.md

# Docker 环境
docker run -v $(pwd):/app/data qqqzhch/ai-pdf-agent:latest read /app/data/document.pdf -o /app/data/output.md
```

### 转换 PDF

```bash
# 转换为 Markdown
ai convert document.pdf --format markdown

# 转换为 HTML
ai convert document.pdf --format html

# 转换为 JSON
ai convert document.pdf --format json

# 输出到文件
ai convert document.pdf --format markdown -o output.md

# Docker 环境
docker run -v $(pwd):/app/data qqqzhch/ai-pdf-agent:latest convert /app/data/document.pdf --format markdown
```

### 批量处理

```bash
# Python 环境
for file in *.pdf; do
    ai convert "$file" --format markdown -o "${file%.pdf}.md"
done

# Docker 环境
docker run -v $(pwd):/app/data qqqzhch/ai-pdf-agent:latest bash -c \
    'for file in /app/data/*.pdf; do ai convert "$file" --format markdown -o "${file%.pdf}.md"; done'
```

---

## 🐳 Docker 使用

### 基本用法

```bash
# 运行容器
docker run qqqzhch/ai-pdf-agent:latest read document.pdf

# 交互式运行
docker run -it qqqzhch/ai-pdf-agent:latest bash

# 挂载目录
docker run -v $(pwd):/app/data qqqzhch/ai-pdf-agent:latest read /app/data/document.pdf

# 指定工作目录
docker run -w /app/data qqqzhch/ai-pdf-agent:latest read document.pdf
```

### Docker Compose

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 执行命令
docker-compose run ai-pdf-agent read document.pdf
```

### 数据卷

```bash
# 创建数据卷
docker volume create ai-pdf-agent-data

# 使用数据卷
docker run -v ai-pdf-agent-data:/app/data qqqzhch/ai-pdf-agent:latest read /app/data/document.pdf

# 查看数据卷
docker volume inspect ai-pdf-agent-data
```

---

## 🔍 故障排查

### 问题 1：安装失败

**错误：** `ModuleNotFoundError: No module named 'click'`

**解决：**
```bash
pip install click>=8.0.0
```

### 问题 2：权限错误

**错误：** `Permission denied`

**解决：**
```bash
# 使用虚拟环境
python -m venv venv
source venv/bin/activate
pip install ai-pdf-agent
```

### 问题 3：Docker 构建失败

**错误：** `Failed to build image`

**解决：**
```bash
# 清理缓存
docker system prune -a

# 重新构建
docker build --no-cache -t ai-pdf-agent .
```

### 问题 4：Python 版本不兼容

**错误：** `Python 3.7 is not supported`

**解决：**
```bash
# 升级 Python 到 3.8+
python3.8 -m pip install ai-pdf-agent
```

---

## 📚 卸级安装

### 开发环境

```bash
# 克隆源码
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e .[dev]

# 运行测试
pytest

# 代码格式化
black .

# 类型检查
mypy .
```

### 生产环境

```bash
# 使用虚拟环境
python -m venv venv
source venv/bin/activate

# 安装
pip install ai-pdf-agent

# 验证
ai --version
```

---

## 🎯 配置选项

### 环境变量

```bash
# 日志级别
export AI_PDF_LOG_LEVEL=DEBUG

# 缓存目录
export AI_PDF_CACHE_DIR=/path/to/cache

# 最大并行任务
export AI_PDF_MAX_PARALLEL=3

# Docker 环境
docker run -e AI_PDF_LOG_LEVEL=DEBUG qqqzhch/ai-pdf-agent:latest read document.pdf
```

### 配置文件

```bash
# 创建配置文件
mkdir -p ~/.config/ai-pdf-agent

# 配置示例
cat > ~/.config/ai-pdf-agent/config.json << EOF
{
  "log_level": "INFO",
  "cache_dir": "/tmp/ai-pdf-cache",
  "max_parallel_tasks": 3,
  "default_format": Markdown"
}
EOF
```

---

## 📚 更新和卸载

### 更新

```bash
# 检查更新
pip list --outdated | grep ai-pdf-agent

# 更新到最新版本
pip install --upgrade ai-pdf-agent

# Docker 更新
docker pull qqqzhch/ai-pdf-agent:latest
```

### 卸载

```bash
# 卸载
pip uninstall ai-pdf-agent

# 删除虚拟环境
rm -rf venv

# Docker 清理
docker rmi qqqzhch/ai-pdf-agent:latest
docker volume rm ai-pdf-agent-data
```

---

## 📞 获取帮助

### 命令行帮助

```bash
# 查看所有命令
ai --help

# 查看具体命令帮助
ai read --help
ai convert --help
```

### 文档

- **在线文档：** https://github.com/qqqzhch/ai-pdf-agent#readme
- **API 文档：** https://github.com/qqqzhch/ai-pdf-agent/docs
- **示例代码：** https://github.com/qqqzhch/ai-pdf-agent/examples

---

## 🎉 下一步

- 查看 [使用示例](USAGE.md)
- 了解 [开发指南](DEVELOPMENT.md)
- 加入 [社区讨论](https://github.com/qqqzhch/ai-pdf-agent/discussions)

---

**创建日期：** 2026-03-06
**版本：** 1.0.0
