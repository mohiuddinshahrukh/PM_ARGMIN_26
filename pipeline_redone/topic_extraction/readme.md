Here is a clean, professional `README.md` file tailored to your code. You can copy-paste this directly into a file named `README.md` in your project folder.

---

```markdown
# XML Attribute Extractor

A robust command-line tool to scan a directory of XML files, extract specific attributes (like `topic_id`, `stance`, or `id`) from the `<arggraph>` tag, and generate a summary report in **CSV** or **XML** format.

## Features
- **Flexible Extraction:** Extract any attribute (e.g., `topic_id`, `stance`) without changing code.
- **Dual Output Formats:** Automatically detects whether to save as `.csv` or `.xml`.
- **Automatic Directory Creation:** Creates the output folder if it doesn't exist.
- **Detailed Statistics:** Reports total files, total XMLs, processed files, and unique attribute counts.

## Prerequisites
- Python 3.6+
- `beautifulsoup4`
- `lxml` (optional, but recommended for faster XML parsing)

## Installation

1. Clone or download this repository.
2. Install the required dependencies:

```bash
pip install beautifulsoup4 lxml

```

## Usage

Run the script from your terminal (Command Prompt, PowerShell, or Bash).

### Basic Syntax

```bash
python script_name.py <INPUT_DIR> <OUTPUT_FILE> [--attribute <ATTRIBUTE_NAME>]

```

| Argument | Type | Description |
| --- | --- | --- |
| `input_dir` | **Required** | Path to the folder containing your `.xml` files. |
| `output_file` | **Required** | Path for the result file. Must end in `.csv` or `.xml`. |
| `--attribute` | *Optional* | The XML attribute to extract. Defaults to `topic_id`. |

---

### Examples

#### 1. Extract Topics to CSV (Default behavior)

Extracts the `topic_id` from all XML files and saves a summary CSV.

```bash
python pipeline_redone/1_extract_all_topics.py "E:\Path\To\corpus\en" results/topics.csv

```

#### 2. Extract Stance to XML

Extracts the `stance` attribute (e.g., "pro" or "con") and saves an XML tree.

```bash
python pipeline_redone/1_extract_all_topics.py "E:\Path\To\corpus\en" results/stance_report.xml --attribute stance

```

#### 3. Extract IDs to CSV

Extracts the unique `id` attribute.

```bash
python pipeline_redone/1_extract_all_topics.py "E:\Path\To\corpus\en" results/ids.csv --attribute id

```

---

## Output Format

### CSV Example

The CSV output includes a summary header followed by the data table.

```csv
--- SUMMARY STATISTICS ---
Total Files in Directory,122
Total XML Files,120
Files containing 'topic_id',120
Unique 'topic_id' values,18

topic_id,Found In Files
waste_separation,"micro_b001.xml, micro_b005.xml"
public_transport,"micro_k002.xml"
...

```

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

## Troubleshooting

* **"File not found" Error:** Ensure your `input_dir` path is correct. If the path contains spaces, wrap the entire path in double quotes (e.g., `"C:\My Documents\Data"`).
* **"Module not found":** Run `pip install beautifulsoup4`.

```

```