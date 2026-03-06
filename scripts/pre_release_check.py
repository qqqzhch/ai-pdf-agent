# scripts/pre_release_check.py
"""
发布前检查脚本

在发布到 GitHub 前，运行此脚本验证：
1. 入口点是否可用
2. 版本命令是否工作
3. 帮助命令是否工作
4. 读取功能是否正常
5. 转换功能是否正常

所有检查通过才能发布。
"""
import subprocess
import sys
import os


def print_success(message):
    """打印成功消息"""
    print(f"✅ {message}")


def print_error(message):
    """打印错误消息"""
    print(f"❌ {message}")


def print_info(message):
    """打印信息消息"""
    print(f"ℹ️  {message}")


def print_header(message):
    """打印标题"""
    print()
    print("=" * 80)
    print(f"{message}")
    print("=" * 80)


def check_entry_point():
    """检查入口点是否正确"""
    print_header("检查 1：入口点")
    
    try:
        result = subprocess.run(
            ["python3", "-m", "ai_pdf_agent.cli.cli", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print_error("入口点不可用")
            print(f"错误信息：{result.stderr}")
            return False
        
        if "1.0.0" not in result.stdout:
            print_error("版本信息不正确")
            print(f"输出：{result.stdout}")
            return False
        
        print_success("入口点检查通过")
        print(f"版本：{result.stdout.strip()}")
        return True
        
    except Exception as e:
        print_error(f"入口点检查失败：{str(e)}")
        return False


def check_help_command():
    """检查帮助命令是否工作"""
    print_header("检查 2：帮助命令")
    
    try:
        result = subprocess.run(
            ["python3", "-m", "ai_pdf_agent.cli.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print_error("帮助命令失败")
            print(f"错误信息：{result.stderr}")
            return False
        
        if "Simple PDF" not in result.stdout:
            print_error("帮助信息不正确")
            print(f"输出：{result.stdout[:200]}")
            return False
        
        if "read" not in result.stdout or "convert" not in result.stdout:
            print_error("命令列表不完整")
            print(f"输出：{result.stdout[:200]}")
            return False
        
        print_success("帮助命令检查通过")
        print_info("可用命令：read, convert")
        return True
        
    except Exception as e:
        print_error(f"帮助命令检查失败：{str(e)}")
        return False


def check_read_functionality():
    """检查读取功能是否工作"""
    print_header("检查 3：读取功能")
    
    pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
    
    # 检查测试文件是否存在
    if not os.path.exists(pdf_path):
        print_error(f"测试文件不存在：{pdf_path}")
        print_info("请确保测试 PDF 文件可用")
        return False
    
    print_info(f"使用测试文件：{pdf_path}")
    
    try:
        result = subprocess.run(
            ["python3", "-m", "ai_pdf_agent.cli.cli", "read", pdf_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print_error("读取命令失败")
            print(f"错误信息：{result.stderr}")
            return False
        
        if len(result.stdout) < 100:
            print_error("读取内容太少")
            print(f"输出长度：{len(result.stdout)}")
            print(f"输出：{result.stdout}")
            return False
        
        if "Nginx" not in result.stdout:
            print_error("读取内容不正确")
            print(f"输出预览：{result.stdout[:200]}")
            return False
        
        print_success("读取功能检查通过")
        print_info(f"读取了 {len(result.stdout)} 字节")
        print_info("内容预览：")
        print(result.stdout[:100])
        return True
        
    except Exception as e:
        print_error(f"读取功能检查失败：{str(e)}")
        return False


def check_convert_functionality():
    """检查转换功能是否工作"""
    print_header("检查 4：转换功能")
    
    pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
    formats = ['markdown', 'json', 'html', 'text']
    
    # 检查测试文件是否存在
    if not os.path.exists(pdf_path):
        print_error(f"测试文件不存在：{pdf_path}")
        print_info("请确保测试 PDF 文件可用")
        return False
    
    print_info(f"使用测试文件：{pdf_path}")
    print_info(f"测试格式：{', '.join(formats)}")
    
    success_count = 0
    
    for format in formats:
        try:
            result = subprocess.run(
                ["python3", "-m", "ai_pdf_agent.cli.cli", "convert", pdf_path,
                 "--format", format],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print_error(f"{format} 转换失败")
                print(f"错误信息：{result.stderr}")
                continue
            
            if len(result.stdout) < 100:
                print_error(f"{format} 转换内容太少")
                print(f"输出长度：{len(result.stdout)}")
                continue
            
            # 验证内容
            if format == 'json':
                if '"file"' not in result.stdout or '"pages"' not in result.stdout:
                    print_error(f"{format} 转换内容不正确")
                    continue
            
            success_count += 1
            print_success(f"{format} 转换成功（{len(result.stdout)} 字节）")
            
        except Exception as e:
            print_error(f"{format} 转换检查失败：{str(e)}")
    
    if success_count == len(formats):
        print_success("所有格式转换检查通过")
        return True
    else:
        print_error(f"只有 {success_count}/{len(formats)} 个格式转换通过")
        return False


def run_all_checks():
    """运行所有检查"""
    print()
    print("🔍 Simple PDF 预发布检查")
    print("=" * 80)
    
    checks = [
        check_entry_point(),
        check_help_command(),
        check_read_functionality(),
        check_convert_functionality(),
    ]
    
    print_header("检查总结")
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"通过：{passed}/{total}")
    
    if passed == total:
        print_success("所有检查通过！可以发布！")
        return True
    else:
        print_error(f"{total - passed} 个检查失败")
        print_info("请修复问题后重新运行")
        return False


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
