"""Reader Plugins"""

from .ocr_reader import OCRReaderPlugin
from .structure_reader import StructureReaderPlugin
from .text_reader import TextReaderPlugin

__all__ = [
    "TextReaderPlugin",
    "StructureReaderPlugin",
    "OCRReaderPlugin",
]
