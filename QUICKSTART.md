# AI PDF Agent - 5 分钟快速开始指南

> 在 5 分钟内快速上手 AI PDF Agent，开始处理 PDF 文档

---

## ⚡ 一键安装

### 方式 1：推荐（开发模式）

```bash
# 克隆项目
git clone https://github.com/ai-agent/ai-pdf-agent.git
cd ai-pdf-agent

# 安装依赖
pip install -r requirements.txt

# 验证安装
python -m ai.pdf --help
```

### 方式 2：全局安装

```bash
# 克隆项目
git clone https://github.com/ai-agent/ai-pdf-agent.git
cd ai-pdf-agent

# 安装到系统
pip install -e .

# 验证安装
ai-pdf --help
```

**预期输出：**
```
Usage: ai-pdf [OPTIONS] COMMAND [ARGS]...

  AI Agent 友好的 PDF 处理工具

Options:
  -v, --version  显示版本号
  --help         显示帮助信息

Commands:
  text          提取 PDF 文本
  tables        提取 PDF 表格
  images        提取 PDF 图片
  to-markdown   转换为 Markdown
  to-json       转换为 JSON
  ...
```

---

## 🚀 第一个示例：读取文本

**准备测试文件：**
```bash
# 下载测试 PDF（或使用你自己的文件）
wget https://example.com/sample.pdf -o test.pdf
```

**提取文本：**
```bash
# 基本用法
python -m ai.pdf text test.pdf -o output.txt

# 查看结果
cat output.txt
```

**AI Agent 友好方式（JSON 输出）：**
```bash
# 输出 JSON 格式
python -m ai.pdf text test.pdf --json -o output.json

# 查看结果
cat output.json
```

**预期输出：**
```json
{
  "success": true,
  "file": "test.pdf",
  "pages": 5,
  "text": "这是 PDF 文档的文本内容...",
  "metadata": {
    "title": "示例文档",
    "author": "AI PDF Agent",
    "created": "2026-03-03"
  }
}
```

---

## 💡 常见用例

### 1️⃣ 提取表格数据

```bash
# 提取所有表格
python -m ai.pdf tables report.pdf -o tables.json

# 提取并导出为 CSV
python -m ai.pdf tables report.pdf --csv -o tables.csv
```

**输出示例：**
```json
{
  "tables": [
    {
      "page": 1,
      "rows": [
        ["姓名", "年龄", "城市"],
        ["张三", "25", "北京"],
        ["李四", "30", "上海"]
      ]
    }
  ]
}
```

---

### 2️⃣ 提取图片

```bash
# 提取所有图片
python -m ai.pdf images document.pdf --extract-dir ./images

# 输出：
# images/page1_img1.png
# images/page1_img2.png
# images/page2_img1.png
```

---

### 3️⃣ 格式转换

**PDF → Markdown（适合博客/文档）：**
```bash
python -m ai.pdf to-markdown document.pdf -o document.md
```

**PDF → JSON（结构化数据）：**
```bash
python -m ai.pdf to-json document.pdf -o document.json
```

**PDF → HTML（网页预览）：**
```bash
python -m ai.pdf to-html document.pdf -o document.html
```

---

### 4️⃣ 批量处理

```bash
# 批量转换多个 PDF
for file in *.pdf; do
    python -m ai.pdf to-markdown "$file" -o "${file%.pdf}.md"
done
```

---

## 🔧 故障排除

### ❌ 问题 1：找不到命令 `ai-pdf`

**原因：** 未使用全局安装

**解决：** 使用 `python -m ai.pdf` 代替 `ai-pdf`

```bash
# 错误
ai-pdf text test.pdf

# 正确
python -m ai.pdf text test.pdf
```

---

### ❌ 问题 2：依赖安装失败

**原因：** 缺少系统依赖（如 poppler）

**解决：** 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# CentOS/RHEL
sudo yum install poppler-utils
```

---

### ❌ 问题 3：内存不足（大文件）

**原因：** 文件太大，超过可用内存

**解决：** 分批处理或增加系统内存

```bash
# 查看文件大小
ls -lh large-file.pdf

# 分批处理（按页）
python -m ai.pdf text large-file.pdf --pages 1-10 -o part1.txt
python -m ai.pdf text large-file.pdf --pages 11-20 -o part2.txt
```

---

### ❌ 问题 4：插件未找到

**原因：** 插件未正确安装或配置

**解决：** 检查插件状态

```bash
# 列出所有插件
python -m ai.pdf plugin list

# 检查特定插件
python -m ai.pdf plugin check text_reader

# 重新安装插件
python -m ai.pdf plugin install text_reader
```

---

### ❌ 问题 5：权限错误

**原因：** 输出目录无写入权限

**解决：** 使用有权限的目录或修改权限

```bash
# 使用当前目录
python -m ai.pdf text test.pdf -o ./output.txt

# 或修改目录权限
mkdir -p output
chmod 755 output
```

---

## 📚 下一步

### 📖 深入阅读

- **[README.md](README.md)** - 完整项目文档
- **[WORKFLOW.md](WORKFLOW.md)** - 工作流程指南
- **[DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)** - 开发计划
- **[TEST_PLAN.md](TEST_PLAN.md)** - 测试计划

### 🔌 插件开发

想要开发自己的插件？

```bash
# 查看插件开发文档
cat docs/PLUGIN_DEVELOPMENT.md

# 查看示例插件
ls plugins/readers/
ls plugins/converters/
```

### 🧪 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_text_reader.py

# 生成覆盖率报告
pytest --cov=ai --cov-report=html
```

### 💬 获取帮助

- **GitHub Issues**: https://github.com/ai-agent/ai-pdf-agent/issues
- **Discord**: https://discord.gg/ai-pdf-agent
- **Email**: support@ai-pdf-agent.com

---

## ⏱️ 5 分钟完成清单

- [x] 安装 AI PDF Agent（1 分钟）
- [x] 运行 `--help` 查看命令（30 秒）
- [x] 提取第一个 PDF 文本（1 分钟）
- [x] 尝试 JSON 输出（30 秒）
- [x] 转换为 Markdown（1 分钟）
- [x] 提取表格或图片（1 分钟）

**恭喜！你已经掌握了 AI PDF Agent 的基本用法！** 🎉

---

*最后更新：2026-03-03*
*版本：v1.0*
