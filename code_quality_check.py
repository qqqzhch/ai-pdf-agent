"""
运行代码质量检查

包括：
1. pylint 检查
2. mypy 类型检查
3. black 格式检查
4. isort import 检查
"""

import subprocess
import sys


def run_pylint():
    """运行 pylint 检查"""
    print("=" * 60)
    print("1. 运行 pylint 检查")
    print("=" * 60)
    
    result = subprocess.run(
        [
            "pylint",
            "plugins/",
            "team/",
            "cli/",
            "core/",
            "--errors-only",
            "--max-line-length=120",
            "--disable=import-error",
            "-j", "4"  # 并行 4 个进程
        ],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode == 0:
        print("✅ pylint: 无错误")
        return True
    else:
        print("⚠️ pylint 发现错误：")
        print(result.stdout[-2000:])  # 最后 2000 字符
        return False


def run_mypy():
    """运行 mypy 类型检查"""
    print("\n" + "=" * 60)
    print("2. 运行 mypy 类型检查")
    print("=" * 60)
    
    # 检查是否有 mypy
    try:
        subprocess.run(["mypy", "--version"], capture_output=True, timeout=5)
    except Exception:
        print("⚠️ mypy 未安装，跳过类型检查")
        return True
    
    result = subprocess.run(
        [
            "mypy",
            "plugins/",
            "team/",
            "cli/",
            "core/",
            "--ignore-missing-imports",
            "--no-error-summary",
            "--show-error-codes"
        ],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode == 0:
        print("✅ mypy: 类型检查通过")
        return True
    else:
        print("⚠️ mypy 发现类型问题：")
        print(result.stdout[-2000:])
        return False


def run_black_check():
    """运行 black 格式检查"""
    print("\n" + "=" * 60)
    print("3. 运行 black 格式检查")
    print("=" * 60)
    
    result = subprocess.run(
        [
            "black",
            "--check",
            "plugins/",
            "team/",
            "cli/",
            "core/"
        ],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if result.returncode == 0:
        print("✅ black: 代码格式符合规范")
        return True
    else:
        print("⚠️ black 发现格式问题：")
        print(result.stdout[-1000:])
        return False


def run_is_isort_check():
    """运行 isort import 检查"""
    print("\n" + "=" * 60)
    print("4. 运行 isort import 检查")
    print("=" * 60)
    
    result = subprocess.run(
        [
            "isort",
            "--check-only",
            "plugins/",
            "team/",
            "cli/",
            "core/"
        ],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if result.returncode == 0:
        print("✅ isort: import 排序符合规范")
        return True
    else:
        print("⚠️ isort 发现 import 排序问题：")
        print(result.stdout[-1000:])
        return False


def main():
    """运行所有代码质量检查"""
    print("🔍 代码质量检查")
    print("=" * 60)
    
    results = {
        "pylint": run_pylint(),
        "mypy": run_mypy(),
        "black": run_black_check(),
        "isort": run_is_isort_check()
    }
    
    print("\n" + "=" * 60)
    print("📊 检查结果汇总")
    print("=" * 60)
    
    for tool, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{tool:10} : {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有代码质量检查通过！")
    else:
        print("⚠️ 部分检查未通过，需要修复")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
