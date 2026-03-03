# 第一阶段开发计划 (Development Plan)

> **项目：** AI PDF Agent
> **阶段：** 第一阶段（插件化 PDF 阅读器器 + 转换器）
> **开发方式：** 测试驱动开发（TDD）
> **编写日期：** 2026-03-03

---

## 📋 开发策略

### 测试驱动开发（TDD）流程

1. **编写测试用例** - 先写测试，明确功能需求
2. **运行测试** - 测试失败（红色）
3. **编写最小实现** - 让测试通过（绿色）
4. **重构代码** - 优化代码结构（重构）
5. **重复** - 继续下一个功能

### 开发原则

- ✅ **测试先行** - 每个功能先写测试
- ✅ **小步快跑** - 每次提交只包含一个功能
- ✅ **持续集成** - 每次提交都运行所有测试
- ✅ **代码审查** - 关键代码需要审查
- ✅ **文档同步** - 代码和文档同步更新

---

## 🎯 第一阶段开发任务分解

### Sprint 1：插件系统基础（Week 1-2）

**目标：** 实现插件系统核心框架

| 任务 | 优先级 | 预计时间 | 测试覆盖率目标 |
|------|--------|---------|----------------|
| **Task 1.1** | P0 | 1 天 | 100% |
| **Task 1.2** | P0 | 2 天 | 90% |
| **Task 1.3** | P0 | 1 天 | 80% |
| **Task 1.4** | P0 | 2 天 | 85% |
| **Task 1.5** | P0 | 1 天 | 75% |

#### Task 1.1：插件基类（BasePlugin）

**功能：**
- 插件元数据（name、version、description、plugin_type）
- 生命周期钩子（on_load、on_unload、on_config_update）
- 依赖检查（check_dependencies）
- 输入输出验证（validate_input、validate_output）
- 元数据获取（get_metadata）

**TDD 流程：**
1. 编写 `test_base_plugin.py`
   - 测试插件元数据
   - 测试生命周期钩子
   - 测试依赖检查
   - 测试输入输出验证
2. 实现 `BasePlugin` 类
3. 运行测试，确保 100% 通过

**测试用例：**
```python
# tests/test_base_plugin.py
def test_plugin_metadata():
    """测试插件元数据"""
    plugin = MockPlugin()
    assert plugin.name == "mock"
    assert plugin.version == "1.0.0"

def test_lifecycle_hooks():
    """测试生命周期钩子"""
    plugin = MockPlugin()
    plugin.on_load()  # 应该被调用
    plugin.on_unload()  # 应该被调用

def test_dependency_check():
    """测试依赖检查"""
    plugin = MockPlugin()
    deps_ok, missing = plugin.check_dependencies()
    assert isinstance(deps_ok, bool)
    assert isinstance(missing, list)
```

---

#### Task 1.2：插件管理器（PluginManager）

**功能：**
- 单例模式
- 插件发现（discover_plugins）
- 插件加载（load_plugin、load_all_plugins）
- 插件卸载（unload_plugin）
- 插件查询（get_plugin、list_plugins）
- 插件执行（execute_plugin）
- 插件配置管理（load_plugin_config、save_plugin_config）
- Hook 系统（register_hook、trigger_hook）

**TDD 流程：**
1. 编写 `test_plugin_manager.py`
   - 测试单例模式
   - 测试插件发现
   - 测试插件加载/卸载
   - 测试插件查询
   - 测试插件执行
   - 测试配置管理
   - 测试 Hook 系统
2. 实现 `PluginManager` 类
3. 运行测试，确保 90%+ 通过

**测试用例：**
```python
# tests/test_plugin_manager.py
def test_singleton_pattern():
    """测试单例模式"""
    manager1 = PluginManager()
    manager2 = PluginManager()
    assert manager1 is manager2

def test_plugin_discovery():
    """测试插件发现"""
    manager = PluginManager()
    plugins = manager.discover_plugins()
    assert isinstance(plugins, list)

def test_plugin_load_unload():
    """测试插件加载/卸载"""
    manager = PluginManager()
    plugin_path = "./tests/fixtures/mock_plugin.py"
    plugin = manager.load_plugin(plugin_path)
    assert plugin is not None
    
    success = manager.unload_plugin("mock")
    assert success

def test_hook_system():
    """测试 Hook 系统"""
    manager = PluginManager()
    calls = []
    
    def callback():
        calls.append("called")
    
    manager.register_hook("test_event", callback)
    manager.trigger_hook("test_event")
    
    assert "called" in calls
```

---

