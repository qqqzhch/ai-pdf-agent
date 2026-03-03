# AI PDF Agent - 插件开发指南

> 为 AI PDF Agent 开发自定义插件的完整指南

---

## 📚 目录

1. [插件基础](#插件基础)
   - [继承体系](#继承体系)
   - [核心接口](#核心接口)
   - [生命周期](#生命周期)
2. [Reader 插件开发](#reader-插件开发)
   - [继承 BaseReaderPlugin](#继承-basereaderplugin)
   - [实现 read 方法](#实现-read-方法)
   - [实现 validate 方法](#实现-validate-方法)
   - [完整示例](#reader-插件完整示例)
3. [Converter 插件开发](#converter-插件开发)
   - [继承 BaseConverterPlugin](#继承-baseconverterplugin)
   - [实现 convert 方法](#实现-convert-方法)
   - [完整示例](#converter-插件完整示例)
4. [插件注册和加载](#插件注册和加载)
   - [插件目录结构](#插件目录结构)
   - [手动注册](#手动注册)
   - [自动发现](#自动发现)
5. [测试插件](#测试插件)
   - [单元测试](#单元测试)
   - [集成测试](#集成测试)
   - [测试覆盖率](#测试覆盖率)
6. [发布插件](#发布插件)
   - [打包插件](#打包插件)
   - [发布到 PyPI](#发布到-pypi)
   - [贡献到主项目](#贡献到主项目)

---

## 插件基础

### 继承体系

AI PDF Agent 使用面向对象的设计，所有插件都继承自基类：

```
BasePlugin (抽象基类)
├── BaseReaderPlugin (读取器插件基类)
│   └── TextReaderPlugin, TableReaderPlugin, ImageReaderPlugin, ...
├── BaseConverterPlugin (转换器插件基类)
│   └── ToMarkdownPlugin, ToHtmlPlugin, ToJsonPlugin, ...
└── BaseOcrPlugin (OCR 插件基类)
    └── TesseractOcrPlugin, PaddleOcrPlugin, ...
```

### 核心接口

#### BasePlugin - 所有插件的基类

所有插件必须继承 `BasePlugin` 并实现核心接口：

```python
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType

class MyPlugin(BasePlugin):
    # ========== 插件元数据（必须定义） ==========
    name: str                          # 插件名称（唯一标识）
    version: str                       # 插件版本
    description: str                   # 插件描述
    plugin_type: PluginType           # 插件类型
    author: str = ""                   # 作者
    homepage: str = ""                # 主页
    license: str = "MIT"              # 许可证
    
    # ========== 插件依赖（可选） ==========
    dependencies: List[str] = []      # Python 依赖，如 ["paddleocr>=2.7", "numpy>=1.24"]
    system_dependencies: List[str] = []  # 系统依赖，如 ["tesseract", "poppler"]
    
    # ========== 核心接口（必须实现） ==========
    @abstractmethod
    def is_available(self) -> bool:
        """检查插件是否可用（依赖是否满足）"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行插件核心功能"""
        pass
```

#### 插件类型

```python
from core.plugin_system.plugin_type import PluginType

PluginType.READER      # 读取器插件 - 提取 PDF 内容
PluginType.CONVERTER   # 转换器插件 - 格式转换
PluginType.OCR         # OCR 插件 - 文字识别
PluginType.RAG         # RAG 插件 - 检索增强生成
PluginType.ENCRYPT     # 加密插件 - PDF 加密/解密
PluginType.COMPRESS    # 压缩插件 - 文件压缩
PluginType.EDIT        # 编辑插件 - 文档编辑
PluginType.ANALYZE     # 分析插件 - 文档分析
PluginType.CUSTOM      # 自定义插件
```

### 生命周期

插件的生命周期包括以下阶段：

```
1. 发现 (Discovery)   - 扫描插件目录，发现插件文件
2. 加载 (Loading)     - 动态导入插件模块，实例化插件类
3. 初始化 (Init)      - 调用 __init__，执行插件初始化
4. 可用性检查 (Check) - 调用 is_available()，检查依赖是否满足
5. 配置 (Config)      - 加载插件配置
6. 使用 (Use)         - 调用 execute/read/convert 等方法
7. 卸载 (Unload)      - 调用 on_unload()，清理资源
```

#### 生命周期钩子

```python
class MyPlugin(BasePlugin):
    def on_load(self) -> None:
        """插件加载时调用"""
        self._logger.info(f"Plugin {self.name} loaded")
    
    def on_unload(self) -> None:
        """插件卸载时调用"""
        self._logger.info(f"Plugin {self.name} unloaded")
    
    def on_config_update(self, old_config: Dict, new_config: Dict) -> None:
        """配置更新时调用"""
        self._config = new_config
        self._logger.info(f"Plugin {self.name} config updated")
```

---

## Reader 插件开发

### 继承 BaseReaderPlugin

Reader 插件用于从 PDF 中提取内容（文本、表格、图片、元数据等）。

```python
from core.plugin_system.base_reader_plugin import BaseReaderPlugin
from core.plugin_system.plugin_type import PluginType

class MyReaderPlugin(BaseReaderPlugin):
    plugin_type = PluginType.READER
    
    def __init__(self, pdf_engine=None):
        super().__init__(pdf_engine)
        # 初始化逻辑
```

### 实现 read 方法

`read` 方法是 Reader 插件的核心，必须实现以下签名：

```python
def read(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
    """
    读取 PDF 内容
    
    Args:
        pdf_path: PDF 文件路径
        **kwargs: 额外参数
            - page: int - 指定页码（1-based）
            - page_range: Tuple[int, int] - 页面范围 (start, end)
            - pages: List[int] - 多个页码列表
    
    Returns:
        Dict[str, Any]: 结构化数据
            {
                "success": bool,
                "content": Any,  # 提取的内容
                "metadata": Dict,  # 文档元数据
                "error": Optional[str]  # 错误信息
            }
    """
```

### 实现 validate 方法

`validate` 方法用于验证 PDF 文件：

```python
def validate(self, pdf_path: str) -> Tuple[bool, Optional[str]]:
    """
    验证 PDF 文件
    
    Args:
        pdf_path: PDF 文件路径
    
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
```

### Reader 插件完整示例

```python
"""自定义文本读取插件示例"""

import os
from typing import Dict, Optional, Any, Tuple
import logging

from core.plugin_system.base_reader_plugin import BaseReaderPlugin
from core.plugin_system.plugin_type import PluginType

logger = logging.getLogger(__name__)


class CustomTextReaderPlugin(BaseReaderPlugin):
    """自定义文本读取插件"""

    # ========== 插件元数据 ==========
    name = "custom_text_reader"
    version = "1.0.0"
    description = "自定义文本读取插件，支持高级文本提取"
    plugin_type = PluginType.READER
    author = "你的名字"
    homepage = "https://github.com/yourname/custom-text-reader"
    license = "MIT"

    # ========== 插件依赖 ==========
    dependencies = ["pymupdf>=1.23.0"]
    system_dependencies = []

    def __init__(self, pdf_engine=None):
        """
        初始化插件

        Args:
            pdf_engine: PDF 引擎实例（可选）
        """
        super().__init__(pdf_engine)

        # 如果没有传入引擎，则创建默认的 PyMuPDF 引擎
        if self.pdf_engine is None:
            try:
                from core.engine.pymupdf_engine import PyMuPDFEngine
                self.pdf_engine = PyMuPDFEngine()
            except ImportError as e:
                logger.warning(f"Failed to import PyMuPDFEngine: {e}")
                self.pdf_engine = None

    def is_available(self) -> bool:
        """检查插件是否可用"""
        if self.pdf_engine is None:
            return False

        # 检查依赖
        deps_ok, missing_deps = self.check_dependencies()
        if not deps_ok:
            logger.warning(f"Missing dependencies: {missing_deps}")
            return False

        return True

    def validate(self, pdf_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证 PDF 文件

        Args:
            pdf_path: PDF 文件路径

        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        if not os.path.exists(pdf_path):
            return False, f"文件不存在: {pdf_path}"

        if not pdf_path.lower().endswith(".pdf"):
            return False, "不是 PDF 文件"

        # 尝试打开文件验证
        try:
            doc = self.pdf_engine.open(pdf_path)
            if doc.page_count == 0:
                self.pdf_engine.close(doc)
                return False, "PDF 文件为空"
            self.pdf_engine.close(doc)
        except Exception as e:
            return False, f"无法打开 PDF 文件: {str(e)}"

        return True, None

    def read(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        读取 PDF 文本内容

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - page: int - 指定页码（1-based）
                - page_range: Tuple[int, int] - 页面范围 (start, end)
                - pages: List[int] - 多个页码列表

        Returns:
            Dict[str, Any]: 结构化结果
        """
        result = {
            "success": False,
            "content": "",
            "metadata": {},
            "page_count": 0,
            "pages_extracted": [],
            "error": None,
        }

        try:
            # 验证文件
            is_valid, error_msg = self.validate(pdf_path)
            if not is_valid:
                result["error"] = error_msg
                return result

            # 打开文档
            doc = self.pdf_engine.open(pdf_path)
            page_count = doc.page_count
            result["page_count"] = page_count

            # 获取元数据
            result["metadata"] = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "keywords": doc.metadata.get("keywords", ""),
            }

            # 确定要提取的页面
            pages_to_extract = self._get_pages_to_extract(page_count, **kwargs)
            result["pages_extracted"] = pages_to_extract

            # 提取文本
            texts = []
            for page_num in pages_to_extract:
                page = doc[page_num - 1]  # 0-based index
                text = page.get_text()
                texts.append(text)

            # 合并文本
            result["content"] = "\n\n".join(texts)
            result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error reading PDF: {e}")

        finally:
            if 'doc' in locals():
                self.pdf_engine.close(doc)

        return result

    def _get_pages_to_extract(self, page_count: int, **kwargs) -> list:
        """
        根据参数确定要提取的页面

        Args:
            page_count: PDF 总页数
            **kwargs: 参数

        Returns:
            list: 要提取的页码列表（1-based）
        """
        # 指定单页
        if 'page' in kwargs:
            page = kwargs['page']
            if 1 <= page <= page_count:
                return [page]

        # 指定页面范围
        if 'page_range' in kwargs:
            start, end = kwargs['page_range']
            start = max(1, start)
            end = min(page_count, end)
            return list(range(start, end + 1))

        # 指定多个页面
        if 'pages' in kwargs:
            pages = kwargs['pages']
            return [p for p in pages if 1 <= p <= page_count]

        # 默认提取所有页面
        return list(range(1, page_count + 1))
```

---

## Converter 插件开发

### 继承 BaseConverterPlugin

Converter 插件用于将 PDF 转换为其他格式（Markdown、HTML、JSON、EPUB 等）。

```python
from core.plugin_system.base_converter_plugin import BaseConverterPlugin
from core.plugin_system.plugin_type import PluginType

class MyConverterPlugin(BaseConverterPlugin):
    plugin_type = PluginType.CONVERTER
    
    def __init__(self, pdf_engine=None):
        super().__init__(pdf_engine)
        # 初始化逻辑
```

### 实现 convert 方法

`convert` 方法是 Converter 插件的核心，必须实现以下签名：

```python
def convert(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
    """
    转换 PDF

    Args:
        pdf_path: PDF 文件路径
        **kwargs: 额外参数
            - output_path: str - 输出文件路径
            - page: int - 指定页码（1-based）
            - page_range: Tuple[int, int] - 页面范围
            - pages: List[int] - 多个页码列表
    
    Returns:
        Dict[str, Any]: 转换结果
            {
                "success": bool,
                "content": str,  # 转换后的内容
                "output_path": str,  # 输出文件路径
                "pages": int,  # 转换的页数
                "error": Optional[str]
            }
    """
```

### Converter 插件完整示例

```python
"""自定义 Markdown 转换器插件示例"""

import os
import logging
from typing import Dict, Optional, Any, Tuple

import fitz  # PyMuPDF

from core.plugin_system.base_converter_plugin import BaseConverterPlugin
from core.plugin_system.plugin_type import PluginType

logger = logging.getLogger(__name__)


class CustomMarkdownConverterPlugin(BaseConverterPlugin):
    """自定义 Markdown 转换器插件"""

    # ========== 插件元数据 ==========
    name = "custom_to_markdown"
    version = "1.0.0"
    description = "自定义 Markdown 转换器，支持高级格式转换"
    plugin_type = PluginType.CONVERTER
    author = "你的名字"
    homepage = "https://github.com/yourname/custom-markdown-converter"
    license = "MIT"

    # ========== 插件依赖 ==========
    dependencies = ["pymupdf>=1.24.0"]
    system_dependencies = []

    def __init__(self, pdf_engine=None):
        super().__init__(pdf_engine)
        self._heading_styles = {
            0: "#",
            1: "#",
            2: "##",
            3: "###",
            4: "####",
            5: "#####",
            6: "######",
        }

    def is_available(self) -> bool:
        """检查插件是否可用"""
        try:
            import fitz
            return True
        except ImportError:
            return False

    def validate(self, pdf_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证 PDF 文件是否可转换

        Args:
            pdf_path: PDF 文件路径

        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        if not os.path.exists(pdf_path):
            return False, f"文件不存在: {pdf_path}"

        if not pdf_path.lower().endswith(".pdf"):
            return False, "不是 PDF 文件"

        try:
            doc = fitz.open(pdf_path)
            if doc.page_count == 0:
                doc.close()
                return False, "PDF 文件为空"
            doc.close()
        except Exception as e:
            return False, f"无法打开 PDF 文件: {str(e)}"

        return True, None

    def convert(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        转换 PDF 到 Markdown

        Args:
            pdf_path: PDF 文件路径
            **kwargs: 额外参数
                - output_path: str - 输出文件路径
                - page: int - 指定页码
                - page_range: Tuple[int, int] - 页面范围
                - pages: List[int] - 多个页码列表

        Returns:
            Dict[str, Any]: 转换结果
        """
        result = {
            "success": False,
            "content": "",
            "output_path": "",
            "pages": 0,
            "error": None,
        }

        try:
            # 验证文件
            is_valid, error_msg = self.validate(pdf_path)
            if not is_valid:
                result["error"] = error_msg
                return result

            # 打开文档
            doc = fitz.open(pdf_path)
            total_pages = doc.page_count

            # 确定要转换的页面
            pages_to_convert = self._get_pages_to_convert(total_pages, **kwargs)
            result["pages"] = len(pages_to_convert)

            # 转换为 Markdown
            markdown_parts = []
            for page_num in pages_to_convert:
                page = doc[page_num - 1]
                markdown_part = self._convert_page_to_markdown(page)
                markdown_parts.append(markdown_part)

            # 合并 Markdown
            result["content"] = "\n\n---\n\n".join(markdown_parts)
            result["success"] = True

            # 保存到文件
            output_path = kwargs.get("output_path")
            if output_path:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result["content"])
                result["output_path"] = output_path

            doc.close()

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error converting to Markdown: {e}")

        return result

    def _convert_page_to_markdown(self, page) -> str:
        """
        将单个页面转换为 Markdown

        Args:
            page: PyMuPDF 页面对象

        Returns:
            str: Markdown 内容
        """
        # 获取文本块
        blocks = page.get_text("blocks")
        
        markdown_lines = []
        
        for block in blocks:
            if block[6] == 0:  # 文本块
                text = block[4]
                
                # 简单的标题检测（根据字体大小）
                font_size = block[7]
                if font_size > 20:
                    markdown_lines.append(f"# {text}")
                elif font_size > 16:
                    markdown_lines.append(f"## {text}")
                elif font_size > 14:
                    markdown_lines.append(f"### {text}")
                else:
                    markdown_lines.append(text)
        
        return "\n".join(markdown_lines)

    def _get_pages_to_convert(self, page_count: int, **kwargs) -> list:
        """
        根据参数确定要转换的页面

        Args:
            page_count: PDF 总页数
            **kwargs: 参数

        Returns:
            list: 要转换的页码列表（1-based）
        """
        # 指定单页
        if 'page' in kwargs:
            page = kwargs['page']
            if 1 <= page <= page_count:
                return [page]

        # 指定页面范围
        if 'page_range' in kwargs:
            start, end = kwargs['page_range']
            start = max(1, start)
            end = min(page_count, end)
            return list(range(start, end + 1))

        # 指定多个页面
        if 'pages' in kwargs:
            pages = kwargs['pages']
            return [p for p in pages if 1 <= p <= page_count]

        # 默认转换所有页面
        return list(range(1, page_count + 1))
```

---

## 插件注册和加载

### 插件目录结构

插件必须放在正确的目录才能被自动发现：

```
ai-pdf-agent/
├── plugins/                    # 内置插件目录
│   ├── readers/               # 读取器插件
│   │   ├── text_reader.py
│   │   ├── table_reader.py
│   │   ├── image_reader.py
│   │   └── custom_reader.py   # 你的自定义读取器
│   ├── converters/            # 转换器插件
│   │   ├── to_markdown.py
│   │   ├── to_html.py
│   │   └── custom_converter.py  # 你的自定义转换器
│   └── ocr/                   # OCR 插件
│       └── custom_ocr.py       # 你的自定义 OCR
```

### 手动注册

你也可以手动注册插件：

```python
from core.plugin_system.plugin_manager import PluginManager
from plugins.readers.custom_reader import CustomReaderPlugin

# 获取插件管理器
manager = PluginManager()

# 创建插件实例
plugin = CustomReaderPlugin()

# 手动注册
manager.register_plugin(plugin)

# 使用插件
result = plugin.read("document.pdf")
```

### 自动发现

插件管理器会自动发现和加载插件：

```python
from core.plugin_system.plugin_manager import PluginManager

# 获取插件管理器
manager = PluginManager()

# 发现所有插件
plugin_paths = manager.discover_plugins()
print(f"Found {len(plugin_paths)} plugins")

# 加载所有插件
for plugin_path in plugin_paths:
    plugin = manager.load_plugin(plugin_path)
    if plugin:
        print(f"Loaded: {plugin.name} v{plugin.version}")

# 列出已加载的插件
plugins = manager.list_plugins()
for name, plugin in plugins.items():
    print(f"{name}: {plugin.description}")
```

---

## 测试插件

### 单元测试

使用 pytest 编写单元测试：

```python
"""自定义 Reader 插件单元测试"""

import os
import pytest
import tempfile
import fitz

from plugins.readers.custom_reader import CustomReaderPlugin


class TestCustomReaderPlugin:
    """CustomReaderPlugin 测试类"""
    
    @pytest.fixture
    def plugin(self):
        """创建插件实例"""
        return CustomReaderPlugin()
    
    @pytest.fixture
    def sample_pdf_path(self):
        """创建示例 PDF 文件"""
        # 创建临时 PDF 文件
        doc = fitz.open()
        
        # 添加第一页
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "First Page Content", fontsize=12)
        
        # 添加第二页
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "Second Page Content", fontsize=12)
        
        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc.save(temp_file.name)
        doc.close()
        
        yield temp_file.name
        
        # 清理
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
    
    def test_plugin_is_available(self, plugin):
        """测试插件是否可用"""
        assert plugin.is_available()
    
    def test_read_all_pages(self, plugin, sample_pdf_path):
        """测试读取所有页面"""
        result = plugin.read(sample_pdf_path)
        
        assert result["success"] is True
        assert result["content"] is not None
        assert result["page_count"] == 2
        assert result["error"] is None
        assert "First Page Content" in result["content"]
        assert "Second Page Content" in result["content"]
    
    def test_read_single_page(self, plugin, sample_pdf_path):
        """测试读取单个页面"""
        result = plugin.read(sample_pdf_path, page=1)
        
        assert result["success"] is True
        assert result["content"] is not None
        assert result["pages_extracted"] == [1]
        assert "First Page Content" in result["content"]
        assert "Second Page Content" not in result["content"]
    
    def test_read_page_range(self, plugin, sample_pdf_path):
        """测试读取页面范围"""
        result = plugin.read(sample_pdf_path, page_range=(1, 1))
        
        assert result["success"] is True
        assert result["pages_extracted"] == [1]
    
    def test_validate_valid_file(self, plugin, sample_pdf_path):
        """测试验证有效文件"""
        is_valid, error = plugin.validate(sample_pdf_path)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_invalid_file(self, plugin):
        """测试验证无效文件"""
        is_valid, error = plugin.validate("/nonexistent/file.pdf")
        
        assert is_valid is False
        assert error is not None
    
    def test_metadata_extraction(self, plugin, sample_pdf_path):
        """测试元数据提取"""
        result = plugin.read(sample_pdf_path)
        
        assert "metadata" in result
        assert isinstance(result["metadata"], dict)
```

### 集成测试

测试插件与 CLI 的集成：

```python
"""自定义 Reader 插件集成测试"""

import pytest
import subprocess
import json
import tempfile
import fitz


class TestCustomReaderIntegration:
    """CustomReaderPlugin 集成测试"""
    
    @pytest.fixture
    def sample_pdf_path(self):
        """创建示例 PDF 文件"""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), "Test Content", fontsize=12)
        
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        doc.save(temp_file.name)
        doc.close()
        
        yield temp_file.name
        
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
    
    def test_cli_integration(self, sample_pdf_path):
        """测试 CLI 集成"""
        # 调用 CLI 命令
        result = subprocess.run(
            ["python", "-m", "ai.pdf", "text", sample_pdf_path, "--json"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        # 解析 JSON 输出
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "Test Content" in data["text"]
```

### 测试覆盖率

运行测试并生成覆盖率报告：

```bash
# 运行所有测试
pytest

# 运行特定插件测试
pytest tests/test_custom_reader.py

# 生成覆盖率报告
pytest --cov=plugins.readers.custom_reader --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html

# 生成终端覆盖率报告
pytest --cov=plugins.readers.custom_reader --cov-report=term-missing
```

---

## 发布插件

### 打包插件

创建插件的独立包：

```
my-custom-reader/
├── README.md              # 插件文档
├── LICENSE                # 许可证
├── setup.py               # 安装脚本
├── requirements.txt       # 依赖
├── my_custom_reader/      # 插件代码
│   ├── __init__.py
│   └── plugin.py
└── tests/                 # 测试
    └── test_plugin.py
```

**setup.py 示例：**

```python
from setuptools import setup, find_packages

setup(
    name="ai-pdf-custom-reader",
    version="1.0.0",
    description="Custom reader plugin for AI PDF Agent",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourname/ai-pdf-custom-reader",
    packages=find_packages(),
    install_requires=[
        "pymupdf>=1.23.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
```

### 发布到 PyPI

```bash
# 构建发布包
python -m pip install --upgrade build
python -m build

# 上传到 PyPI（需要注册账号）
python -m pip install --upgrade twine
python -m twine upload dist/*

# 或者上传到测试 PyPI
python -m twine upload --repository testpypi dist/*
```

### 贡献到主项目

如果你想将插件贡献到 AI PDF Agent 主项目：

1. **Fork 项目**
   ```bash
   git clone https://github.com/yourname/ai-pdf-agent.git
   cd ai-pdf-agent
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/custom-reader-plugin
   ```

3. **添加插件文件**
   ```bash
   # 将插件复制到 plugins/readers/ 目录
   cp my_custom_reader/plugin.py plugins/readers/custom_reader.py
   ```

4. **添加测试**
   ```bash
   # 将测试复制到 tests/ 目录
   cp tests/test_plugin.py tests/test_custom_reader.py
   ```

5. **提交更改**
   ```bash
   git add plugins/readers/custom_reader.py
   git add tests/test_custom_reader.py
   git commit -m "feat: add custom reader plugin"
   ```

6. **推送到分支**
   ```bash
   git push origin feature/custom-reader-plugin
   ```

7. **创建 Pull Request**
   - 访问 https://github.com/ai-agent/ai-pdf-agent
   - 点击 "New Pull Request"
   - 选择你的分支
   - 填写 PR 描述

---

## 📚 参考资源

### 现有插件示例

- **TextReaderPlugin**: `plugins/readers/text_reader.py`
- **TableReaderPlugin**: `plugins/readers/table_reader.py`
- **ImageReaderPlugin**: `plugins/readers/image_reader.py`
- **ToMarkdownPlugin**: `plugins/converters/to_markdown.py`
- **ToHtmlPlugin**: `plugins/converters/to_html.py`
- **ToJsonPlugin**: `plugins/converters/to_json.py`

### 核心类参考

- **BasePlugin**: `core/plugin_system/base_plugin.py`
- **BaseReaderPlugin**: `core/plugin_system/base_reader_plugin.py`
- **BaseConverterPlugin**: `core/plugin_system/base_converter_plugin.py`
- **PluginManager**: `core/plugin_system/plugin_manager.py`

### 测试示例

- **TextReaderPlugin 测试**: `tests/test_text_reader.py`
- **TableReaderPlugin 测试**: `tests/test_table_reader.py`
-` ToMarkdownPlugin 测试`: `tests/test_to_markdown.py`

---

## 🤝 贡献

欢迎贡献插件！请遵循以下准则：

1. **代码风格**: 使用 Black 格式化代码
2. **测试覆盖**: 确保测试覆盖率 > 80%
3. **文档**: 编写清晰的文档和示例
4. **许可证**: 使用 MIT License
5. **兼容性**: 支持 Python 3.8+

---

## 📞 获取帮助

- **GitHub Issues**: https://github.com/ai-agent/ai-pdf-agent/issues
- **Discussions**: https://github.com/ai-agent/ai-pdf-agent/discussions
- **Email**: support@ai-pdf-agent.com

---

**Happy Plugin Development! 🎉**

*最后更新：2026-03-03*
*版本：v1.0*
