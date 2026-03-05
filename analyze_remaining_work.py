"""
分析 AI PDF Agent 项目剩余工作
"""

import subprocess
from pathlib import Path


def check_test_coverage():
    """检查测试覆盖率"""
    print("=" * 60)
    print("🧪 检查测试覆盖率")
    print("=" * 60)
    
    result = subprocess.run(
        ["python3", "-m", "pytest", "tests/", "--cov=plugins", "--cov-report=term", "--cov-report=json"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if "coverage" in result.stdout.lower():
        print("✅ pytest-cov 已安装")
        print("\n覆盖率报告：")
        print(result.stdout[-500:])
    else:
        print("⚠️ pytest-cov 未安装或未生成报告")


def check_code_quality_tools():
    """检查代码质量工具配置"""
    print("\n" + "=" * 60)
    print("🔍 检查代码质量工具配置")
    print("=" * 60)
    
    # 检查 pylint 配置
    pylint_cfg = Path(".pylintrc")
    if pylint_cfg.exists():
        print("✅ pylint 配置存在")
        with open(pylint_cfg, 'r') as f:
            lines = f.readlines()[:5]
            for line in lines:
                print(f"  {line.strip()}")
    else:
        print("⚠️ pylint 配置不存在")
    
    # 检查 mypy 配置
    mypy_cfg = Path("mypy.ini")
    if mypy_cfg.exists():
        print("\n✅ mypy 配置存在")
        with open(mypy_cfg, 'r') as f:
            lines = f.readlines()[:5]
            for line in lines:
                print(f"  {line.strip()}")
    else:
        print("\n⚠️ mypy 配置不存在")


def check_ci_cd_status():
    """检查 CI/CD 状态"""
    print("\n" + "=" * 60)
    print("🔧 检查 CI/CD 状态")
    print("=" * 60)
    
    # 检查 GitHub Actions
    workflows_dir = Path(".github/workflows")
    if workflows_dir.exists():
        workflows = list(workflows_dir.glob("*.yml"))
        print(f"✅ GitHub Actions 配置：{len(workflows)} 个")
        for wf in workflows:
            print(f"  - {wf.name}")
    else:
        print("⚠️ .github/workflows 不存在")
    
    # 检查 pre-commit
    precommit_cfg = Path(".pre-commit-config.yaml")
    if precommit_cfg.exists():
        print("\n✅ pre-commit 配置存在")
        with open(precommit_cfg, 'r') as f:
            lines = f.readlines()[:10]
            for line in lines:
                print(f"  {line.strip()}")
    else:
        print("\n⚠️ pre-commit 未配置")


def check_documentation():
    """检查文档完整性"""
    print("\n" + "=" * 60)
    print("📚 检查文档完整性")
    print("=" * 60)
    
    docs = [
        "README.md",
        "QUICKSTART.md",
        "COMMANDS.md",
        "EXAMPLES.md",
        "PLUGIN_DEV.md"
    ]
    
    missing_docs = []
    for doc in docs:
        if Path(doc).exists():
            print(f"✅ {doc}")
        else:
            print(f"⚠️ {doc} - 缺少")
            missing_docs.append(doc)
    
    if missing_docs:
        print(f"\n⚠️ 缺少 {len(missing_docs)} 个文档")
        return missing_docs
    else:
        print("\n✅ 所有文档完整")
        return []


def check_temp_files():
    """检查临时文件"""
    print("\n" + "=" * 60)
    print("🧹 检查临时文件")
    print("=" * 60)
    
    temp_files = [
        "test_team.py",
        "assign_tasks.py",
        "start_team.py",
        "fix_tests.py",
        "analyze_failed_tests.py",
        "check_methods.py",
        "continue_fix_tests.py",
        "skip_unimplemented.py",
        "complete_tests.py",
        "analyze_remaining_work.py",
        "code_quality_check.py",
        "continue_automation.py",
        "analyze_remaining_work.py"
    ]
    
    existing_temp = []
    for temp_file in temp_files:
        if Path(temp_file).exists():
            existing_temp.append(temp_file)
    
    if existing_temp:
        print(f"⚠️ 存在 {len(existing_temp)} 个临时文件：")
        for file in existing_temp[:5]:
            print(f"  - {file}")
        if len(existing_temp) > 5:
            print(f"  ... 还有 {len(existing_temp) - 5} 个")
    else:
        print("✅ 无临时文件")
    
    return existing_temp


def check_performance_baseline():
    """检查性能基准测试"""
    print("\n" + "=" * 60)
    print("⚡ 检查性能基准测试")
    print("=" * 60)
    
    perf_test = Path("tests/test_performance.py")
    if perf_test.exists():
        print("✅ 性能测试文件存在")
        
        # 尝试运行一个快速的性能测试
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/test_performance.py", "-v", "-k", "test_plugin_loading_performance", "--tb=no"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if "PASSED" in result.stdout:
            print("✅ 性能基准测试可运行")
        elif "FAILED" in result.stdout:
            print("⚠️ 性能基准测试失败")
    else:
        print("⚠️ 性能测试文件不存在")


def main():
    """主函数"""
    print("🔍 分析 AI PDF Agent 项目剩余工作")
    print("=" * 60)
    
    # 1. 测试覆盖率
    check_test_coverage()
    
    # 2. 代码质量工具
    check_code_quality_tools()
    
    # 3. CI/CD 状态
    check_ci_cd_status()
    
    # 4. 文档完整性
    missing_docs = check_documentation()
    
    # 5. 临时文件
    temp_files = check_temp_files()
    
    # 6. 性能基准测试
    check_performance_baseline()
    
    print("\n" + "=" * 60)
    print("📊 剩余工作汇总")
    print("=" * 60)
    
    print("\n待完成项目：")
    print(f"  测试覆盖率：{'⚠️ 需要配置' if not Path('tests/.coverage').exists() else '✅ 已配置'}")
    print(f"  代码质量工具：{'✅ 已配置' if Path('.pylintrc').exists() or Path('mypy.ini').exists() else '⚠️ 需要配置'}")
    print(f"  CI/CD 配置：{'✅ 已配置' if Path('.github/workflows').exists() else '⚠️ 需要配置'}")
    print(f"  文档完整性：{'⚠️ 缺少 ' + str(len(missing_docs)) + ' 个' if missing_docs else '✅ 完整'}")
    print(f"  临时文件清理：{'⚠️ ' + str(len(temp_files)) + ' 个待删除' if temp_files else '✅ 已清理'}")
    print(f"  性能基准测试：{'⚠️ 可运行' if Path('tests/test_performance.py').exists() else '⚠️ 不存在'}")
    
    # 优先级建议
    print("\n" + "=" * 60)
    print("🎯 优先级建议")
    print("=" * 60)
    
    if missing_docs:
        print("\n📝 优先级 1（高）：完善文档")
        for doc in missing_docs:
            print(f"  - 创建 {doc}")
    
    if temp_files:
        print("\n🧹 优先级 2（中）：清理临时文件")
        print(f"  - 删除 {len(temp_files)} 个临时文件")
    
    if not Path('.pylintrc').exists():
        print("\n🎨 优先级 3（中）：配置代码质量工具")
        print("  - 创建 .pylintrc")
        print("  - 创建 mypy.ini")
    
    if not Path('.github/workflows').exists():
        print("\n🚀 优先级 4（低）：配置 CI/CD")
        print("  - 创建 GitHub Actions workflows")
        print("  - 配置 pre-commit hooks")
    
    if Path('tests/test_performance.py').exists():
        print("\n⚡ 优先级 5（低）：运行性能基准测试")
        print("  - 运行性能测试")
        print("  - 生成性能报告")


if __name__ == "__main__":
    main()