#### Task 1.3：插件类型枚举（PluginType）

**功能：**
- 定义所有插件类型
- 提供插件类型说明

**TDD 流程：**
1. 编写 `test_plugin_type.py`
   - 测试插件类型枚举
   - 测试插件类型说明
2. 实现 `PluginType` 枚举
3. 运行测试，确保 100% 通过

**测试用例：**
```python
# tests/test_plugin_type.py
def test_plugin_type_enum():
    """测试插件类型枚举"""
    assert PluginType.READER.value == "reader"
    assert PluginType.CONVERTER.value == "converter"
```

---

#### Task 1.4：错误处理系统

**功能：**
- 标准化错误类（AI_PDF_Error 及其子类）
- 错误处理装饰器（handle_errors）
- 标准化退出码（0-6）



**TDD 流程：**
1. 编写 `test_error_handler.py`
   - 测试错误类
   - 测试错误处理装饰器
   - 测试退出码
2. 实现错误处理系统
3. 运行测试，确保 85%+ 通过

**测试用例：**
```python
# tests/test_error_handler.py
def test_error_classes():
    """测试错误类"""
    error = ParamError("Invalid parameter")
    assert error.exit_code == 1
    
    error = FileNotFoundError("File not found")
    assert error.exit_code == 2

def test_error_handler_decorator():
    """测试错误处理装饰器"""
    @handle_errors
    def failing_function():
        raise ParamError("Invalid parameter")
    
    with pytest.raises(SystemExit):
        failing_function()
```

---

#### Task 1.5：插件系统集成测试

**功能：**
- 端到端测试插件系统
- 测试插件生命周期
- 测试插件配置持久化

**TDD 流程：**
1. 编写 `test_plugin_system_integration.py`
2. 运行集成测试
3. 修复发现的问题

**测试用例：**
```python
# tests/test_plugin_system_integration.py
def test_plugin_lifecycle():
    """测试插件生命周期"""
    manager = PluginManager()
    manager.load_all_plugins()
    
    # 加载插件
    plugin = manager.get_plugin("mock")
    assert plugin is not None
    
    # 执行插件
    result = manager.execute_plugin("mock")
    assert result is not None
    
    # 卸载插件
    success = manager.unload_plugin("mock")
    assert success
```

---

### Sprint 2：PDF 引擎（Week 2-3）

**目标：** 实现 PDF 引擎抽象层和 PyMuPDF 实现

| 任务 | 优先级 | 预计时间 | 测试覆盖率目标 |
|------|--------|---------|----------------|
| **Task 2.1** | P0 | 1 天 | 100% |
| **Task 2.2** | P0 | 3 天 | 85% |
| **Task 2.3** | P0 | 1 天 | 80% |

#### Task 2.1：PDF 引擎抽象类（BasePDFEngine）

**功能：**
- 定义统一的 PDF 引擎接口
- 文档打开/关闭
- 页数获取
- 文本提取
- 表格提取
- 图片提取
- 元数据读取
- 结构读取

**TDD 流程：**
1. 编写 `test_base_pdf_engine.py`
   - 测试抽象方法
2. 实现 `BasePDFEngine` 类
3. 运行测试，确保 100% 通过

---

#### Task 2.2：PyMuPDF 引擎实现

**功能：**
- 使用 PyMuPDF 实现所有 PDF 引擎接口
- 文本提取
- 表格提取（使用 pdfplumber）
- 图片提取
- 元数据读取
- 结构读取

**TDD 流程：**
1. 编写 `test_pymupdf_engine.py`
   - 测试文档打开/关闭
   - 测试页数获取
   - 测试文本提取
   - 测试表格提取
   - 测试图片提取
   - 测试元数据读取
   - 测试结构读取
2. 实现 `PyMuPDFEngine` 类
3. 运行测试，确保 85%+ 通过

**测试用例：**
```python
# tests/test_pymupdf_engine.py
def test_open_close_document():
    """测试文档打开/关闭"""
    engine = PyMuPDFEngine()
    doc = engine.open("./tests/fixtures/sample.pdf")
    assert doc is not None
    engine.close(doc)

def test_get_page_count():
    """测试获取页数"""
    engine = PyMuPDFEngine()
    doc = engine.open("./tests/fixtures/sample.pdf")
    count = engine.get_page_count(doc)
    assert count > 0
    engine.close(doc)

def test_extract_text():
    """测试文本提取"""
    engine = PyMuPDFEngine()
    doc = engine.open("./tests/fixtures/sample.pdf")
    text = engine.extract_text(doc)
    assert len(text) > 0
    engine.close(doc)
```

