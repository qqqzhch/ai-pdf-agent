# 测试与安装差异分析报告

## 问题概述

- **pytest 测试结果：** ✅ 所有 1101 个测试通过
- **源码安装后 CLI：** ❌ 从非项目目录运行时插件加载失败

## 根本原因分析

### 1. 环境差异

#### pytest 环境
```python
# pytest 运行时的工作目录
# 总是在项目根目录: /root/.openclaw/workspace/ai-pdf-agent
```

**原因：**
- pytest 从 `pytest.ini` 所在目录启动
- 测试文件使用 `sys.path.insert(0, project_root)` 确保导入正确
- 工作目录天然就是项目根目录

#### 安装生产环境
```python
# CLI 命令运行时的工作目录
# 可能是任意目录，如: /tmp, /home/user 等
```

**原因：**
- 用户可以从任何目录调用 `ai-pdf` 命令
- 编辑模式安装（editable install）通过 `.pth` 文件指向源码
- 但当前工作目录（CWD）不受控制

### 2. 插件路径解析差异

#### PluginManager 的默认配置
```python
# core/plugin_system/plugin_manager.py
self.plugin_dirs = plugin_dirs or [
    "./plugins",                    # ❌ 相对 CWD！
    "~/.ai-pdf/plugins",           # 用户插件目录
    os.path.join(os.path.dirname(__file__), "..", "builtin_plugins")  # 内置插件
]
```

**问题：**
- `"./plugins"` 是**相对路径**，相对于**当前工作目录**
- 在项目根目录运行时：`./plugins` = `/project/plugins` ✅
- 在其他目录运行时：`./plugins` = `/current/dir/plugins` ❌

#### CLIContext 的路径计算
```python
# cli/main.py: _init_plugin_system()
plugin_dir = Path(__file__).parent.parent / 'plugins'
# 正确计算为: /absolute/path/to/project/plugins ✅
```

**问题：**
- CLIContext 计算了正确的插件目录
- **但是没有传递给 PluginManager**
- PluginManager 使用默认的相对路径配置

### 3. 实验验证

#### 实验 1: 从项目根目录运行
```bash
cd /root/.openclaw/workspace/ai-pdf-agent
./test_install/bin/ai-pdf plugin list
# 结果: ✅ 加载了 11 个插件
```

#### 实验 2: 从其他目录运行
```bash
cd /tmp
/root/.openclaw/workspace/ai-pdf-agent/test_install/bin/ai-pdf plugin list
# 结果: ❌ No plugins found.
```

#### 实验 3: 检查路径解析
```python
# 从 /tmp 运行时
plugin_dir = Path(__file__).parent.parent / 'plugins'
# plugin_dir = /root/.openclaw/workspace/ai-pdf-agent/plugins  ✅

# 但 PluginManager 使用
os.path.exists("./plugins")  # False，因为 CWD 是 /tmp
```

### 4. pytest 测试通过的原因

1. **pytest 总是从项目根目录运行**
   - `pytest.ini` 位于项目根目录
   - 测试发现自动从该目录开始

2. **测试文件手动添加项目路径**
   ```python
   # tests/conftest.py 和测试文件中
   project_root = Path(__file__).parent.parent
   sys.path.insert(0, str(project_root))
   ```

3. **Click CliRunner 使用隔离环境**
   - `CliRunner()` 默认在测试目录内运行
   - 测试可能通过其他方式模拟环境

## 解决方案

### 方案 1: 修复 PluginManager 的默认路径（推荐）⭐

**修改 `core/plugin_system/plugin_manager.py`:**

```python
def __init__(self, plugin_dirs: List[str] = None):
    if self._initialized:
        return

    # 计算项目根目录（相对于 core.plugin_system 包）
    package_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(package_dir, "..", ".."))
    local_plugins_dir = os.path.join(project_root, "plugins")

    self.plugin_dirs = plugin_dirs or [
        local_plugins_dir,           # ✅ 使用绝对路径
        "~/.ai-pdf/plugins",
        os.path.join(project_root, "builtin_plugins")
    ]
    # ... 其余代码不变
```

