"""Reader Plugins"""

from .text_reader import TextReaderPlugin
from .structure_reader import StructureReaderPlugin
from .ocr_reader import OCRReaderPlugin

__all__ = [
    "TextReaderPlugin",
    "StructureReaderPlugin",
    "OCRReaderPlugin",
]
