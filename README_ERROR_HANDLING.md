# 错误处理和配置

## 错误处理

AI PDF Agent 提供了完善的错误处理机制，包括统一的错误代码、友好的错误提示和解决方案建议。

### 错误代码

| 错误代码 | 说明 |
|---------|------|
| 0 | 成功 |
| 1 | 通用错误 |
| 2 | 参数错误 |
| 3 | 文件不存在 |
| 4 | 文件读取错误 |
| 5 | 文件写入错误 |
| 6 | PDF 格式错误 |
| 7 | PDF 密码错误 |
||8 | 插件错误 |
| 9 | 插件未找到 |
| 10 | 配置错误 |
| 11 | 网络错误 |
| 12 | 权限错误 |
| 13 | 内存错误 |
| 14 | 数据验证失败 |

### 错误处理示例

#### 静默模式（只显示错误）

```bash
ai-pdf-agent -q text input.pdf
```

#### 调试模式（显示完整堆栈）

```bash
ai-pdf-agent --debug text input.pdf
```

#### JSON 格式错误输出

```bash
ai-pdf-agent --json text input.pdf
```

错误输出示例：

```json
{
  "error": "FileNotFoundError",
  "message": "File not found: input.pdf",
  "exit_code": 3,
  "details": null,
  "solution": "Please check if the file path is correct: input.pdf"
}
```

### 常见错误处理

#### 文件不存在错误

```bash
$ ai-pdf-agent text non_existent.pdf
❌ File not found: non_existent.pdf
  💡 Solution: Please check if the file path is correct: non_existent.pdf
```

#### PDF 格式错误

```bash
$ ai-pdf-agent text corrupted.pdf
❌ Invalid PDF format or corrupted file
  💡 Solution: Please ensure the file is a valid PDF document
```

#### PDF 密码错误

```bash
$ ai-pdf-agent text protected.pdf
❌ PDF file is password-protected
  💡 Solution: Please provide the password using --password option
```

#### 插件未找到错误

```bash
$ ai-pdf-agent text input.pdf
❌ Plugin not found: text_reader
  💡 Solution: Please check if the plugin 'text_reader' is installed and available
```

---

## 配置管理

AI PDF Agent 支持通过配置文件和环境变量来管理配置。

### 配置文件格式

支持 JSON 和 YAML 格式的配置文件。

#### JSON 配置文件示例 (`config.json`)

```json
{
  "pdf_engine": "pymupdf",
  "output_format": "markdown",
  "include_images": true,
  "include_tables": true,
  "image_format": "png",
  "image_dpi": 150,
  "output_encoding": "utf-8",
  "chunk_size": 1000,
  "overlap": 100,
  "log_level": "INFO",
  "log_file": null,
  "log_format": "standard"
}
```

#### YAML 配置文件示例 (`config.yaml`)

```yaml
pdf_engine: pymupdf
output_format: markdown
include_images: true
include_tables: true
image_format: png
image_dpi: 150
output_encoding: utf-8
chunk_size: 1000
overlap: 100
log_level: INFO
log_file: null
log_format: standard
```

### 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| `pdf_engine` | string | `pymupdf` | PDF 引擎（pymupdf, pdfplumber, p.ypdf） |
| `output_format` | string | `markdown` | 输出格式（markdown, html, json, text, csv） |
| `include_images` | boolean | `true` | 是否包含图片 |
| `include_tables` | boolean | `true` | 是否包含表格 |
| `image_format` | string | `png` | 图片格式（png, jpeg, jpg, webp） |
| `image_dpi` | integer | `150` | 图片 DPI（72-600） |
| `output_encoding` | string | `utf-8` | 输出编码 |
| `chunk_size` | integer | `1000` | 分块大小（100-10000） |
| `overlap` | integer | `100` | 重叠大小（0-1000） |
| `log_level` | string | `INFO` | 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL） |
| `log_file` | string | `null` | 日志文件路径 |
| `log_format` | string | `standard` | 日志格式（minimal, simple, standard, detailed, full） |

### 使用配置文件

```bash
# 指定配置文件
ai-pdf-agent -c config.json text input.pdf

# 指定 YAML 配置文件
ai-pdf-agent -c config.yaml text input.pdf
```

### 环境变量配置

支持通过环境变量覆盖配置项。环境变量命名规则：`AIPDF_<CONFIG_KEY>`

```bash
# 设置 PDF 引擎
export AIPDF_PDF_ENGINE=pdfplumber

# 设置输出格式
export AIPDF_OUTPUT_FORMAT=json

# 设置图片 DPI
export AIPDF_IMAGE_DPI=300

# 设置是否包含图片
export AIPDF_INCLUDE_IMAGES=true

# 设置日志级别
export AIPDF_LOG_LEVEL=DEBUG

# 使用配置
ai-pdf-agent text input.pdf
```

### 配置优先级

配置优先级从高到低：

1. **环境变量** - 优先级最高
2. **配置文件** - 中等优先级
3. **默认配置** - 优先级最低

### 创建默认配置文件

```python
from cli.config import create_default_config

# 创建 JSON 配置文件
create_default_config('config.json', format='json')

# 创建 YAML 配置文件
create_default_config('config.yaml', format='yaml')
```

