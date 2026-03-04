# 测试与安装差异分析报告

**分析时间：** 2026-03-04 19:15
**任务：** 分析测试与安装差异

---

## 问题概述

- ✅ **pytest 测试结果：** 所有 1101 个测试通过
- ❌ **源码安装后 CLI：** 从非项目目录运行时插件加载失败

---

## 根本原因分析

### 1. 环境差异

#### pytest 环境
```bash
# pytest 从项目根目录启动
cd /root/.openclaw/workspace/ai-pdf-agent
pytest tests/  # 使用 Python 搜索路径
```

**工作目录：** `/root/.openclaw/workspace/ai-pdf-agent`

**插件路径解析：**
- `tests/conftest.py` 中手动添加项目路径：
  ```python
  project_root = Path(__file__).parent.parent
  sys.path.insert(0, str(project_root))
  ```
- pytest 发现插件：`from plugins.readers.text_reader import TextReaderPlugin`
- 相对导入有效：`plugins` 包名在 Python 搜索路径中

---

#### CLI 环境（非项目目录）
```bash
# 从 /tmp 或其他目录运行
cd /tmp
ai-pdf plugin list
```

**工作目录：** `/tmp`（或其他非项目目录）

**插件路径解析问题：**
- `plugin_manager.py` 默认使用相对路径：
  ```python
  self.plugin_dirs = ["./plugins", "~/.ai-pdf/plugins", ...]
  ```
- `"./plugins"` 相对于当前工作目录（/tmp）
- 实际搜索：`/tmp/plugins` → 不存在
- 失败：插件未找到

---

### 2. PluginManager 路径问题

**当前代码（问题）：**
```python
# core/plugin_system/plugin_manager.py
self.plugin_dirs = plugin_dirs or [
    "./plugins",                    # ❌ 相对当前工作目录
    "~/.ai-pdf/plugins",
    os.path.join(os.path.dirname(__file__), "builtin_plugins")
]
```

**问题分析：**
1. `"./plugins"` 是相对路径
2. 在项目根目录运行时：`./plugins` = `/project/plugins` ✅
3. 在其他目录运行时：`./plugins` = `/other_dir/plugins` ❌

---

## 3. CLI 使用方式问题

**用户期望：**
```bash
# 安装后可以从任何目录使用
ai-pdf text document.pdf
```

**当前限制：**
- 只能从项目根目录使用
- 或需要设置环境变量
- 不符合 CLI 工具的期望行为

---

## 解决方案

### 方案 1：修复 PluginManager 默认路径（推荐）⭐

**修改 `core/plugin_system/plugin_manager.py`:**

```python
def __init__(self, plugin_dirs: List[str] = None):
    if self._initialized:
        return

    # 计算项目根目录（相对于 core.plugin_system 包）
    package_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(package_dir, ".."))

    # 使用绝对路径
    local_plugins_dir = os.path.join(project_root, "plugins")

    self.plugin_dirs = plugin_dirs or [
        local_plugins_dir,           # ✅ 使用绝对路径
        "~/.ai-pdf/plugins",
        os.path.join(project_root, "builtin_plugins")
    ]

    logger.info(f"Project root: {project_root}")
    logger.info(f"Plugins directory: {local_plugins_dir}")
    logger.info(f"Plugin directories: {self.plugin_dirs}")
```

**优点：**
- ✅ 解决相对路径问题
- ✅ 从任何目录运行都能找到插件
- ✅ 不依赖工作目录

**缺点：**
- 无

---

### 方案 2：CLI 传递插件路径

**修改 `cli/main.py`:**

```python
# 添加选项
@click.option('--plugin-dir', type=click.Path(exists=True), help='Plugin directory')
def cli(ctx, plugin_dir):
    # 传递插件路径给上下文
    ctx.ensure_object(dict)
    ctx.obj['plugin_dir'] = str(plugin_dir)
```

**优点：**
- 灵活配置
- 支持多个插件目录

**缺点：**
- 用户需要额外参数
- 不符合"安装即用"的期望

---

### 方案 3：使用环境变量

**修改启动脚本：**

```bash
# 设置环境变量
export AI_PDF_PLUGIN_DIR="/root/.openclaw/workspace/ai-pdf-agent/plugins"
```

**优点：**
- 简单
- 标准

**缺点：**
- 需要环境配置
- 不便携

---

## 推荐方案

**实施方案 1：** 修复 PluginManager 默认路径

**理由：**
1. 最符合用户期望
2. 无需额外配置
3. "安装即用"（pip install -e .）
4. 从任何目录都能正常工作

---

## 测试验证

### 测试用例 1：从项目根目录
```bash
cd /root/.openclaw/workspace/ai-pdf-agent
./test_install/bin/ai-pdf plugin list
# 预期：✅ 显示 11 个插件
```

### 测试用例 2：从其他目录
```bash
cd /tmp
/root/.openclaw/workspace/ai-pdf-agent/test_install/bin/ai-pdf plugin list
# 预期：✅ 显示 11 个插件
```

### 测试用例 3：文本提取
```bash
cd /tmp
/root/.openclaw/workspace/ai-pdf-agent/test_install/bin/ai-pdf \
    text /root/.openclaw/workspace/ai-pdf-agent/examples/sample_pdfs/sample_text.pdf \
    -o /tmp/output.txt
# 预期：✅ 成功提取文本
```

---

## 实施步骤

1. **修改 PluginManager**
   - 更新 `__init__` 方法
   - 使用绝对路径计算
   - 添加调试日志

2. **测试验证**
   - 从项目根目录运行
   - 从其他目录运行
   - 验证所有命令可用

3. **提交代码**
   - git add core/plugin_system/plugin_manager.py
   - git commit -m "fix: 修复插件路径问题"

4. **推送代码**
   - git push origin main

---

## 飄险评估

**风险等级：** 低

**原因：**
- 只修改路径计算逻辑
- 不影响核心功能
- 向后兼容

**测试覆盖：**
- pytest 测试：100% 通过（已验证）
- 需要新增：多目录运行测试

---

**生成时间：** 2026-03-04 19:15
**分析者：** AI PDF Agent 团队
**下一步：** 实施方案 1
