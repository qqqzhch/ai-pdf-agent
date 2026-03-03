# Plugin Management Commands - Usage Guide

## Overview

The AI PDF Agent provides a comprehensive plugin management system through the CLI. All plugin commands are available under the `plugin` subcommand group.

## Commands

### 1. List All Plugins

Display all available plugins with their details.

```bash
# List all enabled plugins
ai-pdf-agent plugin list

# List all plugins (including disabled ones)
ai-pdf-agent plugin list --all

# Filter by plugin type
ai-pdf-agent plugin list --type reader
ai-pdf-agent plugin list --type converter
ai-pdf-agent plugin list --type ocr

# Output in JSON format
ai-pdf-agent plugin list --json
```

**Output Example:**
```
Name                    Version    Type         Status   Description
--------------------------------------------------------------------------------
text_reader            1.0.0      reader       ✓        Extract text content from PDF files
table_reader           1.0.0      reader       ✓        Extract tables from PDF files
image_reader           1.0.0      reader       ✓        Extract images from PDF files
```

### 2. View Plugin Information

Display detailed information about a specific plugin.

```bash
# Show plugin details
ai-pdf-agent plugin info text_reader

# Output in JSON format
ai-pdf-agent plugin info text_reader --json
```

**Output Example:**
```
插件信息: text_reader
============================================================
名称: text_reader
版本: 1.0.0
描述: Extract text content from PDF files
类型: reader
作者: AI PDF Agent Team
主页: https://github.com/example/ai-pdf-agent
许可证: MIT

状态:
  启用状态: ✓ 已启用
  可用状态: ✓ 可用
  依赖状态: ✓ 满足

依赖项:
  Python 依赖: pypdf2>=3.0.0
  系统依赖: poppler-utils
```

### 3. Check Plugin Health

Verify plugin dependencies and availability.

```bash
# Check all plugins
ai-pdf-agent plugin check

# Check specific plugin
ai-pdf-agent plugin check --name text_reader

# Verbose output
ai-pdf-agent plugin check --verbose

# JSON output
ai-pdf-agent plugin check --json
```

**Output Example:**
```
Plugin              Type         Status     Enabled   Deps 
------------------------------------------------------------
text_reader        reader       ✓ OK       ✓         ✓    
table_reader       reader       ✓ OK       ✓         ✓    
image_reader       reader       ✗ FAIL     ✓         ✗    

✓ 部分插件存在问题，请检查详细输出
```

**Verbose Output Example:**
```
插件健康状态检查
================================================================================

✓ text_reader (v1.0.0)
  类型: reader
  启用: ✓
  可用: ✓
  依赖: ✓

✗ image_reader (v1.0.0)
  类型: reader
  启用: ✓
  可用: ✗
  依赖: ✗
  缺失: Pillow>=10.0.0
```

### 4. Enable Plugin

Enable a disabled plugin.

```bash
# Enable a plugin
ai-pdf-agent plugin enable text_reader
```

**Output:**
```
✓ Plugin 'text_reader' has been enabled
```

**Already Enabled:**
```
✓ Plugin 'text_reader' is already enabled
```

### 5. Disable Plugin

Disable a plugin (it won't be loaded on startup).

```bash
# Disable a plugin
ai-pdf-agent plugin disable text_reader

# Force disable (even if plugin is in use)
ai-pdf-agent plugin disable text_reader --force
```

**Output:**
```
✓ Plugin 'text_reader' has been disabled
```

### 6. Reload Plugins

Reload all plugins (useful after installing new plugins or updating configuration).

```bash
# Reload all plugins
ai-pdf-agent plugin reload

# Verbose output with details
ai-pdf-agent plugin reload --verbose
```

**Output Example:**
```
当前加载的插件 (3):
  - text_reader
  - table_reader
  - image_reader

已卸载 3 个插件

✓ 加载插件: text_reader v1.0.0
✓ 加载插件: table_reader_reader v1.0.0
✗ 加载失败: image_reader

成功加载 2 个插件

✓ 插件重新加载完成 (2 个插件已加载)
```

## Plugin Types

The following plugin types are available:

| Type | Description |
|------|-------------|
| `reader` | Reader plugins for extracting content (text, tables, images) |
| `converter` | Converter plugins for format conversion (Markdown, HTML, JSON) |
| `ocr` | OCR plugins for text recognition (Tesseract, PaddleOCR) |
| `rag` | RAG plugins for retrieval-augmented generation |
| `encrypt` | Encryption plugins for password protection |
| `compress` | Compression plugins for file optimization |
| `edit` | Editor plugins for modifying PDFs |
| `analyze` | Analyzer plugins for document analysis |
| `custom` | Custom plugins for user-defined functionality |

## Configuration

Plugin enable/disable state is persisted in:
```
~/.ai-pdf/disabled_plugins.json
```

**Example configuration:**
```json
{
  "disabled": [
    "image_reader",
    "old_plugin"
  ]
}
```

## Tips and Best Practices

1. **Check dependencies first**: Always run `plugin check` after installing new dependencies
2. **Use verbose mode**: When troubleshooting, use `--verbose` to see detailed information
3. **JSON output**: Use `--json` for programmatic access and integration with other tools
4. **Reload after changes**: After installing new plugins, run `plugin reload` to make them available
5. **Filter by type**: Use `--type` to quickly find plugins of a specific category

## Integration Examples

### Bash Script - Check All Plugins
```bash
#!/bin/bash

# Check plugin health
ai-pdf-agent plugin check --json > /tmp/plugin_status.json

# Parse and alert on failed plugins
failed_plugins=$(jq '.[] | select(.healthy == false) | .name' /tmp/plugin_status.json)

if [ -n "$failed_plugins" ]; then
    echo "⚠️  Failed plugins: $failed_plugins"
    exit 1
fi
```

### Python - Get Plugin List
```python
import subprocess
import json

# Get plugin list
result = subprocess.run(
    ['ai-pdf-agent', 'plugin', 'list', '--json'],
    capture_output=True,
    text=True
)

plugins = json.loads(result.stdout)

# Print reader plugins
for plugin in plugins:
    if plugin['plugin_type'] == 'reader' and plugin['enabled']:
        print(f"{plugin['name']}: {plugin['description']}")
```

### Cron Job - Daily Health Check
```cron
# Check plugin health every day at 2 AM
0 2 * * * /usr/local/bin/ai-pdf-agent plugin check --verbose > /var/log/plugin-check.log 2>&1
```

## Troubleshooting

### Plugin Not Found
```
Error: Plugin 'xyz' not found
```
**Solution**: Run `plugin list` to see available plugins

### Missing Dependencies
```
✗ Plugin 'xyz' missing dependencies: Pillow>=10.0.0
```
**Solution**: Install the missing dependencies:
```bash
pip install Pillow>=10.0.0
```

### Plugin Won't Load
```
✗ Load failed: xyz
```
**Solution**: 
1. Run `plugin check --name xyz --verbose` for details
2. Check the plugin logs
3. Verify all system dependencies are installed

### Can't Disable Plugin
```
Error: Failed to disable plugin 'xyz'
```
**Solution**: Use `--force` flag if you're sure:
```bash
ai-pdf-agent plugin disable xyz --force
```
