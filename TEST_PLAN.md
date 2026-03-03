# 第一阶段测试计划 (Test Plan)

> **项目：** AI PDF Agent
> **阶段：** 第一阶段（插件化 PDF 阅读器器 + 转换器）
> **测试策略：** 测试驱动开发（TDD）
> **编写日期：** 2026-03-03

---

## 📋 测试策略

### 测试驱动开发（TDD）

1. **Red（红色）** - 编写失败的测试用例
2. **Green（绿色）** - 编写最小实现使测试通过
3. **Refactor（重构）** - 优化代码结构
3循环

### 测试金字塔

```
        /\
       /  \      端到端测试（E2E Tests）
      /____\     少量，高价值
     /      \
    /        \   集成测试（Integration Tests）
   /__________\   中等数量
  /            \
 /              \ 单元测试（Unit Tests）
/________________\ 大量，快速
```

**测试比例：**
- 单元测试：70%
- 集成测试：20%
- 端到端测试：10%

---

## 🎯 测试覆盖率目标

| 模块 | 覆盖率目标 | 当前状态 |
|------|----------|---------|
| **插件系统** | 90% | 待测试 |
| **PDF 引擎** | 85% | 待测试 |
| **阅读器插件** | 80% | 待测试 |
| **转换器插件** | 80% | 待测试 |
| **CLI 框架** | 80% | 待测试 |
| **错误处理** | 90% | 待测试 |
| **整体** | 75% | 待测试 |

---

## 🧪 单元测试（Unit Tests）

### 测试范围

- 测试单个函数/方法
- 测试单个类
- 不依赖外部系统（文件、网络、数据库）

### 插件系统测试

#### test_base_plugin.py

```测试文件：tests/test_base_plugin.py
import pytest
from core.plugin_system.base_plugin import BasePlugin
from core.plugin_system.plugin_type import PluginType


class MockPlugin(BasePlugin):
    """Mock 插件用于测试"""
    name = "mock"
    version = "1.0.0"
    description = "Mock plugin for testing"
    plugin_type = PluginType.READER


class TestBasePlugin:
    """测试插件基类"""
    
    def test_plugin_metadata(self):
        """测试插件元数据"""
        plugin = MockPlugin()
        assert plugin.name == "mock"
        assert plugin.version == "1.0.0"
        assert plugin.description == "Mock plugin for testing"
        assert plugin.plugin_type == PluginType.READER
    
    def test_lifecycle_hooks(self):
        """测试生命周期钩子"""
        plugin = MockPlugin()
        plugin.on_load()  # 应该被调用
        plugin.on_unload()  # 应该被调用
    
    def test_dependency_check(self):
        """测试依赖检查"""
        plugin = MockPlugin()
        deps_ok, missing = plugin.check_dependencies()
        assert isinstance(deps_ok, bool)
        assert isinstance(missing, list)
    
    def test_validate_input(self):
        """测试输入验证"""
        plugin = MockPlugin()
        result = plugin.validate_input(param1="value1")
        assert result is True
    
    def test_validate_output(self):
        """测试输出验证"""
        plugin = MockPlugin()
        result = plugin.validate_output({"key": "value"})
        assert result is True
    
    def test_get_metadata(self):
        """测试获取元数据"""
        plugin = MockPlugin()
        metadata = plugin.get_metadata()
        assert isinstance(metadata, dict)
        assert "name" in metadata
        assert "version" in metadata
        assert "description" in metadata
        assert "plugin_type" in metadata
```

---

#### test_plugin_manager.py