---

#### Task 2.3：PDF 引擎集成测试

**功能：**
- 端到端测试 PDF 引擎
- 测试各种 PDF 文件（纯文本、表格、图片）

**TDD 流程：**
1. 编写 `test_pdf_engine_integration.py`
2. 使用多种测试 PDF 文件
3. 运行集成测试

---

### Sprint 3：阅读器插件（Week 3-4）

**目标：** 实现 5 个阅读器插件

| 任务 | 优先级 | 预计时间 | 测试覆盖率目标 |
|------|--------|---------|----------------|
| **Task 3.1** | P0 | 2 天 | 85% |
| **Task 3.2** | P0 | 2 天 | 85% |
| **Task 3.3** | P0 | 2 天 | 85% |
| **Task 3.4** | P0 | 1 天 | 80% |
| **Task 3.5** | P0 | 1 天 | 80% |

#### Task 3.1：文本读取插件（read-text）

**功能：**
- 提取 PDF 文本内容
- 支持页码范围
- 支持结构化输出

**TDD 流程：**
1. 编写 `test_read_text_plugin.py`
2. 实现 `TextReaderPlugin` 类
3. 运行测试，确保 85%+ 通过

**测试用例：**
```python
# tests/test_read_text_plugin.py
def test_extract_text():
    """测试文本提取"""
    manager = PluginManager()
    manager.load_all_plugins()
    
    result = manager.execute_plugin("read-text", pdf_path="./tests/fixtures/sample.pdf")
    assert "text" in result
    assert len(result["text"]) > 0

def test_extract_text_with_page_range():
    """测试按页码范围提取文本"""
    manager = PluginManager()
    manager.load_all_plugins()
    
    result = manager.execute_plugin(
        "read-text",
        pdf_path="./tests/fixtures/sample.pdf",
        page_range=(1, 5)
    )
    assert "text" in result
```

---

#### Task 3.2：表格读取插件（read-tables）

**功能：**
- 提取 PDF 表格
- 支持页码范围
- 保留表格结构

**TDD 流程：**
1. 编写 `test_read_tables_plugin.py`
2. 实现 `TableReaderPlugin` 类
3. 运行测试，确保 85%+ 通过

---

#### Task 3.3：图片读取插件（read-images）

**功能：**
- 提取 PDF 图片
- 支持页码范围
- 生成图片元数据

**TDD 流程：**
1. 编写 `test_read_images_plugin.py`
2. 实现 `ImageReaderPlugin` 类
3. 运行测试，确保 85%+ 通过

---

#### Task 3.4：元数据读取插件（read-metadata）

**功能：**
- 读取 PDF 元数据
- 生成 JSON 格式

**TDD 流程：**
1. 编写 `test_read_metadata_plugin.py`
2. 实现 `MetadataReaderPlugin` 类
3. 运行测试，确保 80%+ 通过

---

#### Task 3.5：结构读取插件（read-structure）

**功能：**
- 提取文档结构
- 生成大纲树

**TDD 流程：**
1. 编写 `test_read_structure_plugin.py`
2. 实现 `StructureReaderPlugin` 类
3. 运行测试，确保 80%+ 通过

---

### Sprint 4：转换器插件（Week 4-5）

**目标：** 实现 6 个转换器插件

| 任务 | 优先级 | 预计时间 | 测试覆盖率目标 |
|------|--------|---------|----------------|
| **Task 4.1** | P0 | 1 天 | 85% |
| **Task 4.2** | P0 | 1 天 | 85% |
| **Task 4.3** | P0 | 1 天 | 85% |
| **Task 4.4** | P0 | 1 天 | 80% |
| **Task 4.5** | P0 | 1 天 | 80% |
| **Task 4.6** | P0 | 1 天 | 80% |

#### Task 4.1：Markdown 转换器插件（to-markdown）

**功能：**
- 将 PDF 转换为 Markdown
- 保留标题、列表、表格结构

**TDD 流程：**
1. 编写 `test_to_markdown_plugin.py`
2. 实现 `ToMarkdownPlugin` 类
3. 运行测试，确保 85%+ 通过

**测试用例：**
```python

# tests/test_to_markdown_plugin.py
def test_convert_to_markdown():
    """测试转换为 Markdown"""
    manager = PluginManager()
    manager.load_all_plugins()
    
    output_path = "/tmp/output.md"
    result = manager.execute_plugin(
        "to-markdown",
        pdf_path="./tests/fixtures/sample.pdf",
        output_path=output_path
    )
    
    assert os.path.exists(output_path)
    assert result["success"]
```

