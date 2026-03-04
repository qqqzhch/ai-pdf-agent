# 测试与安装差异分析 - 最终报告

**分析时间：** 2026-03-04 19:25
**任务：** 问题定位与根因分析

---

## 问题总结

### 现象描述

**测试通过：** ✅ pytest tests/ - 1101 个测试全部通过
**CLI 错误：** ❌ 从非项目目录运行 `ai-pdf` 时插件加载失败

**具体错误：**
```
Plugin class not found in plugins/converters/html_converter.py
Plugin class not found in plugins/converters/csv_converter.py
Plugin class not found in plugins/converters/image_converter.py
Plugin class not found in plugins/converters/epub_converter.py
Missing dependencies: ['pillow>=9.0.0']
```

---

## 根本原因分析

### 1. 工作目录差异（主要问题）

#### pytest 环境
```bash
# pytest 从项目根目录运行
cd /root/.openclaw/workspace/ai-pdf-agent
pytest tests/
# 工作目录：/root/.openclaw/workspace/ai-pdf-agent
```

#### CLI 环境（错误环境）
```bash
# 从其他目录运行 CLI
cd /tmp  # 或 /home/user 等
ai-pdf text document.pdf
# 工作目录：/tmp 或其他非项目目录
```

---

### 2. 路径解析机制

**pytest 成功原因：**
1. 测试文件手动添加项目路径到 sys.path：
   ```python
   project_root = Path(__file__).parent.parent
   sys.path.insert(0, str(project_root))
   ```

2. 直接导入插件模块：
   ```python
   from plugins.readers.text_reader import TextReaderPlugin
   # 有效，因为项目根目录在 sys.path 中
   ```

**CLI 失败原因：**
1. CLI 使用相对路径查找插件：
   ```python
   # cli/commands/plugin.py
   plugin_dir = Path(__file__).parent / 'plugins'
   # 解析为：/current_dir/plugins（相对路径）
   ```

2. PluginManager 使用相对路径验证：
   ```python
   # core/plugin_system/plugin_manager.py
   self.plugin_dirs = ["./plugins", ...]
   # 检查 os.path.exists("./plugins")
   # 在 /tmp 目录下：失败（/tmp/plugins 不存在）
   ```

---

### 3. 模块导入机制

**pytest 直接导入：**
```python
# 测试通过
sys.path = [
    "/root/.openclaw/workspace/ai-pdf-agent",  # 项目根目录
    ...系统路径
]
from plugins.readers.text_reader import TextReaderPlugin  # ✅ 成功
```

**CLI 通过插件管理器导入：**
```python
# CLI 失败
# 1. 使用相对路径加载
spec = importlib.util.spec_from_file_location(
    f"plugins.text_reader",
    plugin_path  # 项目绝对路径
)
# 2. exec_module 时，搜索路径不同
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
# 3. 模块内相对导入失败
from .to_json import ToJsonPlugin  # ❌ 失败
```

---

## 解决方案

### 方案 1：使用绝对路径（推荐）⭐

**修改 `core/plugin_system/plugin_manager.py`**

```python
class PluginManager:
    def load_plugin(self, plugin_path: str) -> Optional[BasePlugin]:
        import sys
        
        # 保存原始 sys.path
        original_path = sys.path.copy()
        
        try:
            # 获取插件文件的绝对路径
            abs_plugin_path = os.path.abspath(plugin_path)
            
            # 确定项目根目录（查找包含 core/plugins 的目录）
            plugin_dir = os.path.dirname(abs_plugin_path)
            current_dir = plugin_dir
            
            # 向上查找项目根目录
            project_root = None
            for _ in range(5):  # 最多向上查找 5 层
                if os.path.exists(os.path.join(current_dir, 'core')):
                    project_root = current_dir
                    break
                parent = os.path.dirname(current_dir)
                if parent == current_dir:
                    break
                current_dir = parent
            
            # 添加项目根目录到 sys.path
            if project_root and project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            # 动态导入插件模块
            module_name = os.path.splitext(os.path.basename(plugin_path))[0]
            spec = importlib.util.spec_from_file_location(
                f"plugins.{module_name.}",
                abs_plugin_path
            )
            module = importlib.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找插件类
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type) and
                    hasattr(attr, 'name') and
                    hasattr(attr, 'version') and
                    hasattr(attr, 'plugin_type') and
                    hasattr(attr, 'is_available') and
                    hasattr(attr, 'execute')
                ):
                    plugin_class = attr
                    break
            
            return plugin_class
        finally:
            # 恢复原始 sys.path
            sys.path = original_path
```

