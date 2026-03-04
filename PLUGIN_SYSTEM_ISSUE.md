# 插件系统问题调查

**发现时间：** 2026-03-04 17:43
**问题类型：** 插件系统未正确初始化

---

## 🔍 问题描述

### 测试步骤

**1. 安装方式：** 从源码安装（`pip install -e .`）
**2. 虚拟环境：** 创建新虚拟环境 `test_install`
**3. 安装结果：** ✅ 成功
**4. 版本检查：** ✅ `ai-pdf --version` 正常
**5. 帮助信息：** ✅ `ai-pdf --help` 正常

---

### ❌ 发现的问题

**插件列表为空：**
```bash
ai-pdf plugin list
# 输出：No plugins found.
```

**文本提取失败：**
```bash
ai-pdf text examples/sample_pdfs/sample_text.pdf -o /tmp/test_output.txt
# 错误：Plugin not found: text_reader
```

**错误信息：**
```
Missing dependencies: ['pymupdf>=1.23.0']
AI_PDF_Error: Plugin not found: text_reader
WARNING: Missing dependencies: ['pymupdf>=1.23.0']
ERROR: AI_PDF_Error: Plugin not found: text_reader
❌ Plugin not found: text_reader
```

---

## 🔧 问题分析

### 可能原因

#### 1. 插件路径配置错误

**检查项：**
- 插件目录是否正确
- 插件文件是否包含
- 插件 __init__.py 是否正确

**需要检查：**
```bash
ls -la /root/.openclaw/workspace/ai-pdf-agent/plugins/
ls -la /root/.openclaw/workspace/ai-pdf-agent/plugins/readers/
ls -la /root/.openclaw/workspace/ai-pdf-agent/plugins/converters/
```

---

#### 2. setup.py 配置问题

**检查项：**
- `packages=find_packages()` 是否正确
- `include_package_data=True` 是否设置
- 插件数据文件是否包含

**需要检查：**
```bash
cat /root/.openclaw/workspace/ai-pdf-agent/setup.py
```

---

#### 3. 插件发现机制问题

**检查项：**
- 插件管理器是否正确初始化
- 插件扫描路径是否正确
- 插件加载逻辑是否有错误

**需要检查：**
```bash
cat /root/.openclaw/workspace/ai-pdf-agent/cli/commands/plugin.py
cat /root/.openclaw/workspace/ai-pdf-agent/core/plugin_system/plugin_manager.py
```

---

#### 4. 依赖检查逻辑错误

**问题：** pymupdf 已安装（1.27.1），但插件检查失败

**可能原因：**
- 依赖检查逻辑有错误
- 版本检查过于严格
- 依赖名称不匹配

---

## 📊 测试结果

| 测试项 | 结果 | 说明 |
|--------|------|------|
| 虚拟环境创建 | ✅ 成功 | test_install 创建成功 |
| 安装到系统 | ✅ 成功 | pip install -e . 成功 |
| 版本检查 | ✅ 成功 | ai-pdf --version 正常 |
| 帮助信息 | ✅ 成功 | ai-pdf --help 正常 |
| 插件列表 | ❌ 失败 | No plugins found. |
| 文本提取 | ❌ 失败 | Plugin not found: text_reader |

**通过率：** 4/6 (67%)

---

## 🎯 下一步调查

### 1. 检查插件目录结构

```bash
cd /root/.openclaw/workspace/ai-pdf-agent
find plugins/ -name "*.py" -type f
```

### 2. 检查插件管理器

```bash
cat core/plugin_system/plugin_manager.py
```

### 3. 检查 CLI 插件命令

```bash
cat cli/commands/plugin.py
```

### 4. 运行插件发现调试

```bash
source test_install/bin/activate
python3 -c "
from core.plugin_system.plugin_manager import PluginManager
manager = PluginManager()
plugins = manager.discover_plugins()
print(f'发现插件数量: {len(plugins)}')
for plugin in plugins:
    print(f'  - {plugin.name}')
"
```

---

## 💡 初步判断

**问题可能在于：**
1. 插件系统未正确初始化
2. 插件路径配置错误
3. 依赖检查逻辑有误

**需要团队解决：**
- 检查插件系统代码
- 修复插件发现机制
- 更新依赖检查逻辑

---

**分配给：** AI PDF Agent 团队
**优先级：** 高
**状态：** 待调查
