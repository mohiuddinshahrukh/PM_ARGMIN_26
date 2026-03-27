
```markdown
# Microtext ADU Extractor

This script automates the extraction of **argumentative discourse units** (ADUs: Claims, Premises, and Objections) from the **Microtext Corpus** (XML format). It is designed to process directories of XML files, classify logical units based on their graph structure, and export the findings.

## Features

* **ADU Selection:** Selectively extract `claims`, `premises`, or `objections`.
* **Batch Processing:** Scans an entire directory for `.xml` files.
* **Flexible Output:** Supports both CSV and XML export formats.
* **Automatic Path Handling:** Automatically creates missing output directories.

### Command Syntax

```bash
python 2_adu_extraction.py <input_dir> --extract <ADUs> --output <output_file>

```

## How It Works

The script parses the Argument Graph (`<arggraph>`) structure within each file to classify text segments:

1. **Parsing:** It reads `<edu>` tags for text and `<edge>` tags for relationships.
2. **Logic Classification:**
* **Claim:** Identified as the **Root Node** (an ADU with no outgoing argument edges).
* **Premise:** Identified by an outgoing `sup` (support) edge.
* **Objection:** Identified by an outgoing `reb` (rebuttal) or `und` (undercut) edge.


3. **Export:** Formatting the extracted text into the requested file type.

## Output Format

**CSV Output Example:**

```csv
filename,type,text
micro_b001.xml,premise,"Germany produces way too much rubbish"
micro_b002.xml,claim,"Higher fines are therefore the right measure..."

```

**XML Output Example:**

```xml
<extraction_results>
  <item>
    <filename>micro_b003.xml</filename>
    <type>objection</type>
    <text>Patients do often report relief...</text>
  </item>
</extraction_results>

```