**优点：**
- 彻底解决路径问题
- 不依赖当前工作目录
- 适用于所有使用场景

**缺点：**
- 编辑模式安装的特殊处理
- 需要验证打包安装后的行为

### 方案 2: 让 CLIContext 传递插件路径

**修改 `cli/main.py`:**

```python
def _init_plugin_system(self):
    """初始化插件系统"""
    try:
        # 计算正确的插件目录
        plugin_dir = str(Path(__file__).parent.parent / 'plugins')

        # 传递给 PluginManager
        self.plugin_manager = PluginManager(plugin_dirs=[plugin_dir])

        # 加载插件
        if os.path.exists(plugin_dir):
            loaded_count = self.plugin_manager.load_all_plugins()
            logger.info(f"Loaded {loaded_count} plugins")
```

**优点：**
- 修改范围小
- 不影响其他 PluginManager 使用者

**缺点：**
- 只解决 CLI 问题，不影响其他场景
- 其他代码直接使用 PluginManager 仍会有问题

### 方案 3: 统一使用配置文件

**创建配置文件 `ai_pdf_config.json`:**

```json
{
  "plugin_dirs": [
    "auto",  // 自动检测
    "~/.ai-pdf/plugins"
  ]
}
```

**实现：**
```python
def _resolve_plugin_dirs(plugin_dirs):
    """解析插件目录配置"""
    if not plugin_dirs:
        plugin_dirs = ["auto", "~/.ai-pdf/plugins"]

    resolved = []
    for d in plugin_dirs:
        if d == "auto":
            # 自动检测：从包位置计算
            package_dir = os.path.dirname(__file__)
            project_root = os.path.abspath(os.path.join(package_dir, "..", ".."))
            resolved.append(os.path.join(project_root, "plugins"))
        else:
            resolved.append(os.path.expanduser(d))

    return resolved
```

**优点：**
- 灵活配置
- 支持用户自定义插件目录

**缺点：**
- 增加配置复杂度
- 需要文档说明

### 方案 4: 添加调试信息（辅助）

**在 PluginManager 中添加日志：**

```python
def discover_plugins(self, force_refresh: bool = False) -> List[str]:
    """发现所有可用插件"""
    if hasattr(self, '_plugin_cache') and not force_refresh:
        return self._plugin_cache

    discovered = []
    for plugin_dir in self.plugin_dirs:
        plugin_dir = os.path.expanduser(plugin_dir)
        logger.debug(f"Searching for plugins in: {plugin_dir}")

        if not os.path.exists(plugin_dir):
            logger.debug(f"Plugin directory does not exist: {plugin_dir}")
            continue

        # ... 其余代码
```

## 推荐实施步骤

### 立即修复（P0）
1. **实施方案 1** - 修复 PluginManager 路径解析
2. **添加方案 4** - 增强调试日志
3. **更新测试** - 验证从不同目录运行

### 后续优化（P1）
1. 考虑实施方案 2 作为 CLI 的额外保护
2. 添加集成测试验证多目录运行
3. 更新文档说明插件目录查找机制

## 测试验证清单

- [ ] 从项目根目录运行 CLI
- [ ] 从 /tmp 目录运行 CLI
- [ ] 从用户 home 目录运行 CLI
- [ ] 打包安装后运行（非编辑模式）
- [ ] pytest 所有测试仍通过
- [ ] 调试日志正确显示路径解析过程

## 总结

**核心问题：** PluginManager 使用相对路径 `"./plugins"` 依赖于当前工作目录

**根本原因：** pytest 总是从项目根目录运行，而 CLI 可能从任意目录运行

**解决思路：** 使用绝对路径（相对于包位置）替代相对路径

**风险等级：** 低（路径问题，不影响核心逻辑）
