# Simple PDF - 包结构修复计划

## 问题分析

### 当前问题
1. **ModuleNotFoundError**: `No module named 'ai_pdf_agent'`
2. **原因**: `simple-pdf` 命令无法找到 `ai_pdf_agent` 模块

### 原因分析
- `setup.py` 中的 `entry_points` 指向 `ai_pdf_agent.cli.main:cli`
- 但 `ai_pdf_agent/__init__.py` 初始化文件可能有问题
- 包导入路径不匹配

---

## 修复方案

### 方案 1：修复包结构（推荐）

#### 1.1 确保包初始化文件存在

```bash
ai_pdf_agent/
├── __init__.py          # ✅ 必需
├── cli/
│   ├── __init__.py      # ✅ 必需
│   └── main.py
├── core/
│   ├── __init__.py      # ✅ 必需
│   └── ...
└── ...
```

#### 1.2 检查并修复 `__init__.py` 文件

**ai_pdf_agent/__init__.py**:
```python
"""Simple PDF - 包初始化"""

__version__ = "1.0.0"
__author__ = "Simple PDF Team"
```

**ai_pdf_agent/cli/__init__.py**:
```python
"""Simple PDF - CLI 模块初始化"""

from .main import cli

__all__ = ['cli']
```

---

### 方案 2：使用 pyproject.toml（更现代）

#### 创建 pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "simple-pdf"
version = "1.0.0"
description = "Simple PDF - 简单易用的 PDF 处理工具"
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "click>=8.0.0",
    "pymupdf>=1.23.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]

[project.scripts]
simple-pdf = "ai_pdf_agent.cli.main:cli"

[project.entry-points."console_scripts"]
simple-pdf = "ai_pdf_agent.cli.main:cli"
```

---

## 修复步骤

### 步骤 1：创建所有必需的 `__init__.py` 文件

```bash
# 创建包根目录的 __init__.py
touch ai_pdf_agent/__init__.py

# 创建所有子模块的 __init__.py
find ai_pdf_agent -type d -exec touch {}/__init__.py \;
```

### 步骤 2：重新安装包

```bash
# 卸载旧版本
pip uninstall -y simple-pdf

# 重新安装
pip install -e .

# 验证
simple-pdf --version
```

### 步骤 3：测试

```bash
# 测试导入
python3 -c "from ai_pdf_agent.cli.main import cli; print('Import success')"

# 测试命令
simple-pdf --help
```

---

## 建议的文件结构

```
ai-pdf-agent/
├── ai_pdf_agent/              # 包根目录
│   ├── __init__.py            # ✅ 必需
│   ├── cli/                   # CLI 模块
│   │   ├── __init__.py        # ✅ 必需
│   │   └── main.py
│   ├── core/                  # 核心模块
│   │   ├── __init__.py        # ✅ 必需
│   │   ├── pdf_engine.py
│   │   └── ...
│   ├── plugins/               # 插件系统
│   │   ├── __init__.py        # ✅ 必需
│   │   ├── readers/
│   │   │   ├── __init__.py    # ✅ 必需
│   │   │   └── ...
│   │   └── converters/
│   │       ├── __init__.py    # ✅ 必需
│   │       └── ...
│   └── version.py             # 版本信息
├── tests/
│   ├── __init__.py            # ✅ 必需
│   └── ...
├── setup.py
├── pyproject.toml             # ✅ 推荐
├── requirements.txt
└── README.md
```

---

## 需要修复的文件

### 高优先级
1. ✅ `ai_pdf_agent/__init__.py` - 已创建
2. ✅ `ai_pdf_agent/cli/__init__.py` - 已创建
3. ⏳ `ai_pdf_agent/core/__init__.py` - 需要创建
4. ⏳ `ai_pdf_agent/plugins/__init__.py` - 需要创建

### 中优先级
5. ⏳ 所有插件子模块的 `__init__.py` - 需要创建
6. ⏳ `tests/__init__.py` - 需要创建

---

## 下一步

1. 创建所有缺失的 `__init__.py` 文件
2. 重新安装包并测试
3. 如果还有问题，使用 pyproject.toml 代替 setup.py
