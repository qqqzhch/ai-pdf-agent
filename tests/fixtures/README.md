# 测试数据说明

此目录包含用于测试的 PDF 文件和 Mock 插件。

## 测试 PDF 文件

- `sample.pdf` - 标准测试 PDF 文件
- `text_only.pdf` - 纯文本 PDF
- `tables_only.pdf` - 表格 PDF
- `images_only.pdf` - 图片 PDF
- `complex_layout.pdf` - 复杂布局 PDF
- `encrypted.pdf` - 加密 PDF
- `malformed.pdf` - 损坏的 PDF

## Mock 插件

- `mock_plugin.py` - Mock 插件用于测试插件系统

## 如何添加测试文件

1. 将测试 PDF 文件放到此目录
2. 更新此 README.md 文件
3. 在测试用例中引用文件路径

## 注意事项

- 测试文件应该是公开可用的（无版权问题）
- 测试文件应该尽可能小（测试速度快）
- 测试文件应该覆盖各种场景
