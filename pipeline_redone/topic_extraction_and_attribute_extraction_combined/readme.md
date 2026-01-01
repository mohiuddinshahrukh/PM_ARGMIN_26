
### README.md

```markdown
# Microtext Argument Grouping Tool

This tool extracts argument units (claims, premises, and objections) from a directory of Microtext Corpus XML files. It aggregates the data by `topic_id`, combining all arguments for a specific topic into a single entry, regardless of how many files cover that topic.

## Features
* **Topic-Based Grouping:** Automatically groups extracted text segments by their unique `topic_id`.
* **Flexible Extraction:** You can choose to extract specific units (`claims`, `premises`, `objections`) or any combination of them.
* **Dual Output Formats:** Supports exporting data to **CSV** (for spreadsheets) or **XML** (for hierarchical data).
* **Auto-Directory Creation:** Automatically creates the output directory if it does not exist.

## Prerequisites
* Python 3.x
* No external dependencies required (uses standard libraries: `os`, `argparse`, `xml.etree.ElementTree`, `csv`, `sys`, `collections`).

## Installation
1.  Save the provided Python script as `unified_extractor.py` (or your preferred filename).
2.  Ensure your input data consists of valid `.xml` files formatted according to the Microtext Corpus structure.

## Usage

Run the script from the command line using the following syntax:

```bash
python unified_extractor.py <input_dir> <output_file> --units <unit_types>

```

### Arguments

| Argument | Type | Description |
| --- | --- | --- |
| `input_dir` | Positional | The path to the directory containing the `.xml` files. |
| `output_file` | Positional | The path where the output file will be saved. Must end in `.csv` or `.xml`. |
| `--units` | Required | Space-separated list of unit types to extract. Choices: `claims`, `premises`, `objections`. |

## Examples

### 1. Extract Objections to XML

Extract only **objections**, group them by topic, and save as an XML file.

```bash
python 3_unified_extractor.py .\arg-microtexts\corpus\en\ results\output_objections.xml --units objections

```

*Result:* An XML file where each `<topic>` contains a list of `<objections>` found for that topic.

### 2. Extract Premises to CSV

Extract only **premises** and save as a CSV file.

```bash
python 3_unified_extractor.py ./data/corpus results/all_premises.csv --units premises

```

*Result:* A CSV file where each row represents a unique topic, and the `premises` column contains all premises joined by a pipe `|` separator.

### 3. Extract Everything

Extract **claims, premises, and objections** together into one CSV.

```bash
python 3_unified_extractor.py ./data/corpus results/full_corpus.csv --units claims premises objections

```

*Result:* A CSV with columns for `topic_id`, `claims`, `premises`, and `objections`.

## Output Structure

### CSV Output

The CSV output uses `|` as a separator for multiple text segments within the same topic.

| topic_id | premises |
| --- | --- |
| waste_separation | Text segment 1... |
| higher_dog_poo_fines | Text segment A... |

### XML Output

The XML output is hierarchical, nesting unit types under their specific topic.

```xml
<grouped_corpus>
  <topic id="waste_separation">
    <premises count="2">
      <item>Text segment 1...</item>
      <item>Text segment 2...</item>
    </premises>
  </topic>
</grouped_corpus>

```

