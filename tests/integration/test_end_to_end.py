# tests/integration/test_end_to_end.py
"""
V2 团队端到端测试

测试完整的用户工作流，从命令输入到最终结果
"""
import pytest
import subprocess
import tempfile
from pathlib import Path


class TestEndToEndV2:
    """V2 端到端测试"""

    def test_user_workflow_read_and_convert(self):
        """测试用户工作流：读取并转换"""
        pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 步骤 1：读取 PDF
            read_output = Path(tmpdir) / "read.txt"
            result = subprocess.run(
                ["python3", "-m", "ai_pdf_agent.cli.cli", "read", pdf_path, "-o", str(read_output)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            assert result.returncode == 0
            assert read_output.exists()
            
            read_content = read_output.read_text(encoding='utf-8', errors='ignore')
            assert len(read_content) > 0
            assert "Nginx" in read_content
            
            # 步骤 2：转换为 Markdown
            md_output = Path(tmpdir) / "convert.md"
            result = subprocess.run(
                ["python3", "-m", "ai_pdf_agent.cli.cli", "convert", pdf_path,
                 "--format", "markdown", "-o", str(md_output)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            assert result.returncode == 0
            assert md_output.exists()
            
            md_content = md_output.read_text(encoding='utf-8', errors='ignore')
            assert len(md_content) > 0
            assert "Nginx" in md_content
            
            # 步骤 3：转换为 JSON
            json_output = Path(tmpdir) / "convert.json"
            result = subprocess.run(
                ["python3", "-m", "ai_pdf_agent.cli.cli", "convert", pdf_path,
                 "--format", "json", "-o", str(json_output)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            assert result.returncode == 0
            assert json_output.exists()
            
            json_content = json_output.read_text(encoding='utf-8')
            assert len(json_content) > 0
            assert '"file"' in json_content
            assert '"pages"' in json_content

    def test_multiple_pdf_processing(self):
        """测试批量 PDF 处理"""
        pdf_files = [
            "/root/book/Nginx 安全配置指南技术手册.pdf",
            "/root/book/【51】TCP IP详解 卷1：协议.pdf",
            "/root/book/【53】TCP IP详解 卷3：TCP事务协议，HTTP，NNTP和UNIX域协议.pdf"
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            for i, pdf_file in enumerate(pdf_files[:3]):  # 测试前 3 个
                output = Path(tmpdir) / f"output_{i}.txt"
                
                result = subprocess.run(
                    ["python3", "-m", "ai_pdf_agent.cli.cli", "read", pdf_file, "-o", str(output)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                assert result.returncode == 0
                assert output.exists()
                
                content = output.read_text(encoding='utf-8', errors='ignore')
                assert len(content) > 0

    def test_all_format_conversions(self):
        """测试所有格式转换"""
        pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
        
        formats = ['markdown', 'json', 'html', 'text']
        
        with tempfile.TemporaryDirectory() as tmpdir:
            for format in formats:
                output = Path(tmpdir) / f"output.{format}"
                
                result = subprocess.run(
                    ["python3", "-m", "ai_pdf_agent.cli.cli", "convert", pdf_path,
                     "--format", format, "-o", str(output)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                assert result.returncode == 0
                assert output.exists()
                assert output.stat().st_size > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