---

### 方案 2：自动检测项目根目录（增强）⭐

**添加自动检测功能：**

```python
class PluginManager:
    @staticmethod
    def auto_detect_project_root() -> Optional[str]:
        """自动检测项目根目录"""
        import os
        from pathlib import Path
        
        # 从当前文件向上查找
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        for _ in range(5):
            if os.path.exists(os.path.join(current_dir, 'core')):
                return current_dir
            parent = os.path.dirname(current_dir)
            if parent == current_dir:
                break
            current_dir = parent
        
        return None
    
    def __init__(self, plugin_dirs: List[str] = None):
        if self._initialized:
            return

        # 自动检测项目根目录
        if plugin_dirs is None:
            project_root = self.auto_detect_project_root()
            if project_root:
                local_plugins_dir = os.path.join(project_root, "plugins")
                self.plugin_dirs = [
                    local_plugins_dir,
                    os.path.join(project_root, "builtin_plugins")
                ]
                logger.info(f"Auto-detected project root: {project_root}")
            else:
                # 回退到默认配置
                self.plugin_dirs = [
                    "./plugins",
                    "~/.ai-pdf/plugins",
                    "/usr/local/lib/ai-pdf-agent/plugins",
                ]
                logger.warning("Could not auto-detect project root, using default paths")
        else:
            self.plugin_dirs = plugin_dirs
```

---

### 方案 3：修复相对导入问题

**修改插件文件，避免相对导入：**

```python
# ❌ 错误做法（当前）
from .to_json import ToJsonPlugin  # ❌ 依赖工作目录

# ✅ 正确做法
from core.plugin_system.base_converter_plugin import ToJsonPlugin  # ✅ 绝对导入
```

**修复 `plugins/converters/__init__.py`：**

```python
"""转换器插件模块"""

# 使用相对导入（因为同一包内）
from ..base_converter_plugin import ToJsonPlugin
from ..base_converter_plugin import ToHtmlConverter
from ..base_converter_plugin import ToMarkdownPlugin
from ..base_converter_plugin import ToImageConverter
from ..base_converter_plugin import ToEpubConverter

__all__ = [
    'ToJsonPlugin',
    'ToHtmlConverter',
    'ToMarkdownPlugin',
    'ToImageConverter',
    'ToEpubPlugin',
]
```

---

## 验证步骤

### 1. 从项目根目录测试
```bash
cd /root/.openclaw/workspace/ai-pdf-agent
ai-pdf plugin list
# 预期：11 个插件
```

### 2. 从其他目录测试
```bash
cd /tmp
/root/.openclaw/workspace/ai-pdf-agent/test_install/bin/ai-pdf plugin list
# 预期：11 个插件（自动检测）
```

### 3. 文本提取测试
```bash
cd /tmp
/root/.openclaw/workspace/ai-pdf-agent/test_install/bin/ai-pdf \
    text /root/.openclaw/workspace/ai-pdf-agent/examples/sample_pdfs/sample_text.pdf \
    -o /tmp/output.txt
# 预期：成功
```

---

## 预期结果

| 测试场景 | 当前状态 | 预期结果 |
|---------|---------|---------|
| pytest 测试 | ✅ 通过 | ✅ 通过 |
| 项目根目录 CLI | ❌ 失败 | ✅ 通过 |
| 非项目根目录 CLI | ❌ 失败 | ✅ 通过 |
| 文本提取 | ❌ 失败 | ✅ 通过 |
| 插件列表 | ❌ 失败 | ✅ 通过 |

---

## 总结

### 根本问题
1. **相对路径依赖工作目录：** CLI 使用相对导入，只在工作目录为项目根时有效
2. **插件查找机制：** 使用相对路径验证，在非项目根目录失败

### 解决方案
1. **使用绝对路径加载插件** - 修改 plugin_manager.py 的 load_plugin 方法
2. **自动检测项目根目录** - 添加 auto_detect_project_root 静态方法
3. **修复相对导入** - 改用绝对导入替代相对导入
4. **添加项目根到 sys.path** - 确保模块能找到

### 优势
- ✅ 从任何目录都能正常工作
- ✅ "安装即用"体验
- ✅ 不依赖工作目录
- ✅ 向后兼容

---

**生成时间：** 2026-03-04 19:30
**分析者：** AI PDF Agent 团队
**状态：** 问题已定位，解决方案已准备
