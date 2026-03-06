#!/bin/bash
# Simple PDF 诊断脚本

echo "🔍 === Simple PDF 诊断 ==="
echo ""

echo "1. 📦 Python 版本:"
python3 --version
echo ""

echo "2. 📦 Pip 版本:"
pip3 --version
echo ""

echo "3. 📁 当前工作目录:"
pwd
echo ""

echo "4. 🔧 PATH 环境变量:"
echo $PATH | tr ':' '\n' | head -10
echo ""

echo "5. 🔍 查找 simple-pdf 命令:"
which simple-pdf || echo "❌ 未找到 simple-pdf 命令"
echo ""

echo "6. 🔍 搜索文件系统中的 simple-pdf:"
find ~ -name "simple-pdf" -type f 2>/dev/null | head -5 || echo "❌ 未找到"
echo ""

echo "7. 📦 检查包是否安装:"
pip list | grep simple-pdf || echo "❌ 包未安装"
echo ""

echo "8. 🧪 测试 Python 导入:"
python3 -c "from ai_pdf_agent.cli.main import cli; print('✅ Import success')" 2>&1 || echo "❌ 导入失败"
echo ""

echo "9. 🧪 测试模块执行:"
python3 -m ai_pdf_agent.cli.main --version 2>&1 || echo "❌ 执行失败"
echo ""

echo "10. 📂 检查包结构:"
ls -la ai_pdf_agent/ 2>&1 | head -10
echo ""

echo "🔍 === 诊断完成 ==="