---

#### Task 4.2：HTML 转换器插件（to-html）

**功能：**
- 将 PDF 转换为 HTML
- 保留基本样式和布局

**TDD 流程：**
1. 编写 `test_to_html_plugin.py`
2. 实现 `ToHtmlPlugin` 类
3. 运行测试，确保 85%+ 通过

---

#### Task 4.3：JSON 转换器插件（to-json）

**功能：**
- 将 PDF 转换为结构化 JSON
- 包含文本、表格、图片、元数据

**TDD 流程：**
1. 编写 `test_to_json_plugin.py`
2. 实现 `ToJsonPlugin` 类
3. 运行测试，确保 85%+ 通过

---

#### Task 4.4：CSV 转换器插件（to-csv）

**功能：**
- 将 PDF 表格转换为 CSV

**TDD 流程：**
1. 编写 `test_to_csv_plugin.py`
2. 实现 `ToCsvPlugin` 类
3. 运行测试，确保 80%+ 通过

---

#### Task 4.5：Image 转换器插件（to-image）

**功能：**
- 将 PDF 页面转换为图片
- 支持指定 DPI

**TDD 流程：**
1. 编写 `test_to_image_plugin.py`
2. 实现 `ToImagePlugin` 类
3. 运行测试，确保 80%+ 通过

---

#### Task 4.6：EPUB 转换器插件（to-epub）

**功能：**
- 将 PDF 转换为 EPUB

**TDD 流程：**
1. 编写 `test_to_epub_plugin.py`
2. 实现 `ToEpubPlugin` 类
3. 运行测试，确保 80%+ 通过

---

### Sprint 5：CLI 框架和命令（Week 5）

**目标：** 实现 CLI 框架和所有命令

| 任务 | 优先级 | 预计时间 | 测试覆盖率目标 |
|------|--------|---------|----------------|
| **Task 5.1** | P0 | 2 天 | 85% |
| **Task 5.2** | P0 | 3 天 | 80% |

#### Task 5.1：CLI 主框架

**功能：**
- Click 框架
- 全局选项（`--json`、`--quiet`、`--verbose`）
- 版本信息
- 错误处理

**TDD 流程：**
1. 编写 `test_cli_main.py`
2. 实现 `cli/main.py`
3. 运行测试，确保 85%+ 通过

**测试用例：**
```python
# tests/test_cli_main.py
def test_cli_help():
    """测试帮助信息"""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "AI PDF Agent" in result.output

def test_cli_json_output():
    """测试 JSON 输出"""
    runner = CliRunner()
    result = runner.invoke(cli, ["plugin", "list", "--json"])
    assert result.exit_code == 0
    # 验证 JSON 输出
    json.loads(result.output)
```

---

#### Task 5.2：CLI 子命令

**功能：**
- 插件管理命令（6 个）
- 读取命令（5 个）
- 转换命令（6 个）

**TDD 流程：**
1. 编写所有子命令测试
2. 实现所有子命令
3. 运行测试，确保 80%+ 通过

---

### Sprint 6：文档和优化（Week 6）

**目标：** 完善文档和性能优化

| 任务 | 优先级 | 预计时间 |
|------|--------|---------|
| **Task 6.1** | P0 | 2 天 |
| **Task 6.2** | P0 | 1 天 |
| **Task 6.3** | P0 | 1 天 |
| **Task 6.4** | P0 | 1 天 |

#### Task 6.1：编写文档

- 快速开始指南（QUICKSTART.md）
- 命令参考文档（COMMANDS.md）
- 插件开发指南（PLUGIN_DEV.md）
- 插件 API 文档（PLUGIN_API.md）
- 使用示例（EXAMPLES.md）

---

#### Task 6.2：性能优化

- 插件加载优化
- PDF 处理性能优化
- 内存使用优化

---

#### Task 6.3：代码审查

- 代码风格审查（flake8）
- 代码格式化（black）
- 安全性审查

---

#### Task 6.4：集成测试

- 端到端测试
- 性能测试
- 兼容性测试

---

## 📅 开发时间表

