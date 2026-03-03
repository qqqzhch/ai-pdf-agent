#!/usr/bin/env python3
"""AI PDF Agent - Setup Script"""

from setuptools import setup, find_packages

setup(
    name="ai-pdf-agent",
    version="0.1.0",
    description="AI Agent-friendly PDF processing tool with plugin system",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="AI PDF Agent Team",
    author_email="team@ai-pdf-agent.com",
    url="https://github.com/ai-pdf-agent/ai-pdf-agent",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.1.0",
        "pymupdf>=1.24.0",
        "pdfplumber>=0.10.0",
        "Pillow>=10.0.0",
        "pdf2image>=1.16.0",
        "ebooklib>=0.18",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-pdf=cli.main:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Filters",
        "Topic :: Utilities",
    ],
)
