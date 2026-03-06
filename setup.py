"""
Simple PDF - 安装配置（修复版）
"""

from setuptools import setup, find_packages

# 读取 README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取版本
with open("VERSION", "r", encoding="utf-8") as fh:
    version = fh.read().strip()

setup(
    name="simple-pdf",
    version=version,
    author="Simple PDF Team",
    author_email="simplepdf@example.com",
    description="Simple PDF - 简单易用的 PDF 处理工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qqqzhch/ai-pdf-agent",
    project_urls={
        "Bug Tracker": "https://github.com/qqqzhch/ai-pdf-agent/issues",
        "Documentation": "https://github.com/qqqzhch/ai-pdf-agent#readme",
        "Source Code": "https://github.com/qqqzhch/ai-pdf-agent",
    },
    packages=find_packages(exclude=["tests*", "docs*"]),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pymupdf>=1.23.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            # 修复：使用 ai_pdf_agent.cli.cli:main 而不是 ai_pdf_agent.cli.main:cli
            "simple-pdf=ai_pdf_agent.cli.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords=["pdf", "simple", "document", "converter", "pymupdf"],
)