```测试文件：tests/test_plugin_manager.py
import pytest
from core.plugin_system.plugin_manager import PluginManager
from core.plugin_system.plugin_type import PluginType


class TestPluginManager:
    """测试插件管理器"""
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        manager1 = PluginManager()
        manager2 = PluginManager()
        assert manager1 is manager2
    
    def test_plugin_discovery(self):
        """测试插件发现"""
        manager = PluginManager()
        plugins = manager.discover_plugins()
        assert isinstance(plugins, list)
    
    def test_plugin_discovery_cache(self):
        """测试插件发现缓存"""
        manager = PluginManager()
        plugins1 = manager.discover_plugins()
        plugins2 = manager.discover_plugins()
        assert plugins1 == plugins2
    
    def test_plugin_discovery_force_refresh(self):
        """测试强制刷新插件发现"""
        manager = PluginManager()
        plugins1 = manager.discover_plugins()
        plugins2 = manager.discover_plugins(force_refresh=True)
        assert isinstance(plugins1, list)
        assert isinstance(plugins2, list)
    
    def test_plugin_load_unload(self):
        """测试插件加载/卸载"""
        manager = PluginManager()
        
        # 加载插件
        plugin_path = "./tests/fixtures/mock_plugin.py"
        plugin = manager.load_plugin(plugin_path)
        
        if plugin:
            assert plugin.name == "mock"
            
            # 卸载插件
            success = manager.unload_plugin("mock")
            assert success is True
    
    def test_plugin_query(self):
        """测试插件查询"""
        manager = PluginManager()
        manager.load_all_plugins()
        
        # 获取插件
        plugin = manager.get_plugin("mock")
        if plugin:
            assert plugin.name == "mock"
        
        # 列出所有插件
        plugins = manager.list_plugins()
        assert isinstance(plugins, list)
        
        # 列出特定类型的插件
        reader_plugins = manager.list_plugins(PluginType.READER)
        assert isinstance(reader_plugins, list)
    
    def test_plugin_execute(self):
        """测试插件执行"""
        manager = PluginManager()
        manager.load_all_plugins()
        
        # 执行插件
        result = manager.execute_plugin("mock", param1="value1")
        assert result is not None
    
    def test_plugin_config(self):
        """测试插件配置"""
        manager = PluginManager()
        
        # 设置配置
        success = manager.set_plugin_config("mock", {"key": "value"})
        assert success is True
        
        # 获取配置
        config = manager.get_plugin_config("mock")
        assert isinstance(config, dict)
    
    def test_hook_system(self):
        """测试 Hook 系统"""
        manager = PluginManager()
        
        calls = []
        
        def callback():
            calls.append("called")
        
        # 注册 Hook
        manager.register_hook("test_event", callback)
        
        # 触发 Hook
        results = manager.trigger_hook("test_event")
        assert "called" in calls
```

---

### PDF 引擎测试

#### test_pymupdf_engine.py

```测试文件：tests/test_pymupdf_engine.py
import pytest
from core.engine.pymupdf_engine import PyMuPDFEngine


class TestPyMuPDFEngine:
    """测试 PyMuPDF 引擎"""
    
    def test_open_close_document(self):
        """测试文档打开/关闭"""
        engine = PyMuPDFEngine()
        doc = engine.open("./tests/fixtures/sample.pdf")
        assert doc is not None
        engine.close(doc)
    
    def test_get_page_count(self):
        """测试获取页数"""
        engine = PyMuPDFEngine()
        doc = engine.open("./tests/fixtures/sample.pdf")
        count = engine.get_page_count(doc)
        assert count > 0
        engine.close(doc)
    
    def test_extract_text(self):
        """测试文本提取"""
        engine = PyMuPDFEngine()
        doc = engine.open("./tests/fixtures/sample.pdf")
        
        # 提取全部文本
        text = engine.extract_text(doc)
        assert len(text) > 0
        
        # 提取指定页码范围的文本
        text_range = engine.extract_text(doc, page_range=(1, 3))
        assert len(text_range) > 0
        
        engine.close(doc)
    
    def test_extract_tables(self):
        """测试表格提取"""
        engine = PyMuPDFEngine()
        doc = engine.open("./tests/fixtures/sample.pdf")
        
        tables = engine.extract_tables(doc)
        assert isinstance(tables, list)
        
        engine.close(doc)
    
    def test_extract_images(self):
        """测试图片提取"""
        engine = PyMuPDFEngine()
        doc = engine.open("./tests/fixtures/sample.pdf")
        
        images = engine.extract_images(doc)
        assert isinstance(images, list)
        
        engine.close(doc)
    
    def test_get_metadata(self):
        """测试获取元数据"""
        engine = PyMuPDFEngine()
        doc = engine.open("./tests/fixtures/sample.pdf")
        
        metadata = engine.get_metadata(doc)
        assert isinstance(metadata, dict)
        assert "title" in metadata
        assert "author" in metadata
        assert "page_count" in metadata
        assert metadata["page_count"] > 0
        
        engine.close(doc)
    
    def test_get_structure(self):
        """测试获取结构"""
        engine = PyMuPDFEngine()
        doc = engine.open("./tests/fixtures/sample.pdf")
        
        structure = engine.get_structure(doc)
        assert isinstance(structure, dict)
        assert "title" in structure
        assert "sections" in structure
        
        engine.close(doc)
```

