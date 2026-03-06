# tests/integration/test_pdf_engine_integration.py
"""
V2 团队 PDF 引擎集成测试

测试 PDF 引擎的初始化、页面读取和完整操作
"""
import pytest
import subprocess
import tempfile
from pathlib import Path


class TestPDFEngineIntegrationV2:
    """V2 PDF 引擎集成测试"""

    def test_pdf_engine_initialization(self):
        """测试 PDF 引擎初始化"""
        pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
        
        result = subprocess.run(
            ["python3", "-c", """
import sys
sys.path.insert(0, '.')
from ai_pdf_agent.core.pdf_engine import PDFEngine

pdf = PDFEngine('/root/book/Nginx 安全配置指南技术手册.pdf')
assert pdf is not None
assert pdf.get_page_count() > 0
print(f'页数: {pdf.get_page_count()}')
print('PDF 引擎初始化成功')
"""],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/root/.openclaw/workspace/ai-pdf-agent"
        )
        
        assert result.returncode == 0
        assert "页数: 48" in result.stdout
        assert "PDF 引擎初始化成功" in result.stdout

    def test_pdf_engine_page_reading(self):
        """测试 PDF 引擎页面读取"""
        pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
        
        result = subprocess.run(
            ["python3", "-c", """
import sys
sys.path.insert(0, '.')
from ai_pdf_agent.core.pdf_engine import PDFEngine

pdf = PDFEngine('/root/book/Nginx 安全配置指南技术手册.pdf')

# 读取第一页
page_1_text, success_1 = pdf.read_page(1)
assert success_1
assert len(page_1_text) > 0

# 读取所有页面
full_text, success_all = pdf.read_all()
assert success_all
assert len(full_text) > 0
assert len(full_text) > len(page_1_text)

print('第一页字符数:', len(page_1_text))
print('全文字符数:', len(full_text))
print('PDF 引擎页面读取成功')
"""],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/root/.openclaw/workspace/ai-pdf-agent"
        )
        
        assert result.returncode == 0
        assert "第一页字符数:" in result.stdout
        assert "全文字符数:" in result.stdout
        assert "PDF 引擎页面读取成功" in result.stdout

    def test_pdf_engine_full_reading(self):
        """测试 PDF 引擎完整读取"""
        pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
        
        result = subprocess.run(
            ["python3", "-c", """
import sys
sys.path.insert(0, '.')
from ai_pdf_agent.core.pdf_engine import PDFEngine

pdf = PDFEngine('/root/book/Nginx 安全配置指南技术手册.pdf')

# 完整读取
text, success = pdf.read_all()
assert success
assert len(text) > 0
assert "Nginx" in text

print(f'总字符数: {len(text)}')
print('PDF 引擎完整读取成功')
"""],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/root/.openclaw/workspace/ai-pdf-agent"
        )
        
        assert result.returncode == 0
        assert "总字符数:" in result.stdout
        assert "PDF 引擎完整读取成功" in result.stdout

    def test_pdf_engine_metadata(self):
        """测试 PDF 元数据"""
        pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
        
        result = subprocess.run(
            ["python3", "-c", """
import sys
sys.path.insert(0, '.')
from ai_pdf_agent.core.pdf_engine import PDFEngine

pdf = PDFEngine('/root/book/Nginx 安全配置指南技术手册.pdf')

# 获取元数据
metadata = pdf.get_metadata()
assert metadata is not None
assert 'page_count' in metadata
assert metadata['page_count'] > 0

print(f'页数: {metadata["page_count"]}')
print('PDF 元数据成功')
"""],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/root/.openclaw/workspace/ai-pdf-agent"
        )
        
        assert result.returncode == 0
        assert "页数:" in result.stdout
        assert "PDF 元数据成功" in result.stdout

    def test_multiple_pdf_files(self):
        """测试多个 PDF 文件"""
        pdf_files = [
            "/root/book/Nginx 安全配置指南技术手册.pdf",
            "/root/book/C程序设计语言(K&R)_第2版中文版.pdf",
        ]
        
        for pdf_file in pdf_files:
            result = subprocess.run(
                ["python3", "-c", f"""
import sys
sys.path.insert(0, '.')
from ai_pdf_agent.core.pdf_engine import PDFEngine

pdf = PDFEngine('{pdf_file}')
text, success = pdf.read_all()

assert success
assert len(text) > 0
print(f'{{pdf_file}}: {{len(text)}} 字节')
""",
                capture_output=True,
                text=True,
                timeout=30,
                cwd="/root/.openclaw/workspace/ai-pdf-agent"
            )
            
            assert result.returncode == 0
            assert "字节" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
