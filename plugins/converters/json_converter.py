"""JSON 转换器插件 - 将 PDF 内容转换为 JSON 格式

此模块提供了 ToJsonConverter 类，它是 ToJsonPlugin 的别名，
用于保持向后兼容性和任务要求的一致性。

主要功能：
- 将 PDF 转换为结构化 JSON 格式
- 提取文本、表格、图片、元数据
- 支持页码范围选择
- 支持自定义输出路径
- 支持字段过滤和自定义 schema
"""

from .to_json import ToJsonPlugin

# 创建别名以符合任务要求
ToJsonConverter = ToJsonPlugin

__all__ = ["ToJsonConverter"]