| 周次 | Sprint | 主要任务 | 预计时间 |
|------|--------|---------|---------|
| **Week 1** | Sprint 1 | 插件系统基础（Tasks 1.1-1.3） | 5 天 |
| **Week 2** | Sprint 1-2 | 插件系统集成 + PDF 引擎（Tasks 1.4-1.5, 2.1-2.2） | 5 天 |
| **Week 3** | Sprint 2-3 | PDF 引擎集成 + 阅读器插件（Tasks 2.3, 3.1-3.2） | 5 天 |
| **Week 4** | Sprint 3 | 阅读器插件 + 转换器插件（Tasks 3.3-3.5, 4.1-4.2） | 5 天 |
| **Week 5** | Sprint 4-5 | 转换器插件 + CLI 框架（Tasks 4.3-4.6, 5.1） | 5 天 |
| **Week 6** | Sprint 5-6 | CLI 命令 + 文档 + 优化（Tasks 5.2, 6.1-6.4） | 5 天 |

**总计：** 30 天（约 6 周）

---

## ✅ 开发验收标准

### 功能验收

- [ ] 插件系统运行正常（所有功能通过插件实现）
- [ ] 11 个内置插件全部正常工作
- [ ] CLI 框架运行正常（17 个命令）
- [ ] AI Agent 友好接口完整（`--json`、`--quiet`、标准化错误码）

### 质量验收

- [ ] 单元测试覆盖率 > 70%
- [ ] 集成测试通过
- [ ] 代码符合 PEP 8 规范（flake8 检查通过）
- [ ] 代码格式统一（black 格式化）
- [ ] 无严重 bug（无 ERROR 日志）

### 文档验收

- [ ] README.md 完整
- [ ] 快速开始指南完整
- [ ] 命令参考文档完整
- [ ] 插件开发指南完整
- [ ] 插件 API 文档完整
- [ ] 至少 5 个使用示例

### 性能验收

- [ ] 处理 10 页 PDF 文档 < 5 秒
- [ ] 处理 100 页 PDF 文档 < 30 秒
- [ ] 内存使用 < 500MB（处理 100 页 PDF）
- [ ] 插件加载时间 < 1 秒

---

## 🔄 开发流程

### 日常开发流程

1. **拉取最新代码**
   ```bash
   git pull origin main
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/task-name
   ```

3. **编写测试用例**
   ```bash
   # 创建测试文件
   touch tests/test_feature.py
   ```

4. **运行测试（应该失败）**
   ```bash
   pytest tests/test_feature.py
   ```

5. **实现功能**
   ```bash
   # 编写功能代码
   ```

6. **运行测试（应该通过）**
   ```bash
   pytest tests/test_feature.py -v
   ```

7. **运行所有测试**
   ```bash
   pytest -v
   ```

8. **代码格式化和检查**
   ```bash
   black .
   flake8 .
   ```

9. **生成测试覆盖率报告**
   ```bash
   pytest --cov=. --cov-report=html
   ```

10. **提交代码**
    ```bash
    git add .
    git commit -m "feat: implement feature-name"
    git push origin feature/task-name
    ```

11. **创建 Pull Request**
    - 在 GitHub 上创建 PR
    - 等待代码审查
    - 根据反馈修改代码

12. **合并到主分支**
    - 审查通过后合并到 main
    - 删除功能分支

### 持续集成（CI）流程

1. **触发 CI**
   - 每次提交自动触发 CI

2. **运行测试**
   - 运行所有单元测试
   - 运行集成测试

3. **代码质量检查**
   - flake8 检查
   - black 检查

4. **生成覆盖率报告**
   - 生成 HTML 覆盖率报告
   - 检查覆盖率是否达标

5. **构建文档**
   - 生成 API 文档

6. **发布**
   - 测试通过后自动构建
   - 打包发布到 PyPI

---

## 📊 测试覆盖率目标

| 模块 | 覆盖率目标 | 说明当前状态 |
|------|----------|----------------|
| **插件系统** | 90% | BasePlugin、PluginManager |
| **PDF 引擎** | 85% | BasePDFEngine、PyMuPDFEngine |
| **阅读器插件** | 80% | 5 个阅读器插件 |
| **转换器插件** | 80% | 6 个转换器插件 |
| **CLI 框架** | 80% | CLI 主框架和所有命令 |
| **错误处理** | 90% | 错误类和装饰器 |
| **整体** | 75% | 所有模块平均 |

---

## 🎯 开发成功指标

### 技术指标

- ✅ 测试覆盖率 > 70%
- ✅ 所有测试通过
- ✅ 代码符合 PEP 8 规范
- ✅ 无严重 bug

### 产品指标

- ✅ 所有功能正常工作
- ✅ AI Agent 友好接口完整
- ✅ 性能达标

### 用户体验指标

- ✅ 安装简单
- ✅ 文档完整
- ✅ 错误提示清晰

---

*开发计划完成 - 第一阶段*
