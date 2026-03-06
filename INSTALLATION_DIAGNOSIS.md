# Simple PDF 安装诊断报告

## 问题现象

```
bash: simple-pdf: command not found
```

**环境信息：**
- Python: 3.12+
- 镜像源：清华大学 TUNA 镜像
- 安装方式：pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

---

## 问题诊断

### 可能原因

#### 1. **未使用可编辑模式安装**
```bash
# ❌ 错误方式
pip install -r requirements.txt

# ✅ 正确方式（开发模式）
pip install -e .
```

#### 2. **PATH 环境变量问题**
- `simple-pdf` 安装路径不在 `PATH` 中
- 需要检查 `~/.local/bin/` 或虚拟环境的 `bin/` 目录

#### 3. **Python 环境不一致**
- 系统安装了多个 Python 版本
- `pip` 和 `python` 指向不同的环境

#### 4. **包未正确安装**
- 安装时出错但未注意到
- 依赖冲突导致安装失败

---

## 解决方案

### 方案 A：使用可编辑模式安装（推荐）

```bash
# 1. 进入项目目录
cd ai-pdf-agent

# 2. 清理环境（可选）
pip uninstall -y simple-pdf

# 3. 使用可编辑模式安装
pip install -e .

# 4. 验证安装
which simple-pdf
simple-pdf --version
```

**为什么可编辑模式？**
- 直接链接到源代码，无需复制
- 修改代码后立即生效
- 方便开发和调试

---

### 方案 B：使用虚拟环境（推荐）

```bash
# 1. 创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安装包
pip install -e .

# 4. 验证安装
which simple-pdf
simple-pdf --version
```

**为什么使用虚拟环境？**
- 隔离项目依赖
- 避免版本冲突
- 确保干净的安装环境

---

### 方案 C：检查 PATH 环境变量

```bash
# 1. 查找 simple-pdf 安装在哪里
find ~ -name "simple-pdf" -type f 2>/dev/null

# 2. 查看 PATH
echo $PATH

# 3. 添加到 PATH（如果需要）
echo ~/.local/bin" >> ~/.bashrc
source ~/.bashrc
```

---

### 方案 D：手动安装脚本

```bash
#!/bin/bash
# install.sh

echo "开始安装 Simple PDF..."

# 检查 Python 版本
echo "Python 版本: $(python3 --version)"

# 进入项目目录
cd ai-pdf-agent

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 安装包（可编辑模式）
echo "安装 Simple PDF..."
pip install -e .

# 验证安装
echo "验证安装..."
which simple-pdf
simple-pdf --version
simple-pdf --help

echo "安装完成！"
echo "使用方法："
echo "  source venv/bin/activate"
echo "  simple-pdf read document.pdf -o output.txt"
```

**使用方法：**
```bash
chmod +x install.sh
./install.sh
```

---

## 验证步骤

### 步骤 1：检查包是否安装

```bash
# 检查是否在已安装列表中
pip list | grep simple-pdf

# 查看详细信息
pip show simple-pdf
```

### 步骤 2：检查命令位置

```bash
# 查找命令
which simple-pdf

# 如果找不到，搜索文件系统
find ~ -name "simple-pdf" -type f 2>/dev/null
```

### 步骤 3：手动测试导入

```bash
# 测试 Python 导入
python3 -c "from ai_pdf_agent.cli.main import cli; print('Import success')"

# 测试命令
python3 -m ai_pdf_agent.cli.main --version
```

---

## 常见问题

### Q1: 安装成功但找不到命令？

**A:** 可能是 PATH 问题
```bash
# 找到安装位置
find ~/.local -name "simple-pdf" 2>/dev/null

# 添加到 PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Q2: ModuleNotFoundError: No module named 'ai_pdf_agent'？

**A:** 包结构问题
```bash
# 检查包结构
ls -la ai_pdf_agent/

# 确保 __init__.py 存在
ls -la ai_pdf_agent/__init__.py
ls -la ai_pdf_agent/cli/__/__init__.py
```

### Q3: AttributeError: version？

**A:** CLI 语法错误
```bash
# 检查 main.py
cat ai_pdf_agent/cli/main.py | grep @click.version

# 应该是：
# @click.version_option(version="1.0.0", prog_name="simple-pdf")
```

---

## 调试命令

### 完整诊断脚本

```bash
#!/bin/bash
# diagnose.sh

echo "=== Simple PDF 诊断 ==="
echo ""

echo "1. Python 版本:"
python3 --version
echo ""

echo "2. Pip 版本:"
pip3 --version
echo ""

echo "3. 当前工作目录:"
pwd
echo ""

echo "4. PATH 环境变量:"
echo $PATH | tr ':' '\n'
echo ""

echo "5. 查找 simple-pdf 命令:"
which simple-pdf || echo "未找到 simple-pdf 命令"
echo ""

echo "6. 搜索文件系统中的 simple-pdf:"
find ~ -name "simple-pdf" -type f 2>/dev/null | head -5
echo ""

echo "7. 检查包是否安装:"
pip list | grep simple-pdf || echo "包未安装"
echo ""

echo "8. 测试 Python 导入:"
python3 -c "from ai_pdf_agent.cli.main import cli; print('Import success')" 2>&1
echo ""

echo "9. 测试模块执行:"
python3 -m ai_pdf_agent.cli.main --version 2>&1
echo ""

echo "10. 检查包结构:"
ls -la ai_pdf_agent/ 2>&1 | head -10
echo ""

echo "=== 诊断完成 ==="
```

---

## 推荐安装流程

### 完整安装步骤

```bash
# 1. Clone 仓库
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 升级 pip
pip install --upgrade pip

# 5. 安装依赖
pip install -r requirements.txt

# 6. 安装包（可编辑模式）
pip install -e .

# 7. 验证安装
echo "=== 验证安装 ==="
which simple-pdf
simple-pdf --version
simple-pdf --help

# 8. 测试命令（如果有测试 PDF）
# simple-pdf read test_sample.pdf -o output.txt
```

---

## 快速测试

### 最简单的测试方法

```bash
# 方法 1：直接运行模块
python3 -m ai_pdf_agent.cli.main --version

# 方法 2：在虚拟环境中
python3 -m venv test_env && source test_env/bin/activate && pip install -e . && simple-pdf --version

# 方法 3：检查安装位置
find ~/.local -name "simple-pdf" 2>/dev/null
```

---

## 下一步

1. **运行诊断脚本** - 查看完整环境信息
2. **检查 PATH** - 确保 simple-pdf 在 PATH 中
3. **重新安装** - 使用可编辑模式
4. **使用虚拟环境** - 推荐方案

---

**需要帮助？** 提供以上诊断脚本的输出结果。
