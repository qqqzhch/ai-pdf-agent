# Simple PDF 安装方案重新设计

## 问题重新定义

**用户需求：**
- ✅ 源码安装后，直接使用 `simple-pdf` 命令
- ❌ 不是 `python3 -m ai_pdf_agent.cli.main`
- ❌ 不是需要复杂脚本或虚拟环境

**当前问题：**
- ❌ `simple-pdf` 命令不在 PATH 中
- ❌ `which simple-pdf` 找不到命令

---

## 根本原因分析

### 问题 1：安装方式错误

```bash
# ❌ 错误方式 1：只用 requirements.txt
pip install -r requirements.txt
# 结果：安装依赖，不安装包本身

# ❌ 错误方式 2：普通安装模式
pip install .
# 结果：复制文件到 site-packages，但不创建 console_scripts

# ✅ 正确方式：可编辑模式
pip install -e .
# 结果：创建 console_scripts 并链接到当前目录
```

### 问题 2：PATH 环境变量

```bash
# pip install -e . 默认安装位置
~/.local/bin/simple-pdf  # Linux/Mac
%USERPROFILE%\AppData\Local\Programs\Python\Python3x\Scripts\simple-pdf.exe  # Windows

# 但这个路径可能不在 PATH 中
echo $PATH
# 可能不包含 ~/.local/bin
```

### 问题 3：setup.py 配置问题

**当前配置可能的问题：**
1. `entry_points` 格式错误
2. `console_scripts` 键误
3. 包名与命令名不匹配

---

## 正确的解决方案

### 方案 1：修复 setup.py（推荐）✅

#### 1.1 确保 entry_points 正确

```python
# setup.py
entry_points={
    "console_scripts": [
        "simple-pdf=ai_pdf_agent.cli.cli:main",  # 注意：cli.cli，不是 cli.main
    ],
},
```

**关键点：**
- ✅ `ai_pdf_agent.cli.cli:main` - 导入路径
- ✅ 不是 `ai_pdf_agent.cli.main:cli`

#### 1.2 确保包结构正确

```
ai_pdf_agent/
├── __init__.py
└── cli/
    ├── __init__.py
    └── cli.py       # 注意：是 cli.py，不是 main.py
```

#### 1.3 使用可编辑模式安装

```bash
pip uninstall -y simple-pdf
pip install -e .
```

---

### 方案 2：修改包结构（如果方案 1 失败）

#### 2.1 重命名 main.py 为 cli

```bash
# 重命名
mv ai_pdf_agent/cli/main.py ai_pdf_agent/cli/cli.py

# 更新 setup.py
# entry_points={
#     "console_scripts": [
#         "simple-pdf=ai_pdf_agent.cli.cli:main",
#     ],
# },
```

#### 2.2 更新 CLI 入口点

```python
# ai_pdf_agent/cli/cli.py
import click

@click.group()
@click.version_option(version="1.0.0", prog_name="simple-pdf")
def main():  # 函数名改为 main
    """Simple PDF - 简单易用的 PDF 处理工具"""
    pass

if __name__ == '__main__':
    main()  # 调用 main()
```

---

### 方案 3：使用 pyproject.toml（最现代）✅

#### 3.1 创建 pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "simple-pdf"
version = "1.0.0"
description = "Simple PDF - 简单易用的 PDF 处理工具"
requires-python = ">=3.8"
dependencies = [
    "click>=8.0.0",
    "pymupdf>=1.23.0",
    "pydantic>=2.0.0",
]

[project.scripts]
simple-pdf = "ai_pdf_agent.cli.cli:main"

[project.entry-points."console_scripts"]
simple-pdf = "ai_project.cli.cli:main"
```

#### 3.2 删除或简化 setup.py

```python
# setup.py 可以简化为空或删除
from setuptools import setup

setup()  # 从 pyproject.toml 读取配置
```

---

### 方案 4：手动添加到 PATH（临时方案）

```bash
# 1. 找到安装位置
which simple-pdf 2>/dev/null || find ~/.local -name "simple-pdf" 2>/dev/null

# 2. 添加到 PATH（临时）
export PATH="$HOME/.local/bin:$PATH"

# 3. 永久添加（bash）
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrcarez

# 4. 永久添加（zsh）
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

# 5. 重新加载
source ~/.bashrc
```

---

## V2 团队修复计划

### 步骤 1：修复 setup.py

```python
# 修改 setup.py
entry_points={
    "console_scripts": [
        "simple-pdf=ai_pdf_agent.cli.cli:main",
    ],
},
```

### 步骤 2：重命名 main.py 为 cli.py

```bash
mv ai_pdf_agent/cli/main.py ai_pdf_agent/cli/cli.py

# 更新 cli.py 中的函数名
# def cli() -> def main()
```

### 步骤 3：更新 cli/__init__.py

```python
from .cli import main  # 导入 main 函数

__all__ = ['main']
```

### 步骤 4：重新安装并测试

```bash
pip uninstall -y simple-pdf
pip install -e .

# 测试
which simple-pdf
simple-pdf --version
simple-pdf --help
```

---

## 验证步骤

### 1. 检查安装位置

```bash
# 找到命令
find ~/.local -name "simple-pdf" 2>/dev/null

# 或使用 which
which simple-pdf
```

### 2. 检查 PATH

```bash
echo $PATH | tr ':' '\n' | grep -i local
```

### 3. 手动测试命令

```bash
# 如果找到位置
~/.local/bin/simple-pdf --version

# 或直接运行
python3 -m ai_pdf_agent.cli.cli --version
```

---

## 推荐方案排序

1. **方案 3（pyproject.toml）** - 最现代，最可靠 ⭐⭐⭐
2. **方案 1（修复 setup.py）** - 快速修复 ⭐⭐
3. **方案 2（重命名文件）** - 深度修复 ⭐⭐
4. **方案 4（添加 PATH）** - 临时方案 ⭐

---

## 下一步

### V2 团队需要做：

1. ✅ 检查当前 setup.py 配置
2. ✅ 重命名 main.py 为 cli.py
3. ✅ 更新 cli/__init__.py
4. ✅ 重新安装并测试
5. ✅ 验证 `simple-pdf` 命令可用
6. ✅ 创建安装指南文档
7. ✅ 提交修复到 GitHub

### 用户需要做：

1. ✅ 卸载旧版本
2. ✅ 使用 `pip install -e .` 安装
3. ✅ 检查 `which simple-pdf`
4. ✅ 如果找不到，添加 `~/.local/bin` 到 PATH

---

## 总结

**问题本质：**
- setup.py 中的 entry_points 配置不正确
- `ai_pdf_agent.cli.main:cli` 应改为 `ai_pdf_agent.cli.cli:main`

**解决方案：**
- 方案 1：修复 entry_points（快速）
- 方案 2：重命名文件并修复结构
- 方案 3：使用 pyproject.toml（最现代）

**验证方法：**
- `which simple-pdf` 找到命令
- `simple-pdf --version` 正常工作
