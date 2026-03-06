"""
Simple PDF - CLI 模块初始化（修复版）
"""

# 修复：从 .cli 导入 main 函数
# 注意：文件已重命名为 cli.py，不是 main.py
from .cli import main

__all__ = ['main']
