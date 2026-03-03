#!/usr/bin/env python3
"""性能测试运行脚本"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def print_banner():
    print("=" * 70)
    print(" " * 15 + "AI-PDF-AGENT Performance Benchmarks")
    print("=" * 70)


def print_menu():
    print("\nAvailable Tests:")
    print("  1. All Benchmarks")
    print("  2. PDF Reading Benchmark")
    print("  3. Plugin Loading Benchmark")
    print("  4. Parallel Processing Benchmark")
    print("  5. All Profile Tests")
    print("  6. PDF Extraction Profile")
    print("  7. Plugin Discovery Profile")
    print("  8. Parallel Processing Profile")
    print("  0. Exit")
    print()


def run_choice(choice):
    """运行用户选择的测试"""
    
    # 导入测试模块
    from benchmarks import (
        benchmark_pdf_reading,
        benchmark_plugin_loading,
        benchmark_parallel_processing,
        run_all_benchmarks
    )
    from profile_tests import (
        test_pdf_text_extraction_profile,
        test_plugin_discovery_profile,
        test_parallel_processing_profile,
        run_all_profiles
    )
    
    if choice == "1":
        run_all_benchmarks()
    
    elif choice == "2":
        benchmark_pdf_reading()
    
    elif choice == "3":
        benchmark_plugin_loading()
    
    elif choice == "4":
        benchmark_parallel_processing()
    
    elif choice == "5":
        run_all_profiles()
    
    elif choice == "6":
        test_pdf_text_extraction_profile()
    
    elif choice == "7":
        test_plugin_discovery_profile()
    
    elif choice == "8":
        test_parallel_processing_profile()
    
    elif choice == "0":
        print("\nExiting...")
        return False
    
    else:
        print(f"\nInvalid choice: {choice}")
    
    return True


def main():
    """主函数"""
    print_banner()
    
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 命令行模式
        test_name = sys.argv[1].lower()
        
        if test_name == "all":
            from benchmarks import run_all_benchmarks
            run_all_benchmarks()
        elif test_name == "pdf":
            from benchmarks import benchmark_pdf_reading
            benchmark_pdf_reading()
        elif test_name == "plugin":
            from benchmarks import benchmark_plugin_loading
            benchmark_plugin_loading()
        elif test_name == "parallel":
            from benchmarks import benchmark_parallel_processing
            benchmark_parallel_processing()
        elif test_name == "profile-all":
            from profile_tests import run_all_profiles
            run_all_profiles()
        elif test_name == "profile-pdf":
            from profile_tests import test_pdf_text_extraction_profile
            test_pdf_text_extraction_profile()
        elif test_name == "profile-plugin":
            from profile_tests import test_plugin_discovery_profile
            test_plugin_discovery_profile()
        elif test_name == "profile-parallel":
            from profile_tests import test_parallel_processing_profile
            test_parallel_processing_profile()
        else:
            print(f"Unknown test: {test_name}")
            print_usage()
            sys.exit(1)
    else:
        # 交互模式
        while True:
            print_menu()
            choice = input("Select test (0-8): ").strip()
            
            if not run_choice(choice):
                break


def print_usage():
    """打印使用说明"""
    print("\nUsage:")
    print("  python run_benchmarks.py [test_name]")
    print("\nTest names:")
    print("  all           - Run all benchmarks")
    print("  pdf           - PDF reading benchmark")
    print("  plugin        - Plugin loading benchmark")
    print("  parallel      - Parallel processing benchmark")
    print("  profile-all   - Run all profile tests")
    print("  profile-pdf   - PDF extraction profile")
    print("  profile-plugin- Plugin discovery profile")
    print("  profile-parallel - Parallel processing profile")
    print("\nWithout arguments, runs in interactive mode.")


if __name__ == "__main__":
    main()
