"""
修复剩余测试错误
"""

import subprocess
import sys


def fix_plugin_integration_tests():
    """修复插件集成测试"""
    print("=== 修复插件集成测试 ===")
    
    # 1. 更新测试代码中的类名引用
    print("\n1. 更新测试代码中的类名引用...")
    
    # 读取测试文件
    with open('tests/test_plugin_system_integration.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换类名引用
    replacements = [
        ('TestReaderPlugin', 'TestReaderPluginFixture'),
        ('TestConverterPlugin', 'TestConverterPluginFixture'),
        ('TestOCRPlugin', 'TestOCRPluginFixture'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open('tests/test_plugin_system_integration.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 类名引用已更新")
    
    # 2. 运行测试
    print("\n2. 运行插件集成测试...")
    result = subprocess.run(
        ['python3', '-m', 'pytest', 'tests/test_plugin_system_integration.py', '-v', '--tb=short'],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    print(result.stdout)
    
    if result.returncode == 0:
        print("\n✅ 所有插件集成测试通过！")
    else:
        print(f"\n❌ 测试失败，退出码: {result.returncode}")
        if result.stderr:
            print("错误信息:")
            print(result.stderr[-500:])  # 最后 500 字符
    
    return result.returncode == 0


if __name__ == "__main__":
    success = fix_plugin_integration_tests()
    sys.exit(0 if success else 1)
