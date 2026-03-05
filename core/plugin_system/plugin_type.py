"""插件类型枚举"""

from enum import Enum


class PluginType(Enum):
    """插件类型

    各类型说明：
    - READER: 阅读器插件，用于读取/提取 PDF 内容（文本、表格、图片等）
    - CONVERTER: 转换器插件，用于 PDF 格式转换（Markdown、HTML、JSON 等）
    - OCR: OCR 插件，用于文字识别（Tesseract、PaddleOCR、多模态）
    - RAG: RAG 插件，用于检索增强生成（向量索引、语义检索）
    - ENCRYPT: 加密插件，用于密码保护（PDF 加密、解密）
    - COMPRESS: 压缩插件，用于文件压缩（PDF 压缩、图片优化）
    - EDIT: 编辑插件，用于修改 PDF（添加文本、删除页面、旋转等）
    - ANALYZE: 分析插件，用于文档分析（质量评估、内容分析）
    - CUSTOM: 自定义插件，用户自定义功能
    """

    READER = "reader"
    CONVERTER = "converter"
    OCR = "ocr"
    RAG = "rag"
    ENCRYPT = "encrypt"
    COMPRESS = "compress"
    EDIT = "edit"
    ANALYZE = "analyze"
    CUSTOM = "custom"