---

### 错误处理测试

#### test_error_handler.py

```测试文件：tests/test_error_handler.py
import pytest
from utils.error_handler import (
    AI_PDF_Error,
    ParamError,
    FileNotFoundError,
    PDFFormatError,
    ProcessError,
    PermissionError,
    PluginError,
    handle_errors,
)


class TestErrorHandling:
    """测试错误处理"""
    
    def test_error_classes(self):
        """测试错误类"""
        error = ParamError("Invalid parameter")
        assert error.exit_code == 1
        
        error = FileNotFoundError("File not found")
        assert error.exit_code == 2
        
        error = PDFFormatError("Invalid PDF format")
        assert error.exit_code == 3
        
        error = ProcessError("Processing failed")
        assert error.exit_code == 4
        
        error = PermissionError("Permission denied")
        assert error.exit_code == 5
        
        error = PluginError("Plugin error")
        assert error.exit_code == 6
    
    def test_error_handler_decorator(self):
        """测试错误处理装饰器"""
        @handle_errors
        def failing_function():
            raise ParamError("Invalid parameter")
        
        with pytest.raises(SystemExit):
            failing_function()
```

---

## 🧩 集成测试（Integration Tests）

### 测试范围

- 测试多个模块之间的交互
- 测试插件系统的完整流程
- 测试 CLI 和插件系统的集成

### 插件系统集成测试

#### test_plugin_system_integration.py

```测试文件：tests/test_plugin_system_integration.py
import pytest
from core.plugin_system.plugin_manager import PluginManager


class TestPluginSystemIntegration:
    """测试插件系统集成"""
    
    def test_plugin_lifecycle(self):
        """测试插件生命周期"""
        manager = PluginManager()
        
        # 加载所有插件
        count = manager.load_all_plugins()
        assert count > 0
        
        # 查询插件
        plugin_names = manager.list_plugin_names()
        assert len(plugin_names) > 0
        
        # 获取插件信息
        for name in plugin_names:
            info = manager.get_plugin_info(name)
            assert info is not None
            assert info["name"] == name
            assert info["loaded"] is True
    
    def test_plugin_execution_flow(self):
        """测试插件执行流程"""
        manager = PluginManager()
        manager.load_all_plugins()
        
        # 执行插件
        for name in manager.list_plugin_names():
            try:
                result = manager.execute_plugin(name)
                assert result is not None
            except Exception as e:
                pytest.fail(f"Plugin {name} execution failed: {e}")
```

---

### PDF 引擎集成测试

#### test_pdf_engine_integration.py