### 日志配置

#### 日志级别

| 级别 | 说明 |
|------|------|
| DEBUG | 调试信息（最详细） |
| INFO | 一般信息 |
| WARNING | 警告信息 |
| ERROR | 错误信息 |
| CRITICAL | 严重错误信息 |

#### 日志格式

| 格式 | 说明 |
|------|------|
| minimal | 仅消息 |
| simple | 级别: 消息 |
| standard | 时间 - 名称 - 级别 - 消息 |
| detailed | 时间 - 名称 - 级别 - 文件:行号 - 消息 |
| full | 完整信息（包含函数名） |

#### 配置日志

**通过配置文件：**

```json
{
  "log_level": "DEBUG",
  "log_file": "/var/log/ai-pdf-agent.log",
  "log_format": "detailed"
}
```

**通过环境变量：**

```bash
export AIPDF_LOG_LEVEL=DEBUG
export AIPDF_LOG_FILE=/var/log/ai-pdf-agent.log
export AIPDF_LOG_FORMAT=detailed
```

**通过命令行选项：**

```bash
ai-pdf-agent --debug text input.pdf
ai-pdf-agent --verbose text input.pdf
ai-pdf-agent --quiet text input.pdf
```

### 编程接口

#### 加载配置

```python
from cli.config import Config, load_config

# 使用默认配置
config = Config()

# 从文件加载配置
config = Config('config.json')

# 加载并验证配置
config = load_config('config.json', validate=True)

# 获取配置项
pdf_engine = config.get('pdf_engine', 'pymupdf')

# 设置配置项
config.set('pdf_engine', 'pdfplumber')

# 更新多个配置项
config.update({
    'pdf_engine': 'pdfplumber',
    'output_format': 'json'
})

# 验证配置
if config.validate():
    print("配置有效")
else:
    print("配置无效")
    for error in config.get_validation_errors():
        print(f"  - {error}")

# 保存配置
config.save_to_file('config.json', format='json')
config.save_to_file('config.yaml', format='yaml')
```

#### 错误处理

```python
from cli.error_handler import (
    AI_PDF_Error,
    FileNotFoundError,
    PDFFormatError,
    handle_errors,
    safe_execute,
    validate_file_exists,
    validate_pdf_file,
)

# 使用自定义错误
raise FileNotFoundError('input.pdf')

# 验证文件
validate_file_exists('input.pdf')
validate_pdf_file('input.pdf')

# 使用错误处理装饰器
@handle_errors()
def my_function():
    # 函数实现
    pass

# 安全执行
result = safe_execute(
    lambda: risky_operation(),
    default=None,
    error_handler=lambda e: print(f"Error: {e}")
)
```

### 最佳实践

1. **使用配置文件** - 对于生产环境，建议使用配置文件管理所有配置
2. **环境变量覆盖** - 使用环境变量覆盖特定配置（如日志级别）
3. **日志文件** - 设置日志文件以便排查问题
4. **验证配置** - 加载配置后进行验证
5. **错误处理** - 使用错误处理装饰器统一处理异常

---

## 示例

### 完整配置示例

创建 `config.json`：

```json
{
  "pdf_engine": "pymupdf",
  "output_format": "markdown",
  "include_images": true,
  "include_tables": true,
  "image_format": "png",
  "image_dpi": 300,
  "output_encoding": "utf-8",
  "chunk_size": 2000,
  "overlap": 200,
  "log_level": "INFO",
  "log_file": "./ai-pdf-agent.log",
  "log_format": "detailed"
}
```

使用配置：

```bash
ai-pdf-agent -c config.json to-markdown input.pdf -o output.md
```

### 开发环境配置

创建 `dev-config.yaml`：

```yaml
pdf_engine: pymupdf
output_format: markdown
include_images: true
include_tables: true
log_level: DEBUG
log_file: ./debug.log
log_format: full
```

使用配置：

```bash
ai-pdf-agent -c dev-config.yaml --debug text input.pdf
```

### 生产环境配置

通过环境变量设置：

```bash
export AIPDF_PDF_ENGINE=pymupdf
export AIPDF_OUTPUT_FORMAT=markdown
export AIPDF_LOG_LEVEL=WARNING
export AIPDF_LOG_FILE=/var/log/ai-pdf-agent.log

ai-pdf-agent -q to-markdown input.pdf -o output.md
```

### 错误处理脚本

```python
#!/usr/bin/env python3
"""PDF 处理脚本，带有完善的错误处理"""

import sys
from pathlib import Path

from cli.config import Config
from cli.error_handler import (
    handle_errors,
    FileNotFoundError,
    PDFFormatError,
    validate_pdf_file,
)

@handle_errors()
def process_pdf(input_path: str, output_path: str):
    """处理 PDF 文件"""

    # 验证输入文件
    validate_pdf_file(input_path)

    # 加载配置
    config = Config()

    # 处理 PDF
    # ... 处理逻辑 ...

    print(f"✓ 处理完成: {output_path}")

if __name__ == '__main__':
    import click

    @click.command()
    @click.argument('input', type=click.Path())
    @click.argument('output', type=click.Path())
    def main(input, output):
        process_pdf(input, output)

    main()
```
