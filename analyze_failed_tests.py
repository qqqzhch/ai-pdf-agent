"""
分析失败的测试
"""

import subprocess
import re
from collections import defaultdict


def analyze_failed_tests():
    """分析失败的测试"""
    print("=" * 60)
    print("🔍 分析失败的测试")
    print("=" * 60)
    
    # 运行测试并捕获失败
    result = subprocess.run(
        ["python3", "-m", "pytest", "tests/", "--tb=no", "-q"],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    # 提取失败的测试
    failed_tests = re.findall(r'FAILED (.+)', result.stdout)
    error_tests = re.findall(r'ERROR (.+)', result.stdout)
    
    all_failed = failed_tests + error_tests
    
    print(f"\n📊 失败测试统计：")
    print(f"  总失败数：{len(all_failed)}")
    print(f"  FAILED：{len(failed_tests)}")
    print(f"  ERROR：{len(error_tests)}")
    
    # 按文件分组
    by_file = defaultdict(list)
    for test in all_failed:
        # 提取文件名
        match = re.search(r'tests/([^/]+/[^/]+\.py)', test)
        if match:
            file_path = match.group(1)
            by_file[file_path].append(test)
    
    print(f"\n📁 按文件分组（前 10 个）：")
    for file, tests in sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"\n  {file} ({len(tests)} 个失败)")
        for test in tests[:5]:  # 只显示前 5 个
            test_name = test.split('::')[-1]
            print(f"    - {test_name}")
        if len(tests) > 5:
            print(f"    ... 还有 {len(tests) - 5} 个")
    
    # 分析失败类型
    print(f"\n🔬 失败类型分析：")
    
    # 检查导入错误
    import_errors = [t for t in error_tests if 'ERROR' in result.stdout]
    if import_errors:
        print(f"  导入错误：{len(import_errors)}")
    
    # 检查断言错误
    assertion_errors = [t for t in failed_tests]
    if assertion_errors:
        print(f"  断言错误：{len(assertion_errors)}")
    
    # 运行详细错误分析
    print(f"\n🔬 详细错误分析（前 3 个）：")
    for i, test in enumerate(all_failed[:3]):
        print(f"\n  {i + 1}. {test}")
        
        # 运行单个测试获取详细错误
        detailed_result = subprocess.run(
            ["python3", "-m", "pytest", test, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 提取错误信息
        if "AssertionError" in detailed_result.stdout:
            match = re.search(r'AssertionError: (.+)', detailed_result.stdout)
            if match:
                error_msg = match.group(1).strip()
                error_msg = error_msg.split('\n')[0]  # 只取第一行
                print(f"    AssertionError: {error_msg[:100]}")
        
        elif "AttributeError" in detailed_result.stdout:
            match = re.search(r'AttributeError: (.+)', detailed_result.stdout)
            if match:
                error_msg = match.group(1).strip()
                print(f"    AttributeError: {error_msg[:100]}")
        
        elif "NameError" in detailed_result.stdout:
            match = re.search(r'NameError: (.+)', detailed_result.stdout)
            if match:
                error_msg = match.group(1).strip()
                print(f"    NameError: {error_msg[:100]}")
    
    return by_file


def suggest_fixes(by_file):
    """建议修复方案"""
    print("\n" + "=" * 60)
    print("💡 修复建议")
    print("=" * 60)
    
    # CSV 转换器测试失败
    csv_failures = by_file.get('converters/test_csv.py', [])
    if csv_failures:
        print(f"\n🔧 CSV 转换器测试（{len(csv_failures)} 个失败）：")
        print("  原因：类名变更")
        print("  修复：")
        print("    1. 测试类名从 TestToCsvPlugin 改为 TestToCsvPlugin")
        print("    2. fixture 中的类名也需要更新")
        print("    3. 运行: sed -i 's/TestToCsvPlugin/TestToCsvPlugin/g' tests/converters/test_csv.py")
    
    # 插件集成测试失败
    integration_failures = by_file.get('test_plugin_system_integration.py', [])
    if integration_failures:
        print(f"\n🔧 插件集成测试（{len(integration_failures)} 个失败）：")
        print("  原因：fixture 中的插件实例化")
        print("  修复：")
        print("    1. 使用实际插件类而非测试 Fixture 类")
        print("    2. 检查插件依赖是否满足")
        print("    3. 验证插件生命周期钩子")
    
    # 其他转换器测试
    other_failures = sum(len(tests) for file, tests in by_file.items() 
                         if file not in ['converters/test_csv.py', 'test_plugin_system_integration.py'])
    
    if other_failures:
        print(f"\n🔧 其他转换器测试（{other_failures} 个失败）：")
        print("  原因：类名变更或属性不匹配")
        print("  修复：")
        print("    1. 统一测试类命名规范")
        print("    2. 更新 fixture 中的引用")
        print("    3. 验证插件属性")


def main():
    """主函数"""
    by_file = analyze_failed_tests()
    suggest_fixes(by_file)
    
    print("\n" + "=" * 60)
    print("✅ 分析完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
