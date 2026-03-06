#!/bin/bash
# Simple PDF Installer - Linux/macOS 版本（支持多 pip 镜像源）

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# 镜像源配置
PIP_MIRRORS=(
    "default|https://pypi.org/simple"
    "tuna|https://pypi.tuna.tsinghua.edu.cn/simple"
    "tsinghua|https://pypi.tuna.tsinghua.edu.cn/simple"
    "aliyun|https://mirrors.aliyun.com/pypi/simple"
    "ustc|https://mirrors.ustc.edu.cn/pypi/simple"
    "chima|https://pypi.mirrors.china.edu/simple"
    "pypi|https://pypi.org/simple"
)

# 函数：显示帮助
show_help() {
    echo -e "${CYAN}Simple PDF Installer - Linux/macOS 版本${NC}"
    echo ""
    echo "用法: ./install.sh [选项]"
    echo ""
    echo "选项:"
    echo "  --help             显示帮助信息"
    echo "  --reinstall        卸载并重新安装"
    echo "  --test             安装后测试"
    echo "  --mirror <name>    指定 pip 镜像源（default, tuna, tsinghua, aliyun, ustc, chima, pypi）"
    echo "  --mirror-index <url> 指定自定义镜像源 URL"
    echo ""
    echo "示例:"
    echo "  ./install.sh                           # 安装 Simple PDF"
    echo "  ./install.sh --reinstall                 # 重新安装"
    echo "  ./install.sh --test                      # 安装并测试"
    echo "  ./install.sh --mirror tuna                # 使用清华大学镜像"
    echo "  ./install.sh --mirror-index https://pypi.tuna.tsing. edu.cn/simple"
}

# 函数：设置 pip 镜像源
set_pip_mirror() {
    local mirror_name=$1
    
    echo -e "${YELLOW}🔄 设置 pip 镜像源...${NC}"
    
    if [ "$mirror_name" = "default" ]; then
        # 清除环境变量，使用默认源
        unset PIP_INDEX_URL
        unset PIP_INDEX
        echo -e "${GREEN}✅ 使用默认 pip 镜像源${NC}"
    else
        # 查找镜像源
        local mirror_url=""
        for mirror in "${PIP_MIRRORS[@]}"; do
            IFS='|' read -r name url <<< "$mirror"
            if [ "$name" = "$mirror_name" ]; then
                mirror_url=$url
                break
            fi
        done
        
        if [ -z "$mirror_url" ]; then
            echo -e "${RED}❌ 未知镜像源：$mirror_name${NC}"
            echo -e "${GRAY}可用源：default, tuna, tsinghua, aliyun, ustc, chima, pypi${NC}"
            return 1
        fi
        
        export PIP_INDEX_URL="$mirror_url"
        echo -e "${GREEN}✅ 使用镜镜像源：$mirror_name${NC}"
        echo -e "   URL: $mirror_url${NC}"
    fi
    
    echo ""
}

# 函数：检查 Python
check_python() {
    echo -e "${YELLOW}📦 检查 Python...${NC}"
    if command -v python3 &> /dev/null; then
        local version=$(python3 --version 2>&1)
        echo -e "${GREEN}✅ Python 已安装: $version${NC}"
    else
        echo -e "${RED}❌ Python 未安装，请先安装 Python 3.8+${NC}"
        exit 1
    fi
}

# 函数：检查 pip
check_pip() {
    echo -e "${YELLOW}📦 检查 pip...${NC}"
    
    # 显示当前镜像源
    if [ -n "$PIP_INDEX_URL" ]; then
        echo -e "${CYAN}📡 当前 pip 镜像源：$PIP_INDEX_URL${NC}"
    fi
    
    if command -v pip3 &> /dev/null; then
        local version=$(pip3 --version 2>&1)
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
        pip3 uninstall -y simple-pdf 2>&1 | tail -1 || true
    fi
    
    echo -e "${YELLOW}📦 升级 pip...${NC}"
    pip3 install --upgrade pip 2>&1 | tail -1 || true
    echo -e "${GREEN}✅ pip 升级完成${NC}"
    echo ""
    
    echo -e "${YELLOW}📦 安装 Simple PDF...${NC}"
    cd "$project_dir"
    
    if pip3 install -e . 2>&1; then
        echo ""
        echo -e "${GREEN}✅ Simple PDF 安装成功！${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}❌ Simple PDF 安装失败！${NC}"
        return 1
    fi
}

# 函数：测试安装
test_installation() {
    echo -e "${CYAN}🧪 测试安装...${NC}"
    echo ""
    
    # 测试命令
    echo -e "${YELLOW}1️⃣ 测试命令: simple-pdf --version${NC}"
    if command -v simple-pdf &> /dev/null; then
        local result=$(simple-pdf --version 2>&1)
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 命令工作正常${NC}"
            echo -e "   输出: $result${NC}"
        else
            echo -e "${RED}❌ 命令执行失败${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  命令未找到，尝试模块直接执行...${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}2️⃣ 测试命令: simple-pdf --help${NC}"
    if command -v simple-pdf &> /dev/null; then
        local result=$(simple-pdf --help 2>&1 | head -5)
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 帮助信息显示正常${NC}"
            echo -e "   输出预览:"
            echo "$result" | sed 's/^/   /'
        else
            echo -e "${RED}❌ 帮助信息显示失败${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  模块方式测试...${NC}"
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
    echo ""
    echo -e "${YELLOW}可用镜像源：${NC}"
    for mirror in "${PIP_MIRRORS[@]}"; do
        IFS='|' read -r name url <<< "$mirror"
        echo -e "  - $name ($url)${NC}"
    done
}

# 主函数
main() {
    local reinstall=false
    local run_test=false
    local mirror_name=""
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
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
            --mirror)
                shift
                mirror_name="$1"
                ;;
            --mirror-index)
                shift
                export PIP_INDEX_URL="$1"
                ;;
            *)
                echo -e "${RED}❌ 未知选项: $1${NC}"
                echo -e "使用 --help 查看帮助"
                exit 1
                ;;
        esac
        shift
    done
    
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}Simple PDF Installer${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    
    echo -e "${GRAY}📁 项目目录: $(pwd)${NC}"
    echo ""
    
    # 设置镜像源
    if [ -n "$mirror_name" ]; then
        set_pip_mirror "$mirror_name"
    fi
    
    # 检查前提条件
    check_python
    check_pip
    
    # 安装包
    if ! install_package "$(pwd)" "$reinstall"; then
        echo -e "${RED}❌ 安装失败，请检查错误信息${NC}"
        exit 1
    fi
    
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
