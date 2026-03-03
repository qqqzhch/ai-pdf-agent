# JSON Converter Plugin (ToJsonConverter)

## Overview

The `ToJsonConverter` plugin converts PDF documents to structured JSON format, extracting text, tables, images, and metadata.

## Implementation

### Files

- **Plugin:** `/root/.openclaw/workspace/ai-pdf-agent/plugins/converters/json_converter.py`
- **Tests:** `/root/.openclaw/workspace/ai-pdf-agent/tests/converters/test_json_converter.py`

### Architecture

The `ToJsonConverter` is implemented as an alias to the existing `ToJsonPlugin` class to maintain consistency with task requirements while avoiding code duplication. All actual functionality is implemented in `to_json.py`.

## Features

### 1. Content Extraction

- **Text:** Full text and text blocks with bounding boxes
- **Tables:** Automatic table detection and extraction
- **Metadata:** Document metadata (title, author, keywords, etc.)
- **Structure:** Page dimensions, rotation, block counts

### 2. Page Selection PageRange)

- `pages` - List of specific page numbers

### 3. Output Options

- `pretty` - Format JSON with indentation (default: True)
- `output_path` - Save to file
- `schema` - Custom schema for field filtering

### 4. JSON Schema Support

- Built-in JSON schema validation
- Custom schema with include/exclude fields
- Field filtering capability

## Usage Example

```python
from plugins.converters.json_converter import ToJsonConverter

# Create converter
converter = ToJsonConverter()

# Convert PDF
result = converter.convert(
    pdf_path="document.pdf",
    pages=[1, 2, 3],
    include_text=True,
    include_tables=True,
    include_metadata=True,
    include_structure=True,
    pretty=True,
    output_path="output.json"
)

# Check result
if result["success"]:
    json_str = result["content"]
    import json
    data = json.loads(json_str)

    # Access data
    print(data["document"]["filename"])
    print(data["metadata"]["title"])
    for page in data["text"]["pages"]:
        print(page["full_text"])
else:
    print(f"Error: {result['error']}")
```

## JSON Output Structure

```json
{
  "document": {
    "filename": "document.pdf",
    "path": "/path/to/document.pdf",
    "page_count": 10,
    "pages_processed": [1, 2, 3]
  },
  "metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "subject": "Subject",
    "keywords": ["keyword1", "keyword2"],
    "creator": "Creator",
    "producer": "Producer",
    "created": "D:20240101120000Z",
    "modified": "D:20240102120000Z",
    "page_count": 10,
    "is_encrypted": false,
    "pdf_version": "1.7"
  },
  "text": {
    "total_pages": 3,
    "pages": [
      {
        "page_number": 1,
        "full_text": "Page text content...",
        "blocks": [
          {
            "text": "Block text",
            "bbox": [x0, y0, x1, y1],
            "line_no": 1
          }
        ],
        "char_count": 150
      }
    ]
  },
  "tables": {
    "total_tables": 2,
    "pages": [
      {
        "page_number": 1,
        "tables": [
          {
            "bbox": [x0, y0, x1, y1],
            "header": ["Column 1", "Column 2"],
            "rows": [
              ["Row 1 Col 1", "Row 1 Col 2"],
              ["Row 2 Col 1", "Row 2 Col 2"]
            ],
            "row_count": 3,
            "col_count": 2
          }
        ],
        "table_count": 1
      }
    ]
  },
  "structure": {
    "pages": [
      {
        "page_number": 1,
        "width": 595.0,
        "height": 842.0,
        "rotation": 0,
        "text_blocks": 10,
        "image_blocks": 2,
        "drawing_blocks": 0
      }
    ]
  }
}
```

## Test Coverage

### Test Suites (54 tests total)

1. **Initialization** (6 tests)
   - Plugin class existence
   - Metadata validation
   - Dependency checking
   - Availability verification
   - Help text

2. **Validation** (8 tests)
   - File existence checks
   - PDF format validation
   - Readable file validation
   - Input/output validation

3. **Conversion** (6 tests)
   - Basic conversion success
   - Result structure validation
   - JSON validity
   - Error handling

4. **Page Selection** (6 tests)
   - Single page conversion
   - Page range conversion
   - Multiple pages list
   - All pages (default)
   - Invalid page handling

5. **Content Extraction** (10 tests)
   - Text extraction
   - Table extraction
   - Metadata extraction
   - Structure extraction
   - Field exclusion options

6. **Output Options** (5 tests)
   - Pretty JSON format
   - Compact JSON format
   - File output saving
   - Pretty file output

7. **Custom Schema** (5 tests)
   - Include fields
   - Exclude fields
   - Empty schema handling
   - Schema building

8. **Edge Cases** (5 tests)
   - Empty PDF files
   - Corrupted PDF files
   - Long filenames
   - Unicode filenames
   - Special characters

9. **Integration** (2 tests)
   - Full workflow test
   - Minimal conversion test

## Dependencies

- `pymupdf>=1.23.0` (PyMuPDF)

## Test Results

All 54 tests passing ✓

```bash
pytest tests/converters/test_json_converter.py -v
```

## Notes

- The plugin uses PyMuPDF for PDF processing
- Empty pages list falls back to processing all pages
- `result["pages"]` reflects the actual number of pages processed, not total pages
- All text is extracted with Unicode support (ensure_ascii=False)
