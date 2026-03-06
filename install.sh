#!/bin/bash
# Simple PDF Installer - Windows 批处理版本（Linux/macOS）

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# 函数：显示帮助
show_help() {
    echo -e "${CYAN}Simple PDF Installer - Linux/macOS 版本${NC}"
    echo ""
    echo "用法: ./install.sh [选项]"
    echo ""
    echo "选项:"
    echo "  --help     显示帮助信息"
    echo "  --reinstall 卸载并重新安装"
    echo "  --test     安装后测试"
    echo ""
    echo "示例:"
    echo "  ./install.sh           # 安装 Simple PDF"
    echo "  ./install.sh --reinstall  # 重新安装"
    echo "  ./install.sh --test     # 安装并测试"
}

# 函数：检查 Python
check_python() {
    echo -e "${YELLOW}📦 检查 Python...${NC}"
    if command -v python3 &> /dev/null; then
        local version=$(python3 --version)
        echo -e "${GREEN}✅ Python 已安装: $version${NC}"
    else
        echo -e "${RED}❌ Python 未安装，请先安装 Python 3.8+${NC}"
        exit 1
    fi
}

# 函数：检查 pip
check_pip() {
    echo -e "${YELLOW}📦 检查 pip...${NC}"
    if command -v pip3 &> /dev/null; then
        local version=$(pip3 --version)
        echo -e "${GREEN}✅ pip 已安装: $version${NC}"
    else
        echo -e "${RED}❌ pip 未安装${NC}"
        exit 1
    fi
}

# 函数：安装包
install_package() {
    local project_dir=$1
    local reinstall=$2

    echo -e "${CYAN}🚀 开始安装 Simple PDF...${NC}"
    echo ""

    if [ "$reinstall" = true ]; then
        echo -e "${YELLOW}🗑️  卸载旧版本...${NC}"
        pip3 uninstall -y simple-pdf 2>/dev/null || true
    fi

    echo -e "${YELLOW}📦 升级 pip...${NC}"
    pip3 install --upgrade pip 2>/dev/null
    echo -e "${GREEN}✅ pip 升级完成${NC}"
    echo ""

    echo -e "${YELLOW}📦 安装 Simple PDF...${NC}"
    cd "$project_dir"
    pip3 install -e . 2>&1 | while IFS= read -r line; do
        echo "  $line"
    done

    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Simple PDF 安装成功！${NC}"
    else
        echo ""
        echo -e "${RED}❌ Simple PDF 安装失败！${NC}"
        exit 1
    fi
}

# 函数：测试安装
test_installation() {
    echo -e "${CYAN}🧪 测试安装...${NC}"
    echo ""

    echo -e "${YELLOW}1️⃣  测试命令: simple-pdf --version${NC}"
    if command -v simple-pdf &> /dev/null; then
        local version=$(simple-pdf --version 2>&1)
        echo -e "${GREEN}✅ 命令工作正常${NC}"
        echo -e "   输出: $version${NC}"
    else
        echo -e "${YELLOW}⚠️  命令未找到，尝试其他方法...${NC}"
        echo -e "${YELLOW}2️⃣  测试模块: python3 -m ai_pdf_agent.cli.cli --version${NC}"
        if python3 -m ai_pdf_agent.cli.cli --version &> /dev/null; then
            local version=$(python3 -m ai_pdf_agent.cli.cli --version 2>&1)
            echo -e "${GREEN}✅ 模块执行成功${NC}"
            echo -e "   输出: $version${NC}"
        else
            echo -e "${RED}❌ 模块执行失败${NC}"
            echo ""
            echo -e "${YELLOW}💡 可能需要创建虚拟环境：${NC}"
            echo -e "   python3 -m venv venv${NC}"
            echo -e "   source venv/bin/activate${NC}"
            echo -e "   pip install -e .${NC}"
            exit 1
        fi
    fi

    echo ""
    echo -e "${YELLOW}2️⃣  测试命令: simple-pdf --help${NC}"
    if command -v simple-pdf &> /dev/null; then
        simple-pdf --help &> /dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 帮助信息显示正常${NC}"
        else
            echo -e "${YELLOW}⚠️  模块方式测试...${NC}"
            python3 -m ai_pdf_agent.cli.cli --help &> /dev/null
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ 帮助信息显示正常（模块方式）${NC}"
            else
                echo -e "${RED}❌ 帮助信息显示失败${NC}"
                exit 1
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  模块方式方式测试...${NC}"
        python3 -m ai_pdf_agent.cli.cli --help &> /dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 帮助信息显示正常（模块方式）${NC}"
        else
            echo -e "${RED}❌ 帮助信息显示失败${NC}"
            exit 1
        fi
    fi

    echo ""
    echo -e "${GREEN}🎉 测试完成！${NC}"
}

# 函数：显示使用方法
show_usage() {
    echo -e "${CYAN}📋 使用方法：${NC}"
    echo ""
    echo -e "${YELLOW}激活虚拟环境（如果需要）：${NC}"
    echo "  source venv/bin/activate"
    echo ""
    echo -e "${YELLOW}使用命令：${NC}"
    if command -v simple-pdf &> /dev/null; then
        echo "  simple-pdf --version           # 显示版本"
        echo "  simple-pdf --help              # 显示帮助"
        echo "  simple-pdf read document.pdf -o output.txt    # 读取 PDF"
        echo "  simple-pdf convert document.pdf --format markdown -o output.md    # 转换为 Markdown"
    else
        echo "  python3 -m ai_pdf_agent.cli.cli --version           # 显示版本"
        echo "  python3 -m ai_pdf_agent.cli.cli --help              # 显示帮助"
        echo "  python3 -m ai_pdf_agent.cli.cli read document.pdf -o output.txt    # 读取 PDF"
        echo "  python3 -m ai_pdf_agent.cli.cli convert document.pdf --format markdown -o output.md    # 转换为 Markdown"
    fi
}

# 主函数
main() {
    local reinstall=false
    local run_test=false

    # 解析参数
    for arg in "$@"; do
        case $arg in
            --help)
                show_help
                exit 0
                ;;
            --reinstall)
                reinstall=true
                ;;
            --test)
                run_test=true
                ;;
            *)
                echo -e "${RED}❌ 未知选项: $arg${NC}"
                echo -e "使用 --help 查看帮助"
                exit 1
                ;;
        esac
    done

    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}Simple PDF Installer${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""

    echo -e "${GRAY}📁 项目目录: $(pwd)${NC}"
    echo ""

    # 检查前提条件
    check_python
    check_pip

    # 安装包
    install_package "$(pwd)" "$reinstall"

    # 测试安装
    if [ "$run_test" = true ]; then
        test_installation
    fi

    # 显示使用方法
    show_usage

    echo ""
    echo -e "${GREEN}✅ 安装完成！${NC}"
    echo ""
}

# 运行主函数
main "$@"
