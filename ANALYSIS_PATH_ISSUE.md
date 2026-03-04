# 测试与安装差异分析

**分析时间：** 2026-03-04 19:25
**问题：** pytest 测试通过但从源码安装后 CLI 使用失败

---

## 问题概述

### 现象

**pytest 测试：** ✅ 所有 1101 个测试通过
**CLI 使用：** ❌ 从非项目目录运行时插件加载失败

### 错误类型

1. **模块导入错误**
   ```
   ModuleNotFoundError: No module named 'plugins.to_json'
   ```

2. **插件类未找到**
   ```
   Plugin class not found in plugins/converters/html_converter.py
   Plugin class not found in plugins/converters/csv_converter.py
   Plugin class not found in plugins/converters/image_converter.py
   Plugin class not found in plugins/converters/epub_converter.py
   ```

3. **依赖检查错误**
   ```
   Missing dependencies: ['pillow>=9.0.0']
   ```
   （但实际安装的是 PIL 12.1.1，包名是 pillow 而非 pillow）

---

## 根本原因分析

### 环境差异

#### pytest 环境

```bash
# 工作目录
/root/.openclaw/workspace/ai-pdf-agent

# pytest 从项目根目录启动
pytest tests/
```

**路径解析：**
- 项目根目录：`/root/.openclaw/workspace/ai-pdf-agent`
- 插件目录：`./plugins` 或 `plugins/`（绝对路径）
- Python 搜索路径：包含项目根目录

**插件导入：**
```python
from plugins.readers.text_reader import TextReaderPlugin
# 有效，因为项目根目录在 sys.path 中
```

---

#### CLI 环境（从非项目目录）

```bash
# 工作目录
/tmp 或 /home/user 等

# 运行 ai-pdf 命令
ai-pdf text document.pdf
```

**路径解析问题：**
- 工作目录：`/tmp`
- 插件目录：`./plugins` → `/tmp/plugins`（相对路径）
- 项目根目录：无法确定

**插件导入失败：**
```python
# CLIContext 计算
plugin_dir = Path(__file__).parent / 'plugins'
# 假设 __file__ 是 /path/to/cli/main.py
# plugin_dir = /path/to/plugins

# PluginManager 使用
self.plugin_dirs = ["./plugins"]
# 解析为 /tmp/plugins（不存在）
```

---

### 路径解析差异

#### pytest：✅ 正确

```python
# tests/conftest.py
import sys

# 添加项目路径到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 插件导入
from plugins.readers.text_reader import TextReaderPlugin  # ✅ 成功
```

#### CLI：❌ 错误

```python
# cli/main.py
from core.plugin_system.plugin_manager import PluginManager

# PluginManager 使用默认配置
plugin_manager = PluginManager()
# self.plugin_dirs = ["./plugins", "~/.ai-pdf/plugins", ...]

# 问题：
# 1. "~/.ai-pdf/plugins" 是用户主目录，不是项目目录
# 2. 项目安装路径无法确定
```

---

## 解决方案

### 方案 1：修复 PluginManager 默认路径（推荐）⭐

**修改 `core/plugin_system/plugin_manager.py`**

```python
def __init__(self, plugin_dirs: List[str] = None):
    """初始化插件管理器"""
    if self._initialized:
        return

    # 计算项目根目录
    if plugin_dirs is None:
        # 自动检测项目根目录
        # 方法 1：从 __file__ 反推
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 向上查找包含 'core' 和 'plugins' 的目录
        project_root = None
        for _ in range(5):
            if os.path.exists(os.path.join(current_dir, 'core')):
                project_root = current_dir
                break
            parent = os.path.dirname(current_dir)
            if parent == current_dir:
                break
            current_dir = parent
        
        # 如果找到项目根，使用其插件目录
        if project_root:
            self.plugin_dirs = [
                os.path.join(project_root, 'plugins'),
                os.path.join(project_root, 'builtin_plugins')
            ]
            logger.info(f"Auto-detected project root: {project_root}")
            logger.info(f"Plugin directories: {self.plugin_dirs}")
        else:
            # 回退到默认配置
            self.plugin_dirs = [
                "./plugins",
                "~/.ai-pdf/plugins",
                "/usr/local/lib/ai-pdf-agent/plugins",
                os.path.join(sys.prefix, "lib/pythonX.Y/site-packages/ai_pdf_agent/plugins"),
            ]
            logger.warning("Could not auto-detect project root, using default paths")
    else:
        self.plugin_dirs = plugin_dirs
```

**优点：**
- ✅ 自动检测项目根目录
- ✅ 从任何目录运行都能找到插件
- ✅ 不依赖当前工作目录
- ✅ 向后兼容

---

### 方案 2：CLIContext 强制传递插件路径

**修改 `cli/commands/cli.py`**

```python
class CLIContext:
    def __init__(self):
        # 计算项目根目录
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 向上查找项目根
        project_root = None
        for _ in range(5):
            if os.path.exists(os.path.join(current_dir, 'core')):
                project_root = current_dir
                break
            parent = os.path.dirname(current_dir)
            if parent == current_dir:
                break
            current_dir = parent
        
        # 设置插件目录
        self.plugin_dir = os.path.join(project_root, 'plugins') if project_root else None
```

**传递给 PluginManager：**

```python
# 在 CLI 命令中
plugin_manager = PluginManager(plugin_dirs=[ctx.plugin_dir])
```

**优点：**
- ✅ 明确传递插件路径
- ✅ 不依赖 PluginManager 自动检测

**缺点：**
- 需要修改所有 CLI 命令

---

### 方案 3：使用配置文件

**创建 `ai_pdf_config.json`**

```json
{
  "plugin_dirs": [
    "/root/.openclaw/workspace/ai-pdf-agent/plugins",
    "~/.ai-pdf/plugins"
  ]
}
```

**加载配置：**

```python
import json
import os

config_path = os.path.expanduser("~/.ai-pdf/config.json")
if os.path.exists(config_path):
    with open(config_path) as f:
        config = json.load(f)
        plugin_dirs = config.get('plugin_dirs', [])
```

---

## 推荐实施

### 阶段 1：实施方案 1（自动检测）

**修改文件：** `core/plugin_system/plugin_manager.py`

**关键修改：**
1. 添加 `auto_detect_project_root()` 方法
2. 修改 `__init__` 默认行为
3. 添加调试日志

**测试验证：**
```bash
cd /tmp
ai-pdf text /path/to/document.pdf
# 应该能自动找到插件

cd /root/.openclaw/workspace/ai-pdf-agent
ai-pdf text document.pdf
# 应该继续正常工作
```

---

### 阶段 2：增强测试覆盖

**新增测试：** `tests/test_plugin_auto_detection.py`

```python
def test_auto_detect_from_different_directories():
    """测试从不同目录自动检测项目根"""
    # 测试从项目根目录
    # 测试从上级目录
    # 测试从完全不同目录
```

---

## 总结

**问题根源：** 相对路径依赖当前工作目录

**推荐方案：** 方案 1（自动检测项目根目录）

**理由：**
1. 从任何目录运行都能找到插件
2. 不依赖工作目录
3. 向后兼容
4. 用户配置可覆盖

**风险等级：** 低（只修改路径计算逻辑）

---

**生成时间：** 2026-03-04 19:25
**分析者：** AI PDF Agent 团队
