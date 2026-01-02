
```markdown
# Microtext Argument Extractor

This Python utility automates the extraction of argumentative components (Claims, Premises, and Objections) from the **Microtext Corpus** (XML format). It is designed to process directories of XML files, classify logical units based on their graph structure, and export the findings.

## 📌 Features

* **Attribute Selection:** Selectively extract `claims`, `premises`, or `objections`.
* **Batch Processing:** Scans an entire directory for `.xml` files.
* **Flexible Output:** Supports both CSV and XML export formats.
* **Automatic Path Handling:** Automatically creates missing output directories.

## 🚀 Setup & Usage

### Prerequisites
* Python 3.x
* The Microtext Corpus XML files (e.g., in a folder named `corpus/`)

### Command Syntax

```bash
python extract_args.py <input_dir> --extract <attributes> --output <output_file>

```

| Argument | Description | Options |
| --- | --- | --- |
| `input_dir` | Directory containing the corpus XML files. | (e.g., `./corpus`) |
| `--extract` | List of attributes to extract (space-separated). | `claims` `premises` `objections` |
| `--output` | Destination file path. Extension determines format. | `.csv` or `.xml` |

### Examples

**1. Extract Claims and Objections to CSV**
Reads files from `arg-microtexts/corpus/en/` and saves results to a new folder `results/`.

```bash
python extract_args.py arg-microtexts/corpus/en/ --extract claims objections --output results/extraction.csv

```

**2. Extract All Data to XML**
Extracts all argument types and saves them as an XML file.

```bash
python extract_args.py data/ --extract claims premises objections --output analysis/full_dataset.xml

```

## 🧠 How It Works

The script parses the Argument Graph (`<arggraph>`) structure within each file to classify text segments:

1. **Parsing:** It reads `<edu>` tags for text and `<edge>` tags for relationships.
2. **Logic Classification:**
* **Claim:** Identified as the **Root Node** (an ADU with no outgoing argument edges).
* **Premise:** Identified by an outgoing `sup` (support) edge.
* **Objection:** Identified by an outgoing `reb` (rebuttal) or `und` (undercut) edge.


3. **Export:** Formatting the extracted text into the requested file type.

## 📂 Output Format

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

## 🛠 Troubleshooting

* **"No such file or directory"**: The script automatically handles *output* directory creation. If you see this error, check that your **input** directory path is correct and contains `.xml` files.
* **Empty Output File**: Ensure the XML files follow the standard Microtext DTD structure (containing `<edu>`, `<adu>`, and `<edge>` tags).

