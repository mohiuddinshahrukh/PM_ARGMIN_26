
```markdown
# XML Attribute Extractor

A command-line tool to scan a directory of XML files, extract specific attributes (like `topic_id`, `stance`, or `id`) from the `<arggraph>` tag, and generate a summary report in **CSV** or **XML** format.

## Features
- **Flexible Extraction:** Extract any attribute (e.g., `topic_id`, `stance`) without changing code.
- **Dual Output Formats:** Automatically detects whether to save as `.csv` or `.xml`.
- **Automatic Directory Creation:** Creates the output folder if it doesn't exist.
- **Detailed Statistics:** Reports total files, total XMLs, processed files, and unique attribute counts.

### Basic Syntax

```bash
python 1_extract_all_topics.py <INPUT_DIR> <OUTPUT_FILE> [--attribute <ATTRIBUTE_NAME>]
```

## Output Format

### XML Example

The XML output contains metadata attributes in the root tag.

```xml
<report target_attribute="topic_id" total_files_in_directory="122" total_xml_files="120" processed_files_with_match="120" unique_values_count="18">
  <topic value="waste_separation" count="2">
    <file>micro_b001.xml</file>
    <file>micro_b005.xml</file>
  </topic>
  <topic value="public_transport" count="1">
    <file>micro_k002.xml</file>
  </topic>
</report>

```