```测试文件：tests/test_pdf_engine_integration.py
import pytest
from core.engine.pymupdf_engine import PyMuPDFEngine


class TestPDFEngineIntegration:
    """测试 PDF 引擎集成"""
    
    def test_full_document_processing(self):
        """测试完整文档处理流程"""
        engine = PyMuPDFEngine()
        doc = engine.open("./tests/fixtures/sample.pdf")
        
        # 获取页数
        page_count = engine.get_page_count(doc)
        assert page_count > 0
        
        # 提取文本
        text = engine.extract_text(doc)
        assert len(text) > 0
        
        # 提取表格
        tables = engine.extract_tables(doc)
        assert isinstance(tables, list)
        
        # 提取图片
        images = engine.extract_images(doc)
        assert isinstance(images, list)
        
        # 获取元数据
        metadata = engine.get_metadata(doc)
        assert isinstance(metadata, dict)
        
        # 获取结构
        structure = engine.get_structure(doc)
        assert isinstance(structure, dict)
        
        engine.close(doc)
```

---

### CLI 集成测试

#### test_cli_integration.py

```测试文件：tests/test_cli_integration.py
from click.testing import CliRunner
from cli.main import cli


class TestCLIIntegration:
    """测试 CLI 集成"""
    
    def test_cli_help(self):
        """测试帮助信息"""
命令"""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "AI PDF Agent" in result.output
    
    def test_plugin_list_command(self):
        """测试插件列表命令"""
        runner = CliRunner()
        result = runner.invoke(cli, ["plugin", "list"])
        assert result.exit_code == 0
    
    def test_plugin_list_json_output(self):
        """测试插件列表 JSON 输出"""
        runner = CliRunner()
        result = runner.invoke(cli, ["plugin", "list", "--json"])
        assert result.exit_code == 0
        import json
        json.loads(result.output)  # 验证 JSON 格式
    
    def test_text_command(self):
        """测试文本读取命令"""
        runner = CliRunner()
        result = runner.invoke(cli, [
            "text",
            "./tests/fixtures/sample.pdf",
            "--json"
        ])
        assert result.exit_code == 0
        import json
        data = json.loads(result.output)
        assert "text" in data
```

---

## 🎯 端到端测试（End-to-End Tests）

### 测试范围

- 测试完整的用户工作流
- 测试从 CLI 到插件到 PDF 引擎的完整流程
- 使用真实的 PDF 文件

#### test_e2e.py

```测试文件：tests/test_e2e.py
from click.testing import CliRunner
from cli.main import cli
import json
import os


class TestEndToEnd:
    """测试端到端流程"""
    
    def test_e2e_text_extraction(self):
        """测试端到端文本提取"""
        runner = CliRunner()
        result = runner.invoke(cli, [
            "text",
            "./tests/fixtures/sample.pdf",
            "-o", "/tmp/output.txt"
        ])
        assert result.exit_code == 0
        assert os.path.exists("/tmp/output.txt")
    
    def test_e2e_markdown_conversion(self):
        """测试端到端 Markdown �转换"""
        runner = CliRunner()
        result = runner.invoke(cli, [
            "to-markdown",
            "./tests/fixtures/sample.pdf",
            "-o", "/tmp/output.md"
        ])
        assert result.exit_code == 0
        assert os.path.exists("/tmp/output.md")
    
    def test_e2e_json_conversion(self):
        """测试端到端 JSON 转换"""
        runner = CliRunner()
        result = runner.invoke(cli, [
            "to-json",
            "./tests/fixtures/sample.pdf",
            "-o", "/tmp/output.json"
        ])
        assert result.exit_code == 0
        assert os.path.exists("/tmp/output.json")
        
        # 验证 JSON 格式
        with open("/tmp/output.json", 'r') as f:
            data = json.load(f)
        assert isinstance(data, dict)
```

---

## 📊 测试执行

### 运行所有测试

```bash
# 运行所有测试
pytest -v

# 运行所有测试并生成覆盖率报告
pytest --cov=. --cov-report=html --cov-report=term

# 运行特定测试文件
pytest tests/test_base_plugin.py -v

# 运行特定测试类
pytest tests/test_base_plugin.py::TestBasePlugin -v

# 运行特定测试方法
pytest tests/test_base_plugin.py::TestBasePlugin::test_plugin_metadata -v
```

### 运行单元测试

