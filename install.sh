#!/bin/bash
# Simple PDF 安装脚本

echo "🚀 开始安装 Simple PDF..."

# 检查 Python 版本
echo "📦 Python 版本: $(python3 --version)"

# 进入项目目录
cd "$(dirname "$0")"

# 创建虚拟环境
echo "🔧 创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "✅ 激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt

# 安装包（可编辑模式）
echo "📦 安装 Simple PDF..."
pip install -e .

# 验证安装
echo "🔍 验证安装..."
which simple-pdf
simple-pdf --version
simple-pdf --help

echo ""
echo "✅ 安装完成！"
echo ""
echo "使用方法："
echo "  source venv/bin/activate"
echo "  simple-pdf read document.pdf -o output.txt"
echo "  simple-pdf convert document.pdf --format markdown -o output.md"
