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
            cwd="/root/.openclaw/workspace/ai-pdf-agent"
        )
        
        assert result.returncode == 0
        assert "Markdown 转换器初始化成功" in result.stdout
        assert "版本" in result.stdout

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
            cwd="/root/.openclaw/workspace/ai-pdf-agent"
        )
        
        assert result.returncode == 0
        assert "JSON 转换器初始化成功" in result.stdout
        assert "版本" in result.stdout

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
            cwd="/root/.openclaw/workspace/ai-pdf-agent"
        )
        
        assert result.returncode == 0
        assert "HTML 转换器初始化成功" in result.stdout

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
            cwd="/root/.openclaw/workspace/ai-pdf-agent"
        )
        
        assert result.returncode == 0
        assert "Text 转换器初始化成功" in result.stdout
        assert "版本" in result.stdout

    def test_convert_all_formats(self):
        """测试所有格式转换"""
        pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
        formats = ['markdown', 'json', 'html', 'text']
        
        with tempfile.TemporaryDirectory() as tmpdir:
            for format in formats:
                output_file = Path(tmpdir) / f"output.{format}"

                result = subprocess.run(
                    ["python3", "-m", "ai_pdf_agent.cli.cli", "convert", pdf_path,
                     "--"format", format, "-o", str(output_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                assert result.returncode == 0
                assert output_file.exists()
                
                content = output_file.read_text(encoding='utf-8', errors='ignore')
                assert len(content) > 0
                
                # 验证内容
                if format == 'json':
                    assert '"file"' in content
                    assert '"pages"' in content
                elif format == 'html':
                    assert "<html>" in content
                elif format == 'markdown':
                    assert "#" in content or "##" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
