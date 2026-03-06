# tests/integration/test_converter_integration.py
"""
V2 团队转换器集成测试

测试所有转换器的集成和格式支持
"""
import pytest
import subprocess
import tempfile
from pathlib import Path


class TestConverterIntegrationV2:
    """V2 转换器集成测试"""

    def test_markdown_converter_initialization(self):
        """测试 Markdown 转换器初始化"""
        result = subprocess.run(
            ["python3", "-c", """
import sys
sys.path.insert(0, '.')
from plugins.converters.to_markdown import MarkdownConverter

converter = MarkdownConverter()
assert converter is not None
assert converter.name == 'to_markdown'
print('Markdown 转换器初始化成功')
print(f'版本: {converter.version}')
"""],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/root/.openclaw/workspace/ai-pdf-agent"
        )
        
        print("输出：")
        print(result.stdout)
        assert result.returncode == 0

    def test_json_converter_initialization(self):
        """测试 JSON 转换器初始化"""
        result = subprocess.run(
            ["python3", "-c", """
import sys
sys.path.insert(0, '.')
from plugins.converters.to_json import JSONConverter

converter = JSONConverter()
assert converter is not None
assert converter.name == 'to_json'
print('JSON 转换器初始化成功')
print(f'版本: {converter.version}')
"""],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/root/.openclaw/workspace/ai-pdf-agent"
        )
        
        print("输出：")
        print(result.stdout)
        assert result.returncode == 0

    def test_html_converter_initialization(self):
        """测试 HTML 转换器初始化"""
        result = subprocess.run(
            ["python3", "-c", """
import sys
sys.path.insert(0, '.')
from plugins.converters.to_html import HTMLConverter

converter = HTMLConverter()
assert converter is not None
assert converter.name == 'to_html'
print('HTML 转换器初始化成功')
print(f'版本: {converter.version}')
"""],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/root/.openclaw/workspace/ai-pdf-agent"
        )
        
        print("输出：")
        print(result.stdout)
        assert result.returncode == 0

    def test_text_converter_initialization(self):
        """测试 Text 转换器初始化"""
        result = subprocess.run(
            ["python3", "-c", """
import sys
sys.path.insert(0, '.')
from plugins.converters.to_text import TextConverter

converter = TextConverter()
assert converter is not None
assert converter.name == 'to_text'
print('Text 转换器初始化成功')
print(f'版本: {converter.version}')
"""],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/root/.openclaw/workspace/ai-pdf-agent"
        )
        
        print("输出：")
        print(result.stdout)
        assert result.returncode == 0

    def test_all_converters_available(self):
        """测试所有转换器都可用"""
        result = subprocess.run(
            ["python3", "-c", """
import sys
sys.path.insert(0, '.')
from plugins.converters.to_markdown import MarkdownConverter
from plugins.converters.to_json import JSONConverter
from plugins.converters.to_html import HTMLConverter
from plugins.converters.to_text import TextConverter

converters = [MarkdownConverter(), JSONConverter(), HTMLConverter(), TextConverter()]

for converter in converters:
    assert converter is not None
    print(f'{converter.name}: 可用')
    assert converter.is_available()

print('所有转换器都可用')
"""],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/root/.openclaw/workspace/ai-pdf-agent"
        )
        
        print("输出：")
        print(result.stdout)
        assert result.returncode == 0

    def test_get_supported_formats(self):
        """测试获取支持的格式"""
        result = subprocess.run(
            ["python3", "-c", """
import sys
sys.path.insert(0, '.')
from plugins.converters.to_markdown import MarkdownConverter

converter = MarkdownConverter()
formats = converter.get_supported_formats()

assert isinstance(formats, list)
assert len(formats) > 0
print(f'支持格式：{formats}')
assert 'markdown' in formats
assert 'html' in formats
assert 'json' in formats
assert 'text' in
```
"""],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/root/.openclaw/workspace/ai-pdf-agent"
        )
        
        print("输出：")
        print(result.stdout)
        assert result.returncode == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
