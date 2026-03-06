# tests/integration/test_documentation_examples.py
"""
V2 团队文档示例测试

测试 README.md 和 INSTALL.md 中的所有示例都能正常工作
"""
import pytest
import subprocess
import re
from pathlib import Path


class TestDocumentationExamples:
    """文档示例测试"""

    def extract_commands_from_readme(self):
        """从 README.md 提取命令示例"""
        readme = Path("README.md").read_text(encoding='utf-8')

        # 提取 ```bash 或 ```powershell 中的代码
        commands = re.findall(r'```(?:bash|powershell)
(.*?)```', readme, re.DOTALL)
        return [cmd.strip() for block in commands for cmd in block.split('\n') if cmd.strip() and not cmd.startswith('#')]

    def extract_commands_from_install(self):
        """从 INSTALL.md 提取命令示例"""
        install = Path("INSTALL.md").read_text(encoding='utf-8')

        # 提取 ```bash 中的代码
        commands = re.findall(r'```bash
(.*?)```', install, re.DOTALL)
        return [cmd.strip() for block in commands for cmd in block.split('\n') if cmd.strip() and not cmd.startswith('#')]

    def test_readme_commands(self):
        """测试 README 中的所有命令示例"""
        commands = self.extract_commands_from_readme()
        
        print(f"README.md 找到 {len(commands)} 个命令示例")

        for cmd in commands:
            # 跳过简单的命令（如 ls、cd）
            if 'simple-pdf' not in cmd and 'pip install' not in cmd and 'git ' not in cmd:
                continue
            
            print(f"测试命令：{cmd[:50]}...")
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"❌ 失败：{cmd[:50]}...")
                print(f"错误：{result.stderr[:100]}")
                raise AssertionError(f"命令失败：{cmd[:50]}")

    def test_install_commands(self):
        """测试 INSTALL.md 中的命令示例"""
        commands = self.extract_commands_from_install()
        
        print(f"INSTALL.md 找到 {len(commands)} 个命令示例")

        for cmd in commands:
            # 跳过简单的命令
            if 'simple-pdf' not in cmd and 'pip install' not in cmd and 'git ' not in cmd:
                continue
            
            print(f"测试命令：{cmd[:50]}...")
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"❌ 失败：{cmd[:50]}...")
                print(f"错误：{result.stderr[:100]}")
                raise AssertionError(f"命令失败：{cmd[:50]}")
