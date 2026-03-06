# AI PDF Agent Skill

## Description
AI Agent 友好的 PDF 处理工具，专为 AI Agent 设计的 CLI 工具，通过插件化架构提供灵活的 PDF 处理能力。

## Use Cases
Use this skill when:
- User asks to extract text, tables, images from PDF documents
- User wants to convert PDF to Markdown, JSON, HTML, CSV formats
- User needs to analyze PDF metadata or structure
- User requests PDF content extraction for AI Agent processing
- User mentions "PDF", "document", "pdf tool", "document processing"

## Installation
```bash
# Clone repository
git clone https://github.com/qqqzhch/ai-pdf-agent.git
cd ai-pdf-agent

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m ai.pdf --help
```

## Quick Start
```bash
# Extract text from PDF
python -m ai.pdf text document.pdf -o output.txt

# Extract with JSON output (AI Agent friendly)
python -m ai.pdf text document.pdf --json -o output.json

# Convert to Markdown
python -m ai.pdf to-markdown document.pdf -o output.md

# Extract tables
python -m ai.pdf tables report.pdf -o tables.json

# Extract images
python -m ai.pdf images document.pdf --extract-dir ./images
```

## Features
- **Plugin System**: Modular architecture for easy extension
- **Multi-format Support**: PDF → Markdown, JSON, HTML, CSV, EPUB
- **Content Extraction**: Text, tables, images, metadata, structure
- **AI Agent Friendly**: JSON output for easy programmatic access
- **Local Processing**: Privacy-focused, no file size limits

## Commands
- `text`: Extract PDF text
- `tables`: Extract PDF tables
- `images`: Extract PDF images
- `metadata`: Extract PDF metadata
- `to-markdown`: Convert to Markdown
- `to-json`: Convert to JSON
- `to-html`: Convert to HTML
- `to-csv`: Convert to CSV
- `to-image`: Convert pages to images
- `to-epub`: Convert to EPUB

## Example Output (JSON)
```json
{
  "success": true,
  "file": "document.pdf",
  "pages": 5,
  "text": "PDF document content...",
  "metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "created": "2026-03-05"
  }
}
```

## Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=plugins --cov-report=html

# Run specific test
pytest tests/test_text_reader.py
```

## Documentation
- README.md: Complete project documentation
- QUICKSTART.md: 5-minute quick start guide
- PLUGIN_DEV.md: Plugin development guide

## License
MIT License

## Repository
https://github.com/qqqzhch/ai-pdf-agent
