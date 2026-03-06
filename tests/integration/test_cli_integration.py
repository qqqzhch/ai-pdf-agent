# tests/integration/test_cli_integration.py
"""
V2 团队 CLI 集成测试

测试整个 CLI 工作流程，验证所有命令和参数
"""
import subprocess
import tempfile
from pathlib import Path


class TestCLIIntegrationV2:
    """V2 CLI 集成测试"""

    def test_version_command(self):
        """测试版本命令"""
        result = subprocess.run(
            ["python3", "-m", "ai_pdf_agent.cli.cli", "--version"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "1.1.0" in result.stdout

    def test_help_command(self):
        """测试帮助命令"""
        result = subprocess.run(
            ["python3", "-m", "ai_pdf_agent.cli.cli", "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Simple PDF" in result.stdout
        assert "read" in result.stdout
        assert "convert" in result.stdout

    def test_read_command_with_output(self):
        """测试读取命令（带输出文件）"""
        pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.txt"

            result = subprocess.run(
                ["python3", "-m", "ai_pdf_agent.cli.cli", "read", pdf_path, "-o", str(output_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            assert result.returncode == 0
            assert output_file.exists()
            
            content = output_file.read_text(encoding='utf-8', errors='ignore')
            assert len(content) > 0
            assert "Nginx" in content

    def test_read_command_without_output(self):
        """测试读取命令（输出到控制台）"""
        pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"

        result = subprocess.run(
            ["python3", "-m", "ai_pdf_agent.cli.cli", "read", pdf_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0
        assert len(result.stdout) > 0
        assert "Nginx" in result.stdout

    def test_convert_to_markdown(self):
        """测试 Markdown 转换"""
        pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.md"

            result = subprocess.run(
                ["python3", "-m", "ai_pdf_agent.cli.cli", "convert", pdf_path,
                 "--format", "markdown", "-o", str(output_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            assert result.returncode == 0
            assert output_file.exists()
            
            content = output_file.read_text(encoding='utf-8', errors='ignore')
            assert len(content) > 0
            assert "Nginx" in content

    def test_convert_to_json(self):
        """测试 JSON 转换"""
        pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.json"

            result = subprocess.run(
                ["python3", "-m", "ai_pdf_agent.cli.cli", "convert", pdf_path,
                 "--format", "json", "-o", str(output_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            assert result.returncode == 0
            assert output_file.exists()
            
            content = output_file.read_text(encoding='utf-8')
            assert len(content) > 0
            assert '"file"' in content
            assert '"pages"' in content
            assert '"content"' in content

    def test_convert_to_html(self):
        """测试 HTML 转换"""
        pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.html"

            result = subprocess.run(
                ["python3", "-m", "ai_pdf_agent.cli.cli", "convert", pdf_path,
                 "--format", "html", "-o", str(output_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            assert result.returncode == 0
            assert output_file.exists()
            
            content = output_file.read_text(encoding='utf-8', errors='ignore')
            assert len(content) > 0
            assert "<html>" in content
            assert "<body>" in content

    def test_convert_to_text(self):
        """测试 Text 转换"""
        pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.txt"

            result = subprocess.run(
                ["python3", "-m", "ai_pdf_agent.cli.cli", "convert", pdf_path,
                 "--format", "text", "-o", str(output_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            assert result.returncode == 0
            assert output_file.exists()
            
            content = output_file.read_text(encoding='utf-8', errors='ignore')
            assert len(content) > 0
            assert "Nginx" in content

    def test_all_formats(self):
        """测试所有格式转换"""
        pdf_path = "/root/book/Nginx 安全配置指南技术手册.pdf"
        formats = ['markdown', 'json', 'html', 'text']
        
        with tempfile.TemporaryDirectory() as tmpdir:
            for format in formats:
                output_file = Path(tmpdir) / f"output.{format}"

                result = subprocess.run(
                    ["python3", "-m", "ai_pdf_agent.cli.cli", "convert", pdf_path,
                     "--format", format, "-o", str(output_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                assert result.returncode == 0
                assert output_file.exists()
                
                content = output_file.read_text(encoding='utf-8', errors='ignore')
                assert len(content) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
