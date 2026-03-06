# 多阶段构建
FROM python:3.11-slim as base

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
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
RUN useradd -m -u 1000 aiuser && \
    chown -R aiuser:aiuser /app
USER aiuser

# 暴露端口（API）
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import ai_pdf_agent; print('OK')" || exit 1

# 默认命令
CMD ["ai", "--help"]
