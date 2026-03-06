#!/usr/bin/env python3
"""
Simple PDF - CLI 主入口（完整实现）
"""

import click
import os
import sys
import json

# 添加插件路径
plugin_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins')
if plugin_path not in sys.path:
    sys.path.insert(0, plugin_path)


def read_pdf_text(pdf_path):
    """
    读取 PDF 文本内容（使用 PyMuPDF）
    
    Args:
        pdf_path: PDF 文件路径
        
    Returns:
        str: PDF 文本内容
    """
    try:
        import fitz  # PyMuPDF
        
        # 打开 PDF
        pdf = fitz.open(pdf_path)
        
        # 提取所有文本
        text = ""
        page_count = pdf.page_count
        
        for page_num in range(page_count):
            page = pdf[page_num]
            text += page.get_text() + "\n\n"
        
        # 关闭 PDF
        pdf.close()
        
        return text
        
    except ImportError:
        return "错误: 未安装 PyMuPDF。请运行: pip install pymupdf"
    except Exception as e:
        return f"错误: {str(e)}"


def convert_pdf(pdf_path, output_format):
    """
    转换 PDF 到指定格式
    
    Args:
        pdf_path: PDF 文件路径
        output_format: 输出格式（markdown, html, json, text）
        
    Returns:
        str: 转换后的内容
    """
    try:
        import fitz  # PyMuPDF
        
        # 打开 PDF
        pdf = fitz.open(pdf_path)
        
        # 获取页数
        page_count = pdf.page_count
        
        # 提取文本
        text = ""
        for page_num in range(page_count):
            page = pdf[page_num]
            text += page.get_text() + "\n\n"
        
        # 关闭 PDF
        pdf.close()
        
        # 根据格式转换
        if output_format == 'text':
            return text
        
        elif output_format == 'json':
            return json.dumps({
                'file': pdf_path,
                'pages': page_count,
                'content': text
            }, ensure_ascii=False, indent=2)
        
        elif output_format == 'markdown':
            # 简单转换为 Markdown
            lines = text.split('\n')
            md_content = ""
            for line in lines:
                if line.strip():
                    # 如果行太长，可能是标题
                    if len(line) > 0 and len(line) < 100 and line.strip()[0].isdigit():
                        md_content += f"## {line}\n\n"
                    else:
                        md_content += f"{line}\n"
            return md_content
        
        elif output_format == 'html':
            # 简单转换为 HTML
            lines = text.split('\n')
            html_content = "<html><head><meta charset='UTF-8'><title>PDF 转换</title></head><body>"
            for line in lines:
                if line.strip():
                    html_content += f"<p>{line}</p>"
            html_content += "</body></html>"
            return html_content
        
        else:
            return text
            
    except ImportError:
        return "错误: 未安装 PyMuPDF。请运行: pip install pymupdf"
    except Exception as e:
        return f"错误: {str(e)}"


@click.group()
@click.version_option(version="1.0.0", prog_name="simple-pdf")
def main():
    """Simple PDF - 简单易用的 PDF 处理工具

    使用方法：
      simple-pdf read <pdf-path> [-o output]
      simple-pdf convert <pdf-path> --format <format> [-o output]
    """
    pass


@main.command()
@click.argument('pdf_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
def read(pdf_path, output):
    """读取 PDF 内容并提取信息"""
    click.echo(f"读取 PDF: {pdf_path}")
    
    # 读取 PDF 文本
    content = read_pdf_text(pdf_path)
    
    # 输出到文件或控制台
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(content)
        click.echo(f"输出到: {output}")
    else:
        click.echo(content)


@main.command()
@click.argument('pdf_path', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['markdown', 'html', 'json', 'text']), required=True, help='输出格式')
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
def convert(pdf_path, format, output):
    """转换 PDF 到指定格式"""
    click.echo(f"转换 PDF: {pdf_path} -> {format}")
    
    # 转换 PDF
    content = convert_pdf(pdf_path, format)
    
    # 输出到文件或控制台
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(content)
        click.echo(f"输出到: {output}")
    else:
        click.echo(content)


if __name__ == '__main__':
    main()
