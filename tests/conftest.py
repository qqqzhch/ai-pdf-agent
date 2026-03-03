"""pytest 配置文件"""

import pytest


def pytest_configure(config):
    """pytest 配置"""
    # 可以在这里添加自定义配置
    pass


@pytest.fixture
def sample_pdf_path(tmp_path):
    """测试 PDF 文件路径 fixture"""
    # 这里可以创建一个测试 PDF 文件
    # 或者返回一个已存在的测试文件
    return "./tests/fixtures/sample.pdf"


@pytest.fixture
def output_path(tmp_path):
    """输出文件路径 fixture"""
    output_file = tmp_path / "output.txt"
    return str(output_file)
