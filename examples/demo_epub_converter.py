"""
EPUB 转换器演示脚本

演示如何使用 ToEpubConverter 将 PDF 转换为 EPUB 电子书
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.converters import ToEpubConverter


def demo_convert_pdf_to_epub():
    """演示：PDF 转 EPUB"""
    print("=" * 60)
    print("EPUB 转换器演示")
    print("=" * 60)

    # 创建转换器实例
    converter = ToEpubConverter()

    # 显示插件信息
    print(f"\n插件信息:")
    print(f"  名称: {converter.name}")
    print(f"  版本: {converter.version}")
    print(f"  描述: {converter.description}")
    print(f"  作者: {converter.author}")
    print(f"  许可证: {converter.license}")
    print(f"  可用: {converter.is_available()}")

    # 示例 1: 简单文本转 EPUB
    print("\n" + "-" * 60)
    print("示例 1: 将纯文本转换为 EPUB")
    print("-" * 60)

    text_content = """
第一章：引言

这是一个演示文本，用于展示 EPUB 转换器的功能。

• 第一个要点
• 第二个要点
• 第三个要点

1. 第一个编号项
2. 第二个编号项
3. 第三个编号项

第二章：更多内容

这是第二章的内容。EPUB 格式支持：
- 章节结构
- 目录导航
- 元数据（标题、作者等）
- CSS 样式

希望你喜欢这个演示！
""".strip()

    output_file = "/tmp/demo_text.epub"

    result = converter.convert_text_to_epub(
        text_content,
        output_file,
        title="演示文档",
        author="李开发"
    )

    if result["success"]:
        print(f"✓ 转换成功!")
        print(f"  输出文件: {result['output_path']}")
        print(f"  页数: {result['pages']}")
        print(f"  章节数: {result['chapters']}")
        print(f"  文件大小: {os.path.getsize(output_file)} 字节")
    else:
        print(f"✗ 转换失败: {result.get('error')}")

    # 示例 2: 如果有 PDF 文件，演示转换
    print("\n" + "-" * 60)
    print("示例 2: PDF 转 EPUB（需要 PDF 文件）")
    print("-" * 60)

    pdf_file = "/testfiles/simple.pdf"
    if os.path.exists(pdf_file):
        epub_file = "/tmp/demo_pdf.epub"

        result = converter.convert(
            pdf_file,
            output_path=epub_file,
            title="Simple PDF",
            author="Unknown",
            include_images=True,
            chapter_pages=0  # 每页一章
        )

        if result["success"]:
            print(f"✓ 转换成功!")
            print(f"  输出文件: {result['output_path']}")
            print(f"  页数: {result['pages']}")
            print(f"  章节数: {result['chapters']}")
            print(f"  图片数: {result['images']}")
            print(f"  文件大小: {os.path.getsize(epub_file)} 字节")
        else:
            print(f"✗ 转换失败: {result.get('error')}")
    else:
        print(f"✗ 未找到示例 PDF 文件: {pdf_file}")
        print("  跳过此示例")

    # 显示帮助信息
    print("\n" + "-" * 60)
    print("使用帮助")
    print("-" * 60)
    print(converter.get_help())

    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    demo_convert_pdf_to_epub()