```bash
# 运行所有单元测试
pytest tests/ -k "unit" -v

# 运行插件系统单元测试
pytest tests/test_base_plugin.py tests/test_plugin_manager.py -v
```

### 运行集成测试

```bash
# 运行所有集成测试
pytest tests/ -k "integration" -v

# 运行插件系统集成测试
pytest tests/test_plugin_system_integration.py -v
```

### 运行端到端测试

```bash
# 运行所有端到端测试
pytest tests/ -k "e2e" -v

# 运行端到端测试
pytest tests/test_e2e.py -v
```

---

## 📈 测试覆盖率报告

### 生成覆盖率报告

```bash
# 生成 HTML 覆盖率报告
pytest --cov=. --cov-report=html

# 生成终端覆盖率报告
pytest --cov=. --cov-report=term

# 生成 XML 覆盖率报告（CI/CD）
pytest --cov=. --cov-report=xml
```

### 覆盖率报告示例

```
Name                                      Stmts   Miss  Cover
-------------------------------------------------------
cli/main.py                                 45      2    96%
cli/commands/plugin.py                       78      5    94%
cli/commands/text.py                        32      3    91%
core/plugin_system/base_plugin.py             56      4    93%
core/plugin_system/plugin_manager.py        145     12    92%
core/plugin_system/plugin_type.py              8      0   100%
core/engine/base.py                          24      2    92%
core/engine/pymupdf_engine.py              167     18    89%
utils/error_handler.py                       45      3    93%
-------------------------------------------------------
TOTAL                                      700     79    89%
```

---

## 🧪 测试数据

### 测试 PDF 文件

```
tests/fixtures/
├── sample.pdf              # 标准测试 PDF
├── text_only.pdf           # 纯文本 PDF
├── tables_only.pdf         # 表格 PDF
├── images_only.pdf         # 图片 PDF
├── complex_layout.pdf      # 复杂布局 PDF
├── encrypted.pdf           # 加密 PDF
└── malformed.pdf            # 损坏的 PDF
```

### Mock 插件

```
tests/fixtures/
└── mock_plugin.py          # Mock 插件用于测试
```

---

## ✅ 测试验收标准

### 测试覆盖率验收

- [ ] 整体测试覆盖率 > 70%
- [ ] 插件系统测试覆盖率 > 85%
- [ ] PDF 引擎测试覆盖率 > 80%
- [ ] 阅读器插件测试覆盖率 > 75%
- [ ] 转换器插件测试覆盖率 > 75%
- [ ] CLI 框架测试覆盖率 > 75%

### 测试通过验收

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 所有端到端测试通过
- [ ] 无失败的测试

### 测试质量验收

- [ ] 测试代码符合 PEP 8 规范
- [ ] 测试用例有清晰的描述
- [ ] 测试覆盖所有主要功能
- [ ] 测试使用 fixtures 和 mocks（避免外部依赖）

---

## 🔄 持续集成（CI）

### CI 配置

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v2
```

---

## 📝 测试文档

### 测试用例文档

每个测试文件应包含：

- 测试目的
- 测试场景
- 预期结果
- 依赖条件

```python
# 测试用例文档示例

def test_extract_text():
    """
    测试文本提取功能
    
    场景：
    - 打开测试 PDF 文件
    - 提取所有页面的文本内容
    
    预期结果：
    - 返回的文本长度 > 0
    - 文本包含预期的内容
    
    依赖：
    - tests/fixtures/sample.pdf 存在
    - PDF 文件包含文本内容
    """
    # 测试代码
```

---

## 🎯 测试成功指标

### 技术指标

- ✅ 测试覆盖率 > 70%
- ✅ 所有测试通过
- ✅ 无失败的测试

### 质量指标

- ✅ 测试代码质量高
- ✅ 测试用例清晰易懂
- ✅ 测试运行速度快

### 可维护性指标

- ✅ 测试易于维护
- ✅ 测试易于扩展
- ✅ 测试文档完整

---

*测试计划完成 - 第一阶段*
