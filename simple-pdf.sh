#!/bin/bash
# Simple PDF 快速启动脚本

echo "🚀 启动 Simple PDF..."

# 显示版本
python3 -m ai_pdf_agent.cli.main --version

# 显示帮助
echo ""
echo "📋 使用方法："
echo "  python3 -m ai_pdf_agent.cli.main read <pdf-path> [-o output]"
echo "  python3 -m ai_pdf_agent.cli.main convert <pdf-path> --format <format> [-o output]"
echo ""
echo "示例："
echo "  python3 -m ai_pdf_agent.cli.main read document.pdf -o output.txt"
echo "  python3 -m ai_pdf_agent.cli.main convert document.pdf --format markdown -o output.md"

# 显示完整帮助
echo ""
python3 -m ai_pdf_agent.cli.main --help
